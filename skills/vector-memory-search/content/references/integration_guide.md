# MaxHermes 集成指南

## 概述

本指南说明如何将向量记忆系统集成到 MaxHermes 中，替换或增强原有的上下文记忆机制。

## 集成架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         MaxHermes Core                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │   Session   │  │    LLM      │  │  Tools      │               │
│  │   Manager   │  │  Generator  │  │  Executor   │               │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │
│         │                │                │                      │
│         └────────────────┼────────────────┘                      │
│                          │                                       │
│                   ┌──────▼──────┐                                │
│                   │   Context   │                                │
│                   │   Builder   │                                │
│                   └──────┬──────┘                                │
└──────────────────────────┼───────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   Vector    │ │  Semantic   │ │   Memory    │
    │   Memory    │ │  Retrieval  │ │  Manager    │
    │   System    │ │   Engine    │ │             │
    └─────────────┘ └─────────────┘ └─────────────┘
```

## 集成方式

### 方式一: 完全替换

用向量记忆系统完全替换 MaxHermes 原有的线性上下文存储。

```python
# maxhermes_integration.py

from vector_memory import VectorMemoryStore, TieredMemorySystem

class MaxHermesVectorIntegration:
    """
    MaxHermes 向量记忆集成
    替换原有的线性上下文存储
    """

    def __init__(self, max_context_length: int = 128000):
        # 初始化向量记忆系统
        self.memory = TieredMemorySystem({
            "immediate_capacity": 3,
            "working_capacity": 50,
            "longterm_capacity": 10000,
            "embedding_model": "text-embedding-3-small"
        })

        # 上下文长度限制
        self.max_context_length = max_context_length

    async def build_context(self, current_input: str) -> str:
        """
        构建增强的上下文提示
        """
        # 1. 检索相关记忆
        relevant_memories = await self.memory.retrieve(current_input, top_k=10)

        # 2. 计算可用空间
        input_length = len(current_input) * 4  # rough token estimate
        available_space = self.max_context_length - input_length - 1000  # buffer

        # 3. 按优先级组装上下文
        context_parts = []

        # 相关记忆 (高优先级)
        if relevant_memories["longterm"]:
            context_parts.append(f"【相关背景知识】\n{relevant_memories['longterm']}")

        if relevant_memories["working"]:
            context_parts.append(f"【工作上下文】\n{relevant_memories['working']}")

        # 即时会话
        if relevant_memories["immediate"]:
            context_parts.append(f"【当前对话】\n{relevant_memories['immediate']}")

        # 4. 截断以适应上下文限制
        full_context = "\n\n".join(context_parts)
        if len(full_context) * 4 > available_space:
            # 按比例截断
            context_parts = self._truncate_to_fit(context_parts, available_space)
            full_context = "\n\n".join(context_parts)

        return full_context

    async def process_response(self, user_input: str, assistant_response: str):
        """
        处理回复并存储记忆
        """
        await self.memory.store(
            user_input,
            assistant_response,
            session_state={"session_id": self.session_id}
        )
```

### 方式二: 增强模式

保留原有上下文机制，添加向量记忆作为增强层。

```python
class MaxHermesEnhancedIntegration:
    """
    MaxHermes 增强模式集成
    在原有上下文基础上添加向量检索增强
    """

    def __init__(self, max_hermes_instance):
        # 保留原有实例
        self.max_hermes = max_hermes_instance

        # 添加向量记忆层
        self.vector_memory = VectorMemoryStore()
        self.retrieval_threshold = 0.75

    async def chat(self, user_input: str) -> str:
        """
        增强的对话处理
        """
        # 1. 原有上下文构建
        original_context = await self.max_hermes.build_context(user_input)

        # 2. 向量检索增强
        enhanced_context = await self._enhance_with_vectors(original_context, user_input)

        # 3. 生成回复
        response = await self.max_hermes.generate(enhanced_context, user_input)

        # 4. 存储到向量记忆
        await self.vector_memory.add(
            content=f"用户: {user_input}\n助手: {response}",
            metadata={"session_id": self.max_hermes.session_id}
        )

        return response

    async def _enhance_with_vectors(self, original_context: str, query: str) -> str:
        """
        使用向量检索增强上下文
        """
        # 检索相关记忆
        results = await self.vector_memory.search(
            query=query,
            top_k=5,
            threshold=self.retrieval_threshold
        )

        if not results:
            return original_context

        # 构建增强提示
        memory_section = "\n".join([
            f"- {content} (相关度: {score:.2f})"
            for _, score, content in results
        ])

        enhanced = f"""{original_context}

【检索到的相关记忆】
{memory_section}

请结合上述背景信息回复用户问题。
"""

        return enhanced
```

## 环境配置

### 1. 安装依赖

```bash
# 核心依赖
pip install chromadb openai numpy scikit-learn

# 可选依赖 (根据后端选择)
pip install faiss-cpu  # CPU版本
pip install faiss-gpu  # GPU版本
pip install qdrant-client  # Qdrant客户端
```

### 2. 环境变量配置

```bash
# .env 文件
OPENAI_API_KEY=sk-xxxxx
VECTOR_STORE_BACKEND=chroma
VECTOR_STORE_PATH=./vector_memory_data
```

### 3. 初始化脚本

```python
# init_integration.py

import asyncio
import sys
sys.path.insert(0, "/path/to/vector-memory-search")

from scripts.init_vector_store import VectorStoreInitializer
from vector_memory import TieredMemorySystem

async def setup_maxhermes_integration():
    """
    设置 MaxHermes 向量记忆集成
    """
    print("=" * 60)
    print("MaxHermes Vector Memory Integration Setup")
    print("=" * 60)
    print()

    # 1. 初始化向量存储
    print("[1/3] 初始化向量存储...")
    initializer = VectorStoreInitializer()
    success = await initializer.run_initialization("chroma")

    if not success:
        print("✗ 向量存储初始化失败")
        return False

    print()

    # 2. 测试连接
    print("[2/3] 测试向量存储连接...")
    try:
        from vector_memory import VectorMemoryStore
        store = VectorMemoryStore()
        test_result = await store.health_check()
        if test_result:
            print("✓ 向量存储连接正常")
        else:
            print("✗ 向量存储连接失败")
            return False
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False

    print()

    # 3. 创建示例记忆
    print("[3/3] 创建示例记忆...")
    try:
        memory = TieredMemorySystem()
        await memory.store(
            "用户询问项目架构",
            "项目采用微服务架构，包含用户服务、订单服务、支付服务等",
            {"session_id": "init", "topic": "architecture"}
        )
        print("✓ 示例记忆创建成功")
    except Exception as e:
        print(f"⚠ 示例记忆创建失败 (不影响使用): {e}")

    print()
    print("=" * 60)
    print("✓ 设置完成!")
    print("=" * 60)
    print()
    print("下一步:")
    print("  1. 在 MaxHermes 中导入:")
    print("     from maxhermes_integration import MaxHermesVectorIntegration")
    print()
    print("  2. 初始化集成:")
    print("     integration = MaxHermesVectorIntegration()")
    print()
    print("  3. 在对话中使用:")
    print("     context = await integration.build_context(user_input)")
    print()

    return True

if __name__ == "__main__":
    asyncio.run(setup_maxhermes_integration())
```

## 配置示例

### 基础配置

```yaml
# config.yaml
maxhermes:
  max_context_length: 128000
  session_timeout: 3600

vector_memory:
  enabled: true
  backend: chroma
  embedding_model: text-embedding-3-small
  persist_path: ./vector_memory_data

  memory_tiers:
    immediate:
      max_turns: 3
    working:
      max_size: 50
      decay_factor: 0.95
    longterm:
      max_capacity: 10000
      promotion_threshold: 0.7

  retrieval:
    default_top_k: 5
    similarity_threshold: 0.75
    enable_reranking: true
```

### 高级配置

```yaml
# config_advanced.yaml
maxhermes:
  max_context_length: 128000

vector_memory:
  enabled: true
  backend: qdrant
  embedding_model: text-embedding-3-large
  qdrant:
    host: localhost
    port: 6333
    collection: maxhermes_memory

  memory_tiers:
    immediate:
      max_turns: 5
      include_system: true
    working:
      max_size: 100
      decay_factor: 0.9
      enable_hot_promotion: true
    longterm:
      max_capacity: 100000
      promotion_threshold: 0.6
      enable_compression: true

  retrieval:
    default_top_k: 10
    similarity_threshold: 0.7
    enable_reranking: true
    reranker_model: cross-encoder/ms-marco-MiniLM-L-6v2
    hybrid_search: true  # 混合关键词和向量搜索

  management:
    auto_forget: true
    forgetting_threshold: 0.2
    deduplication: true
    deduplication_threshold: 0.9
    cleanup_interval_hours: 12
```

## 迁移指南

### 从线性上下文迁移

如果 MaxHermes 使用的是线性上下文存储，按以下步骤迁移：

```python
# 1. 导出原有记忆 (可选)
def export_existing_memories(linear_context: list) -> list[dict]:
    """
    将线性上下文转换为向量记忆格式
    """
    memories = []
    for item in linear_context:
        memories.append({
            "content": item["content"],
            "metadata": {
                "timestamp": item.get("timestamp"),
                "source": "migration"
            }
        })
    return memories

# 2. 批量导入
async def migrate_memories(memories: list[dict]):
    """
    批量迁移记忆到向量存储
    """
    from vector_memory import VectorMemoryStore

    store = VectorMemoryStore()

    for memory in memories:
        await store.add(
            content=memory["content"],
            metadata=memory["metadata"]
        )

    print(f"✓ 已迁移 {len(memories)} 条记忆")

# 3. 验证迁移
async def verify_migration():
    """
    验证迁移完整性
    """
    from vector_memory import VectorMemoryStore

    store = VectorMemoryStore()
    stats = await store.get_stats()

    print("迁移统计:")
    print(f"  - 总记忆数: {stats['total']}")
    print(f"  - 向量维度: {stats['dimension']}")
    print(f"  - 存储大小: {stats['storage_size_mb']:.2f} MB")
```

## 监控与调试

### 1. 记忆统计

```python
async def get_memory_stats():
    """
    获取记忆系统统计信息
    """
    from vector_memory import TieredMemorySystem

    memory = TieredMemorySystem()

    stats = {
        "immediate": len(memory.immediate.buffer),
        "working": len(memory.working.cache),
        "longterm": await memory.longterm.count()
    }

    return stats
```

### 2. 检索调试

```python
async def debug_retrieval(query: str):
    """
    调试检索过程
    """
    from vector_memory import TieredMemorySystem

    memory = TieredMemorySystem()

    # 逐层检索
    results = await memory.retrieve(query, top_k=5)

    print("检索调试信息:")
    print()

    for tier_name, tier_results in results.items():
        print(f"【{tier_name.upper()}】")
        if tier_results:
            for i, item in enumerate(tier_results[:3], 1):
                print(f"  {i}. {item[:100]}...")
        else:
            print("  (无结果)")
        print()
```

### 3. 性能监控

```python
import time
from functools import wraps

def monitor_performance(func):
    """
    性能监控装饰器
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start

        print(f"[性能] {func.__name__}: {duration*1000:.2f}ms")

        return result
    return wrapper

# 使用示例
@monitor_performance
async def retrieve_with_monitoring(query: str):
    # 检索逻辑
    pass
```

## 常见问题

### Q1: 向量检索返回空结果

**原因**: 记忆库为空或相似度阈值过高

**解决方案**:
```python
# 降低阈值
results = await memory.search(query, threshold=0.5)

# 或使用混合搜索
results = await memory.hybrid_search(query)
```

### Q2: 上下文超出限制

**原因**: 检索到的记忆过多或单条记忆过长

**解决方案**:
```python
# 限制检索数量
results = await memory.search(query, top_k=3)

# 截断长记忆
truncated = truncate_content(content, max_length=2000)
```

### Q3: 存储性能下降

**原因**: 索引未优化或数据量过大

**解决方案**:
```python
# 重建索引
await vector_store.rebuild_index()

# 启用量化
await vector_store.enable_quantization(precision="int8")
```

## 联系与支持

如有问题，请提交 Issue 到项目仓库。
