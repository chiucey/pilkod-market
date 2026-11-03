#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verify.py  —  第一步 ③ 结果核验（免费）

对增强前后的图像做几何与画质核验，回答两个问题：
  1. 增强有没有把比例改坏（增强工具会改变纵横比，且同批逐件不同）
  2. 画质有没有实质提升，值不值得这一次计费

用法:
    python verify.py --src "原图.jpg" --out "增强图.jpg"
    python verify.py --src a.jpg --out b.jpg -o verify.json
"""
import argparse
import hashlib
import json
import os

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
EDGE_WHITE = 252


def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def stats(path, resize_to=None):
    im = Image.open(path)
    if resize_to:
        im = im.resize(resize_to, Image.LANCZOS)
    w, h = im.size
    g = np.asarray(im.convert("L")).astype(np.float32)
    lap = float(np.abs(np.diff(g, axis=0)).mean() + np.abs(np.diff(g, axis=1)).mean())
    edges = [float(g[:3].mean()), float(g[-3:].mean()), float(g[:, :3].mean()), float(g[:, -3:].mean())]
    return {
        "path": os.path.abspath(path), "md5": md5_file(path), "bytes": os.path.getsize(path),
        "width": w, "height": h, "aspect": round(w / h, 5),
        "sharpness": round(lap, 3),
        "gray_mean": round(float(g.mean()), 1),
        "edge_all_white": all(v >= EDGE_WHITE for v in edges),
        "edge_means": [round(v, 1) for v in edges],
    }


def main():
    ap = argparse.ArgumentParser(description="第一步 ③ 结果核验（免费）")
    ap.add_argument("--src", required=True, help="源图/预处理图")
    ap.add_argument("--out", required=True, help="增强结果图")
    ap.add_argument("-o", "--json", default=None, help="核验报告输出路径")
    ap.add_argument("--change-warn", type=float, default=2.0, help="几何变化率警戒线 %%")
    ap.add_argument("--change-fail", type=float, default=5.0, help="几何变化率不可接受线 %%")
    a = ap.parse_args()

    b = stats(a.src)
    f = stats(a.out)

    geo = abs(f["aspect"] - b["aspect"]) / b["aspect"] * 100.0
    if geo <= a.change_warn:
        geo_level = "良好"
    elif geo <= a.change_fail:
        geo_level = "可接受(须在报告中标注)"
    else:
        geo_level = "超限(须人工确认，禁止拉伸修正)"

    # 锐度比较必须同尺寸：增强常伴随超分放大，放大后逐像素锐度天然下降，直接比会误判
    area_ratio = (f["width"] * f["height"]) / float(b["width"] * b["height"])
    norm_note = None
    if area_ratio > 1.2:
        fn = stats(a.out, resize_to=(b["width"], b["height"]))
        sharp_ratio = (fn["sharpness"] / b["sharpness"]) if b["sharpness"] else None
        norm_note = ("增强图为源图的 %.2f 倍面积（%dx%d vs %dx%d），锐度已归一化到同尺寸后比较"
                     % (area_ratio, f["width"], f["height"], b["width"], b["height"]))
    else:
        sharp_ratio = (f["sharpness"] / b["sharpness"]) if b["sharpness"] else None

    if sharp_ratio is None:
        verdict = "C"
    elif geo <= a.change_fail and sharp_ratio >= 1.0:
        verdict = "A"
    elif geo <= a.change_fail:
        verdict = "B"
    else:
        verdict = "C"

    todo = []
    if geo > a.change_warn:
        todo.append("几何变化率 %.2f%%，落版时须按主导边锚定、另一边等比推算，不得沿用增强前的 mm 尺寸"
                    % geo)
    if sharp_ratio is not None and sharp_ratio < 1.0:
        todo.append("锐度未提升（%.2f 倍），考虑换工具或改用本地路径" % sharp_ratio)
    if not f["edge_all_white"]:
        todo.append("增强后四缘非纯白，若下游需要 1:1 落版请先确认边界")

    rep = {
        "before": b, "after": f,
        "geometry_change_pct": round(geo, 3), "geometry_level": geo_level,
        "sharpness_ratio": round(sharp_ratio, 3) if sharp_ratio is not None else None,
        "sharpness_note": norm_note,
        "size_delta_px": [f["width"] - b["width"], f["height"] - b["height"]],
        "verdict": {"level": verdict,
                    "note": {"A": "达标：几何稳定且画质提升",
                             "B": "基本可用：画质提升有限，人工确认",
                             "C": "需人工确认"}[verdict],
                    "todo": todo},
    }
    text = json.dumps(rep, ensure_ascii=False, indent=2)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("verify -> %s" % a.json)
    else:
        print(text)


if __name__ == "__main__":
    main()
