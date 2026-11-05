#!/usr/bin/env python3
"""
按项目编号（Booking Code）归类打包：每个 code 一个目录，
内含 知情同意书/ 与 支付凭证/ 两个子目录。

命名规则（方案二）：
    {姓氏}_{文档名}_{BookingCode}.pdf
同一 code 内撞名时加序号后缀：(2) (3) ...
撞名项按 sort_key（用户给的编号）升序排列，保证顺序稳定可复现。

用法:
    python3 package.py --pdf-dir ./out/pdf \
        --codes booking_codes.json \
        --surnames surnames.json \
        --vouchers ./支付凭证目录 [--voucher-codes vcodes.json] \
        -o out.zip
"""
import os, sys, json, glob, argparse, zipfile, shutil, unicodedata


def uniq_name(base, used):
    """base 已含后缀的扩展名之外部分；撞名加 (2)(3)"""
    if base not in used:
        used.add(base)
        return base
    stem, ext = os.path.splitext(base)
    i = 2
    while f'{stem}({i}){ext}' in used:
        i += 1
    name = f'{stem}({i}){ext}'
    used.add(name)
    return name


def pdf_voucher_code(path, lang='chi_sim+eng'):
    """支付凭证右下角印有项目编号，小字需放大后 OCR"""
    from PIL import Image, ImageOps
    import subprocess, re, tempfile
    from collections import Counter
    tmp = tempfile.mkdtemp()
    subprocess.run(['pdfimages', '-png', path, os.path.join(tmp, 'v')], check=False)
    pngs = glob.glob(os.path.join(tmp, '*.png'))
    cands = []
    for p in pngs:
        im = Image.open(p)
        w, h = im.size
        for box in ((0.55, 0.55, 1.0, 1.0), (0.45, 0.45, 1.0, 1.0), (0.0, 0.4, 1.0, 1.0)):
            c = im.crop((int(w*box[0]), int(h*box[1]), int(w*box[2]), int(h*box[3])))
            c = ImageOps.autocontrast(c.resize((c.width*3, c.height*3), Image.LANCZOS).convert('L'))
            c.save('/tmp/_vc.png')
            t = subprocess.run(['tesseract', '/tmp/_vc.png', '-', '-l', 'eng', '--psm', '6'],
                               capture_output=True, text=True).stdout
            t = t.replace(' ', '').replace('O', '0').replace('8', 'B')
            cands += [x[:7].replace('G', '6') for x in re.findall(r'2[6G]C[B8]0\d{2}', t)]
    shutil.rmtree(tmp, ignore_errors=True)
    if not cands:
        return None
    return Counter(cands).most_common(1)[0][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf-dir', required=True)
    ap.add_argument('--codes', required=True, help='ocr_booking.py 产出')
    ap.add_argument('--surnames', required=True, help='{page_key: 姓}')
    ap.add_argument('--vouchers', default=None)
    ap.add_argument('--voucher-codes', default=None, help='{凭证文件名: code}，不给则自动 OCR')
    ap.add_argument('--sort', default='sort_key.json', help='{page_key: 排序号}')
    ap.add_argument('-o', '--out', required=True)
    a = ap.parse_args()

    codes = json.load(open(a.codes, encoding='utf-8'))['codes']
    surnames = json.load(open(a.surnames, encoding='utf-8'))
    sortk = json.load(open(a.sort, encoding='utf-8')) if os.path.exists(a.sort) else {}

    # code -> [(sort_key, 源文件, 目标名)]
    per_code = {}
    used = {}
    missing = []
    for key, code in sorted(codes.items(), key=lambda kv: sortk.get(kv[0], 999)):
        sur = surnames.get(key)
        if not sur:
            missing.append(key)
            continue
        src = os.path.join(a.pdf_dir, key + '.pdf')
        if not os.path.exists(src):
            missing.append(key + '(无PDF)')
            continue
        nm = uniq_name(f'{sur}_知情同意书_{code}.pdf', used.setdefault(code, set()))
        per_code.setdefault(code, []).append((sortk.get(key, 999), src, nm))

    # 支付凭证
    if a.vouchers:
        vc = json.load(open(a.voucher_codes, encoding='utf-8')) if a.voucher_codes else {}
        vused = {}
        for f in sorted(os.listdir(a.vouchers)):
            if not f.lower().endswith('.pdf'):
                continue
            code = vc.get(f) or pdf_voucher_code(os.path.join(a.vouchers, f))
            if not code:
                print('!! 凭证未识别出编号:', f)
                continue
            nm = uniq_name(f, vused.setdefault(code, set()))
            per_code.setdefault(code, []).append((0, os.path.join(a.vouchers, f), nm, '凭证'))

    if missing:
        print('!! 缺姓氏/缺文件，需向用户确认:', missing)

    if os.path.exists(a.out):
        os.remove(a.out)
    with zipfile.ZipFile(a.out, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for code in sorted(per_code):
            for item in per_code[code]:
                kind = item[3] if len(item) > 3 else '同意书'
                sub = '支付凭证' if kind == '凭证' else '知情同意书'
                arc = f'{code}/{sub}/{item[2]}'
                zi = zipfile.ZipInfo(arc, date_time=(2026, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.flag_bits |= 0x800
                zi.external_attr = 0o644 << 16
                with open(item[1], 'rb') as fh:
                    z.writestr(zi, fh.read())
    print('\n打包 %d 个 code -> %s' % (len(per_code), a.out))
    for code in sorted(per_code):
        n = sum(1 for i in per_code[code] if len(i) == 3)
        print('  %s : %d 份同意书, %d 份凭证' %
              (code, n, len(per_code[code]) - n))


if __name__ == '__main__':
    main()
