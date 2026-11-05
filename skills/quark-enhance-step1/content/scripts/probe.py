#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
probe.py  —  第一步 ⓪ 源件体检（免费）

判件体（扫描件 / 拍摄件 / 文档类图像）、估算 DPI、量四缘、核比例、读 EXIF、算锐度。
输出一份 JSON，供 run_step1.py 与下游归档消费。

用法:
    python probe.py --input "图.jpg"
    python probe.py --input "扫描件.pdf"
    python probe.py --input "目录/"          # 批量，逐件输出

依赖: Pillow, numpy；读 PDF 另需 pypdf + pypdfium2
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

# 标准纸幅/证件幅面（宽 mm, 高 mm）
PAPERS = {
    "A4": (210.0, 297.0),
    "A4-横向": (297.0, 210.0),
    "A5": (148.0, 210.0),
    "A3": (297.0, 420.0),
    "Letter": (215.9, 279.4),
    "ID-1(身份证/银行卡)": (85.6, 54.0),
    "出生证第四版正页": (189.0, 130.0),
}

EDGE_WHITE = 252          # 四缘"纯白"阈值（rgb 灰度等价）
PAPER_TOL = 0.5           # 比例匹配容差 %
DPI_LOCAL = 300           # 本地处理门槛


def md5_file(p, buf=1 << 20):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(buf), b""):
            h.update(b)
    return h.hexdigest()


def match_paper(w_px, h_px):
    """按像素比例匹配标准幅面。返回 (名称, 相对误差%) 或 (None, None)。"""
    if not (w_px and h_px):
        return None, None
    ar = w_px / h_px
    best, best_err = None, None
    for name, (wm, hm) in PAPERS.items():
        for flip in (False, True):
            target = (hm / wm) if flip else (wm / hm)
            err = abs(ar - target) / target * 100.0
            if best_err is None or err < best_err:
                best, best_err = name, err
    if best_err is not None and best_err <= PAPER_TOL:
        return best, round(best_err, 4)
    return None, round(best_err, 4) if best_err is not None else None


def edge_stats(gray):
    """四缘亮度与'是否纯白'。gray: float32 2D array。"""
    top = float(gray[:3].mean())
    bottom = float(gray[-3:].mean())
    left = float(gray[:, :3].mean())
    right = float(gray[:, -3:].mean())
    mn = float(min(gray[:3].min(), gray[-3:].min(), gray[:, :3].min(), gray[:, -3:].min()))
    white = all(v >= EDGE_WHITE for v in (top, bottom, left, right))
    return {"top": round(top, 1), "bottom": round(bottom, 1),
            "left": round(left, 1), "right": round(right, 1),
            "min": round(mn, 1), "all_white": white}


def dark_band(gray, rows=25):
    """测四边是否存在扫描暗带（返回最暗边的均值），供裁边参考。"""
    probes = {
        "top": float(gray[:rows].mean()), "bottom": float(gray[-rows:].mean()),
        "left": float(gray[:, :rows].mean()), "right": float(gray[:, -rows:].mean()),
    }
    edge_mean = float(np.mean([float(gray[:3].mean()), float(gray[-3:].mean()),
                               float(gray[:, :3].mean()), float(gray[:, -3:].mean())]))
    flagged = [k for k, v in probes.items() if v < edge_mean - 40]
    return {"band_means": {k: round(v, 1) for k, v in probes.items()}, "flagged": flagged}


def sharpness(gray):
    """简易锐度：相邻行/列绝对差均值。可用于增强前后的相对比较。"""
    d = np.abs(np.diff(gray, axis=0)).mean() + np.abs(np.diff(gray, axis=1)).mean()
    return round(float(d), 3)


def probe_image(path):
    im = Image.open(path)
    fmt, mode = im.format, im.mode
    w, h = im.size
    ex = im.getexif()
    exif = {
        "orientation": ex.get(274),
        "datetime": ex.get(306) or ex.get(36867) or None,
        "make": ex.get(271), "model": ex.get(272),
    }
    dpi = im.info.get("dpi")
    gray = np.asarray(im.convert("L")).astype(np.float32)

    e = edge_stats(gray)
    paper, paper_err = match_paper(w, h)
    ar = round(w / h, 5)

    # DPI 估算：能匹配标准幅面时，用短边像素 / 短边 mm 反推
    dpi_est = None
    if paper:
        wm, hm = PAPERS[paper]
        short_px, short_mm = (min(w, h), min(wm, hm))
        dpi_est = round(short_px / short_mm * 25.4, 1)
    elif dpi:
        dpi_est = round(float(dpi[0]), 1)

    # 件体判定（三档，中间一档是模糊带，须人工确认）
    edge_min_mean = min(e["top"], e["bottom"], e["left"], e["right"])
    if e["all_white"] and paper:
        kind = "文档类图像"          # 导出图/扫描件，正射无边
    elif e["all_white"]:
        kind = "文档类图像(非标准幅面)"
    elif edge_min_mean >= 245:
        kind = "浅底/白底图像(边界非纯白)"
    else:
        kind = "拍摄件"

    # 建议路径（cloud=None 表示判据落在模糊带，需要目视确认）
    if kind == "拍摄件":
        cloud, reason = True, "拍摄件（四缘均低于 245·疑有透视/背景/光照不均）→ 上云做几何校正"
    elif kind == "浅底/白底图像(边界非纯白)":
        cloud, reason = None, (f"模糊带：四缘均值 {edge_min_mean:.0f}（245–251），"
                               "既可能是合成/导出件（应走本地），也可能是浅色背景的拍摄件（应上云）"
                               "→ 建议目视确认后决定；未能确认时按上云处理（安全侧）")
    elif dpi_est is None:
        cloud, reason = False, "文档类图像但无法估算 DPI → 先本地，必要时人工确认"
    elif dpi_est >= DPI_LOCAL:
        cloud, reason = False, f"文档类图像且折算约 {dpi_est} DPI（>= {DPI_LOCAL}）→ 本地无损，0 计费"
    else:
        cloud, reason = False, (f"文档类图像但折算约 {dpi_est} DPI（< {DPI_LOCAL}）→ "
                                "可本地；如需印刷级请以原件重扫（上云不会增加信息量）")

    return {
        "path": os.path.abspath(path),
        "md5": md5_file(path),
        "size": os.path.getsize(path),
        "format": fmt, "mode": mode,
        "width": w, "height": h, "aspect": ar,
        "dpi_meta": dpi, "dpi_est": dpi_est,
        "std_paper": paper, "std_paper_err_pct": paper_err,
        "edge": e,
        "dark_band": dark_band(gray),
        "gray_mean": round(float(gray.mean()), 1),
        "sharpness": sharpness(gray),
        "exif": exif,
        "kind": kind,
        "cloud_suggest": cloud,
        "cloud_reason": reason,
    }


def probe_pdf(path):
    out = {"path": os.path.abspath(path), "md5": md5_file(path),
           "size": os.path.getsize(path), "kind": "扫描PDF/原生PDF",
           "pages": [], "has_text_layer": False, "producer": None}
    try:
        from pypdf import PdfReader
    except ImportError:
        out["error"] = "需要 pypdf：pip install pypdf"
        return out
    r = PdfReader(path)
    meta = r.metadata or {}
    out["producer"] = " | ".join(str(meta.get(k, "")) for k in ("/Producer", "/Creator")).strip(" |") or None
    total_txt = 0
    for i, pg in enumerate(r.pages):
        mb = pg.mediabox
        wmm, hmm = float(mb.width) / 72 * 25.4, float(mb.height) / 72 * 25.4
        imgs = []
        try:
            xo = pg.get("/Resources", {}).get("/XObject")
            xo = xo.get_object() if hasattr(xo, "get_object") else (xo or {})
            for k in (xo or {}):
                o = xo[k].get_object()
                if o.get("/Subtype") == "/Image":
                    imgs.append({"w": o.get("/Width"), "h": o.get("/Height"),
                                 "filter": str(o.get("/Filter"))})
        except Exception:
            pass
        t = pg.extract_text() or ""
        total_txt += len(t)
        out["pages"].append({"page": i + 1,
                             "mm": [round(wmm, 1), round(hmm, 1)],
                             "rotate": int(pg.get("/Rotate", 0) or 0),
                             "images": imgs})
    out["has_text_layer"] = total_txt > 200
    out["text_chars"] = total_txt
    out["cloud_suggest"] = False
    out["cloud_reason"] = ("既有 PDF：本地处理即可（页面级克隆 / 字节复制 / 只改 MediaBox），"
                           "0 计费；除非调用方明确要求提升画质")
    out["kind"] = "扫描PDF" if not out["has_text_layer"] else "原生PDF(含文字层)"
    return out


def main():
    ap = argparse.ArgumentParser(description="第一步 ⓪ 源件体检（免费）")
    ap.add_argument("--input", required=True, help="图片 / PDF / 目录")
    ap.add_argument("-o", "--out", default=None, help="JSON 输出路径（缺省打印到 stdout）")
    ap.add_argument("--pretty", action="store_true", help="格式化输出")
    a = ap.parse_args()

    src = a.input
    results = []
    if os.path.isdir(src):
        for dp, _, fns in os.walk(src):
            for fn in sorted(fns):
                p = os.path.join(dp, fn)
                if fn.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp")):
                    try:
                        results.append(probe_image(p))
                    except Exception as e:
                        results.append({"path": p, "error": str(e)})
                elif fn.lower().endswith(".pdf"):
                    try:
                        results.append(probe_pdf(p))
                    except Exception as e:
                        results.append({"path": p, "error": str(e)})
    elif src.lower().endswith(".pdf"):
        results = [probe_pdf(src)]
    else:
        results = [probe_image(src)]

    payload = results if len(results) != 1 else results[0]
    text = json.dumps(payload, ensure_ascii=False, indent=2 if a.pretty else None)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print("probe -> %s" % a.out)
    else:
        print(text)


if __name__ == "__main__":
    main()
