"""
PDF Bookmarks & Metadata — Hierarchical Bookmark Generation
============================================================

Generates PDF bookmarks from the document's section hierarchy.
Supports both LaTeX (\\pdfbookmark) and Word (outline/XML) output,
plus standard PDF metadata (Title, Author, Subject, Keywords).

Usage:
    bookmarks = generate_bookmarks(document_tree)
    latex_code = render_latex_bookmarks(bookmarks)
    # Or for Word:
    word_xml = render_word_bookmarks(bookmarks)
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# ── Bookmark data types ───────────────────────────────────────────

@dataclass
class BookmarkEntry:
    """A single bookmark entry at one level of the hierarchy."""
    title: str
    level: int                       # 0=chapter, 1=section, 2=subsection
    page_number: int = 0             # Placeholder, set during PDF generation
    children: List['BookmarkEntry'] = field(default_factory=list)
    bookmark_id: str = ""            # Unique anchor identifier

    def add_child(self, child: 'BookmarkEntry'):
        self.children.append(child)


@dataclass
class PdfMetadata:
    """Standard PDF metadata fields."""
    title: str = ""
    author: str = ""
    subject: str = ""
    keywords: str = ""
    creator: str = "SJTU Thesis Formatter Engine"
    producer: str = "python-docx / XeLaTeX"

    def to_dict(self) -> dict:
        return {
            "Title": self.title,
            "Author": self.author,
            "Subject": self.subject,
            "Keywords": self.keywords,
            "Creator": self.creator,
        }


@dataclass
class BookmarkHierarchy:
    """Complete bookmark hierarchy with metadata."""
    entries: List[BookmarkEntry] = field(default_factory=list)
    metadata: Optional[PdfMetadata] = None

    def total_bookmarks(self) -> int:
        """Count all bookmarks recursively."""
        def count(entries: List[BookmarkEntry]) -> int:
            total = len(entries)
            for e in entries:
                total += count(e.children)
            return total
        return count(self.entries)

    def max_depth(self) -> int:
        """Return the deepest nesting level."""
        def depth(entries: List[BookmarkEntry], current: int = 0) -> int:
            if not entries:
                return current
            return max(depth(e.children, current + 1) for e in entries)
        return depth(self.entries)


# ── Generate bookmarks from document tree ─────────────────────────

def bookmarks_from_tree(tree, numbering_system: str = "阿拉伯数字") -> BookmarkHierarchy:
    """Convert a semantic_parser DocumentNode tree into bookmarks.

    Args:
        tree: The root DocumentNode from semantic_parser.parse_document().
        numbering_system: For heading level detection.

    Returns:
        BookmarkHierarchy with nested entries.
    """
    hierarchy = BookmarkHierarchy()
    stack: List[tuple[int, BookmarkEntry]] = []  # (level, entry) tracking

    def walk(node):
        nonlocal stack
        if not hasattr(node, 'type') or not hasattr(node, 'children'):
            return

        # Only process nodes that represent sections/headings
        if node.type.name in ("CHAPTER", "SECTION", "SUBSECTION",
                               "ABSTRACT", "ABSTRACT_EN", "ACKNOWLEDGEMENT",
                               "REFERENCE_LIST", "APPENDIX", "TOC"):
            entry = BookmarkEntry(
                title=_clean_bookmark_title(node.text),
                level=_bookmark_level(node),
                bookmark_id=_make_bookmark_id(node.text, node.level),
            )

            # Insert into hierarchy based on level
            if entry.level <= 0 or not stack:
                # Chapter-level or no parent → root
                hierarchy.entries.append(entry)
                stack = [(entry.level, entry)]
            else:
                # Pop stack until we find a parent whose level is lower
                while stack and stack[-1][0] >= entry.level:
                    stack.pop()
                if stack:
                    stack[-1][1].add_child(entry)
                else:
                    hierarchy.entries.append(entry)
                stack.append((entry.level, entry))

        for child in getattr(node, 'children', []):
            walk(child)

    walk(tree)
    return hierarchy


def _clean_bookmark_title(text: str) -> str:
    """Clean a heading text for use as a bookmark title."""
    # Remove numbering prefixes
    text = re.sub(r'^(?:第[一二三四五六七八九十百千]+章|[\d\.]+)\s*', '', text)
    text = re.sub(r'^[一二三四五六七八九十]+[、．]\s*', '', text)
    # Truncate and clean
    text = text.strip()[:80]
    return text if text else "Untitled"


def _bookmark_level(node) -> int:
    """Determine bookmark level from node type and level."""
    type_map = {
        "CHAPTER": 0,
        "ABSTRACT": 0,
        "ABSTRACT_EN": 0,
        "TOC": 0,
        "REFERENCE_LIST": 0,
        "APPENDIX": 0,
        "ACKNOWLEDGEMENT": 0,
        "SECTION": 1,
        "SUBSECTION": 2,
        "SUBSUBSECTION": 3,
    }
    return type_map.get(node.type.name, node.level)


def _make_bookmark_id(text: str, level: int) -> str:
    """Generate a unique bookmark anchor ID."""
    base = re.sub(r'[^a-zA-Z0-9一-鿿]', '_', text)[:30]
    return f"sec:{base}"


# ── LaTeX bookmark output ─────────────────────────────────────────

def render_latex_bookmarks(hierarchy: BookmarkHierarchy) -> str:
    """Generate LaTeX \\pdfbookmark commands from bookmark hierarchy.

    Outputs commands compatible with hyperref + bookmark packages.
    """
    if not hierarchy.entries:
        return ""

    lines = [
        "% ── PDF Bookmarks (auto-generated) ──────────────────────────",
        "% Requires: \\usepackage[bookmarks=true]{hyperref}",
        "%            \\usepackage{bookmark}",
        "",
    ]

    def render(entries: List[BookmarkEntry], indent: int = 0):
        prefix = "  " * indent
        for entry in entries:
            lines.append(
                f"{prefix}\\pdfbookmark[{entry.level}]{{{entry.title}}}"
                f"{{{entry.bookmark_id}}}"
            )
            if entry.children:
                render(entry.children, indent + 1)

    render(hierarchy.entries)
    lines.append("")
    return "\n".join(lines)


def render_latex_metadata(metadata: PdfMetadata) -> str:
    """Generate LaTeX \\hypersetup with PDF metadata."""
    lines = [
        "\\hypersetup{",
        f"  pdftitle={{{metadata.title}}},",
        f"  pdfauthor={{{metadata.author}}},",
        f"  pdfsubject={{{metadata.subject}}},",
        f"  pdfkeywords={{{metadata.keywords}}},",
        f"  pdfcreator={{{metadata.creator}}},",
        "  bookmarks=true,",
        "  bookmarksnumbered=true,",
        "  bookmarksopen=true,",
        "  bookmarksopenlevel=1,",
        "}",
    ]
    return "\n".join(lines)


# ── Word bookmark output (via XML) ────────────────────────────────

def render_word_bookmarks_xml(hierarchy: BookmarkHierarchy) -> str:
    """Generate Word-compatible bookmark XML for insertion into document.xml.

    Each heading gets a <w:bookmarkStart> and <w:bookmarkEnd> pair.
    """
    xml_parts: List[str] = []
    bm_counter = [0]  # mutable counter for unique IDs

    def render(entries: List[BookmarkEntry]):
        for entry in entries:
            bm_counter[0] += 1
            bm_id = bm_counter[0]
            xml_parts.append(
                f'<w:bookmarkStart w:id="{bm_id}" '
                f'w:name="{entry.bookmark_id}"/>'
            )
            if entry.children:
                render(entry.children)
            xml_parts.append(
                f'<w:bookmarkEnd w:id="{bm_id}"/>'
            )

    render(hierarchy.entries)
    return "\n".join(xml_parts)


def render_word_outline(hierarchy: BookmarkHierarchy) -> str:
    """Generate a human-readable outline of the bookmark hierarchy.

    Useful for console display or preview.
    """
    if not hierarchy.entries:
        return "(empty)"

    lines: List[str] = []
    def render(entries: List[BookmarkEntry], indent: int = 0):
        for entry in entries:
            indent_str = "  " * indent
            icon = {0: "📘", 1: "📗", 2: "📙"}.get(entry.level, "📄")
            lines.append(f"{indent_str}{icon} {entry.title}")
            if entry.children:
                render(entry.children, indent + 1)

    render(hierarchy.entries)
    return "\n".join(lines)


# ── Metadata helpers ──────────────────────────────────────────────

def metadata_from_thesis_info(info) -> PdfMetadata:
    """Extract PDF metadata from a ThesisInfo object."""
    return PdfMetadata(
        title=info.title_cn or info.title,
        author=info.author,
        subject=f"{info.degree_type}学位论文 — {info.college} {info.major}",
        keywords=", ".join(info.keywords_cn) if info.keywords_cn else "",
    )


# ── Bookmark validation ───────────────────────────────────────────

def validate_bookmarks(hierarchy: BookmarkHierarchy) -> List[str]:
    """Check bookmark hierarchy for issues like gaps, duplicates, etc."""
    issues: List[str] = []
    seen_ids = set()

    def check(entries: List[BookmarkEntry], parent_level: int = -1):
        for entry in entries:
            if entry.bookmark_id in seen_ids:
                issues.append(f"Duplicate bookmark ID: {entry.bookmark_id}")
            seen_ids.add(entry.bookmark_id)

            if not entry.title.strip():
                issues.append(f"Empty bookmark title at level {entry.level}")

            if entry.level < parent_level:
                issues.append(
                    f"Level jump: {parent_level} → {entry.level} "
                    f"('{entry.title}')"
                )

            if entry.children:
                check(entry.children, entry.level)

    check(hierarchy.entries)
    return issues
