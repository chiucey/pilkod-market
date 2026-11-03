# ASRANK 算法技术参考

## 算法原理

ASRANK（ASymmetric RANKing）是一种两阶段检索架构，结合了向量检索的速度和大语言模型的语义理解能力。

### 为什么需要两阶段？

1. **向量检索的局限性**
   - 优点：速度快、可扩展性好
   - 缺点：语义相似不等于相关性强

2. **LLM重排的优势**
   - 深层语义理解
   - 上下文推理能力
   - 可解释的相关性判断

## 核心技术细节

### 1. 文档分块策略

**固定窗口分块**
```python
chunk_size = 800  # 字符数
chunk_overlap = 150  # 重叠字符数
```

**智能分块**
- 在句子边界（。！？.!?）断开
- 保留段落完整性
- 处理代码块的特殊分隔

### 2. 向量化模型选择

| 模型 | 维度 | 语言 | 适用场景 |
|------|------|------|----------|
| bge-large-zh | 1024 | 中英 | 通用场景 |
| text-embedding-ada-002 | 1536 | 多语言 | OpenAI生态 |
| m3e-base | 768 | 中英 | 中文优化 |
| BAAI/bge-base-zh | 768 | 中文 | 高性能 |

### 3. 相似度计算

**余弦相似度**
```python
def cosine_similarity(a, b):
    dot_prod = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5
    return dot_prod / (norm_a * norm_b)
```

**内积（当向量已归一化时）**
```python
def inner_product(a, b):
    return sum(x * y for x, y in zip(a, b))
```

### 4. LLM重排提示工程

**关键要素**
1. 明确的评分标准
2. 具体的输出格式要求
3. 简洁的文档片段展示
4. 限制输入数量（建议50个）

**提示模板**
```markdown
你是一个专业的文档检索专家。请根据用户问题评估以下每个文档片段的相关性。

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
```

## 性能优化

### 1. 批量向量化
```python
# 批量处理提升效率
batch_embeddings = embed_model.encode(chunks, batch_size=32)
```

### 2. 向量索引
- 使用 FAISS 构建索引
- 支持百万级文档快速检索
- 近似最近邻（ANN）算法

### 3. 缓存策略
```python
# 缓存文档embedding
cache_key = hash(chunks)
if cache_key in embedding_cache:
    return embedding_cache[cache_key]
```

### 4. 异步处理
```python
import asyncio

async def async_retrieve(query, chunks):
    # 并行执行召回和重排
    recall_task = asyncio.create_task(vector_recall(query, chunks))
    rerank_task = asyncio.create_task(llm_rerank(query, candidates))

    candidates = await recall_task
    results = await rerank_task
    return results
```

## 与Agent集成

### 上下文窗口管理
```python
MAX_CONTEXT_TOKENS = 4000

def truncate_context(context: str, max_tokens: int = MAX_CONTEXT_TOKENS) -> str:
    # 按token截断
    tokens = context.split()
    if len(tokens) <= max_tokens:
        return context
    return ' '.join(tokens[:max_tokens])
```

### 多文档场景
```python
def multi_doc_retrieve(queries: List[str], documents: List[Dict]) -> Dict:
    """处理多文档场景"""
    all_results = []

    for doc in documents:
        retriever = ASRANKRetriever()
        retriever.index_document(doc['path'], doc['content'])
        results = retriever.retrieve(queries)
        all_results.extend(results['results'])

    # 合并去重后重排
    return merge_and_rerank(all_results)
```

## 评估指标

### 1. 召回率 (Recall@K)
```
Recall@K = (相关且被召回的文档数) / (所有相关文档数)
```

### 2. MRR (Mean Reciprocal Rank)
```
MRR = (1/N) * Σ(1/rank_i)
```

### 3. NDCG (Normalized Discounted Cumulative Gain)
```
NDCG@K = DCG@K / IDCG@K
```

## 常见问题

### Q: 如何处理长文档？
A: 使用递归分块 + 父子索引策略

### Q: 多语言文档如何处理？
A: 使用多语言embedding模型或按语言分别索引

### Q: 如何处理实时更新的文档？
A: 使用增量索引 + 版本控制

### Q: embedding模型如何选择？
A: 考虑：语言、维度、性能、成本
