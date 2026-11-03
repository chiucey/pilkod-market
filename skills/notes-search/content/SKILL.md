---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 0ce661ebdd4f8cde2a190005b5a9bbd2
    PropagateID: 0ce661ebdd4f8cde2a190005b5a9bbd2
    ReservedCode1: 3046022100f5196df3a7aaa20597df5ba2afd7400a9a339123fc560e54c7e5dda319b33f34022100ec82e68fb6a0aaae6c39cd49fae4bfb54178554ca9e11008e90b48a389056fca
    ReservedCode2: 3045022100c9815940109a56915de028b469663b81d3faff0cbe8efc2d7ea0f06c3de0cb930220336907317cb7facb8b870f8c4902cf0ae0c83dc3690774f2007640403e92fa06
description: 智能短文本笔记记录与语义搜索。当用户需要记录不超过100字的短语句片段、查找相关笔记内容、进行模糊语义搜索时使用。利用OpenClaw内置memory系统进行语义搜索，无需额外安装向量搜索库，适合快速记录灵感并事后检索。
name: notes-search
---

# 智能短文本笔记搜索技能

## 核心功能

本技能提供短文本笔记的记录与智能搜索能力，专门针对≤100字的短语句片段优化。

### 功能模块

#### 1. 笔记记录
- **快速添加**：用户输入短笔记，自动存储
- **格式校验**：确保内容不超过100字
- **时间戳**：自动记录创建时间

#### 2. 语义搜索（基于OpenClaw）
- **OpenClaw Memory Search**：利用OpenClaw内置的向量搜索能力
- **本地关键词匹配**：后备搜索模式，支持模糊匹配
- **混合搜索**：优先使用OpenClaw，不可用时自动降级

#### 3. 笔记管理
- **查看所有**：列出所有已记录的笔记
- **删除笔记**：根据ID删除指定笔记

## 使用方式

### 记录笔记
```
用户：请帮我记录"今天的会议要点"
技能：调用add_note工具，添加笔记
```

### 搜索笔记
```
用户：搜索"会议相关的内容"
技能：
1. 尝试使用OpenClaw memory search进行语义搜索
2. 如果不可用，使用本地关键词匹配
3. 返回最相关的笔记
```

## 技术架构

| 组件 | 实现 | 说明 |
|-----|------|------|
| 向量搜索 | OpenClaw Memory | 利用OpenClaw内置的memory系统 |
| 本地搜索 | 关键词匹配 | TF-IDF风格的评分算法 |
| 数据存储 | JSON文件 | 本地持久化 |
| 搜索协调 | 混合模式 | OpenClaw优先，降级后备 |

## 搜索流程

```
查询文本 → 检查OpenClaw可用性 → OpenClaw Memory Search
                                    ↓ (失败时)
                              本地关键词匹配 → 返回Top-K
```

## 数据结构

```
笔记存储:
- note_id: UUID字符串
- content: 笔记内容（≤100字）
- created_at: ISO时间戳
```

## 配置文件

配置文件位于 `./skills/config.py`，包含：
- `MAX_CONTENT_LENGTH`: 笔记最大长度（100字）
- `TOP_K`: 默认返回结果数量
- `DATA_DIR`: 数据存储目录

## 依赖项

本技能**无需额外安装向量搜索库**，依赖OpenClaw生态：
- OpenClaw CLI（用于memory search）
- Python标准库（json, subprocess, re, datetime）

## 搜索模式

| 模式 | 触发条件 | 说明 |
|-----|---------|------|
| OpenClaw Memory | openclaw命令可用 | 利用OpenClaw内置向量搜索 |
| 本地关键词 | openclaw不可用 | 基于词频和短语匹配 |

## 限制说明

- 单条笔记内容不超过100字
- 搜索结果默认返回5条，可配置
- 所有数据存储在本地JSON文件
- OpenClaw未安装时自动降级到本地搜索