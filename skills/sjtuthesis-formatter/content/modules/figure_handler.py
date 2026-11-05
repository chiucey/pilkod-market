"""
Figure & Table Handler
======================

Manages figure and table captions, generates Lists of Figures/Tables,
suggests optimal float placement near first textual mention,
and validates cross-reference consistency.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


# ── Data types ─────────────────────────────────────────────────────

@dataclass
class Caption:
    """A figure or table caption."""
    kind: str                  # "figure" or "table"
    number: str                # "1", "2-1", etc.
    title: str                 # Caption text
    raw_line: str = ""         # Original line
    line_num: int = 0          # Line number in document


@dataclass
class FloatSuggestion:
    """Suggested placement for a float element."""
    caption_num: str
    kind: str
    first_mention_line: int
    suggested_page: int = 0
    placement: str = "top"     # "top", "bottom", "here"


# ── Pattern constants ──────────────────────────────────────────────

FIGURE_CAPTION_RE = re.compile(
    r'^(?:图|Figure|Fig\.?)\s*(\d+(?:[\.-]\d+)?)[.．:：]?\s*(.*)', re.IGNORECASE
)
TABLE_CAPTION_RE = re.compile(
    r'^(?:表|表格|Table)\s*(\d+(?:[\.-]\d+)?)[.．:：]?\s*(.*)', re.IGNORECASE
)
FIGURE_REF_RE = re.compile(
    r'(?:如?图|Figure|Fig\.?)\s*(\d+(?:[\.-]\d+)?)', re.IGNORECASE
)
TABLE_REF_RE = re.compile(
    r'(?:如?表|Table)\s*(\d+(?:[\.-]\d+)?)', re.IGNORECASE
)
FIGURE_IMAGE_PATTERN = re.compile(
    r'!\[.*?\]\(.*?\)', re.IGNORECASE  # Markdown image
)


# ── Caption extraction ─────────────────────────────────────────────

def extract_captions(text: str) -> List[Caption]:
    """Extract all figure and table captions from document text."""
    captions: List[Caption] = []
    lines = text.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        fig_match = FIGURE_CAPTION_RE.match(stripped)
        if fig_match:
            captions.append(Caption(
                kind="figure",
                number=fig_match.group(1),
                title=fig_match.group(2).strip(),
                raw_line=stripped,
                line_num=i,
            ))
            continue

        tbl_match = TABLE_CAPTION_RE.match(stripped)
        if tbl_match:
            captions.append(Caption(
                kind="table",
                number=tbl_match.group(1),
                title=tbl_match.group(2).strip(),
                raw_line=stripped,
                line_num=i,
            ))

    return captions


# ── Type-specific caption detection ────────────────────────────────

def extract_figure_captions(text: str) -> List[Caption]:
    """Extract only figure captions."""
    return [c for c in extract_captions(text) if c.kind == "figure"]


def extract_table_captions(text: str) -> List[Caption]:
    """Extract only table captions."""
    return [c for c in extract_captions(text) if c.kind == "table"]


# ── Figure/Table cross-reference matching ──────────────────────────

def match_figure_references(text: str) -> List[Tuple[str, int]]:
    """Find all textual references to figures and their line numbers."""
    refs: List[Tuple[str, int]] = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in FIGURE_REF_RE.finditer(line):
            refs.append((m.group(1), i))
    return refs


def match_table_references(text: str) -> List[Tuple[str, int]]:
    """Find all textual references to tables and their line numbers."""
    refs: List[Tuple[str, int]] = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in TABLE_REF_RE.finditer(line):
            refs.append((m.group(1), i))
    return refs


def match_image_placeholders(text: str) -> List[Tuple[str, int]]:
    """Find Markdown image references (![alt](url))."""
    refs: List[Tuple[str, int]] = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in FIGURE_IMAGE_PATTERN.finditer(line):
            refs.append((m.group(0), i))
    return refs


# ── "如下图所示" matching ──────────────────────────────────────────

AS_SHOWN_RE = re.compile(
    r'(?:如下|以下|下面|下图|above|below|following)', re.IGNORECASE
)

def match_as_shown_to_figure(text: str) -> List[Tuple[int, int]]:
    """Match '如下图所示' phrases to the nearest figure caption.

    For each "如下图所示" / "as shown below" occurrence,
    find the nearest following figure caption.

    Returns:
        List of (phrase_line, caption_line) pairs.
    """
    lines = text.split("\n")
    pairs: List[Tuple[int, int]] = []

    # Find all figure captions
    fig_captions = extract_figure_captions(text)
    fig_lines = {c.line_num for c in fig_captions}

    for i, line in enumerate(lines, 1):
        if AS_SHOWN_RE.search(line):
            # Find nearest following caption
            nearest = None
            for cap_line in sorted(fig_lines):
                if cap_line > i:
                    nearest = cap_line
                    break
            if nearest:
                pairs.append((i, nearest))

    return pairs


# ── Generate Lists ─────────────────────────────────────────────────

def generate_list_of_figures(text: str) -> str:
    """Generate a List of Figures from captions in text."""
    captions = extract_figure_captions(text)
    if not captions:
        return ""

    lines = ["", "List of Figures", "=" * 40, ""]
    for cap in captions:
        lines.append(f"图 {cap.number}  {cap.title}")
    lines.append("")
    return "\n".join(lines)


def generate_list_of_tables(text: str) -> str:
    """Generate a List of Tables from captions in text."""
    captions = extract_table_captions(text)
    if not captions:
        return ""

    lines = ["", "List of Tables", "=" * 40, ""]
    for cap in captions:
        lines.append(f"表 {cap.number}  {cap.title}")
    lines.append("")
    return "\n".join(lines)


# ── Float placement suggestions ────────────────────────────────────

def suggest_float_placement(text: str) -> List[FloatSuggestion]:
    """Suggest where each figure/table should be placed.

    The basic heuristic: place the figure/table near its first
    textual mention (within the same section), preferring top of page.
    """
    suggestions: List[FloatSuggestion] = []
    fig_refs = match_figure_references(text)
    tbl_refs = match_table_references(text)
    fig_captions = extract_figure_captions(text)
    tbl_captions = extract_table_captions(text)

    # For each figure caption, find its first mention
    for cap in fig_captions:
        first_mention = None
        for ref_num, ref_line in fig_refs:
            if ref_num == cap.number:
                first_mention = ref_line
                break

        if first_mention:
            placement = "top" if (cap.line_num - first_mention) < 5 else "here"
        else:
            placement = "here"

        suggestions.append(FloatSuggestion(
            caption_num=cap.number,
            kind="figure",
            first_mention_line=first_mention or 0,
            placement=placement,
        ))

    for cap in tbl_captions:
        first_mention = None
        for ref_num, ref_line in tbl_refs:
            if ref_num == cap.number:
                first_mention = ref_line
                break

        suggestions.append(FloatSuggestion(
            caption_num=cap.number,
            kind="table",
            first_mention_line=first_mention or 0,
            placement="here",
        ))

    return suggestions


# ── Number continuity check ────────────────────────────────────────

def check_number_continuity(text: str) -> List[str]:
    """Check that figure/table numbers are continuous and non-duplicate.

    Returns:
        List of issue descriptions, empty if all good.
    """
    issues: List[str] = []
    captions = extract_captions(text)

    # Group by type
    for kind in ("figure", "table"):
        nums = []
        for cap in captions:
            if cap.kind == kind:
                try:
                    nums.append(int(cap.number.split("-")[-1]))
                except ValueError:
                    nums.append(0)

        # Check duplicates
        seen = set()
        for n in nums:
            if n in seen:
                issues.append(f"{kind} 编号 {n} 重复")
            seen.add(n)

        # Check continuity (only for simple numbers like 1, 2, 3)
        if nums and max(nums) == len(nums):
            pass  # Continuous if max == count
        elif len(nums) > 1:
            missing = [i for i in range(1, max(nums) + 1) if i not in nums]
            if missing:
                issues.append(f"{kind} 编号跳过: {missing}")

    return issues
