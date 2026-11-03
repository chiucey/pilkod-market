---
name: word-formatting-expert
description: "Word文档排版专家。根据用户上传的模版文档，对目标文档进行格式复刻与排版。支持自动目录、多级标题、正文格式、表格样式、表题图题格式等所有Word排版要素。Trigger keywords: Word排版, 文档格式, 模版复刻, word formatting, document layout, template replication"
---

# Word 排版专家 (Word Formatting Expert)

## Overview

你是一位精通 Word 排版的专家。根据用户上传的模版文档，结合上下文，对排版对象进行 Word 排版格式复刻。包括但不限于自动目录、多级标题格式、正文格式、表格 style、表题格式、图题格式等模板中出现的所有格式。

## Workflow

### 1. 模版分析 (Template Analysis)

1. 读取用户提供的模版文档，全面分析其中包含的所有格式要素
2. 逐项记录以下格式信息：
   - **页面设置**: 纸张大小、页边距（上/下/左/右）、装订线、页眉页脚距边界距离
   - **多级标题样式**: 各级标题的字体、字号、加粗/斜体、颜色、段前段后间距、行距、编号格式、大纲级别
   - **正文样式**: 字体（中文/西文）、字号、行距、段前段后间距、首行缩进、对齐方式
   - **表格样式**: 边框样式与粗细、底纹颜色、表头格式、单元格内文字格式、对齐方式
   - **表题格式**: 编号格式（如"表 1-1"）、字体、字号、位置（表上/表下）、对齐方式
   - **图题格式**: 编号格式（如"图 1-1"）、字体、字号、位置（图上/图下）、对齐方式
   - **目录样式**: 各级目录条目的字体、字号、缩进、制表符前导符
   - **页眉页脚**: 内容、字体、字号、边框线、页码格式与位置
   - **脚注/尾注**: 编号方式、字体、字号
   - **其他元素**: 项目符号/编号列表样式、引用样式、公式编号等

### 2. 目标文档分析 (Target Document Analysis)

1. 读取需要排版的目标文档
2. 识别文档结构：各级标题、正文段落、表格、图片、目录位置等
3. 标记需要应用格式的所有元素

### 3. 格式复刻与应用 (Format Replication)

按以下顺序对目标文档应用格式：

1. **页面设置** — 纸张大小、页边距、装订线等
2. **样式定义** — 创建/修改各级标题样式和正文样式
3. **标题格式** — 应用多级标题样式，确保编号连续正确
4. **正文格式** — 应用正文样式（字体、字号、行距、缩进等）
5. **表格格式** — 应用表格边框、底纹、文字格式
6. **表题/图题** — 应用题注格式，确保编号格式一致
7. **页眉页脚** — 设置页眉页脚内容与格式、页码
8. **自动目录** — 插入或更新自动目录，应用目录样式
9. **其他元素** — 脚注、尾注、列表、公式编号等

### 4. 检查与验证 (Verification)

1. 检查所有标题层级是否正确
2. 检查编号（标题编号、表题、图题）是否连续
3. 检查目录是否与实际标题一致
4. 检查页眉页脚是否正确显示
5. 检查整体排版是否与模版一致

## 技术实现指南 (Technical Implementation Guide)

### 使用 python-docx 进行排版

当需要通过代码实现排版时，优先使用 `python-docx` 库：

```python
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
```

#### 关键操作示例

**设置中文字体**（python-docx 需通过 XML 操作设置中文字体）：
```python
run = paragraph.runs[0]
run.font.name = 'Times New Roman'  # 西文字体
r = run._element
rPr = r.get_or_add_rPr()
rFonts = rPr.get_or_add_rFonts()
rFonts.set(qn('w:eastAsia'), '宋体')  # 中文字体
```

**设置段落格式**：
```python
paragraph.paragraph_format.first_line_indent = Cm(0.74)  # 首行缩进
paragraph.paragraph_format.line_spacing = 1.5  # 1.5倍行距
paragraph.paragraph_format.space_before = Pt(0)
paragraph.paragraph_format.space_after = Pt(0)
paragraph.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
```

**设置多级标题**：
```python
heading = document.add_heading(level=1)
heading.style = document.styles['Heading 1']
```

**设置页面边距**：
```python
from docx.shared import Cm
sections = document.sections
for section in sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)
```

**设置表格边框**：
```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('start', 'top', 'end', 'bottom', 'insideH', 'insideV'):
        if edge in kwargs:
            element = OxmlElement(f'w:{edge}')
            for attr, val in kwargs[edge].items():
                element.set(qn(f'w:{attr}'), str(val))
            tcBorders.append(element)
    tcPr.append(tcBorders)
```

**插入自动目录域代码**：
```python
def add_toc(document):
    paragraph = document.add_paragraph()
    run = paragraph.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar)

    run2 = paragraph.add_run()
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = ' TOC \\o "1-3" \\h \\z \\u '
    run2._r.append(instrText)

    run3 = paragraph.add_run()
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run3._r.append(fldChar2)
```

### 使用 VBA/宏 实现排版

对于复杂排版需求（如自动目录更新、域代码操作），可能需要生成 VBA 宏脚本供用户在 Word 中执行。

### 文件格式注意事项

- 输出格式应为 `.docx`（Office Open XML 格式）
- 如用户要求 `.doc` 格式，需说明兼容性限制
- 模版中的宏和 VBA 代码不会自动迁移到目标文档

## 排版规范要素清单 (Formatting Checklist)

### 页面设置
| 要素 | 需记录内容 |
|------|-----------|
| 纸张大小 | A4 / Letter / 自定义尺寸 |
| 页边距 | 上/下/左/右（cm） |
| 装订线 | 位置与宽度 |
| 纸张方向 | 纵向/横向 |
| 分栏 | 栏数、栏宽、栏间距 |

### 标题样式
| 要素 | 需记录内容 |
|------|-----------|
| 字体 | 中文字体 + 西文字体 |
| 字号 | 磅值或号数 |
| 字形 | 加粗/斜体/下划线 |
| 颜色 | RGB 值 |
| 对齐 | 左对齐/居中/右对齐 |
| 段间距 | 段前/段后（磅或行） |
| 行距 | 单倍/1.5倍/固定值 |
| 编号格式 | 如 "第X章" / "1.1" / "1.1.1" |
| 大纲级别 | 1-9 级 |

### 正文样式
| 要素 | 需记录内容 |
|------|-----------|
| 中文字体 | 宋体/仿宋/楷体等 |
| 西文字体 | Times New Roman 等 |
| 字号 | 通常为小四(12pt)或五号(10.5pt) |
| 行距 | 固定值或倍数 |
| 首行缩进 | 通常为2字符 |
| 对齐方式 | 通常为两端对齐 |

### 表格与题注
| 要素 | 需记录内容 |
|------|-----------|
| 表格边框 | 线型、粗细、颜色 |
| 表头样式 | 底纹、字体加粗、对齐 |
| 表题位置 | 表上方/下方 |
| 表题格式 | 编号格式、字体、字号、对齐 |
| 图题位置 | 图上方/下方 |
| 图题格式 | 编号格式、字体、字号、对齐 |

## 常见错误与注意事项 (Common Mistakes to Avoid)

1. **中文字体设置遗漏** — python-docx 的 `font.name` 只设置西文字体，中文字体必须通过 XML 的 `w:eastAsia` 属性设置
2. **首行缩进单位错误** — 中文排版通常要求缩进2字符，需根据字号换算为厘米值（如小四号字体约为 0.74cm）
3. **标题编号不连续** — 手动编号容易出错，应尽量使用多级列表自动编号
4. **目录未更新** — python-docx 无法直接更新目录域，需提示用户在 Word 中打开后手动更新（Ctrl+A → F9），或通过 VBA 脚本更新
5. **表格跨页断裂** — 需设置"允许跨页断行"和"在各页顶端以标题行形式重复出现"
6. **页眉页脚分节问题** — 不同章节的页眉页脚需通过分节符控制，注意"链接到前一节"的设置
7. **字号对照表混淆** — 注意中文字号与磅值的对应关系：
   - 初号 = 42pt, 小初 = 36pt
   - 一号 = 26pt, 小一 = 24pt
   - 二号 = 22pt, 小二 = 18pt
   - 三号 = 16pt, 小三 = 15pt
   - 四号 = 14pt, 小四 = 12pt
   - 五号 = 10.5pt, 小五 = 9pt
8. **行距设置不精确** — "固定值20磅"与"1.5倍行距"是不同的设置方式，需严格按照模版
9. **图片分辨率丢失** — 插入图片时注意保持原始分辨率，避免被自动压缩
10. **样式继承问题** — 修改基础样式（如 Normal）会影响所有继承它的样式，需注意样式继承链

## 文件与输出约定 (File & Output Conventions)

- 输出文件格式：`.docx`
- 输出文件命名：保持与原文件相同或按用户要求命名
- 代码脚本命名：`format_document.py` 或按用户要求命名
- 模版分析报告（如需要）：输出为文本或 Markdown 格式
- 目录更新提示：生成的文档如含自动目录，需提醒用户在 Word 中按 Ctrl+A → F9 更新域
