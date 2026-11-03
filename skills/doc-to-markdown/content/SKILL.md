---
name: doc-to-markdown
description: 多格式文档转Markdown工具。当用户要求转换文档格式、提取PDF/Word/PPT/Excel内容、将图片转为文字、网页内容抓取、文档结构化处理时使用。触发短语包括：文档转Markdown、转PDF为Markdown、Word转Markdown、提取文档内容、OCR识别、图片转文字、网页内容提取等。
---

# 多格式文档转Markdown转换器

将各种格式的文档转换为结构化的Markdown格式，支持PDF、Word、PPT、Excel、图片OCR、网页提取等多种输入格式。

## 核心功能

- **文档转换**: PDF、Word (DOCX)、PowerPoint (PPTX)、Excel (XLSX)
- **文本处理**: TXT、Markdown直接转换
- **图片OCR**: JPG、PNG、GIF、BMP、WebP自动识别文字
- **网页抓取**: URL链接自动提取正文内容
- **数据格式**: JSON格式化输出

## 架构设计

### 后端处理器模块

每个文件格式对应独立的处理器类，继承自 `BaseProcessor`:

```
app/processors/
├── base.py           # 基类，定义接口
├── txt_processor.py  # 文本文件
├── pdf_processor.py  # PDF文档
├── docx_processor.py # Word文档
├── pptx_processor.py # PowerPoint
├── xlsx_processor.py # Excel表格
├── image_processor.py # 图片OCR
├── json_processor.py # JSON数据
├── web_processor.py  # 网页提取
└── audio_processor.py # 音视频转录
```

### API端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/upload` | POST | 上传并处理多个文件 |
| `/api/extract-url` | POST | 从URL提取网页内容 |
| `/api/convert-text` | POST | 文本转Markdown |
| `/api/supported-formats` | GET | 获取支持的格式列表 |
| `/api/health` | GET | 健康检查 |

### 前端交互

- 拖拽上传文件
- 实时Markdown预览
- 一键复制/下载
- 支持批量处理

## 实现步骤

### 1. 创建FastAPI应用结构

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="文档转Markdown工具")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 实现处理器基类

```python
# app/processors/base.py
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    supported_extensions = []

    @abstractmethod
    def process(self, file_path: str, **kwargs) -> dict:
        """返回 {"success": bool, "markdown": str, "metadata": dict}"""
        pass
```

### 3. 各格式处理器实现

#### PDF处理器
使用 `pdfplumber` 提取文本和表格结构。

#### Word处理器
使用 `python-docx` 提取段落、标题、列表、表格。

#### 图片OCR
使用 `pytesseract` 进行文字识别，支持中英文。

#### 网页提取
使用 `beautifulsoup4` + `html2text` 提取正文。

## 依赖清单

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6
pdfplumber>=0.10.3
python-docx>=1.1.0
python-pptx>=0.6.23
openpyxl>=3.1.2
Pillow>=10.2.0
pytesseract>=0.3.10
beautifulsoup4>=4.12.3
requests>=2.31.0
html2text>=2024.2.26
```

## 部署说明

### 本地运行
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### OCR支持
安装Tesseract OCR引擎:
- Ubuntu: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
- macOS: `brew install tesseract tesseract-lang`
- Windows: 下载安装包并添加到PATH

## 质量标准

- 所有处理器返回一致的响应格式
- 错误处理包含友好的中文提示
- 保留文档原有结构（标题层级、列表、表格）
- 支持UTF-8编码，处理中英文内容
