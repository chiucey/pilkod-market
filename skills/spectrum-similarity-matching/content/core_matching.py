#!/usr/bin/env python3
"""
MS/MS 质谱相似度匹配核心脚本
Core module for MS/MS spectrum similarity matching

支持算法：
- Modified Cosine (优先)
- Standard Cosine
- Weighted Cosine (平方根加权)
- Spectral Entropy

作者: Paul, Skill创建达人
"""

import warnings
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# 尝试导入依赖包
try:
    from matchms import Spectrum
    from matchms.similarity import (
        CosineGreedy,
        CosineHungarian,
        ModifiedCosineGreedy,
        ModifiedCosineHungarian,
        FlashSimilarity,
    )
    MATCHMS_AVAILABLE = True
except ImportError:
    MATCHMS_AVAILABLE = False

try:
    from ms_entropy import FlashEntropySearch
    MS_ENTROPY_AVAILABLE = True
except ImportError:
    MS_ENTROPY_AVAILABLE = False


# ============================================================
# 依赖检查
# ============================================================

def check_dependencies() -> Dict[str, Union[bool, List[str]]]:
    """
    检查必需的依赖包是否已安装

    Returns:
        dict: {
            "status": "ready" | "missing",
            "packages": list of missing packages,
            "install_command": str
        }
    """
    required = ["matchms", "pandas"]
    optional = ["ms_entropy"]

    missing_required = []
    missing_optional = []

    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing_required.append(pkg)

    for pkg in optional:
        try:
            __import__(pkg)
        except ImportError:
            missing_optional.append(pkg)

    if missing_required:
        install_cmd = f"pip install {' '.join(missing_required)}"
        if missing_optional:
            install_cmd += f" {' '.join(missing_optional)}"
        return {
            "status": "missing",
            "packages": missing_required + missing_optional,
            "install_command": install_cmd
        }

    return {"status": "ready", "packages": [], "install_command": ""}


# ============================================================
# 数据预处理
# ============================================================

def round_mz(mz: float, decimals: int = 4) -> float:
    """将 mz 值保留至指定小数位"""
    return round(mz, decimals)


def read_spectrum_from_csv(
    file_path: str,
    mz_col: str = "mz",
    intensity_col: str = "intensity",
    mz_decimals: int = 4,
    precursor_mz: float = 0.0
) -> Spectrum:
    """
    从 CSV 文件读取质谱数据

    Args:
        file_path: CSV 文件路径
        mz_col: mz 列名
        intensity_col: intensity 列名
        mz_decimals: mz 保留小数位
        precursor_mz: 前体离子 mz (用于 Modified Cosine)

    Returns:
        Spectrum 对象
    """
    df = pd.read_csv(file_path)

    # 过滤 intensity > 0 的峰
    df = df[df[intensity_col] > 0]

    # 保留 mz 小数位
    mz_values = df[mz_col].round(mz_decimals).values
    intensity_values = df[intensity_col].values

    return Spectrum(
        mz=mz_values,
        intensities=intensity_values,
        metadata={"precursor_mz": precursor_mz}
    )


def filter_peaks_by_intensity(
    spectrum: Spectrum,
    threshold: float = 0.01
) -> Spectrum:
    """
    根据强度阈值过滤峰

    Args:
        spectrum: 输入谱图
        threshold: 相对于最大强度的阈值（默认 1%）

    Returns:
        过滤后的谱图
    """
    max_intensity = np.max(spectrum.peaks.intensities)
    cutoff = max_intensity * threshold

    mask = spectrum.peaks.intensities >= cutoff

    return Spectrum(
        mz=spectrum.peaks.mz[mask],
        intensities=spectrum.peaks.intensities[mask],
        metadata=spectrum.metadata
    )


def normalize_intensities(spectrum: Spectrum) -> Spectrum:
    """
    归一化峰强度（使其和为 1）

    Args:
        spectrum: 输入谱图

    Returns:
        归一化后的谱图
    """
    intensities = spectrum.peaks.intensities / np.sum(spectrum.peaks.intensities)

    return Spectrum(
        mz=spectrum.peaks.mz,
        intensities=intensities,
        metadata=spectrum.metadata
    )


# ============================================================
# 峰对齐与匹配
# ============================================================

def align_peaks_by_ppm(
    mz1: np.ndarray,
    mz2: np.ndarray,
    tolerance_ppm: float = 10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    基于 ppm 容差进行峰对齐

    Args:
        mz1: 谱图1的 mz 值
        mz2: 谱图2的 mz 值
        tolerance_ppm: ppm 容差

    Returns:
        (matched_mz1, matched_mz2): 对齐的峰对
    """
    matched1 = []
    matched2 = []

    for mz_val in mz1:
        tolerance = mz_val * tolerance_ppm / 1e6
        diffs = np.abs(mz2 - mz_val)
        min_idx = np.argmin(diffs)

        if diffs[min_idx] <= tolerance:
            matched1.append(mz_val)
            matched2.append(mz2[min_idx])

    return np.array(matched1), np.array(matched2)


# ============================================================
# 核心匹配算法
# ============================================================

class SpectrumMatcher:
    """质谱相似度匹配器"""

    def __init__(
        self,
        algorithm: str = "modified_cosine",
        matching_method: str = "greedy",
        tolerance_ppm: float = 10,
        min_matched_peaks: int = 6,
        intensity_weight: str = "none"
    ):
        """
        初始化匹配器

        Args:
            algorithm: 算法类型
                - "modified_cosine": 改进余弦相似度（默认）
                - "cosine": 标准余弦相似度
                - "weighted_cosine": 加权余弦相似度
                - "spectral_entropy": 谱图熵
            matching_method: 匹配方法
                - "greedy": 贪心匹配（快）
                - "hungarian": 匈牙利算法（精确）
            tolerance_ppm: ppm 容差（默认 10）
            min_matched_peaks: 最小匹配峰数（默认 6）
            intensity_weight: 强度加权
                - "none": 不加权
                - "sqrt": 平方根加权
        """
        self.algorithm = algorithm
        self.matching_method = matching_method
        self.tolerance_ppm = tolerance_ppm
        self.min_matched_peaks = min_matched_peaks

        # 强度加权
        if intensity_weight == "sqrt":
            self.intensity_power = 0.5
        else:
            self.intensity_power = 1.0

        self._init_similarity_function()

    def _init_similarity_function(self):
        """初始化相似度函数"""
        if self.algorithm in ["modified_cosine", "cosine", "weighted_cosine"]:
            if self.matching_method == "greedy":
                if self.algorithm == "modified_cosine":
                    self._similarity_fn = ModifiedCosineGreedy(
                        tolerance=self.tolerance_ppm / 1e6 * 1000,  # ppm to Da approximation
                        intensity_power=self.intensity_power
                    )
                else:
                    self._similarity_fn = CosineGreedy(
                        tolerance=self.tolerance_ppm / 1e6 * 1000,
                        intensity_power=self.intensity_power
                    )
            else:  # hungarian
                if self.algorithm == "modified_cosine":
                    self._similarity_fn = ModifiedCosineHungarian(
                        tolerance=self.tolerance_ppm / 1e6 * 1000,
                        intensity_power=self.intensity_power
                    )
                else:
                    self._similarity_fn = CosineHungarian(
                        tolerance=self.tolerance_ppm / 1e6 * 1000,
                        intensity_power=self.intensity_power
                    )

        elif self.algorithm == "spectral_entropy":
            self._similarity_fn = FlashSimilarity(
                score_type="spectral_entropy",
                tolerance=self.tolerance_ppm / 1e6 * 1000
            )

    def pair(self, spec1: Spectrum, spec2: Spectrum) -> Dict:
        """
        计算两个谱图的相似度

        Args:
            spec1: 谱图1
            spec2: 谱图2

        Returns:
            dict: {
                "score": float,
                "matches": int,
                "algorithm": str,
                "parameters": dict
            }
        """
        if self.algorithm == "spectral_entropy":
            result = self._similarity_fn.pair(spec1, spec2)
            score = result.get("score", 0.0)
            matches = result.get("matches", 0)
        else:
            result = self._similarity_fn.pair(spec1, spec2)
            score = result.get("score", 0.0)
            matches = result.get("matches", 0)

        # 检查最小匹配峰数
        if matches < self.min_matched_peaks:
            warnings.warn(
                f"匹配峰数 ({matches}) 低于最小阈值 ({self.min_matched_peaks})，"
                f"结果可能不可靠。"
            )

        return {
            "score": float(score),
            "matches": int(matches),
            "algorithm": self.algorithm,
            "parameters": {
                "matching_method": self.matching_method,
                "tolerance_ppm": self.tolerance_ppm,
                "min_matched_peaks": self.min_matched_peaks,
                "intensity_weight": "sqrt" if self.intensity_power == 0.5 else "none"
            }
        }

    def batch_compare(
        self,
        spectra_list: List[Spectrum],
        reference: Spectrum
    ) -> List[Dict]:
        """
        批量比较多个谱图与参考谱图的相似度

        Args:
            spectra_list: 待比较的谱图列表
            reference: 参考谱图

        Returns:
            结果列表
        """
        results = []
        for spec in spectra_list:
            result = self.pair(reference, spec)
            results.append(result)

        # 按相似度降序排序
        results.sort(key=lambda x: x["score"], reverse=True)

        return results


# ============================================================
# 便捷函数
# ============================================================

def compare_spectra(
    file1: str,
    file2: str,
    algorithm: str = "modified_cosine",
    matching_method: str = "greedy",
    tolerance_ppm: float = 10,
    min_matched_peaks: int = 6,
    intensity_weight: str = "none",
    precursor_mz: float = 0.0
) -> Dict:
    """
    比较两个质谱文件的相似度

    Args:
        file1: 文件路径1
        file2: 文件路径2
        algorithm: 算法类型
        matching_method: 匹配方法
        tolerance_ppm: ppm 容差
        min_matched_peaks: 最小匹配峰数
        intensity_weight: 强度加权
        precursor_mz: 前体离子 mz

    Returns:
        相似度结果
    """
    # 检查依赖
    dep_check = check_dependencies()
    if dep_check["status"] != "ready":
        raise ImportError(
            f"缺少依赖包: {dep_check['packages']}\n"
            f"请运行: {dep_check['install_command']}"
        )

    # 读取谱图
    spec1 = read_spectrum_from_csv(file1, precursor_mz=precursor_mz)
    spec2 = read_spectrum_from_csv(file2, precursor_mz=precursor_mz)

    # 创建匹配器
    matcher = SpectrumMatcher(
        algorithm=algorithm,
        matching_method=matching_method,
        tolerance_ppm=tolerance_ppm,
        min_matched_peaks=min_matched_peaks,
        intensity_weight=intensity_weight
    )

    # 执行匹配
    return matcher.pair(spec1, spec2)


# ============================================================
# 主程序入口
# ============================================================

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("MS/MS 质谱相似度匹配工具")
    print("=" * 60)

    # 检查依赖
    dep_check = check_dependencies()
    if dep_check["status"] != "ready":
        print(f"\n[警告] 缺少依赖包: {dep_check['packages']}")
        print(f"请运行安装命令: {dep_check['install_command']}")
    else:
        print("\n[OK] 所有依赖包已安装")

    print("\n使用方法:")
    print("  from core_matching import compare_spectra, SpectrumMatcher")
    print("  result = compare_spectra('spec1.csv', 'spec2.csv')")
    print("=" * 60)
