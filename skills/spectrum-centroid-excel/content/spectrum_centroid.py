"""
MS/MS质谱数据Centroid归中心化处理
实现msconvert风格的centroid算法
Mass列保留原始值，只修改Intensity列
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Tuple, List

import numpy as np
import openpyxl

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_peaks(masses: np.ndarray, intensities: np.ndarray, min_intensity: float = 100) -> List[int]:
    """
    找到所有局部最大值作为峰的索引

    Args:
        masses: m/z值数组
        intensities: 强度值数组
        min_intensity: 最小强度阈值，过滤低信噪比峰

    Returns:
        peaks: 峰索引列表
    """
    peaks = []
    n = len(intensities)

    for i in range(1, n - 1):
        # 局部最大值检测
        if intensities[i] > intensities[i-1] and intensities[i] > intensities[i+1]:
            # 过滤低强度峰
            if intensities[i] > min_intensity:
                peaks.append(i)

    return peaks


def calculate_centroid(
    masses: np.ndarray,
    intensities: np.ndarray,
    peak_idx: int,
    window: int = 3
) -> Tuple[float, float]:
    """
    计算峰的质心位置
    使用Intensity加权平均

    Args:
        masses: m/z值数组
        intensities: 强度值数组
        peak_idx: 峰索引
        window: 质心计算窗口大小

    Returns:
        centroid_mass: 质心m/z值
        max_intensity: 峰范围内最大强度
    """
    n = len(masses)
    start = max(0, peak_idx - window)
    end = min(n - 1, peak_idx + window)

    # 计算加权质心
    total_intensity = 0
    weighted_mass = 0

    for i in range(start, end + 1):
        if intensities[i] > 0:
            total_intensity += intensities[i]
            weighted_mass += intensities[i] * masses[i]

    if total_intensity > 0:
        centroid_mass = weighted_mass / total_intensity
        # 返回峰范围内的最大强度
        max_intensity = max(intensities[start:end+1])
        return centroid_mass, max_intensity
    else:
        return masses[peak_idx], intensities[peak_idx]


def centroid_spectrum(
    masses: np.ndarray,
    intensities: np.ndarray,
    min_intensity: float = 500,
    window: int = 3
) -> Tuple[np.ndarray, List[Tuple[int, float, float, float]]]:
    """
    对质谱数据进行centroid归中心化

    Args:
        masses: m/z值数组
        intensities: 强度值数组
        min_intensity: 最小强度阈值
        window: 质心计算窗口大小

    Returns:
        result_intensities: centroid处理后的强度数组
        peak_info: 峰信息列表 [(索引, 原始m/z, 质心m/z, 强度), ...]
    """
    # 找到所有峰
    peaks = find_peaks(masses, intensities, min_intensity)

    logger.info(f"检测到 {len(peaks)} 个峰")

    # 创建结果数组 - 保留所有原始Mass值
    result_intensities = np.zeros_like(intensities)

    # 对每个峰计算质心
    peak_info = []
    for peak_idx in peaks:
        centroid_mass, centroid_intensity = calculate_centroid(masses, intensities, peak_idx, window)

        # 在峰位置写入质心化的强度
        result_intensities[peak_idx] = centroid_intensity
        peak_info.append((peak_idx, masses[peak_idx], centroid_mass, centroid_intensity))

    return result_intensities, peak_info


def validate_input_file(file_path: str) -> bool:
    """
    验证输入文件是否存在且为有效的Excel文件

    Args:
        file_path: 输入文件路径

    Returns:
        是否有效
    """
    path = Path(file_path)

    if not path.exists():
        logger.error(f"文件不存在: {file_path}")
        return False

    if not path.suffix.lower() in ['.xlsx', '.xls']:
        logger.error(f"不支持的文件格式: {path.suffix}，仅支持.xlsx和.xls")
        return False

    return True


def process_ms2_file(
    input_file: str,
    output_file: Optional[str] = None,
    min_intensity: float = 500,
    window: int = 3,
    show_details: bool = True
) -> str:
    """
    处理MS2质谱文件

    Args:
        input_file: 输入Excel文件路径
        output_file: 输出Excel文件路径（可选，默认在原文件名后加_centroid）
        min_intensity: 最小强度阈值
        window: 质心计算窗口大小
        show_details: 是否显示详细输出

    Returns:
        处理后的文件路径

    Raises:
        FileNotFoundError: 输入文件不存在
        ValueError: 文件格式无效
    """
    # 验证输入文件
    if not validate_input_file(input_file):
        raise FileNotFoundError(f"输入文件无效: {input_file}")

    logger.info(f"读取Excel文件: {input_file}")
    wb = openpyxl.load_workbook(input_file)
    ws = wb.active

    # 读取质谱数据（第8行开始）
    masses = []
    intensities = []
    max_row = ws.max_row

    for row in range(8, max_row + 1):
        m = ws.cell(row, 1).value
        intensity = ws.cell(row, 2).value
        if m is not None and intensity is not None:
            try:
                masses.append(float(m))
                intensities.append(float(intensity))
            except (ValueError, TypeError):
                logger.warning(f"第{row}行数据格式错误，已跳过")

    if not masses:
        raise ValueError("未读取到有效的质谱数据")

    logger.info(f"读取到 {len(masses)} 个数据点")

    # 转换为numpy数组
    masses = np.array(masses)
    intensities = np.array(intensities)

    # 显示原始数据统计
    if show_details:
        logger.info(f"原始数据统计:")
        logger.info(f"  m/z范围: {masses.min():.4f} - {masses.max():.4f}")
        logger.info(f"  强度范围: {intensities.min():.2f} - {intensities.max():.2f}")

    # 进行centroid处理
    logger.info(f"执行centroid归中心化 (min_intensity={min_intensity}, window={window})...")
    result_intensities, peak_info = centroid_spectrum(
        masses, intensities,
        min_intensity=min_intensity,
        window=window
    )

    # 统计非零强度的数据点数量
    non_zero_count = np.sum(result_intensities > 0)
    logger.info(f"Centroid处理后: {len(peak_info)} 个峰（强度非零的数据点）")

    # 确定输出文件路径
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_centroid{ext}"

    # 创建新workbook
    wb_out = openpyxl.Workbook()
    ws_out = wb_out.active
    ws_out.title = "Sheet1"

    # 复制元数据（第1-6行）
    for row_idx in range(1, 7):
        for col_idx in range(1, 3):
            value = ws.cell(row_idx, col_idx).value
            ws_out.cell(row_idx, col_idx, value)

    # 写入表头（第7行）
    ws_out.cell(7, 1, "Mass")
    ws_out.cell(7, 2, "Intensity")

    # 写入数据（第8行开始）- Mass保留原始值，Intensity使用centroid结果
    for i in range(len(masses)):
        ws_out.cell(i + 8, 1, masses[i])  # 保留原始Mass值
        ws_out.cell(i + 8, 2, result_intensities[i])  # 使用centroid后的Intensity

    # 保存文件
    wb_out.save(output_file)
    logger.info(f"输出文件: {output_file}")

    # 显示检测到的峰信息
    if show_details:
        logger.info(f"\n检测到的峰详情 (前10个):")
        logger.info(f"{'索引':>6} {'原始m/z':>12} {'质心m/z':>12} {'强度':>12}")
        logger.info("-" * 44)
        for idx, orig_mz, centroid_mz, intensity in peak_info[:10]:
            logger.info(f"{idx+8:6d} {orig_mz:12.4f} {centroid_mz:12.4f} {intensity:12.2f}")

        logger.info(f"\n总共保留 {len(masses)} 行数据（与原始数据一致）")
        logger.info(f"其中 {non_zero_count} 行Intensity > 0（峰位置）")

    return output_file


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='MS/MS质谱数据Centroid归中心化处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python spectrum_centroid.py input.xlsx output.xlsx 500
  python spectrum_centroid.py input.xlsx
  python spectrum_centroid.py input.xlsx -o result.xlsx -m 300 -w 5
        """
    )

    parser.add_argument('input_file', nargs='?', help='输入Excel文件路径')
    parser.add_argument('-o', '--output', dest='output_file',
                        help='输出Excel文件路径（默认: 原文件名_centroid.xlsx）')
    parser.add_argument('-m', '--min-intensity', type=float, default=500,
                        help='最小强度阈值（默认: 500）')
    parser.add_argument('-w', '--window', type=int, default=3,
                        help='质心计算窗口大小（默认: 3）')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='静默模式，减少输出')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')

    args = parser.parse_args()

    # 如果没有提供输入文件，显示帮助
    if args.input_file is None:
        parser.print_help()
        sys.exit(1)

    # 设置日志级别
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    try:
        output = process_ms2_file(
            args.input_file,
            args.output_file,
            min_intensity=args.min_intensity,
            window=args.window,
            show_details=not args.quiet
        )
        print(f"处理完成: {output}")
    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
