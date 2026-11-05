# PaddleStructure 使用指南

## 概述

PaddleStructure 是 PaddleOCR 的高级版本，提供了表格识别、版面分析、公式识别等高级功能。

## 安装

```bash
# 基础安装
pip install paddleocr paddlepaddle paddlestructure

# GPU 版本
pip install paddleocr paddlepaddle-gpu paddlestructure
```

## 核心功能

### 1. 表格识别

PaddleStructure 支持高精度的表格识别，能够提取表格的结构和内容。

**使用方法**：

```python
from paddlestructure import PaddleStructure

# 初始化表格引擎
table_engine = PaddleStructure(
    show_log=False,
    image_orientation=True,
    table=True,      # 启用表格识别
    ocr=True,
    layout=False,    # 表格模式不需要版面分析
    structure_version='PP-StructureV3'  # 升级到 V3 版本
)

# 识别表格
result = table_engine("table_image.jpg")

# 解析结果
for item in result:
    if 'res' in item:
        res = item['res']
        if res.get('type') == 'table':
            html = res.get('html', '')
            print(html)  # HTML 格式的表格
```

**结果格式**：

```python
{
    "success": True,
    "tables": [
        {
            "rows": [
                ["姓名", "年龄", "职业"],
                ["张三", "25", "工程师"],
                ["李四", "30", "设计师"]
            ],
            "html": "<table>...</table>",
            "bbox": [x_min, y_min, x_max, y_max],
            "confidence": 0.98
        }
    ],
    "table_count": 1
}
```

### 2. 版面分析

PaddleStructure 支持智能版面分析，能够识别文档的各个区域。

**使用方法**：

```python
from paddlestructure import PaddleStructure

# 初始化版面分析引擎
layout_engine = PaddleStructure(
    show_log=False,
    image_orientation=True,
    layout=True,     # 启用版面分析
    table=True,      # 同时支持表格
    ocr=True,
    structure_version='PP-StructureV3'  # 升级到 V3 版本
)

# 分析版面
result = layout_engine("document_image.jpg")

# 解析结果
for item in result:
    if 'res' in item:
        res = item['res']
        print(f"类型: {res.get('type')}")
        print(f"文本: {res.get('text')}")
        print(f"位置: {res.get('bbox')}")
```

**支持的版面类型**：

- `title`: 标题
- `text`: 正文文本
- `header`: 页眉
- `footer`: 页脚
- `table`: 表格
- `figure`: 图片
- `list`: 列表
- `formula`: 公式

**结果格式**：

```python
{
    "success": True,
    "regions": [
        {
            "type": "title",
            "text": "文档标题",
            "bbox": [x_min, y_min, x_max, y_max],
            "confidence": 0.99
        },
        {
            "type": "text",
            "text": "正文内容...",
            "bbox": [x_min, y_min, x_max, y_max],
            "confidence": 0.97
        }
    ],
    "regions_by_type": {
        "title": [...],
        "text": [...]
    }
}
```

## 在 Web Automation Skill 中的使用

### 1. 表格识别

使用 `ocr_service.py` 的 `extract_table` 方法：

```python
from scripts.ocr_service import OCRService

# 初始化 OCR 服务
ocr = OCRService()

# 提取表格
result = ocr.extract_table("table_image.jpg")

if result["success"]:
    for i, table in enumerate(result["tables"]):
        print(f"表格 {i+1}:")
        for row in table["rows"]:
            print("  |".join(row))
```

### 2. 版面分析

使用 `page_parser.py` 的 `analyze_layout` 方法：

```python
from scripts.page_parser import PageParser

# 初始化页面解析器
parser = PageParser()

# 分析版面
result = parser.analyze_layout("document_image.jpg")

if result["success"]:
    for region_type, regions in result["regions_by_type"].items():
        print(f"{region_type}: {len(regions)} 个")
        for region in regions:
            print(f"  {region['text']}")
```

## 命令行使用

### 表格识别

```bash
python scripts/ocr_service.py table_image.jpg --table --output result.json
```

### 版面分析

```bash
python scripts/page_parser.py document_image.jpg --type layout --output result.json
```

### 可视化

```bash
# 可视化版面分析结果
python scripts/page_parser.py document_image.jpg --visualize
```

## 性能优化

### GPU 加速

```python
# 使用 GPU 加速
ocr = OCRService(use_gpu=True)
parser = PageParser(use_gpu=True)
```

### 模型缓存

首次运行时会自动下载模型，后续运行会使用缓存的模型。

### 批量处理

```python
# 批量识别表格
images = ["table1.jpg", "table2.jpg", "table3.jpg"]
for image in images:
    result = ocr.extract_table(image)
    print(f"{image}: {result['table_count']} 个表格")
```

## 注意事项

### 1. 模型下载

首次运行时会自动下载模型文件（约 200MB），需要网络连接。

### 2. 内存占用

PaddleStructure 比基础 PaddleOCR 需要更多内存，建议至少 4GB 可用内存。

### 3. 图片质量

- 建议：清晰度高、对比度好的图片
- 避免：模糊、倾斜、光线不均的图片

### 4. 表格复杂度

- 简单表格：识别准确率高（95%+）
- 复杂表格：包含合并单元格、嵌套表格等，识别准确率可能下降

## 高级功能

### 1. 表格结构识别

PaddleStructure 不仅能提取文字，还能识别表格的结构：

```python
result = ocr.extract_table("complex_table.jpg")

for table in result["tables"]:
    html = table["html"]
    # HTML 包含完整的表格结构（合并单元格等）
    print(html)
```

### 2. 多页文档

对于多页文档（如 PDF），需要先转换为图片：

```python
from scripts.mineru_service import MinerUService
from scripts.ocr_service import OCRService

# 将 PDF 转换为图片
mineru = MinerUService()
images = mineru.pdf_to_images("document.pdf")

# 识别每一页
ocr = OCRService()
for i, image in enumerate(images):
    result = ocr.extract_table(image)
    print(f"第 {i+1} 页: {result['table_count']} 个表格")
```

### 3. 元素检测

结合版面分析和元素检测：

```python
from scripts.page_parser import PageParser

parser = PageParser()

# 获取所有表格
layout = parser.analyze_layout("document.jpg")
tables = layout["regions_by_type"].get("table", [])

for table in tables:
    print(f"表格位置: {table['bbox']}")
    print(f"表格内容: {table['text'][:50]}...")
```

## 常见问题

### Q1: PaddleStructure 和 PaddleOCR 有什么区别？

A: PaddleStructure 是 PaddleOCR 的高级版本，增加了表格识别、版面分析等高级功能。

### Q2: 表格识别准确率如何？

A: 对于标准表格，准确率可达 95%+；复杂表格（合并单元格、嵌套表格）准确率略低。

### Q3: 版面分析支持哪些文档类型？

A: 支持论文、报告、合同、发票等多种文档类型。

### Q4: 如何提高识别准确率？

A:
- 使用高质量的图片（分辨率、对比度）
- 图片预处理（去噪、矫正倾斜）
- 使用 GPU 加速
- 调整模型参数

## 参考资料

- [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleStructure 文档](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/ppstructure/docs/)
- [PP-StructureV2 模型介绍](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/ppstructure/docs/models_list.md)

## 总结

PaddleStructure 提供了强大的表格识别和版面分析能力，使用简单，效果优秀。在 Web Automation Skill 中，这些功能已经被集成到 `ocr_service.py` 和 `page_parser.py` 中，可以直接使用。
