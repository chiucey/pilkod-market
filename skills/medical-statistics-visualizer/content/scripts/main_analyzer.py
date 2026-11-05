"""
医学统计 - 主分析器
功能：自然语言解析 + 调度各分析模块 + 生成综合报告
"""

import pandas as pd
import numpy as np
import re
import os
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# 导入各分析模块
from .survival_analysis import SurvivalAnalyzer
from .statistical_tests import StatisticalTester
from .regression_analysis import RegressionAnalyzer
from .roc_analysis import ROCAnalyzer
from .visualization import VisualizationEngine, set_sci_style
from .data_parser import DataParser


class MedicalStatisticsAnalyzer:
    """医学统计分析主类"""

    def __init__(self, output_dir: str = './output'):
        """
        初始化分析器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 初始化各模块
        self.survival = SurvivalAnalyzer()
        self.stats = StatisticalTester()
        self.regression = RegressionAnalyzer()
        self.roc = ROCAnalyzer()
        self.vis = VisualizationEngine()
        self.parser = DataParser()

        # 结果存储
        self.results = {}
        self.report = []

    def load_data(self, file_path: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """加载数据"""
        self.data = self.parser.load(file_path, encoding)
        self.detected_columns = self.parser.auto_detect_columns()
        return self.data

    def load_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """直接从DataFrame加载"""
        self.data = df
        self.detected_columns = self.parser.auto_detect_columns()
        return self.data

    def parse_command(self, command: str) -> Dict:
        """
        解析自然语言命令

        Args:
            command: 用户指令

        Returns:
            解析后的任务参数
        """
        command_lower = command.lower()

        task = {
            'type': None,
            'params': {}
        }

        # 识别任务类型
        if any(kw in command_lower for kw in ['生存', 'km', 'k-m', 'kaplan', 'log-rank', 'logrank']):
            task['type'] = 'survival'
        elif any(kw in command_lower for kw in ['cox', '回归', 'regression']):
            if 'cox' in command_lower:
                task['type'] = 'cox_regression'
            elif 'logistic' in command_lower or '逻辑' in command_lower:
                task['type'] = 'logistic_regression'
            elif '线性' in command_lower or 'linear' in command_lower:
                task['type'] = 'linear_regression'
            else:
                task['type'] = 'regression'
        elif any(kw in command_lower for kw in ['roc', 'auc', '诊断效能', '诊断能力', 'cut-off', 'cutoff']):
            task['type'] = 'roc'
        elif any(kw in command_lower for kw in ['t检验', 't test', 'mann-whitney', 'u检验', '卡方', 'chi', 'fisher']):
            task['type'] = 'statistical_test'
        elif any(kw in command_lower for kw in ['比较', '对比', '差异', 'compare', 'diff']):
            if self.detected_columns['group_col']:
                task['type'] = 'compare'
        elif any(kw in command_lower for kw in ['相关', 'correlation', '热力']):
            task['type'] = 'correlation'
        else:
            task['type'] = 'general'

        # 提取变量名
        # 提取组名（如A组、B组）
        group_pattern = r'([A-Za-z0-9\u4e00-\u9fa5]+组)'
        groups = re.findall(group_pattern, command)

        # 提取标志物名
        marker_keywords = ['cea', 'ca19-9', 'ca19_9', 'afp', 'ca125', 'ca15-3', 'psa', 'nse', 'cyfra']
        for mk in marker_keywords:
            if mk in command_lower:
                task['params']['marker'] = mk.replace('_', '-')

        # 提取协变量
        common_covariates = ['年龄', 'age', '分期', 'stage', '分级', 'grade', '治疗', 'treatment',
                            '性别', 'sex', 'gender', 'bmi', '肿瘤大小', 'size']
        covariates = [c for c in common_covariates if c.lower() in command_lower]
        if covariates:
            task['params']['covariates'] = covariates

        task['params']['groups'] = groups if groups else None

        return task

    def analyze(self, command: str, time_col: str = None, event_col: str = None,
               group_col: str = None, outcome_col: str = None,
               marker_col: str = None, covariates: List[str] = None,
               groups: List[str] = None) -> Dict:
        """
        执行分析

        Args:
            command: 自然语言指令
            time_col: 时间列（生存分析用）
            event_col: 事件列
            group_col: 分组列
            outcome_col: 结局列（回归分析用）
            marker_col: 标志物列（ROC分析用）
            covariates: 协变量列表
            groups: 要比较的分组

        Returns:
            分析结果
        """
        if self.data is None:
            raise ValueError("请先加载数据")

        # 解析命令
        task = self.parse_command(command)

        # 使用指定的列名或自动检测的列名
        time_col = time_col or self.detected_columns.get('time_col')
        event_col = event_col or self.detected_columns.get('event_col')
        group_col = group_col or self.detected_columns.get('group_col')

        output_prefix = os.path.join(self.output_dir, task['type'])

        results = {}

        # 根据任务类型执行分析
        if task['type'] in ['survival', 'cox_regression']:
            if time_col and event_col:
                # Kaplan-Meier分析
                km_output = f"{output_prefix}_km.png"
                km_results = self.survival.kaplan_meier(
                    self.data, time_col, event_col, group_col, groups,
                    output_path=km_output
                )
                results['km_analysis'] = km_results
                results['km_plot'] = km_output

                # Cox回归
                if task['type'] == 'cox_regression' or covariates:
                    cov_list = covariates or [c for c in self.data.columns
                                            if c not in [time_col, event_col, group_col]
                                            and pd.api.types.is_numeric_dtype(self.data[c])]
                    if cov_list:
                        cox_output = f"{output_prefix}_forest.png"
                        cox_results = self.survival.cox_regression(
                            self.data, time_col, event_col, cov_list,
                            output_path=cox_output
                        )
                        results['cox_analysis'] = cox_results
                        results['forest_plot'] = cox_output

        elif task['type'] == 'statistical_test' or task['type'] == 'compare':
            command_lower = command.lower()
            # 识别检验类型
            if any(kw in command_lower for kw in ['t检验', 't test', 'mean']):
                if 'mann' in command_lower or 'u检验' in command_lower:
                    test_type = 'non_parametric'
                else:
                    test_type = 'parametric'
            else:
                test_type = 'auto'

            # 找到数值列
            if marker_col:
                value_col = marker_col
            else:
                numeric_cols = self.data.select_dtypes(include=[np.number]).columns
                value_col = covariates[0] if covariates and covariates[0] in numeric_cols else None

            if value_col and group_col:
                box_output = f"{output_prefix}_boxplot.png"
                test_results = self.stats.compare_continuous(
                    self.data, value_col, group_col, groups,
                    output_path=box_output
                )
                results['comparison'] = test_results
                results['boxplot'] = box_output

        elif task['type'] == 'logistic_regression':
            if outcome_col and covariates:
                logit_output = f"{output_prefix}_forest.png"
                logit_results = self.regression.logistic_regression(
                    self.data, outcome_col, covariates,
                    output_path=logit_output
                )
                results['logistic'] = logit_results
                results['forest_plot'] = logit_output

        elif task['type'] == 'linear_regression':
            if outcome_col and covariates:
                linear_output = f"{output_prefix}_forest.png"
                linear_results = self.regression.linear_regression(
                    self.data, outcome_col, covariates,
                    output_path=linear_output
                )
                results['linear'] = linear_results
                results['forest_plot'] = linear_output

        elif task['type'] == 'roc':
            if marker_col:
                diagnosis_col = outcome_col or self._detect_diagnosis_col()
                roc_output = f"{output_prefix}_curve.png"
                roc_results = self.roc.analyze(
                    self.data, marker_col, diagnosis_col,
                    output_path=roc_output
                )
                results['roc_analysis'] = roc_results
                results['roc_plot'] = roc_output

        elif task['type'] == 'correlation':
            cols = covariates or self.detected_columns.get('marker_cols', [])
            if len(cols) >= 2:
                corr_output = f"{output_prefix}_heatmap.png"
                corr_results = self.stats.correlation_analysis(
                    self.data, cols
                )
                results['correlation'] = corr_results
                results['heatmap'] = corr_output

        self.results = results
        return results

    def _detect_diagnosis_col(self) -> Optional[str]:
        """自动检测诊断结果列"""
        for col in self.data.columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in ['diagnosis', '诊断', 'result', '结果', 'disease']):
                unique_vals = self.data[col].unique()
                if set(str(v) for v in unique_vals).issubset({'0', '1', 'True', 'False'}):
                    return col
        return None

    def generate_report(self) -> str:
        """生成综合分析报告"""
        report = ["# 医学统计分析报告\n"]
        report.append(f"分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("---\n\n")

        # 数据概况
        report.append("## 数据概况\n\n")
        report.append(f"- 样本量: {len(self.data)}\n")
        report.append(f"- 变量数: {len(self.data.columns)}\n\n")

        # 列信息
        report.append("### 变量列表\n\n")
        col_info = self.parser.get_column_info()
        report.append("| 变量名 | 类型 | 唯一值数 | 缺失率 |\n")
        report.append("|--------|------|---------|--------|\n")
        for _, row in col_info.iterrows():
            report.append(f"| {row['column']} | {row['dtype']} | {row['n_unique']} | {row['missing_pct']} |\n")

        # 分析结果
        if 'km_analysis' in self.results:
            report.append("\n## 生存分析结果\n\n")
            km = self.results['km_analysis']
            if 'log_rank' in km and km['log_rank']:
                report.append(f"**Log-rank检验**: χ² = {km['log_rank']['test_statistic']:.4f}, "
                            f"P = {km['log_rank']['p_value']:.4f}\n\n")

        if 'cox_analysis' in self.results:
            report.append("\n### Cox回归结果\n\n")
            cox = self.results['cox_analysis']
            report.append(f"**C-index**: {cox['concordance_index']:.4f}\n\n")
            report.append("| 变量 | HR | 95% CI | P值 |\n")
            report.append("|------|-----|--------|-----|\n")
            for idx, row in cox['summary'].iterrows():
                if idx != 'Intercept':
                    p_str = f"{row['p']:.4f}" if row['p'] >= 0.001 else "<0.001"
                    report.append(f"| {idx} | {row['HR']:.3f} | "
                                f"{row['HR_lower']:.3f}-{row['HR_upper']:.3f} | {p_str} |\n")

        if 'comparison' in self.results:
            report.append("\n## 组间比较结果\n\n")
            comp = self.results['comparison']
            for test_type, res in comp.get('tests', {}).items():
                report.append(f"**{res['test']}**: ")
                if 'statistic' in res:
                    report.append(f"统计量 = {res['statistic']:.4f}, ")
                report.append(f"P = {res['p_value']:.4f}\n")
                report.append(f"结论: {res['interpretation']}\n\n")

        if 'roc_analysis' in self.results:
            report.append("\n## ROC分析结果\n\n")
            roc = self.results['roc_analysis']
            report.append(f"**AUC**: {roc['auc']:.4f} (95% CI: {roc['auc_ci_lower']:.4f}-{roc['auc_ci_upper']:.4f})\n\n")
            report.append(f"- 最佳截断值: {roc['optimal_threshold']:.2f}\n")
            report.append(f"- 敏感度: {roc['sensitivity']:.4f} ({roc['sensitivity']*100:.1f}%)\n")
            report.append(f"- 特异度: {roc['specificity']:.4f} ({roc['specificity']*100:.1f}%)\n\n")

        # 输出文件
        report.append("---\n\n")
        report.append("## 输出文件\n\n")
        for key, path in self.results.items():
            if isinstance(path, str) and path.endswith('.png'):
                report.append(f"- {key}: `{path}`\n")

        return ''.join(report)

    def save_report(self, output_path: str = None, format: str = 'markdown') -> str:
        """保存报告"""
        report = self.generate_report()

        if output_path is None:
            output_path = os.path.join(self.output_dir, 'analysis_report.md')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return output_path


def demo():
    """演示函数"""
    import os
    output_dir = '/workspace/temp-skills/medical-statistics-visualizer/assets'
    os.makedirs(output_dir, exist_ok=True)

    # 创建示例数据
    np.random.seed(42)
    n = 200

    demo_data = pd.DataFrame({
        'group': np.random.choice(['A组', 'B组'], n),
        'time': np.random.exponential(20, n),
        'event': np.random.binomial(1, 0.6, n),
        'age': np.random.normal(55, 10, n),
        'stage': np.random.choice([1, 2, 3, 4], n),
        'CEA': np.random.lognormal(2, 0.5, n),
        'CA19_9': np.random.lognormal(3, 0.6, n),
        'diagnosis': np.random.binomial(1, 0.4, n)
    })
    demo_data['time'] = demo_data['time'].clip(lower=0.5)

    # 初始化分析器
    analyzer = MedicalStatisticsAnalyzer(output_dir=output_dir)
    analyzer.load_dataframe(demo_data)

    # 解析命令
    print("解析测试:")
    print(analyzer.parse_command("比较A组和B组的总生存期，画K-M曲线"))
    print(analyzer.parse_command("评估CA19-9对胰腺癌的诊断效能，画ROC曲线"))
    print(analyzer.parse_command("做Cox回归，分析年龄、分期对生存的影响"))

    # 执行生存分析
    print("\n执行生存分析:")
    results = analyzer.analyze("比较两组的生存差异")

    # 执行ROC分析
    print("\n执行ROC分析:")
    roc_results = analyzer.analyze("评估CA19-9的诊断效能", marker_col='CA19_9', outcome_col='diagnosis')

    # 生成报告
    print("\n生成报告:")
    report = analyzer.generate_report()
    print(report[:1000])

    # 保存报告
    report_path = analyzer.save_report()
    print(f"\n报告已保存至: {report_path}")


if __name__ == '__main__':
    demo()
