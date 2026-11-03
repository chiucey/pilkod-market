"""
Max-RDT 统一入口模块

整合 Recipe、Data Flywheel、Taste Standard 的统一API
"""

from scripts.models import (
    Recipe, TasteProfile, FlywheelMetrics, EvaluationResult,
    TaskOutcome, EnhancedTaskContext
)
from scripts.recipe_engine import RecipeEngine, RecipeDatabase
from scripts.data_flywheel import DataFlywheel
from scripts.taste_engine import TasteStandard
from scripts.integration import MaxRDTLayer, MaxRDTOrchestrator

__all__ = [
    # 模型
    'Recipe',
    'TasteProfile',
    'FlywheelMetrics',
    'EvaluationResult',
    'TaskOutcome',
    'EnhancedTaskContext',
    # 引擎
    'RecipeEngine',
    'RecipeDatabase',
    'DataFlywheel',
    'TasteStandard',
    # 集成层
    'MaxRDTLayer',
    'MaxRDTOrchestrator',
]

__version__ = '1.0.0'
