# -*- coding: utf-8 -*-
"""
本地RAG引擎 - 检索增强生成核心实现

功能：
- 文档解析与分块
- 向量化嵌入
- 向量存储与检索
- 上下文组装与答案生成
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """文档块数据结构"""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    chunk_id: str = ""

    def __post_init__(self):
        if not self.chunk_id:
            self.chunk_id = hashlib.md5(
                self.content.encode()).hexdigest()[:12]


@dataclass
class RetrievalResult:
    """检索结果数据结构"""
    content: str
    metadata: Dict[str, Any]
    score: float
    chunk_id: str


class DocumentLoader:
    """文档加载器 - 支持多种格式"""

    @staticmethod
    def load(file_path: str) -> str:
        """加载文档内容"""
        path = Path(file_path)
        suffix = path.suffix.lower()

        loaders = {
            '.txt': DocumentLoader._load_txt,
            '.md': DocumentLoader._load_markdown,
            '.pdf': DocumentLoader._load_pdf,
            '.docx': DocumentLoader._load_docx,
            '.html': DocumentLoader._load_html,
        }

        loader = loaders.get(suffix)
        if not loader:
            raise ValueError(f"不支持的文件格式: {suffix}")

        return loader(path)

    @staticmethod
    def _load_txt(path: Path) -> str:
        """加载文本文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def _load_markdown(path: Path) -> str:
        """加载Markdown文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def _load_pdf(path: Path) -> str:
        """加载PDF文件（需要 PyPDF2 或 pdfplumber）"""
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return '\n\n'.join(text_parts)
        except ImportError:
            logger.warning("pdfplumber 未安装，尝试使用 PyPDF2")
            try:
                from PyPDF2 import PdfReader
                text_parts = []
                reader = PdfReader(path)
                for page in reader.pages:
                    text_parts.append(page.extract_text())
                return '\n\n'.join(text_parts)
            except ImportError:
                raise ImportError("请安装 pdfplumber 或 PyPDF2 来处理 PDF 文件")

    @staticmethod
    def _load_docx(path: Path) -> str:
        """加载Word文档（需要 python-docx）"""
        try:
            from docx import Document
            doc = Document(path)
            paragraphs = [para.text for para in doc.paragraphs if para.text]
            return '\n\n'.join(paragraphs)
        except ImportError:
            raise ImportError("请安装 python-docx 来处理 Word 文档")

    @staticmethod
    def _load_html(path: Path) -> str:
        """加载HTML文件"""
        try:
            from bs4 import BeautifulSoup
            with open(path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator='\n', strip=True)
        except ImportError:
            raise ImportError("请安装 beautifulsoup4 来处理 HTML 文件")


class TextChunker:
    """文本分块器"""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        初始化分块器

        Args:
            chunk_size: 每块字符数
            overlap: 块间重叠字符数
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, metadata: Optional[Dict] = None) -> List[DocumentChunk]:
        """将文本分割成块"""
        metadata = metadata or {}
        chunks = []

        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para_length = len(para)

            # 如果单个段落超过chunk_size，进行进一步分割
            if para_length > self.chunk_size:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, metadata))
                    current_chunk = []
                    current_length = 0

                # 递归分割长段落
                sub_chunks = self._split_long_text(para, metadata)
                chunks.extend(sub_chunks)
                continue

            # 检查是否需要分块
            if current_length + para_length + 1 > self.chunk_size:
                chunks.append(self._create_chunk(current_chunk, metadata))
                # 保留重叠部分
                current_chunk = self._get_overlap_chunks(current_chunk, self.overlap)
                current_length = sum(len(c) for c in current_chunk)

            current_chunk.append(para)
            current_length += para_length + 1

        # 处理最后一块
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, metadata))

        return chunks

    def _split_long_text(self, text: str, metadata: Dict) -> List[DocumentChunk]:
        """分割长文本"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            # 尝试在句子边界分割
            if end < len(text):
                last_period = chunk_text.rfind('。')
                last_newline = chunk_text.rfind('\n')
                split_pos = max(last_period, last_newline)

                if split_pos > self.chunk_size // 2:
                    chunk_text = chunk_text[:split_pos + 1]
                    end = start + split_pos + 1

            chunks.append(DocumentChunk(
                content=chunk_text.strip(),
                metadata=metadata.copy()
            ))
            start = end - self.overlap

        return chunks

    def _create_chunk(self, lines: List[str], metadata: Dict) -> DocumentChunk:
        """创建文档块"""
        return DocumentChunk(
            content='\n'.join(lines),
            metadata=metadata.copy()
        )

    def _get_overlap_chunks(self, chunks: List[str], overlap_chars: int) -> List[str]:
        """获取重叠部分"""
        if not chunks:
            return []

        overlap_text = '\n'.join(chunks)[-overlap_chars:]
        # 找到完整段落的起点
        last_newline = overlap_text.rfind('\n')
        if last_newline > 0:
            overlap_text = overlap_text[last_newline + 1:]

        return [overlap_text] if overlap_text.strip() else []


class EmbeddingEngine:
    """嵌入引擎 - 文本向量化"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        初始化嵌入引擎

        Args:
            model_name: 模型名称或本地路径
        """
        self.model_name = model_name
        self._model = None

    def load_model(self):
        """加载模型"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"正在加载嵌入模型: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info("模型加载完成")
            except ImportError:
                raise ImportError("请安装 sentence-transformers: pip install sentence-transformers")

    def encode(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """编码文本为向量"""
        self.load_model()

        if isinstance(texts, str):
            texts = [texts]

        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def get_embedding_dim(self) -> int:
        """获取向量维度"""
        self.load_model()
        return self._model.get_sentence_embedding_dimension()


class VectorStore:
    """向量存储 - 支持多种后端"""

    def __init__(self, backend: str = "faiss", dimension: int = 384):
        """
        初始化向量存储

        Args:
            backend: 存储后端 (faiss, chroma)
            dimension: 向量维度
        """
        self.backend = backend.lower()
        self.dimension = dimension
        self._index = None
        self._chunks = []
        self._metadata = []

    def init_index(self):
        """初始化索引"""
        if self.backend == "faiss":
            self._init_faiss()
        elif self.backend == "chroma":
            self._init_chroma()
        else:
            raise ValueError(f"不支持的后端: {self.backend}")

    def _init_faiss(self):
        """初始化 Faiss 索引"""
        try:
            import faiss
            # 使用内积索引（需要归一化向量）或 L2 距离索引
            self._index = faiss.IndexFlatIP(self.dimension)
            logger.info(f"已初始化 Faiss 索引，维度: {self.dimension}")
        except ImportError:
            raise ImportError("请安装 faiss: pip install faiss-cpu 或 faiss-gpu")

    def _init_chroma(self):
        """初始化 Chroma 索引"""
        try:
            import chromadb
            self._client = chromadb.Client()
            self._collection = self._client.create_collection("rag_store")
            logger.info("已初始化 Chroma 索引")
        except ImportError:
            raise ImportError("请安装 chromadb: pip install chromadb")

    def add(self, chunks: List[DocumentChunk]):
        """添加文档块到索引"""
        if not chunks:
            return

        if self.backend == "faiss":
            self._add_faiss(chunks)
        elif self.backend == "chroma":
            self._add_chroma(chunks)

    def _add_faiss(self, chunks: List[DocumentChunk]):
        """添加文档块到 Faiss"""
        import faiss
        import numpy as np

        embeddings = np.array([c.embedding for c in chunks]).astype('float32')
        # L2 距离需要归一化
        faiss.normalize_L2(embeddings)
        self._index.add(embeddings)
        self._chunks.extend(chunks)
        logger.info(f"已添加 {len(chunks)} 个文档块到 Faiss 索引")

    def _add_chroma(self, chunks: List[DocumentChunk]):
        """添加文档块到 Chroma"""
        for i, chunk in enumerate(chunks):
            self._collection.add(
                embeddings=[chunk.embedding],
                documents=[chunk.content],
                metadatas=[chunk.metadata],
                ids=[chunk.chunk_id]
            )
            self._chunks.append(chunk)
        logger.info(f"已添加 {len(chunks)} 个文档块到 Chroma 索引")

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[RetrievalResult]:
        """搜索最相似的文档块"""
        if self.backend == "faiss":
            return self._search_faiss(query_embedding, top_k)
        elif self.backend == "chroma":
            return self._search_chroma(query_embedding, top_k)
        return []

    def _search_faiss(self, query_embedding: List[float], top_k: int) -> List[RetrievalResult]:
        """在 Faiss 中搜索"""
        import faiss
        import numpy as np

        query = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query)

        scores, indices = self._index.search(query, min(top_k, len(self._chunks)))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self._chunks):
                chunk = self._chunks[idx]
                results.append(RetrievalResult(
                    content=chunk.content,
                    metadata=chunk.metadata,
                    score=float(score),
                    chunk_id=chunk.chunk_id
                ))

        return results

    def _search_chroma(self, query_embedding: List[float], top_k: int) -> List[RetrievalResult]:
        """在 Chroma 中搜索"""
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        retrieval_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                retrieval_results.append(RetrievalResult(
                    content=doc,
                    metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                    score=results['distances'][0][i] if results['distances'] else 1.0,
                    chunk_id=results['ids'][0][i] if results['ids'] else ""
                ))

        return retrieval_results

    def save(self, path: str):
        """保存索引到磁盘"""
        if self.backend == "faiss":
            import faiss
            faiss.write_index(self._index, path)
            # 保存元数据
            metadata_path = path + ".meta.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump([{
                    "content": c.content,
                    "metadata": c.metadata,
                    "chunk_id": c.chunk_id
                } for c in self._chunks], f, ensure_ascii=False, indent=2)
            logger.info(f"索引已保存到: {path}")

    def load(self, path: str):
        """从磁盘加载索引"""
        if self.backend == "faiss":
            import faiss
            self._index = faiss.read_index(path)
            # 加载元数据
            metadata_path = path + ".meta.json"
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    chunks_data = json.load(f)
                    self._chunks = [
                        DocumentChunk(
                            content=d['content'],
                            metadata=d['metadata'],
                            chunk_id=d['chunk_id']
                        ) for d in chunks_data
                    ]
            logger.info(f"索引已从 {path} 加载")


class RAGEngine:
    """RAG引擎 - 整合所有组件"""

    def __init__(
        self,
        embed_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_provider: str = "mock",
        vector_store: str = "faiss",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        top_k: int = 5,
        similarity_threshold: float = 0.5
    ):
        """
        初始化RAG引擎

        Args:
            embed_model: 嵌入模型名称
            llm_provider: LLM提供者 (mock, ollama, openai, anthropic)
            vector_store: 向量存储后端
            chunk_size: 分块大小
            chunk_overlap: 分块重叠
            top_k: 检索数量
            similarity_threshold: 相似度阈值
        """
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.llm_provider = llm_provider

        # 初始化组件
        self.embedding_engine = EmbeddingEngine(embed_model)
        self.chunker = TextChunker(chunk_size, chunk_overlap)
        self.vector_store = VectorStore(
            backend=vector_store,
            dimension=self.embedding_engine.get_embedding_dim()
        )
        self.vector_store.init_index()

        logger.info(f"RAG引擎初始化完成 | 嵌入模型: {embed_model} | LLM: {llm_provider}")

    def index_documents(self, paths: List[str], show_progress: bool = True) -> Dict[str, Any]:
        """
        索引文档

        Args:
            paths: 文档路径列表（文件或目录）
            show_progress: 是否显示进度

        Returns:
            索引统计信息
        """
        all_chunks = []
        total_files = 0

        # 收集所有文件
        for path_str in paths:
            path = Path(path_str)
            if path.is_file():
                if path.suffix.lower() in ['.txt', '.md', '.pdf', '.docx', '.html']:
                    total_files += 1
            elif path.is_dir():
                for ext in ['.txt', '.md', '.pdf', '.docx', '.html']:
                    total_files += len(list(path.rglob(f"*{ext}")))

        logger.info(f"找到 {total_files} 个文档待处理")

        # 处理每个文件
        processed = 0
        for path_str in paths:
            path = Path(path_str)

            if path.is_file():
                chunks = self._process_file(path)
                all_chunks.extend(chunks)
                processed += 1
                if show_progress:
                    logger.info(f"处理进度: {processed}/{total_files}")

            elif path.is_dir():
                for ext in ['.txt', '.md', '.pdf', '.docx', '.html']:
                    for file_path in path.rglob(f"*{ext}"):
                        chunks = self._process_file(file_path)
                        all_chunks.extend(chunks)
                        processed += 1
                        if show_progress:
                            logger.info(f"处理进度: {processed}/{total_files}")

        # 批量生成嵌入
        logger.info(f"正在生成 {len(all_chunks)} 个文档块的嵌入...")
        contents = [c.content for c in all_chunks]
        embeddings = self.embedding_engine.encode(contents)

        for chunk, embedding in zip(all_chunks, embeddings):
            chunk.embedding = embedding

        # 添加到向量存储
        self.vector_store.add(all_chunks)

        stats = {
            "total_files": total_files,
            "total_chunks": len(all_chunks),
            "avg_chunk_length": sum(len(c.content) for c in all_chunks) / len(all_chunks) if all_chunks else 0
        }

        logger.info(f"索引完成: {stats}")
        return stats

    def _process_file(self, file_path: Path) -> List[DocumentChunk]:
        """处理单个文件"""
        try:
            logger.info(f"正在处理: {file_path.name}")
            text = DocumentLoader.load(str(file_path))
            metadata = {
                "source": str(file_path),
                "filename": file_path.name,
                "file_type": file_path.suffix
            }
            chunks = self.chunker.chunk(text, metadata)
            return chunks
        except Exception as e:
            logger.error(f"处理文件失败 {file_path}: {e}")
            return []

    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        return_sources: bool = True
    ) -> Dict[str, Any]:
        """
        查询问答

        Args:
            question: 问题
            top_k: 检索数量（覆盖默认值）
            return_sources: 是否返回来源

        Returns:
            答案和来源
        """
        top_k = top_k or self.top_k

        # 1. 生成查询向量
        query_embedding = self.embedding_engine.encode(question)

        # 2. 检索相关文档
        results = self.vector_store.search(query_embedding, top_k)

        # 3. 过滤低相似度结果
        results = [r for r in results if r.score >= self.similarity_threshold]

        if not results:
            return {
                "answer": "抱歉，未找到与您问题相关的文档内容。",
                "sources": [],
                "context": ""
            }

        # 4. 组装上下文
        context_parts = []
        for i, r in enumerate(results):
            context_parts.append(f"[文档 {i + 1}] {r.content}")
            if r.metadata.get('source'):
                context_parts.append(f"来源: {r.metadata['source']}")

        context = '\n\n'.join(context_parts)

        # 5. 构建Prompt并生成答案
        prompt = self._build_prompt(question, context)
        answer = self._generate_answer(prompt)

        response = {
            "answer": answer,
            "context": context,
            "num_sources": len(results)
        }

        if return_sources:
            response["sources"] = [
                {
                    "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                    "source": r.metadata.get('source', 'Unknown'),
                    "score": r.score
                }
                for r in results
            ]

        return response

    def _build_prompt(self, question: str, context: str) -> str:
        """构建Prompt"""
        return f"""基于以下参考内容回答问题。如果参考内容不足以回答，请明确说明。

参考内容：
{context}

问题：{question}

回答："""

    def _generate_answer(self, prompt: str) -> str:
        """生成答案（使用配置的LLM）"""
        if self.llm_provider == "mock":
            return self._mock_generate(prompt)
        elif self.llm_provider == "ollama":
            return self._ollama_generate(prompt)
        elif self.llm_provider == "openai":
            return self._openai_generate(prompt)
        elif self.llm_provider == "anthropic":
            return self._anthropic_generate(prompt)
        else:
            return self._mock_generate(prompt)

    def _mock_generate(self, prompt: str) -> str:
        """模拟生成（用于测试）"""
        return "这是一个基于本地RAG的模拟回答。在实际部署中，请配置真实的LLM提供者（如 Ollama、OpenAI 等）来获得真实的生成答案。"

    def _ollama_generate(self, prompt: str, model: str = "llama2") -> str:
        """使用 Ollama 生成答案"""
        try:
            import ollama
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content']
        except ImportError:
            raise ImportError("请安装 ollama Python 包")
        except Exception as e:
            logger.error(f"Ollama 调用失败: {e}")
            return f"Ollama 生成失败: {e}"

    def _openai_generate(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """使用 OpenAI 生成答案"""
        try:
            from openai import OpenAI
            client = OpenAI()
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("请安装 openai Python 包")
        except Exception as e:
            logger.error(f"OpenAI 调用失败: {e}")
            return f"OpenAI 生成失败: {e}"

    def _anthropic_generate(self, prompt: str, model: str = "claude-3-sonnet-20240229") -> str:
        """使用 Anthropic 生成答案"""
        try:
            import anthropic
            client = anthropic.Anthropic()
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except ImportError:
            raise ImportError("请安装 anthropic Python 包")
        except Exception as e:
            logger.error(f"Anthropic 调用失败: {e}")
            return f"Anthropic 生成失败: {e}"

    def save_index(self, path: str):
        """保存索引"""
        self.vector_store.save(path)

    def load_index(self, path: str):
        """加载索引"""
        self.vector_store.load(path)


# 使用示例
if __name__ == "__main__":
    # 示例用法
    rag = RAGEngine(
        embed_model="BAAI/bge-large-zh",
        llm_provider="mock",
        vector_store="faiss",
        chunk_size=500,
        top_k=5
    )

    # 索引文档
    stats = rag.index_documents(["/path/to/your/documents/"])
    print(f"索引统计: {stats}")

    # 保存索引
    rag.save_index("rag_index.faiss")

    # 查询
    result = rag.query("什么是RAG技术？")
    print(f"答案: {result['answer']}")
    print(f"来源: {result['sources']}")
