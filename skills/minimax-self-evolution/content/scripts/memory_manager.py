"""
记忆体管理器 - FiveLayerMemory 实现

提供完整的五层记忆体系统，支持：
- L1: 会话上下文（内存）
- L2: 任务状态（任务周期）
- L3: 项目上下文（跨会话）
- L4: 知识库（永久）
- L5: 进化记忆（永久）
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional
from collections import OrderedDict
from dataclasses import dataclass, asdict


@dataclass
class MemoryEntry:
    """记忆条目"""
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    metadata: Optional[Dict] = None


class L1SessionMemory:
    """L1 会话记忆 - 高速内存缓存"""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.store: OrderedDict[str, MemoryEntry] = OrderedDict()

    def set(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """设置记忆"""
        entry = MemoryEntry(
            key=key,
            value=value,
            timestamp=time.time(),
            metadata=metadata
        )
        self.store[key] = entry

        # 保持大小限制
        if len(self.store) > self.max_size:
            self.store.popitem(last=False)

    def get(self, key: str) -> Optional[Any]:
        """获取记忆"""
        if key in self.store:
            entry = self.store[key]
            entry.access_count += 1
            # 移动到末尾（最近使用）
            self.store.move_to_end(key)
            return entry.value
        return None

    def search(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        """搜索记忆"""
        results = []
        query_lower = query.lower()

        for entry in self.store.values():
            value_str = str(entry.value).lower()
            if query_lower in value_str:
                results.append(entry)

            # 检查键名
            if query_lower in entry.key.lower():
                results.append(entry)

        return results[:top_k]

    def clear(self):
        """清空会话记忆"""
        self.store.clear()


class L2TaskMemory:
    """L2 任务记忆 - 当前任务上下文"""

    def __init__(self):
        self.current_task: Optional[Dict] = None
        self.subtasks: List[Dict] = []
        self.progress: float = 0.0
        self.checkpoint: Optional[Dict] = None
        self.task_history: List[Dict] = []

    def start_task(self, task: Dict):
        """开始新任务"""
        # 保存当前任务到历史
        if self.current_task:
            self.task_history.append({
                'task': self.current_task,
                'progress': self.progress,
                'completed_at': time.time()
            })

        self.current_task = task
        self.subtasks = task.get('subtasks', [])
        self.progress = 0.0

    def update_progress(self, subtask_id: str, status: str, result: Any = None):
        """更新任务进度"""
        for subtask in self.subtasks:
            if subtask.get('id') == subtask_id:
                subtask['status'] = status
                subtask['result'] = result
                subtask['updated_at'] = time.time()
                break

        # 计算总体进度
        completed = sum(1 for s in self.subtasks if s.get('status') == 'completed')
        self.progress = completed / len(self.subtasks) if self.subtasks else 0

    def create_checkpoint(self) -> str:
        """创建检查点"""
        checkpoint_id = f"cp_{int(time.time() * 1000)}"
        self.checkpoint = {
            'id': checkpoint_id,
            'task': self.current_task,
            'subtasks': self.subtasks.copy(),
            'progress': self.progress,
            'created_at': time.time()
        }
        return checkpoint_id

    def restore_checkpoint(self, checkpoint: Dict):
        """恢复检查点"""
        self.current_task = checkpoint.get('task')
        self.subtasks = checkpoint.get('subtasks', [])
        self.progress = checkpoint.get('progress', 0.0)

    def get_state(self) -> Dict:
        """获取任务状态"""
        return {
            'current_task': self.current_task,
            'subtasks': self.subtasks,
            'progress': self.progress,
            'checkpoint': self.checkpoint
        }


class L3ProjectMemory:
    """L3 项目记忆 - 跨会话持久化"""

    def __init__(self, storage_path: str = './project_memory.json'):
        self.storage_path = storage_path
        self.store: Dict[str, Any] = {}
        self.load()

    def load(self):
        """从磁盘加载"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                self.store = json.load(f)
        except FileNotFoundError:
            self.store = {}

    def save(self):
        """保存到磁盘"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.store, f, ensure_ascii=False, indent=2)

    async def set(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """设置项目记忆"""
        self.store[key] = {
            'value': value,
            'metadata': metadata or {},
            'updated_at': time.time()
        }
        self.save()

    async def get(self, key: str) -> Optional[Any]:
        """获取项目记忆"""
        if key in self.store:
            return self.store[key]['value']
        return None

    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索项目记忆"""
        results = []
        query_lower = query.lower()

        for key, data in self.store.items():
            value_str = str(data['value']).lower()
            if query_lower in value_str or query_lower in key.lower():
                results.append({
                    'key': key,
                    'value': data['value'],
                    'metadata': data.get('metadata'),
                    'relevance': value_str.count(query_lower)
                })

        # 按相关性排序
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:top_k]


class L4KnowledgeBase:
    """L4 知识库 - 向量化语义存储"""

    def __init__(self, storage_path: str = './knowledge_base.json'):
        self.storage_path = storage_path
        self.entries: List[Dict] = []
        self.load()

    def load(self):
        """加载知识库"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                self.entries = json.load(f)
        except FileNotFoundError:
            self.entries = []

    def save(self):
        """保存知识库"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

    async def upsert(self, value: Any, metadata: Optional[Dict] = None):
        """添加或更新知识条目"""
        entry = {
            'content': value,
            'metadata': metadata or {},
            'created_at': time.time(),
            'access_count': 0
        }

        # 检查是否已存在
        content_hash = str(hash(str(value)))
        for i, e in enumerate(self.entries):
            if e.get('content_hash') == content_hash:
                self.entries[i] = {**e, **entry}
                self.save()
                return

        entry['content_hash'] = content_hash
        self.entries.append(entry)
        self.save()

    async def similarity_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """语义相似度搜索（简化版：基于关键词匹配）"""
        query_terms = set(query.lower().split())

        scored = []
        for entry in self.entries:
            content_str = str(entry.get('content', '')).lower()
            content_terms = set(content_str.split())

            # 计算交集
            overlap = len(query_terms & content_terms)
            if overlap > 0:
                scored.append({
                    'content': entry.get('content'),
                    'metadata': entry.get('metadata'),
                    'score': overlap / len(query_terms)
                })

        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:top_k]


class L5EvolutionMemory:
    """L5 进化记忆 - 经验模式库"""

    def __init__(self, storage_path: str = './evolution_memory.json'):
        self.storage_path = storage_path
        self.experiences: List[Dict] = []
        self.preferences: Dict[str, Any] = {}
        self.success_patterns: List[Dict] = []
        self.failure_lessons: List[Dict] = []
        self.load()

    def load(self):
        """加载进化记忆"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.experiences = data.get('experiences', [])
                self.preferences = data.get('preferences', {})
                self.success_patterns = data.get('success_patterns', [])
                self.failure_lessons = data.get('failure_lessons', [])
        except FileNotFoundError:
            self.reset()

    def save(self):
        """保存进化记忆"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump({
                'experiences': self.experiences,
                'preferences': self.preferences,
                'success_patterns': self.success_patterns,
                'failure_lessons': self.failure_lessons,
                'saved_at': time.time()
            }, f, ensure_ascii=False, indent=2)

    def reset(self):
        """重置进化记忆"""
        self.experiences = []
        self.preferences = {}
        self.success_patterns = []
        self.failure_lessons = []

    async def record(self, value: Any, metadata: Optional[Dict] = None):
        """记录经验"""
        entry = {
            'content': value,
            'metadata': metadata or {},
            'timestamp': time.time()
        }

        # 根据元数据分类存储
        record_type = metadata.get('record_type', 'experience')

        if record_type == 'preference':
            pref_type = metadata.get('preference_type', 'general')
            self.preferences[pref_type] = entry
        elif record_type == 'success_pattern':
            self.success_patterns.append(entry)
        elif record_type == 'failure_lesson':
            self.failure_lessons.append(entry)
        else:
            self.experiences.append(entry)

        self.save()

    async def query_experiences(self, query: str, top_k: int = 5) -> List[Dict]:
        """查询相关经验"""
        query_lower = query.lower()
        results = []

        for exp in self.experiences:
            content_str = str(exp.get('content', '')).lower()
            if query_lower in content_str:
                results.append(exp)

        return results[:top_k]

    async def get_preferences(self) -> Dict[str, Any]:
        """获取所有偏好"""
        return self.preferences.copy()

    async def get_success_patterns(self, task_type: str = None) -> List[Dict]:
        """获取成功模式"""
        if task_type:
            return [p for p in self.success_patterns
                   if p.get('metadata', {}).get('task_type') == task_type]
        return self.success_patterns.copy()

    async def get_failure_lessons(self, task_type: str = None) -> List[Dict]:
        """获取失败教训"""
        if task_type:
            return [l for l in self.failure_lessons
                   if l.get('metadata', {}).get('task_type') == task_type]
        return self.failure_lessons.copy()


class FiveLayerMemory:
    """
    五层记忆体系统 - 统一接口

    提供跨层的统一存储和检索接口
    """

    def __init__(self):
        # 初始化各层记忆
        self.l1_session = L1SessionMemory()
        self.l2_task = L2TaskMemory()
        self.l3_project = L3ProjectMemory()
        self.l4_knowledge = L4KnowledgeBase()
        self.l5_evolution = L5EvolutionMemory()

        # 层级映射
        self.layers = {
            1: self.l1_session,
            2: self.l2_task,
            3: self.l3_project,
            4: self.l4_knowledge,
            5: self.l5_evolution
        }

    async def store(self, layer: int, key: str, value: Any, metadata: Optional[Dict] = None):
        """存储到指定层"""
        if layer == 1:
            self.l1_session.set(key, value, metadata)
        elif layer == 2:
            await self.l2_task.set(key, value, metadata) if hasattr(self.l2_task, 'set') else None
        elif layer == 3:
            await self.l3_project.set(key, value, metadata)
        elif layer == 4:
            await self.l4_knowledge.upsert(value, metadata)
        elif layer == 5:
            await self.l5_evolution.record(value, metadata)

    async def retrieve(self, query: str, layers: List[int] = None, top_k: int = 5) -> List[Dict]:
        """跨层检索"""
        layers = layers or [1, 2, 3, 4, 5]
        results = []

        for layer in sorted(layers):
            if layer == 1:
                results.extend(self.l1_session.search(query, top_k))
            elif layer == 2:
                # L2 任务记忆搜索
                state = self.l2_task.get_state()
                if query.lower() in str(state).lower():
                    results.append(state)
            elif layer == 3:
                results.extend(await self.l3_project.search(query, top_k))
            elif layer == 4:
                results.extend(await self.l4_knowledge.similarity_search(query, top_k))
            elif layer == 5:
                results.extend(await self.l5_evolution.query_experiences(query, top_k))

        return self._rank_and_merge(results, query)[:top_k]

    def _rank_and_merge(self, results: List[Dict], query: str) -> List[Dict]:
        """排序合并结果"""
        # 简单实现：按相关性排序
        return results

    def get_system_status(self) -> Dict:
        """获取记忆体系统状态"""
        return {
            'l1_session_size': len(self.l1_session.store),
            'l2_task_active': self.l2_task.current_task is not None,
            'l2_task_progress': self.l2_task.progress,
            'l3_project_count': len(self.l3_project.store),
            'l4_knowledge_entries': len(self.l4_knowledge.entries),
            'l5_experiences': len(self.l5_evolution.experiences),
            'l5_preferences': len(self.l5_evolution.preferences),
            'l5_success_patterns': len(self.l5_evolution.success_patterns),
            'l5_failure_lessons': len(self.l5_evolution.failure_lessons)
        }


# 导出
__all__ = [
    'FiveLayerMemory',
    'L1SessionMemory',
    'L2TaskMemory',
    'L3ProjectMemory',
    'L4KnowledgeBase',
    'L5EvolutionMemory',
    'MemoryEntry'
]
