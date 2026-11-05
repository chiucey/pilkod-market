# 代码模板参考

本文档包含智能文件处理助手的详细实现代码模板。

## 1. PDF 处理模板

```python
import PyPDF2
from pdfplumber import pdfplumber
import pandas as pd

def process_pdf(file_path, task="extract_text"):
    """
    处理PDF文件
    task: extract_text | extract_tables | extract_images | metadata
    """
    if task == "extract_text":
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n\n"
        return text

    elif task == "extract_tables":
        tables = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                for table in page_tables:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    tables.append(df)
        return tables

    elif task == "metadata":
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            return reader.metadata
```

## 2. 图片处理模板

```python
from PIL import Image, ExifTags
import pytesseract
import os

def process_image(file_path, task="ocr", lang="chi_sim+eng"):
    """
    处理图片文件
    task: ocr | exif | convert | compress
    """
    img = Image.open(file_path)

    if task == "ocr":
        gray = img.convert('L')
        text = pytesseract.image_to_string(gray, lang=lang)
        return text.strip()

    elif task == "exif":
        exif = img._getexif()
        if exif:
            return {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
        return {}

    elif task == "convert":
        output_path = file_path.rsplit('.', 1)[0] + '_converted.png'
        img.save(output_path, 'PNG')
        return output_path

    elif task == "compress":
        output_path = file_path.rsplit('.', 1)[0] + '_compressed.jpg'
        img.save(output_path, 'JPEG', quality=85, optimize=True)
        return output_path
```

## 3. Office 文档处理模板

```python
from docx import Document
import pandas as pd

def process_docx(file_path, task="extract"):
    """处理Word文档"""
    doc = Document(file_path)

    if task == "extract":
        content = []
        for para in doc.paragraphs:
            if para.text.strip():
                content.append({
                    'text': para.text,
                    'style': para.style.name
                })
        return content

    elif task == "to_markdown":
        md = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            if para.style.name.startswith('Heading'):
                level = int(para.style.name.replace('Heading ', ''))
                md.append(f"{'#' * level} {text}")
            else:
                md.append(text)
        return '\n\n'.join(md)

def process_excel(file_path, task="extract"):
    """处理Excel文件"""
    xl = pd.ExcelFile(file_path)

    if task == "extract":
        data = {}
        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            data[sheet_name] = df.to_dict('records')
        return data

    elif task == "to_csv":
        output_files = []
        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            csv_path = f"output/{sheet_name}.csv"
            df.to_csv(csv_path, index=False)
            output_files.append(csv_path)
        return output_files
```

## 4. 批量处理模板

```python
import os
import re
from pathlib import Path

def batch_rename(directory, pattern, replacement, dry_run=True):
    """
    批量重命名文件
    pattern: 正则匹配模式
    replacement: 替换字符串
    """
    changes = []
    for file in Path(directory).iterdir():
        if file.is_file():
            new_name = re.sub(pattern, replacement, file.name)
            if new_name != file.name:
                changes.append((file.name, new_name))
                if not dry_run:
                    file.rename(file.parent / new_name)
    return changes

def batch_process(directory, file_types, operation):
    """
    批量处理文件
    operation: 具体操作函数
    """
    results = []
    for file in Path(directory).glob('*'):
        if file.suffix.lower() in file_types:
            try:
                result = operation(file)
                results.append({'file': file.name, 'status': 'success', 'result': result})
            except Exception as e:
                results.append({'file': file.name, 'status': 'error', 'error': str(e)})
    return results
```

## 5. 输出规范模板

```python
def create_response(success, file_type, task, content=None, files=None, metadata=None, error=None):
    """统一响应格式"""
    return {
        "success": success,
        "file_type": file_type,
        "task": task,
        "content": content,
        "files": files or [],
        "metadata": metadata or {},
        "error": error
    }
```

## 6. 文件类型映射表

| 类型 | 扩展名 | 处理模块 | 主要工具 |
|-----|-------|---------|---------|
| PDF | .pdf | pdf_processor | PyPDF2, pdfplumber |
| 图片 | .jpg/.png/.tiff | image_processor | PIL, pytesseract |
| Word | .doc/.docx | docx_processor | python-docx |
| Excel | .xls/.xlsx | excel_processor | openpyxl, pandas |
| 压缩包 | .zip/.rar/.7z | archive_processor | zipfile, py7zr |
| 文本 | .txt/.md/.json | text_processor | 内置IO |
| 代码 | .py/.js/.html | code_processor | ast, re |
