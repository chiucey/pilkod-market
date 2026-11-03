#!/usr/bin/env python3
"""
Vector Memory Core - 核心实现
神经网络向量记忆系统的核心模块
"""

import asyncio
import hashlib
import json
import time
from collections import OrderedDict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import numpy as np


# ============== 配置 ==============

DEFAULT_CONFIG = {
    "embedding_model": "text-embedding-3-small",
    "embedding_dimension": 1536,
    "longterm_capacity": 10000,
    "working_capacity": 50,
    "immediate_capacity": 3,
    "default_top_k": 5,
    "similarity_threshold": 0.75,
    "deduplication_threshold": 0.85,
    "promotion_threshold": 0.7,
    "forgetting_threshold": 0.3,
    "decay_factor": 0.95,
}

SCORING_WEIGHTS = {
    "frequency": 0.1,
    "recency": 0.2,
    "uniqueness": 0.2,
    "task_relevance": 0.3,
    "user_emphasis": 0.2,
}


# ============== 数据模型 ==============

@dataclass
class MemoryBlock:
    """记忆块"""
    id: str
    content: str
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    importance_score: float = 0.5
    tier: str = "working"  # immediate, working, longterm
    metadata: dict = field(default_factory=dict)
    vector: Optionallist] = None  # 延迟加载

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryBlock":
        return cls(**data)


@dataclass
class Turn:
    """对话轮次"""
    user: str
    assistant: str
    timestamp: float = field(default_factory=time.time)


# ============== 工具函数 ==============

def generate_id(content: str) -> str:
    """生成记忆唯一ID"""
    return hashlib.sha256(f"{content}{time.time()}".encode()).hexdigest()[:16]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """计算余弦相似度"""
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def truncate_content(content: str, max_length: int = 2000) -> str:
    """截断内容"""
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


# ============== 向量存储接口 ==============

class VectorStoreBackend:
    """向量存储后端接口"""

    async def add(self, memory_id: str, vector: list[float], content: str, metadata: dict):
        """添加记忆"""
        raise NotImplementedError

    async def search(self, query_vector: list[float], top_k: int, threshold: float) -> list[tuple]:
        """搜索相似记忆"""
        raise NotImplementedError

    async def delete(self, memory_id: str):
        """删除记忆"""
        raise NotImplementedError

    async def count(self) -> int:
        """获取记忆数量"""
        raise NotImplementedError

    async def get(self, memory_id: str) -> Optional[dict]:
        """获取单个记忆"""
        raise NotImplementedError


class ChromaBackend(VectorStoreBackend):
    """ChromaDB后端实现"""

    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "memory"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self._client = None
        self._collection = None

    def _ensure_init(self):
        """延迟初始化"""
        if self._client is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=chromadb.config.Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"description": "Long-term memory store"}
                )
            except ImportError:
                raise ImportError("请安装 chromadb: pip install chromadb")

    async def add(self, memory_id: str, vector: list[float], content: str, metadata: dict):
        self._ensure_init()
        self._collection.add(
            ids=[memory_id],
            embeddings=[vector],
            documents=[content],
            metadatas=[metadata]
        )

    async def search(self, query_vector: list[float], top_k: int, threshold: float) -> list[tuple]:
        self._ensure_init()
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )

        matches = []
        if results["ids"] and results["ids"][0]:
            for i, (memory_id, distance, doc, meta) in enumerate(zip(
                results["ids"][0],
                results["distances"][0],
                results["documents"][0],
                results["metadatas"][0]
            )):
                similarity = 1 - distance
                if similarity >= threshold:
                    matches.append((memory_id, similarity, doc, meta))

        return matches

    async def delete(self, memory_id: str):
        self._ensure_init()
        self._collection.delete(ids=[memory_id])

    async def count(self) -> int:
        self._ensure_init()
        return self._collection.count()

    async def get(self, memory_id: str) -> Optional[dict]:
        self._ensure_init()
        try:
            result = self._collection.get(ids=[memory_id])
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0]
                }
        except Exception:
            pass
        return None


class InMemoryBackend(VectorStoreBackend):
    """内存后端实现 (用于测试或小规模部署)"""

    def __init__(self):
        self._vectors: dict[str, list[float]] = {}
        self._contents: dict[str, str] = {}
        self._metadata: dict[str, dict] = {}

    async def add(self, memory_id: str, vector: list[float], content: str, metadata: dict):
        self._vectors[memory_id] = vector
        self._contents[memory_id] = content
        self._metadata[memory_id] = metadata

    async def search(self, query_vector: list[float], top_k: int, threshold: float) -> list[tuple]:
        if not self._vectors:
            return []

        similarities = []
        for memory_id, vector in self._vectors.items():
            sim = cosine_similarity(query_vector, vector)
            if sim >= threshold:
                similarities.append((memory_id, sim, self._contents[memory_id], self._metadata[memory_id]))

        # 排序并返回top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    async def delete(self, memory_id: str):
        self._vectors.pop(memory_id, None)
        self._contents.pop(memory_id, None)
        self._metadata.pop(memory_id, None)

    async def count(self) -> int:
        return len(self._vectors)

    async def get(self, memory_id: str) -> Optional[dict]:
        if memory_id in self._contents:
            return {
                "id": memory_id,
                "content": self._contents[memory_id],
                "metadata": self._metadata[memory_id]
            }
        return None


# ============== 重要性评分器 ==============

class ImportanceScorer:
    """多因子重要性评分器"""

    def __init__(self, weights: dict = SCORING_WEIGHTS):
        self.weights = weights

    async def score(self, content: str, session_context: dict, existing_memories: list[MemoryBlock] = None) -> dict:
        """
        计算记忆重要性分数

        返回:
            {
                "total_score": float,
                "factors": dict,
                "tier": str  # immediate, working, longterm
            }
        """
        factors = {
            "frequency": self._calc_frequency(content, existing_memories or []),
            "recency": 0.5,  # 新记忆默认中间值
            "uniqueness": self._calc_uniqueness(content, existing_memories or []),
            "task_relevance": self._calc_relevance(content, session_context),
            "user_emphasis": self._calc_emphasis(content)
        }

        # 加权求和
        total_score = sum(factors[k] * self.weights[k] for k in self.weights)

        # 归一化到0-1
        total_score = min(1.0, max(0.0, total_score))

        return {
            "total_score": total_score,
            "factors": factors,
            "tier": self._get_tier(total_score)
        }

    def _calc_frequency(self, content: str, memories: list[MemoryBlock]) -> float:
        """计算出现频率因子"""
        if not memories:
            return 0.5
        count = sum(1 for m in memories if content in m.content)
        return min(1.0, count / 10)

    def _calc_uniqueness(self, content: str, memories: list[MemoryBlock]) -> float:
        """计算独特性因子"""
        if not memories:
            return 0.8  # 新内容默认高独特性
        similar = sum(1 for m in memories if cosine_similarity(
            self._simple_hash(content),
            self._simple_hash(m.content)
        ) > 0.8)
        return max(0.0, 1.0 - similar * 0.1)

    def _calc_relevance(self, content: str, context: dict) -> float:
        """计算任务相关性"""
        topic = context.get("topic", "")
        keywords = context.get("keywords", [])

        score = 0.5
        if topic and topic.lower() in content.lower():
            score += 0.3
        for kw in keywords:
            if kw.lower() in content.lower():
                score += 0.1

        return min(1.0, score)

    def _calc_emphasis(self, content: str) -> float:
        """计算用户强调程度"""
        emphasis_markers = ["重要", "记住", "特别", "务必", "关键", "强调", "important", "remember", "key"]
        count = sum(1 for marker in emphasis_markers if marker.lower() in content.lower())
        return min(1.0, 0.5 + count * 0.1)

    def _get_tier(self, score: float) -> str:
        """根据分数确定存储层级"""
        if score >= 0.7:
            return "longterm"
        elif score >= 0.4:
            return "working"
        return "immediate"

    def _simple_hash(self, text: str) -> list[float]:
        """简单文本哈希 (用于快速相似度计算)"""
        import hashlib
        h = hashlib.md5(text.encode()).digest()
        return list(h[:16]) + [0] * (16 - 16)


# ============== 分层记忆系统 ==============

class TieredMemorySystem:
    """
    三层记忆系统

    层级:
    1. Immediate - 即时记忆 (当前对话轮次)
    2. Working - 工作记忆 (滑动窗口)
    3. LongTerm - 长期记忆 (向量数据库)
    """

    def __init__(self, config: dict = None, backend: VectorStoreBackend = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.scorer = ImportanceScorer()

        # 即时记忆
        self.immediate_buffer: list[Turn] = []
        self.max_immediate = self.config["immediate_capacity"]

        # 工作记忆
        self.working_cache: OrderedDict[str, MemoryBlock] = OrderedDict()
        self.max_working = self.config["working_capacity"]

        # 长期记忆
        self.backend = backend or InMemoryBackend()

    async def store(self, user_input: str, assistant_response: str, session_context: dict = None):
        """
        存储对话记忆

        Args:
            user_input: 用户输入
            assistant_response: 助手回复
            session_context: 会话上下文
        """
        session_context = session_context or {}
        combined = f"用户: {user_input}\n助手: {assistant_response}"

        # 1. 添加到即时记忆
        self._add_immediate(user_input, assistant_response)

        # 2. 评估重要性
        existing = list(self.working_cache.values())
        score_result = await self.scorer.score(combined, session_context, existing)

        # 3. 根据层级存储
        tier = score_result["tier"]

        if tier in ("working", "longterm"):
            memory_block = MemoryBlock(
                id=generate_id(combined),
                content=combined,
                importance_score=score_result["total_score"],
                tier=tier,
                metadata={
                    "user_input": user_input,
                    "assistant_response": assistant_response,
                    "session_id": session_context.get("session_id", "default"),
                    "topic": session_context.get("topic", ""),
                    "created_at": datetime.now().isoformat()
                }
            )

            if tier == "working":
                self._add_working(memory_block)
            else:
                await self._add_longterm(memory_block)

        # 4. 定期清理
        if len(self.working_cache) > self.max_working:
            self._forget_low_value()

    def _add_immediate(self, user_input: str, assistant_response: str):
        """添加即时记忆"""
        self.immediate_buffer.append(Turn(user=user_input, assistant=assistant_response))
        if len(self.immediate_buffer) > self.max_immediate:
            self.immediate_buffer.pop(0)

    def _add_working(self, block: MemoryBlock):
        """添加工作记忆"""
        # 检查是否已存在
        if block.id in self.working_cache:
            self._touch_working(block.id)
            return

        self.working_cache[block.id] = block
        self.working_cache.move_to_end(block.id)

        # 容量检查
        if len(self.working_cache) > self.max_working:
            self.working_cache.popitem(last=False)

    def _touch_working(self, block_id: str):
        """更新工作记忆访问"""
        if block_id in self.working_cache:
            block = self.working_cache[block_id]
            block.last_accessed = time.time()
            block.access_count += 1
            self.working_cache.move_to_end(block_id)

    async def _add_longterm(self, block: MemoryBlock):
        """添加长期记忆"""
        # 生成向量 (延迟到实际需要时)
        vector = self._generate_mock_vector(block.content)

        await self.backend.add(
            memory_id=block.id,
            vector=vector,
            content=block.content,
            metadata=block.metadata
        )

    def _generate_mock_vector(self, content: str) -> list[float]:
        """生成模拟向量 (生产环境应使用真实嵌入模型)"""
        import hashlib
        h = hashlib.sha256(content.encode()).digest()
        vec = list(np.frombuffer(h, dtype=np.float32))
        # 归一化
        vec = vec / (np.linalg.norm(vec) + 1e-8)
        return vec.tolist()

    def _forget_low_value(self):
        """遗忘低价值记忆"""
        if not self.working_cache:
            return

        threshold = self.config["forgetting_threshold"]

        # 计算有效分数
        def effective_score(block: MemoryBlock) -> float:
            age_hours = (time.time() - block.created_at) / 3600
            decay = self.config["decay_factor"] ** age_hours
            return block.importance_score * decay

        # 找到最低分
        lowest_id = min(
            self.working_cache.keys(),
            key=lambda k: effective_score(self.working_cache[k])
        )

        if effective_score(self.working_cache[lowest_id]) < threshold:
            del self.working_cache[lowest_id]

    async def retrieve(self, query: str, top_k: int = None) -> dict:
        """
        检索相关记忆

        Returns:
            {
                "immediate": str,
                "working": list[MemoryBlock],
                "longterm": list[tuple]
            }
        """
        top_k = top_k or self.config["default_top_k"]

        # 即时记忆
        immediate_context = self._get_immediate_context()

        # 工作记忆 (计算相似度)
        working_results = self._search_working(query, top_k)

        # 长期记忆
        query_vector = self._generate_mock_vector(query)
        longterm_results = await self.backend.search(
            query_vector=query_vector,
            top_k=top_k,
            threshold=self.config["similarity_threshold"]
        )

        return {
            "immediate": immediate_context,
            "working": working_results,
            "longterm": longterm_results
        }

    def _get_immediate_context(self) -> str:
        """获取即时记忆上下文"""
        if not self.immediate_buffer:
            return ""
        return "\n".join([
            f"用户: {t.user}\n助手: {t.assistant}"
            for t in self.immediate_buffer
        ])

    def _search_working(self, query: str, top_k: int) -> list[MemoryBlock]:
        """在工作记忆中搜索"""
        if not self.working_cache:
            return []

        query_vec = self._generate_mock_vector(query)
        results = []

        for block in self.working_cache.values():
            if block.content:
                block_vec = self._generate_mock_vector(block.content)
                sim = cosine_similarity(query_vec, block_vec)
                if sim >= self.config["similarity_threshold"]:
                    results.append((block, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:top_k]]

    def build_context(self, retrieval_result: dict, max_length: int = 8000) -> str:
        """构建模型上下文"""
        parts = []

        # 长期记忆 (高优先级)
        if retrieval_result["longterm"]:
            parts.append("【相关背景知识】")
            for _, sim, content, _ in retrieval_result["longterm"][:3]:
                parts.append(f"- {truncate_content(content, 500)} (相关度: {sim:.2f})")

        # 工作记忆
        if retrieval_result["working"]:
            parts.append("\n【工作上下文】")
            for block in retrieval_result["working"][:2]:
                parts.append(f"- {truncate_content(block.content, 300)}")

        # 即时记忆
        if retrieval_result["immediate"]:
            parts.append("\n【当前对话】")
            parts.append(retrieval_result["immediate"])

        context = "\n".join(parts)

        # 截断
        if len(context) > max_length:
            context = context[:max_length] + "\n...(上下文已截断)"

        return context

    async def get_stats(self) -> dict:
        """获取记忆统计"""
        return {
            "immediate": len(self.immediate_buffer),
            "working": len(self.working_cache),
            "longterm": await self.backend.count(),
            "config": self.config
        }

    async def clear(self, tier: str = None):
        """清理记忆"""
        if tier == "immediate" or tier is None:
            self.immediate_buffer.clear()
        if tier == "working" or tier is None:
            self.working_cache.clear()
        if tier == "longterm" or tier is None:
            # 清空后端需要特殊处理
            pass


# ============== 导出 ==============

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
