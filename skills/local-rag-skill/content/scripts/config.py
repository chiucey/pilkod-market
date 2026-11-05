"""
Local RAG Skill - 配置文件
定义知识库的默认配置和参数
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class KnowledgeBaseConfig:
    """知识库配置类"""

    # 数据库路径
    db_path: str = "./vector_db"

    # 文档存储路径
    docs_path: str = "./documents"

    # 分块参数
    chunk_size: int = 500  # 每个文本块的字符数
    chunk_overlap: int = 50  # 相邻块之间的重叠字符数

    # Embedding配置
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # 本地模型
    embedding_device: str = "cpu"  # 或 "cuda"
    use_openai: bool = False  # 是否使用OpenAI API
    openai_api_key: Optional[str] = None
    openai_model: str = "text-embedding-ada-002"

    # 向量数据库配置
    vector_db_type: str = "chroma"  # chroma 或 faiss
    collection_name: str = "knowledge_base"

    # 搜索配置
    default_top_k: int = 4
    similarity_threshold: float = 0.5  # 相似度阈值

    # 支持的文件格式
    supported_formats: list = field(default_factory=lambda: [
        '.pdf', '.docx', '.doc', '.txt', '.md', '.html', '.htm'
    ])

    def __post_init__(self):
        """初始化后处理"""
        # 确保路径为绝对路径
        self.db_path = str(Path(self.db_path).expanduser().absolute())
        self.docs_path = str(Path(self.docs_path).expanduser().absolute())

        # 从环境变量获取OpenAI API Key
        if self.use_openai and not self.openai_api_key:
            self.openai_api_key = os.environ.get("OPENAI_API_KEY")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'embedding_model': self.embedding_model,
            'vector_db_type': self.vector_db_type,
            'collection_name': self.collection_name,
            'default_top_k': self.default_top_k,
            'similarity_threshold': self.similarity_threshold,
        }


# 默认配置实例
DEFAULT_CONFIG = KnowledgeBaseConfig()


def load_config(**kwargs) -> KnowledgeBaseConfig:
    """加载配置，支持自定义参数"""
    config = DEFAULT_CONFIG
    for key, value in kwargs.items():
        if hasattr(config, key) and value is not None:
            setattr(config, key, value)
    return config
