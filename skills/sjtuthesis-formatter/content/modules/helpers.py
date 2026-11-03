"""
Shared utility functions used across modules.
Extracted to eliminate duplication (e.g., heading detection in both renderers).
"""

import re
from typing import Optional


HAO_TO_PT = {
    "初号": 42, "小初": 36, "一号": 26, "小一": 24,
    "二号": 22, "小二": 18, "三号": 16, "小三": 15,
    "四号": 14, "小四": 12, "五号": 10.5, "小五": 9,
    "六号": 7.5, "小六": 6.5,
}


def hao_to_pt(hao: str) -> float:
    """Convert Chinese font size name to points."""
    return HAO_TO_PT.get(hao, 12)


# ── Heading detection (shared between word and latex renderers) ───

def detect_heading_level(line: str, numbering_system: str = "阿拉伯数字") -> int:
    """Detect heading level from a line of text.

    Returns:
        0 = body text (not a heading)
        1 = chapter-level (章)
        2 = section-level (节)
        3 = subsection-level (子节)

    Supports both Arabic-number and Chinese-ordinal systems.
    Also detects semantic headings like "摘要", "关键词", "引言", etc.
    """
    stripped = line.strip()
    if not stripped:
        return 0

    # ── Semantic heading detection ──────────────────────────────
    semantic_level = _detect_semantic_heading(stripped)
    if semantic_level:
        return semantic_level

    # ── Number-based detection ──────────────────────────────────
    if numbering_system == "中文序号":
        # 一、二、三、... → Level 1
        if re.match(r"^[一二三四五六七八九十百千]+[、．]", stripped):
            return 1
        # （一）（二）... → Level 2
        if re.match(r"^（[一二三四五六七八九十百千]+）", stripped):
            return 2
        # 1. 2. ... in Chinese context → Level 3
        if re.match(r"^\d+[、．]", stripped):
            return 3
    else:
        # 第一章 or 1. → Level 1
        if re.match(r"^((第[一二三四五六七八九十百千]+章)|(\d+[\.．]))\s", stripped):
            return 1
        # 1.1 → Level 2
        if re.match(r"^\d+[\.．]\d+(\s|$)", stripped):
            return 2
        # 1.1.1 → Level 3
        if re.match(r"^\d+[\.．]\d+[\.．]\d+(\s|$)", stripped):
            return 3
        # (1) type → Level 4 (not a heading for our purposes)
        if re.match(r"^\(\d+\)", stripped):
            return 0

    return 0


def _detect_semantic_heading(text: str) -> int:
    """Detect headings by semantic content (not just numbering).

    Recognizes common Chinese academic paper headings.
    """
    # Exact match patterns for common headings
    semantic_headings_l1 = {
        "摘要", "abstract", "ABSTRACT",
        "目录", "目  录",
        "致谢", "致  谢",
        "参考文献", "參考文獻",
        "附录", "附  录", "附录a", "附录b", "附录c",
    }

    semantic_headings_l2 = {
        "引言", "前言", "绪论", "绪  论",
        "结论", "结  论",
        "总结", "总  结",
        "本章小结",
        "研究背景", "背景",
        "相关工作", "related work",
        "研究方法", "方法",
        "实验结果", "实验",
        "讨论", "discussion",
    }

    text_clean = text.strip().lower()
    text_clean = re.sub(r'\s+', '', text_clean)  # remove all whitespace for matching

    # Check level 1 semantic headings
    for h in semantic_headings_l1:
        if text_clean == h or text_clean == h.replace(" ", ""):
            return 1

    # Check level 2 semantic headings
    for h in semantic_headings_l2:
        h_clean = re.sub(r'\s+', '', h.lower())
        if text_clean == h_clean:
            return 2

    return 0


def extract_heading_text(line: str, numbering_system: str = "阿拉伯数字") -> str:
    """Extract heading title without the numbering prefix."""
    stripped = line.strip()
    if numbering_system == "中文序号":
        text = re.sub(r"^[一二三四五六七八九十百千]+[、．]\s*", "", stripped)
        text = re.sub(r"^（[一二三四五六七八九十百千]+）\s*", "", text)
    else:
        text = re.sub(r"^(第[一二三四五六七八九十百千]+章|[\d\.]+)\s*", "", stripped)
    return text.strip()


def is_list_item(line: str) -> bool:
    """Detect numbered or bullet list items."""
    return bool(re.match(r"^[\(（]?\d+[\)）]|^[•·\-*]", line.strip()))


# ── CJK text utilities ─────────────────────────────────────────

def is_cjk_char(ch: str) -> bool:
    """Check if a character is CJK Unified Ideograph."""
    cp = ord(ch)
    return (0x4E00 <= cp <= 0x9FFF or
            0x3400 <= cp <= 0x4DBF or
            0xF900 <= cp <= 0xFAFF or
            0x2F800 <= cp <= 0x2FA1F)


def has_cjk(text: str) -> bool:
    """Check if text contains any CJK characters."""
    return any(is_cjk_char(ch) for ch in text)


def insert_cjk_spacing(text: str) -> str:
    """Insert thin spaces between CJK and Latin/numeral characters.

    "基于Transformer的模型" → "基于 Transformer 的模型"
    """
    # CJK followed by Latin/numeral
    text = re.sub(
        r'([一-鿿㐀-䶿豈-﫿])([A-Za-z0-9@#\$%\^&\*])',
        r'\1 \2', text
    )
    # Latin/numeral followed by CJK
    text = re.sub(
        r'([A-Za-z0-9@#\$%\^&\*])([一-鿿㐀-䶿豈-﫿])',
        r'\1 \2', text
    )
    return text


def normalize_punctuation(text: str) -> str:
    """Normalize mixed full/half-width punctuation.

    - Chinese punctuation → full-width
    - English punctuation → half-width
    - Unified quote marks
    """
    # Full-width letters/numbers → half-width
    text = re.sub(r'[Ａ-Ｚ]', lambda m: chr(ord(m.group(0)) - 0xfee0), text)
    text = re.sub(r'[ａ-ｚ]', lambda m: chr(ord(m.group(0)) - 0xfee0), text)
    text = re.sub(r'[０-９]', lambda m: chr(ord(m.group(0)) - 0xfee0), text)

    # Half-width CJK punctuation → full-width
    text = text.replace(',', '，')
    text = text.replace('.', '。')
    text = text.replace('!', '！')
    text = text.replace('?', '？')
    text = text.replace(':', '：')
    text = text.replace(';', '；')

    return text


def detect_language(text: str) -> str:
    """Detect primary language of text: 'zh', 'en', or 'mixed'."""
    cjk_count = sum(1 for ch in text if is_cjk_char(ch))
    latin_count = sum(1 for ch in text if ch.isascii() and ch.isalpha())

    total = cjk_count + latin_count
    if total == 0:
        return "mixed"
    ratio = cjk_count / total
    if ratio > 0.8:
        return "zh"
    elif ratio < 0.2:
        return "en"
    return "mixed"
