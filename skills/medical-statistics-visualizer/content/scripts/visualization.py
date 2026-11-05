"""
医学统计 - 可视化模块
功能：热力图、箱线图、专业图表样式设置
依赖：matplotlib, seaborn, pandas, numpy
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# SCI期刊标准配色方案
SCIHUBS_COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'neutral': '#6C757D',
    'background': '#F8F9FA'
}

SCIHUBS_PALETTE = [
    '#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B',
    '#95C623', '#7B2D26', '#4A6FA5', '#9B59B6', '#1ABC9C'
]

SCIHUBS_FONT = {
    'family': 'Arial',
    'size': {
        'title': 14,
        'subtitle': 12,
        'label': 10,
        'tick': 9,
        'legend': 9,
        'annotation': 8
    }
}


def set_sci_style():
    """设置SCI期刊标准全局样式"""
    plt.rcParams.update({
        'font.family': SCIHUBS_FONT['family'],
        'font.size': SCIHUBS_FONT['size']['label'],
        'axes.labelsize': SCIHUBS_FONT['size']['label'],
        'axes.titlesize': SCIHUBS_FONT['size']['subtitle'],
        'xtick.labelsize': SCIHUBS_FONT['size']['tick'],
        'ytick.labelsize': SCIHUBS_FONT['size']['tick'],
        'legend.fontsize': SCIHUBS_FONT['size']['legend'],
        'figure.titlesize': SCIHUBS_FONT['size']['title'],
        'axes.linewidth': 0.8,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linewidth': 0.5,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1
    })


class VisualizationEngine:
    """可视化引擎"""

    def __init__(self):
        set_sci_style()

    def heatmap(self, data: pd.DataFrame, output_path: str,
                title: str = 'Heatmap', cmap: str = 'RdBu_r',
                annot: bool = True, fmt: str = '.2f',
                center: Optional[float] = None,
                figsize: Tuple = (10, 8),
                labels: Optional[Dict] = None,
                show_clustering: bool = False) -> str:
        """
        绘制热力图

        Args:
            data: 数据框（矩阵形式）
            output_path: 输出图片路径
            title: 图表标题
            cmap: 配色方案
            annot: 是否显示数值
            fmt: 数值格式
            center: 颜色中心值
            figsize: 图表尺寸
            labels: 行列标签映射
            show_clustering: 是否显示聚类

        Returns:
            输出文件路径
        """
        fig, ax = plt.subplots(figsize=figsize)

        plot_data = data.copy()
        if labels:
            plot_data.index = [labels.get(x, x) for x in plot_data.index]
            plot_data.columns = [labels.get(x, x) for x in plot_data.columns]

        if show_clustering:
            sns.clustermap(plot_data, cmap=cmap, center=center,
                          annot=annot, fmt=fmt, figsize=figsize,
                          dendrogram_ratio=(0.1, 0.1),
                          cbar_pos=(0.02, 0.8, 0.03, 0.15))
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        else:
            sns.heatmap(plot_data, cmap=cmap, center=center,
                       annot=annot, fmt=fmt, square=True,
                       linewidths=0.5, ax=ax,
                       cbar_kws={'shrink': 0.8, 'label': ''})

            ax.set_title(title, fontsize=SCIHUBS_FONT['size']['title'],
                        fontweight='bold', pad=15)

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path

    def correlation_heatmap(self, data: pd.DataFrame, columns: List[str],
                           output_path: str, method: str = 'pearson',
                           title: str = 'Correlation Matrix') -> str:
        """
        绘制相关性热力图

        Args:
            data: 数据框
            columns: 要分析的列
            output_path: 输出路径
            method: 相关性方法
            title: 标题

        Returns:
            输出文件路径
        """
        corr = data[columns].corr(method=method)

        fig, ax = plt.subplots(figsize=(max(8, len(columns) * 0.8), max(6, len(columns) * 0.7)))

        mask = np.triu(np.ones_like(corr, dtype=bool))

        sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
                   cmap='RdBu_r', center=0, square=True,
                   linewidths=0.5, ax=ax, vmin=-1, vmax=1,
                   annot_kws={'size': 9},
                   cbar_kws={'shrink': 0.8, 'label': f'{method.capitalize()} Correlation'})

        ax.set_title(title, fontsize=SCIHUBS_FONT['size']['title'],
                    fontweight='bold', pad=15)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path

    def boxplot_with_points(self, data: pd.DataFrame, x_col: str,
                           y_col: str, output_path: str,
                           title: str = '', palette: Optional[List] = None,
                           add_jitter: bool = True) -> str:
        """
        箱线图+散点叠加

        Args:
            data: 数据框
            x_col: 分组列
            y_col: 数值列
            output_path: 输出路径
            title: 标题
            palette: 配色
            add_jitter: 是否添加散点抖动

        Returns:
            输出文件路径
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        if palette is None:
            palette = SCIHUBS_PALETTE

        # 箱线图
        box = sns.boxplot(data=data, x=x_col, y=y_col, palette=palette,
                         width=0.5, ax=ax,
                         boxprops={'linewidth': 1.2},
                         medianprops={'color': 'black', 'linewidth': 1.5},
                         whiskerprops={'linewidth': 1.2},
                         capprops={'linewidth': 1.2},
                         fliersize=0)  # 隐藏离群点

        # 叠加散点
        if add_jitter:
            sns.stripplot(data=data, x=x_col, y=y_col, palette=palette,
                         size=4, alpha=0.4, ax=ax, jitter=True)

        ax.set_xlabel(x_col, fontsize=SCIHUBS_FONT['size']['label'])
        ax.set_ylabel(y_col, fontsize=SCIHUBS_FONT['size']['label'])

        if title:
            ax.set_title(title, fontsize=SCIHUBS_FONT['size']['subtitle'],
                        fontweight='bold', pad=10)

        sns.despine()
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path

    def grouped_barplot(self, data: pd.DataFrame, x_col: str,
                       y_cols: List[str], output_path: str,
                       title: str = '', ylabel: str = '') -> str:
        """
        分组柱状图

        Args:
            data: 数据框
            x_col: X轴分类列
            y_cols: Y轴数值列列表
            output_path: 输出路径
            title: 标题
            ylabel: Y轴标签

        Returns:
            输出文件路径
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        n_groups = len(data)
        n_bars = len(y_cols)
        bar_width = 0.8 / n_bars

        x = np.arange(n_groups)

        for i, col in enumerate(y_cols):
            offset = (i - n_bars / 2 + 0.5) * bar_width
            bars = ax.bar(x + offset, data[col], bar_width * 0.95,
                         label=col, color=SCIHUBS_PALETTE[i % len(SCIHUBS_PALETTE)],
                         edgecolor='black', linewidth=0.5)

            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3), textcoords="offset points",
                           ha='center', va='bottom', fontsize=8)

        ax.set_xticks(x)
        ax.set_xticklabels(data[x_col], fontsize=SCIHUBS_FONT['size']['tick'])
        ax.set_ylabel(ylabel, fontsize=SCIHUBS_FONT['size']['label'])
        ax.legend(loc='upper right', frameon=False, fontsize=SCIHUBS_FONT['size']['legend'])

        if title:
            ax.set_title(title, fontsize=SCIHUBS_FONT['size']['subtitle'],
                        fontweight='bold', pad=10)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path

    def survival_risk_table(self, kmf_data: List[Dict], time_points: List[float],
                           group_names: List[str], output_path: str) -> str:
        """
        绘制带风险表的可视化

        Args:
            kmf_data: KM估计器列表
            time_points: 时间点列表
            group_names: 分组名称
            output_path: 输出路径

        Returns:
            输出文件路径
        """
        fig, (ax_table, ax_plot) = plt.subplots(2, 1, figsize=(10, 8),
                                                gridspec_kw={'height_ratios': [1, 3]})

        # 风险表
        n_groups = len(group_names)
        n_times = len(time_points)

        # 表头
        ax_table.axis('off')
        table_data = [['Time'] + [f'{t:.0f}' for t in time_points]]

        for name, kmf in zip(group_names, kmf_data):
            n_at_risk = []
            for t in time_points:
                try:
                    n = kmf.survival_function_at_times(t).values[0]
                    # 估算风险人数（简化）
                    n_at = int(kmf.event_observed.shape[0] * (1 - n))
                except:
                    n_at = 'NA'
                n_at_risk.append(n_at)
            table_data.append([name] + n_at_risk)

        table = ax_table.table(cellText=table_data, loc='center',
                               cellLoc='center', colWidths=[0.2] + [0.8 / n_times] * n_times)
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)

        # 设置表头样式
        for i in range(n_times + 1):
            table[(0, i)].set_facecolor(SCIHUBS_COLORS['primary'])
            table[(0, i)].set_text_props(color='white', fontweight='bold')

        # 生存曲线
        ax_plot.set_position([0.1, 0.1, 0.85, 0.5])

        for i, (name, kmf) in enumerate(zip(group_names, kmf_data)):
            kmf.plot_survival_function(ax=ax_plot, ci_show=True,
                                      color=SCIHUBS_PALETTE[i % len(SCIHUBS_PALETTE)],
                                      label=name)

        ax_plot.set_xlabel('Time', fontsize=SCIHUBS_FONT['size']['label'])
        ax_plot.set_ylabel('Survival Probability', fontsize=SCIHUBS_FONT['size']['label'])
        ax_plot.legend(loc='lower left', frameon=False, fontsize=SCIHUBS_FONT['size']['legend'])
        ax_plot.spines['top'].set_visible(False)
        ax_plot.spines['right'].set_visible(False)

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path


def demo():
    """演示函数"""
    import os
    os.makedirs('/workspace/temp-skills/medical-statistics-visualizer/assets', exist_ok=True)

    # 相关性热力图
    np.random.seed(42)
    n_markers = 8
    n_samples = 100

    demo_data = pd.DataFrame(
        np.random.randn(n_samples, n_markers),
        columns=['CEA', 'CA19-9', 'AFP', 'CA125', 'CA15-3', 'NSE', 'CYFRA21-1', 'ProGRP']
    )

    vis = VisualizationEngine()
    vis.correlation_heatmap(
        demo_data,
        columns=demo_data.columns.tolist(),
        output_path='/workspace/temp-skills/medical-statistics-visualizer/assets/corr_heatmap.png'
    )

    # 箱线图+散点
    box_data = pd.DataFrame({
        'Group': ['A'] * 50 + ['B'] * 50,
        'Value': np.random.randn(50) + 2 + np.concatenate([
            np.zeros(25),
            np.ones(25) * 0.5
        ])
    })

    vis.boxplot_with_points(
        box_data, 'Group', 'Value',
        output_path='/workspace/temp-skills/medical-statistics-visualizer/assets/boxplot_demo.png'
    )

    print("可视化示例完成")


if __name__ == '__main__':
    demo()
