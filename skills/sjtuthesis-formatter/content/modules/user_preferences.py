"""
User Preferences — Control Model & Custom Templates
=====================================================

Stores user-configurable preferences for formatting behavior,
including template strictness, page density, margin overrides,
custom template uploads, and protected regions.

Enables commands like:
  "严格遵循学校模板，不允许调整页边距"
  "紧凑排版以节省页数"
  "按照我上传的论文格式进行编排"
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Set


class TemplateStrictness(Enum):
    STRICT = "strict"        # No deviation from template
    NORMAL = "normal"        # Default behavior
    FLEXIBLE = "flexible"    # Allow smart adjustments


class PageDensity(Enum):
    COMPACT = "compact"      # Save pages (tighter spacing)
    NORMAL = "normal"        # Standard spacing
    SPACIOUS = "spacious"    # More white space


# ── Protection regions ────────────────────────────────────────────

@dataclass
class ProtectedRegion:
    """A region of text that should not be modified."""
    start: int               # Character offset
    end: int                 # Character offset
    reason: str              # Why protected
    original_text: str = ""


# ── User template ─────────────────────────────────────────────────

@dataclass
class UserTemplate:
    """A custom template uploaded by the user."""
    name: str
    source_path: str         # Original file path
    style_profile: str = "custom"
    page_margins: dict = field(default_factory=dict)
    heading_font: str = ""
    body_font: str = ""
    rules: List[str] = field(default_factory=list)


# ── Preferences ───────────────────────────────────────────────────

@dataclass
class UserPreferences:
    """Complete user formatting preferences."""
    # Behavior
    strictness: TemplateStrictness = TemplateStrictness.NORMAL
    density: PageDensity = PageDensity.NORMAL

    # Template overrides
    margin_top_cm: Optional[float] = None
    margin_bottom_cm: Optional[float] = None
    margin_left_cm: Optional[float] = None
    margin_right_cm: Optional[float] = None
    body_font_cn: str = ""
    body_font_en: str = ""
    body_font_size_pt: Optional[float] = None
    line_spacing_pt: Optional[float] = None
    first_line_indent_chars: Optional[int] = None

    # Reference format
    reference_format: str = ""            # gbt7714, ieee, acm, ...

    # Content protection
    protect_track_changes: bool = True    # Ask before modifying tracked changes
    protect_comments: bool = True         # Ask before removing comments
    protect_todo_markers: bool = False    # Auto-remove [TODO] markers

    # Special instructions
    extra_rules: List[str] = field(default_factory=list)

    # Custom template
    custom_template: Optional[UserTemplate] = None

    # Protected regions
    protected_regions: List[ProtectedRegion] = field(default_factory=list)

    def to_json(self) -> str:
        d = {
            "strictness": self.strictness.value,
            "density": self.density.value,
            "margin_top_cm": self.margin_top_cm,
            "margin_bottom_cm": self.margin_bottom_cm,
            "margin_left_cm": self.margin_left_cm,
            "margin_right_cm": self.margin_right_cm,
            "body_font_cn": self.body_font_cn,
            "body_font_en": self.body_font_en,
            "body_font_size_pt": self.body_font_size_pt,
            "line_spacing_pt": self.line_spacing_pt,
            "reference_format": self.reference_format,
            "protect_track_changes": self.protect_track_changes,
            "extra_rules": self.extra_rules,
        }
        return json.dumps(d, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "UserPreferences":
        data = json.loads(json_str)
        prefs = cls()
        if "strictness" in data:
            try:
                prefs.strictness = TemplateStrictness(data["strictness"])
            except ValueError:
                pass
        if "density" in data:
            try:
                prefs.density = PageDensity(data["density"])
            except ValueError:
                pass
        for key in ("margin_top_cm", "margin_bottom_cm", "margin_left_cm", "margin_right_cm",
                     "body_font_size_pt", "line_spacing_pt", "first_line_indent_chars"):
            if key in data:
                setattr(prefs, key, data[key])
        for key in ("body_font_cn", "body_font_en", "reference_format"):
            if key in data:
                setattr(prefs, key, data[key])
        if "protect_track_changes" in data:
            prefs.protect_track_changes = data["protect_track_changes"]
        if "extra_rules" in data:
            prefs.extra_rules = data["extra_rules"]
        return prefs

    def add_protected_region(self, start: int, end: int, reason: str, text: str = ""):
        self.protected_regions.append(ProtectedRegion(start, end, reason, text))

    def is_position_protected(self, pos: int) -> bool:
        return any(r.start <= pos <= r.end for r in self.protected_regions)

    # ── Parser for natural language instructions ───────────────

    @classmethod
    def from_instruction(cls, instruction: str) -> "UserPreferences":
        """Parse a natural language formatting instruction into preferences.

        E.g., "严格遵循学校模板，不允许调整页边距"
              "紧凑排版以节省页数"
              "按照这篇论文的格式编排 [attached file]"
        """
        prefs = cls()
        text = instruction.lower()

        # Strictness
        if any(kw in text for kw in ("严格", "不许", "不允许", "必须遵守", "exact")):
            prefs.strictness = TemplateStrictness.STRICT
        elif any(kw in text for kw in ("灵活", "自由", "随意", "flexible")):
            prefs.strictness = TemplateStrictness.FLEXIBLE

        # Density
        if any(kw in text for kw in ("紧凑", "省页", "节省", "compact", "tight")):
            prefs.density = PageDensity.COMPACT
        elif any(kw in text for kw in ("宽松", "舒", "spacious", "loose")):
            prefs.density = PageDensity.SPACIOUS

        # Specific overrides
        margin_match = re.search(r'页边距[上下左右前后]?\s*([\d.]+)\s*cm', text)
        if margin_match:
            val = float(margin_match.group(1))
            if "上" in text:
                prefs.margin_top_cm = val
            if "下" in text:
                prefs.margin_bottom_cm = val
            if "左" in text:
                prefs.margin_left_cm = val
            if "右" in text:
                prefs.margin_right_cm = val

        # Reference format
        if "gbt" in text or "国标" in text or "7714" in text:
            prefs.reference_format = "gbt7714"
        elif "ieee" in text:
            prefs.reference_format = "ieee"

        # Margin protection
        if "页边距" in text and "不允许" in text:
            prefs.extra_rules.append("禁止修改页边距")

        return prefs


# ── Template analysis ─────────────────────────────────────────────

def analyze_template(file_path: Path) -> UserTemplate:
    """Analyze an uploaded template document and extract its style rules.

    Supports .docx and .tex files.
    """
    name = file_path.stem
    ext = file_path.suffix.lower()

    if ext == ".docx":
        return _analyze_docx_template(file_path, name)
    elif ext == ".tex":
        return _analyze_tex_template(file_path, name)
    else:
        return UserTemplate(name=name, source_path=str(file_path))


def _analyze_docx_template(file_path: Path, name: str) -> UserTemplate:
    """Extract style information from a .docx template."""
    try:
        from docx import Document
        doc = Document(str(file_path))
        rules = []
        margins = {}

        section = doc.sections[0] if doc.sections else None
        if section:
            margins = {
                "top_cm": round(section.top_margin.cm, 1) if section.top_margin else None,
                "bottom_cm": round(section.bottom_margin.cm, 1) if section.bottom_margin else None,
                "left_cm": round(section.left_margin.cm, 1) if section.left_margin else None,
                "right_cm": round(section.right_margin.cm, 1) if section.right_margin else None,
            }
            rules.append(f"页边距: 上{margins['top_cm']}cm 下{margins['bottom_cm']}cm "
                        f"左{margins['left_cm']}cm 右{margins['right_cm']}cm")

        # Extract heading fonts from styles
        for style_name in ("Heading 1", "Heading 2", "Heading 3", "Normal"):
            if style_name in doc.styles:
                style = doc.styles[style_name]
                font = style.font
                font_info = f"{style_name}: "
                if font.name:
                    font_info += f"字体={font.name}"
                if font.size:
                    font_info += f" 字号={font.size.pt:.0f}pt"
                if font.bold:
                    font_info += " 加粗"
                rules.append(font_info)

        return UserTemplate(
            name=name,
            source_path=str(file_path),
            style_profile="custom",
            page_margins=margins,
            rules=rules,
        )
    except Exception as e:
        return UserTemplate(name=name, source_path=str(file_path),
                            rules=[f"分析失败: {e}"])


def _analyze_tex_template(file_path: Path, name: str) -> UserTemplate:
    """Extract style information from a .tex template."""
    try:
        content = file_path.read_text("utf-8", errors="ignore")
        rules = []

        # Detect geometry
        geo_match = re.search(r'\\usepackage\[(.*?)\]{geometry}', content)
        if geo_match:
            rules.append(f"页面设置: {geo_match.group(1)}")

        # Detect document class
        cls_match = re.search(r'\\documentclass\[?(.*?)\]?\{(.*?)\}', content)
        if cls_match:
            rules.append(f"文档类: {cls_match.group(2)} [{cls_match.group(1)}]")

        # Detect fonts
        if "SimSun" in content:
            rules.append("中文字体: SimSun (宋体)")
        if "SimHei" in content:
            rules.append("中文字体: SimHei (黑体)")

        return UserTemplate(
            name=name,
            source_path=str(file_path),
            style_profile="custom",
            rules=rules,
        )
    except Exception as e:
        return UserTemplate(name=name, source_path=str(file_path),
                            rules=[f"分析失败: {e}"])
