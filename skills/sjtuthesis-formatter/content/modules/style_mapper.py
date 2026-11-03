"""
Style Mapping Engine
====================

Maps semantic roles (e.g., "paper_title", "chapter_heading") to concrete
typographic styles. Supports multiple profiles (SJTU, IEEE, generic)
so the same semantic content can be reformatted for different venues.

Usage:
    mapper = StyleMapper(profile='sjtu')
    style = mapper.map('chapter_heading')
    # Returns: { 'font_cn': '黑体', 'font_en': 'Times New Roman',
    #             'size_pt': 16, 'bold': True, 'align': 'center', ... }
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Style definition ───────────────────────────────────────────────

@dataclass
class TextStyle:
    """A complete typographic style definition."""
    font_cn: str = "宋体"
    font_en: str = "Times New Roman"
    size_pt: float = 12.0
    bold: bool = False
    italic: bool = False
    align: str = "justify"         # left, center, right, justify
    first_line_indent_chars: int = 2
    line_spacing_pt: float = 20.0
    line_spacing_rule: str = "exact"  # exact, single, multiple
    space_before_pt: float = 0.0
    space_after_pt: float = 0.0
    keep_with_next: bool = False
    page_break_before: bool = False
    outline_level: int = -1        # Word outline level (-1 = body)

    @classmethod
    def merge(cls, base: 'TextStyle', override: dict) -> 'TextStyle':
        """Merge base style with overrides."""
        kwargs = {f.name: getattr(base, f.name) for f in field(TextStyle)}
        kwargs.update(override)
        return cls(**kwargs)


# ── Profile definitions ────────────────────────────────────────────

PROFILES = {
    "sjtu": {
        # Shanghai Jiao Tong University thesis (2022 spec)
        "paper_title": TextStyle(
            font_cn="黑体", font_en="Times New Roman",
            size_pt=26, bold=True, align="center",
            space_before_pt=60, space_after_pt=30,
        ),
        "chapter_heading": TextStyle(
            font_cn="黑体", font_en="Times New Roman",
            size_pt=16, bold=True, align="center",
            line_spacing_pt=20, line_spacing_rule="exact",
            space_before_pt=24, space_after_pt=18,
            keep_with_next=True, page_break_before=True,
        ),
        "section_heading": TextStyle(
            font_cn="黑体", font_en="Times New Roman",
            size_pt=14, bold=True, align="left",
            line_spacing_pt=20, line_spacing_rule="exact",
            space_before_pt=12, space_after_pt=6,
            keep_with_next=True,
        ),
        "subsection_heading": TextStyle(
            font_cn="黑体", font_en="Times New Roman",
            size_pt=12, bold=True, align="left",
            line_spacing_pt=20, line_spacing_rule="exact",
            space_before_pt=6, space_after_pt=3,
            keep_with_next=True,
        ),
        "body_text": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=12, bold=False, align="justify",
            first_line_indent_chars=2,
            line_spacing_pt=20, line_spacing_rule="exact",
            space_before_pt=0, space_after_pt=0,
        ),
        "abstract_title": TextStyle(
            font_cn="黑体", font_en="Times New Roman",
            size_pt=16, bold=False, align="center",
            space_before_pt=24, space_after_pt=18,
        ),
        "abstract_body": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=12, bold=False, align="justify",
            first_line_indent_chars=2,
            line_spacing_pt=20, line_spacing_rule="exact",
        ),
        "keyword_label": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=12, bold=True, align="justify",
            line_spacing_pt=20,
        ),
        "keyword": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=12, bold=False, align="justify",
            line_spacing_pt=20,
        ),
        "toc_title": TextStyle(
            font_cn="黑体", font_en="Times New Roman",
            size_pt=16, bold=False, align="center",
            space_before_pt=24, space_after_pt=18,
        ),
        "toc_chapter": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=14, bold=False, align="left",
            line_spacing_pt=14, line_spacing_rule="single",
        ),
        "toc_section": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=12, bold=False, align="left",
            line_spacing_pt=14, line_spacing_rule="single",
            first_line_indent_chars=1,
        ),
        "toc_subsection": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=9, bold=False, align="left",
            line_spacing_pt=14, line_spacing_rule="single",
            first_line_indent_chars=2,
        ),
        "figure_caption": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=10.5, bold=True, align="center",
            line_spacing_pt=16, line_spacing_rule="exact",
            space_before_pt=6, space_after_pt=12,
        ),
        "table_caption": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=10.5, bold=True, align="center",
            line_spacing_pt=16, line_spacing_rule="exact",
            space_before_pt=12, space_after_pt=6,
        ),
        "table_body": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=10.5, bold=False, align="left",
            line_spacing_pt=14, line_spacing_rule="single",
        ),
        "reference_item": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=10.5, bold=False, align="left",
            line_spacing_pt=14, line_spacing_rule="single",
            first_line_indent_chars=0,
        ),
        "acknowledgement_title": TextStyle(
            font_cn="黑体", font_en="Times New Roman",
            size_pt=16, bold=False, align="center",
            space_before_pt=24, space_after_pt=18,
        ),
        "acknowledgement_body": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=12, bold=False, align="justify",
            first_line_indent_chars=2,
            line_spacing_pt=20, line_spacing_rule="exact",
        ),
        "formula": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=12, bold=False, align="center",
            line_spacing_pt=20,
        ),
        "formula_number": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=12, bold=False, align="right",
        ),
        "header_odd": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=9, bold=False, align="center",
        ),
        "header_even": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=9, bold=False, align="center",
        ),
        "footer_page": TextStyle(
            font_cn="Times New Roman", font_en="Times New Roman",
            size_pt=9, bold=False, align="center",
        ),
    },

    "ieee": {
        # IEEE conference/journal format
        "paper_title": TextStyle(
            font_cn="Times New Roman", font_en="Times New Roman",
            size_pt=24, bold=True, align="center",
            line_spacing_pt=28, line_spacing_rule="exact",
            space_before_pt=24, space_after_pt=12,
        ),
        "author": TextStyle(
            font_cn="Times New Roman", font_en="Times New Roman",
            size_pt=10, bold=False, align="center",
            line_spacing_pt=12, line_spacing_rule="exact",
        ),
        "abstract_title": TextStyle(
            font_cn="Times New Roman", font_en="Times New Roman",
            size_pt=10, bold=True, align="left",
            line_spacing_pt=12, line_spacing_rule="exact",
        ),
        "abstract_body": TextStyle(
            font_cn="Times New Roman", font_en="Times New Roman",
            size_pt=9, bold=False, align="justify",
            line_spacing_pt=10, line_spacing_rule="exact",
            first_line_indent_chars=0,
        ),
        "chapter_heading": TextStyle(
            font_cn="Times New Roman", font_en="Times New Roman",
            size_pt=10, bold=True, align="center",
            line_spacing_pt=12, line_spacing_rule="exact",
            space_before_pt=12, space_after_pt=3,
            keep_with_next=True,
        ),
        "section_heading": TextStyle(
            font_cn="Times New Roman", font_en="Times New Roman",
            size_pt=10, bold=True, align="left",
            line_spacing_pt=12, line_spacing_rule="exact",
            space_before_pt=12, space_after_pt=3,
            keep_with_next=True,
        ),
        "subsection_heading": TextStyle(
            font_cn="Times New Roman", font_en="Times New Roman",
            size_pt=10, bold=True, italic=True, align="left",
            line_spacing_pt=12, line_spacing_rule="exact",
            space_before_pt=6, space_after_pt=3,
            keep_with_next=True,
        ),
        "body_text": TextStyle(
            font_cn="Times New Roman", font_en="Times New Roman",
            size_pt=9, bold=False, align="justify",
            first_line_indent_chars=0,
            line_spacing_pt=10, line_spacing_rule="exact",
        ),
        "figure_caption": TextStyle(
            font_cn="Times New Roman", font_en="Times New Roman",
            size_pt=8, bold=False, align="center",
            line_spacing_pt=9, line_spacing_rule="exact",
        ),
        "reference_item": TextStyle(
            font_cn="Times New Roman", font_en="Times New Roman",
            size_pt=8, bold=False, align="left",
            line_spacing_pt=9, line_spacing_rule="exact",
        ),
    },

    "generic": {
        # Generic academic default
        "paper_title": TextStyle(
            font_cn="黑体", font_en="Times New Roman",
            size_pt=22, bold=True, align="center",
            space_before_pt=36, space_after_pt=24,
        ),
        "chapter_heading": TextStyle(
            font_cn="黑体", font_en="Times New Roman",
            size_pt=16, bold=True, align="center",
            space_before_pt=18, space_after_pt=12,
            keep_with_next=True, page_break_before=True,
        ),
        "section_heading": TextStyle(
            font_cn="黑体", font_en="Times New Roman",
            size_pt=14, bold=True, align="left",
            space_before_pt=12, space_after_pt=6,
            keep_with_next=True,
        ),
        "subsection_heading": TextStyle(
            font_cn="黑体", font_en="Times New Roman",
            size_pt=12, bold=True, align="left",
            keep_with_next=True,
        ),
        "body_text": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=12, align="justify",
            first_line_indent_chars=2,
            line_spacing_pt=20,
        ),
        "abstract_body": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=12, align="justify",
            first_line_indent_chars=2,
            line_spacing_pt=20,
        ),
        "reference_item": TextStyle(
            font_cn="宋体", font_en="Times New Roman",
            size_pt=10.5, align="left",
            line_spacing_pt=16,
        ),
    },
}


# ── Style Mapper ───────────────────────────────────────────────────

class StyleMapper:
    """Map semantic roles → typographic styles using named profiles."""

    def __init__(self, profile: str = "sjtu"):
        if profile not in PROFILES:
            available = ", ".join(PROFILES.keys())
            raise ValueError(f"Unknown profile '{profile}'. Available: {available}")
        self.profile = profile
        self._styles = PROFILES[profile]

    def map(self, semantic_role: str) -> Optional[TextStyle]:
        """Get the TextStyle for a semantic role.

        Falls back to body_text for unknown roles.
        """
        if semantic_role in self._styles:
            return self._styles[semantic_role]
        # Fallback
        return self._styles.get("body_text")

    def map_or_raise(self, semantic_role: str) -> TextStyle:
        """Get TextStyle or raise KeyError."""
        return self._styles[semantic_role]

    def has_role(self, semantic_role: str) -> bool:
        return semantic_role in self._styles

    def list_roles(self) -> list:
        return list(self._styles.keys())

    def override(self, semantic_role: str, **kwargs) -> TextStyle:
        """Get a style with field-level overrides."""
        base = self.map(semantic_role)
        return TextStyle.merge(base, kwargs)


# ── Semantic role inference ────────────────────────────────────────

def infer_semantic_role(node_type_name: str, level: int = 0) -> str:
    """Infer a StyleMapper semantic role from a semantic_parser node type and level.

    Maps DocumentNode types to style_mapper roles:
        CHAPTER (level=1)      → "chapter_heading"
        SECTION (level=2)      → "section_heading"
        SUBSECTION (level=3)   → "subsection_heading"
        ABSTRACT              → "abstract_body"
        ABSTRACT_EN           → "abstract_body"
        KEYWORDS              → "keyword"
        FIGURE_CAPTION        → "figure_caption"
        TABLE_CAPTION         → "table_caption"
        REFERENCE_ITEM        → "reference_item"
        ACKNOWLEDGEMENT       → "acknowledgement_body"
        PARAGRAPH             → "body_text"
        TITLE                 → "paper_title"
        TOC                   → "toc_title"
    """
    mapping = {
        "CHAPTER": "chapter_heading",
        "SECTION": "section_heading",
        "SUBSECTION": "subsection_heading",
        "SUBSUBSECTION": "subsection_heading",
        "ABSTRACT": "abstract_body",
        "ABSTRACT_EN": "abstract_body",
        "KEYWORDS": "keyword",
        "FIGURE_CAPTION": "figure_caption",
        "TABLE_CAPTION": "table_caption",
        "TABLE": "table_body",
        "REFERENCE_ITEM": "reference_item",
        "REFERENCE_LIST": "chapter_heading",
        "ACKNOWLEDGEMENT": "acknowledgement_body",
        "PARAGRAPH": "body_text",
        "LIST_ITEM": "body_text",
        "TITLE": "paper_title",
        "TOC": "toc_title",
        "FORMULA": "formula",
        "APPENDIX": "chapter_heading",
    }

    if node_type_name in mapping:
        return mapping[node_type_name]

    # Fallback by level
    if level >= 3:
        return "subsection_heading"
    elif level >= 2:
        return "section_heading"
    elif level >= 1:
        return "chapter_heading"
    return "body_text"


# ── Available profiles ─────────────────────────────────────────────

def available_profiles() -> list:
    return list(PROFILES.keys())


def profile_description(profile: str) -> str:
    descriptions = {
        "sjtu": "上海交通大学学位论文 (2022规范)",
        "ieee": "IEEE 会议/期刊双栏格式",
        "generic": "通用学术论文格式",
    }
    return descriptions.get(profile, profile)
