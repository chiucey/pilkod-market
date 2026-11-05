"""
MiniMax Self-Evolution Package
MiniMax 自进化系统包
"""

from .memory_manager import FiveLayerMemory, memory_system
from .evolution_engine import EvolutionEngine, SuccessTracker, PatternExtractor
from .integration import (
    MiniMaxSelfEvolution,
    MaxHermes,
    MaxClaw,
    DeerFlow,
    create_system
)

__all__ = [
    'FiveLayerMemory',
    'memory_system',
    'EvolutionEngine',
    'SuccessTracker',
    'PatternExtractor',
    'MiniMaxSelfEvolution',
    'MaxHermes',
    'MaxClaw',
    'DeerFlow',
    'create_system'
]

__version__ = '1.0.0'
