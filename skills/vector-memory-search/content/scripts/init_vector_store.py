#!/usr/bin/env python3
"""
Vector Memory Store - 初始化脚本
用于初始化向量数据库和配置

使用方法:
    python init_vector_store.py --mode standalone
    python init_vector_store.py --mode distributed
    python init_vector_store.py --reindex
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 向量存储后端选项
BACKENDS = {
    "chroma": "ChromaDB - 生产级向量数据库",
    "faiss": "FAISS - Facebook高性能向量检索",
    "sqlite": "SQLite + NumPy - 嵌入式轻量方案",
    "qdrant": "Qdrant - 云原生向量搜索引擎"
}


class VectorStoreConfig:
    """向量存储配置管理"""

    def __init__(self, storage_path: str = "./vector_memory_data"):
        self.storage_path = Path(storage_path)
        self.config_file = self.storage_path / "config.json"

    def get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            "version": "1.0.0",
            "initialized_at": datetime.now().isoformat(),
            "embedding": {
                "model": "text-embedding-3-small",
                "dimension": 1536,
                "batch_size": 100
            },
            "storage": {
                "backend": "chroma",
                "persist_directory": "./chroma_db"
            },
            "memory": {
                "longterm_capacity": 10000,
                "working_capacity": 50,
                "immediate_capacity": 3
            },
            "retrieval": {
                "default_top_k": 5,
                "similarity_threshold": 0.75,
                "enable_reranking": True
            },
            "management": {
                "auto_forget": True,
                "deduplication_threshold": 0.85,
                "promotion_interval": 10,
                "cleanup_interval_hours": 24
            }
        }

    def save_config(self, config: dict):
        """保存配置"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✓ 配置已保存至: {self.config_file}")

    def load_config(self) -> Optional[dict]:
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None


class VectorStoreInitializer:
    """向量存储初始化器"""

    def __init__(self, config: VectorStoreConfig):
        self.config = config

    async def initialize_chroma(self) -> bool:
        """初始化ChromaDB后端"""
        try:
            import chromadb
            from chromadb.config import Settings

            persist_dir = self.config.get_default_config()["storage"]["persist_directory"]

            client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # 创建集合
            collection = client.get_or_create_collection(
                name="longterm_memory",
                metadata={"description": "长期记忆向量存储"}
            )

            print(f"✓ ChromaDB初始化成功")
            print(f"  - 持久化目录: {persist_dir}")
            print(f"  - 集合名称: longterm_memory")
            print(f"  - 向量维度: 1536")

            return True

        except ImportError:
            print("✗ ChromaDB未安装，请运行: pip install chromadb")
            return False
        except Exception as e:
            print(f"✗ ChromaDB初始化失败: {e}")
            return False

    async def initialize_faiss(self) -> bool:
        """初始化FAISS后端"""
        try:
            import faiss
            import numpy as np

            dimension = self.config.get_default_config()["embedding"]["dimension"]

            # 使用IndexFlatIP (内积) 用于余弦相似度
            index = faiss.IndexFlatIP(dimension)

            # 归一化向量
            faiss.normalize_L2(index)

            print(f"✓ FAISS初始化成功")
            print(f"  - 向量维度: {dimension}")
            print(f"  - 索引类型: IndexFlatIP (内积)")

            return True

        except ImportError:
            print("✗ FAISS未安装，请运行: pip install faiss-cpu 或 faiss-gpu")
            return False
        except Exception as e:
            print(f"✗ FAISS初始化失败: {e}")
            return False

    async def initialize_sqlite(self) -> bool:
        """初始化SQLite后端"""
        try:
            import sqlite3
            import numpy as np

            db_path = self.config.storage_path / "memory.sqlite"

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 创建记忆表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    vector BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    importance_score REAL DEFAULT 0.5,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    metadata TEXT
                )
            """)

            # 创建向量索引表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_index (
                    memory_id TEXT,
                    index_type TEXT,
                    index_data BLOB,
                    FOREIGN KEY (memory_id) REFERENCES memories(id)
                )
            """)

            # 创建元数据索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_importance
                ON memories(importance_score DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created
                ON memories(created_at DESC)
            """)

            conn.commit()
            conn.close()

            print(f"✓ SQLite后端初始化成功")
            print(f"  - 数据库路径: {db_path}")

            return True

        except Exception as e:
            print(f"✗ SQLite初始化失败: {e}")
            return False

    async def initialize_qdrant(self) -> bool:
        """初始化Qdrant后端"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            # 尝试连接本地Qdrant
            client = QdrantClient(host="localhost", port=6333)

            # 创建集合
            dimension = self.config.get_default_config()["embedding"]["dimension"]

            collections = client.get_collections().collections
            collection_names = [c.name for c in collections]

            if "longterm_memory" not in collection_names:
                client.create_collection(
                    collection_name="longterm_memory",
                    vectors_config=VectorParams(
                        size=dimension,
                        distance=Distance.COSINE
                    )
                )

            print(f"✓ Qdrant后端初始化成功")
            print(f"  - 地址: localhost:6333")
            print(f"  - 集合: longterm_memory")

            return True

        except ImportError:
            print("✗ Qdrant客户端未安装，请运行: pip install qdrant-client")
            return False
        except Exception as e:
            print(f"✗ Qdrant初始化失败: {e}")
            print("  提示: 确保Qdrant服务正在运行")
            return False

    async def run_initialization(self, backend: str = "chroma"):
        """运行初始化流程"""
        print("=" * 50)
        print("Vector Memory Store 初始化")
        print("=" * 50)
        print()

        # 保存配置
        config = self.config.get_default_config()
        config["storage"]["backend"] = backend
        self.config.save_config(config)

        # 根据后端初始化
        print(f"正在初始化 {backend.upper()} 后端...")
        print()

        init_methods = {
            "chroma": self.initialize_chroma,
            "faiss": self.initialize_faiss,
            "sqlite": self.initialize_sqlite,
            "qdrant": self.initialize_qdrant
        }

        if backend in init_methods:
            success = await init_methods[backend]()
        else:
            print(f"✗ 不支持的后端: {backend}")
            print(f"  可选后端: {', '.join(BACKENDS.keys())}")
            return False

        if success:
            print()
            print("=" * 50)
            print("✓ 初始化完成!")
            print("=" * 50)
            print()
            print("下一步:")
            print("  1. 查看配置: cat vector_memory_data/config.json")
            print("  2. 测试连接: python test_connection.py")
            print("  3. 开始使用向量记忆系统")
            return True

        return False


class VectorStoreDiagnostics:
    """向量存储诊断工具"""

    @staticmethod
    def check_dependencies():
        """检查依赖项"""
        print("检查依赖项...")
        print()

        deps = {
            "chromadb": "ChromaDB向量数据库",
            "faiss": "FAISS向量索引",
            "numpy": "NumPy数值计算",
            "openai": "OpenAI API客户端",
            "qdrant-client": "Qdrant客户端"
        }

        installed = []
        missing = []

        for package, description in deps.items():
            try:
                __import__(package.replace("-", "_"))
                print(f"  ✓ {description}")
                installed.append(package)
            except ImportError:
                print(f"  ✗ {description} (未安装)")
                missing.append(package)

        print()
        if missing:
            print(f"缺少 {len(missing)} 个依赖项:")
            print(f"  pip install {' '.join(missing)}")
        else:
            print("✓ 所有依赖项已安装")

        return len(missing) == 0

    @staticmethod
    def check_storage_health(storage_path: str = "./vector_memory_data"):
        """检查存储健康状态"""
        print(f"检查存储路径: {storage_path}")
        print()

        path = Path(storage_path)

        if not path.exists():
            print("  ⚠ 存储路径不存在，需要初始化")
            return False

        # 检查目录权限
        if os.access(path, os.W_OK):
            print("  ✓ 写入权限正常")
        else:
            print("  ✗ 缺少写入权限")
            return False

        # 检查配置文件
        config_file = path / "config.json"
        if config_file.exists():
            print("  ✓ 配置文件存在")
            with open(config_file, "r") as f:
                config = json.load(f)
                print(f"    - 版本: {config.get('version')}")
                print(f"    - 后端: {config['storage']['backend']}")
                print(f"    - 初始化时间: {config.get('initialized_at')}")
        else:
            print("  ⚠ 配置文件不存在，需要初始化")

        print()
        return True


async def main():
    parser = argparse.ArgumentParser(description="Vector Memory Store 初始化工具")
    parser.add_argument(
        "--mode",
        choices=["chroma", "faiss", "sqlite", "qdrant"],
        default="chroma",
        help="选择向量存储后端"
    )
    parser.add_argument(
        "--path",
        default="./vector_memory_data",
        help="存储路径"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="仅检查依赖和健康状态"
    )
    parser.add_argument(
        "--backend-info",
        action="store_true",
        help="显示后端信息"
    )

    args = parser.parse_args()

    if args.backend_info:
        print("可用的向量存储后端:")
        print()
        for key, desc in BACKENDS.items():
            print(f"  {key:10} - {desc}")
        print()
        return

    if args.check:
        VectorStoreDiagnostics.check_dependencies()
        print()
        VectorStoreDiagnostics.check_storage_health(args.path)
        return

    config = VectorStoreConfig(args.path)
    initializer = VectorStoreInitializer(config)
    await initializer.run_initialization(args.mode)


if __name__ == "__main__":
    asyncio.run(main())
