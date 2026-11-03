# 分层记忆架构详解

## 架构概述

三层记忆架构是解决上下文长度限制和记忆检索效率的核心设计。通过将记忆按重要性和访问频率分层，实现：

- **即时记忆(Immediate)**: 毫秒级访问延迟
- **工作记忆(Working)**: 秒级检索能力
- **长期记忆(Long-Term)**: 高容量语义检索

## 层级详细设计

### 第1层: 即时记忆 (Immediate Memory)

**设计目标**: 存储当前对话最近N轮交互，保证上下文连贯性

```
┌────────────────────────────────────────┐
│           Immediate Memory             │
│  ┌─────────────────────────────────┐   │
│  │  Turn N: 用户输入 + 助手回复     │   │
│  ├─────────────────────────────────┤   │
│  │  Turn N-1: 用户输入 + 助手回复    │   │
│  ├─────────────────────────────────┤   │
│  │  Turn N-2: 用户输入 + 助手回复    │   │
│  └─────────────────────────────────┘   │
│                                        │
│  容量: 3轮对话                         │
│  访问: 直接内存访问                    │
│  TTL: 当前会话结束                    │
└────────────────────────────────────────┘
```

**实现代码**:

```python
class ImmediateMemory:
    def __init__(self, max_turns: int = 3):
        self.max_turns = max_turns
        self.buffer: list[Turn] = []

    def add_turn(self, user_input: str, assistant_response: str):
        """添加一轮对话"""
        self.buffer.append(Turn(
            user=user_input,
            assistant=assistant_response,
            timestamp=datetime.now()
        ))

        # 保持固定容量
        if len(self.buffer) > self.max_turns:
            self.buffer.pop(0)

    def get_context(self) -> str:
        """获取格式化上下文"""
        return "\n".join([
            f"用户: {t.user}\n助手: {t.assistant}"
            for t in self.buffer
        ])
```

**适用场景**:

- 维持当前话题连贯性
- 临时变量和状态保持
- 快速状态恢复

### 第2层: 工作记忆 (Working Memory)

**设计目标**: 中期记忆存储，包含当前任务相关的重要交互

```
┌────────────────────────────────────────┐
│           Working Memory               │
│                                        │
│  ┌─────────┐  ┌─────────┐  ┌───────┐ │
│  │ Memory  │  │ Memory  │  │Memory │ │
│  │ Block 1 │  │ Block 2 │  │Block 3│ │
│  │ Score:  │  │ Score:  │  │Score: │ │
│  │ 0.82    │  │ 0.75    │  │0.68   │ │
│  └─────────┘  └─────────┘  └───────┘ │
│       ↑            ↑            ↑     │
│       └────────────┼────────────┘     │
│                    │                   │
│              LRU Cache                 │
│              (按访问频率排序)            │
│                                        │
│  容量: 50条                             │
│  访问: 内存 + 索引                      │
│  TTL: 滑动窗口衰减                     │
└────────────────────────────────────────┘
```

**实现代码**:

```python
from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class MemoryBlock:
    id: str
    content: str
    importance_score: float
    created_at: float
    last_accessed: float
    access_count: int = 0

class WorkingMemory:
    def __init__(self, max_size: int = 50, decay_factor: float = 0.95):
        self.max_size = max_size
        self.decay_factor = decay_factor
        self.cache: OrderedDict[str, MemoryBlock] = OrderedDict()

    def add(self, block: MemoryBlock):
        """添加记忆块"""
        # 检查容量
        if len(self.cache) >= self.max_size:
            self._evict_lowest()

        self.cache[block.id] = block
        self._touch(block.id)

    def get(self, block_id: str) -> Optional[MemoryBlock]:
        """获取记忆块"""
        if block_id in self.cache:
            self._touch(block_id)
            return self.cache[block_id]
        return None

    def _touch(self, block_id: str):
        """更新访问时间和频率"""
        block = self.cache[block_id]
        block.last_accessed = time.time()
        block.access_count += 1

        # 移动到末尾(最新)
        self.cache.move_to_end(block_id)

    def _evict_lowest(self):
        """驱逐最低分记忆"""
        if not self.cache:
            return

        # 计算有效分数 (重要性 × 衰减因子)
        def effective_score(block: MemoryBlock) -> float:
            age_hours = (time.time() - block.created_at) / 3600
            decay = self.decay_factor ** age_hours
            return block.importance_score * decay

        # 找到最低分
        lowest_id = min(
            self.cache.keys(),
            key=lambda k: effective_score(self.cache[k])
        )

        del self.cache[lowest_id]

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[MemoryBlock]:
        """在工作记忆内搜索"""
        from sklearn.metrics.pairwise import cosine_similarity

        results = []
        for block_id, block in self.cache.items():
            # 简化的相似度计算 (需要预先计算的embedding)
            if hasattr(block, 'embedding'):
                sim = cosine_similarity([query_embedding], [block.embedding])[0][0]
                results.append((block, sim))

        # 返回top_k
        return [r[0] for r in sorted(results, key=lambda x: x[1], reverse=True)[:top_k]]
```

**晋升条件**: 连续N次被访问且分数高于阈值

```python
def should_promote_to_longterm(self, block: MemoryBlock) -> bool:
    """判断是否应晋升到长期记忆"""
    return (
        block.access_count >= 5 and
        block.importance_score >= 0.7
    )
```

### 第3层: 长期记忆 (Long-Term Memory)

**设计目标**: 持久化大容量语义存储，支持复杂查询

```
┌────────────────────────────────────────────────────────────────┐
│                     Long-Term Memory                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Vector Database                        │  │
│  │                                                           │  │
│  │   ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐            │  │
│  │   │ V1  │  │ V2  │  │ V3  │  │ V4  │  │ V5  │  ...      │  │
│  │   │0.92 │  │0.88 │  │0.85 │  │0.81 │  │0.78 │            │  │
│  │   └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘  └──┬──┘            │  │
│  │      │        │        │        │        │               │  │
│  │      └────────┼────────┼────────┼────────┘               │  │
│  │               │        │        │                         │  │
│  │         Similarity Index (HNSW/IVF)                       │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Metadata Store                         │  │
│  │                                                           │  │
│  │  • 重要性评分    • 时间戳         • 访问次数             │  │
│  │  • 主题标签      • 来源会话       • 关联记忆ID           │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  容量: 无限制 (受磁盘限制)                                       │
│  访问: 毫秒级向量检索                                            │
│  TTL: 永久 (除非手动删除)                                        │
└────────────────────────────────────────────────────────────────┘
```

**向量数据库选型**:

| 数据库 | 优势 | 适用场景 | 部署方式 |
|--------|------|---------|---------|
| ChromaDB | 轻量、易用 | 原型/小规模 | 嵌入式 |
| FAISS | 高性能 | 大规模检索 | 独立服务 |
| Qdrant | 云原生 | 云部署 | Docker/K8s |
| Milvus | 企业级 | 超大规模 | 分布式集群 |

## 层级间流转机制

### 晋升流程 (Promotion)

```
工作记忆 ──→ 长期记忆
    │
    ├── 触发条件:
    │   • 访问频率 ≥ 5次
    │   • 重要性分数 ≥ 0.7
    │   • 存在时间 ≥ 1小时
    │
    └── 执行过程:
        1. 计算完整向量表示
        2. 生成元数据标签
        3. 写入向量数据库
        4. 更新工作记忆缓存
        5. 设置晋升标记
```

### 下沉流程 (Demotion)

```
长期记忆 ──→ 工作记忆
    │
    ├── 触发条件:
    │   • 热点访问模式
    │   • 与当前任务高度相关
    │   • 周期性预加载
    │
    └── 执行过程:
        1. 查询向量相似度
        2. 获取相关记忆
        3. 缓存到工作记忆
        4. 更新访问统计
```

### 遗忘流程 (Forgetting)

```
长期记忆/工作记忆 ──→ 删除
    │
    ├── 触发条件:
    │   • 容量超限
    │   • 重要性 < 阈值
    │   • 时间衰减至低分
    │   • 用户请求清理
    │
    └── 执行过程:
        1. 计算遗忘分数
        2. 识别低价值记忆
        3. 软删除(可恢复)或硬删除
        4. 更新索引
        5. 记录遗忘日志
```

## 遗忘算法

### LIRS (Low Inter-reference Recency Set)

```python
class LIRSForgetting:
    """
    基于LIRS算法的记忆遗忘策略
    保留最近被引用和频繁被引用的记忆
    """

    def __init__(self, max_memory_blocks: int):
        self.max_blocks = max_memory_blocks
        self.recents: OrderedDict[str, MemoryBlock] = OrderedDict()
        self.residents: OrderedDict[str, MemoryBlock] = OrderedDict()

    def access(self, block_id: str):
        """访问记忆块"""
        # LIRS特有的栈距离计算
        if block_id in self.residents:
            # 已在常驻集，移到末尾
            self.residents.move_to_end(block_id)
        elif block_id in self.recents:
            # 从最近集移到常驻集
            block = self.recents.pop(block_id)
            self.residents[block_id] = block
        else:
            # 新记忆添加到最近集
            pass

        self._prune()

    def _prune(self):
        """剪枝以维持容量"""
        while len(self.residents) + len(self.recents) > self.max_blocks:
            if self.recents:
                # 驱逐最近集中最旧的
                self.recents.popitem(last=False)
            elif len(self.residents) > self.max_blocks * 0.5:
                # 驱逐部分常驻集
                self.residents.popitem(last=False)
```

### 基于重要性的遗忘

```python
class ImportanceBasedForgetting:
    """基于重要性分数的遗忘策略"""

    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold

    def should_forget(self, block: MemoryBlock) -> bool:
        """判断是否应遗忘"""
        # 时间衰减
        time_weight = self._time_decay(block)
        # 访问模式
        access_weight = self._access_pattern(block)
        # 综合分数
        effective_score = block.importance_score * time_weight * access_weight

        return effective_score < self.threshold

    def _time_decay(self, block: MemoryBlock) -> float:
        """时间衰减因子"""
        import math
        hours_since_access = (time.time() - block.last_accessed) / 3600
        # 指数衰减，半衰期24小时
        return math.exp(-0.029 * hours_since_access)

    def _access_pattern(self, block: MemoryBlock) -> float:
        """访问模式因子"""
        if block.access_count == 0:
            return 0.5  # 从未访问，降低权重
        # 访问频率的对数加成
        return min(1.0, 1.0 + 0.1 * math.log(block.access_count))
```

## 完整集成示例

```python
class TieredMemorySystem:
    """三层记忆系统"""

    def __init__(self, config: dict):
        self.immediate = ImmediateMemory(
            max_turns=config["immediate_capacity"]
        )
        self.working = WorkingMemory(
            max_size=config["working_capacity"]
        )
        self.longterm = VectorMemoryStore(
            embedding_model=config["embedding_model"]
        )
        self.scorer = ImportanceScorer()

    async def store(self, user_input: str, assistant_response: str, session_state: dict):
        """存储新记忆"""
        # 1. 即时记忆总是添加
        self.immediate.add_turn(user_input, assistant_response)

        # 2. 评估重要性
        combined = f"用户: {user_input}\n助手: {assistant_response}"
        score = await self.scorer.score(combined, session_state)

        # 3. 根据分数决定存储层级
        if score >= 0.7:
            # 长期记忆
            await self.longterm.add(combined, {
                "score": score,
                "session_id": session_state.get("session_id")
            })
        elif score >= 0.4:
            # 工作记忆
            block = MemoryBlock(
                id=generate_id(combined),
                content=combined,
                importance_score=score,
                created_at=time.time(),
                last_accessed=time.time()
            )
            self.working.add(block)

            # 检查是否应晋升
            if self.working.should_promote_to_longterm(block):
                await self._promote(block)

    async def retrieve(self, query: str, top_k: int = 5) -> str:
        """检索相关记忆"""
        results = []

        # 1. 即时记忆直接返回
        immediate_context = self.immediate.get_context()
        results.append(("immediate", immediate_context))

        # 2. 工作记忆向量检索
        working_results = self.working.search(query, top_k=3)
        results.append(("working", "\n".join([r.content for r in working_results])))

        # 3. 长期记忆向量检索
        longterm_results = await self.longterm.search(query, top_k=5)
        results.append(("longterm", "\n".join([r[2] for r in longterm_results])))

        # 4. 组装最终上下文
        return self._assemble_context(results)

    async def _promote(self, block: MemoryBlock):
        """将工作记忆晋升到长期记忆"""
        await self.longterm.add(block.content, {
            "score": block.importance_score,
            "promoted_from": "working_memory"
        })
        self.working.cache.pop(block.id, None)
```

## 配置参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `immediate_capacity` | 3 | 即时记忆轮数 |
| `working_capacity` | 50 | 工作记忆条目数 |
| `longterm_capacity` | 10000 | 长期记忆条目数上限 |
| `promotion_threshold` | 0.7 | 晋升到长期记忆的分数阈值 |
| `forgetting_threshold` | 0.3 | 遗忘分数阈值 |
| `decay_factor` | 0.95 | 工作记忆衰减因子 |
| `promotion_interval` | 10 | 晋升检查的轮次间隔 |
