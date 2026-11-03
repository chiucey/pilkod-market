---
name: vector-memory-search
description: 神经网络向量记忆搜索系统。当用户需要解决MaxHermes上下文记忆堆栈溢出问题、实现长期记忆存取、进行语义相似度记忆检索、建立分层记忆架构或需要替代传统时间序列记忆时使用。触发场景包括：上下文溢出警告、记忆检索不准确、对话历史过长、需要遗忘机制、记忆压缩、跨会话上下文恢复。
---

# Vector Memory Search - 神经网络向量记忆系统

## 核心设计理念

将传统的线性上下文存储转变为**语义向量索引**的记忆系统，通过嵌入(Embedding)技术实现：
- **语义检索**: 按含义而非时间顺序存取记忆
- **动态容量**: 自适应记忆池，避免固定长度限制
- **智能遗忘**: 基于重要性评分自动清理低价值记忆
- **去重压缩**: 合并语义相似的记忆片段

## 三层记忆架构

```
┌─────────────────────────────────────────────────────────┐
│                    Long-Term Memory                      │
│  (向量数据库 - ChromaDB/SQLite)                          │
│  - 持久化存储高价值记忆片段                               │
│  - 支持语义相似度检索                                     │
│  - 自动去重和聚类                                        │
└─────────────────────────────────────────────────────────┘
                            ▲
                            │ 定期下沉
                            │
┌─────────────────────────────────────────────────────────┐
│                    Working Memory                        │
│  (滑动窗口 - 最近N条关键交互)                             │
│  - 当前会话核心上下文                                     │
│  - 高频访问记忆缓存                                      │
│  - 实时更新衰减                                          │
└─────────────────────────────────────────────────────────┘
                            ▲
                            │ 热点上升
                            │
┌─────────────────────────────────────────────────────────┐
│                    Immediate Memory                     │
│  (当前对话轮次)                                          │
│  - 最近1-3轮对话                                        │
│  - 临时变量和状态                                        │
│  - 快速读写                                             │
└─────────────────────────────────────────────────────────┘
```

## 核心工作流程

### 1. 记忆写入流程

```
用户输入 → 重要性评分 → 决策节点
                         │
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
        [高分]        [中分]        [低分]
           │             │             │
           ▼             ▼             ▼
      Long-Term     Working      丢弃/
      Memory        Memory        合并
```

**执行步骤**:

1. **输入编码**: 将当前输入转换为语义向量
2. **重要性评分**: 评估记忆价值（基于频率、时效、唯一性）
3. **相似度检测**: 与现有记忆比对去重
4. **分层存储**: 根据评分决定存储层级
5. **索引更新**: 更新向量数据库索引

### 2. 记忆检索流程

```
查询向量 → 向量数据库检索 → Top-K候选
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
              [高相似度]                   [中相似度]
                    │                           │
                    ▼                           ▼
              直接返回                   重排序过滤
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
                           上下文组装
                                  │
                                  ▼
                           返回给模型
```

**执行步骤**:

1. **查询编码**: 将当前对话上下文转为向量
2. **向量检索**: 在各层记忆库并行检索
3. **分数融合**: 加权合并多层检索结果
4. **时效调整**: 应用时间衰减因子
5. **上下文组装**: 格式化为模型可读形式

### 3. 记忆压缩与遗忘

**触发条件**:
- 记忆池达到容量上限
- 记忆碎片化程度过高
- 新旧记忆语义重叠

**遗忘策略**:
- **LIRS算法**: 基于引用局部性的遗忘
- **重要性阈值**: 低于阈值自动清理
- **聚类合并**: 相似记忆合并保留核心

## 关键技术实现

### 向量存储方案

```python
# 推荐使用轻量级向量库
class VectorMemoryStore:
    """
    支持多种后端:
    - ChromaDB: 生产级向量数据库
    - FAISS: Facebook高性能向量检索
    - SQLite + numpy: 嵌入式方案
    """

    def __init__(self, embedding_model="text-embedding-3-small"):
        self.embedding_model = embedding_model
        self.client = None  # 延迟初始化

    async def add_memory(self, content, metadata=None):
        """添加记忆片段"""
        vector = await self.encode(content)
        memory_id = generate_id(content)

        # 存储向量 + 元数据
        self.client.add(
            ids=[memory_id],
            embeddings=[vector],
            documents=[content],
            metadatas=[metadata or {}]
        )

        return memory_id

    async def search(self, query, top_k=5, threshold=0.7):
        """语义检索"""
        query_vector = await self.encode(query)

        results = self.client.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )

        # 过滤低相似度结果
        filtered = [
            r for r in zip(results['ids'], results['distances'], results['documents'])
            if 1 - r[1] >= threshold  # 余弦距离转相似度
        ]

        return filtered

    async def deduplicate(self, content):
        """去重检测"""
        results = await self.search(content, top_k=3, threshold=0.85)

        if results:
            return {"is_duplicate": True, "similar_id": results[0][0]}
        return {"is_duplicate": False}
```

### 重要性评分模型

```python
class ImportanceScorer:
    """多因子重要性评分"""

    async def score(self, memory_content, session_context):
        factors = {
            "frequency": self.calc_frequency(memory_content),      # 出现频率
            "recency": self.calc_recency(memory_content),         # 时效性
            "uniqueness": self.calc_uniqueness(memory_content),  # 独特性
            "task_relevance": self.calc_relevance(memory_content, session_context),  # 任务相关性
            "user_emphasis": self.calc_emphasis(memory_content)  # 用户强调程度
        }

        # 加权求和
        weights = {"frequency": 0.1, "recency": 0.2, "uniqueness": 0.2,
                   "task_relevance": 0.3, "user_emphasis": 0.2}

        score = sum(factors[k] * weights[k] for k in weights)

        return {
            "total_score": score,
            "factors": factors,
            "tier": self.get_tier(score)  # long-term/working/immediate
        }

    def get_tier(self, score):
        if score >= 0.7: return "long-term"
        if score >= 0.4: return "working"
        return "immediate"
```

### 会话上下文整合

```python
class MaxHermesIntegration:
    """与MaxHermes记忆系统整合"""

    def __init__(self, vector_store, importance_scorer):
        self.store = vector_store
        self.scorer = importance_scorer
        self.current_session = []

    async def process_turn(self, user_input, agent_response, session_state):
        """处理每个对话轮次"""

        # 1. 评估当前交互重要性
        combined_content = f"用户: {user_input}\n助手: {agent_response}"
        score_result = await self.scorer.score(combined_content, session_state)

        # 2. 决策存储层级
        tier = score_result["tier"]

        if tier == "long-term":
            await self.store.add_memory(
                content=combined_content,
                metadata={
                    "score": score_result["total_score"],
                    "timestamp": now(),
                    "session_id": session_state.get("session_id")
                }
            )
        elif tier == "working":
            self.current_session.append({
                "content": combined_content,
                "score": score_result["total_score"],
                "turn": session_state.get("turn", 0)
            })
            self.enforce_working_limit()

        # 3. 定期下沉热点记忆到长期存储
        if self.should_promote_to_longterm():
            await self.promote_hot_memories()

        return {"tier": tier, "score": score_result["total_score"]}

    async def retrieve_context(self, current_query, session_state):
        """检索相关上下文"""

        # 1. 即时记忆直接返回
        immediate = self.current_session[-3:]  # 最近3轮

        # 2. 长期记忆向量检索
        longterm_results = await self.store.search(
            query=current_query,
            top_k=5,
            threshold=0.75
        )

        # 3. 构建上下文提示
        context_parts = []

        # 按时间/相关性排序
        if longterm_results:
            context_parts.append("【相关记忆】")
            for _, _, doc in longterm_results:
                context_parts.append(doc)

        if immediate:
            context_parts.append("【最近对话】")
            for m in immediate:
                context_parts.append(m["content"])

        return "\n\n".join(context_parts)
```

## 使用触发器

### 自动触发场景

| 触发条件 | 系统行为 |
|---------|---------|
| 上下文token超过阈值 | 激活向量压缩 |
| 对话超过20轮 | 启用长期记忆归档 |
| 检测到重复模式 | 触发去重合并 |
| 记忆库接近容量 | 启动遗忘机制 |
| 跨会话恢复 | 检索历史相关记忆 |

### 手动触发指令

- `/memory search <query>` - 检索特定记忆
- `/memory stats` - 查看记忆统计
- `/memory clear` - 清理低价值记忆
- `/memory export` - 导出记忆库
- `/memory dump` - 查看当前记忆池内容

## 性能配置

```yaml
vector_memory:
  # 向量维度
  embedding_dim: 1536  # OpenAI text-embedding-3-small

  # 存储容量
  longterm_capacity: 10000
  working_capacity: 50  # 条目数
  immediate_capacity: 3  # 轮次数

  # 检索参数
  default_top_k: 5
  similarity_threshold: 0.75

  # 自动管理
  auto_forget: true
  deduplication_threshold: 0.85
  promotion_interval: 10  # 轮次

  # 评分权重
  scoring:
    frequency: 0.1
    recency: 0.2
    uniqueness: 0.2
    task_relevance: 0.3
    user_emphasis: 0.2
```

## 集成指南

### 替换MaxHermes原有记忆

```python
# 在MaxHermes初始化时替换
from vector_memory import VectorMemoryStore, MaxHermesIntegration

# 初始化向量记忆系统
vector_store = VectorMemoryStore(
    embedding_model="text-embedding-3-small",
    db_path="./memory_store"
)

scorer = ImportanceScorer()
memory_integration = MaxHermesIntegration(vector_store, scorer)

# 在对话循环中使用
async def chat_loop():
    while True:
        user_input = await get_user_input()

        # 检索相关上下文
        context = await memory_integration.retrieve_context(
            user_input,
            session_state
        )

        # 构建增强提示
        enhanced_prompt = f"{context}\n\n当前: {user_input}"

        # 生成回复
        response = await model.generate(enhanced_prompt)

        # 处理记忆
        await memory_integration.process_turn(
            user_input,
            response,
            session_state
        )

        session_state["turn"] += 1
```

## 参考资料

- `references/embedding_models.md` - 向量模型选择指南
- `references/memory_tiering.md` - 分层架构详解
- `references/integration_guide.md` - MaxHermes集成指南
- `scripts/init_vector_store.py` - 向量存储初始化脚本

## 输出格式

执行记忆检索时，输出格式如下：

```
【记忆检索结果】

📚 相关长期记忆 (3条):
   ├─ [2024-01-15] 用户偏好Python开发 (相似度: 0.92)
   ├─ [2024-01-10] 项目上下文: 电商平台重构 (相似度: 0.88)
   └─ [2024-01-08] 技术栈: FastAPI + PostgreSQL (相似度: 0.85)

💭 当前会话 (最近3轮):
   ├─ 轮次12: 讨论API性能优化方案
   ├─ 轮次11: 用户询问缓存策略
   └─ 轮次10: 分析现有架构瓶颈

💾 记忆统计:
   ├─ 长期记忆: 1,247 条
   ├─ 工作记忆: 23 条
   └─ 置信度: 高
```
