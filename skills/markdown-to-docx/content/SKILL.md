---
name: markdown-to-docx
description: 将markdown文件转换为docx文档。当用户要求转换markdown为word文档、处理包含图片、表格的markdown文件、批量转换markdown文件时使用。
---

# Markdown 转 DOCX 工具

## 功能说明

将Markdown文件转换为Microsoft Word (DOCX)格式，支持：
- 文本内容（标题、段落、列表、引用、代码块）
- 图片（本地图片和URL图片）
- 表格
- 超链接
- 粗体、斜体等格式

## 环境要求

- Python 3.8.5 - 3.11
- 依赖库：python-docx, markdown, Pillow, requests

## 安装依赖

```bash
pip install python-docx markdown Pillow requests
```

## 使用方法

### 命令行使用

```bash
python markdown_to_docx.py input.md output.docx
```

### API调用

```python
from markdown_to_docx import MarkdownToDocxConverter

converter = MarkdownToDocxConverter()
converter.convert("input.md", "output.docx", image_dir="images/")
```

## 转换规则

| Markdown元素 | DOCX对应 |
|-------------|----------|
| # 标题1 | 标题1样式 |
| ## 标题2 | 标题2样式 |
| ### 标题3 | 标题3样式 |
| **粗体** | 粗体文本 |
| *斜体* | 斜体文本 |
| [链接](url) | 超链接 |
| `代码` | 内联代码块 |
| ```代码块``` | 代码段落 |
| > 引用 | 引用段落 |
| - 列表 | 项目符号列表 |
| 1. 列表 | 编号列表 |
| \| 表格 \| | 表格 |
| ![图片](path) | 图片 |

## 注意事项

1. **图片处理**：本地图片使用相对路径，URL图片自动下载
2. **表格样式**：表头使用加粗背景色
3. **代码块**：使用等宽字体并添加边框
4. **输出目录**：默认在同目录下生成同名.docx文件