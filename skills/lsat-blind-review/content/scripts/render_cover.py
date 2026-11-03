"""
Render LSAT LR Blind Review cover PNG (A4 @ 300 dpi).

Usage (as a script):
    python render_cover.py "PrepTest 01 · Section 3 & 4" /tmp/cover.png [2026]

Usage (as a library):
    from render_cover import render_cover
    from pathlib import Path
    render_cover("PrepTest 01 · Section 3 & 4",
                 Path("/Users/log/LSAT_LR_PT01_cover.png"))

Design: see references/cover-template.md.
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 2481, 3508  # A4 @ 300 dpi

_FONTS = {
    "logo": "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "bold": "/System/Library/Fonts/Arial Bold.ttf",
    "reg":  "/System/Library/Fonts/Arial.ttf",
}

# Palette
INK        = "#000000"
INK_SOFT   = "#666666"
INK_GREY   = "#888888"
INK_LIGHT  = "#bbbbbb"
INK_PALE   = "#dcdcdc"
SWOOSH     = "#d9d9d9"


def _draw_open_book(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """Stylized open book viewed from above.

    Anatomy (only 3 page-stack layers — front + 2 back layers — for clarity):
      - 2 outer pages spreading from a central spine (V / fan shape)
      - 2 inner page-curves on each side, stacked toward the spine to give
        depth (book block thickness)
      - 3 horizontal "text" lines on each side of the front page
    """
    half_w = 470
    half_h = 240
    top_spine   = (cx,        cy - 70)
    bot_spine   = (cx,        cy + 60)
    top_left    = (cx - half_w, cy - half_h)
    top_right   = (cx + half_w, cy - half_h)
    bot_left    = (cx - half_w, cy + half_h)
    bot_right   = (cx + half_w, cy + half_h)

    # Page stack layers — 3 nested V-shapes (front + 2 back), drawn back-to-front
    stack_specs = [
        # (shrink, color, width)
        (32, INK_PALE, 4),  # back-most (lightest)
        (16, INK_LIGHT, 4),
        (0,  INK_GREY,  8),  # front-most (darkest)
    ]
    for shrink, color, w in stack_specs:
        ts = (top_spine[0],            top_spine[1] + shrink)
        bs = (bot_spine[0],            bot_spine[1] - shrink)
        tl = (top_left[0]  + shrink,   top_left[1]  + shrink // 2)
        tr = (top_right[0] - shrink,   top_right[1] + shrink // 2)
        bl = (bot_left[0]  + shrink,   bot_left[1]  - shrink // 2)
        br = (bot_right[0] - shrink,   bot_right[1] - shrink // 2)

        # Left page outline
        draw.line([tl, ts], fill=color, width=w)
        draw.line([tl, bl], fill=color, width=w)
        draw.line([bl, bs], fill=color, width=w)
        # Right page outline
        draw.line([tr, ts], fill=color, width=w)
        draw.line([tr, br], fill=color, width=w)
        draw.line([br, bs], fill=color, width=w)

    # Spine emphasis on front page
    draw.line([top_spine, bot_spine], fill=INK_SOFT, width=6)

    # Text-line decorations on the front page (3 short horizontal lines
    # on each side to suggest printed text)
    line_color = INK_LIGHT
    for y_offset in (-20, 10, 40):
        y = cy + y_offset
        # Left page: 1 short line
        draw.line([(cx - 320, y), (cx - 180, y)], fill=line_color, width=3)
        draw.line([(cx - 160, y), (cx - 50,  y)], fill=line_color, width=3)
        # Right page: 1 short line
        draw.line([(cx + 50,  y), (cx + 160, y)], fill=line_color, width=3)
        draw.line([(cx + 180, y), (cx + 320, y)], fill=line_color, width=3)


def render_cover(subtitle: str, output_path: Path,
                 year: int | None = None) -> Path:
    """Render a single-page cover PNG.

    Args:
        subtitle: 例如 "PrepTest 01 · Section 3 & 4"
        output_path: 写入路径
        year: meta 年份；默认取本地系统当前年
    """
    if year is None:
        year = datetime.now().year

    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    # Background: 2 light-gray arcs (decorative swoosh)
    draw.arc([W * 0.4, -H * 0.15, W * 1.2, H * 0.7],
             start=180, end=270, fill=SWOOSH, width=80)
    draw.arc([-W * 0.2, H * 0.55, W * 0.7, H * 1.15],
             start=0, end=90, fill=SWOOSH, width=60)

    # Logo (top-left) — proper line spacing between [R.Cap] and LSAT PREP
    f_logo    = ImageFont.truetype(_FONTS["logo"], 110)
    f_sublogo = ImageFont.truetype(_FONTS["reg"],  38)
    draw.text((180,  220), "[R.Cap]",   font=f_logo,    fill=INK)
    draw.text((180,  420), "LSAT PREP", font=f_sublogo, fill=INK)

    # Main title
    f_lsat = ImageFont.truetype(_FONTS["logo"], 360)
    draw.text((180, 1240), "LSAT", font=f_lsat, fill=INK)

    # Subtitle (parameterized)
    f_prep = ImageFont.truetype(_FONTS["bold"], 80)
    draw.text((180, 1860), subtitle, font=f_prep, fill=INK)
    f_ver = ImageFont.truetype(_FONTS["reg"], 50)
    draw.text((180, 2020), "Blind Review", font=f_ver, fill=INK)

    # Open-book silhouette (bottom-right) — fan shape with stacked page layers
    _draw_open_book(draw, cx=W - 540, cy=H - 950)

    # Bottom meta
    f_meta = ImageFont.truetype(_FONTS["reg"], 32)
    draw.text((180, H - 180),
              f"R.Cap · J. Hu · Blind Review · {year}",
              font=f_meta, fill=INK_SOFT)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG", optimize=True)
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python render_cover.py <subtitle> <output.png> [year]")
        sys.exit(1)
    subtitle = sys.argv[1]
    out = Path(sys.argv[2])
    year = int(sys.argv[3]) if len(sys.argv) > 3 else None
    p = render_cover(subtitle, out, year)
    print(f"Saved: {p} ({p.stat().st_size} bytes)")