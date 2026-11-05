#!/usr/bin/env python3
"""
批量处理手拍照纸质文档：裁切去桌面 -> 手写签名打码 -> 合并 PDF。

用法:
    python3 process.py <config.json> [outdir]

config 结构见 references/config-example.md。
依赖: opencv-python-headless, numpy, img2pdf, Pillow
"""
import json, os, re, sys, glob, shutil, subprocess
import numpy as np
import cv2

# ---------- 读图（忽略 EXIF 方向，保留手机原始像素排列） ----------
def imread_raw(path):
    with open(path, 'rb') as f:
        buf = np.frombuffer(f.read(), np.uint8)
    return cv2.imdecode(buf, cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION)


def imwrite_cn(path, img, quality=95):
    """中文路径安全写出，4:4:4 无色度抽样（文字边缘锐利）。"""
    params = [cv2.IMWRITE_JPEG_QUALITY, quality,
              cv2.IMWRITE_JPEG_SAMPLING_FACTOR,
              cv2.IMWRITE_JPEG_SAMPLING_FACTOR_444]
    ok, buf = cv2.imencode('.jpg', img, params)
    if not ok:
        raise RuntimeError('encode failed: %s' % path)
    with open(path, 'wb') as f:
        f.write(buf.tobytes())


def paper_mask(img, t_rb=20, t_min=110):
    """纸=中性(r-b 小)且够亮。返回 uint8 0/1。"""
    b = img[:, :, 0].astype(np.int16)
    g = img[:, :, 1].astype(np.int16)
    r = img[:, :, 2].astype(np.int16)
    mn = np.minimum(np.minimum(r, g), b)
    m = (((r - b) < t_rb) & (mn > t_min)).astype(np.uint8)
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))


# ---------- 裁切 ----------
def _runs(sig, thr, minlen=1):
    out, s = [], None
    for i, v in enumerate(sig):
        if v > thr and s is None:
            s = i
        elif v <= thr and s is not None:
            if i - s >= minlen:
                out.append((s, i - 1))
            s = None
    if s is not None and len(sig) - s >= minlen:
        out.append((s, len(sig) - 1))
    return out


def crop_pages(img, expect, inset=0.02):
    """
    按期望页数把纸分开，返回每页轴对齐矩形 (x0,y0,x1,y1)，从左到右。
    expect = 该照片应有的页数（来自配置）。以"切准 expect 段"为目标，
    而不是"猜有几页"——粘连、叠纸干扰时仍然能切对。
    内缩 inset 去掉边缘桌面残留；不做透视矫正。
    """
    H, W = img.shape[:2]
    pm = paper_mask(img)
    y0, y1 = int(0.42 * H), int(0.76 * H)
    cp = pm[y0:y1, :].sum(0).astype(np.float32)
    c = np.convolve(cp, np.ones(7, np.float32) / 7, mode='same')
    segs = _runs(c, 0.5 * c.max(), 250) if c.max() > 0 else []

    guard = 0
    while len(segs) < expect and segs and guard < 6:
        guard += 1
        i = int(np.argmax([s[1] - s[0] for s in segs]))
        a, b = segs[i]
        k = np.convolve(cp[a:b + 1], np.ones(31, np.float32) / 31, mode='same')
        lo, hi = len(k) // 5, max(len(k) // 5 + 1, 4 * len(k) // 5)
        j = lo + int(np.argmin(k[lo:hi]))
        segs[i:i + 1] = [(a, a + j), (a + j, b)]
    while len(segs) > expect and guard < 12:
        guard += 1
        w = [s[1] - s[0] for s in segs]
        i = int(np.argmin(w))
        if i + 1 < len(segs):
            segs[i:i + 2] = [(segs[i][0], segs[i + 1][1])]
        else:
            segs.pop()

    if not segs:                                   # 兜底：等分整幅
        segs = [(int(W * i / expect), int(W * (i + 1) / expect) - 1) for i in range(expect)]

    boxes = []
    for (a, b) in segs[:expect]:
        # 垂直边界：段内行投影中"够宽且够高"的连续带才算纸，
        # 否则上方的叠纸/圆盘会被当成纸边带进来。
        strip = pm[:, a:b + 1]
        rp = strip.sum(1).astype(np.float32)
        yr = _runs(rp, strip.shape[1] * 0.5, max(60, int(H * 0.35)))
        if yr:
            yb0, yb1 = max(yr, key=lambda r: r[1] - r[0])
            ya, yb = int(yb0), int(yb1)
        else:                                  # 兜底：取中间带
            ya, yb = int(0.25 * H), int(0.88 * H)
        dx = int((b - a) * inset)
        dy = int((yb - ya) * inset)
        boxes.append((a + dx, max(0, ya + dy), b - dx, min(H - 1, yb - dy)))
    return boxes


def apply_rotation(img, deg):
    if deg == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    if deg == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    if deg == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img


# ---------- 去斜（只在歪得明显时才做） ----------
def estimate_skew(gray, rng=2.5, step=0.2):
    s = cv2.resize(gray, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    s = cv2.GaussianBlur(s, (0, 0), 1.0).astype(np.float32)
    h, w = s.shape
    c = (w / 2, h / 2)
    best = (0.0, -1.0)
    for a in np.arange(-rng, rng + step, step):
        M = cv2.getRotationMatrix2D(c, float(a), 1.0)
        r = cv2.warpAffine(s, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=255)
        p = r.sum(1)
        e = float(((p[1:] - p[:-1]) ** 2).sum())
        if e > best[1]:
            best = (float(a), e)
    return best[0]


def deskew(img, thresh=0.6):
    ang = estimate_skew(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    if abs(ang) < thresh:
        return img, ang
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    out = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LANCZOS4,
                         borderMode=cv2.BORDER_REPLICATE)
    return out, ang


# ---------- 签名打码 ----------
def mask_signature(img, roi, bar, pad_y=0.02):
    """
    roi = [y0,y1,x0,x1] 归一化，签名在页面中的大致区域
    bar = [x0,x1] 黑条在该 roi 宽度内的起止比例（宽松即可，盖住名字为主）
    """
    y0, y1, x0, x1 = roi
    bx0, bx1 = bar
    H, W = img.shape[:2]
    ya, yb = int(H * y0), int(H * y1)
    xa, xb = int(W * x0), int(W * x1)
    lx = xa + int(round(bx0 * (xb - xa)))
    rx = xa + int(round(bx1 * (xb - xa)))
    # 纵向范围：直接铺满签名区，不需要精确贴合笔画
    ty = ya + int(pad_y * (yb - ya))
    by = yb - int(pad_y * (yb - ya))
    cv2.rectangle(img, (lx, ty), (rx, by), (0, 0, 0), -1)
    return img


# ---------- 主流程 ----------
def run(cfg, outdir):
    crops_dir = os.path.join(outdir, 'crops')
    final_dir = os.path.join(outdir, 'pdf')
    os.makedirs(crops_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)

    ow, oh = cfg.get('out_size', [2000, 2829])
    inset = cfg.get('inset', 0.02)
    src_root = cfg['src_root']

    produced = {}          # key -> (crop_path, masked_path)
    manifest = []

    for src in cfg['sources']:
        p = os.path.join(src_root, src['photo'])
        if not os.path.exists(p):
            print('!! 找不到源文件:', p)
            continue
        img = imread_raw(p)
        img = apply_rotation(img, src.get('rotate', 0))
        pages = src['pages']
        boxes = crop_pages(img, expect=len(pages), inset=inset)
        if len(boxes) != len(pages):
            print('!! %s 检出 %d 页，配置写 %d 页' % (src['photo'], len(boxes), len(pages)))
        for box, page in zip(boxes, pages):
            x0, y0, x1, y1 = box
            sub = img[y0:y1, x0:x1]
            sub = cv2.resize(sub, (ow, oh), interpolation=cv2.INTER_AREA
                             if (x1 - x0) > ow else cv2.INTER_LANCZOS4)
            ang = src.get('deskew', True)
            if ang:
                sub, _ = deskew(sub)
            crop_path = os.path.join(crops_dir, page['key'] + '.jpg')
            imwrite_cn(crop_path, sub)

            masked = sub.copy()
            if page.get('mask'):
                masked = mask_signature(masked, page['mask'][:4], page['mask'][4:6])
            m_path = os.path.join(crops_dir, page['key'] + '.masked.jpg')
            imwrite_cn(m_path, masked)

            produced[page['key']] = (crop_path, m_path)
            manifest.append({
                'key': page['key'], 'src': src['photo'],
                'surname': page.get('surname', ''),
                'out_pdf': page.get('pdf_name', ''),
            })

    # ---- 合并 PDF ----
    try:
        import img2pdf
        from pypdf import PdfReader
    except ImportError:
        print('!! 缺 img2pdf / pypdf，跳过 PDF 合并；裁切图已在 %s' % crops_dir)
        return manifest

    A4 = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
    by_key = {m['key']: m for m in manifest}
    docs = cfg.get('documents', [])
    if not docs:
        # 没给 documents 就按 pdf_name / key 各自成单页 PDF
        for m in manifest:
            if not m['out_pdf']:
                continue
            out = os.path.join(final_dir, m['out_pdf'] + '.pdf')
            with open(out, 'wb') as f:
                f.write(img2pdf.convert(produced[m['key']][1],
                                        layout_fun=img2pdf.get_layout_fun(pagesize=A4)))
    else:
        for doc in docs:
            pages, title = doc['pages'], doc.get('pdf_name')
            miss = [k for k in pages if k not in produced]
            if miss:
                print('!! 文档 %s 缺页: %s' % (title, miss))
                continue
            out = os.path.join(final_dir, title + '.pdf')
            with open(out, 'wb') as f:
                f.write(img2pdf.convert([produced[k][1] for k in pages],
                                        layout_fun=img2pdf.get_layout_fun(pagesize=A4)))
            print('PDF:', title, len(PdfReader(out).pages), '页')
    return manifest


def main():
    cfg_path = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else './out'
    with open(cfg_path, encoding='utf-8') as f:
        cfg = json.load(f)
    os.makedirs(outdir, exist_ok=True)
    man = run(cfg, outdir)
    with open(os.path.join(outdir, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
    print('\n产出 %d 页 -> %s' % (len(man), os.path.abspath(outdir)))


if __name__ == '__main__':
    main()