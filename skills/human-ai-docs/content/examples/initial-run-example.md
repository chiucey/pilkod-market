# 首次运行完整示例

> **场景**: 首次为项目初始化 Human-AI-Docs 文档系统

---

## 对话记录

### 用户触发

```
用户: 梳理项目
```

### AI 分析项目

```
AI: 检测项目结构...

发现:
- Python 项目 (requirements.txt, setup.py)
- 项目名称: DataPipeline
- 目录结构: src/, tests/, configs/, scripts/
- 已有文件: README.md, requirements.txt

请描述项目的主要功能：
1. 这是什么类型的项目？
2. 主要使用的技术栈？
3. 核心模块有哪些？
4. 典型的开发工作流是什么？
```

### 用户描述

```
用户:
这是一个数据处理流水线项目，使用 Python 构建。主要功能是从多个数据源
采集数据，进行清洗转换，最后存入数据仓库。

技术栈:
- 数据采集: requests, scrapy
- 数据处理: pandas, numpy
- 数据存储: PostgreSQL, Redis
- 任务调度: Celery

核心模块:
- collectors/: 数据采集器
- processors/: 数据处理器
- loaders/: 数据加载器
- schedulers/: 任务调度

开发工作流:
1. 添加新的采集器
2. 配置数据源
3. 运行测试
4. 部署到生产环境
```

### AI 生成文档

```
AI: 正在分析并生成文档...

检测到项目类型: 数据处理流水线
技术栈: Python + 数据处理工具
模块数量: 4 个核心模块

正在生成三层文档...
```

### 生成结果

```
✅ 创建目录结构:
   docs/

✅ 生成核心文档:
   README.md (156 行)
   CLAUDE.md (78 行)
   docs/architecture.md
   docs/tech-stack.md
   docs/workflows.md
   docs/api.md

✅ 初始化状态日志:
   .ai-docs/doc-state.log.md

完成!
- CLAUDE.md: 78 行 (<100 ✅)
- README.md: 156 行
- docs/: 4 个技术文档
```

---

## 生成的文件

### README.md 摘要

```markdown
# DataPipeline

> Python 数据处理流水线 - 多数据源采集、清洗、存储

## 快速开始

### 环境要求
- Python 3.9+
- PostgreSQL 14+
- Redis 6+

### 安装

```bash
git clone https://github.com/xxx/datapipeline.git
cd datapipeline
pip install -r requirements.txt
python scripts/init_db.py
```

### 运行

```bash
# 启动数据流水线
python -m src.main

# 或使用调度器
celery -A src.schedulers.celery_app worker
```

## 主要功能

1. **多数据源采集**: 支持 API、爬虫、文件导入
2. **数据清洗**: pandas 数据预处理
3. **数据仓库**: PostgreSQL + Redis 存储

## 技术栈

- 数据采集: requests, scrapy, beautifulsoup4
- 数据处理: pandas, numpy
- 数据存储: PostgreSQL, Redis
- 任务调度: Celery, Redis Queue

## 开发指南

详见 [开发指南](docs/workflows.md)
```

### CLAUDE.md 摘要

```markdown
# DataPipeline AI Context

## 项目概览

- **类型**: Python 数据处理流水线
- **技术栈**: pandas, Celery, PostgreSQL, Redis
- **核心模块**: collectors, processors, loaders, schedulers

## 操作索引表

| 操作指令 | 详细文档 | 触发词 |
|----------|----------|--------|
| 添加采集器 | @docs/workflows.md#add-collector | "添加采集", "new collector" |
| 添加处理器 | @docs/workflows.md#add-processor | "添加处理", "new processor" |
| 运行测试 | @docs/workflows.md#run-tests | "测试", "run tests" |
| 部署应用 | @docs/workflows.md#deploy | "部署", "deploy" |

## 常用命令

```bash
# 开发
python -m src.main --config configs/dev.yaml

# 测试
pytest tests/ -v

# 构建 Docker
docker build -t datapipeline:latest .
```

## 技术栈

@docs/tech-stack.md

## 架构设计

@docs/architecture.md
```

---

## 验证步骤

### 1. 检查文件存在

```bash
ls -la README.md CLAUDE.md docs/
```

### 2. 验证行数

```bash
wc -l CLAUDE.md
# 预期: <100 行
```

### 3. 测试 @import

```
在 Claude Code 中输入:
@import docs/architecture.md

预期: 显示架构文档内容
```

---

## 后续使用

### 更新文档

```
用户: 更新工程文档

AI: 请描述变更...

用户: 添加了新的 MongoDB 数据源支持
```

### 查看文档

```
@import docs/tech-stack.md
@import docs/workflows.md
```

---

## 常见问题

### Q: 如何添加新的数据采集器？

**A**: 详见 @docs/workflows.md#add-collector

### Q: 如何配置新的数据源？

**A**: 编辑 configs/sources.yaml，添加数据源配置

### Q: 如何运行单元测试？

**A**: `pytest tests/ -v`
