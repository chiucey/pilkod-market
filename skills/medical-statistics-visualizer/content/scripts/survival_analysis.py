"""
医学统计 - 生存分析模块
功能：Kaplan-Meier曲线、Log-rank检验、Cox比例风险回归、森林图
依赖：lifelines, matplotlib, seaborn, pandas, numpy
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from lifelines import KaplanMeierFitter, CoxPHFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# SCI期刊标准配色方案
SCIHUBS_COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#95C623', '#7B2D26']
SCIHUBS_FONT = {'family': 'Arial', 'size': 10}


class SurvivalAnalyzer:
    """生存分析器"""

    def __init__(self, figsize: Tuple = (8, 6), dpi: int = 300):
        """
        初始化分析器

        Args:
            figsize: 图表尺寸
            dpi: 输出分辨率
        """
        self.figsize = figsize
        self.dpi = dpi
        self.results = {}

    def _apply_sci_style(self, ax: plt.Axes) -> None:
        """应用SCI期刊标准样式"""
        ax.set_xlabel(ax.get_xlabel(), fontfamily='Arial', fontsize=10)
        ax.set_ylabel(ax.get_ylabel(), fontfamily='Arial', fontsize=10)
        ax.tick_params(labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        for spine in ax.spines.values():
            spine.set_linewidth(0.5)

    def kaplan_meier(self, data: pd.DataFrame, time_col: str = 'time',
                     event_col: str = 'event', group_col: Optional[str] = None,
                     groups: Optional[List] = None, output_path: Optional[str] = None,
                     show_risk_table: bool = True) -> Dict:
        """
        Kaplan-Meier生存曲线

        Args:
            data: 数据框
            time_col: 时间列名
            event_col: 事件列名（1=事件发生，0=删失）
            group_col: 分组列名（可选，单组分析）
            groups: 要分析的分组列表
            output_path: 输出图片路径
            show_risk_table: 是否显示风险表

        Returns:
            包含生存分析结果的字典
        """
        results = {'curves': {}, 'log_rank': {}}

        # 单组分析
        if group_col is None or (groups is not None and len(groups) == 1):
            kmf = KaplanMeierFitter()
            kmf.fit(data[time_col], event_observed=data[event_col])

            results['curves']['overall'] = {
                'median_survival': kmf.median_survival_time_,
                'survival_function': kmf.survival_function_,
                'confidence_interval': kmf.confidence_interval_
            }

            # 绘图
            fig, ax = plt.subplots(figsize=self.figsize)
            kmf.plot_survival_function(ax=ax, ci_show=True, color=SCIHUBS_COLORS[0])
            ax.set_xlabel('Time (months)', **SCIHUBS_FONT)
            ax.set_ylabel('Survival Probability', **SCIHUBS_FONT)
            self._apply_sci_style(ax)

            # 添加中位生存期标注
            median_time = kmf.median_survival_time_
            if not np.isinf(median_time):
                ax.axhline(y=0.5, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
                ax.axvline(x=median_time, color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
                ax.annotate(f'Median: {median_time:.1f}', xy=(median_time, 0.5),
                           xytext=(10, 10), textcoords='offset points', fontsize=9)

            if show_risk_table:
                self._add_risk_table(ax, kmf)

            plt.tight_layout()
            if output_path:
                plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

        # 多组对比分析
        else:
            fig, ax = plt.subplots(figsize=self.figsize)

            if groups is None:
                groups = data[group_col].unique()

            for i, group in enumerate(groups):
                group_data = data[data[group_col] == group]
                kmf = KaplanMeierFitter()
                kmf.fit(group_data[time_col], event_observed=group_data[event_col],
                        label=f'{group} (n={len(group_data)})')
                kmf.plot_survival_function(ax=ax, ci_show=True, color=SCIHUBS_COLORS[i % len(SCIHUBS_COLORS)])

                results['curves'][group] = {
                    'n': len(group_data),
                    'events': group_data[event_col].sum(),
                    'median_survival': kmf.median_survival_time_,
                    'survival_function': kmf.survival_function_,
                    'confidence_interval': kmf.confidence_interval_
                }

            # Log-rank检验
            if len(groups) == 2:
                group1_data = data[data[group_col] == groups[0]]
                group2_data = data[data[group_col] == groups[1]]

                lr_result = logrank_test(
                    group1_data[time_col], group2_data[time_col],
                    group1_data[event_col], group2_data[event_col]
                )

                results['log_rank'] = {
                    'test_statistic': lr_result.test_statistic,
                    'p_value': lr_result.p_value,
                    'interpretation': self._interpret_pvalue(lr_result.p_value)
                }

                # 在图上标注P值
                ax.annotate(f'Log-rank P = {lr_result.p_value:.4f}',
                           xy=(0.95, 0.95), xycoords='axes fraction',
                           ha='right', va='top', fontsize=10,
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            ax.set_xlabel('Time (months)', **SCIHUBS_FONT)
            ax.set_ylabel('Survival Probability', **SCIHUBS_FONT)
            ax.legend(loc='best', frameon=False, fontsize=9)
            self._apply_sci_style(ax)

            if show_risk_table:
                self._add_risk_table_multigroup(ax, data, time_col, group_col, groups)

            plt.tight_layout()
            if output_path:
                plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
            plt.close()

        self.results['km_analysis'] = results
        return results

    def _add_risk_table(self, ax: plt.Axes, kmf: KaplanMeierFitter) -> None:
        """添加单组风险表"""
        pass  # 简化实现

    def _add_risk_table_multigroup(self, ax: plt.Axes, data: pd.DataFrame,
                                   time_col: str, group_col: str, groups: List) -> None:
        """添加多组风险表"""
        pass  # 简化实现

    def cox_regression(self, data: pd.DataFrame, time_col: str = 'time',
                       event_col: str = 'event', covariates: List[str],
                       output_path: Optional[str] = None) -> Dict:
        """
        Cox比例风险回归分析

        Args:
            data: 数据框
            time_col: 时间列名
            event_col: 事件列名
            covariates: 协变量列表
            output_path: 输出路径

        Returns:
            回归结果字典
        """
        # 准备数据
        cox_data = data[[time_col, event_col] + covariates].copy()

        # 拟合模型
        cph = CoxPHFitter()
        cph.fit(cox_data, duration_col=time_col, event_col=event_col)

        # 提取结果
        summary = cph.summary.copy()
        summary['HR'] = np.exp(summary['coef'])
        summary['HR_lower'] = np.exp(summary['coef lower 95%'])
        summary['HR_upper'] = np.exp(summary['coef upper 95%'])

        results = {
            'concordance_index': cph.concordance_index_,
            'log_likelihood': cph.log_likelihood_,
            'AIC': cph.AIC_partial_,
            'summary': summary
        }

        # 生成森林图
        if output_path:
            self.forest_plot(summary, output_path)

        self.results['cox_regression'] = results
        return results

    def forest_plot(self, summary: pd.DataFrame, output_path: str,
                    title: str = 'Forest Plot - Cox Regression') -> None:
        """
        绘制森林图

        Args:
            summary: Cox回归结果摘要
            output_path: 输出图片路径
            title: 图表标题
        """
        fig, ax = plt.subplots(figsize=(10, max(4, len(summary) * 0.5 + 1)))

        # 准备数据
        variables = summary.index.tolist()
        hr = summary['HR'].values
        ci_lower = summary['HR_lower'].values
        ci_upper = summary['HR_upper'].values
        p_values = summary['p'].values

        y_pos = np.arange(len(variables))
        colors = [SCIHUBS_COLORS[0] if p < 0.05 else 'gray' for p in p_values]

        # 绘制点估计和置信区间
        for i, (h, lo, hi, c) in enumerate(zip(hr, ci_lower, ci_upper, colors)):
            ax.plot([lo, hi], [i, i], color=c, linewidth=2)
            ax.plot(h, i, 'o', color=c, markersize=6)

        # 参考线
        ax.axvline(x=1, color='black', linestyle='--', linewidth=0.8)

        # 设置标签
        ax.set_yticks(y_pos)
        ax.set_yticklabels(variables, fontsize=10)
        ax.set_xlabel('Hazard Ratio (95% CI)', **SCIHUBS_FONT)
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)

        # 添加HR值和P值
        for i, (h, lo, hi, p) in enumerate(zip(hr, ci_lower, ci_upper, p_values)):
            p_str = f'{p:.4f}' if p >= 0.001 else '<0.001'
            ax.text(hi + 0.1, i, f'{h:.2f} ({lo:.2f}-{hi:.2f})\nP={p_str}',
                   va='center', ha='left', fontsize=8)

        ax.set_xlim(0, max(ci_upper) * 1.5)
        ax.invert_yaxis()
        sns.despine()
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

    def _interpret_pvalue(self, p_value: float) -> str:
        """解释P值"""
        if p_value < 0.001:
            return "极显著差异 (P < 0.001)"
        elif p_value < 0.01:
            return "高度显著差异 (P < 0.01)"
        elif p_value < 0.05:
            return "显著差异 (P < 0.05)"
        else:
            return "无显著差异 (P >= 0.05)"

    def generate_report(self) -> str:
        """生成分析报告"""
        report = ["## 生存分析报告\n"]

        if 'km_analysis' in self.results:
            report.append("### Kaplan-Meier分析\n")
            km = self.results['km_analysis']

            if 'log_rank' in km and km['log_rank']:
                report.append(f"**Log-rank检验**: χ² = {km['log_rank']['test_statistic']:.4f}, "
                            f"P = {km['log_rank']['p_value']:.4f}\n")
                report.append(f"**结论**: {km['log_rank']['interpretation']}\n\n")

            report.append("| 组别 | 样本量 | 事件数 | 中位生存期 |\n")
            report.append("|------|--------|--------|------------|\n")
            for group, data in km['curves'].items():
                med = data['median_survival']
                med_str = f"{med:.1f}" if not np.isinf(med) else "未达到"
                report.append(f"| {group} | {data.get('n', 'N/A')} | "
                            f"{data.get('events', 'N/A')} | {med_str} |\n")

        if 'cox_regression' in self.results:
            report.append("\n### Cox回归分析\n")
            cox = self.results['cox_regression']
            report.append(f"**一致性指数 (C-index)**: {cox['concordance_index']:.4f}\n\n")

            report.append("| 变量 | HR | 95% CI | P值 |\n")
            report.append("|------|-----|--------|-----|\n")
            for idx, row in cox['summary'].iterrows():
                p_str = f"{row['p']:.4f}" if row['p'] >= 0.001 else "<0.001"
                report.append(f"| {idx} | {row['HR']:.3f} | "
                            f"{row['HR_lower']:.3f}-{row['HR_upper']:.3f} | {p_str} |\n")

        return ''.join(report)


def demo():
    """演示函数"""
    import os

    # 生成示例数据
    np.random.seed(42)
    n = 200

    demo_data = pd.DataFrame({
        'group': np.random.choice(['手术组', '化疗组'], n),
        'time': np.random.exponential(20, n) + np.random.normal(0, 2, n),
        'event': np.random.binomial(1, 0.6, n)
    })
    demo_data['time'] = demo_data['time'].clip(lower=0.5)

    # 初始化分析器
    analyzer = SurvivalAnalyzer()

    # 执行分析
    os.makedirs('/workspace/temp-skills/medical-statistics-visualizer/assets', exist_ok=True)

    # Kaplan-Meier曲线
    km_results = analyzer.kaplan_meier(
        demo_data,
        time_col='time',
        event_col='event',
        group_col='group',
        groups=['手术组', '化疗组'],
        output_path='/workspace/temp-skills/medical-statistics-visualizer/assets/km_curve.png'
    )

    print("Kaplan-Meier分析结果:")
    print(f"Log-rank P值: {km_results['log_rank']['p_value']:.4f}")

    # Cox回归
    demo_data['age'] = np.random.normal(55, 10, n)
    demo_data['stage'] = np.random.choice([1, 2, 3, 4], n)

    cox_results = analyzer.cox_regression(
        demo_data,
        time_col='time',
        event_col='event',
        covariates=['age', 'stage'],
        output_path='/workspace/temp-skills/medical-statistics-visualizer/assets/forest_plot.png'
    )

    print(f"\nCox回归 C-index: {cox_results['concordance_index']:.4f}")

    # 生成报告
    report = analyzer.generate_report()
    print("\n" + report)


if __name__ == '__main__':
    demo()
