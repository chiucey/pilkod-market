# 本地RAG技术规格说明

## 概述

本地RAG（Retrieval-Augmented Generation，检索增强生成）是一种结合信息检索与语言模型生成的技术架构。该技能实现了完整的本地化RAG系统，无需依赖云服务即可进行基于私有文档的智能问答。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户查询                            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    文档索引流程                           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ 文档加载 │───▶│ 文本分块 │───▶│ 向量嵌入 │          │
│  └──────────┘    └──────────┘    └────┬─────┘          │
│                                        │                │
│                                        ▼                │
│                                 ┌──────────────┐        │
│                                 │  向量数据库   │        │
│                                 └──────────────┘        │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    查询回答流程                           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ 查询嵌入 │───▶│ 相似检索 │───▶│ 上下文组装│          │
│  └──────────┘    └──────────┘    └────┬─────┘          │
│                                        │                │
│                                        ▼                │
│                                 ┌──────────────┐        │
│                                 │  LLM 生成答案 │        │
│                                 └──────────────┘        │
└─────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. 文档加载器（DocumentLoader）

**支持的格式**：

| 格式 | 扩展名 | 依赖库 | 说明 |
|------|--------|--------|------|
| 纯文本 | .txt | 内置 | UTF-8 编码 |
| Markdown | .md | 内置 | 保留格式结构 |
| PDF | .pdf | PyPDF2/pdfplumber | 文本提取 |
| Word | .docx | python-docx | 段落提取 |
| HTML | .html | beautifulsoup4 | 去噪提取 |

**设计原则**：
- 统一接口：`load(file_path) -> str`
- 异常处理：每种格式独立错误处理
- 编码兼容：优先 UTF-8，自动检测备用编码

### 2. 文本分块器（TextChunker）

**分块策略**：

1. **段落级分块**：按自然段落分割
2. **句子边界优化**：避免在句子中间截断
3. **重叠机制**：相邻块保留重叠内容，保持语义连续性

**参数配置**：

| 参数 | 默认值 | 说明 | 建议范围 |
|------|--------|------|----------|
| chunk_size | 500 | 每块字符数 | 300-1000 |
| overlap | 50 | 块间重叠 | 10%-20% |

**分块算法**：

```
输入: 文本内容, chunk_size, overlap
输出: List[DocumentChunk]

1. 按换行分割获取段落列表
2. 遍历段落，累积字符数
3. 当累积超过 chunk_size 时：
   a. 尝试在最近句号/换行处截断
   b. 保存当前块
   c. 保留最后 overlap 字符作为下一块开头
4. 处理末尾残余文本
```

### 3. 嵌入引擎（EmbeddingEngine）

**支持的模型**：

| 模型 | 维度 | 语言 | 适用场景 | 模型大小 |
|------|------|------|----------|----------|
| BAAI/bge-large-zh | 1024 | 中英 | 中文优先 | ~1.3GB |
| sentence-transformers/all-MiniLM-L6-v2 | 384 | 多语言 | 轻量快速 | ~90MB |
| moka-ai/m3e-base | 768 | 中英 | 通用中文 | ~400MB |

**配置示例**：

```python
# 中文优化配置
engine = EmbeddingEngine("BAAI/bge-large-zh")

# 多语言通用配置
engine = EmbeddingEngine("sentence-transformers/all-MiniLM-L6-v2")

# 获取向量维度
dim = engine.get_embedding_dim()  # e.g., 1024
```

### 4. 向量存储（VectorStore）

**后端对比**：

| 后端 | 特点 | 优点 | 缺点 |
|------|------|------|------|
| **Faiss** | Facebook开源 | 速度快、支持GPU | 需要手动管理 |
| **Chroma** | Python原生 | 简单易用 | 功能较基础 |

**Faiss 索引类型**：

| 索引类型 | 说明 | 适用规模 |
|----------|------|----------|
| IndexFlatIP | 内积（需归一化） | 小规模，精确检索 |
| IndexIVFFlat | 倒排文件索引 | 中等规模 |
| IndexHNSW | 图索引 | 大规模，高速 |

**使用方法**：

```python
# 初始化
store = VectorStore(backend="faiss", dimension=1024)
store.init_index()

# 添加文档块
store.add(chunks)

# 检索
results = store.search(query_embedding, top_k=5)

# 保存/加载
store.save("index.faiss")
store.load("index.faiss")
```

## 检索算法

### 向量相似度计算

**内积（Inner Product）**：
```
similarity(a, b) = Σ(a_i × b_i)
```

**余弦相似度**（归一化后等价于内积）：
```
similarity(a, b) = (a · b) / (||a|| × ||b||)
```

### 检索流程

```
1. 查询向量化
   query_embedding = encode(query)

2. 相似度搜索
   scores, indices = index.search(query_embedding, k=top_k)

3. 结果过滤
   results = [r for r in results if r.score >= threshold]

4. 结果组装
   context = "\n\n".join([r.content for r in results])
```

## Prompt 设计

### 默认模板

```
基于以下参考内容回答问题。如果参考内容不足以回答，请明确说明。

参考内容：
{retrieved_context}

问题：{user_question}

回答：
```

### 优化策略

1. **few-shot 示例**：添加示例问答提升准确性
2. **引用标注**：让模型标注信息来源
3. **安全边界**：明确告知模型"不知道"的情况

## 性能优化

### 1. 索引优化

```python
# 批量添加提升速度
batch_size = 100
for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i+batch_size]
    store.add(batch)
```

### 2. 内存优化

```python
# 使用量化模型减少内存
model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder='./models')
```

### 3. 缓存策略

```python
# 复用嵌入结果
from functools import lru_cache

@lru_cache(maxsize=10000)
def get_embedding(text):
    return encoder.encode(text)
```

## 准确性评估

### 评估指标

| 指标 | 说明 | 计算方式 |
|------|------|----------|
| Precision@K | 前K结果准确率 | 相关文档数/K |
| Recall@K | 前K结果召回率 | 检出相关数/总相关数 |
| MRR | 平均倒数排名 | Σ(1/rank_i)/N |
| NDCG | 归一化折扣收益 | 综合排序质量 |

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 检索不相关 | Embedding 模型不匹配 | 更换中英/领域模型 |
| 答案不完整 | 上下文被截断 | 增大 chunk_size |
| 重复内容 | 块间重叠过大 | 减小 overlap |
| 遗漏关键信息 | 分块破坏语义 | 使用语义分块 |

## 部署建议

### 单机部署

```bash
# 安装依赖
pip install -r requirements.txt

# 下载模型（首次）
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-large-zh')"

# 运行
python quick_start.py -d ./docs -q "你的问题"
```

### Docker 部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "quick_start.py", "-d", "/data/docs", "-q", "你的问题"]
```

### GPU 加速

```bash
# 安装 GPU 版本
pip install faiss-gpu

# 或使用 CUDA 加速的嵌入模型
```
