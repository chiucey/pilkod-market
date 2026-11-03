---
name: imageOCR-to-table
description: 从用户上传的图片中识别文本内容（OCR），并将数据填入用户上传的Excel表格模板。当用户要求识别图片内容填入表格、从截图提取数据到Excel、或上传图片和表格进行数据录入时使用。
---

# 图片OCR数据提取技能

## 功能概述

识别用户上传的图片（截图、文档扫描件等）中的文本内容，按照用户上传的Excel表格模板格式，将数据填入相应单元格。

## 用户交互要求

**必须提示用户上传**：
1. **Excel表格模板文件** - 需要填写数据的表格（支持 .xlsx, .xls 格式）
2. **图片文件** - 至少1张，包含需要提取的数据（支持 .jpg, .jpeg, .png 格式）

## 工作流程

### 步骤1：读取Excel表格模板

使用 Python openpyxl 读取用户上传的表格：
```python
import openpyxl
wb = openpyxl.load_workbook('用户上传的表格.xlsx')
ws = wb.active

# 获取表头字段（第一行）
headers = []
for cell in ws[1]:
    headers.append(cell.value)

print("表格字段:", headers)
```

### 步骤2：识别图片内容

使用 `images_understand` 工具识别图片文本：
- 每次最多处理10张图片
- 提示词应要求提取所有可见的文本字段
- 对于表格类图片，要求以结构化方式输出字段名和对应值

示例提示词：
```
请详细识别这张图片中的所有文本内容和数据字段。请列出所有可见的字段名称及其对应的值。
```

### 步骤3：字段映射

将图片识别的数据与Excel表头进行智能匹配：
1. 读取Excel表头字段
2. 根据字段名称相似度进行匹配
3. 无法匹配的字段可询问用户确认

### 步骤4：填充数据并保存

```python
import openpyxl
wb = openpyxl.load_workbook('用户上传的表格.xlsx')
ws = wb.active

# 从第2行开始填充数据（保留表头）
for row_idx, record in enumerate(data_list, start=2):
    for col_idx, header in enumerate(headers, start=1):
        if header in record:
            ws.cell(row=row_idx, column=col_idx).value = record[header]

wb.save('填写完成的表格.xlsx')
```

## 支持的文件格式

### 图片格式
- JPG / JPEG
- PNG
- WebP
- BMP

### 表格格式
- Excel (.xlsx)
- Excel 97-2003 (.xls)

## 注意事项

1. **图片质量**：确保图片清晰，光照均匀，无严重遮挡
2. **表格结构**：建议用户使用规范的表格模板，第一行为表头
3. **多图处理**：可一次处理多张图片，数据按顺序填入后续行
4. **数据类型**：数字、日期等会自动转换格式
5. **空值处理**：图片中无法识别的字段留空

## 输出

生成填写完成的 Excel 文件，保留原始表格的样式和格式。
