#!/usr/bin/env python3
"""
reader.py — 多格式文档读取模块
==============================
统一入口：read_document(path) → str
支持格式：.md .txt .docx .xlsx .xls .pdf .pptx .csv .html

每个格式的读取器均为独立函数，extract_metadata() 额外提取文档元信息。
"""

import os
import re
from pathlib import Path
from typing import Optional


# ============================================================================
# 主入口
# ============================================================================

def read_document(path: str) -> dict:
    """
    读取任意支持格式的文档，返回结构化结果。

    返回：
    {
        "text": str,        # 纯文本内容
        "meta": dict,       # 元信息
        "error": str|None   # 若失败，包含错误信息
    }
    """
    p = Path(path)
    if not p.exists():
        return {"text": "", "meta": {}, "error": f"文件不存在: {path}"}

    ext = p.suffix.lower()
    reader_map = {
        ".md":    _read_markdown,
        ".txt":   _read_text,
        ".csv":   _read_csv,
        ".html":  _read_html,
        ".xlsx":  _read_excel,
        ".xls":   _read_excel,
        ".docx":  _read_docx,
        ".pptx":  _read_pptx,
        ".pdf":   _read_pdf,
    }

    reader = reader_map.get(ext)
    if not reader:
        return {
            "text": f"[不支持的文件格式: {ext}]",
            "meta": {"ext": ext},
            "error": None
        }

    try:
        text = reader(p)
        meta = _extract_metadata(p, text)
        return {"text": text, "meta": meta, "error": None}
    except Exception as e:
        return {"text": "", "meta": {}, "error": str(e)}


# ============================================================================
# 各格式读取器
# ============================================================================

def _read_markdown(p: Path) -> str:
    """读取 Markdown 文件，保留结构信息"""
    return p.read_text(encoding="utf-8")


def _read_text(p: Path) -> str:
    """读取纯文本文件"""
    for enc in ("utf-8", "gbk", "gb2312", "utf-16"):
        try:
            return p.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return p.read_text(encoding="utf-8", errors="replace")


def _read_csv(p: Path) -> str:
    """读取 CSV 文件"""
    import csv
    lines = []
    with open(p, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            lines.append(" | ".join(row))
    return "\n".join(lines)


def _read_html(p: Path) -> str:
    """读取 HTML 文件（去除标签，保留文本）"""
    from html.parser import HTMLParser

    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.texts = []
            self.skip_tags = {"script", "style", "head"}

        def handle_data(self, data):
            if data.strip():
                self.texts.append(data.strip())

        def handle_starttag(self, tag, attrs):
            pass

        def get_text(self):
            return "\n".join(self.texts)

    html = p.read_text(encoding="utf-8", errors="replace")
    parser = TextExtractor()
    try:
        parser.feed(html)
        return parser.get_text()
    except Exception:
        # fallback: 简单去除标签
        text = re.sub(r'<[^>]+>', '', html)
        return "\n".join(t for t in text.split() if t)


def _read_excel(p: Path) -> str:
    """读取 Excel 文件（.xlsx / .xls）"""
    try:
        import openpyxl
    except ImportError:
        return "[需要安装 openpyxl: pip install openpyxl]"

    wb = openpyxl.load_workbook(p, data_only=True)
    lines = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        lines.append(f"\n{'='*60}")
        lines.append(f"Sheet: {sheet_name}")
        lines.append('='*60)

        for row in ws.iter_rows(values_only=True):
            if any(cell is not None for cell in row):
                cells = [str(c) if c is not None else "" for c in row]
                lines.append(" | ".join(cells))

    return "\n".join(lines)


def _read_docx(p: Path) -> str:
    """读取 Word .docx 文件"""
    try:
        from docx import Document
    except ImportError:
        return "[需要安装 python-docx: pip install python-docx]"

    doc = Document(p)
    lines = []

    # 读取正文段落
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            lines.append(text)

    # 读取表格
    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                lines.append(" | ".join(cells))

    return "\n".join(lines)


def _read_pptx(p: Path) -> str:
    """读取 PowerPoint .pptx 文件"""
    try:
        from pptx import Presentation
    except ImportError:
        return "[需要安装 python-pptx: pip install python-pptx]"

    prs = Presentation(p)
    lines = []

    for slide_num, slide in enumerate(prs.slides, 1):
        lines.append(f"\n--- Slide {slide_num} ---")
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                lines.append(shape.text.strip())
            # 读取表格
            if shape.has_table:
                for row in shape.table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    if any(cells):
                        lines.append(" | ".join(cells))

    return "\n".join(lines)


def _read_pdf(p: Path) -> str:
    """读取 PDF 文件（优先 pdfplumber，降级到 pypdf）"""
    # 优先用 pdfplumber（表格支持更好）
    try:
        import pdfplumber
        parts = []
        with pdfplumber.open(p) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    parts.append(t)
                # 尝试提取表格
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        cells = [str(c) if c else "" for c in row]
                        if any(cells):
                            parts.append(" | ".join(cells))
        return "\n\n".join(parts)
    except ImportError:
        pass

    # 降级到 pypdf
    try:
        from pypdf import PdfReader
    except ImportError:
        return "[需要安装 pypdf 或 pdfplumber]"

    reader = PdfReader(p)
    parts = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            parts.append(t)
    return "\n\n".join(parts)


# ============================================================================
# 元信息提取
# ============================================================================

def _extract_metadata(p: Path, text: str) -> dict:
    """从文本中提取文档元信息"""
    meta = {
        "filename": p.name,
        "size_kb": p.stat().st_size // 1024,
        "char_count": len(text),
        "line_count": text.count("\n") + 1,
    }

    # 尝试提取版本号
    version_match = re.search(r'v?(\d+[.]\d+[.]\d+)|版本[：:\s]*(\d+\.\d+)', text, re.IGNORECASE)
    if version_match:
        meta["version"] = version_match.group(1) or version_match.group(2)

    # 尝试提取日期
    date_match = re.search(r'(20\d{2}[-/年]\d{1,2}[-/月]\d{0,2}[日]?)', text)
    if date_match:
        meta["date"] = date_match.group(1)

    # 尝试提取产品名（第一个标题行或第一行）
    title_match = re.search(r'^#\s+(.+)$|^(.{5,50})$', text, re.MULTILINE)
    if title_match:
        meta["title"] = (title_match.group(1) or title_match.group(2) or "").strip()

    # 章节数量估计
    section_matches = re.findall(r'^#{1,6}\s+', text, re.MULTILINE)
    meta["section_count"] = len(section_matches)

    return meta


# ============================================================================
# CLI 测试
# ============================================================================

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python3 reader.py <文件路径>")
        sys.exit(1)

    result = read_document(sys.argv[1])
    print(f"=== 文件信息 ===")
    for k, v in result["meta"].items():
        print(f"  {k}: {v}")
    print(f"\n=== 正文（前2000字符）===")
    print(result["text"][:2000])
    if result["error"]:
        print(f"\n❌ 错误: {result['error']}")
