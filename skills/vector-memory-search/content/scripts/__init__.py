"""
Vector Memory Search - 神经网络向量记忆系统

解决 MaxHermes 上下文记忆堆栈溢出问题
"""

from .vector_memory_core import (
    TieredMemorySystem,
    MemoryBlock,
    ImportanceScorer,
    VectorStoreBackend,
    ChromaBackend,
    InMemoryBackend,
    DEFAULT_CONFIG,
    generate_id,
    cosine_similarity,
)

__version__ = "1.0.0"
__all__ = [
    "TieredMemorySystem",
    "MemoryBlock",
    "ImportanceScorer",
    "VectorStoreBackend",
    "ChromaBackend",
    "InMemoryBackend",
    "DEFAULT_CONFIG",
    "generate_id",
    "cosine_similarity",
]
