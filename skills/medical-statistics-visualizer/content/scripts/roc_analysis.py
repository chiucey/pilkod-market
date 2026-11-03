"""
医学统计 - ROC分析模块
功能：ROC曲线绘制、AUC计算、最佳截断值确定、诊断效能评估
依赖：scikit-learn, pandas, numpy, matplotlib, scipy
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    roc_curve, auc, roc_auc_score, confusion_matrix,
    accuracy_score, precision_score, recall_score, f1_score,
    specificity_score, sensitivity_score, youden_index
)
from scipy.optimize import brentq
from scipy.interpolate import interp1d
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# SCI期刊标准样式
SCIHUBS_COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
SCIHUBS_FONT = {'family': 'Arial', 'size': 10}


class ROCAnalyzer:
    """ROC曲线分析器"""

    def __init__(self, alpha: float = 0.05):
        """
        初始化分析器

        Args:
            alpha: 显著性水平
        """
        self.alpha = alpha
        self.results = {}

    def analyze(self, data: pd.DataFrame, marker_col: str,
               diagnosis_col: str, positive_label: int = 1,
               output_path: Optional[str] = None) -> Dict:
        """
        ROC分析主函数

        Args:
            data: 数据框
            marker_col: 生物标志物/检测指标列名
            diagnosis_col: 诊断结果列名（0=阴性，1=阳性）
            positive_label: 阳性标签值（默认为1）
            output_path: ROC曲线输出路径

        Returns:
            分析结果字典
        """
        # 准备数据
        clean_data = data[[marker_col, diagnosis_col]].dropna()
        y_true = (clean_data[diagnosis_col] == positive_label).astype(int)
        y_scores = clean_data[marker_col].values

        # 计算ROC曲线
        fpr, tpr, thresholds = roc_curve(y_true, y_scores)

        # 计算AUC及95%CI（Bootstrap法）
        auc_value = roc_auc_score(y_true, y_scores)
        auc_ci = self._bootstrap_auc_ci(y_true, y_scores, n_bootstraps=1000)

        # 找最佳截断值（Youden指数最大）
        optimal_idx = np.argmax(tpr - fpr)
        optimal_threshold = thresholds[optimal_idx]
        optimal_sensitivity = tpr[optimal_idx]
        optimal_specificity = 1 - fpr[optimal_idx]
        optimal_youden = tpr[optimal_idx] - fpr[optimal_idx]

        # 计算其他诊断指标
        y_pred = (y_scores >= optimal_threshold).astype(int)
        cm = confusion_matrix(y_true, y_pred)

        results = {
            'auc': auc_value,
            'auc_ci_lower': auc_ci[0],
            'auc_ci_upper': auc_ci[1],
            'optimal_threshold': optimal_threshold,
            'sensitivity': optimal_sensitivity,
            'specificity': optimal_specificity,
            'youden_index': optimal_youden,
            'accuracy': accuracy_score(y_true, y_pred),
            'ppv': precision_score(y_true, y_pred),  # Positive Predictive Value
            'npv': self._calculate_npv(y_true, y_pred),  # Negative Predictive Value
            'f1_score': f1_score(y_true, y_pred),
            'confusion_matrix': cm.tolist(),
            'roc_curve': {
                'fpr': fpr.tolist(),
                'tpr': tpr.tolist(),
                'thresholds': thresholds.tolist()
            },
            'data_summary': {
                'total': len(y_true),
                'positive': y_true.sum(),
                'negative': (1 - y_true).sum()
            }
        }

        # 绘制ROC曲线
        if output_path:
            self._plot_roc(fpr, tpr, auc_value, auc_ci, output_path, optimal_idx)

        self.results['roc_analysis'] = results
        return results

    def compare_markers(self, data: pd.DataFrame, markers: List[str],
                       diagnosis_col: str, positive_label: int = 1,
                       output_path: Optional[str] = None) -> Dict:
        """
        多标志物ROC对比分析

        Args:
            data: 数据框
            markers: 多个标志物列名列表
            diagnosis_col: 诊断结果列名
            positive_label: 阳性标签值
            output_path: 输出路径

        Returns:
            各标志物的分析结果
        """
        results = {}

        for marker in markers:
            clean_data = data[[marker, diagnosis_col]].dropna()
            y_true = (clean_data[diagnosis_col] == positive_label).astype(int)
            y_scores = clean_data[marker].values

            fpr, tpr, _ = roc_curve(y_true, y_scores)
            auc_value = roc_auc_score(y_true, y_scores)
            auc_ci = self._bootstrap_auc_ci(y_true, y_scores)

            # 最佳截断值
            optimal_idx = np.argmax(tpr - fpr)
            optimal_threshold = _[optimal_idx] if len(_) > 0 else np.median(y_scores)

            results[marker] = {
                'auc': auc_value,
                'auc_ci_lower': auc_ci[0],
                'auc_ci_upper': auc_ci[1],
                'optimal_threshold': float(optimal_threshold),
                'sensitivity': float(tpr[optimal_idx]),
                'specificity': float(1 - fpr[optimal_idx])
            }

        # 绘制对比图
        if output_path:
            self._plot_multiple_roc(data, markers, diagnosis_col, positive_label, results, output_path)

        self.results['marker_comparison'] = results
        return results

    def _bootstrap_auc_ci(self, y_true: np.ndarray, y_scores: np.ndarray,
                         n_bootstraps: int = 1000) -> Tuple[float, float]:
        """
        Bootstrap法计算AUC的95%CI

        Args:
            y_true: 真实标签
            y_scores: 预测分数
            n_bootstraps: Bootstrap迭代次数

        Returns:
            (CI_lower, CI_upper)
        """
        n = len(y_true)
        rng = np.random.RandomState(42)
        bootstrapped_scores = []

        for _ in range(n_bootstraps):
            indices = rng.randint(0, n, n)
            if len(np.unique(y_true[indices])) < 2:
                continue
            score = roc_auc_score(y_true[indices], y_scores[indices])
            bootstrapped_scores.append(score)

        alpha = 1 - (1 - self.alpha) / 2
        ci_lower = np.percentile(bootstrapped_scores, (1 - alpha) * 100)
        ci_upper = np.percentile(bootstrapped_scores, alpha * 100)

        return (ci_lower, ci_upper)

    def _calculate_npv(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """计算阴性预测值"""
        tn = np.sum((y_true == 0) & (y_pred == 0))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        if tn + fn == 0:
            return 0.0
        return tn / (tn + fn)

    def _plot_roc(self, fpr: np.ndarray, tpr: np.ndarray,
                  auc_value: float, auc_ci: Tuple[float, float],
                  output_path: str, optimal_idx: int) -> None:
        """绘制ROC曲线"""
        fig, ax = plt.subplots(figsize=(8, 8))

        # ROC曲线
        ax.plot(fpr, tpr, color=SCIHUBS_COLORS[0], linewidth=2,
               label=f'ROC curve (AUC = {auc_value:.3f}, 95% CI: {auc_ci[0]:.3f}-{auc_ci[1]:.3f})')

        # 对角线
        ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random classifier')

        # 最佳截断点
        ax.scatter(fpr[optimal_idx], tpr[optimal_idx], marker='o', s=100,
                  color=SCIHUBS_COLORS[1], zorder=5, label=f'Optimal cutoff')

        # 标注最佳点
        ax.annotate(f'Sens={tpr[optimal_idx]:.2f}\nSpec={1-fpr[optimal_idx]:.2f}',
                   xy=(fpr[optimal_idx], tpr[optimal_idx]),
                   xytext=(fpr[optimal_idx] + 0.15, tpr[optimal_idx] - 0.1),
                   fontsize=9, ha='left',
                   arrowprops=dict(arrowstyle='->', color='gray'))

        ax.set_xlabel('1 - Specificity (False Positive Rate)', **SCIHUBS_FONT)
        ax.set_ylabel('Sensitivity (True Positive Rate)', **SCIHUBS_FONT)
        ax.set_title('ROC Curve Analysis', fontsize=12, fontweight='bold', pad=10)
        ax.set_xlim([-0.02, 1.02])
        ax.set_ylim([-0.02, 1.02])
        ax.legend(loc='lower right', frameon=False, fontsize=9)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_multiple_roc(self, data: pd.DataFrame, markers: List[str],
                           diagnosis_col: str, positive_label: int,
                           results: Dict, output_path: str) -> None:
        """绘制多标志物ROC对比图"""
        fig, ax = plt.subplots(figsize=(10, 10))

        for i, marker in enumerate(markers):
            clean_data = data[[marker, diagnosis_col]].dropna()
            y_true = (clean_data[diagnosis_col] == positive_label).astype(int)
            y_scores = clean_data[marker].values

            fpr, tpr, _ = roc_curve(y_true, y_scores)
            auc_value = roc_auc_score(y_true, y_scores)
            auc_ci = results[marker]['auc_ci_lower'], results[marker]['auc_ci_upper']

            ax.plot(fpr, tpr, color=SCIHUBS_COLORS[i % len(SCIHUBS_COLORS)],
                   linewidth=2, label=f'{marker} (AUC = {auc_value:.3f}, 95% CI: {auc_ci[0]:.3f}-{auc_ci[1]:.3f})')

        # 对角线
        ax.plot([0, 1], [0, 1], 'k--', linewidth=1, alpha=0.5)

        ax.set_xlabel('1 - Specificity (False Positive Rate)', **SCIHUBS_FONT)
        ax.set_ylabel('Sensitivity (True Positive Rate)', **SCIHUBS_FONT)
        ax.set_title('ROC Curves Comparison', fontsize=12, fontweight='bold', pad=10)
        ax.set_xlim([-0.02, 1.02])
        ax.set_ylim([-0.02, 1.02])
        ax.legend(loc='lower right', frameon=False, fontsize=9)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

    def generate_report(self) -> str:
        """生成ROC分析报告"""
        report = ["## ROC曲线分析报告\n"]

        if 'roc_analysis' in self.results:
            res = self.results['roc_analysis']
            report.append("### 诊断效能评估\n\n")

            # 数据概况
            report.append("**数据概况**\n\n")
            report.append(f"- 总样本数: {res['data_summary']['total']}\n")
            report.append(f"- 阳性病例: {res['data_summary']['positive']}\n")
            report.append(f"- 阴性病例: {res['data_summary']['negative']}\n")

            # AUC
            report.append("\n**AUC分析**\n\n")
            report.append(f"- AUC值: {res['auc']:.4f}\n")
            report.append(f"- 95% CI: ({res['auc_ci_lower']:.4f} - {res['auc_ci_upper']:.4f})\n")

            # 最佳截断值
            report.append("\n**最佳截断值**\n\n")
            report.append(f"- 截断值: {res['optimal_threshold']:.4f}\n")
            report.append(f"- 敏感度: {res['sensitivity']:.4f} ({res['sensitivity']*100:.1f}%)\n")
            report.append(f"- 特异度: {res['specificity']:.4f} ({res['specificity']*100:.1f}%)\n")
            report.append(f"- Youden指数: {res['youden_index']:.4f}\n")

            # 诊断指标
            report.append("\n**诊断指标**\n\n")
            report.append(f"- 准确度: {res['accuracy']:.4f} ({res['accuracy']*100:.1f}%)\n")
            report.append(f"- 阳性预测值 (PPV): {res['ppv']:.4f} ({res['ppv']*100:.1f}%)\n")
            report.append(f"- 阴性预测值 (NPV): {res['npv']:.4f} ({res['npv']*100:.1f}%)\n")
            report.append(f"- F1分数: {res['f1_score']:.4f}\n")

            # 混淆矩阵
            report.append("\n**混淆矩阵**\n\n")
            cm = res['confusion_matrix']
            report.append(f"|  | 预测阴性 | 预测阳性 |\n")
            report.append(f"|---|---|---|\n")
            report.append(f"| 实际阴性 | {cm[0][0]} | {cm[0][1]} |\n")
            report.append(f"| 实际阳性 | {cm[1][0]} | {cm[1][1]} |\n")

        if 'marker_comparison' in self.results:
            report.append("\n### 多标志物对比\n\n")
            report.append("| 标志物 | AUC | 95% CI | 敏感度 | 特异度 | 截断值 |\n")
            report.append("|--------|-----|--------|--------|--------|--------|\n")

            for marker, res in self.results['marker_comparison'].items():
                report.append(f"| {marker} | {res['auc']:.3f} | "
                            f"{res['auc_ci_lower']:.3f}-{res['auc_ci_upper']:.3f} | "
                            f"{res['sensitivity']:.3f} | {res['specificity']:.3f} | "
                            f"{res['optimal_threshold']:.2f} |\n")

        return ''.join(report)


def demo():
    """演示函数"""
    import os
    os.makedirs('/workspace/temp-skills/medical-statistics-visualizer/assets', exist_ok=True)

    np.random.seed(42)
    n = 200

    # 生成示例数据
    demo_data = pd.DataFrame({
        'CA19_9': np.concatenate([
            np.random.lognormal(3, 0.4, 80),   # 阳性组
            np.random.lognormal(2, 0.5, 120)    # 阴性组
        ]),
        'diagnosis': np.concatenate([
            np.ones(80),   # 阳性
            np.zeros(120)  # 阴性
        ])
    })

    analyzer = ROCAnalyzer()

    # ROC分析
    results = analyzer.analyze(
        demo_data, 'CA19_9', 'diagnosis',
        output_path='/workspace/temp-skills/medical-statistics-visualizer/assets/roc_curve.png'
    )

    print("ROC分析结果:")
    print(f"AUC: {results['auc']:.4f} (95% CI: {results['auc_ci_lower']:.4f}-{results['auc_ci_upper']:.4f})")
    print(f"最佳截断值: {results['optimal_threshold']:.2f}")
    print(f"敏感度: {results['sensitivity']:.4f}")
    print(f"特异度: {results['specificity']:.4f}")

    # 生成报告
    report = analyzer.generate_report()
    print("\n" + report)


if __name__ == '__main__':
    demo()
