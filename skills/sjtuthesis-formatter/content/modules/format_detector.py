"""
Format Detector — Automatic Input Format Detection
===================================================

Detects the format of an uploaded file (.docx, .tex, .md, .txt, .pdf),
extracts plain text content, and provides format metadata.
Supports batch detection for multiple files and merge scenarios.
"""

import os
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set


class FileFormat:
    """Supported file format constants."""
    DOCX = "docx"
    TEX = "tex"
    MD = "md"
    TXT = "txt"
    PDF = "pdf"
    HTML = "html"
    RTF = "rtf"
    UNKNOWN = "unknown"

    # Extension map
    EXT_MAP = {
        ".docx": DOCX, ".doc": "doc_binary",
        ".tex": TEX, ".ltx": TEX,
        ".md": MD, ".markdown": MD,
        ".txt": TXT,
        ".pdf": PDF,
        ".html": HTML, ".htm": HTML,
        ".rtf": RTF,
    }


@dataclass
class FormatInfo:
    """Detected format information for a file."""
    file_path: str
    format: str = FileFormat.UNKNOWN
    encoding: str = "utf-8"
    char_count: int = 0
    word_count_approx: int = 0
    line_count: int = 0
    is_mergeable: bool = True
    warnings: List[str] = field(default_factory=list)
    sections_detected: int = 0
    has_track_changes: bool = False
    has_comments: bool = False
    is_scanned_pdf: bool = False


# ── Detection ─────────────────────────────────────────────────────

def detect_format(file_path: str) -> FormatInfo:
    """Detect the format and extract basic info from a file.

    Supports: .docx, .tex, .md, .txt, .pdf, .html
    """
    path = Path(file_path)
    info = FormatInfo(file_path=file_path)

    if not path.exists():
        info.warnings.append(f"文件不存在: {file_path}")
        return info

    ext = path.suffix.lower()
    info.format = FileFormat.EXT_MAP.get(ext, FileFormat.UNKNOWN)

    # Try to detect encoding
    raw_bytes = path.read_bytes()
    info.encoding = _detect_encoding(raw_bytes)

    try:
        if info.format == FileFormat.DOCX:
            _analyze_docx(path, info, raw_bytes)
        elif info.format == FileFormat.TEX:
            _analyze_tex(path, info)
        elif info.format == FileFormat.MD:
            _analyze_md(path, info)
        elif info.format == FileFormat.PDF:
            _analyze_pdf(path, info)
        elif info.format == FileFormat.TXT:
            _analyze_txt(path, info)
        else:
            # Try as text
            _analyze_txt(path, info)
            info.is_mergeable = False
    except Exception as e:
        info.warnings.append(f"分析异常: {e}")

    return info


def _detect_encoding(raw_bytes: bytes) -> str:
    """Detect text encoding from bytes."""
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        return "utf-8-sig"
    try:
        raw_bytes.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        try:
            raw_bytes.decode("gbk")
            return "gbk"
        except UnicodeDecodeError:
            return "latin-1"


def _analyze_docx(path: Path, info: FormatInfo, raw_bytes: bytes):
    """Analyze a .docx file."""
    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            # Track changes detection
            if "word/comments.xml" in names:
                info.has_comments = True
                info.warnings.append("文档包含批注")
            if "word/document.xml" in names:
                doc_xml = zf.read("word/document.xml").decode("utf-8", errors="ignore")
                if "<w:ins" in doc_xml or "<w:del" in doc_xml:
                    info.has_track_changes = True
                    info.warnings.append("文档包含修订痕迹")
            # Count sections
            from modules.helpers import detect_heading_level
            text = _extract_docx_text(names, zf)
            info.char_count = len(text)
            info.word_count_approx = len(text.split())
            info.line_count = text.count("\n") + 1
            # Count heading-like lines
            for line in text.split("\n"):
                if detect_heading_level(line.strip()):
                    info.sections_detected += 1
    except zipfile.BadZipFile:
        info.warnings.append("无效的 .docx 文件")


def _extract_docx_text(names: List[str], zf: zipfile.ZipFile) -> str:
    """Extract text from .docx XML parts."""
    text_parts = []
    for name in sorted(names):
        if name.startswith("word/header") or name.startswith("word/footer"):
            continue
        if name.endswith(".xml"):
            try:
                xml = zf.read(name).decode("utf-8", errors="ignore")
                # Extract text between <w:t> tags
                texts = re.findall(r'<w:t[^>]*>(.*?)</w:t>', xml)
                text_parts.extend(texts)
            except Exception:
                pass
    return "\n".join(text_parts)


def _analyze_tex(path: Path, info: FormatInfo):
    """Analyze a .tex file."""
    try:
        text = path.read_text(info.encoding, errors="ignore")
    except Exception:
        text = path.read_text("utf-8", errors="ignore")

    info.char_count = len(text)
    info.line_count = text.count("\n") + 1
    info.word_count_approx = len(text.split())

    # Count sections
    info.sections_detected = len(re.findall(r'\\section\{', text))
    info.sections_detected += len(re.findall(r'\\chapter\{', text))

    # Check for common issues
    if "\\include{" in text or "\\input{" in text:
        info.warnings.append("包含外部文件 (\\include/\\input)，需合并后处理")


def _analyze_md(path: Path, info: FormatInfo):
    """Analyze a .md file."""
    try:
        text = path.read_text(info.encoding, errors="ignore")
    except Exception:
        text = path.read_text("utf-8", errors="ignore")

    info.char_count = len(text)
    info.line_count = text.count("\n") + 1
    info.word_count_approx = len(text.split())

    # Count headings
    info.sections_detected = len(re.findall(r'^#{1,6}\s', text, re.MULTILINE))

    # Check for Markdown images
    images = re.findall(r'!\[.*?\]\(.*?\)', text)
    if images:
        info.warnings.append(f"包含 {len(images)} 个 Markdown 图片引用")


def _analyze_pdf(path: Path, info: FormatInfo):
    """Analyze a PDF file."""
    raw = path.read_bytes()
    info.char_count = len(raw)

    # Detect scanned PDF (no text layer)
    # Simple heuristic: if raw text extraction yields very little
    try:
        text = raw.decode("latin-1")
        # Count printable ASCII as a proxy for text content
        printable = sum(1 for c in text if c.isprintable())
        ratio = printable / len(text) if len(text) > 0 else 0
        if ratio < 0.3:  # Very little printable text
            info.is_scanned_pdf = True
            info.warnings.append("检测为扫描件PDF，建议先进行OCR识别")
        else:
            info.warnings.append("PDF格式，文本提取可能不完整")
    except Exception:
        info.is_scanned_pdf = True
        info.warnings.append("无法提取PDF文本，建议先进行OCR识别")

    info.is_mergeable = False


def _analyze_txt(path: Path, info: FormatInfo):
    """Analyze a plain text file."""
    try:
        text = path.read_text(info.encoding, errors="ignore")
    except Exception:
        text = path.read_text("utf-8", errors="ignore")

    info.char_count = len(text)
    info.line_count = text.count("\n") + 1
    info.word_count_approx = len(text.split())

    # Detect if it looks like a paper (has sections)
    from modules.helpers import detect_heading_level
    for line in text.split("\n"):
        if detect_heading_level(line.strip()):
            info.sections_detected += 1


# ─── Batch detection ──────────────────────────────────────────────

def detect_batch(file_paths: List[str]) -> List[FormatInfo]:
    """Detect formats for multiple files at once."""
    return [detect_format(p) for p in file_paths]


def format_summary(info: FormatInfo) -> str:
    """Generate a human-readable format summary."""
    lines = [
        f"📄 {info.file_path}",
        f"  格式: {info.format.upper()}",
        f"  字符数: {info.char_count:,}",
        f"  行数: {info.line_count}",
        f"  检测到章节: {info.sections_detected}",
    ]
    if info.has_track_changes:
        lines.append("  ⚠ 包含修订痕迹")
    if info.has_comments:
        lines.append("  ⚠ 包含批注")
    if info.is_scanned_pdf:
        lines.append("  ⚠ 扫描件PDF，建议OCR")
    if info.warnings:
        for w in info.warnings:
            lines.append(f"  ! {w}")
    return "\n".join(lines)
