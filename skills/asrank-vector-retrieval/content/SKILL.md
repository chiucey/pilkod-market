---
name: asrank-vector-retrieval
description: Vector retrieval recall skill. Use when users upload attachments and need to query attachment content. Implements ASRANK two-stage algorithm: Stage 1 uses Embedding model to quickly recall Top-50/100 candidate passages (coarse screening), Stage 2 uses large language model for refined reranking of candidate results (fine selection). Trigger scenarios include: users uploading files and asking questions, analyzing attachments, retrieving document information, Q&A based on uploaded files.
---

# ASRANK 向量检索召回技能

## 技能概述

本技能实现ASRANK两阶段检索架构，将向量检索与大模型重排相结合，为Agent执行提供精准的上下文召回能力。

## 触发条件

**必须触发当：**
- 用户上传附件/文件并询问相关内容
- 用户请求分析、总结或检索已上传文档的内容
- 用户问题涉及"根据附件"、"基于上传的文件"、"查看文档内容"等场景
- Agent需要从大量文档中检索相关信息

**不应触发当：**
- 用户仅进行闲聊或一般性问答
- 问题不涉及任何附件内容查询
- 用户明确表示不需要检索功能

## 两阶段检索流程

### 阶段一：向量召回（粗筛）

**目标：** 快速从文档库中召回相关候选段落

**执行步骤：**

1. **文档解析**
   - 解析用户上传的附件（PDF、Word、TXT、Markdown等）
   - 将文档分割为语义完整的段落（chunk）
   - 建议chunk大小：500-1000字符，重叠100-200字符

2. **向量化处理**
   - 使用Embedding模型将每个chunk转换为向量表示
   - 推荐模型：text-embedding-ada-002、bge-large、m3e等

3. **向量相似度检索**
   - 将用户问题同样转换为向量
   - 使用余弦相似度或内积计算相关性
   - 召回Top-50或Top-100个候选chunk

**代码框架：**
```python
def vector_recall(query: str, chunks: List[str], top_k: int = 100) -> List[Dict]:
    """
    阶段一：向量召回

    Args:
        query: 用户查询
        chunks: 文档段落列表
        top_k: 召回数量（默认100）

    Returns:
        召回结果列表，包含chunk内容、相似度分数、来源信息
    """
    # 1. 文档解析与分块（已在预处理阶段完成）
    # 2. 查询向量化
    query_embedding = embed_model.encode(query)

    # 3. 批量计算chunk向量
    chunk_embeddings = embed_model.encode(chunks)

    # 4. 计算相似度并排序
    similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    results = []
    for idx in top_indices:
        results.append({
            "chunk": chunks[idx],
            "score": float(similarities[idx]),
            "index": int(idx)
        })

    return results
```

### 阶段二：重排精选（精筛）

**目标：** 使用大语言模型对召回结果进行精细化排序

**执行步骤：**

1. **候选构建**
   - 将阶段一召回的Top-100 chunk作为输入
   - 组织为适合LLM处理的格式

2. **重排提示设计**
   ```python
   RERANK_PROMPT = """你是一个专业的文档检索专家。请根据用户问题评估以下每个文档片段的相关性。

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
   ```

3. **LLM重排执行**
   - 调用大语言模型进行相关性评分
   - 解析返回的JSON结果
   - 按分数降序排列

4. **精选输出**
   - 选择Top-5至Top-10最相关的结果
   - 附带相关性分数和理由

**代码框架：**
```python
def llm_rerank(query: str, candidates: List[Dict], top_k: int = 10) -> List[Dict]:
    """
    阶段二：LLM重排

    Args:
        query: 用户查询
        candidates: 阶段一召回的候选结果
        top_k: 最终返回数量（默认10）

    Returns:
        重排后的结果列表
    """
    # 构建文档列表
    documents = "\n".join([
        f"[{i}] {c['chunk'][:500]}..."
        for i, c in enumerate(candidates[:50])  # 限制输入数量
    ])

    # 调用LLM进行重排
    response = llm.invoke(RERANK_PROMPT.format(
        query=query,
        documents=documents
    ))

    # 解析结果
    reranked = json.loads(response.content)

    # 合并结果
    final_results = []
    for item in sorted(reranked, key=lambda x: x['relevance_score'], reverse=True)[:top_k]:
        idx = item['index']
        final_results.append({
            "chunk": candidates[idx]['chunk'],
            "relevance_score": item['relevance_score'],
            "vector_score": candidates[idx]['score'],
            "reason": item['reason']
        })

    return final_results
```

## Agent执行集成

### 工作流程

```
用户上传附件 + 提出问题
        ↓
   [检测触发条件]
        ↓
   阶段一：向量召回
   (Embedding + 相似度检索)
        ↓
   阶段二：LLM重排
   (大语言模型精细化排序)
        ↓
   获取Top-K精选结果
        ↓
   构建Agent上下文
        ↓
   执行Agent任务
        ↓
   返回最终答案
```

### 上下文构建

将重排后的精选结果注入Agent上下文：

```python
def build_context(results: List[Dict], query: str) -> str:
    """构建用于Agent执行的上下文"""
    context_parts = [
        "=== 参考文档内容 ===",
        f"基于您的问题：{query}\n",
        "以下是相关度最高的文档片段：\n"
    ]

    for i, r in enumerate(results, 1):
        context_parts.append(
            f"\n【片段 {i}】(相关度: {r['relevance_score']:.2f})"
        )
        context_parts.append(r['chunk'])

    return "\n".join(context_parts)
```

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `chunk_size` | 800 | 文档分块大小（字符数） |
| `chunk_overlap` | 150 | 分块重叠大小 |
| `recall_top_k` | 100 | 阶段一召回数量 |
| `rerank_top_k` | 10 | 阶段二精选数量 |
| `embedding_model` | bge-large-zh | 向量化模型 |
| `rerank_model` | gpt-4 | 重排模型 |

## 错误处理

1. **附件解析失败**
   - 记录错误日志
   - 返回友好提示：无法解析附件格式

2. **向量化失败**
   - 降级为关键词检索
   - 或返回空结果并提示

3. **LLM重排失败**
   - 回退到纯向量相似度排序
   - 使用阶段一结果直接输出

## 性能优化建议

1. **批量处理：** 对多个chunk的向量化使用批量API调用
2. **缓存机制：** 缓存文档的embedding结果，避免重复计算
3. **异步执行：** 向量检索和LLM重排可并行执行
4. **限制输入：** LLM重排时限制输入chunk数量（建议50个）

## 输出格式

技能执行后返回结构化结果：

```json
{
  "status": "success",
  "query": "用户原始问题",
  "stage1_recall_count": 100,
  "stage2_rerank_count": 10,
  "results": [
    {
      "content": "精选的文档片段",
      "relevance_score": 0.95,
      "vector_score": 0.82,
      "source": "附件名称",
      "chunk_index": 5
    }
  ],
  "context_for_agent": "已构建的上下文字符串"
}
```
