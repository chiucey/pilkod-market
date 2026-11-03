"""
Local RAG Skill - 本地知识库主类
提供完整的增删改查接口
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Union
from dataclasses import asdict
import numpy as np

from .config import KnowledgeBaseConfig, load_config
from .document_processor import DocumentProcessor, ProcessedDocument
from .vector_store import VectorStore, create_vector_store, SearchResult


class LocalKnowledgeBase:
    """本地知识库主类"""

    def __init__(self, db_path: str = "./vector_db", **kwargs):
        """
        初始化知识库

        Args:
            db_path: 数据库存储路径
            **kwargs: 其他配置参数
        """
        self.config = load_config(db_path=db_path, **kwargs)

        # 初始化文档处理器
        self.doc_processor = DocumentProcessor(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )

        # 初始化向量存储
        self.vector_store = create_vector_store(
            db_type=self.config.vector_db_type,
            db_path=self.config.db_path,
            collection_name=self.config.collection_name
        )

        # 初始化Embedding模型
        self._init_embedding_model()

        # 文档元数据存储
        self.docs_meta_path = os.path.join(self.config.db_path, "docs_meta.json")
        self.docs_meta = self._load_docs_meta()

        # Markdown内容存储路径
        self.md_store_path = os.path.join(self.config.db_path, "markdown_docs")
        os.makedirs(self.md_store_path, exist_ok=True)

    def _init_embedding_model(self):
        """初始化Embedding模型"""
        if self.config.use_openai and self.config.openai_api_key:
            try:
                import openai
                openai.api_key = self.config.openai_api_key
                self.embedding_client = "openai"
            except ImportError:
                raise ImportError("请安装 openai: pip install openai")
        else:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(
                    self.config.embedding_model,
                    device=self.config.embedding_device
                )
                self.embedding_client = "local"
            except ImportError:
                raise ImportError(
                    "请安装 sentence-transformers: pip install sentence-transformers"
                )

    def _get_embedding(self, texts: Union[str, List[str]]) -> np.ndarray:
        """获取文本的Embedding向量"""
        if isinstance(texts, str):
            texts = [texts]

        if self.embedding_client == "openai":
            import openai
            response = openai.Embedding.create(
                model=self.config.openai_model,
                input=texts
            )
            embeddings = [item['embedding'] for item in response['data']]
            return np.array(embeddings)
        else:
            embeddings = self.embedding_model.encode(texts)
            return embeddings

    def _load_docs_meta(self) -> Dict:
        """加载文档元数据"""
        if os.path.exists(self.docs_meta_path):
            with open(self.docs_meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_docs_meta(self):
        """保存文档元数据"""
        with open(self.docs_meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.docs_meta, f, ensure_ascii=False, indent=2)

    # ==================== 核心API ====================

    def add_document(
        self,
        file_path: str,
        metadata: Optional[Dict] = None,
        auto_convert_md: bool = True
    ) -> str:
        """
        添加文档到知识库

        Args:
            file_path: 文件路径
            metadata: 额外元数据
            auto_convert_md: 是否自动转换为Markdown

        Returns:
            文档ID
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 处理文档
        processed_doc = self.doc_processor.process_file(file_path, metadata)

        # 保存Markdown内容
        md_file_path = os.path.join(self.md_store_path, f"{processed_doc.doc_id}.md")
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {processed_doc.title}\n\n")
            f.write(processed_doc.content)

        # 存储向量
        for chunk in processed_doc.chunks:
            embedding = self._get_embedding(chunk.content)
            self.vector_store.add(
                chunk_id=chunk.chunk_id,
                doc_id=processed_doc.doc_id,
                content=chunk.content,
                embedding=embedding,
                metadata={**processed_doc.metadata, 'chunk_index': chunk.index}
            )

        # 保存元数据
        self.docs_meta[processed_doc.doc_id] = {
            'doc_id': processed_doc.doc_id,
            'title': processed_doc.title,
            'source_path': processed_doc.source_path,
            'md_path': md_file_path,
            'metadata': processed_doc.metadata,
            'chunk_count': len(processed_doc.chunks),
            'added_at': processed_doc.metadata.get('processed_at', '')
        }
        self._save_docs_meta()

        return processed_doc.doc_id

    def add_text(
        self,
        text: str,
        title: str = "Untitled",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        添加纯文本到知识库

        Args:
            text: 文本内容
            title: 标题
            metadata: 额外元数据

        Returns:
            文档ID
        """
        import uuid
        from datetime import datetime

        doc_id = uuid.uuid4().hex[:12]

        # 分块
        chunks = self.doc_processor._chunk_text(text, doc_id)

        # 保存Markdown内容
        md_file_path = os.path.join(self.md_store_path, f"{doc_id}.md")
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n{text}")

        # 存储向量
        for chunk in chunks:
            embedding = self._get_embedding(chunk.content)
            self.vector_store.add(
                chunk_id=chunk.chunk_id,
                doc_id=doc_id,
                content=chunk.content,
                embedding=embedding,
                metadata={
                    'title': title,
                    'source': 'text_input',
                    'chunk_index': chunk.index,
                    'added_at': datetime.now().isoformat(),
                    **(metadata or {})
                }
            )

        # 保存元数据
        self.docs_meta[doc_id] = {
            'doc_id': doc_id,
            'title': title,
            'source_path': '',
            'md_path': md_file_path,
            'metadata': metadata or {},
            'chunk_count': len(chunks),
            'added_at': datetime.now().isoformat()
        }
        self._save_docs_meta()

        return doc_id

    def delete_document(self, doc_id: str) -> bool:
        """
        从知识库删除文档

        Args:
            doc_id: 文档ID

        Returns:
            是否成功删除
        """
        if doc_id not in self.docs_meta:
            return False

        # 删除向量
        self.vector_store.delete(doc_id)

        # 删除Markdown文件
        md_path = self.docs_meta[doc_id].get('md_path')
        if md_path and os.path.exists(md_path):
            os.remove(md_path)

        # 删除元数据
        del self.docs_meta[doc_id]
        self._save_docs_meta()

        return True

    def update_document(
        self,
        doc_id: str,
        new_file_path: Optional[str] = None,
        new_text: Optional[str] = None,
        new_title: Optional[str] = None,
        new_metadata: Optional[Dict] = None
    ) -> bool:
        """
        更新文档

        Args:
            doc_id: 文档ID
            new_file_path: 新文件路径
            new_text: 新文本内容
            new_title: 新标题
            new_metadata: 新元数据

        Returns:
            是否成功更新
        """
        if doc_id not in self.docs_meta:
            return False

        # 删除旧文档
        self.delete_document(doc_id)

        # 添加新文档
        if new_file_path:
            new_doc_id = self.add_document(new_file_path, new_metadata)
        elif new_text:
            title = new_title or self.docs_meta[doc_id].get('title', 'Untitled')
            new_doc_id = self.add_text(new_text, title, new_metadata)
        else:
            return False

        # 如果指定了新的标题，需要更新
        if new_title and new_file_path:
            # 重新读取并更新Markdown文件
            md_path = self.docs_meta[new_doc_id]['md_path']
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(f"# {self.docs_meta[new_doc_id]['title']}", f"# {new_title}")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.docs_meta[new_doc_id]['title'] = new_title
            self._save_docs_meta()

        return True

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict] = None,
        return_raw: bool = False
    ) -> List[Dict]:
        """
        搜索知识库

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_metadata: 元数据过滤条件
            return_raw: 是否返回原始SearchResult对象

        Returns:
            搜索结果列表
        """
        if top_k is None:
            top_k = self.config.default_top_k

        # 获取查询向量
        query_embedding = self._get_embedding(query)

        # 搜索
        results = self.vector_store.search(query_embedding, top_k)

        # 过滤
        if filter_metadata:
            filtered_results = []
            for result in results:
                match = True
                for key, value in filter_metadata.items():
                    if result.metadata.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_results.append(result)
            results = filtered_results

        # 过滤低于阈值的结果
        results = [
            r for r in results
            if r.score >= self.config.similarity_threshold
        ]

        if return_raw:
            return results

        # 构建返回结果
        output = []
        for result in results:
            doc_meta = self.docs_meta.get(result.doc_id, {})
            output.append({
                'chunk_id': result.chunk_id,
                'doc_id': result.doc_id,
                'content': result.content,
                'score': result.score,
                'title': doc_meta.get('title', ''),
                'source': doc_meta.get('source_path', ''),
                'metadata': result.metadata
            })

        return output

    def get_document(self, doc_id: str, include_chunks: bool = False) -> Optional[Dict]:
        """
        获取文档信息

        Args:
            doc_id: 文档ID
            include_chunks: 是否包含所有块

        Returns:
            文档信息字典
        """
        if doc_id not in self.docs_meta:
            return None

        meta = self.docs_meta[doc_id]

        result = {
            'doc_id': doc_id,
            'title': meta['title'],
            'source_path': meta['source_path'],
            'metadata': meta['metadata'],
            'chunk_count': meta['chunk_count'],
            'added_at': meta['added_at']
        }

        # 读取Markdown内容
        md_path = meta.get('md_path')
        if md_path and os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                result['content'] = f.read()
        else:
            result['content'] = ""

        # 获取所有块
        if include_chunks:
            chunks = self.vector_store.get_by_doc_id(doc_id)
            result['chunks'] = [
                {
                    'chunk_id': c.chunk_id,
                    'content': c.content,
                    'index': c.metadata.get('chunk_index', 0)
                }
                for c in chunks
            ]

        return result

    def list_documents(self, with_content: bool = False) -> List[Dict]:
        """
        列出所有文档

        Args:
            with_content: 是否包含内容

        Returns:
            文档列表
        """
        docs = []
        for doc_id, meta in self.docs_meta.items():
            doc_info = {
                'doc_id': doc_id,
                'title': meta['title'],
                'source_path': meta['source_path'],
                'chunk_count': meta['chunk_count'],
                'added_at': meta['added_at']
            }

            if with_content:
                md_path = meta.get('md_path')
                if md_path and os.path.exists(md_path):
                    with open(md_path, 'r', encoding='utf-8') as f:
                        doc_info['content'] = f.read()
                else:
                    doc_info['content'] = ""

            docs.append(doc_info)

        return sorted(docs, key=lambda x: x['added_at'], reverse=True)

    def get_stats(self) -> Dict:
        """获取知识库统计信息"""
        return {
            'total_documents': len(self.docs_meta),
            'total_chunks': self.vector_store.count(),
            'db_path': self.config.db_path,
            'vector_db_type': self.config.vector_db_type,
            'embedding_model': self.config.embedding_model,
            'documents': [
                {
                    'doc_id': doc_id,
                    'title': meta['title'],
                    'chunk_count': meta['chunk_count']
                }
                for doc_id, meta in self.docs_meta.items()
            ]
        }

    def exists(self, doc_id: str) -> bool:
        """检查文档是否存在"""
        return doc_id in self.docs_meta

    def clear(self) -> int:
        """
        清空知识库

        Returns:
            删除的文档数量
        """
        count = len(self.docs_meta)
        for doc_id in list(self.docs_meta.keys()):
            self.delete_document(doc_id)
        return count

    # ==================== 批量操作 ====================

    def add_documents_batch(self, file_paths: List[str], metadata: Optional[Dict] = None) -> List[str]:
        """
        批量添加文档

        Args:
            file_paths: 文件路径列表
            metadata: 额外元数据

        Returns:
            添加的文档ID列表
        """
        doc_ids = []
        for file_path in file_paths:
            try:
                doc_id = self.add_document(file_path, metadata)
                doc_ids.append(doc_id)
            except Exception as e:
                print(f"处理文件失败 {file_path}: {e}")

        return doc_ids

    def add_folder(self, folder_path: str, recursive: bool = True) -> List[str]:
        """
        添加文件夹中的所有文档

        Args:
            folder_path: 文件夹路径
            recursive: 是否递归处理子文件夹

        Returns:
            添加的文档ID列表
        """
        path = Path(folder_path)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"无效的文件夹路径: {folder_path}")

        file_paths = []
        if recursive:
            for ext in self.config.supported_formats:
                file_paths.extend(path.rglob(f"*{ext}"))
        else:
            for ext in self.config.supported_formats:
                file_paths.extend(path.glob(f"*{ext}"))

        return self.add_documents_batch([str(f) for f in file_paths])
