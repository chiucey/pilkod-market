#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_table.py — 把存量的面经卡片导出为「多维表格 CSV」（效果3的本地示意）

把 cards/*.yaml 的每张卡拍平成一行，字段与飞书多维表格的"表字段"一一对应，
这样可直接导入飞书多维表格 / Excel，支持筛选、统计、按字段透视。

表头（==多维表格字段==）：
  ID, 公司, 岗位, 轮次, 日期, 结果, 面试官角色, 能力标签列表,
  高频问题TOP(逗号分隔), 自评最高分, 优点摘要, 短板摘要, 改进建议

用法：
    python export_table.py                 # 输出 cards→ mianjing/卡片表.csv
    python export_table.py --out x.csv
"""

import os
import csv
import glob
import argparse

try:
    import yaml
except ImportError:
    yaml = None

BASE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(BASE, "..", "cards")
OUT = os.path.join(BASE, "..", "卡片表.csv")


def first_company(comp):
    return str(comp).split("·")[0].split("(")[0].strip()


def load():
    rows = []
    if yaml is None:
        return rows
    for p in sorted(glob.glob(os.path.join(CARDS, "I*.yaml"))):
        try:
            c = yaml.safe_load(open(p, encoding="utf-8"))
        except Exception:
            continue
        inter = c.get("interview", {}) or {}
        res = c.get("result", {}) or {}
        ref = c.get("reflection", {}) or {}
        comp = first_company(inter.get("company", ""))
        cid = c.get("id") or os.path.basename(p).split("_")[0]
        # 高频问题 top2
        qs = [q.get("question", "") for q in (c.get("questions", []) or [])
              if isinstance(q, dict) and q.get("question")]
        topq = " / ".join(qs[:2]) if qs else ""
        # 自评最高分
        scores = [int(q.get("score", 0) or 0) for q in (c.get("questions", []) or [])
                  if isinstance(q, dict)]
        best = max(scores) if scores else 0
        skills = " / ".join(str(s) for s in (c.get("skills", []) or []))
        rows.append([
            cid, comp, inter.get("position", ""), inter.get("round", ""),
            inter.get("date", ""), res.get("outcome", ""), inter.get("interviewer_role", ""),
            skills, topq, best,
            str(ref.get("strength", ""))[:80], str(ref.get("weakness", ""))[:80],
            str(ref.get("improvement", ""))[:80],
        ])
    return rows


HEADER = ["ID", "公司", "岗位", "轮次", "日期", "结果", "面试官角色",
          "能力标签", "高频问题TOP", "自评最高分", "优点摘要", "短板摘要", "改进建议"]


def main():
    ap = argparse.ArgumentParser(description="导出卡片为多维表格CSV")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    rows = load()
    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)
    print(f"[OK] 已导出 {len(rows)} 张卡片 -> {args.out}")
    return 0


if __name__ == "__main__":
    exit(main())
