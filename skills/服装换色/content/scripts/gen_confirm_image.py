#!/usr/bin/env python3
"""
gen_confirm_image.py — 生成换色选区确认图片（PNG）
适用于不支持 embed 的渠道（如 Linkfox / Feishu）

输入 JSON 格式与 gen_confirm_gallery.py 相同（stdin）
输出（stdout）：图片绝对路径
"""

import json, sys, os, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── 字体 ──────────────────────────────────────────────────────────────────────
FONT_REG  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_REG
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# ── 颜色（RGB 元组）──────────────────────────────────────────────────────────
BG          = (247, 248, 250)
WHITE       = (255, 255, 255)
DARK        = (26,  26,  26 )
MID         = (85,  85,  85 )
LIGHT       = (160, 160, 160)
BORDER      = (232, 232, 232)
WARN_BG     = (254, 243, 199)
WARN_TXT    = (217, 119,   6)
FOOTER_BG   = (230, 244, 255)
FOOTER_TXT  = (22,  119, 255)
SEC_TXT     = (150, 150, 150)
TARGET_BG   = (240, 245, 255)
TARGET_BD   = (214, 228, 255)
SWATCH_OL   = (200, 200, 200)   # swatch outline

# ── 布局常量 ──────────────────────────────────────────────────────────────────
W        = 600
PAD      = 20
CPAD     = 14   # card inner padding
CARD_R   = 10   # card corner radius
TAG_R    = 6
TAG_PH   = 10   # tag horizontal padding
TAG_PV   = 5    # tag vertical padding
TAG_H    = 26
TAG_GAP  = 6
ROW_GAP  = 6
SEC_GAP  = 10   # gap between sections


# ── 工具函数 ──────────────────────────────────────────────────────────────────
def hex_rgb(h: str) -> tuple:
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def tw(draw: ImageDraw.ImageDraw, text: str, f) -> int:
    return draw.textbbox((0, 0), text, font=f)[2]

def rr(draw, x1, y1, x2, y2, r, fill, outline=None):
    """Filled rounded rectangle; optional 1-px outline."""
    draw.rectangle([x1+r, y1,   x2-r, y2  ], fill=fill)
    draw.rectangle([x1,   y1+r, x2,   y2-r], fill=fill)
    for cx, cy in [(x1, y1), (x2-2*r, y1), (x1, y2-2*r), (x2-2*r, y2-2*r)]:
        draw.ellipse([cx, cy, cx+2*r, cy+2*r], fill=fill)
    if outline:
        draw.arc([x1,     y1,     x1+2*r, y1+2*r], 180, 270, fill=outline)
        draw.arc([x2-2*r, y1,     x2,     y1+2*r], 270, 360, fill=outline)
        draw.arc([x1,     y2-2*r, x1+2*r, y2    ],  90, 180, fill=outline)
        draw.arc([x2-2*r, y2-2*r, x2,     y2    ],   0,  90, fill=outline)
        draw.line([x1+r, y1,   x2-r, y1  ], fill=outline)
        draw.line([x1+r, y2,   x2-r, y2  ], fill=outline)
        draw.line([x1,   y1+r, x1,   y2-r], fill=outline)
        draw.line([x2,   y1+r, x2,   y2-r], fill=outline)

def swatch(draw, cx, cy, r, color_hex):
    """Filled circle color swatch."""
    draw.ellipse([cx-r, cy-r, cx+r, cy+r],
                 fill=hex_rgb(color_hex), outline=SWATCH_OL)

def tag_rows(draw, items, f, content_w):
    """Pack items into rows; return list of rows (each row = list of (text, w))."""
    rows, cur_row, cur_w = [], [], 0
    for item in items:
        tw_ = tw(draw, item, f) + 2 * TAG_PH
        need = tw_ + (TAG_GAP if cur_row else 0)
        if cur_w + need > content_w and cur_row:
            rows.append(cur_row)
            cur_row, cur_w = [(item, tw_)], tw_
        else:
            cur_row.append((item, tw_))
            cur_w += need
    if cur_row:
        rows.append(cur_row)
    return rows


# ── 主渲染 ────────────────────────────────────────────────────────────────────
def render(data: dict) -> Image.Image:
    # Pre-load fonts
    f_title  = _font(18, bold=True)
    f_sec    = _font(11, bold=True)
    f_body   = _font(13)
    f_bold   = _font(13, bold=True)
    f_small  = _font(11)
    f_mono   = _font(10)
    f_warn   = _font(11)

    # Tall scratch canvas; crop at end
    canvas = Image.new('RGB', (W, 2400), BG)
    draw   = ImageDraw.Draw(canvas)

    y = PAD

    # ── 标题 ──────────────────────────────────────────────────────────────────
    draw.text((PAD, y), "换色选区确认", font=f_title, fill=DARK)
    y += 28 + 14

    # ── 原图缩略图 ─────────────────────────────────────────────────────────────
    images = [p for p in data.get("images", []) if os.path.exists(p)]
    if images:
        THUMB = 120
        x = PAD
        for img_path in images[:4]:
            try:
                thumb = Image.open(img_path).convert('RGB')
                thumb.thumbnail((THUMB, THUMB))
                card_w = THUMB + 4
                card_h = THUMB + 22
                rr(draw, x, y, x + card_w, y + card_h, 8, WHITE)
                ox = x + 2 + (THUMB - thumb.width)  // 2
                oy = y + 2 + (THUMB - thumb.height) // 2
                canvas.paste(thumb, (ox, oy))
                label = Path(img_path).name[:12]
                draw.text((x + 2, y + THUMB + 6), label, font=f_mono, fill=LIGHT)
                x += card_w + 10
            except Exception:
                pass
        y += THUMB + 22 + SEC_GAP

    # ── 将换色的项目 ───────────────────────────────────────────────────────────
    change_items  = data.get("change_items", [])
    target_colors = data.get("target_colors", [])
    SWATCH_R = 13

    if change_items:
        card_x1, card_x2 = PAD, W - PAD
        card_y1 = y

        # Measure card height
        ch = CPAD + 16 + 10   # section title
        for item in change_items:
            ch += 2 * SWATCH_R + 10   # row
            if item.get("warning"):
                ch += 22              # warning badge
        ch += CPAD

        rr(draw, card_x1, card_y1, card_x2, card_y1 + ch, CARD_R, WHITE, BORDER)

        iy = card_y1 + CPAD
        draw.text((card_x1 + CPAD, iy), "将换色的项目", font=f_sec, fill=SEC_TXT)
        iy += 16 + 10

        for i, item in enumerate(change_items):
            if i > 0:
                draw.line([card_x1 + CPAD, iy, card_x2 - CPAD, iy], fill=BORDER)
                iy += 1

            ix = card_x1 + CPAD
            mid_y = iy + SWATCH_R + 4

            # Current color swatch
            swatch(draw, ix + SWATCH_R, mid_y, SWATCH_R, item.get("current_hex", "#cccccc"))
            ix += 2 * SWATCH_R + 8

            # Arrow
            arrow = "→"
            draw.text((ix, mid_y - 9), arrow, font=f_body, fill=LIGHT)
            ix += tw(draw, arrow, f_body) + 8

            # Target swatches
            for tc in target_colors:
                swatch(draw, ix + SWATCH_R, mid_y, SWATCH_R, tc.get("hex", "#cccccc"))
                ix += 2 * SWATCH_R + 5
            ix += 6

            # Item name
            draw.text((ix, mid_y - 9), item.get("name", ""), font=f_bold, fill=DARK)
            iy += 2 * SWATCH_R + 10

            # Warning badge
            if item.get("warning"):
                badge = f"! {item['warning']}"
                bw = tw(draw, badge, f_warn) + 2 * TAG_PH
                rr(draw, card_x1 + CPAD, iy, card_x1 + CPAD + bw, iy + 18, 4, WARN_BG)
                draw.text((card_x1 + CPAD + TAG_PH, iy + 2), badge, font=f_warn, fill=WARN_TXT)
                iy += 22

        y = card_y1 + ch + SEC_GAP

    # ── 目标颜色 ───────────────────────────────────────────────────────────────
    if target_colors:
        card_x1, card_x2 = PAD, W - PAD
        card_y1 = y
        BIG = 44
        ch = CPAD + 16 + 10 + BIG + 16 + 4 + CPAD

        rr(draw, card_x1, card_y1, card_x2, card_y1 + ch, CARD_R, TARGET_BG, TARGET_BD)

        iy = card_y1 + CPAD
        draw.text((card_x1 + CPAD, iy), "目标颜色", font=f_sec, fill=SEC_TXT)
        iy += 16 + 10

        ix = card_x1 + CPAD
        for tc in target_colors:
            rr(draw, ix, iy, ix + BIG, iy + BIG, 8, hex_rgb(tc.get("hex", "#cccccc")))
            draw.text((ix, iy + BIG + 4),  tc.get("name", ""), font=f_small, fill=MID)
            draw.text((ix, iy + BIG + 18), tc.get("hex",  ""), font=f_mono,  fill=LIGHT)
            ix += BIG + 20

        y = card_y1 + ch + SEC_GAP

    # ── 保留不变的项目 ─────────────────────────────────────────────────────────
    preserve = data.get("preserve_items", [])
    if preserve:
        card_x1, card_x2 = PAD, W - PAD
        card_y1 = y
        content_w = card_x2 - card_x1 - 2 * CPAD

        rows = tag_rows(draw, preserve, f_small, content_w)
        ch = CPAD + 16 + 10 + len(rows) * (TAG_H + ROW_GAP) - ROW_GAP + CPAD

        rr(draw, card_x1, card_y1, card_x2, card_y1 + ch, CARD_R, WHITE, BORDER)

        iy = card_y1 + CPAD
        draw.text((card_x1 + CPAD, iy), "保留不变的项目", font=f_sec, fill=SEC_TXT)
        iy += 16 + 10

        for row in rows:
            ix = card_x1 + CPAD
            for text, tw_ in row:
                rr(draw, ix, iy, ix + tw_, iy + TAG_H, TAG_R, (240, 240, 240))
                draw.text((ix + TAG_PH, iy + TAG_PV), text, font=f_small, fill=MID)
                ix += tw_ + TAG_GAP
            iy += TAG_H + ROW_GAP

        y = card_y1 + ch + SEC_GAP

    # ── 底部提示 ───────────────────────────────────────────────────────────────
    footer = "以上换色范围是否正确？如需调整请直接告知，确认后立即执行。"
    fh = 40
    rr(draw, PAD, y, W - PAD, y + fh, 8, FOOTER_BG)
    draw.text((PAD + CPAD, y + 12), footer, font=f_small, fill=FOOTER_TXT)
    y += fh + PAD

    return canvas.crop((0, 0, W, y))


def main():
    data = json.load(sys.stdin)
    img  = render(data)
    out  = f"/tmp/fuzhuang-confirm-{int(time.time())}.png"
    img.save(out, 'PNG')
    print(out)


if __name__ == "__main__":
    main()
