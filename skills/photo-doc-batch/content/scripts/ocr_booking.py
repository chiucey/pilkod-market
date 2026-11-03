#!/usr/bin/env python3
"""
从已裁切的知情同意书第一面 OCR 项目编号（Internal Booking Code），
输出 {page_key: "26CB077"} 映射，同时输出识别失败需人工确认的清单。

用法: python3 ocr_booking.py <crops_dir> [-o out.json]
"""
import os, sys, json, re, subprocess
from PIL import Image, ImageOps


def _ocr(img, langs='eng', psm=6):
    img.save('/tmp/_bk.png')
    return subprocess.run(
        ['tesseract', '/tmp/_bk.png', '-', '-l', langs, '--psm', str(psm)],
        capture_output=True, text=True).stdout


def read_code(png_path, box=(0.55, 0.02, 0.95, 0.09)):
    """Bookin Code 在页面右上角。放大+灰度+增强后多参数 OCR 取最长匹配。"""
    im = Image.open(png_path)
    w, h = im.size
    c = im.crop((int(w*box[0]), int(h*box[1]), int(w*box[2]), int(h*box[3])))
    c = ImageOps.autocontrast(c.resize((c.width*3, c.height*3), Image.LANCZOS).convert('L'))
    cands = []
    for psm in (6, 7, 11):
        t = _ocr(c, 'eng', psm)
        t = t.replace(' ', '').replace('O', '0').replace('o', '0')
        t = t.replace('B8', 'B').replace('8', 'B')          # 纠正 8/B 混淆
        for m in re.findall(r'2[6G]C[B8]0\d{2}', t):
            m = m.replace('G', '6')
            cands.append(m[:7] if len(m) > 7 else m)
    if not cands:
        return None
    from collections import Counter
    return Counter(cands).most_common(1)[0][0]


def main():
    crops = sys.argv[1]
    outp = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '-o' else 'booking_codes.json'
    res, fails = {}, []
    for f in sorted(os.listdir(crops)):
        if not f.endswith('_第一面.jpg'):
            continue
        key = f[:-len('_第一面.jpg')]
        code = read_code(os.path.join(crops, f))
        if code and len(code) == 7:
            res[key] = code
        else:
            fails.append(key)
        print('%-22s %s' % (key, code or 'FAILED'))
    json.dump({'codes': res, 'failed': fails}, open(outp, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\n识别 %d / 失败 %d -> %s' % (len(res), len(fails), outp))
    if fails:
        print('需人工确认:', ', '.join(fails))


if __name__ == '__main__':
    main()
