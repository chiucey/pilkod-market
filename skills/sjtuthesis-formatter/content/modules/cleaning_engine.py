"""
Cleaning Engine — Semantic Text Cleaning
=========================================

Performs intelligent cleaning of messy document drafts:
1. Semantic float matching (match "如下图所示" → nearest figure)
2. CJK/Latin spacing normalization
3. Widow/orphan paragraph control
4. Cross-reference cleanup
5. Bulk formatting artifact removal
6. Image placeholder ↔ caption matching
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .helpers import insert_cjk_spacing, normalize_punctuation, has_cjk


# ── Patterns ───────────────────────────────────────────────────────

# Multiple consecutive blank lines
MULTI_BLANK_RE = re.compile(r'\n{3,}')

# Manual spacing artifacts
MANUAL_SPACING_RE = re.compile(r'[ \t]{3,}')

# "如下图所示" / "as shown below" patterns
AS_SHOWN_RE = re.compile(
    r'(?:如下|以下|下面|下图|上图|above|below|following)', re.IGNORECASE
)

# Caption patterns
FIGURE_CAPTION_RE = re.compile(
    r'^(?:图|Figure|Fig\.?)\s*(\d+(?:[\.-]\d+)?)', re.IGNORECASE
)
TABLE_CAPTION_RE = re.compile(
    r'^(?:表|Table)\s*(\d+(?:[\.-]\d+)?)', re.IGNORECASE
)

# Inline annotation removal
ANNOTATION_RE = re.compile(
    r'\[(?:TODO|FIXME|NOTE|HACK|XXX|BUG).*?\]', re.IGNORECASE
)

# Chinese/English mixed quote normalization
LEFT_DOUBLE_QUOTE_RE = re.compile(r'(?<=[一-鿿])"')
RIGHT_DOUBLE_QUOTE_RE = re.compile(r'"(?=[一-鿿])')

# Markdown-style images
MD_IMAGE_RE = re.compile(r'!\[(.*?)\]\((.*?)\)')

# HTML tags (from web paste)
HTML_TAG_RE = re.compile(r'<[^>]+>')

# Widow/orphan detection (single line at page boundary)
WIDOW_RE = re.compile(r'^\s*[。！？，、；：)]$')


@dataclass
class CleaningReport:
    """Report of cleaning operations performed."""
    actions: List[str] = field(default_factory=list)
    blank_lines_removed: int = 0
    annotations_removed: int = 0
    spacing_fixes: int = 0
    caption_matches: int = 0

    def add(self, action: str):
        self.actions.append(action)

    def summary(self) -> str:
        return (f"Cleaning complete: {len(self.actions)} operations "
                f"({self.blank_lines_removed}x blank lines, "
                f"{self.annotations_removed}x annotations, "
                f"{self.caption_matches}x caption matches)")


# ── Main cleaning pipeline ─────────────────────────────────────────

def semantic_clean(text: str) -> Tuple[str, CleaningReport]:
    """Apply full semantic cleaning pipeline.

    Steps:
    1. Remove HTML tags (from web paste)
    2. Remove inline annotations
    3. Normalize blank lines
    4. Fix manual spacing
    5. Insert CJK/Latin spacing
    6. Normalize punctuation
    7. Match "如下图所示" → captions
    8. Fix Markdown image references

    Returns:
        Tuple of (cleaned_text, CleaningReport)
    """
    report = CleaningReport()
    original = text

    # Step 1: Remove HTML tags
    text = HTML_TAG_RE.sub("", text)

    # Step 2: Remove inline annotations
    annotations = ANNOTATION_RE.findall(text)
    if annotations:
        text = ANNOTATION_RE.sub("", text)
        report.annotations_removed = len(annotations)
        report.add(f"Removed {len(annotations)} inline annotations")

    # Step 3: Normalize blank lines (max 1 blank line between paragraphs)
    before = text.count("\n\n\n")
    text = MULTI_BLANK_RE.sub("\n\n", text)
    after = text.count("\n\n\n")
    report.blank_lines_removed = before
    if before > 0:
        report.add(f"Collapsed {before} excess blank lines")

    # Step 4: Remove manual triple+ spaces
    text = MANUAL_SPACING_RE.sub(" ", text)

    # Step 5: CJK/Latin spacing
    spaced = insert_cjk_spacing(text)
    if spaced != text:
        report.spacing_fixes += 1
        report.add("Applied CJK/Latin spacing")
    text = spaced

    # Step 6: Normalize punctuation
    text = normalize_punctuation(text)

    # Step 7: Match "如下图所示" → nearest figure caption
    matched = match_caption_references(text)
    if matched:
        for phrase, caption in matched:
            report.caption_matches += 1
            report.add(f"Matched '{phrase[:20]}...' → caption '{caption}'")
        text = insert_caption_hints(text, matched)

    return text, report


# ── "如下图所示" → caption matching ────────────────────────────────

def match_caption_references(text: str) -> List[Tuple[str, str]]:
    """Find '如下图所示' phrases and match them to nearest figure caption.

    Returns:
        List of (phrase_text, caption_text) pairs.
    """
    lines = text.split("\n")
    matches: List[Tuple[str, str]] = []
    captions: List[Tuple[str, int]] = []

    # First pass: find all captions
    for i, line in enumerate(lines):
        m = FIGURE_CAPTION_RE.match(line.strip())
        if m:
            captions.append((line.strip(), i))

    # Second pass: find "as shown" phrases
    for i, line in enumerate(lines):
        if AS_SHOWN_RE.search(line) and not FIGURE_CAPTION_RE.match(line.strip()):
            # Find nearest following caption
            nearest = None
            for cap_text, cap_line in captions:
                if cap_line > i:
                    nearest = cap_text
                    break
            if nearest:
                matches.append((line.strip()[:50], nearest))

    return matches


def insert_caption_hints(text: str, matches: List[Tuple[str, str]]) -> str:
    """Insert cross-reference hints near 'as shown' phrases."""
    # For now, just return the text as-is; actual cross-reference
    # injection is handled during rendering
    return text


# ── Widow/orphan detection ─────────────────────────────────────────

def detect_widows(text: str) -> List[int]:
    """Detect potential widow/orphan lines.

    A widow is a single line of a paragraph at the top of a page.
    Since we don't have page info on raw text, we detect short
    lines that look like paragraph fragments.

    Returns:
        List of line numbers (1-indexed) with potential issues.
    """
    lines = text.split("\n")
    widows: List[int] = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Very short lines that end sentences → potential widow
        if 1 <= len(stripped) <= 3 and WIDOW_RE.match(stripped):
            widows.append(i + 1)

        # Single character on a line
        if len(stripped) == 1 and stripped.isalpha():
            widows.append(i + 1)

    return widows


# ── Image placeholder handling ─────────────────────────────────────

def find_unmatched_markdown_images(text: str) -> List[Tuple[str, int]]:
    """Find Markdown image references without matching captions."""
    captions = set()
    for line in text.split("\n"):
        m = FIGURE_CAPTION_RE.match(line.strip())
        if m:
            captions.add(m.group(1))

    unmatched: List[Tuple[str, int]] = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in MD_IMAGE_RE.finditer(line):
            # Check if a caption exists nearby
            has_caption = False
            for j in range(max(0, i - 3), min(len(text.split("\n")), i + 3)):
                if FIGURE_CAPTION_RE.match(text.split("\n")[j].strip()):
                    has_caption = True
                    break
            if not has_caption:
                unmatched.append((m.group(0), i))

    return unmatched


# ── Utility cleaning functions ─────────────────────────────────────

def clean_web_paste(text: str) -> str:
    """Clean text pasted from web pages."""
    text = HTML_TAG_RE.sub("", text)
    text = MULTI_BLANK_RE.sub("\n\n", text)
    text = MANUAL_SPACING_RE.sub(" ", text)
    return text.strip()


def remove_track_changes(text: str) -> str:
    """Remove visible track-change annotations."""
    patterns = [
        r'\[(?:删除|插入|批注|TODO|FIXME|HACK|XXX|BUG|NOTE).*?\]',
        r'\{[^}]*\}',
        r'<\w+[^>]*>.*?</\w+>',
    ]
    for pat in patterns:
        text = re.sub(pat, '', text, flags=re.DOTALL)
    return text


def standardize_line_breaks(text: str) -> str:
    """Standardize all line breaks to \\n."""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text


# ── Content Protection ────────────────────────────────────────────

def detect_track_changes(text: str) -> List[Tuple[str, int]]:
    """Detect track change / revision markers in text.

    Returns:
        List of (marker_text, line_number) tuples.
    """
    markers: List[Tuple[str, int]] = []
    patterns = [
        (r'<ins[^>]*>.*?</ins>', "插入"),
        (r'<del[^>]*>.*?</del>', "删除"),
        (r'<span[^>]*style="text-decoration:line-through[^"]*"[^>]*>.*?</span>', "删除线"),
        (r'<span[^>]*style="background:#[0-9a-fA-F]+"[^>]*>.*?</span>', "高亮批注"),
        (r'\[(?:批注|comment|review).*?\]', "批注标记"),
        (r'<!--.*?-->', "HTML注释"),
    ]
    for pattern, label in patterns:
        for match in re.finditer(pattern, text, re.DOTALL | re.IGNORECASE):
            line_num = text[:match.start()].count("\n") + 1
            markers.append((f"[{label}] {match.group()[:40]}", line_num))
    return markers


def protect_content_regions(text: str, regions: List[Tuple[int, int, str]]) -> str:
    """Replace protected regions with placeholders before processing.

    Args:
        text: The full document text.
        regions: List of (start, end, label) tuples.

    Returns:
        Text with protected regions replaced by markers.
    """
    # Process right to left to preserve positions
    protected_blocks = []
    for start, end, label in sorted(regions, key=lambda x: x[0], reverse=True):
        block = text[start:end]
        placeholder = f"§§PROTECTED_{label}_{len(block)}_CHARS§§"
        text = text[:start] + placeholder + text[end:]
        protected_blocks.append((placeholder, block))
    return text, protected_blocks


def restore_protected_regions(text: str, blocks: List[Tuple[str, str]]) -> str:
    """Restore protected regions after processing."""
    for placeholder, original in blocks:
        text = text.replace(placeholder, original)
    return text


def detect_comments(text: str) -> List[Tuple[str, int]]:
    """Detect comment-like annotations in text.

    Returns:
        List of (comment_text, line_number).
    """
    comments: List[Tuple[str, int]] = []
    patterns = [
        (r'(?://|#)\s*(?:TODO|FIXME|NOTE|HACK|XXX|BUG|REVIEW|COMMENT)\s*:.*?(?:\n|$)', "inline"),
        (r'/\*\s*(?:TODO|FIXME|NOTE|HACK|XXX|BUG).*?\*/', "block", re.DOTALL),
    ]
    for pattern_info in patterns:
        if len(pattern_info) == 2:
            pattern, label = pattern_info
            flags = 0
        else:
            pattern, label, flags = pattern_info
        for match in re.finditer(pattern, text, flags | re.IGNORECASE):
            line_num = text[:match.start()].count("\n") + 1
            comments.append((match.group()[:60], line_num))
    return comments


def batch_split_hint(text: str, max_chars: int = 50000) -> List[Tuple[str, int, int]]:
    """Split long text into batchable chunks at chapter boundaries.

    For documents >200 pages, identifies natural split points
    at chapter/section boundaries for parallel processing.

    Returns:
        List of (chunk_text, start_line, end_line) tuples.
    """
    lines = text.split("\n")
    chunks: List[Tuple[str, int, int]] = []
    current_start = 0
    current_chars = 0

    # Find chapter/section boundaries
    chapter_indices = []
    for i, line in enumerate(lines):
        from modules.helpers import detect_heading_level
        if detect_heading_level(line.strip()) >= 1:
            chapter_indices.append(i)

    if not chapter_indices or len(text) <= max_chars:
        return [(text, 1, len(lines))]

    for idx in chapter_indices:
        chunk_text = "\n".join(lines[current_start:idx])
        chunks.append((chunk_text, current_start + 1, idx))
        current_start = idx

    # Last chunk
    if current_start < len(lines):
        chunk_text = "\n".join(lines[current_start:])
        chunks.append((chunk_text, current_start + 1, len(lines)))

    return chunks


def strip_formatting_artifacts(text: str) -> str:
    """Remove visible formatting artifacts from web paste or cross-format copy.

    Handles:
    - Microsoft Word formatting artifacts
    - Google Docs paste artifacts
    - PDF copy artifacts (extra hyphens, broken lines)
    - Unicode formatting characters
    """
    # Zero-width characters
    text = re.sub(r'[​‌‍‎‏﻿]', '', text)
    # Soft hyphen
    text = text.replace('­', '')
    # Non-breaking space -> regular space
    text = text.replace(' ', ' ')
    # Word joiners
    text = re.sub(r'⁠', '', text)
    # Remove visible "¶" pilcrow markers (from Word show/hide)
    text = text.replace('¶', '')
    # Remove visible line-break markers
    text = text.replace('↵', '')
    # Fix PDF hyphenation breaks (word-\\n → word)
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    return text
