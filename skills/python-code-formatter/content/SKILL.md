---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 0346220d00f7823827c66d6c6d3fbfc7
    PropagateID: 0346220d00f7823827c66d6c6d3fbfc7
    ReservedCode1: 3045022100a5a1d0413d2547351341100215ccc53548432d38c9620391de79110fec0bec830220669543c9bf7e4617fca51232cc208e3ca71add17410f741439e519ab3d2e86e1
    ReservedCode2: 3045022009f4f74ce3b9274d4ecf303d8d81040c65de81b1581573147b45c3c1d2b2e7de022100e99eddc5b42aa9113333f2989a76254264d8e63b6895e1662c7d16e84f30a79f
description: Python 代码格式检查工具。当用户要求检查 Python 代码格式、整理代码格式、执行 lint 检查、格式化代码、自动排版 Python 文件时使用。触发短语包括：检查代码格式、格式化代码、整理代码风格、代码格式化检查、Python lint、自动排版。
name: python-code-formatter
---

# Python Code Formatter

Python 代码格式检查和格式化技能，支持多种格式化工具和配置选项。

## 工作流程

### 1. 接收用户输入

接收用户提供的 Python 代码或文件路径，支持以下输入格式：
- 直接粘贴代码片段
- 文件路径列表
- 整个项目目录

### 2. 分析代码格式

执行以下格式检查项目：

| 检查项 | 工具 | 说明 |
|--------|------|------|
| 代码风格 | flake8 | 检查 PEP8 风格违规 |
| 代码格式化 | autopep8 | 自动修复 PEP8 问题 |
| 行长度检查 | - | 检查是否超过 120 字符限制 |
| 缩进检查 | - | 验证使用 4 空格缩进 |
| 导入排序 | isort | 检查和排序 import 语句 |
| 代码布局 | black | 统一代码格式化 |

### 3. 执行格式化

根据用户需求选择格式化工具：

```bash
# 使用 autopep8 格式化（自动修复）
autopep8 --in-place --aggressive --aggressive <file_path>

# 使用 black 格式化
black <file_path>

# 使用 isort 排序导入
isort <file_path>

# 完整检查（flake8）
flake8 <file_path> --max-line-length=120 --extend-ignore=E203,W503
```

### 4. 输出报告

生成格式检查报告，包含：
- 检测到的格式问题列表
- 问题位置（文件、行号）
- 问题严重程度
- 修复建议

## 输出格式

### 检查结果

```
Python Code Format Check Report
================================

File: example.py
Status: Issues Found / All Good

Issues:
  Line 15: E501 - Line too long (85 > 79 characters)
  Line 23: E225 - Missing whitespace around operator
  Line 30: F401 - 'os' imported but unused

Suggested Fixes:
  autopep8 example.py --in-place
  isort example.py
```

### 格式化完成

```
Format Complete
===============

Formatted Files: 3
Total Issues Fixed: 12
Files Modified: example1.py, example2.py

Changes Applied:
  - Fixed indentation (4 spaces)
  - Added missing whitespace
  - Removed unused imports
  - Sorted import statements
```

## 配置选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| max_line_length | 最大行长度 | 120 |
| indent_size | 缩进空格数 | 4 |
| sort_imports | 是否排序导入 | true |
| check_only | 仅检查不修改 | false |

## 执行命令

```bash
# 格式检查（不修改）
flake8 <file_or_dir> --max-line-length=120

# 自动格式化
autopep8 --in-place --aggressive <file_path>

# 统一格式化（black 风格）
black --line-length 120 <file_path>

# 排序导入
isort --profile black <file_path>

# 完整格式化流程
isort <file_path> && autopep8 --in-place --aggressive <file_path> && black --check <file_path>
```

## 常见问题处理

### 问题：多个文件需要检查
```bash
flake8 ./src --max-line-length=120 --extend-ignore=E203,W503
```

### 问题：仅检查特定目录
```bash
flake8 ./src/**/*.py --max-line-length=120
```

### 问题：生成详细报告
```bash
flake8 <file_path> --max-line-length=120 --show-source --statistics
```

## 使用场景

1. **提交前检查**：在 git commit 前运行格式检查
2. **代码审查**：审查 PR 中的格式问题
3. **批量格式化**：修复整个项目的格式问题
4. **持续集成**：在 CI 流程中集成格式检查
