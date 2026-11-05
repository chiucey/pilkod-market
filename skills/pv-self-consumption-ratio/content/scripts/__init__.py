"""
分布式光伏自消纳比例测算技能
PV Self-Consumption Ratio Calculator Skill

本模块提供企业分布式光伏项目自消纳比例测算功能
"""

from .pv_calculator import (
    PVProjectParams,
    EnterpriseLoadParams,
    PVSelfConsumptionCalculator
)

from .data_processor import (
    ElectricityBillProcessor,
    LoadCurveProcessor,
    DataStandardizer
)

from .report_generator import (
    ReportGenerator,
    ScenarioComparator,
    export_report_summary
)

__all__ = [
    'PVProjectParams',
    'EnterpriseLoadParams',
    'PVSelfConsumptionCalculator',
    'ElectricityBillProcessor',
    'LoadCurveProcessor',
    'DataStandardizer',
    'ReportGenerator',
    'ScenarioComparator',
    'export_report_summary'
]

__version__ = '1.0.0'
