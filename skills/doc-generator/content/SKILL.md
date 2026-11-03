---
name: doc-generator
description: "专家级文档创建专家，使用 Python 代码生成专业的 PDF、PPTX、XLSX 和 DOCX 文件。具有适当的格式、图表和数据可视化能力。"
description_zh: "专业文档生成专家，擅长用代码生成 PDF、幻灯片、电子表格和 Word 文档"
description_en: "Expert document generation specialist - create professional PDFs, presentations, spreadsheets, and Word docs programmatically"
version: 1.0.0
tags: [文档生成, PDF生成, PPT制作, Excel处理, Word文档, 报告生成, 数据可视化]
---

# 文档生成器 📄

> 用代码生成专业文档 — PDF、幻灯片、电子表格和报告。

---

## 核心能力

### 支持格式

| 格式 | 库/工具 | 适用场景 |
|------|---------|----------|
| **PDF** | reportlab / weasyprint / fpdf2 | 报告、发票、证书、复杂排版 |
| **PPTX** | python-pptx | 演示文稿、幻灯片、汇报材料 |
| **XLSX** | openpyxl / xlsxwriter | 数据表格、统计报表、透视表 |
| **DOCX** | python-docx | Word文档、合同、表单 |

### 核心技能

- **格式化文档**：自定义字体、颜色、页眉页脚、样式
- **数据可视化**：图表、表格、图形、配色方案
- **批量生成**：模板替换、数据驱动文档生成
- **品牌一致性**：颜色主题、字体、标志统一

---

## 触发场景

当用户提到以下内容时，应激活此 Skill：

- "生成 PDF"
- "制作 PPT" / "做幻灯片"
- "创建 Excel" / "生成表格"
- "写 Word 文档"
- "生成报告"
- "导出数据"
- "帮我做个统计表"
- "把数据做成图表"
- "制作演示文稿"

---

## 技术实现

### PDF 生成

#### 方法一：reportlab（复杂布局）

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# 创建文档
doc = SimpleDocTemplate("report.pdf", pagesize=A4)
styles = getSampleStyleSheet()

# 添加内容
elements = [
    Paragraph("标题", styles['Heading1']),
    Paragraph("正文内容", styles['BodyText']),
    Spacer(1, 12),
    Table(data, colWidths=[100, 200, 100]),
]

# 生成
doc.build(elements)
```

#### 方法二：HTML → PDF（推荐）

```python
from weasyprint import HTML, CSS

html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'SimSun', sans-serif; }
        h1 { color: #1a73e8; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background-color: #1a73e8; color: white; }
    </style>
</head>
<body>
    <h1>报告标题</h1>
    <table>
        <tr><th>列1</th><th>列2</th></tr>
        <tr><td>数据1</td><td>数据2</td></tr>
    </table>
</body>
</html>
"""

HTML(string=html_content).write_pdf("report.pdf")
```

---

### PPTX 演示文稿

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Inches(13.333)  # 16:9
prs.slide_height = Inches(7.5)

# 添加幻灯片
slide_layout = prs.slide_layouts[6]  # 空白布局
slide = prs.slides.add_slide(slide_layout)

# 添加标题
title = slide.shapes.title
title.text = "报告标题"

# 添加文本框
textbox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11), Inches(3))
tf = textbox.text_frame
p = tf.paragraphs[0]
p.text = "内容"
p.font.size = Pt(24)

# 添加图表
from pptx.chart.data import CategoryChartData
chart_data = CategoryChartData()
chart_data.categories = ['A', 'B', 'C']
chart_data.add_series('数据', (100, 200, 150))
chart = slide.shapes.add_chart(
    pptx.enum.chart.XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(1), Inches(4), Inches(10), Inches(4), chart_data
).chart

prs.save('presentation.pptx')
```

---

### XLSX 电子表格

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "数据报告"

# 设置列宽
ws.column_dimensions['A'].width = 20
ws.column_dimensions['B'].width = 15
ws.column_dimensions['C'].width = 15

# 样式定义
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF", size=12)
center_align = Alignment(horizontal="center", vertical="center")
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

# 添加表头
headers = ["项目", "数值", "占比"]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = center_align
    cell.border = thin_border

# 添加数据
data = [("A", 100, "25%"), ("B", 200, "50%"), ("C", 100, "25%")]
for row_idx, row_data in enumerate(data, 2):
    for col_idx, value in enumerate(row_data, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=value)
        cell.alignment = center_align
        cell.border = thin_border

# 创建图表
chart = BarChart()
chart.type = "col"
chart.title = "数据对比"
data_ref = Reference(ws, min_col=2, min_row=1, max_row=4)
cats_ref = Reference(ws, min_col=1, min_row=2, max_row=4)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)
ws.add_chart(chart, "E2")

wb.save("report.xlsx")
```

---

### DOCX Word 文档

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

doc = Document()

# 设置默认字体
doc.styles['Normal'].font.name = 'SimSun'
doc.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# 添加标题
title = doc.add_heading('文档标题', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# 添加正文
doc.add_paragraph('这是正文内容')

# 添加分级标题
doc.add_heading('第一章', level=1)
doc.add_heading('1.1 小节', level=2)

# 添加表格
table = doc.add_table(rows=3, cols=3)
table.style = 'Table Grid'
# 填充数据
cells = table.rows[0].cells
cells[0].text = "列1"
cells[1].text = "列2"
cells[2].text = "列3"

# 添加图片
doc.add_picture('image.png', width=Inches(5))

doc.save('document.docx')
```

---

## 常用模板

### 统计报告模板

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, Reference

def create_statistics_report(data, title, output_path):
    """生成标准统计报告"""
    wb = Workbook()
    ws = wb.active
    ws.title = "统计数据"

    # 样式定义
    title_font = Font(bold=True, size=16, color="FFFFFF")
    title_fill = PatternFill(start_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, size=11)
    header_fill = PatternFill(start_color="D9E2F3", fill_type="solid")

    # 标题行
    ws.merge_cells('A1:F1')
    ws['A1'] = title
    ws['A1'].font = title_font
    ws['A1'].fill = title_fill
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30

    # 数据表头
    headers = ["序号", "类别", "数值", "占比", "累计", "备注"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    # 填充数据...
    # 添加图表...

    wb.save(output_path)
```

### 演示文稿模板

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_presentation_template(title, slides_data, output_path):
    """生成标准演示文稿"""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 封面
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    title_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11), Inches(2))
    title_frame = title_box.text_frame
    p = title_frame.paragraphs[0]
    p.text = title
    p.font.size = Pt(48)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER

    # 内容页
    for slide_data in slides_data:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        # 添加标题和内容...
        pass

    prs.save(output_path)
```

---

## 使用指南

### 对话式任务执行

```
用户："帮我生成一个销售数据报告"
↓
激活 Skill → 了解数据结构 → 确定报告格式 → 生成文档

用户："把这份数据做成 PPT"
↓
激活 Skill → 分析数据 → 设计幻灯片结构 → 生成 PPTX

用户："导出统计表到 Excel"
↓
激活 Skill → 确定表格结构 → 添加样式和图表 → 生成 XLSX
```

### 关键原则

1. **格式优先**：根据用途选择最合适的文档格式
2. **数据驱动**：接受数据输入，生成结构化输出
3. **样式统一**：使用主题色、字体保持品牌一致性
4. **可复用**：构建模板函数，而非一次性脚本

---

### 输出文件位置

默认输出到用户桌面或当前工作目录，完成后提示用户文件位置。

---

*文档生成器 v1.0*
*用代码书写专业文档*
