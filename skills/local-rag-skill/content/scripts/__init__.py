"""
Local RAG Skill - 本地知识库工具包
"""

from .config import KnowledgeBaseConfig, load_config, DEFAULT_CONFIG
from .document_processor import DocumentProcessor, ProcessedDocument, DocumentChunk
from .vector_store import VectorStore, ChromaStore, FAISSStore, SearchResult, create_vector_store
from .knowledge_base import LocalKnowledgeBase
from .cli import main as cli_main

__version__ = "1.0.0"

__all__ = [
    "KnowledgeBaseConfig",
    "load_config",
    "DEFAULT_CONFIG",
    "DocumentProcessor",
    "ProcessedDocument",
    "DocumentChunk",
    "VectorStore",
    "ChromaStore",
    "FAISSStore",
    "SearchResult",
    "create_vector_store",
    "LocalKnowledgeBase",
    "cli_main",
]
