#!/usr/bin/env python3
"""
电力客户用电数据可视化脚本
功能：基于统计结果生成各指标的月度趋势图
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrendVisualizer:
    """趋势图可视化器"""

    # 图表配置
    METRICS_CONFIG = {
        # 总量指标
        '本期电量': {
            'column': '本期电量',
            'unit': 'kWh',
            'color': '#2E86AB',
            'filename': 'total_power_trend.png'
        },
        '本期电费': {
            'column': '本期电费',
            'unit': '元',
            'color': '#A23B72',
            'filename': 'total_cost_trend.png'
        },
        '平均电价': {
            'column': '平均电价',
            'unit': '元/kWh',
            'color': '#F18F01',
            'filename': 'avg_price_trend.png'
        },

        # 尖段指标
        '尖段_计费电量': {
            'column': '尖段_计费电量',
            'unit': 'kWh',
            'color': '#C73E1D',
            'filename': 'peak_kwh_trend.png'
        },
        '尖段_计费标准': {
            'column': '尖段_计费标准',
            'unit': '元/kWh',
            'color': '#E84A5F',
            'filename': 'peak_rate_trend.png'
        },
        '尖段_电费': {
            'column': '尖段_电费',
            'unit': '元',
            'color': '#FF847C',
            'filename': 'peak_cost_trend.png'
        },

        # 峰段指标
        '峰段_计费电量': {
            'column': '峰段_计费电量',
            'unit': 'kWh',
            'color': '#F39C12',
            'filename': 'shoulder_kwh_trend.png'
        },
        '峰段_计费标准': {
            'column': '峰段_计费标准',
            'unit': '元/kWh',
            'color': '#F1C40F',
            'filename': 'shoulder_rate_trend.png'
        },
        '峰段_电费': {
            'column': '峰段_电费',
            'unit': '元',
            'color': '#F5B041',
            'filename': 'shoulder_cost_trend.png'
        },

        # 平段指标
        '平段_计费电量': {
            'column': '平段_计费电量',
            'unit': 'kWh',
            'color': '#27AE60',
            'filename': 'flat_kwh_trend.png'
        },
        '平段_计费标准': {
            'column': '平段_计费标准',
            'unit': '元/kWh',
            'color': '#2ECC71',
            'filename': 'flat_rate_trend.png'
        },
        '平段_电费': {
            'column': '平段_电费',
            'unit': '元',
            'color': '#58D68D',
            'filename': 'flat_cost_trend.png'
        },

        # 谷段指标
        '谷段_计费电量': {
            'column': '谷段_计费电量',
            'unit': 'kWh',
            'color': '#3498DB',
            'filename': 'valley_kwh_trend.png'
        },
        '谷段_计费标准': {
            'column': '谷段_计费标准',
            'unit': '元/kWh',
            'color': '#5DADE2',
            'filename': 'valley_rate_trend.png'
        },
        '谷段_电费': {
            'column': '谷段_电费',
            'unit': '元',
            'color': '#85C1E9',
            'filename': 'valley_cost_trend.png'
        },

        # 其他费用
        '输配容需量电费': {
            'column': '输配容需量电费',
            'unit': '元',
            'color': '#8E44AD',
            'filename': 'capacity_cost_trend.png'
        },
        '功率因数调整电费': {
            'column': '功率因数调整电费',
            'unit': '元',
            'color': '#9B59B6',
            'filename': 'power_factor_cost_trend.png'
        }
    }

    def __init__(self, statistics_file: str, output_dir: str = "output/charts",
                 figsize: Tuple[int, int] = (12, 6), dpi: int = 100):
        """
        初始化可视化器

        Args:
            statistics_file: 统计结果CSV文件路径
            output_dir: 图表输出目录
            figsize: 图表尺寸，默认为 (12, 6)
            dpi: 图表分辨率，默认为 100
        """
        self.statistics_file = Path(statistics_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.figsize = figsize
        self.dpi = dpi

        # 设置中文字体
        self._setup_chinese_font()

    def _setup_chinese_font(self):
        """配置中文字体支持"""
        # 尝试查找可用的中文字体
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/System/Library/Fonts/PingFang.ttc',  # macOS
            'C:/Windows/Fonts/simhei.ttf',  # Windows
        ]

        font_found = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                plt.rcParams['font.sans-serif'] = [font_path]
                plt.rcParams['axes.unicode_minus'] = False
                font_found = True
                logger.info(f"使用字体: {font_path}")
                break

        if not font_found:
            # 使用系统默认字体
            logger.warning("未找到中文字体，使用默认字体")
            # 尝试使用可用的中文字体名
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            chinese_fonts = [f for f in available_fonts if any(
                kw in f.lower() for kw in ['hei', 'song', 'kai', 'ming', 'noto']
            )]
            if chinese_fonts:
                plt.rcParams['font.sans-serif'] = [chinese_fonts[0]]
                plt.rcParams['axes.unicode_minus'] = False
            else:
                logger.warning("无可用中文字体，图表中文可能显示异常")

    def _load_data(self) -> Optional[pd.DataFrame]:
        """
        加载统计数据

        Returns:
            DataFrame，失败返回None
        """
        try:
            df = pd.read_csv(self.statistics_file, encoding='utf-8-sig')
            logger.info(f"加载数据: {len(df)} 行")
            return df
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return None

    def _create_single_chart(self, df: pd.DataFrame, metric_name: str,
                            config: Dict) -> Optional[str]:
        """
        创建单个指标的图表

        Args:
            df: 数据框
            metric_name: 指标名称（中文）
            config: 指标配置

        Returns:
            保存的文件路径，失败返回None
        """
        column = config['column']
        unit = config['unit']
        color = config['color']
        filename = config['filename']

        # 检查列是否存在
        if column not in df.columns:
            logger.warning(f"列不存在: {column}")
            return None

        # 创建图表
        fig, ax = plt.subplots(figsize=self.figsize)

        # 绘制折线图
        months = df['月份'].tolist()
        values = df[column].tolist()

        # 绘制主折线
        ax.plot(months, values, marker='o', markersize=8,
                linewidth=2, color=color, label=metric_name)

        # 填充区域
        ax.fill_between(months, values, alpha=0.3, color=color)

        # 设置标题和标签
        ax.set_title(f'{metric_name}趋势图', fontsize=16, fontweight='bold',
                    pad=20)
        ax.set_xlabel('月份', fontsize=12)
        ax.set_ylabel(f'{metric_name} ({unit})', fontsize=12)

        # 设置x轴刻度
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(months, rotation=45, ha='right')

        # 添加网格线
        ax.grid(True, linestyle='--', alpha=0.7)

        # 添加数据标签
        for i, (month, value) in enumerate(zip(months, values)):
            ax.annotate(f'{value:.2f}',
                       xy=(i, value),
                       xytext=(0, 10),
                       textcoords='offset points',
                       ha='center',
                       fontsize=9,
                       color=color)

        # 调整布局
        plt.tight_layout()

        # 保存图表
        output_path = self.output_dir / filename
        try:
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            logger.info(f"保存图表: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"保存图表失败: {e}")
            return None
        finally:
            plt.close(fig)

    def visualize(self, metrics: Optional[List[str]] = None) -> List[str]:
        """
        生成趋势图

        Args:
            metrics: 要绘制的指标列表，None表示绘制所有指标

        Returns:
            生成的图表文件路径列表
        """
        # 加载数据
        df = self._load_data()
        if df is None or df.empty:
            logger.error("没有可用的数据")
            return []

        # 确定要绘制的指标
        if metrics is None:
            metrics_to_plot = list(self.METRICS_CONFIG.keys())
        else:
            metrics_to_plot = [m for m in metrics if m in self.METRICS_CONFIG]

        logger.info(f"开始绘制 {len(metrics_to_plot)} 个指标的趋势图")

        # 绘制图表
        output_files = []
        for metric_name in metrics_to_plot:
            config = self.METRICS_CONFIG[metric_name]
            output_path = self._create_single_chart(df, metric_name, config)
            if output_path:
                output_files.append(output_path)

        logger.info(f"成功生成 {len(output_files)} 个图表")
        return output_files

    def create_summary_dashboard(self, output_filename: str = 'dashboard.png') -> str:
        """
        创建汇总仪表板（可选）

        Args:
            output_filename: 输出文件名

        Returns:
            仪表板文件路径
        """
        df = self._load_data()
        if df is None or df.empty:
            logger.error("没有可用的数据")
            return ""

        # 创建子图布局
        fig, axes = plt.subplots(4, 3, figsize=(20, 16))
        axes = axes.flatten()

        # 选择主要指标
        main_metrics = [
            '本期电量', '本期电费', '平均电价',
            '尖段_电费', '峰段_电费', '平段_电费', '谷段_电费',
            '尖段_计费电量', '峰段_计费电量', '平段_计费电量', '谷段_计费电量',
            '输配容需量电费'
        ]

        months = df['月份'].tolist()

        for idx, metric_name in enumerate(main_metrics):
            if idx >= len(axes):
                break

            ax = axes[idx]
            config = self.METRICS_CONFIG.get(metric_name)

            if config and config['column'] in df.columns:
                values = df[config['column']].tolist()
                color = config['color']

                ax.plot(months, values, marker='o', linewidth=2,
                       color=color)
                ax.fill_between(months, values, alpha=0.3, color=color)
                ax.set_title(metric_name, fontsize=10, fontweight='bold')
                ax.set_xticks(range(len(months)))
                ax.set_xticklabels(months, rotation=45, ha='right',
                                  fontsize=8)
                ax.grid(True, linestyle='--', alpha=0.5)

        # 隐藏多余的子图
        for idx in range(len(main_metrics), len(axes)):
            axes[idx].set_visible(False)

        # 调整布局
        plt.suptitle('用电数据分析汇总仪表板', fontsize=18, fontweight='bold',
                    y=1.02)
        plt.tight_layout()

        # 保存
        output_path = self.output_dir / output_filename
        try:
            plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            logger.info(f"保存汇总仪表板: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"保存仪表板失败: {e}")
            return ""
        finally:
            plt.close(fig)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='电力用电数据趋势可视化')
    parser.add_argument('statistics_file', help='统计结果CSV文件路径')
    parser.add_argument('-o', '--output', default='output/charts',
                        help='图表输出目录')
    parser.add_argument('--dpi', type=int, default=100,
                        help='图表分辨率')
    parser.add_argument('--width', type=int, default=12,
                        help='图表宽度（英寸）')
    parser.add_argument('--height', type=int, default=6,
                        help='图表高度（英寸）')
    parser.add_argument('--dashboard', action='store_true',
                        help='同时生成汇总仪表板')

    args = parser.parse_args()

    visualizer = TrendVisualizer(
        args.statistics_file,
        args.output,
        figsize=(args.width, args.height),
        dpi=args.dpi
    )

    # 生成趋势图
    output_files = visualizer.visualize()

    if output_files:
        print(f"\n成功生成 {len(output_files)} 个趋势图:")
        for f in output_files:
            print(f"  - {f}")

        # 生成仪表板（可选）
        if args.dashboard:
            dashboard_path = visualizer.create_summary_dashboard()
            if dashboard_path:
                print(f"\n汇总仪表板: {dashboard_path}")
    else:
        print("未能生成图表，请检查数据文件")


if __name__ == '__main__':
    main()
