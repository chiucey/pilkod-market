#!/usr/bin/env python3
"""Parse push2 top/bottom 100 breadth JSONs and output a clean summary.

Use case (2026-06-25 09:30 实战):
- 9:30 阶段 push2 pz=200 实际只返回 100 (隐式上限)
- 要拿全市场涨跌停需要 po=1 (top 100 涨幅) + po=0 (bottom 100 跌幅)
- 两次独立请求 → 各自 100 items → 合并成 breadth summary

Usage:
    python3 scripts/parse_push2_breadth.py /tmp/idx_data/top200_gainers.json /tmp/idx_data/bottom200_losers.json
    # Or use defaults if files are at /tmp/idx_data/{top200_gainers,bottom200_losers}.json

Output (stdout):
    === 9:30 阶段市场宽度摘要 (top 100 涨幅 + bottom 100 跌幅) ===
    Total scanned: 200
    涨停(>=9.5%): 23
    跌停(<=-9.5%): 3 (含退市/特殊: 1)
    涨跌停比: 23:3 = 7.67:1
"""
import json
import os
import sys


def parse_push2_json(path):
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return []
    with open(path) as f:
        raw = f.read()
    start = raw.find("{")
    if start < 0:
        return []
    try:
        d = json.loads(raw[start:])
    except Exception as e:
        print(f"[WARN] JSON parse err in {path}: {e}")
        return []
    items = d.get("data", {}).get("diff", []) if d.get("data") else []
    out = []
    for it in items:
        try:
            out.append({
                "code": it.get("f12", "") or "",
                "name": it.get("name", it.get("f14", "")) or "",
                "pct": float(it.get("f3", 0) or 0),
            })
        except Exception:
            continue
    return out


def is_special(x):
    """退市/特殊股识别 — 创业板ST±20%, 主板±10%, 退市股."""
    return (x["name"].endswith("退") or
            x["pct"] in (-10.71, 10.71, -20.0, 20.0) or
            "*ST" in x["name"].upper())


def categorize(items, asc=False):
    """asc=False: gainers; asc=True: losers."""
    clean = [x for x in items if not is_special(x)]
    special = [x for x in items if is_special(x)]
    if asc:
        limit = sum(1 for x in clean if x["pct"] <= -9.5)
        near_5_9 = sum(1 for x in clean if -9.5 < x["pct"] <= -5)
        near_3_5 = sum(1 for x in clean if -5 < x["pct"] <= -3)
    else:
        limit = sum(1 for x in clean if x["pct"] >= 9.5)
        near_5_9 = sum(1 for x in clean if 5 <= x["pct"] < 9.5)
        near_3_5 = sum(1 for x in clean if 3 <= x["pct"] < 5)
    return {
        "total": len(items),
        "clean": len(clean),
        "special_count": len(special),
        "limit_count": limit,
        "near_5_9_count": near_5_9,
        "near_3_5_count": near_3_5,
        "special": special,
    }


def main():
    gainers_path = "/tmp/idx_data/top200_gainers.json"
    losers_path = "/tmp/idx_data/bottom200_losers.json"
    if len(sys.argv) >= 2:
        gainers_path = sys.argv[1]
    if len(sys.argv) >= 3:
        losers_path = sys.argv[2]

    print(f"=== 9:30 阶段市场宽度摘要 (top 100 涨幅 + bottom 100 跌幅) ===")
    print(f"  Gainers JSON: {gainers_path}")
    print(f"  Losers JSON:  {losers_path}")
    print()

    gainers = parse_push2_json(gainers_path)
    losers = parse_push2_json(losers_path)
    if not gainers and not losers:
        print("[ERROR] No data found, both JSONs empty or missing")
        return

    g_stats = categorize(gainers, asc=False)
    l_stats = categorize(losers, asc=True)

    print(f"  Top 100 涨幅榜 ({len(gainers)} items):")
    print(f"    涨停 (>=9.5%): {g_stats['limit_count']}")
    print(f"    5-9.5% 涨: {g_stats['near_5_9_count']}")
    print(f"    3-5% 涨: {g_stats['near_3_5_count']}")
    print(f"    退市/特殊 (excl): {g_stats['special_count']}")
    if g_stats["special"]:
        print(f"    特殊样本: {[(x['name'], x['pct']) for x in g_stats['special'][:3]]}")
    print()
    print(f"  Bottom 100 跌幅榜 ({len(losers)} items):")
    print(f"    跌停 (<=-9.5%): {l_stats['limit_count']}")
    print(f"    -9.5% to -5%: {l_stats['near_5_9_count']}")
    print(f"    -5% to -3%: {l_stats['near_3_5_count']}")
    print(f"    退市/特殊 (excl): {l_stats['special_count']}")
    if l_stats["special"]:
        print(f"    特殊样本: {[(x['name'], x['pct']) for x in l_stats['special'][:3]]}")
    print()

    if g_stats["limit_count"] and l_stats["limit_count"]:
        ratio = g_stats["limit_count"] / l_stats["limit_count"]
        print(f"** 涨跌停比 (clean): {g_stats['limit_count']} : {l_stats['limit_count']} = {ratio:.2f} : 1 **")
    elif l_stats["limit_count"] == 0:
        print(f"** 涨跌停比: {g_stats['limit_count']} : 0 (实质全涨停) **")

    if gainers:
        g_max = max(x["pct"] for x in gainers)
        g_min = min(x["pct"] for x in gainers)
        print(f"  Top 100 范围: {g_min:.2f}% ~ {g_max:.2f}%")
    if losers:
        l_max = max(x["pct"] for x in losers)
        l_min = min(x["pct"] for x in losers)
        print(f"  Bottom 100 范围: {l_min:.2f}% ~ {l_max:.2f}%")
    print()

    if g_stats["clean"] and l_stats["clean"]:
        top_all_pos = all(x["pct"] > 0 for x in gainers if not is_special(x))
        bottom_all_neg = all(x["pct"] < 0 for x in losers if not is_special(x))
        print(f"  Top 100 全 positive: {top_all_pos}")
        print(f"  Bottom 100 全 negative: {bottom_all_neg}")
        if top_all_pos and bottom_all_neg:
            print("  → 市场宽度\"撕裂\" 格局 (top 全红, bottom 全绿)")
        elif top_all_pos and not bottom_all_neg:
            print("  → 市场宽度\"普涨\" 格局 (top 红, bottom 也有红)")
        elif not top_all_pos and bottom_all_neg:
            print("  → 市场宽度\"普跌\" 格局 (top 有绿, bottom 全绿)")
        else:
            print("  → 市场宽度\"震荡\" 格局 (top 绿 + bottom 红, 弱背离)")
    print()

    if gainers:
        print("  Top 10 涨幅:")
        for i, x in enumerate(gainers[:10]):
            print(f"    {i+1:2d}. {x['name']:10s} ({x['code']:6s})  {x['pct']:+.2f}%")
    print()

    if losers:
        print("  Bottom 10 跌幅:")
        for i, x in enumerate(losers[:10]):
            print(f"    {i+1:2d}. {x['name']:10s} ({x['code']:6s})  {x['pct']:+.2f}%")
    print()

    if g_stats["limit_count"] in range(10, 31) and l_stats["limit_count"] in range(1, 6):
        print("  📌 §26 温和修复区间: 涨停 10-30 + 跌停 1-5 ✓")


if __name__ == "__main__":
    main()
