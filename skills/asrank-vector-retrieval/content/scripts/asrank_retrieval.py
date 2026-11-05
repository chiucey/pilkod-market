#!/usr/bin/env python3
"""
ASRANK 向量检索核心实现脚本

两阶段检索：向量召回 + LLM重排
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RetrievalConfig:
    """检索配置参数"""
    chunk_size: int = 800
    chunk_overlap: int = 150
    recall_top_k: int = 100
    rerank_top_k: int = 10
    embedding_model: str = "bge-large-zh"
    rerank_model: str = "gpt-4"


class DocumentParser:
    """文档解析器"""

    SUPPORTED_FORMATS = {
        '.txt', '.md', '.pdf', '.docx', '.doc',
        '.html', '.json', '.csv', '.xlsx'
    }

    @classmethod
    def parse(cls, file_path: str, content: str) -> List[str]:
        """
        解析文档内容并分块

        Args:
            file_path: 文件路径
            content: 文件内容

        Returns:
            分块后的段落列表
        """
        ext = file_path.split('.')[-1].lower() if '.' in file_path else ''

        # 根据格式选择解析方法
        if ext == 'pdf':
            return cls._parse_pdf(content)
        elif ext in ['docx', 'doc']:
            return cls._parse_docx(content)
        elif ext == 'html':
            return cls._parse_html(content)
        else:
            return cls._chunk_text(content)

    @classmethod
    def _chunk_text(cls, text: str, chunk_size: int = 800,
                    overlap: int = 150) -> List[str]:
        """文本分块"""
        if not text or not text.strip():
            return []

        # 清理文本
        text = cls._clean_text(text)

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size

            # 尽量在句号或换行处断开
            if end < text_len:
                # 向前查找最近的句子边界
                boundary = cls._find_sentence_boundary(text, start, end)
                if boundary > start:
                    end = boundary

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap
            if start < 0:
                start = 0

        return chunks

    @classmethod
    def _clean_text(cls, text: str) -> str:
        """清理文本"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符（保留中文、英文、数字、常用标点）
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,!?;:\'\"()\-]', '', text)
        return text.strip()

    @classmethod
    def _find_sentence_boundary(cls, text: str, start: int, end: int) -> int:
        """查找句子边界"""
        # 在指定范围内向前查找句子结束符
        search_range = text[start:end]
        for sep in ['。', '！', '？', '.', '!', '?', '\n']:
            pos = search_range.rfind(sep)
            if pos != -1:
                return start + pos + 1
        return end

    @classmethod
    def _parse_pdf(cls, content: str) -> List[str]:
        """解析PDF内容"""
        # 假设content已经是提取后的文本
        return cls._chunk_text(content)

    @classmethod
    def _parse_docx(cls, content: str) -> List[str]:
        """解析Word文档内容"""
        return cls._chunk_text(content)

    @classmethod
    def _parse_html(cls, content: str) -> List[str]:
        """解析HTML内容"""
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', ' ', content)
        text = re.sub(r'\s+', ' ', text)
        return cls._chunk_text(text)


class VectorRecall:
    """阶段一：向量召回"""

    def __init__(self, config: RetrievalConfig):
        self.config = config
        self.embeddings_cache: Dict[str, List[float]] = {}

    def recall(self, query: str, chunks: List[str],
               top_k: Optional[int] = None) -> List[Dict]:
        """
        向量召回

        Args:
            query: 用户查询
            chunks: 文档段落列表
            top_k: 召回数量

        Returns:
            召回结果列表
        """
        top_k = top_k or self.config.recall_top_k

        if not chunks:
            return []

        # TODO: 集成实际的embedding模型
        # 示例使用模拟向量计算
        query_emb = self._get_embedding(query)

        results = []
        for i, chunk in enumerate(chunks):
            chunk_emb = self._get_embedding(chunk)
            similarity = self._cosine_similarity(query_emb, chunk_emb)

            results.append({
                'index': i,
                'chunk': chunk,
                'vector_score': similarity,
                'length': len(chunk)
            })

        # 按相似度排序
        results.sort(key=lambda x: x['vector_score'], reverse=True)

        return results[:top_k]

    def _get_embedding(self, text: str) -> List[float]:
        """
        获取文本向量

        TODO: 替换为实际的embedding模型调用
        示例: embed_model.encode(text)
        """
        # 模拟向量（实际使用中替换为真实embedding）
        import hashlib
        import struct

        # 生成伪随机但确定的向量
        hash_val = hashlib.md5(text.encode()).digest()
        vec = list(struct.unpack('f' * (len(hash_val) // 4), hash_val))
        # 归一化
        norm = sum(v ** 2 for v in vec) ** 0.5
        return [v / norm for v in vec]

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        dot_prod = sum(x * y for x, y in zip(a, b))
        return max(0.0, min(1.0, dot_prod))  # 归一化到[0,1]


class LLMRerank:
    """Stage 2: LLM Reranking"""

    def __init__(self, config: RetrievalConfig):
        self.config = config
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """加载重排提示模板"""
        return """你是一个专业的文档检索专家。请根据用户问题评估以下每个文档片段的相关性。

用户问题：{query}

文档片段列表：
{documents}

请对每个文档片段的相关性进行评分，输出格式为JSON数组：
[{{"index": 0, "relevance_score": 0.95, "reason": "简要说明"}}, ...]

评分标准：
- 1.0: 完全相关，直接回答问题的关键信息
- 0.7-0.9: 高度相关，包含部分答案或重要上下文
- 0.4-0.6: 中度相关，提供辅助信息
- 0.1-0.3: 低度相关，仅提及相关话题
- 0.0: 不相关，与问题无关

请严格按照JSON格式输出，不要包含其他内容。"""

    def rerank(self, query: str, candidates: List[Dict],
               top_k: Optional[int] = None) -> List[Dict]:
        """
        LLM重排

        Args:
            query: 用户查询
            candidates: 候选结果列表
            top_k: 返回数量

        Returns:
            重排后的结果列表
        """
        top_k = top_k or self.config.rerank_top_k

        if not candidates:
            return []

        # 限制输入数量
        input_candidates = candidates[:50]

        # 构建文档列表
        documents = "\n".join([
            f"[{i}] {c['chunk'][:500]}..."
            for i, c in enumerate(input_candidates)
        ])

        # 构建提示
        prompt = self.prompt_template.format(
            query=query,
            documents=documents
        )

        # TODO: 集成实际的LLM调用
        # response = llm.invoke(prompt)
        # reranked = json.loads(response.content)

        # 模拟LLM重排结果（实际使用中替换为真实LLM调用）
        reranked = self._mock_rerank(query, input_candidates)

        # 合并结果
        final_results = []
        for item in sorted(reranked,
                          key=lambda x: x['relevance_score'],
                          reverse=True)[:top_k]:
            idx = item['index']
            result = {
                'chunk': input_candidates[idx]['chunk'],
                'relevance_score': item['relevance_score'],
                'vector_score': input_candidates[idx]['vector_score'],
                'reason': item['reason'],
                'source_index': input_candidates[idx]['index']
            }
            final_results.append(result)

        return final_results

    def _mock_rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """
        模拟LLM重排（用于测试）

        实际使用中应替换为真实的LLM调用
        """
        import random

        # 简单的基于关键词的模拟评分
        query_words = set(query.lower().split())

        results = []
        for i, c in enumerate(candidates):
            chunk_words = set(c['chunk'].lower().split())

            # 计算词重叠
            overlap = len(query_words & chunk_words)
            base_score = overlap / max(len(query_words), 1)

            # 加入随机因素模拟LLM判断
            score = min(1.0, base_score + random.uniform(-0.1, 0.2))

            results.append({
                'index': i,
                'relevance_score': round(score, 2),
                'reason': f'关键词匹配度：{overlap}个'
            })

        return results


class ASRANKRetriever:
    """ASRANK检索器主类"""

    def __init__(self, config: Optional[RetrievalConfig] = None):
        self.config = config or RetrievalConfig()
        self.vector_recall = VectorRecall(self.config)
        self.llm_rerank = LLMRerank(self.config)
        self.parser = DocumentParser()
        self.chunks: List[str] = []
        self.metadata: List[Dict] = []

    def index_document(self, file_path: str, content: str,
                       metadata: Optional[Dict] = None) -> int:
        """
        索引文档

        Args:
            file_path: 文件路径
            content: 文件内容
            metadata: 元数据

        Returns:
            分块数量
        """
        chunks = self.parser.parse(file_path, content)

        start_idx = len(self.chunks)
        self.chunks.extend(chunks)

        # 保存元数据
        for i, chunk in enumerate(chunks):
            self.metadata.append({
                'chunk_index': start_idx + i,
                'file_path': file_path,
                'metadata': metadata or {}
            })

        return len(chunks)

    def retrieve(self, query: str,
                 recall_top_k: Optional[int] = None,
                 rerank_top_k: Optional[int] = None) -> Dict:
        """
        执行两阶段检索

        Args:
            query: 用户查询
            recall_top_k: 召回数量
            rerank_top_k: 精选数量

        Returns:
            检索结果
        """
        if not self.chunks:
            return {
                'status': 'error',
                'message': 'No documents indexed',
                'results': []
            }

        # 阶段一：向量召回
        recall_results = self.vector_recall.recall(
            query, self.chunks, recall_top_k
        )

        # 阶段二：LLM重排
        rerank_results = self.llm_rerank.rerank(
            query, recall_results, rerank_top_k
        )

        # 构建上下文
        context = self._build_context(rerank_results, query)

        return {
            'status': 'success',
            'query': query,
            'stage1_recall_count': len(recall_results),
            'stage2_rerank_count': len(rerank_results),
            'results': rerank_results,
            'context_for_agent': context
        }

    def _build_context(self, results: List[Dict], query: str) -> str:
        """构建Agent上下文"""
        parts = [
            "=== 参考文档内容 ===",
            f"基于您的问题：{query}\n",
            "以下是相关度最高的文档片段：\n"
        ]

        for i, r in enumerate(results, 1):
            parts.append(
                f"\n【片段 {i}】(相关度: {r['relevance_score']:.2f})"
            )
            parts.append(r['chunk'])

        return "\n".join(parts)


# CLI入口
def main():
    """命令行测试"""
    import sys

    # 创建检索器
    retriever = ASRANKRetriever()

    # 示例文档
    sample_text = """
    人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，
    致力于开发能够执行通常需要人类智能的任务的系统。这包括视觉感知、
    语音识别、决策制定和语言翻译等。机器学习是人工智能的一个子集，
    它使用统计技术使计算机系统能够从数据中"学习"，而无需进行明确的编程。

    深度学习是机器学习的一个分支，它使用多层神经网络来分析各种因素的数据。
    近年来，深度学习在图像识别、自然语言处理等领域取得了突破性进展。
    大语言模型（LLM）是基于深度学习的自然语言处理模型，它们能够理解和生成人类语言。
    """

    # 索引文档
    chunk_count = retriever.index_document("sample.txt", sample_text)
    print(f"索引了 {chunk_count} 个文档块")

    # 执行检索
    query = sys.argv[1] if len(sys.argv) > 1 else "什么是人工智能？"
    results = retriever.retrieve(query)

    print(f"\n查询: {query}")
    print(f"召回数量: {results['stage1_recall_count']}")
    print(f"精选数量: {results['stage2_rerank_count']}")
    print("\n结果:")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
