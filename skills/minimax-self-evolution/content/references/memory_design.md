# 五层记忆体系统设计说明

## 1. 设计理念

五层记忆体系统借鉴人类记忆的层次结构，将信息按照访问频率、重要性、持久性分为五个层级，实现高效的信息存储和检索。

### 1.1 层级对比

| 层级 | 类比 | 访问速度 | 容量 | 持久性 | 典型用途 |
|------|------|---------|------|--------|----------|
| L1 | 短期记忆 | 微秒级 | 100 条 | 会话 | 当前对话上下文 |
| L2 | 工作记忆 | 微秒级 | 50 项 | 任务 | 任务执行状态 |
| L3 | 项目记忆 | 毫秒级 | 20 项目 | 永久 | 项目整体上下文 |
| L4 | 知识库 | 毫秒级 | 无限制 | 永久 | 技能和模式定义 |
| L5 | 长期记忆 | 毫秒级 | 无限制 | 永久 | 经验和教训 |

## 2. 各层详细设计

### 2.1 L1 会话记忆

**设计目标**：极速访问，支持高频率读写

**数据结构**：
```python
L1SessionMemory = {
    'type': 'OrderedDict[str, MemoryEntry]',
    'max_size': 100,
    'eviction': 'LRU (Least Recently Used)'
}

MemoryEntry = {
    'key': str,           # 记忆键
    'value': Any,          # 记忆值
    'timestamp': float,    # 创建时间
    'access_count': int   # 访问次数
}
```

**关键特性**：
- LRU 淘汰策略
- 访问计数统计
- O(1) 读写复杂度

**典型存储内容**：
- 当前对话的用户输入
- 最近生成的响应
- 临时计算结果
- 意图识别结果

### 2.2 L2 任务记忆

**设计目标**：维护任务执行状态，支持中断恢复

**数据结构**：
```python
L2TaskMemory = {
    'current_task': Task | None,
    'subtasks': List[Subtask],
    'progress': float,     # 0.0 - 1.0
    'checkpoint': Checkpoint | None
}

Task = {
    'id': str,
    'description': str,
    'subtasks': List[Subtask],
    'created_at': float
}

Subtask = {
    'id': str,
    'action': str,
    'status': 'pending' | 'running' | 'completed' | 'failed',
    'result': Any,
    'error': str | None
}

Checkpoint = {
    'id': str,
    'task': Task,
    'subtasks': List[Subtask],
    'progress': float,
    'created_at': float
}
```

**关键特性**：
- 原子性检查点创建
- 进度自动计算
- 任务历史追踪

### 2.3 L3 项目记忆

**设计目标**：跨会话持久化项目上下文

**存储策略**：
- JSON 文件持久化
- 自动保存机制
- 语义搜索支持

**数据结构**：
```python
L3ProjectMemory = {
    'storage_path': str,
    'store': Dict[str, ProjectEntry]
}

ProjectEntry = {
    'value': Any,
    'metadata': Dict,
    'updated_at': float
}
```

**典型存储内容**：
- 项目目录结构
- 用户项目配置
- 跨会话工作状态
- 项目相关文件索引

### 2.4 L4 知识库

**设计目标**：结构化知识存储，支持语义检索

**索引策略**：
- 向量化存储（预留接口）
- 关键词索引
- 内容哈希去重

**数据结构**：
```python
L4KnowledgeBase = {
    'storage_path': str,
    'entries': List[KnowledgeEntry]
}

KnowledgeEntry = {
    'content': Any,
    'content_hash': str,
    'metadata': Dict,
    'created_at': float,
    'access_count': int
}
```

**典型存储内容**：
- 技能定义和描述
- 最佳实践指南
- 代码模式库
- API 使用示例

### 2.5 L5 进化记忆

**设计目标**：永久存储经验和教训，支持模式提取

**分类存储**：
```python
L5EvolutionMemory = {
    'experiences': List[Experience],      # 原始经验
    'preferences': Dict[str, Preference], # 用户偏好
    'success_patterns': List[Pattern],     # 成功模式
    'failure_lessons': List[Lesson]       # 失败教训
}

Experience = {
    'content': Any,
    'metadata': {
        'success': bool,
        'task_category': str,
        'timestamp': float
    }
}

Preference = {
    'type': str,           # 偏好类型
    'value': Any,          # 偏好值
    'confidence': float,    # 置信度
    'learned_at': float
}

Pattern = {
    'task_type': str,
    'approach_structure': str,
    'key_steps': List[str],
    'success_factors': List[str]
}

Lesson = {
    'task': str,
    'cause': str,          # 失败原因
    'lesson': str,         # 教训总结
    'recovery': str        # 恢复建议
}
```

## 3. 跨层检索机制

### 3.1 检索流程

```
用户查询
    │
    ▼
┌─────────────────────────────────────┐
│     层级权重计算                     │
│  L1: 权重 1.0 (即时)                │
│  L2: 权重 0.9                       │
│  L3: 权重 0.7                       │
│  L4: 权重 0.6                       │
│  L5: 权重 0.5                       │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│     并行检索各层                     │
│  (使用 asyncio.gather)              │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│     结果合并与排序                   │
│  score = base_score * layer_weight │
└─────────────────────────────────────┘
    │
    ▼
  返回 Top-K 结果
```

### 3.2 相关性计算

```python
def calculate_relevance(entry: Dict, query: str) -> float:
    # 基础相关性
    base = 0.0

    # 内容匹配
    if query in str(entry.get('content', '')):
        base += 0.5

    # 元数据匹配
    if query in str(entry.get('metadata', {})):
        base += 0.3

    # 访问频率加成
    access_count = entry.get('access_count', 0)
    base += min(access_count * 0.01, 0.2)

    return base
```

## 4. 存储策略

### 4.1 持久化策略

| 层级 | 持久化方式 | 保存时机 | 加载时机 |
|------|-----------|---------|---------|
| L1 | 内存 | - | - |
| L2 | 内存 | 检查点时 | 恢复时 |
| L3 | JSON 文件 | 修改后 | 初始化时 |
| L4 | JSON 文件 | 添加时 | 初始化时 |
| L5 | JSON 文件 | 记录时 | 初始化时 |

### 4.2 清理策略

```python
class MemoryCleanup:
    def cleanup_l1(self):
        # LRU 清理，保持 100 条
        while len(self.store) > self.max_size:
            self.store.popitem(last=False)

    def cleanup_l3(self, max_projects: int = 20):
        # 清理旧项目
        sorted_projects = sorted(
            self.store.items(),
            key=lambda x: x[1].get('updated_at', 0)
        )
        if len(sorted_projects) > max_projects:
            for key, _ in sorted_projects[:-max_projects]:
                del self.store[key]

    def cleanup_l5(self, max_experiences: int = 1000):
        # 清理过期经验
        self.experiences = self.experiences[-max_experiences:]
```

## 5. 扩展接口

### 5.1 自定义存储后端

```python
class BaseMemoryLayer:
    """记忆层基类"""
    async def store(self, key: str, value: Any, metadata: Dict = None):
        raise NotImplementedError

    async def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        raise NotImplementedError


# Redis 后端示例
class RedisMemoryLayer(BaseMemoryLayer):
    def __init__(self, redis_client):
        self.client = redis_client

    async def store(self, key, value, metadata=None):
        await self.client.set(key, json.dumps({'value': value, 'metadata': metadata}))

    async def retrieve(self, query, top_k=5):
        # Redis 搜索实现
        pass
```

### 5.2 向量化检索扩展

```python
class VectorMemoryLayer:
    """向量记忆层"""

    def __init__(self, embedding_model):
        self.embedding = embedding_model
        self.vector_store = None  # Pinecone/Milvus

    async def store(self, key, value, metadata=None):
        # 生成向量
        vector = await self.embedding.embed(value)

        # 存储到向量数据库
        await self.vector_store.upsert(key, vector, metadata)

    async def retrieve(self, query, top_k=5):
        # 生成查询向量
        query_vector = await self.embedding.embed(query)

        # 相似度搜索
        results = await self.vector_store.search(query_vector, top_k)

        return results
```
