"""
故事剧本转漫画技能
纯Python实现，无需大模型
"""

from .parser import ScriptParser
from .character import CharacterManager
from .scene import SceneGenerator
from .dialogue import DialogueBubble
from .panel import PanelGenerator
from .generator import ComicGenerator

__version__ = "1.0.0"
__all__ = [
    "ScriptParser",
    "CharacterManager",
    "SceneGenerator",
    "DialogueBubble",
    "PanelGenerator",
    "ComicGenerator"
]
