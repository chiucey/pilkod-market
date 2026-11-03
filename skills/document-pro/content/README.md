# Document Pro - 专业文档处理技能

## 简介

Document Pro 是一款专为 MiniMax Agent 设计的多格式文档智能处理技能，支持 PDF、DOCX、PPT、TXT、Markdown 等常见文档格式的读取、解析、内容提取与智能总结。

## 核心功能

- **多格式支持**：PDF、DOCX、PPT/TXT、Markdown
- **智能解析**：自动识别文档结构，提取标题、正文、表格
- **内容总结**：生成精准摘要，保留核心信息
- **关键词提取**：自动识别高频词汇与关键概念
- **结构化输出**：JSON 格式输出，便于后续处理
- **隐私保护**：全程本地计算，不上传不存储

## 支持格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| PDF | .pdf | 文本提取、页面分析 |
| Word | .docx | 段落、表格、标题 |
| PowerPoint | .pptx | 幻灯片、文本框 |
| 纯文本 | .txt | 直接读取 |
| Markdown | .md | 结构化解析 |

## 安装依赖

```bash
pip install PyPDF2 python-docx python-pptx PyYAML
```

## 快速开始

### 命令行使用

```bash
# 处理文本
echo '{"content": "文档内容...", "mode": "summary"}' | python src/main.py

# 处理文件
python src/main.py << EOF
{"file_path": "/path/to/document.pdf", "mode": "full"}
EOF
```

### Python API

```python
from src.main import run

# 处理文本内容
result = run({
    "content": "文档内容...",
    "mode": "summary"
})

# 处理文件
result = run({
    "file_path": "/path/to/document.pdf",
    "mode": "full"
})
```

## 输出模式

| 模式 | 说明 |
|------|------|
| `summary` | 仅摘要和关键词 |
| `extract` | 关键词和段落 |
| `structure` | 结构化数据 |
| `full` | 完整结果（含元数据） |

## 配置参数

```yaml
processing:
  min_paragraph_length: 100  # 最小段落长度
  max_summary_length: 1000   # 最大摘要长度
  keyword_count: 10          # 关键词数量
  language: zh-CN            # 输出语言
  default_mode: full         # 默认模式
```

## 触发词

- 文档处理、解析文档、读取文档
- 文档总结、内容总结
- 提取关键信息、关键词提取
- 格式转换、Document Pro

## 项目结构

```
document-pro/
├── SKILL.md                 # 技能定义文件
├── README.md                 # 本文档
├── src/
│   └── main.py              # 核心处理模块
├── instructions/
│   └── system_prompt.md     # 系统提示词
├── config/
│   └── settings.yaml        # 配置文件
├── tests/
│   └── test_main.py         # 测试用例
└── assets/
    └── .gitkeep             # 资源目录
```

## 测试

```bash
cd tests
python test_main.py
```

或使用 unittest：

```bash
python -m unittest test_main -v
```

## 隐私声明

- 全程本地计算，无网络请求
- 不存储用户文档
- 不上传任何数据
- 保护用户隐私安全

## 许可

MIT License

## 作者

Document Pro Team
