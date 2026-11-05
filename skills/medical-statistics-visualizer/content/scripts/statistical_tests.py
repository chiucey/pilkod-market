"""
医学统计 - 统计检验模块
功能：t检验、Mann-Whitney U检验、卡方检验、Fisher精确检验
依赖：scipy, statsmodels, pandas, numpy
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import ttest_ind, mannwhitneyu, chi2_contingency, fisher_exact, shapiro
from statsmodels.stats.weightstats import ttest_ind as welch_ttest
from typing import Dict, Tuple, Optional, List
import warnings
warnings.filterwarnings('ignore')

# SCI期刊标准样式
SCIHUBS_COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
SCIHUBS_FONT = {'family': 'Arial', 'size': 10}


class StatisticalTester:
    """统计检验器"""

    def __init__(self, alpha: float = 0.05):
        """
        初始化检验器

        Args:
            alpha: 显著性水平
        """
        self.alpha = alpha
        self.results = {}

    def _normality_test(self, data: np.ndarray) -> Tuple[float, bool]:
        """正态性检验（Shapiro-Wilk）"""
        if len(data) < 3:
            return 1.0, False
        if len(data) > 5000:
            data = np.random.choice(data, 5000, replace=False)
        stat, p = shapiro(data)
        return p, p > self.alpha

    def _variance_homogeneity(self, group1: np.ndarray, group2: np.ndarray) -> Tuple[float, bool]:
        """方差齐性检验（Levene）"""
        stat, p = stats.levene(group1, group2)
        return p, p > self.alpha

    def _interpret_pvalue(self, p_value: float) -> str:
        """解释P值"""
        if p_value < 0.001:
            return "极显著差异 (P < 0.001)"
        elif p_value < 0.01:
            return "高度显著差异 (P < 0.01)"
        elif p_value < self.alpha:
            return "显著差异 (P < 0.05)"
        else:
            return "无显著差异 (P >= 0.05)"

    def compare_continuous(self, data: pd.DataFrame, value_col: str,
                          group_col: str, groups: Optional[List] = None,
                          output_path: Optional[str] = None,
                          show_points: bool = True) -> Dict:
        """
        连续变量组间比较

        Args:
            data: 数据框
            value_col: 数值列名
            group_col: 分组列名
            groups: 要比较的分组列表
            output_path: 输出图片路径
            show_points: 是否叠加散点

        Returns:
            检验结果字典
        """
        if groups is None:
            groups = data[group_col].unique()

        if len(groups) != 2:
            raise ValueError("当前仅支持两组比较")

        group1_data = data[data[group_col] == groups[0]][value_col].dropna()
        group2_data = data[data[group_col] == groups[1]][value_col].dropna()

        results = {
            'groups': list(groups),
            'descriptive': {},
            'tests': {}
        }

        # 描述性统计
        for name, gdata in zip(groups, [group1_data, group2_data]):
            results['descriptive'][name] = {
                'n': len(gdata),
                'mean': gdata.mean(),
                'std': gdata.std(),
                'median': gdata.median(),
                'q25': gdata.quantile(0.25),
                'q75': gdata.quantile(0.75),
                'min': gdata.min(),
                'max': gdata.max()
            }

        # 正态性检验
        norm1 = self._normality_test(group1_data.values)
        norm2 = self._normality_test(group2_data.values)
        results['normality'] = {
            groups[0]: {'p': norm1[0], 'normal': norm1[1]},
            groups[1]: {'p': norm2[0], 'normal': norm2[1]}
        }

        # 选择检验方法
        if norm1[1] and norm2[1]:
            # 两组都符合正态分布
            equal_var = self._variance_homogeneity(group1_data.values, group2_data.values)[1]

            if equal_var:
                # Student's t检验
                t_stat, p_value = ttest_ind(group1_data, group2_data)
                test_name = "Student's t-test"
            else:
                # Welch's t检验
                t_stat, p_value, df = welch_ttest(group1_data, group2_data)
                test_name = "Welch's t-test"

            results['tests']['parametric'] = {
                'test': test_name,
                'statistic': t_stat,
                'p_value': p_value,
                'interpretation': self._interpret_pvalue(p_value)
            }
        else:
            # 非参数检验 Mann-Whitney U
            u_stat, p_value = mannwhitneyu(group1_data, group2_data, alternative='two-sided')
            results['tests']['non_parametric'] = {
                'test': 'Mann-Whitney U test',
                'statistic': u_stat,
                'p_value': p_value,
                'interpretation': self._interpret_pvalue(p_value)
            }

        # 绘制箱线图
        if output_path:
            self._plot_boxstrip(data, value_col, group_col, groups, output_path, show_points)

        self.results['continuous_comparison'] = results
        return results

    def _plot_boxstrip(self, data: pd.DataFrame, value_col: str, group_col: str,
                       groups: List, output_path: str, show_points: bool) -> None:
        """绘制箱线图+散点图"""
        fig, ax = plt.subplots(figsize=(8, 6))

        plot_data = data[data[group_col].isin(groups)]

        # 箱线图
        box = ax.boxplot([plot_data[plot_data[group_col] == g][value_col].dropna()
                         for g in groups],
                        labels=groups, patch_artist=True,
                        boxprops=dict(linewidth=1.2),
                        medianprops=dict(color='black', linewidth=1.5),
                        whiskerprops=dict(linewidth=1.2),
                        capprops=dict(linewidth=1.2))

        # 设置箱体颜色
        for patch, color in zip(box['boxes'], SCIHUBS_COLORS[:len(groups)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)

        # 叠加散点
        if show_points:
            for i, group in enumerate(groups):
                y = plot_data[plot_data[group_col] == group][value_col].dropna()
                x = np.random.normal(i + 1, 0.04, len(y))
                ax.scatter(x, y, alpha=0.4, s=20, color='black', zorder=3)

        ax.set_ylabel(value_col, **SCIHUBS_FONT)
        ax.set_xlabel(group_col, **SCIHUBS_FONT)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=10)

        # 添加P值标注
        if 'parametric' in self.results.get('continuous_comparison', {}).get('tests', {}):
            p_val = self.results['continuous_comparison']['tests']['parametric']['p_value']
        elif 'non_parametric' in self.results.get('continuous_comparison', {}).get('tests', {}):
            p_val = self.results['continuous_comparison']['tests']['non_parametric']['p_value']
        else:
            p_val = None

        if p_val is not None:
            max_y = max(plot_data[value_col].max(), 1)
            ax.annotate(f'P = {p_val:.4f}', xy=(0.95, 0.95),
                       xycoords='axes fraction', ha='right', va='top',
                       fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def compare_categorical(self, data: pd.DataFrame, value_col: str,
                           group_col: str, groups: Optional[List] = None,
                           output_path: Optional[str] = None) -> Dict:
        """
        分类变量组间比较（卡方检验/Fisher精确检验）

        Args:
            data: 数据框
            value_col: 分类型结局列名
            group_col: 分组列名
            groups: 要比较的分组列表
            output_path: 输出图片路径

        Returns:
            检验结果字典
        """
        if groups is None:
            groups = data[group_col].unique()

        plot_data = data[data[group_col].isin(groups)]

        # 创建列联表
        contingency_table = pd.crosstab(plot_data[group_col], plot_data[value_col])

        results = {
            'groups': list(groups),
            'contingency_table': contingency_table.to_dict(),
            'descriptive': {}
        }

        # 描述性统计
        for group in groups:
            group_data = plot_data[plot_data[group_col] == group]
            total = len(group_data)
            results['descriptive'][group] = {
                'total': total
            }

        # 计算每个类别的比例
        proportions = contingency_table.div(contingency_table.sum(axis=1), axis=0)
        results['proportions'] = proportions.to_dict()

        # 选择检验方法
        n_total = contingency_table.values.sum()
        expected_min = contingency_table.values.min()

        if expected_min < 5 or n_total < 40:
            # Fisher精确检验
            odds_ratio, p_value = fisher_exact(contingency_table)
            results['tests'] = {
                'test': "Fisher's exact test",
                'odds_ratio': odds_ratio,
                'p_value': p_value,
                'interpretation': self._interpret_pvalue(p_value)
            }
        else:
            # 卡方检验
            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
            results['tests'] = {
                'test': 'Chi-square test',
                'chi2': chi2,
                'dof': dof,
                'p_value': p_value,
                'interpretation': self._interpret_pvalue(p_value)
            }

        # 绘制分组柱状图
        if output_path:
            self._plot_grouped_bar(contingency_table, output_path)

        self.results['categorical_comparison'] = results
        return results

    def _plot_grouped_bar(self, contingency_table: pd.DataFrame, output_path: str) -> None:
        """绘制分组柱状图"""
        fig, ax = plt.subplots(figsize=(10, 6))

        contingency_table.plot(kind='bar', ax=ax, width=0.7,
                               color=SCIHUBS_COLORS[:len(contingency_table.columns)],
                               edgecolor='black', linewidth=0.5)

        ax.set_xlabel(contingency_table.index.name or 'Group', **SCIHUBS_FONT)
        ax.set_ylabel('Count', **SCIHUBS_FONT)
        ax.legend(title=contingency_table.columns.name or 'Category',
                 loc='upper right', frameon=False)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(labelsize=10)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def correlation_analysis(self, data: pd.DataFrame, columns: List[str],
                            method: str = 'pearson') -> Dict:
        """
        相关性分析

        Args:
            data: 数据框
            columns: 要分析的列
            method: 'pearson' 或 'spearman'
            output_path: 输出图片路径

        Returns:
            相关性矩阵和热力图路径
        """
        if method == 'pearson':
            corr_matrix = data[columns].corr(method='pearson')
        else:
            corr_matrix = data[columns].corr(method='spearman')

        results = {
            'method': method,
            'correlation_matrix': corr_matrix.to_dict()
        }

        # 绘制热力图
        fig, ax = plt.subplots(figsize=(max(6, len(columns) * 0.8), max(5, len(columns) * 0.7)))

        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f',
                    cmap='RdBu_r', center=0, square=True,
                    linewidths=0.5, ax=ax, vmin=-1, vmax=1,
                    annot_kws={'size': 9})

        ax.set_title(f'{method.capitalize()} Correlation Matrix', fontsize=12, pad=10)
        plt.tight_layout()
        output_path = '/workspace/temp-skills/medical-statistics-visualizer/assets/correlation_heatmap.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        results['heatmap_path'] = output_path
        self.results['correlation'] = results
        return results

    def generate_report(self) -> str:
        """生成统计检验报告"""
        report = ["## 统计检验报告\n"]

        if 'continuous_comparison' in self.results:
            res = self.results['continuous_comparison']
            report.append("### 连续变量组间比较\n\n")

            # 描述性统计
            report.append("**描述性统计**\n\n")
            report.append("| 指标 | " + " | ".join(res['groups']) + " |\n")
            report.append("|------|" + "|".join(["---"] * len(res['groups'])) + "|\n")

            stats_keys = ['n', 'mean ± SD', 'median (IQR)', 'range']
            for key in stats_keys:
                row = [key]
                for g in res['groups']:
                    d = res['descriptive'][g]
                    if key == 'n':
                        row.append(str(d['n']))
                    elif key == 'mean ± SD':
                        row.append(f"{d['mean']:.2f} ± {d['std']:.2f}")
                    elif key == 'median (IQR)':
                        row.append(f"{d['median']:.2f} ({d['q25']:.2f}-{d['q75']:.2f})")
                    elif key == 'range':
                        row.append(f"{d['min']:.2f}-{d['max']:.2f}")
                report.append("| " + " | ".join(row) + " |\n")

            # 正态性检验
            report.append("\n**正态性检验 (Shapiro-Wilk)**\n\n")
            for g, n_res in res['normality'].items():
                normal_status = "符合正态" if n_res['normal'] else "不符合正态"
                report.append(f"- {g}: P = {n_res['p']:.4f} ({normal_status})\n")

            # 检验结果
            report.append("\n**检验结果**\n\n")
            for test_type, test_res in res['tests'].items():
                report.append(f"检验方法: {test_res['test']}\n")
                if 'statistic' in test_res:
                    report.append(f"统计量: {test_res['statistic']:.4f}\n")
                report.append(f"P值: {test_res['p_value']:.4f}\n")
                report.append(f"结论: {test_res['interpretation']}\n")

        if 'categorical_comparison' in self.results:
            res = self.results['categorical_comparison']
            report.append("\n### 分类变量组间比较\n\n")

            # 列联表
            report.append("**列联表**\n\n")
            ct = pd.DataFrame(res['contingency_table'])
            report.append(ct.to_markdown() + "\n")

            # 检验结果
            report.append("\n**检验结果**\n\n")
            test_res = res['tests']
            report.append(f"检验方法: {test_res['test']}\n")
            if 'chi2' in test_res:
                report.append(f"χ² = {test_res['chi2']:.4f}, df = {test_res['dof']}\n")
            if 'odds_ratio' in test_res:
                report.append(f"Odds Ratio = {test_res['odds_ratio']:.4f}\n")
            report.append(f"P值: {test_res['p_value']:.4f}\n")
            report.append(f"结论: {test_res['interpretation']}\n")

        return ''.join(report)


def demo():
    """演示函数"""
    import os
    os.makedirs('/workspace/temp-skills/medical-statistics-visualizer/assets', exist_ok=True)

    np.random.seed(42)
    n = 100

    # 连续变量示例数据
    demo_data = pd.DataFrame({
        'group': np.random.choice(['A组', 'B组'], n),
        'CEA': np.random.lognormal(2, 0.5, n),
        'CA19_9': np.random.lognormal(3, 0.6, n)
    })

    tester = StatisticalTester()

    # 组间比较
    results = tester.compare_continuous(
        demo_data, 'CEA', 'group',
        output_path='/workspace/temp-skills/medical-statistics-visualizer/assets/boxplot_cea.png'
    )

    print("连续变量比较结果:")
    for test_type, res in results['tests'].items():
        print(f"{test_type}: P = {res['p_value']:.4f}")

    # 相关性分析
    corr_results = tester.correlation_analysis(demo_data, ['CEA', 'CA19_9'])
    print(f"\n相关性热力图已保存")

    # 生成报告
    report = tester.generate_report()
    print("\n" + report)


if __name__ == '__main__':
    demo()
