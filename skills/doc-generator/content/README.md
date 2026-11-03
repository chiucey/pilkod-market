# 📄 文档生成器 - 使用说明

## 快速开始

### 安装依赖

```bash
# PDF 生成
pip install reportlab weasyprint fpdf2

# PPT 制作
pip install python-pptx

# Excel 处理
pip install openpyxl xlsxwriter

# Word 文档
pip install python-docx

# 全部安装
pip install reportlab weasyprint python-pptx openpyxl python-docx
```

## 使用方式

### 方式一：直接对话

向 AI 描述你的需求：

- "生成一个 PDF 报告"
- "制作一个数据分析 PPT"
- "创建 Excel 统计表"
- "导出 Word 文档"

### 方式二：编程调用

```python
from doc_generator import create_pdf_report, create_excel_stats

# 生成 PDF
create_pdf_report(data, title="年度报告", output="report.pdf")

# 生成 Excel
create_excel_stats(data, title="销售数据", output="sales.xlsx")
```

## 示例场景

### 1. 财务报告
```
输入：月度销售数据
输出：PDF 报告（含图表、汇总表）
```

### 2. 数据分析
```
输入：统计数据
输出：Excel 表格 + 图表 + PPT 演示
```

### 3. 批量文档
```
输入：数据列表 + 模板
输出：批量生成的个性化文档
```

## 格式选择指南

| 需求 | 推荐格式 |
|------|----------|
| 正式报告/存档 | PDF |
| 演示汇报 | PPTX |
| 数据分析/计算 | XLSX |
| 需要编辑修改 | DOCX |
| 打印/正式文档 | PDF |

## 技术支持

- **Python 版本**：3.8+
- **操作系统**：Windows / macOS / Linux
- **中文支持**：需安装中文字体

### 中文字体设置

```python
# PDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))

# Excel
from openpyxl.styles import Font
cell.font = Font(name='宋体')

# Word
doc.styles['Normal'].font.name = 'SimSun'
```

---

*有问题？随时告诉我你的需求！*
