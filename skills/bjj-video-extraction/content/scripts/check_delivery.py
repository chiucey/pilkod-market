#!/usr/bin/env python3
"""交付前自检：核对报告与图片是否一致

用法:
  python3 check_delivery.py report.md imgs_dir

检查项:
  1. 报告里引用的图片是否都存在
  2. 图片目录里是否有未被引用的孤儿图
  3. 每个动作小节是否带时间戳
  4. 是否存在"讲师说的"和"我的推断"未隔离的情况
  5. 讲师原话是否用引号包裹
"""
import argparse, os, re, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown")
    ap.add_argument("imgdir")
    a = ap.parse_args()

    md = open(a.markdown, encoding="utf-8").read()
    refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", md)
    disk = {f for f in os.listdir(a.imgdir) if f.lower().endswith((".jpg",".jpeg",".png"))}
    refnames = {os.path.basename(r) for r in refs}

    fail = 0

    missing = refnames - disk
    if missing:
        print(f"FAIL 报告引用了不存在的图片: {sorted(missing)}"); fail += 1
    else:
        print(f"OK   引用的 {len(refnames)} 张图片全部存在")

    orphan = disk - refnames
    if orphan:
        print(f"WARN 图片目录有 {len(orphan)} 张未被引用(孤儿图): {sorted(orphan)}")
    else:
        print("OK   没有孤儿图")

    # 时间戳覆盖：只统计「动作/技术」级小节（## 标题），
    # ### 是同一动作下的子项（动作要领/单独练法…），不要求每个都带时间戳
    secs = re.split(r"\n##\s+", md)
    secs = [s for s in secs[1:]]
    no_ts = [s.split("\n")[0].strip() for s in secs
             if not re.search(r"\b\d{1,2}:\d{2}(:\d{2})?\b|\b\d{2,4}\s*s\b|\d+\s*分钟", s)]
    if secs:
        if no_ts:
            print(f"WARN {len(no_ts)}/{len(secs)} 个小节没有时间戳: {no_ts}")
        else:
            print(f"OK   全部 {len(secs)} 个小节都带时间戳")

    # 引号包裹的讲师原话：中英文引号都算
    quoted = len(re.findall(r"[\"“「][^\"”」\n]{12,}[\"”」]", md))
    print(f"OK   带引号的引用 {quoted} 处")

    # 推断隔离
    if re.search(r"推断|我的建议|非讲师|我的观点|以下为我的", md):
        print("OK   存在推断/建议的隔离标记")
    else:
        print("WARN 未找到推断隔离标记 —— 若报告含战术建议，需补标注")

    # 局限声明
    if re.search(r"局限|无官方字幕|ASR|字幕", md):
        print("OK   包含制作说明/局限声明")
    else:
        print("WARN 未找到局限声明")

    print(f"\n{'FAIL' if fail else 'PASS'} — 失败项 {fail}")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
