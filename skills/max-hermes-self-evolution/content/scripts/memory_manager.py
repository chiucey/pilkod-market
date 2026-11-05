"""
Five-Layer Memory Manager
实现 MiniMax Agent 五层记忆体系统
"""

import time
from typing import Any, Dict, List, Optional


class Layer1SessionMemory:
    """L1 会话记忆 - 最快速访问层"""

    def __init__(self, max_items: int = 100):
        self.max_items = max_items
        self.store: Dict[str, Dict] = {}

    def set(self, key: str, value: Any) -> None:
        """设置会话记忆"""
        self.store[key] = {
            'value': value,
            'timestamp': time.time(),
            'access_count': 0
        }
        self._evict_if_needed()

    def get(self, key: str) -> Optional[Any]:
        """获取会话记忆"""
        if key in self.store:
            self.store[key]['access_count'] += 1
            return self.store[key]['value']
        return None

    def _evict_if_needed(self):
        """淘汰最旧项"""
        if len(self.store) > self.max_items:
            oldest_key = min(
                self.store.keys(),
                key=lambda k: self.store[k]['timestamp']
            )
            del self.store[oldest_key]

    def clear(self):
        """清空会话记忆"""
        self.store.clear()


class Layer2TaskMemory:
    """L2 任务记忆 - 任务状态管理层"""

    def __init__(self):
        self.current_task: Optional[Dict] = None
        self.subtasks: List[Dict] = []
        self.progress: float = 0.0
        self.checkpoint: Optional[Dict] = None

    async def save_checkpoint(self, task_id: str) -> str:
        """保存任务检查点"""
        checkpoint = {
            'id': f"cp_{int(time.time() * 1000)}",
            'task_id': task_id,
            'state': {
                'current_task': self.current_task,
                'subtasks': self.subtasks,
                'progress': self.progress
            },
            'created_at': time.time()
        }
        self.checkpoint = checkpoint
        return checkpoint['id']

    async def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """恢复任务检查点"""
        if self.checkpoint and self.checkpoint['id'] == checkpoint_id:
            state = self.checkpoint['state']
            self.current_task = state['current_task']
            self.subtasks = state['subtasks']
            self.progress = state['progress']
            return True
        return False


class Layer3ProjectMemory:
    """L3 项目记忆 - 跨会话项目上下文"""

    def __init__(self, storage_path: str = "/memories/projects"):
        self.storage_path = storage_path
        self.project_contexts: Dict[str, Dict] = {}

    async def save_project(self, project_id: str, context: Dict) -> None:
        """保存项目上下文"""
        self.project_contexts[project_id] = {
            'context': context,
            'updated_at': time.time(),
            'file_structure': context.get('files', []),
            'decisions': context.get('decisions', [])
        }

    async def get_project(self, project_id: str) -> Optional[Dict]:
        """获取项目上下文"""
        return self.project_contexts.get(project_id)

    async def search_projects(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索项目"""
        results = []
        for pid, data in self.project_contexts.items():
            if query.lower() in str(data.get('context', '')).lower():
                results.append({'project_id': pid, 'data': data})
        return results[:top_k]


class Layer4KnowledgeBase:
    """L4 知识库 - 向量化知识存储"""

    def __init__(self):
        self.vectors: List[Dict] = []
        self.metadata: List[Dict] = []

    async def upsert(self, content: str, metadata: Optional[Dict] = None) -> str:
        """添加或更新知识"""
        vector_id = f"vec_{len(self.vectors)}"
        self.vectors.append({'id': vector_id, 'content': content})
        self.metadata.append(metadata or {})
        return vector_id

    async def similarity_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """语义相似度搜索"""
        query_lower = query.lower()
        scored = []
        for vec in self.vectors:
            content_lower = vec['content'].lower()
            score = sum(1 for word in query_lower.split() if word in content_lower)
            if score > 0:
                scored.append({'id': vec['id'], 'content': vec['content'], 'score': score})
        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:top_k]


class Layer5EvolutionMemory:
    """L5 进化记忆 - 经验模式库"""

    def __init__(self):
        self.experiences: List[Dict] = []
        self.patterns: Dict[str, List[Dict]] = {
            'success': [],
            'failure': [],
            'preference': []
        }
        self.lessons: List[Dict] = []

    async def record(self, experience_type: str, data: Dict, metadata: Optional[Dict] = None) -> None:
        """记录进化经验"""
        record = {
            'type': experience_type,
            'data': data,
            'metadata': metadata or {},
            'timestamp': time.time()
        }
        self.experiences.append(record)

        if experience_type in self.patterns:
            self.patterns[experience_type].append(record)

    async def query_experiences(self, query: str, top_k: int = 5) -> List[Dict]:
        """查询进化经验"""
        results = []
        for exp in self.experiences:
            if query.lower() in str(exp.get('data', '')).lower():
                results.append(exp)
        return results[:top_k]

    async def get_patterns(self, pattern_type: str) -> List[Dict]:
        """获取特定类型的模式"""
        return self.patterns.get(pattern_type, [])

    async def extract_lessons(self, limit: int = 10) -> List[Dict]:
        """提取教训"""
        return self.lessons[:limit]


class FiveLayerMemory:
    """
    五层记忆体系统管理器
    协调 L1-L5 各层之间的交互
    """

    def __init__(self):
        self.l1_session = Layer1SessionMemory()
        self.l2_task = Layer2TaskMemory()
        self.l3_project = Layer3ProjectMemory()
        self.l4_knowledge = Layer4KnowledgeBase()
        self.l5_evolution = Layer5EvolutionMemory()

    async def store(self, layer: int, key: str, value: Any, metadata: Optional[Dict] = None) -> None:
        """存储到指定记忆层"""
        if layer == 1:
            self.l1_session.set(key, value)
        elif layer == 2:
            if isinstance(value, dict):
                self.l2_task.current_task = value
        elif layer == 3:
            await self.l3_project.save_project(key, value)
        elif layer == 4:
            await self.l4_knowledge.upsert(value, metadata)
        elif layer == 5:
            await self.l5_evolution.record(key, value, metadata)

    async def retrieve(self, query: str, layers: Optional[List[int]] = None, top_k: int = 5) -> List[Dict]:
        """跨层语义检索"""
        layers = layers or [1, 2, 3, 4, 5]
        results = []

        for layer in layers:
            layer_results = await self._retrieve_layer(layer, query, top_k)
            results.extend(layer_results)

        return self._rank_results(results, query)

    async def _retrieve_layer(self, layer: int, query: str, top_k: int) -> List[Dict]:
        """从指定层检索"""
        if layer == 1:
            return [{'layer': 1, 'key': k, 'value': v['value']}
                    for k, v in self.l1_session.store.items()
                    if query.lower() in str(v['value']).lower()][:top_k]
        elif layer == 2:
            if self.l2_task.current_task and query.lower() in str(self.l2_task.current_task).lower():
                return [{'layer': 2, 'data': self.l2_task.current_task}]
        elif layer == 3:
            return await self.l3_project.search_projects(query, top_k)
        elif layer == 4:
            return await self.l4_knowledge.similarity_search(query, top_k)
        elif layer == 5:
            return await self.l5_evolution.query_experiences(query, top_k)
        return []

    def _rank_results(self, results: List[Dict], query: str) -> List[Dict]:
        """对结果进行排序"""
        return results


# 全局实例
memory_system = FiveLayerMemory()
