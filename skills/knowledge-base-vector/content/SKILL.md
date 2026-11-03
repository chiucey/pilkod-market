---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 4eb21f7a00d7581132f1b4c72ab9b559
    PropagateID: 4eb21f7a00d7581132f1b4c72ab9b559
    ReservedCode1: 3045022100b254feae1d4a37b04e3fe789a32bbca9b24e9754f13091f97df77de9230e302f0220388c80b04d03381bc4286fc1bd8c278bbd0d3aca885af269b8bcfc4f6654ef1e
    ReservedCode2: 3044022064a72c42c0c37e4cfe588f127d275ef65b286bf90990d801c081e0fa3e8c7671022044313bbc3abf1a974b7c0957fa2d76c1e7b2123e12ad6dcfe219edc82893cdd0
description: 知识库向量数据库工具。当用户需要将文档存入向量数据库、进行语义检索、构建RAG知识库问答、或查询知识库内容时使用。触发短语包括："存入知识库"、"向量检索"、"知识库问答"、"语义搜索"、"构建知识库"、"查询知识库"等。
name: knowledge-base-vector
---

# 知识库向量数据库技能

将知识文档存入 SQLite 向量数据库，支持大模型调用进行向量化存储和语义检索。

## 核心功能

1. **文档入库** - 读取文本/Markdown文件，向量化后存入SQLite向量数据库
2. **语义检索** - 基于向量相似度搜索相关知识片段
3. **RAG问答** - 结合检索结果和大模型生成答案

## 工作流程

### 1. 初始化知识库

```bash
# 初始化SQLite向量数据库
python scripts/init_knowledge_base.py --db-path ./knowledge.db
```

### 2. 存入知识文档

```bash
# 存入单个文档
python scripts/ingest_document.py --db-path ./knowledge.db --file ./docs/guide.md --collection main

# 批量存入目录
python scripts/batch_ingest.py --db-path ./knowledge.db --dir ./docs --collection main
```

### 3. 语义检索

```bash
# 检索相关知识
python scripts/retrieve.py --db-path ./knowledge.db --query "如何配置系统" --top-k 5
```

### 4. 知识库问答（RAG）

```bash
# 基于知识库回答问题
python scripts/rag_query.py --db-path ./knowledge.db --question "系统配置步骤是什么" --model gpt-4
```

## 数据库结构

| 表名 | 说明 |
|------|------|
| documents | 文档元数据 |
| chunks | 文本分块 |
| embeddings | 向量数据 |

## 配置说明

环境变量：
- `OPENAI_API_KEY` - OpenAI API密钥（用于嵌入和LLM）
- `DATABASE_PATH` - SQLite数据库路径

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--db-path` | 数据库路径 | ./knowledge.db |
| `--collection` | 集合名称 | default |
| `--chunk-size` | 分块大小 | 500 |
| `--top-k` | 返回数量 | 5 |

## 依赖

- sqlite-vec (SQLite向量扩展)
- openai (嵌入和LLM)
- langchain (文档处理)
