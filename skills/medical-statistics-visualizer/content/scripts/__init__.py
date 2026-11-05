"""
Medical Statistics Visualizer - 医学统计分析可视化工具
Version: 1.0.0

提供专业的医学统计分析能力：
- 生存分析 (Kaplan-Meier, Log-rank, Cox回归)
- 统计检验 (t检验, Mann-Whitney, 卡方检验, Fisher精确检验)
- 回归分析 (Logistic回归, 线性回归)
- ROC曲线分析
- 高质量可视化图表

使用方法:
    from scripts.main_analyzer import MedicalStatisticsAnalyzer

    analyzer = MedicalStatisticsAnalyzer(output_dir='./output')
    analyzer.load_data('your_data.csv')
    results = analyzer.analyze('比较A组和B组的生存差异')
    report = analyzer.generate_report()
"""

from .survival_analysis import SurvivalAnalyzer
from .statistical_tests import StatisticalTester
from .regression_analysis import RegressionAnalyzer
from .roc_analysis import ROCAnalyzer
from .visualization import VisualizationEngine
from .data_parser import DataParser
from .main_analyzer import MedicalStatisticsAnalyzer

__all__ = [
    'SurvivalAnalyzer',
    'StatisticalTester',
    'RegressionAnalyzer',
    'ROCAnalyzer',
    'VisualizationEngine',
    'DataParser',
    'MedicalStatisticsAnalyzer'
]

__version__ = '1.0.0'
