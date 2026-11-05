#!/usr/bin/env python3
"""Sina Market_Center.getHQNodeData 字段类型安全处理 + 涨跌停 + V-reversal 计算

【2026-06-29 实战发现】Sina API 数字字段是 STRINGS, 不是 floats:
- s.get("trade") 返回 string 类型
- s.get("changepercent") 返回 string 类型
- s.get("open") 返回 string 类型
- 直接做算术运算会抛 TypeError: unsupported operand type(s)

【铁律】所有 Sina API 处理必须用 to_float() 包装:
  from sina_field_type_safe import to_float
  trade = to_float(s.get("trade", 0))

【用法】:
  # 处理 sina p1-p5 + bottom100.json
  python3 scripts/sina_field_type_safe.py /tmp/idx_data

  # 输出: /tmp/idx_data/sina_parsed.json
  {
    "total_scanned": 387,
    "count_3_5": 133,
    "count_5_plus": 98,
    "v_reversal_pct": 74.44,
    "quad_counts": {"neg_open": 13, "low_open": 86, "flat_open": 28, "high_open": 6},
    "limit_up_count": 19,
    "limit_up_excl_st_n": 12,
    "limit_down_count": 0,
    "sector_concentration": {"半导体/科技": 0.25, "化工/材料": 0.25, "其他主板": 0.5},
    "top_5pct_stocks": [...],
    "top_3_5pct_stocks": [...]
  }
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

# ST 过滤
ST_PAT = re.compile(r"^(\*?ST|S[A-Z]?ST|^ST)")


def to_float(v):
    """Sina API 数字字段 → float 包装. 字符串/空值/无效值都安全返回 0.0"""
    if v is None or v == "":
        return 0.0
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


def is_st(name):
    """判定 ST 股 (含 *ST / S*ST / ST)"""
    return bool(ST_PAT.search(name))


def limit_threshold(code, name, side="up"):
    """精确涨停/跌停阈值 (主板 9.9%, 创业/科创 19.5%, 北交 29.5%, ST 4.9%)"""
    if code.startswith("300") or code.startswith("688"):
        th = 19.5
    elif code.startswith("8") or code.startswith("4") or code.startswith("920"):
        th = 29.5
    elif is_st(name):
        th = 4.9
    else:
        th = 9.9
    return -th if side == "down" else th


def classify_sector(code, name):
    """按代码 + 名称归类主线"""
    if code.startswith("300"):
        return "创业板"
    if code.startswith("688"):
        return "科创板"
    if code.startswith(("8", "4", "920")):
        return "北交所"
    if is_st(name):
        return "ST"
    if any(k in name for k in ["半导体", "光电", "微电", "科技", "硅", "芯片", "集成", "电子"]):
        return "半导体/科技"
    if any(k in name for k in ["氟", "化工", "化学", "材料", "陶瓷", "锂"]):
        return "化工/材料"
    if any(k in name for k in ["医", "药", "健康"]):
        return "医药"
    if any(k in name for k in ["玻璃", "玻纤", "建材", "水泥", "钢"]):
        return "建材/材料"
    return "其他主板"


def parse_sina_pages(idx_dir, pages=range(1, 6)):
    """解析 Sina p1-p5 涨幅榜 (返回 list of dicts)"""
    results = []
    for p in pages:
        path = Path(idx_dir) / f"sina_p{p}.json"
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        for s in data:
            code = s.get("code", "")
            name = s.get("name", "")
            # 排除科创板(688) 和北交所(8/4/920 开头) 用于 3-5% 涨幅股分析
            if code.startswith("688") or code.startswith("8") or code.startswith("4") or code.startswith("920"):
                continue
            if is_st(name):
                continue
            trade = to_float(s.get("trade", 0))
            pct = to_float(s.get("changepercent", 0))
            opn = to_float(s.get("open", 0))
            if not trade or not opn:
                continue
            results.append({
                "symbol": s.get("symbol", ""),
                "code": code,
                "name": name,
                "trade": trade,
                "pct": pct,
                "open": opn,
            })
    return results


def parse_push2_bottom(idx_dir, filename="bottom100.json"):
    """解析 push2 bottom100 跌幅榜"""
    path = Path(idx_dir) / filename
    if not path.exists():
        return []
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception:
        return []
    start = raw.find("{")
    if start < 0:
        return []
    try:
        d = json.loads(raw[start:])
    except Exception:
        return []
    items = d.get("data", {}).get("diff", [])
    results = []
    for it in items:
        code = it.get("f12", "")
        name = it.get("f14", "")
        pct = it.get("f3", 0) / 100.0  # push2 f3 已经是 float, 不需要 to_float
        results.append({"code": code, "name": name, "pct": pct})
    return results


def compute_v_reversal(stocks):
    """算 4 象限 + V-reversal %"""
    target = [s for s in stocks if 3.0 <= s["pct"] < 5.0]
    quad = {"neg_open": 0, "low_open": 0, "flat_open": 0, "high_open": 0}
    details = []
    for r in target:
        prev_close = r["trade"] / (1 + r["pct"] / 100.0)
        open_pct = (r["open"] / prev_close - 1) * 100
        if open_pct < 0:
            quad["neg_open"] += 1
            cat = "负开(<0%)"
        elif open_pct < 3:
            quad["low_open"] += 1
            cat = "低开(0-3%)"
        elif open_pct < 5:
            quad["flat_open"] += 1
            cat = "平开(3-5%)"
        else:
            quad["high_open"] += 1
            cat = "高开(≥5%)"
        details.append({**r, "open_pct": round(open_pct, 2), "cat": cat})
    total = len(details)
    v_pct = (quad["neg_open"] + quad["low_open"]) / total * 100 if total else 0
    return {
        "count_3_5": total,
        "quad_counts": quad,
        "v_reversal_pct": round(v_pct, 2),
        "details": details[:30],  # 限制明细数
    }


def compute_limits(stocks, bottom_stocks):
    """精确涨跌停 + 主线集中度 (排除 ST + N 新股)"""
    limit_up = []
    new_stocks = []
    for s in stocks:
        code = s["code"]
        name = s["name"]
        pct = s["pct"]
        if pct >= limit_threshold(code, name, "up"):
            # N 新股判定 (名称 N 开头或 C 开头, 或 pct > 100%)
            if name.startswith("N") or name.startswith("C") or pct > 100:
                new_stocks.append(s)
                continue
            limit_up.append(s)

    limit_down = []
    for s in bottom_stocks:
        code = s["code"]
        name = s["name"]
        pct = s["pct"]
        if name.startswith("N") or name.startswith("C"):
            continue
        if pct <= limit_threshold(code, name, "down"):
            limit_down.append(s)

    # 主线集中度 (基于 limit_up)
    sectors = Counter()
    for s in limit_up:
        sectors[classify_sector(s["code"], s["name"])] += 1
    sector_conc = {k: round(v / max(1, len(limit_up)), 3) for k, v in sectors.most_common()}

    return {
        "limit_up_count": len(limit_up),
        "limit_up_incl_st_n": len(limit_up) + len(new_stocks),
        "limit_up_excl_st_n": len(limit_up),
        "limit_down_count": len(limit_down),
        "new_stocks": new_stocks[:10],
        "st_limit_up_count": sum(1 for s in limit_up if is_st(s["name"])),
        "sector_concentration": sector_conc,
        "limit_up_top10": sorted(limit_up, key=lambda x: -x["pct"])[:10],
        "limit_down_top10": sorted(limit_down, key=lambda x: x["pct"])[:10],
    }


def main():
    if len(sys.argv) < 2:
        idx_dir = "/tmp/idx_data"
    else:
        idx_dir = sys.argv[1]

    idx_path = Path(idx_dir)
    if not idx_path.exists():
        print(f"[ERROR] 目录不存在: {idx_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] 扫描 sina p1-p5 + bottom100 @ {idx_dir}")
    sina_stocks = parse_sina_pages(idx_dir)
    bottom_stocks = parse_push2_bottom(idx_dir)
    print(f"[INFO] sina 涨幅榜: {len(sina_stocks)} 只 (排除 ST/科创/北交)")
    print(f"[INFO] push2 bottom100: {len(bottom_stocks)} 只")

    # V-reversal
    v = compute_v_reversal(sina_stocks)
    print(f"[INFO] 3-5% 涨幅股: {v['count_3_5']} 只, V-reversal: {v['v_reversal_pct']}%")
    print(f"[INFO] 4 象限: {v['quad_counts']}")

    # 涨跌停
    lim = compute_limits(sina_stocks, bottom_stocks)
    print(f"[INFO] 涨停 (含 ST/N): {lim['limit_up_incl_st_n']}, 涨停 (剔 ST/N): {lim['limit_up_excl_st_n']}")
    print(f"[INFO] 跌停: {lim['limit_down_count']}")
    print(f"[INFO] 涨停主线: {lim['sector_concentration']}")

    # Top 5% 涨幅股
    top5 = [s for s in sina_stocks if s["pct"] >= 5.0]
    top5pct = sorted(top5, key=lambda x: -x["pct"])[:30]

    result = {
        "total_scanned": len(sina_stocks),
        "count_5_plus": len(top5),
        **v,
        **lim,
        "top_5pct_stocks": top5pct,
    }

    output_path = idx_path / "sina_parsed.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[OK] 输出: {output_path}")


if __name__ == "__main__":
    main()
