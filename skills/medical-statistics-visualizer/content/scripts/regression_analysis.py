"""
医学统计 - 回归分析模块
功能：Logistic回归、线性回归、森林图可视化
依赖：statsmodels, pandas, numpy, matplotlib, seaborn
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import logit, ols
from statsmodels.stats.outliers_influence import variance_inflation_factor
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# SCI期刊标准样式
SCIHUBS_COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
SCIHUBS_FONT = {'family': 'Arial', 'size': 10}


class RegressionAnalyzer:
    """回归分析器"""

    def __init__(self, alpha: float = 0.05):
        """
        初始化分析器

        Args:
            alpha: 显著性水平
        """
        self.alpha = alpha
        self.results = {}

    def _interpret_pvalue(self, p_value: float) -> str:
        """解释P值"""
        if p_value < 0.001:
            return "极显著 (P < 0.001)"
        elif p_value < 0.01:
            return "高度显著 (P < 0.01)"
        elif p_value < self.alpha:
            return "显著 (P < 0.05)"
        else:
            return "不显著 (P >= 0.05)"

    def logistic_regression(self, data: pd.DataFrame, outcome_col: str,
                           covariates: List[str],
                           output_path: Optional[str] = None) -> Dict:
        """
        Logistic回归分析

        Args:
            data: 数据框
            outcome_col: 二分类结局列名（0/1）
            covariates: 协变量列表
            output_path: 森林图输出路径

        Returns:
            回归结果字典
        """
        # 准备数据
        model_data = data[[outcome_col] + covariates].dropna()

        # 添加常数项
        X = sm.add_constant(model_data[covariates])
        y = model_data[outcome_col]

        # 拟合模型
        model = sm.Logit(y, X)
        result = model.fit(disp=0)

        # 提取结果
        summary = pd.DataFrame({
            'coef': result.params,
            'exp_coef': np.exp(result.params),
            'se': result.bse,
            'z': result.tvalues,
            'p': result.pvalues,
            'ci_lower': np.exp(result.conf_int()[0]),
            'ci_upper': np.exp(result.conf_int()[1])
        })

        # 重命名常数项
        summary.index = [x if x != 'const' else 'Intercept' for x in summary.index]

        # 计算VIF（多重共线性检验）
        vif_data = self._calculate_vif(X.drop('const', axis=1, errors='ignore'))

        results = {
            'model': result,
            'summary': summary,
            'vif': vif_data,
            'pseudo_r2': {
                'McFadden': result.prsquared,
                'Cox-Snell': self._calculate_coxsnell(result, len(y)),
                'Nagelkerke': self._calculate_nagelkerke(result, len(y))
            },
            'goodness_of_fit': {
                'llf': result.llf,
                'AIC': result.aic,
                'BIC': result.bic,
                'log_likelihood': result.llf
            }
        }

        # 绘制森林图
        if output_path:
            self._plot_logistic_forest(summary, output_path, 'Odds Ratio (95% CI)')

        self.results['logistic'] = results
        return results

    def linear_regression(self, data: pd.DataFrame, outcome_col: str,
                         covariates: List[str],
                         output_path: Optional[str] = None) -> Dict:
        """
        线性回归分析

        Args:
            data: 数据框
            outcome_col: 连续性结局变量
            covariates: 协变量列表
            output_path: 森林图输出路径

        Returns:
            回归结果字典
        """
        # 准备数据
        model_data = data[[outcome_col] + covariates].dropna()

        # 添加常数项
        X = sm.add_constant(model_data[covariates])
        y = model_data[outcome_col]

        # 拟合模型
        model = sm.OLS(y, X)
        result = model.fit()

        # 提取结果
        summary = pd.DataFrame({
            'coef': result.params,
            'se': result.bse,
            't': result.tvalues,
            'p': result.pvalues,
            'ci_lower': result.conf_int()[0],
            'ci_upper': result.conf_int()[1]
        })

        summary.index = [x if x != 'const' else 'Intercept' for x in summary.index]

        # 计算VIF
        vif_data = self._calculate_vif(X.drop('const', axis=1, errors='ignore'))

        results = {
            'model': result,
            'summary': summary,
            'vif': vif_data,
            'goodness_of_fit': {
                'r_squared': result.rsquared,
                'adj_r_squared': result.rsquared_adj,
                'AIC': result.aic,
                'BIC': result.bic,
                'f_statistic': result.fvalue,
                'f_pvalue': result.f_pvalue
            }
        }

        # 绘制森林图（标准化系数）
        if output_path:
            self._plot_linear_forest(summary, output_path, 'Coefficient (95% CI)')

        self.results['linear'] = results
        return results

    def _calculate_vif(self, X: pd.DataFrame) -> pd.DataFrame:
        """计算方差膨胀因子"""
        vif = pd.DataFrame()
        vif['Variable'] = X.columns
        vif['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
        return vif

    def _calculate_coxsnell(self, result, n: int) -> float:
        """计算Cox-Snell R²"""
        return 1 - np.exp(-result.llf / n)

    def _calculate_nagelkerke(self, result, n: int) -> float:
        """计算Nagelkerke R²"""
        cox_snell = self._calculate_coxsnell(result, n)
        return cox_snell / (1 - np.exp(-result.llnull / n))

    def _plot_logistic_forest(self, summary: pd.DataFrame, output_path: str,
                             xlabel: str) -> None:
        """绘制Logistic回归森林图"""
        fig, ax = plt.subplots(figsize=(10, max(4, len(summary) * 0.5 + 1)))

        # 排除Intercept
        plot_data = summary.drop('Intercept', errors='ignore')
        plot_data = plot_data.sort_values('exp_coef')

        variables = plot_data.index.tolist()
        or_values = plot_data['exp_coef'].values
        ci_lower = plot_data['ci_lower'].values
        ci_upper = plot_data['ci_upper'].values
        p_values = plot_data['p'].values

        y_pos = np.arange(len(variables))
        colors = [SCIHUBS_COLORS[0] if p < 0.05 else 'gray' for p in p_values]

        # 绘制置信区间和点估计
        for i, (or_val, lo, hi, c) in enumerate(zip(or_values, ci_lower, ci_upper, colors)):
            ax.plot([lo, hi], [i, i], color=c, linewidth=2)
            ax.plot(or_val, i, 's', color=c, markersize=6)

        # 参考线
        ax.axvline(x=1, color='black', linestyle='--', linewidth=0.8)

        # 设置标签
        ax.set_yticks(y_pos)
        ax.set_yticklabels(variables, fontsize=10)
        ax.set_xlabel(xlabel, **SCIHUBS_FONT)
        ax.set_title('Logistic Regression Forest Plot', fontsize=12, fontweight='bold', pad=10)

        # 添加数值标注
        for i, (or_val, lo, hi, p) in enumerate(zip(or_values, ci_lower, ci_upper, p_values)):
            p_str = f'{p:.4f}' if p >= 0.001 else '<0.001'
            ax.text(hi + 0.15 * max(or_values), i, f'{or_val:.2f} ({lo:.2f}-{hi:.2f})\nP={p_str}',
                   va='center', ha='left', fontsize=8)

        ax.set_xlim(0, max(ci_upper) * 1.6)
        ax.invert_yaxis()
        sns.despine()
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_linear_forest(self, summary: pd.DataFrame, output_path: str,
                           xlabel: str) -> None:
        """绘制线性回归森林图"""
        fig, ax = plt.subplots(figsize=(10, max(4, len(summary) * 0.5 + 1)))

        # 排除Intercept
        plot_data = summary.drop('Intercept', errors='ignore')
        plot_data = plot_data.sort_values('coef')

        variables = plot_data.index.tolist()
        coef_values = plot_data['coef'].values
        ci_lower = plot_data['ci_lower'].values
        ci_upper = plot_data['ci_upper'].values
        p_values = plot_data['p'].values

        y_pos = np.arange(len(variables))
        colors = [SCIHUBS_COLORS[0] if p < 0.05 else 'gray' for p in p_values]

        # 绘制置信区间和点估计
        for i, (coef, lo, hi, c) in enumerate(zip(coef_values, ci_lower, ci_upper, colors)):
            ax.plot([lo, hi], [i, i], color=c, linewidth=2)
            ax.plot(coef, i, 's', color=c, markersize=6)

        # 参考线
        ax.axvline(x=0, color='black', linestyle='--', linewidth=0.8)

        # 设置标签
        ax.set_yticks(y_pos)
        ax.set_yticklabels(variables, fontsize=10)
        ax.set_xlabel(xlabel, **SCIHUBS_FONT)
        ax.set_title('Linear Regression Forest Plot', fontsize=12, fontweight='bold', pad=10)

        # 添加数值标注
        for i, (coef, lo, hi, p) in enumerate(zip(coef_values, ci_lower, ci_upper, p_values)):
            p_str = f'{p:.4f}' if p >= 0.001 else '<0.001'
            max_abs = max(abs(ci_lower.min()), abs(ci_upper.max()))
            ax.text(hi + 0.05 * max_abs, i, f'{coef:.3f} ({lo:.3f}-{hi:.3f})\nP={p_str}',
                   va='center', ha='left', fontsize=8)

        ax.set_xlim(min(ci_lower.min() * 1.1, -0.1), max(ci_upper.max() * 1.1, 0.1))
        ax.invert_yaxis()
        sns.despine()
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def stepwise_selection(self, data: pd.DataFrame, outcome_col: str,
                          all_covariates: List[str], direction: str = 'both',
                          threshold_in: float = 0.05, threshold_out: float = 0.10) -> Dict:
        """
        逐步回归选择变量

        Args:
            data: 数据框
            outcome_col: 结局变量
            all_covariates: 所有候选协变量
            direction: 'forward', 'backward', 'both'
            threshold_in: 进入模型的P值阈值
            threshold_out: 移出模型的P值阈值

        Returns:
            选中的变量和最终模型
        """
        initial_covariates = []
        remaining = all_covariates.copy()
        done = False

        while not done:
            changed = False

            if direction in ['forward', 'both']:
                # 前向选择
                best_pval = threshold_in
                best_var = None
                for var in remaining:
                    try:
                        if len(initial_covariates) == 0:
                            X = sm.add_constant(data[[var]].dropna())
                            y = data.loc[X.index, outcome_col]
                        else:
                            X = sm.add_constant(data[initial_covariates + [var]].dropna())
                            y = data.loc[X.index, outcome_col]

                        model = sm.Logit(y, X)
                        result = model.fit(disp=0)
                        pval = result.pvalues[var]
                    except:
                        continue

                    if pval < best_pval:
                        best_pval = pval
                        best_var = var

                if best_var is not None:
                    initial_covariates.append(best_var)
                    remaining.remove(best_var)
                    changed = True

            if direction in ['backward', 'both']:
                # 后向消除
                if len(initial_covariates) > 0:
                    X = sm.add_constant(data[initial_covariates].dropna())
                    y = data.loc[X.index, outcome_col]

                    model = sm.Logit(y, X)
                    result = model.fit(disp=0)

                    worst_pval = result.pvalues.drop('const').max()
                    worst_var = result.pvalues.drop('const').idxmax()

                    if worst_pval > threshold_out:
                        initial_covariates.remove(worst_var)
                        remaining.append(worst_var)
                        changed = True

            if not changed:
                done = True

        return {
            'selected_covariates': initial_covariates,
            'removed_covariates': remaining
        }

    def generate_report(self) -> str:
        """生成回归分析报告"""
        report = ["## 回归分析报告\n"]

        if 'logistic' in self.results:
            res = self.results['logistic']
            report.append("### Logistic回归分析\n\n")

            # 模型拟合度
            report.append("**模型拟合度**\n\n")
            for name, value in res['pseudo_r2'].items():
                report.append(f"- {name} R²: {value:.4f}\n")
            report.append(f"- AIC: {res['goodness_of_fit']['AIC']:.2f}\n")
            report.append(f"- BIC: {res['goodness_of_fit']['BIC']:.2f}\n")

            # 多重共线性检验
            report.append("\n**多重共线性检验 (VIF)**\n\n")
            vif = res['vif']
            for _, row in vif.iterrows():
                status = "⚠️ 高" if row['VIF'] > 10 else "正常"
                report.append(f"- {row['Variable']}: VIF = {row['VIF']:.2f} ({status})\n")

            # 回归结果
            report.append("\n**回归系数**\n\n")
            report.append("| 变量 | OR | 95% CI | P值 | 结论 |\n")
            report.append("|------|-----|--------|-----|------|\n")

            for idx, row in res['summary'].iterrows():
                p_str = f"{row['p']:.4f}" if row['p'] >= 0.001 else "<0.001"
                conclusion = self._interpret_pvalue(row['p'])
                if idx == 'Intercept':
                    report.append(f"| {idx} | - | - | {p_str} | - |\n")
                else:
                    report.append(f"| {idx} | {row['exp_coef']:.3f} | "
                                f"{row['ci_lower']:.3f}-{row['ci_upper']:.3f} | {p_str} | {conclusion} |\n")

        if 'linear' in self.results:
            res = self.results['linear']
            report.append("\n### 线性回归分析\n\n")

            # 模型拟合度
            report.append("**模型拟合度**\n\n")
            report.append(f"- R²: {res['goodness_of_fit']['r_squared']:.4f}\n")
            report.append(f"- Adjusted R²: {res['goodness_of_fit']['adj_r_squared']:.4f}\n")
            report.append(f"- F-statistic: {res['goodness_of_fit']['f_statistic']:.2f}\n")
            report.append(f"- F P-value: {res['goodness_of_fit']['f_pvalue']:.4f}\n")

            # 多重共线性检验
            report.append("\n**多重共线性检验 (VIF)**\n\n")
            vif = res['vif']
            for _, row in vif.iterrows():
                status = "⚠️ 高" if row['VIF'] > 10 else "正常"
                report.append(f"- {row['Variable']}: VIF = {row['VIF']:.2f} ({status})\n")

            # 回归结果
            report.append("\n**回归系数**\n\n")
            report.append("| 变量 | β | 95% CI | P值 | 结论 |\n")
            report.append("|------|-----|--------|-----|------|\n")

            for idx, row in res['summary'].iterrows():
                p_str = f"{row['p']:.4f}" if row['p'] >= 0.001 else "<0.001"
                conclusion = self._interpret_pvalue(row['p'])
                if idx == 'Intercept':
                    report.append(f"| {idx} | {row['coef']:.3f} | - | {p_str} | - |\n")
                else:
                    report.append(f"| {idx} | {row['coef']:.3f} | "
                                f"{row['ci_lower']:.3f}-{row['ci_upper']:.3f} | {p_str} | {conclusion} |\n")

        return ''.join(report)


def demo():
    """演示函数"""
    import os
    os.makedirs('/workspace/temp-skills/medical-statistics-visualizer/assets', exist_ok=True)

    np.random.seed(42)
    n = 200

    # 生成示例数据
    demo_data = pd.DataFrame({
        'outcome': np.random.binomial(1, 0.4, n),  # 二分类结局
        'age': np.random.normal(55, 10, n),
        'stage': np.random.choice([1, 2, 3], n, p=[0.3, 0.4, 0.3]),
        'treatment': np.random.choice([0, 1], n),  # 0=对照, 1=治疗
        'bmi': np.random.normal(24, 3, n)
    })

    analyzer = RegressionAnalyzer()

    # Logistic回归
    results = analyzer.logistic_regression(
        demo_data, 'outcome', ['age', 'stage', 'treatment', 'bmi'],
        output_path='/workspace/temp-skills/medical-statistics-visualizer/assets/logistic_forest.png'
    )

    print("Logistic回归结果:")
    print(results['summary'])

    # 生成报告
    report = analyzer.generate_report()
    print("\n" + report)


if __name__ == '__main__':
    demo()
