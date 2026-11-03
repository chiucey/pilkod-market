#!/usr/bin/env python3
"""Build a labelled side-by-side comparison plate on a paper-toned ground.

Usage:
  python3 make_plate.py -o out.jpg \
      --panel photo.jpg:实拍原片:photograph \
      --panel ink.png:江南水乡路:"after Wu · Jiangnan" \
      --title 吴冠中笔下的江南 --subtitle "一幅实拍照片 · 水墨语言的转译"

Each --panel is IMAGE[:CN_LABEL[:EN_LABEL]]. Panels are scaled to equal height.
Requires Pillow.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

PAPER = (247, 244, 236)
INK = (46, 44, 40)
GREY = (135, 130, 122)
RULE = (216, 211, 201)

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Songti.ttc",   # macOS
    "/System/Library/Fonts/STHeiti Medium.ttc",        # macOS fallback
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",  # Linux
    "/usr/share/fonts/truetype/arphic/uming.ttc",      # Linux fallback
    r"C:\Windows\Fonts\simsun.ttc",                    # Windows
]


def resolve_font(explicit):
    for path in ([explicit] if explicit else []) + FONT_CANDIDATES:
        if path and os.path.exists(path):
            return path
    sys.exit("No CJK font found. Pass one with --font.")


def parse_panel(spec):
    parts = spec.split(":")
    path = parts[0]
    if not os.path.isfile(path):
        sys.exit(f"Panel image not found: {path}")
    return path, (parts[1] if len(parts) > 1 else ""), (parts[2] if len(parts) > 2 else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", action="append", required=True,
                    help="IMAGE[:CN_LABEL[:EN_LABEL]] — repeat per panel")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--height", type=int, default=1400, help="panel height in px")
    ap.add_argument("--gap", type=int, default=42)
    ap.add_argument("--margin", type=int, default=64)
    ap.add_argument("--font", default=None)
    args = ap.parse_args()

    font_path = resolve_font(args.font)

    def font(size):
        return ImageFont.truetype(font_path, size)

    panels = [parse_panel(p) for p in args.panel]
    has_labels = any(cn or en for _, cn, en in panels)
    has_title = bool(args.title or args.subtitle)

    H = args.height
    images = []
    for path, _, _ in panels:
        im = Image.open(path).convert("RGB")
        images.append(im.resize((max(1, int(im.width * H / im.height)), H), Image.LANCZOS))

    cap = 104 if has_labels else 0
    bot = 180 if has_title else (args.margin if has_labels else args.margin)

    total_w = args.margin * 2 + sum(i.width for i in images) + args.gap * (len(images) - 1)
    total_h = args.margin + H + cap + bot

    canvas = Image.new("RGB", (total_w, total_h), PAPER)
    draw = ImageDraw.Draw(canvas)

    f_cn, f_en = font(38), font(23)
    x = args.margin
    for im, (_, cn, en) in zip(images, panels):
        canvas.paste(im, (x, args.margin))
        if cn or en:
            draw.line([(x, args.margin + H + 12), (x + im.width, args.margin + H + 12)],
                      fill=RULE, width=2)
        if cn:
            w = draw.textlength(cn, font=f_cn)
            draw.text((x + (im.width - w) / 2, args.margin + H + 32), cn, font=f_cn, fill=INK)
        if en:
            w = draw.textlength(en, font=f_en)
            draw.text((x + (im.width - w) / 2, args.margin + H + 82), en, font=f_en, fill=GREY)
        x += im.width + args.gap

    if has_title:
        ty = args.margin + H + cap + 26
        if args.title:
            f_t = font(50)
            w = draw.textlength(args.title, font=f_t)
            draw.text(((total_w - w) / 2, ty), args.title, font=f_t, fill=INK)
        if args.subtitle:
            f_s = font(25)
            w = draw.textlength(args.subtitle, font=f_s)
            draw.text(((total_w - w) / 2, ty + (72 if args.title else 0)),
                      args.subtitle, font=f_s, fill=GREY)

    canvas.save(args.output, quality=95)
    print(f"saved {args.output} {canvas.size}")


if __name__ == "__main__":
    main()
