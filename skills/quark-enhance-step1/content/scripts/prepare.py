#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
prepare.py  —  第一步 ① 免费预处理（为上云做准备）

做四件事：可选旋正 → 剥离 EXIF → 压缩到载荷限内 → 生成 @args.json（base64）。
全部本地、0 计费。

用法:
    python prepare.py --input "图.jpg" --outdir "./_out" [--rotate 90]
    python prepare.py --input "图.png" --outdir "./_out" --keep-format   # 含底纹件不转 JPEG

要点:
  * EXIF 必须剥离：iPhone 的 Orientation 标记可能是错的，上云会被误用。
  * 含防伪底纹/网纹的文档不要转 JPEG（会破坏细密网纹），用 --keep-format。
  * 大 base64 必须走 @args.json 文件传参（命令行上限约 32KB）。
"""
import argparse
import base64
import json
import os
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def strip_exif(im):
    """返回不带 EXIF 的副本（像素不变）。用 frombytes 避免 getdata 的弃用告警。"""
    im.load()
    out = Image.frombytes(im.mode, im.size, im.tobytes())
    return out


def main():
    ap = argparse.ArgumentParser(description="第一步 ① 免费预处理")
    ap.add_argument("--input", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--rotate", type=int, default=0, choices=[0, 90, 180, 270],
                    help="逆时针旋正角度（以存储像素为准，不要按 EXIF）")
    ap.add_argument("--max-long-edge", type=int, default=800,
                    help="压缩后长边上限。默认 800（与既有口径一致，最省流量）；"
                         "如需保留更多细节可设 1200–1600，但仍须满足载荷 <= 1.4MB")
    ap.add_argument("--max-mb", type=float, default=1.4)
    ap.add_argument("--quality", type=int, default=85)
    ap.add_argument("--keep-format", action="store_true",
                    help="保持源格式（含底纹的 PNG 用它，避免 JPEG 破坏网纹）")
    ap.add_argument("--no-strip-exif", action="store_true")
    ap.add_argument("--name", default=None, help="输出文件名（不含扩展名）")
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)
    src = a.input
    base = a.name or os.path.splitext(os.path.basename(src))[0] + "_prep"

    im = Image.open(src)
    src_fmt, src_w, src_h = im.format, im.width, im.height
    steps = []

    # ① 旋正（以存储像素为准）
    if a.rotate:
        im = im.rotate(a.rotate, expand=True)
        steps.append("rotate_%d_ccw" % a.rotate)

    # ② 剥离 EXIF
    if not a.no_strip_exif:
        im = strip_exif(im)
        steps.append("strip_exif")

    # ③ 压缩：长边超限则等比缩放
    scale = 1.0
    if max(im.size) > a.max_long_edge:
        scale = a.max_long_edge / max(im.size)
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        steps.append("resize_long_edge_%d" % a.max_long_edge)

    # ④ 落盘：格式选择
    lossless_src = os.path.splitext(src)[1].lower() in (".png", ".bmp", ".tif", ".tiff")
    use_png = a.keep_format and lossless_src
    if use_png:
        out_path = os.path.join(a.outdir, base + ".png")
        im.save(out_path, "PNG", optimize=True)
        fmt_used = "PNG"
    else:
        out_path = os.path.join(a.outdir, base + ".jpg")
        im.convert("RGB").save(out_path, "JPEG", quality=a.quality, optimize=True, exif=b"")
        fmt_used = "JPEG q%d" % a.quality
    steps.append("encode_%s" % fmt_used.replace(" ", ""))

    # ⑤ 载荷核算与迭代压缩（超限则降 quality / 缩长边）
    max_bytes = int(a.max_mb * 1024 * 1024)
    payload = open(out_path, "rb").read()
    b64 = base64.b64encode(payload).decode()
    guard = 0
    while len(b64) > int(1.9 * 1024 * 1024) and not use_png and guard < 4:
        guard += 1
        a.quality = max(60, a.quality - 10)
        a.max_long_edge = int(a.max_long_edge * 0.8)
        k = a.max_long_edge / max(im.size)
        if k < 1:
            im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
        im.convert("RGB").save(out_path, "JPEG", quality=a.quality, optimize=True, exif=b"")
        payload = open(out_path, "rb").read()
        b64 = base64.b64encode(payload).decode()
        steps.append("recompress_q%d_edge%d" % (a.quality, a.max_long_edge))

    # ⑥ 生成 @args.json（大 base64 必须走文件）
    args_path = os.path.join(a.outdir, base + ".args.json")
    with open(args_path, "w", encoding="utf-8") as f:
        json.dump({"dataBase64": b64}, f)

    report = {
        "src": os.path.abspath(src),
        "src_format": src_fmt, "src_size_px": [src_w, src_h],
        "out": os.path.abspath(out_path),
        "out_format": fmt_used,
        "out_size_px": [im.width, im.height],
        "scale": round(scale, 4),
        "bytes": len(payload),
        "mb": round(len(payload) / 1048576, 3),
        "base64_kb": round(len(b64) / 1024, 1),
        "base64_within_limit": len(b64) <= int(1.9 * 1024 * 1024),
        "args_json": os.path.abspath(args_path),
        "steps": steps,
        "lossless": use_png and not a.rotate,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if len(b64) > int(1.9 * 1024 * 1024):
        print("警告：base64 仍超约 1.9MB，可能触发 HTTP 413。请调低 --max-long-edge。", file=sys.stderr)


if __name__ == "__main__":
    main()
