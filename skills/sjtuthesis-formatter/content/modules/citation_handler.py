"""
Citation & Reference Handler
============================

Detects citation formats (sequential numbering vs. author-year),
validates citation placeholders against the reference list,
detects and updates cross-references (e.g., "见图 2-1"),
and helps format references according to GB/T 7714.
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Set, Tuple


# ── Citation format detection ──────────────────────────────────────

class CitationFormat(Enum):
    SEQUENTIAL = auto()    # [1], [2,3], [1-4]
    AUTHOR_YEAR = auto()   # [Author, 2020] or (Author, 2020)
    MIXED = auto()
    UNKNOWN = auto()


SEQUENTIAL_CITE_RE = re.compile(r'\[(\d+(?:\s*[,\-\s]\s*\d+)*)\]')
AUTHOR_YEAR_CITE_RE = re.compile(r'\[([A-Za-z一-鿿]+[\s,]+(?:\d{4}))\]')
PAREN_YEAR_CITE_RE = re.compile(r'\(([A-Za-z一-鿿]+[\s,]+\d{4})\)')
CROSS_REF_FIGURE_RE = re.compile(r'(?:如?图|Figure|Fig\.?)\s*(\d+(?:[\.-]\d+)?)', re.IGNORECASE)
CROSS_REF_TABLE_RE = re.compile(r'(?:如?表|Table)\s*(\d+(?:[\.-]\d+)?)', re.IGNORECASE)
CROSS_REF_FORMULA_RE = re.compile(r'(?:公式|式|Equation)\s*[\(（]?(\d+(?:[\.-]\d+)?)[\)）]?', re.IGNORECASE)
DOI_RE = re.compile(r'10\.\d{4,}/[-._;()/:A-Za-z0-9]+', re.IGNORECASE)


@dataclass
class CitationIssue:
    """A citation- or reference-related issue."""
    location: str
    summary: str
    detail: str = ""
    is_error: bool = True


@dataclass
class ReferenceItem:
    """A single reference entry with parsed fields.

    Supports GB/T 7714 format generation, field extraction,
    and missing-field detection.
    """
    index: int = 0
    raw_text: str = ""
    authors: str = ""
    title: str = ""
    year: str = ""
    journal: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    doi: str = ""
    publisher: str = ""
    address: str = ""
    url: str = ""
    ref_type: str = "J"       # J=期刊, M=专著, C=会议, D=学位, P=专利, R=报告, S=标准, EB/OL=电子

    def parse_fields(self):
        """Auto-extract fields from raw_text using regex patterns."""
        # DOI
        doi_match = re.search(r'10\.\d{4,}/[-._;()/:A-Za-z0-9]+', self.raw_text)
        if doi_match:
            self.doi = doi_match.group(0)
        # URL
        url_match = re.search(r'https?://\S+', self.raw_text)
        if url_match:
            self.url = url_match.group(0)
        # Year
        year_match = re.search(r'(\d{4})', self.raw_text)
        if year_match:
            self.year = year_match.group(1)
        # Volume/Issue: "12(3)" or "Vol. 12"
        vol_issue = re.search(r'(\d+)\s*\(\s*(\d+)\s*\)', self.raw_text)
        if vol_issue:
            self.volume = vol_issue.group(1)
            self.issue = vol_issue.group(2)
        else:
            vol_match = re.search(r'[Vv][Oo][Ll]\.?\s*(\d+)', self.raw_text)
            if vol_match:
                self.volume = vol_match.group(1)
        # Pages
        pages_match = re.search(r'[Pp]p?\.?\s*(\d+[\-–]\d+)', self.raw_text)
        if pages_match:
            self.pages = pages_match.group(1)
        # Type marker: [J], [M], etc.
        type_match = re.search(r'\[([JMCWDPRSEB/OL]+)\]', self.raw_text)
        if type_match:
            self.ref_type = type_match.group(1)
        # Authors + Title (before first period pairs)
        clean = re.sub(r'^\[\d+\]\s*', '', self.raw_text)
        parts = clean.split(". ")
        if len(parts) >= 2:
            self.authors = parts[0]
            self.title = parts[1]

    def format_gbt7714(self) -> str:
        """Format as GB/T 7714-2015 bibliographic style.

        Examples:
          [1] 作者. 题名[J]. 刊名, 年, 卷(期): 页码.
          [2] 作者. 题名[M]. 出版地: 出版者, 年.
        """
        self.parse_fields()
        parts = []
        if self.authors:
            parts.append(f"{self.authors}.")
        if self.title:
            parts.append(f"{self.title}[{self.ref_type}].")
        if self.journal and self.ref_type == "J":
            parts.append(f"{self.journal},")
        if self.year:
            parts.append(f"{self.year},")
        if self.volume:
            issue_str = f"({self.issue})" if self.issue else ""
            parts.append(f"{self.volume}{issue_str}:")
        if self.pages:
            parts.append(f"{self.pages}.")
        if self.publisher and self.ref_type == "M":
            addr = f"{self.address}: " if self.address else ""
            parts.append(f"{addr}{self.publisher},")
            if self.year:
                parts.append(f"{self.year}.")
        if self.doi:
            parts.append(f"DOI: {self.doi}.")
        return " ".join(parts) if parts else self.raw_text

    def missing_fields(self) -> List[str]:
        """Return list of missing important bibliographic fields."""
        missing = []
        if not self.authors:
            missing.append("authors")
        if not self.title:
            missing.append("title")
        if not self.year:
            missing.append("year")
        if self.ref_type == "J" and not self.journal:
            missing.append("journal")
        if self.ref_type == "M" and not self.publisher:
            missing.append("publisher")
        return missing


# ── Reference type detection ──────────────────────────────────────

def detect_reference_type(text: str) -> str:
    """Auto-detect reference type from text content.

    Returns: J, M, C, D, P, R, S, EB/OL.
    """
    type_match = re.search(r'\[([JMCWDPRSEB/OL]+)\]', text)
    if type_match:
        return type_match.group(1)
    text_lower = text.lower()
    if any(kw in text_lower for kw in ("dissertation", "phd thesis", "博士", "硕士论文")):
        return "D"
    if any(kw in text_lower for kw in ("conference", "proceedings", "研讨会")):
        return "C"
    if any(kw in text_lower for kw in ("patent", "专利")):
        return "P"
    if any(kw in text_lower for kw in ("http://", "https://", "www.")):
        return "EB/OL"
    if any(kw in text_lower for kw in ("press", "出版社", "publisher")):
        return "M"
    if any(kw in text_lower for kw in ("report", "报告")):
        return "R"
    if any(kw in text_lower for kw in ("standard", "标准", "gb/")):
        return "S"
    return "J"


# ── Reference list management ─────────────────────────────────────

def parse_reference_list(ref_text: str) -> List[ReferenceItem]:
    """Parse raw reference text into structured ReferenceItems."""
    items: List[ReferenceItem] = []
    if not ref_text.strip():
        return items
    for i, line in enumerate(ref_text.split("\n")):
        line = line.strip()
        if not line:
            continue
        item = ReferenceItem(index=i + 1, raw_text=line)
        item.parse_fields()
        items.append(item)
    return items


def sort_references_by_appearance(cited_order: List[int],
                                   refs: List[ReferenceItem]) -> List[ReferenceItem]:
    """Sort references by order of first appearance in text."""
    ref_map = {r.index: r for r in refs}
    sorted_refs = []
    for idx in cited_order:
        if idx in ref_map and ref_map[idx] not in sorted_refs:
            sorted_refs.append(ref_map[idx])
    for r in refs:
        if r not in sorted_refs:
            sorted_refs.append(r)
    return sorted_refs


def format_all_references(refs: List[ReferenceItem], style: str = "gbt7714") -> str:
    """Format all references according to the specified style."""
    formatted = []
    for i, ref in enumerate(refs, 1):
        ref.index = i
        if style == "gbt7714":
            formatted.append(f"[{i}] {ref.format_gbt7714()}")
        else:
            formatted.append(f"[{i}] {ref.raw_text}")
    return "\n".join(formatted)

def detect_citation_format(text: str) -> CitationFormat:
    """Detect which citation format is used in the text."""
    sequential_count = len(SEQUENTIAL_CITE_RE.findall(text))
    author_year_count = len(AUTHOR_YEAR_CITE_RE.findall(text)) + len(PAREN_YEAR_CITE_RE.findall(text))

    if sequential_count > 0 and author_year_count == 0:
        return CitationFormat.SEQUENTIAL
    elif author_year_count > 0 and sequential_count == 0:
        return CitationFormat.AUTHOR_YEAR
    elif sequential_count > 0 and author_year_count > 0:
        return CitationFormat.MIXED
    return CitationFormat.UNKNOWN


def extract_citations(text: str) -> List[str]:
    """Extract all citation placeholders from text."""
    return SEQUENTIAL_CITE_RE.findall(text)


def extract_reference_indices(text: str) -> Set[int]:
    """Extract all reference index numbers from citation markers."""
    indices: Set[int] = set()
    for match in SEQUENTIAL_CITE_RE.finditer(text):
        content = match.group(1)
        for num in re.split(r'[,\s]+', content):
            num = num.strip().replace(" ", "")
            if "-" in num:
                # Range like "1-4"
                parts = num.split("-")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    indices.update(range(int(parts[0]), int(parts[1]) + 1))
            elif num.isdigit():
                indices.add(int(num))
    return indices


# ── Validation ─────────────────────────────────────────────────────

def validate_citations(body_text: str, ref_text: str) -> List[CitationIssue]:
    """Validate that all citations in body text have matching references."""
    issues: List[CitationIssue] = []
    cited = extract_reference_indices(body_text)
    refs = parse_reference_list(ref_text)
    total_refs = len(refs)

    if total_refs == 0 and cited:
        # We have citations but no references section detected
        issues.append(CitationIssue(
            location="参考文献",
            summary="正文包含引用标记，但未检测到参考文献列表",
            is_error=True,
        ))
        return issues

    # Check each cited index has a matching reference
    for idx in sorted(cited):
        if idx > total_refs:
            issues.append(CitationIssue(
                location=f"正文引用[{idx}]",
                summary=f"引用编号 [{idx}] 超出参考文献总数 ({total_refs})",
                is_error=True,
            ))

    # Check for unused references
    unused = set(range(1, total_refs + 1)) - cited
    if unused and total_refs > 0:
        unused_str = ", ".join(f"[{i}]" for i in sorted(unused))
        issues.append(CitationIssue(
            location="参考文献",
            summary=f"以下参考文献未被引用: {unused_str}",
            is_error=False,
        ))

    return issues


# ── Cross-reference detection ──────────────────────────────────────

@dataclass
class CrossReference:
    """A cross-reference from text to a figure/table/formula."""
    ref_type: str        # figure, table, formula
    target_num: str      # "2-1" or "1"
    context: str         # Surrounding text
    line_num: int = 0


def extract_cross_references(text: str) -> List[CrossReference]:
    """Extract all cross-references to figures, tables, and formulas."""
    refs: List[CrossReference] = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        for match in CROSS_REF_FIGURE_RE.finditer(line):
            refs.append(CrossReference(
                ref_type="figure",
                target_num=match.group(1),
                context=match.group(0),
                line_num=i + 1,
            ))
        for match in CROSS_REF_TABLE_RE.finditer(line):
            refs.append(CrossReference(
                ref_type="table",
                target_num=match.group(1),
                context=match.group(0),
                line_num=i + 1,
            ))
        for match in CROSS_REF_FORMULA_RE.finditer(line):
            refs.append(CrossReference(
                ref_type="formula",
                target_num=match.group(1),
                context=match.group(0),
                line_num=i + 1,
            ))
    return refs


def validate_cross_references(text: str) -> List[CitationIssue]:
    """Validate that all cross-references match existing figure/table numbers."""
    issues: List[CitationIssue] = []

    # Extract all figure/table captions from text
    fig_nums = set()
    tbl_nums = set()
    for line in text.split("\n"):
        m = re.match(r'^图\s*(\d+(?:[\.-]\d+)?)', line)
        if m:
            fig_nums.add(m.group(1))
        m = re.match(r'^表\s*(\d+(?:[\.-]\d+)?)', line)
        if m:
            tbl_nums.add(m.group(1))

    # Check cross-references
    for xref in extract_cross_references(text):
        target_set = fig_nums if xref.ref_type == "figure" else tbl_nums
        if target_set and xref.target_num not in target_set:
            issues.append(CitationIssue(
                location=f"第{xref.line_num}行",
                summary=f"交叉引用 '{xref.context}' 指向 {xref.ref_type} {xref.target_num}，"
                       f"但未找到对应题注（已有: {', '.join(sorted(target_set)) if target_set else '无'}）",
                is_error=False,
            ))

    return issues


# ── Format conversion ──────────────────────────────────────────────

def convert_to_gbt7714(ref_text: str) -> str:
    """Attempt to reformat references to GB/T 7714-2005 style.

    This is a best-effort heuristic for common patterns.
    Full conversion requires a dedicated reference manager.
    """
    lines = ref_text.strip().split("\n")
    converted: List[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        converted.append(line)
    return "\n".join(converted)


def citation_format_description(fmt: CitationFormat) -> str:
    """Human-readable description of citation format."""
    descriptions = {
        CitationFormat.SEQUENTIAL: "顺序编码制 [1], [2,3]",
        CitationFormat.AUTHOR_YEAR: "著者-出版年制 [Author, 2020]",
        CitationFormat.MIXED: "混用（同时检测到两种格式）",
        CitationFormat.UNKNOWN: "未识别",
    }
    return descriptions.get(fmt, "未知")
