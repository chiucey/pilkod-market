---
name: local-rag-assistant
description: 本地RAG检索增强生成助手。当用户需要基于本地文档进行问答、检索知识库、提取文档信息、分析本地文件内容，或需要实现私有知识库问答系统时使用此技能。支持PDF、txt、markdown、docx等常见文档格式。
---

# Local RAG Assistant

本地检索增强生成（Retrieval-Augmented Generation）技能，帮助用户基于本地文档进行智能问答和信息检索。

## 核心能力

- **文档解析**：支持 PDF、TXT、Markdown、DOCX、HTML 等格式
- **文本分块**：智能文档分割，保留语义完整性
- **向量嵌入**：使用本地 Embedding 模型生成向量表示
- **相似性检索**：基于向量相似度的精确检索
- **答案生成**：结合检索结果生成准确答案

## 工作流程

### 1. 文档准备

当用户提供本地文档或知识库时：

```
检查文档格式 → 解析文本内容 → 智能分块 → 生成向量索引
```

**分块策略**：
- 按段落或固定长度分块（推荐 500-1000 字符）
- 保留相邻块之间的语义关联
- 记录每个块的来源位置

### 2. 查询处理

当用户提出问题时：

```
解析查询 → 生成查询向量 → 相似度检索 → 上下文组装
```

**检索参数**：
- Top-K 检索（默认 5-10 个最相关块）
- 相似度阈值过滤（默认 >0.5）
- 可选：重排序（Rerank）提升精度

### 3. 答案生成

```
组装检索上下文 → 构建 Prompt → 调用 LLM → 返回答案
```

**Prompt 模板**：
```
基于以下参考内容回答问题。如果参考内容不足以回答，请明确说明。

参考内容：
{retrieved_context}

问题：{user_question}

回答：
```

## 使用场景

| 场景 | 输入 | 输出 |
|------|------|------|
| 文档问答 | 本地 PDF/文档文件 | 基于文档的准确回答 |
| 知识库检索 | 文档集合 | 相关段落和来源 |
| 信息提取 | 结构化/非结构化文档 | 关键信息汇总 |
| 摘要生成 | 长文档 | 自动摘要和要点 |

## 技术实现

### 依赖库

```
# 文档解析
PyPDF2 / pdfplumber  # PDF
python-docx          # Word
markdown             # Markdown

# 向量化 (选择其一)
sentence-transformers  # 推荐：高质量英文/多语言
text2vec / m3e-base    # 中文支持

# 向量存储
faiss / chroma / qdrant  # 本地向量数据库

# LLM (本地模型)
llama.cpp / Ollama / vLLM
```

### 向量数据库选择

| 数据库 | 特点 | 适用场景 |
|--------|------|----------|
| **Faiss** | Facebook 开源，轻量级 | 小规模数据，单机部署 |
| **Chroma** | 简单易用，Python 原生 | 原型开发，快速迭代 |
| **Qdrant** | 高性能，支持过滤 | 生产环境，需要元数据过滤 |

### Embedding 模型推荐

| 模型 | 维度 | 语言 | 特点 |
|------|------|------|------|
| **BAAI/bge-large-zh** | 1024 | 中英 | 中文优化，高精度 |
| **sentence-transformers/all-MiniLM-L6-v2** | 384 | 多语言 | 轻量快速 |
| **moka-ai/m3e-base** | 768 | 中英 | 中文场景优化 |

## 快速启动示例

```python
# 1. 初始化组件
from rag_engine import RAGEngine

engine = RAGEngine(
    embed_model="BAAI/bge-large-zh",
    llm_provider="ollama",  # 或 openai, anthropic
    vector_store="faiss"
)

# 2. 索引文档
engine.index_documents(
    paths=["/path/to/docs/"],
    chunk_size=500,
    chunk_overlap=50
)

# 3. 查询问答
result = engine.query(
    question="文档中的核心观点是什么？",
    top_k=5
)
print(result["answer"])
print(f"参考来源: {result['sources']}")
```

## 注意事项

1. **首次使用**：需要下载 Embedding 模型（约 1-2GB）
2. **性能优化**：
   - 批量索引提升速度
   - 合理设置 chunk_size 平衡精度和速度
   - 冷启动问题：首次查询较慢
3. **准确性提升**：
   - 调整 top_k 和相似度阈值
   - 使用重排序模型优化结果
   - 尝试不同的分块策略

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 模型下载慢 | 使用镜像源或预下载模型 |
| 内存不足 | 减小 batch_size 或使用量化模型 |
| 检索不准 | 尝试其他 Embedding 模型或调整参数 |
| LLM 响应慢 | 使用量化模型或切换到云端 API |
