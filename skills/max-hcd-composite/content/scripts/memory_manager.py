"""
Five-Layer Memory System - 记忆体管理系统
实现5层记忆架构：L1会话 → L2任务 → L3项目 → L4知识库 → L5进化
"""

import json
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import OrderedDict
import asyncio


@dataclass
class MemoryEntry:
    """记忆条目"""
    key: str
    value: Any
    layer: int
    timestamp: float
    access_count: int = 0
    metadata: Optional[Dict] = None

    def to_dict(self):
        return asdict(self)


class PersistentDict:
    """持久化字典存储"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._cache = {}
        self._load()

    def _load(self):
        try:
            with open(self.filepath, 'r') as f:
                self._cache = json.load(f)
        except FileNotFoundError:
            self._cache = {}

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self._cache, f, indent=2, ensure_ascii=False)

    async def set(self, key: str, value: Any, metadata: Optional[Dict] = None):
        entry = {
            'value': value,
            'metadata': metadata or {},
            'timestamp': time.time()
        }
        self._cache[key] = entry
        self._save()

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        return entry['value'] if entry else None

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        results = []
        query_lower = query.lower()
        for key, entry in self._cache.items():
            if query_lower in key.lower() or query_lower in str(entry.get('value', '')).lower():
                results.append({
                    'key': key,
                    'value': entry['value'],
                    'metadata': entry.get('metadata', {}),
                    'score': 1.0 if query_lower in key.lower() else 0.5
                })
        return sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]


class VectorStore:
    """向量知识库（简化版，实际应用中应使用Pinecone/Milvus等）"""

    def __init__(self, name: str):
        self.name = name
        self.vectors = []
        self.metadata = []

    async def add(self, content: str, metadata: Optional[Dict] = None):
        """添加知识条目"""
        vector = self._simple_embed(content)  # 简化嵌入
        self.vectors.append(vector)
        self.metadata.append({
            'content': content,
            'metadata': metadata or {},
            'timestamp': time.time()
        })

    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """向量相似度搜索"""
        query_vec = self._simple_embed(query)
        scores = []

        for i, vec in enumerate(self.vectors):
            score = self._cosine_similarity(query_vec, vec)
            scores.append((i, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in scores[:top_k]:
            results.append({
                'content': self.metadata[idx]['content'],
                'metadata': self.metadata[idx].get('metadata', {}),
                'score': score
            })

        return results

    def _simple_embed(self, text: str) -> List[float]:
        """简化嵌入（实际应用中应使用OpenAI/Cohere等嵌入模型）"""
        words = text.lower().split()
        vec = [0.0] * 128
        for i, word in enumerate(words[:min(len(words), 128)]):
            vec[i % 128] += hash(word) % 100 / 100.0
        return [v / max(len(words), 1) for v in vec]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b + 1e-10)


class ExperienceStore:
    """进化经验存储"""

    def __init__(self, name: str):
        self.name = name
        self.experiences = []

    async def record(self, experience: Any, metadata: Optional[Dict] = None):
        """记录经验"""
        self.experiences.append({
            'experience': experience,
            'metadata': metadata or {},
            'timestamp': time.time()
        })

    async def query(self, context: str, top_k: int = 5) -> List[Dict]:
        """查询相关经验"""
        results = []
        context_lower = context.lower()

        for exp in self.experiences:
            exp_str = str(exp.get('experience', '')).lower()
            if any(word in exp_str for word in context_lower.split()[:3]):
                score = sum(1 for word in context_lower.split()[:5]
                           if word in exp_str) / min(len(context.split()), 5)
                results.append({
                    'experience': exp['experience'],
                    'metadata': exp.get('metadata', {}),
                    'score': score
                })

        return sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]

    async def get_recent(self, count: int) -> List[Dict]:
        """获取最近的经验"""
        return sorted(self.experiences,
                     key=lambda x: x['timestamp'],
                     reverse=True)[:count]


class FiveLayerMemory:
    """
    5层记忆体系统

    L1: 短时会话 - 当前对话上下文
    L2: 任务记忆 - 当前任务状态和进度
    L3: 项目记忆 - 项目级别上下文
    L4: 知识库 - 结构化知识存储
    L5: 进化记忆 - 经验模式库
    """

    # L1 最大容量（条目数）
    L1_MAX_SIZE = 100
    # L1 过期时间（秒）
    L1_TTL = 3600

    def __init__(self, project_file: str = 'project_memory.json'):
        # L1: 短时会话 - 使用有序字典实现LRU
        self.l1_session: OrderedDict = OrderedDict()
        self.l1_timestamps: Dict[str, float] = {}

        # L2: 任务记忆
        self.l2_task: Dict[str, Any] = {
            'current_task': None,
            'subtasks': [],
            'progress': 0.0,
            'history': []
        }

        # L3: 项目记忆 - 持久化
        self.l3_project = PersistentDict(project_file)

        # L4: 知识库 - 向量化
        self.l4_knowledge = VectorStore('knowledge_base')

        # L5: 进化记忆
        self.l5_evolution = ExperienceStore('evolution_memory')

        # 统计数据
        self.stats = {
            'total_stores': 0,
            'total_retrieves': 0,
            'l1_hits': 0,
            'l2_hits': 0,
            'l3_hits': 0,
            'l4_hits': 0,
            'l5_hits': 0
        }

    async def store(self, layer: int, key: str, value: Any,
                   metadata: Optional[Dict] = None) -> bool:
        """存储到指定记忆层"""
        self.stats['total_stores'] += 1

        try:
            if layer == 1:
                return await self._store_l1(key, value)
            elif layer == 2:
                return await self._store_l2(key, value, metadata)
            elif layer == 3:
                await self.l3_project.set(key, value, metadata)
                return True
            elif layer == 4:
                await self.l4_knowledge.add(str(value), metadata)
                return True
            elif layer == 5:
                await self.l5_evolution.record(value, metadata)
                return True
            else:
                raise ValueError(f"Invalid layer: {layer}")
        except Exception as e:
            print(f"Store error at layer {layer}: {e}")
            return False

    async def _store_l1(self, key: str, value: Any) -> bool:
        """L1存储（带LRU和TTL）"""
        # 检查容量
        if len(self.l1_session) >= self.L1_MAX_SIZE and key not in self.l1_session:
            # 移除最旧的条目
            self.l1_session.popitem(last=False)

        self.l1_session[key] = value
        self.l1_timestamps[key] = time.time()
        return True

    async def _store_l2(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """L2存储（任务记忆）"""
        self.l2_task[key] = value
        if metadata:
            # 记录到历史
            self.l2_task['history'].append({
                'key': key,
                'value': value,
                'metadata': metadata,
                'timestamp': time.time()
            })
        return True

    async def retrieve(self, query: str, layers: Optional[List[int]] = None,
                      top_k: int = 5) -> List[Dict]:
        """跨层检索"""
        layers = layers or [1, 2, 3, 4, 5]
        results = []
        self.stats['total_retrieves'] += 1

        for layer in sorted(layers):
            try:
                if layer == 1:
                    layer_results = self._retrieve_l1(query)
                    self.stats['l1_hits'] += len(layer_results)
                elif layer == 2:
                    layer_results = await self._retrieve_l2(query, top_k)
                    self.stats['l2_hits'] += len(layer_results)
                elif layer == 3:
                    layer_results = self.l3_project.search(query, top_k)
                    self.stats['l3_hits'] += len(layer_results)
                elif layer == 4:
                    layer_results = await self.l4_knowledge.search(query, top_k)
                    self.stats['l4_hits'] += len(layer_results)
                elif layer == 5:
                    layer_results = await self.l5_evolution.query(query, top_k)
                    self.stats['l5_hits'] += len(layer_results)

                # 标记来源层
                for r in layer_results:
                    r['layer'] = layer
                results.extend(layer_results)

            except Exception as e:
                print(f"Retrieve error at layer {layer}: {e}")

        # 按分数排序并合并
        return self._rank_and_merge(results)

    def _retrieve_l1(self, query: str) -> List[Dict]:
        """L1检索（精确匹配 + 前缀匹配）"""
        results = []
        query_lower = query.lower()
        current_time = time.time()

        keys_to_remove = []

        for key, value in self.l1_session.items():
            # 检查TTL
            if current_time - self.l1_timestamps.get(key, 0) > self.L1_TTL:
                keys_to_remove.append(key)
                continue

            # 匹配
            score = 0.0
            if key.lower() == query_lower:
                score = 1.0
            elif key.lower().startswith(query_lower):
                score = 0.8
            elif query_lower in key.lower():
                score = 0.6
            elif query_lower in str(value).lower():
                score = 0.4

            if score > 0:
                results.append({
                    'key': key,
                    'value': value,
                    'score': score,
                    'layer': 1
                })

        # 清理过期条目
        for key in keys_to_remove:
            self.l1_session.pop(key, None)
            self.l1_timestamps.pop(key, None)

        return sorted(results, key=lambda x: x['score'], reverse=True)

    async def _retrieve_l2(self, query: str, top_k: int) -> List[Dict]:
        """L2检索（任务记忆）"""
        results = []
        query_lower = query.lower()

        # 搜索当前任务
        current = self.l2_task.get('current_task')
        if current and query_lower in str(current).lower():
            results.append({
                'key': 'current_task',
                'value': current,
                'score': 1.0,
                'layer': 2
            })

        # 搜索子任务
        for i, subtask in enumerate(self.l2_task.get('subtasks', [])):
            if query_lower in str(subtask).lower():
                results.append({
                    'key': f'subtask_{i}',
                    'value': subtask,
                    'score': 0.8,
                    'layer': 2
                })

        return sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]

    def _rank_and_merge(self, results: List[Dict]) -> List[Dict]:
        """结果排序与合并"""
        # 按分数、层级的复合排序
        # 层级权重：L1 > L2 > L3 > L4 > L5
        layer_weights = {1: 1.0, 2: 0.9, 3: 0.8, 4: 0.7, 5: 0.6}

        for r in results:
            r['final_score'] = r['score'] * layer_weights.get(r['layer'], 0.5)

        # 去重（基于key）
        seen = set()
        unique_results = []
        for r in results:
            key = r.get('key', str(r.get('value', '')))
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        return sorted(unique_results, key=lambda x: x['final_score'], reverse=True)

    def get_stats(self) -> Dict:
        """获取记忆系统统计"""
        return {
            **self.stats,
            'l1_size': len(self.l1_session),
            'l1_capacity': self.L1_MAX_SIZE,
            'l2_task': {
                'has_current': self.l2_task.get('current_task') is not None,
                'subtask_count': len(self.l2_task.get('subtasks', [])),
                'history_size': len(self.l2_task.get('history', []))
            }
        }

    async def clear_layer(self, layer: int):
        """清除指定层"""
        if layer == 1:
            self.l1_session.clear()
            self.l1_timestamps.clear()
        elif layer == 2:
            self.l2_task = {
                'current_task': None,
                'subtasks': [],
                'progress': 0.0,
                'history': []
            }
        elif layer == 3:
            self.l3_project._cache = {}
            self.l3_project._save()
        elif layer == 4:
            self.l4_knowledge.vectors = []
            self.l4_knowledge.metadata = []
        elif layer == 5:
            self.l5_evolution.experiences = []

    def summary(self) -> str:
        """获取记忆系统摘要"""
        stats = self.get_stats()
        return f"""
╔═══════════════════════════════════════════════════╗
║           5-LAYER MEMORY SYSTEM STATUS            ║
╠═══════════════════════════════════════════════════╣
║  L1 SESSION  │ {stats['l1_size']:3d}/{stats['l1_capacity']:<3d} │ Hits: {stats['l1_hits']:<5d}        ║
║  L2 TASK     │ {stats['l2_task']['subtask_count']:<3d} tasks│ Hits: {stats['l2_hits']:<5d}        ║
║  L3 PROJECT  │ Active │ Hits: {stats['l3_hits']:<5d}        ║
║  L4 KNOWLEDGE│ {len(self.l4_knowledge.vectors):<4d} items│ Hits: {stats['l4_hits']:<5d}        ║
║  L5 EVOLUTION│ {len(self.l5_evolution.experiences):<4d} exp │ Hits: {stats['l5_hits']:<5d}        ║
╠═══════════════════════════════════════════════════╣
║  Total Stores: {stats['total_stores']:<5d} │ Total Retrieves: {stats['total_retrieves']:<5d}   ║
╚═══════════════════════════════════════════════════╝
        """


# 便捷函数
def create_memory_system(project_name: str = 'default') -> FiveLayerMemory:
    """创建记忆系统实例"""
    return FiveLayerMemory(f'{project_name}_memory.json')


if __name__ == '__main__':
    # 测试
    async def test():
        memory = create_memory_system('test')

        # 存储测试
        await memory.store(1, 'user_name', 'Alice')
        await memory.store(2, 'current_task', 'Building a chatbot')
        await memory.store(3, 'project_goal', 'Create an intelligent assistant')
        await memory.store(4, 'Python is a great language for AI')
        await memory.store(5, {'success_pattern': 'break_complex_tasks'})

        # 检索测试
        results = await memory.retrieve('task')
        print("Search results for 'task':")
        for r in results:
            print(f"  Layer {r['layer']}: {r.get('key', 'value')} (score: {r['final_score']:.2f})")

        print(memory.summary())

    asyncio.run(test())
