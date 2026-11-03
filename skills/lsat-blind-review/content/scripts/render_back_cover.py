"""
Render LSAT LR Blind Review back cover PNG (A4 @ 300 dpi).

硬约束：所有文字 ≤9pt（per 用户 2026-09-28 反馈）。
ABOUT THIS WORKBOOK 部分（4 段英文正文 + sub-section 标题 + 顶部 logo 行）
总 word count ≤350。

Usage:
    python render_back_cover.py "<subtitle>" /tmp/back_cover.png [2026]

As a library:
    from render_back_cover import render_back_cover
    render_back_cover("PrepTest 01 · Section 3 & 4",
                      Path("/Users/log/LSAT_LR_PT01_back_cover.png"))
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 2481, 3508  # A4 @ 300 dpi

_FONTS = {
    "logo_bold":  "/System/Library/Fonts/Arial Bold.ttf",
    "bold":       "/System/Library/Fonts/Arial Bold.ttf",
    "reg":        "/System/Library/Fonts/Arial.ttf",
}

INK        = "#000000"
INK_LINE   = "#000000"   # 分隔线颜色（黑色 1pt）
SOFT_LINE  = "#999999"   # 备用浅灰分隔线

# 默认正文 4 段（≤350 字总计）。用户可在 back-cover-template.md 改写。
DEFAULT_BODY = {
    "what": (
        "The Blind Review Workbook you are reading is a 7Sage-style "
        "compilation of argument-by-argument analysis for the user's "
        "wrong answers on LSAT PrepTest N, Section X. Part I presents "
        "the original questions; Part II gives a speed table plus a "
        "four-section annotation per question; Part III summarizes "
        "cross-question weakness patterns."
    ),
    "methodology": (
        "Each wrong question is reduced to a four-section annotation: "
        "question type plus task, stimulus structure, why the correct "
        "answer closes the argument, and a transferable pattern that "
        "recurs across LSAT items. Wrong-answer buckets follow the four "
        "canonical capacities: conditional logic, scope control, method "
        "recognition, principle matching."
    ),
    "how": (
        "Read Part I blind without referring to Part II. Then verify "
        "with Part II's speed table and per-question four-section "
        "analysis. Read Part III for cross-question weakness patterns "
        "and a consolidated training checklist."
    ),
    "caveat": (
        "The four-section analysis is one practitioner's opinionated "
        "reading; use it as a study aid, not as the only source of "
        "truth. Where public prep sites disagree, trust them."
    ),
}


def _draw_separator(draw: ImageDraw.ImageDraw, y: int, color: str = INK_LINE,
                    width_px: int = 5) -> None:
    """Horizontal separator (1pt ≈ 5px at 300 dpi)."""
    draw.line([(180, y), (W - 180, y)], fill=color, width=width_px)


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
               max_width_px: int) -> list[str]:
    """Greedy word-wrap to lines that fit within max_width_px."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        candidate = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width_px:
            cur = candidate
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_back_cover(subtitle: str, output_path: Path,
                      year: int | None = None,
                      body: dict | None = None) -> Path:
    """Render a single-page back cover PNG.

    Args:
        subtitle: 例如 "PrepTest 01 · Section 3 & 4"
        output_path: 写入路径
        year: meta 年份；默认取本地系统当前年
        body: 4 段英文正文 dict；默认 DEFAULT_BODY
    """
    if year is None:
        year = datetime.now().year
    if body is None:
        body = DEFAULT_BODY

    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    # ---------- 顶部 (9pt logo + separator) ----------
    f_logo  = ImageFont.truetype(_FONTS["logo_bold"], 9)
    f_reg   = ImageFont.truetype(_FONTS["reg"],      9)
    f_bold  = ImageFont.truetype(_FONTS["bold"],     9)

    y = 200
    draw.text((180, y), "R.Cap",      font=f_logo, fill=INK)
    draw.text((180, y + 16), "LSAT PREP", font=f_reg,  fill=INK)
    y += 40
    _draw_separator(draw, y)

    # ---------- 标题 "ABOUT THIS WORKBOOK" ----------
    y += 20
    draw.text((180, y), "ABOUT THIS WORKBOOK", font=f_bold, fill=INK)
    y += 20

    # ---------- 正文 4 段 ----------
    max_w = W - 360  # 文本宽度，左右各留 180
    line_height = 13  # 9pt + 1.0 line spacing ≈ 13px

    sections = [
        ("WHAT THIS IS",      body["what"]),
        ("METHODOLOGY",       body["methodology"]),
        ("HOW TO USE",        body["how"]),
        ("CAVEAT",            body["caveat"]),
    ]

    for title, text in sections:
        # 标题（粗体 9pt）
        draw.text((180, y), title, font=f_bold, fill=INK)
        y += line_height + 2
        # 正文（regular 9pt，word-wrapped）
        for line in _wrap_text(draw, text, f_reg, max_w):
            draw.text((180, y), line, font=f_reg, fill=INK)
            y += line_height
        y += 6  # 段间空隙

    # ---------- 分隔线 + 版权块 ----------
    y += 10
    _draw_separator(draw, y)
    y += 16

    draw.text((180, y), f"© {year} J. Hu. All rights reserved.",
              font=f_bold, fill=INK)
    y += line_height

    copyright_text = (
        "Unauthorized reproduction or distribution of this document, "
        "in whole or in part, is strictly prohibited without the prior "
        "written consent of the author."
    )
    for line in _wrap_text(draw, copyright_text, f_reg, max_w):
        draw.text((180, y), line, font=f_reg, fill=INK)
        y += line_height

    y += 8
    draw.text((180, y), f"R.Cap · J. Hu · {year}",
              font=f_reg, fill=INK)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG", optimize=True)
    return output_path


def word_count(text: str) -> int:
    return len(text.split())


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python render_back_cover.py <subtitle> <output.png> [year]")
        sys.exit(1)
    subtitle = sys.argv[1]
    out = Path(sys.argv[2])
    year = int(sys.argv[3]) if len(sys.argv) > 3 else None

    # Word-count check (硬约束 ≤350)
    total_words = (
        word_count("ABOUT THIS WORKBOOK")
        + word_count("R.Cap LSAT PREP")
        + word_count(DEFAULT_BODY["what"]) + word_count("WHAT THIS IS")
        + word_count(DEFAULT_BODY["methodology"]) + word_count("METHODOLOGY")
        + word_count(DEFAULT_BODY["how"]) + word_count("HOW TO USE")
        + word_count(DEFAULT_BODY["caveat"]) + word_count("CAVEAT")
    )
    if total_words > 350:
        print(f"FAIL: ABOUT THIS WORKBOOK 部分 word count = {total_words} > 350")
        print("  请精简 DEFAULT_BODY 中的 4 段内容")
        sys.exit(1)

    p = render_back_cover(subtitle, out, year)
    print(f"Saved: {p} ({p.stat().st_size} bytes)")
    print(f"ABOUT THIS WORKBOOK 部分 word count = {total_words} ≤ 350 ✓")