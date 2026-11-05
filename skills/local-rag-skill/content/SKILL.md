---
name: local-rag-skill
description: 本地知识库构建与管理工具。当用户需要将文档转化为Markdown形成本地知识库，或需要进行知识库的增删改查、文档检索、向量搜索等操作时使用。触发短语包括："创建知识库"、"上传文档"、"知识库管理"、"文档检索"、"RAG"、"向量搜索"、"本地知识库"等。
---

# Local RAG Skill - 本地知识库构建与管理

## 概述

Local RAG Skill 提供完整的本地知识库解决方案，支持将各种格式的文档（PDF、Word、TXT、HTML等）转化为Markdown格式，并提供基于向量数据库的语义检索能力。

## 核心功能

### 1. 文档处理
- 支持多种文档格式：PDF、DOCX、TXT、HTML、Markdown
- 自动将文档内容转换为Markdown格式
- 保留文档结构和关键元数据

### 2. 知识库管理
- **增（Create）**：添加新文档到知识库
- **删（Delete）**：从知识库移除文档
- **改（Update）**：更新已有文档内容
- **查（Query）**：语义检索和关键词搜索

### 3. 向量检索
- 基于Embedding的语义相似度匹配
- 支持混合搜索（语义+关键词）
- 可配置相似度阈值

## 文件结构

```
local-rag-skill/
├── SKILL.md                 # 技能说明文档
├── scripts/
│   ├── config.py            # 配置文件
│   ├── document_processor.py # 文档处理模块
│   ├── vector_store.py      # 向量存储模块
│   ├── knowledge_base.py    # 知识库主类
│   └── cli.py               # 命令行工具
├── requirements.txt         # 依赖包
└── README.md               # 使用说明
```

## 使用方式

### 命令行接口

```bash
# 初始化知识库
python -m local_rag init --db_path ./vector_db

# 添加文档
python -m local_rag add ./documents/*.pdf --chunk-size 500

# 搜索
python -m local_rag search "如何配置系统" --top-k 5

# 列出知识库内容
python -m local_rag list

# 删除文档
python -m local_rag delete <doc_id>

# 更新文档
python -m local_rag update <doc_id> --file ./new_doc.pdf
```

### Python API

```python
from knowledge_base import LocalKnowledgeBase

# 初始化
kb = LocalKnowledgeBase(db_path="./vector_db")

# 添加文档
doc_id = kb.add_document("./report.pdf", metadata={"source": "report"})

# 搜索
results = kb.search("查询内容", top_k=5)

# 获取原始文档
doc = kb.get_document(doc_id)

# 删除文档
kb.delete_document(doc_id)

# 更新文档
kb.update_document(doc_id, "./new_version.pdf")
```

## 配置选项

| 参数 | 默认值 | 说明 |
|------|--------|------|
| chunk_size | 500 | 文本分块大小（字符数） |
| chunk_overlap | 50 | 相邻块重叠字符数 |
| embedding_model | text-embedding-ada-002 | Embedding模型 |
| vector_db | chromadb | 向量数据库类型 |
| top_k | 4 | 默认返回结果数 |

## 技术栈

- **文档处理**：PyMuPDF、python-docx、beautifulsoup4
- **向量存储**：ChromaDB / FAISS
- **Embedding**：sentence-transformers（本地）或 OpenAI API
- **CLI**：argparse / click

## 适用场景

- 个人知识管理
- 企业内部文档问答系统
- 研究资料整理
- 法律/医疗文档检索
- 产品手册智能问答
