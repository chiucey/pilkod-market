---
name: mineru-pdf-decomposer
description: 使用 MinerU 将 PDF 论文分解为 Markdown、JSON 等结构化格式。当用户需要解析 PDF 文档、提取论文内容、转换 PDF 为 Markdown、处理学术论文、将 PDF 转换为结构化数据、或使用 minerU 工具时使用此技能。支持表格提取、公式转换、图片提取、批量处理。
---

# MinerU PDF 论文分解技能

将 PDF 论文高效分解为 Markdown、JSON 等机器可读格式，支持表格、公式、图片提取。

## 核心能力

| 功能 | 说明 |
|------|------|
| 文本提取 | 保留文档结构（标题、段落、列表） |
| 表格提取 | 输出 CSV/HTML/Markdown 格式 |
| 公式转换 | 转换为 LaTeX/MathML |
| 图片提取 | 自动识别并提取文档中的图像 |
| 多格式输出 | Markdown、JSON、中间格式 |
| 批量处理 | 支持多文件并发处理 |

## 使用方式

### 方式一：命令行解析

```bash
# 安装 mineru
pip install -U "mineru[core]"

# 下载模型（首次使用）
python -m mineru.cli.models_download -s modelscope -m all

# 解析单个 PDF
mineru -p input.pdf -o output/

# 批量解析
mineru -p "*.pdf" -o output/

# 指定解析模式 (-m auto 自动检测)
mineru -p input.pdf -o output/ -m auto
```

### 方式二：Python API

```python
from mineru import Dataset

# 方式1：使用 Dataset 类
dataset = Dataset.from_file("paper.pdf")
result = dataset.process()

# 获取结果
md_content = result.markdown  # Markdown 格式
json_content = result.json()   # JSON 格式

# 方式2：使用更细粒度的 API
from mineru.data.dataset import PymuDocDataset

pdf_file_name = "paper.pdf"
name_without_suff = pdf_file_name.split(".")[0]
local_image_dir = "output/images"
local_md_dir = "output"

dataset = PymuDocDataset(pdf_file_name)
dataset.parse(
    method="ocr",  # 或 "auto"
    lang="ch"       # ch/en/auto
)

# 写入结果
with open(f"{local_md_dir}/{name_without_suff}.md", "w", encoding="utf-8") as f:
    f.write(dataset.piped_md)
```

### 方式三：在线 API

访问 [https://mineru.net](https://mineru.net) 使用在线版本，无需本地部署。

## 解析模式选择

| 模式 | 适用场景 | 后端 |
|------|---------|------|
| `auto` | 自动检测（推荐） | 自动选择 |
| `ocr` | 扫描件、乱码 PDF | pipeline |
| `tesseract` | 英文文档 | pipeline |
| `pdfminer` | 原生 PDF | pipeline |

## 输出格式说明

### Markdown 输出结构

```markdown
# 标题1
## 标题2

内容段落...

![图像描述](images/image_1.png)

表格内容 | 表格内容
--------|--------
单元格1 | 单元格2

数学公式：
$$
E = mc^2
$$
```

### JSON 输出结构

```json
{
  "metadata": {
    "title": "文档标题",
    "author": "作者",
    "page_count": 10
  },
  "content": [
    {
      "type": "text",
      "content": "段落内容"
    },
    {
      "type": "table",
      "content": "表格内容"
    },
    {
      "type": "image",
      "path": "images/image_1.png",
      "caption": "图像描述"
    },
    {
      "type": "formula",
      "latex": "E = mc^2"
    }
  ]
}
```

## 环境要求

| 项目 | 最低要求 | 推荐 |
|------|---------|------|
| Python | 3.10-3.13 | 3.10 |
| 内存 | 16GB | 32GB |
| GPU | 可选 | 6GB+ VRAM |
| 磁盘 | 20GB | SSD |

## 常见问题

**Q: 模型下载失败怎么办？**
```bash
# 使用国内镜像
python -m mineru.cli.models_download -s modelscope -m all

# 或手动下载后配置路径
# 修改 ~/.magic-pdf.json 中的 models-dir 字段
```

**Q: 如何处理大文件？**
```python
# 分批处理
from concurrent.futures import ProcessPoolExecutor

files = ["paper1.pdf", "paper2.pdf", ...]
with ProcessPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(process_pdf, files))
```

**Q: 如何指定输出格式？**
```bash
# 输出 Markdown
mineru -p input.pdf -o output/ --fmt md

# 输出 JSON
mineru -p input.pdf -o output/ --fmt json

# 输出所有格式
mineru -p input.pdf -o output/ --fmt all
```

## 使用示例

### 示例 1：解析学术论文

```python
from mineru import Dataset

# 解析学术论文
paper = Dataset.from_file("research_paper.pdf")
result = paper.process()

# 保存为 Markdown
with open("paper.md", "w", encoding="utf-8") as f:
    f.write(result.markdown)

# 保存为 JSON
import json
with open("paper.json", "w", encoding="utf-8") as f:
    json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
```

### 示例 2：批量处理多篇论文

```python
import os
from mineru import Dataset
from concurrent.futures import ThreadPoolExecutor

def process_paper(pdf_path):
    try:
        dataset = Dataset.from_file(pdf_path)
        result = dataset.process()

        # 生成输出路径
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = f"output/{base_name}.md"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.markdown)

        return f"成功: {pdf_path}"
    except Exception as e:
        return f"失败: {pdf_path} - {str(e)}"

# 批量处理
pdf_files = [f for f in os.listdir("papers") if f.endswith(".pdf")]
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_paper, pdf_files))

for r in results:
    print(r)
```

### 示例 3：提取表格并导出

```python
from mineru.data.dataset import PymuDocDataset

dataset = PymuDocDataset("paper.pdf")
dataset.parse(method="auto")

# 提取所有表格
tables = []
for block in dataset.content_list:
    if block.get("type") == "table":
        tables.append(block["content"])

# 导出为 CSV
import csv
with open("tables.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for table in tables:
        for row in table.split("\n"):
            writer.writerow(row.split("|"))
```