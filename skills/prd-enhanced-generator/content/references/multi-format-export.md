# 多格式文档导出指南

## 概述

本指南说明如何将PRD Markdown文档导出为Word(.docx)和PDF(.pdf)格式。

## 格式对比

| 格式 | 优势 | 劣势 | 适用场景 |
|------|------|------|---------|
| Markdown | 轻量、版本控制友好、可直接编辑 | 样式有限 | 协作开发、代码审查 |
| Word | 样式丰富、易编辑、可批注 | 跨平台可能有兼容问题 | 正式评审、离线编辑 |
| PDF | 版式固定、打印保真 | 不可直接编辑 | 最终交付、打印存档 |

## 工具选择

### 推荐工具：Pandoc

Pandoc是一个通用的文档转换工具，支持多种格式之间的转换。

**安装方式**：

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc

# Windows (使用Chocolatey)
choco install pandoc
```

**额外依赖**：
- Word导出：需要LibreOffice或自定义模板
- PDF导出：需要LaTeX环境（如TeX Live、MiKTeX）

## 转换命令参考

### Markdown → Word

```bash
# 基础转换
pandoc PRD文档.md -o PRD文档.docx

# 使用自定义模板
pandoc PRD文档.md -o PRD文档.docx \
  --reference-doc=template.docx

# 保留表格样式
pandoc PRD文档.md -o PRD文档.docx \
  --from=markdown+grid_tables
```

### Markdown → PDF

```bash
# 使用xelatex引擎（推荐，支持中文）
pandoc PRD文档.md -o PRD文档.pdf \
  --pdf-engine=xelatex \
  -V mainfont="Microsoft YaHei" \
  -V monofont="Source Code Pro"

# 使用wkhtmltopdf引擎
pandoc PRD文档.md -o PRD文档.pdf \
  --pdf-engine=wkhtmltopdf \
  --self-contained

# 使用pandoc wrapper（最简单）
pandoc PRD文档.md -o PRD文档.pdf
```

## 自定义Word模板

### 模板结构

```
template.docx/
├── word/
│   ├── document.xml      # 主文档内容
│   ├── styles.xml        # 样式定义
│   ├── settings.xml      # 文档设置
│   └── theme/
│       └── theme1.xml    # 主题定义
├── _rels/
│   └── .rels
└── [Content_Types].xml
```

### 样式定义建议

在styles.xml中定义以下样式：

```xml
<w:style w:type="paragraph" w:styleId="Normal">
  <w:name w:val="Normal"/>
  <w:rPr>
    <w:rFonts w:eastAsia="微软雅黑" w:ascii="Calibri"/>
    <w:sz w:val="24"/>
  </w:rPr>
</w:style>

<w:style w:type="paragraph" w:styleId="Heading1">
  <w:name w:val="heading 1"/>
  <w:basedOn w:val="Normal"/>
  <w:pPr>
    <w:outlineLvl w:val="0"/>
    <w:spacing w:before="480" w:after="240"/>
  </w:pPr>
  <w:rPr>
    <w:b/>
    <w:sz w:val="44"/>
  </w:rPr>
</w:style>
```

## PDF导出最佳实践

### 中文支持

确保LaTeX环境支持中文：

```bash
# 安装中文字体包
tlmgr install ctex xeCJK notoCJK

# 或者使用ctexart文档类
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V documentclass=ctexart
```

### 图片处理

Mermaid图表在PDF中可能显示为代码块。如需保留图表：

1. **方案一**：将Mermaid图表预渲染为图片
2. **方案二**：使用HTML输出，在Word/PDF中显示代码
3. **方案三**：使用Mermaid CLI预渲染

```bash
# 预渲染Mermaid图表
npx @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.png
```

### 分页控制

```yaml
---
title: PRD文档标题
geometry: margin=2.5cm
papersize: a4
fontsize: 11pt
---
```

## 自动化脚本

### 批量转换脚本

```bash
#!/bin/bash
# convert.sh - PRD文档多格式转换脚本

INPUT="$1"
NAME="${INPUT%.md}"

echo "正在转换文档..."
echo "输入: $INPUT"

# 创建输出目录
mkdir -p "output"

# 转换为Word
echo "生成Word文档..."
pandoc "$INPUT" \
  -o "output/${NAME}.docx" \
  --reference-doc=template.docx

# 转换为PDF
echo "生成PDF文档..."
pandoc "$INPUT" \
  -o "output/${NAME}.pdf" \
  --pdf-engine=xelatex \
  -V mainfont="Microsoft YaHei" \
  -V monofont="Source Code Pro"

echo "转换完成！"
echo "输出目录: output/"
ls -la "output/"
```

### Python脚本（跨平台）

```python
#!/usr/bin/env python3
"""
prd_converter.py - PRD文档多格式转换工具
"""

import subprocess
import os
import sys
from pathlib import Path

def convert_to_word(input_file: str, output_dir: str = "output"):
    """Markdown转换为Word"""
    output_file = Path(output_dir) / f"{Path(input_file).stem}.docx"
    cmd = [
        "pandoc", input_file,
        "-o", str(output_file),
        "--reference-doc=template.docx"
    ]
    subprocess.run(cmd, check=True)
    return output_file

def convert_to_pdf(input_file: str, output_dir: str = "output"):
    """Markdown转换为PDF"""
    output_file = Path(output_dir) / f"{Path(input_file).stem}.pdf"
    cmd = [
        "pandoc", input_file,
        "-o", str(output_file),
        "--pdf-engine=xelatex",
        "-V", "mainfont=Microsoft YaHei",
        "-V", "monofont=Source Code Pro"
    ]
    subprocess.run(cmd, check=True)
    return output_file

def main():
    if len(sys.argv) < 2:
        print("用法: python prd_converter.py <input.md>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = "output"

    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)

    # 执行转换
    try:
        word_file = convert_to_word(input_file, output_dir)
        print(f"Word文档已生成: {word_file}")
    except Exception as e:
        print(f"Word转换失败: {e}")

    try:
        pdf_file = convert_to_pdf(input_file, output_dir)
        print(f"PDF文档已生成: {pdf_file}")
    except Exception as e:
        print(f"PDF转换失败: {e}")

if __name__ == "__main__":
    main()
```

## 常见问题

### Q: Pandoc找不到怎么办？
A: 确保Pandoc已正确安装并添加到PATH：
```bash
# 检查安装
pandoc --version

# 如未安装
# macOS: brew install pandoc
# Ubuntu: sudo apt-get install pandoc
```

### Q: PDF中文显示为方块怎么办？
A: 安装中文字体并指定字体：
```bash
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V mainfont="PingFang SC"  # macOS
  # 或 -V mainfont="Microsoft YaHei"  # Windows
```

### Q: 表格样式丢失怎么办？
A: 使用grid_tables扩展：
```bash
pandoc input.md \
  --from=markdown+grid_tables \
  -o output.docx
```

### Q: 代码块无法高亮怎么办？
A: 指定高亮主题：
```bash
pandoc input.md \
  --highlight-style=pygments \
  -o output.pdf
```

## 交付检查清单

- [ ] Markdown源文件语法正确
- [ ] Word文档标题层级正确
- [ ] 表格格式完整
- [ ] 图片/图表正常显示
- [ ] 中文显示无乱码
- [ ] PDF排版美观
- [ ] 文件大小合理（< 10MB）

---

*本文档为参考指南，详细实现请参考SKILL.md第4节*
