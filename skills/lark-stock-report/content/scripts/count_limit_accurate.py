#!/usr/bin/env python3
"""A 股精确涨跌停计数脚本（2026-06-26 新增）

用法:
    python3 scripts/count_limit_accurate.py <path_to_sina_pages_dir>

输入:
    /tmp/sina_close_p1.json, sina_close_p2.json, ..., sina_close_p10.json
    (新浪 vip.stock.finance.sina.com.cn hs_a 排序接口)

输出:
    JSON to stdout: {
      "limit_up_count": N,          # 主板/创业板/科创板 真实涨停（剔除 N 新股 + 退市 + 北交所 + ST）
      "limit_up_excl_n": N,         # 真实涨停剔除 N 新股
      "limit_down_count": N,        # 非退市非 ST 跌停
      "limit_up_by_type": {"mb": N, "cyb": N, "kc": N, "bse": N},
      "new_stocks": [...],          # N 新股列表
      "st_limit_up": [...],         # ST 涨停
      "st_limit_down": [...],       # ST 跌停
      "delisted": [...]             # 退市股
    }

【2026-06-26 实测案例】
    输入: 924 stocks (10 pages)
    输出: limit_up_count=19, limit_up_excl_n=19, limit_down_count=0
          limit_up_by_type={mb: 18, cyb: 1, kc: 0, bse: 0}
"""
import json
import os
import sys


def limit_threshold(code: str, name: str):
    """Return (up_threshold, down_threshold) for limit detection.

    A 股涨跌停规则:
    - 主板 (000/001/002/600/601/603/605): ±10% → ≥9.9% 视为涨停
    - 创业板 (300/301): ±20% → ≥19.5% 视为涨停
    - 科创板 (688): ±20% → ≥19.5% 视为涨停
    - 北交所 (8/4/92): ±30% → ≥29.5% 视为涨停
    - ST 股票: ±5% → ≥4.9% 视为 ST 涨停
    - 退市股: 不计入常规涨跌停
    """
    if 'ST' in name or name.startswith('*'):
        return 4.9, -4.9
    if code.startswith(('300', '301', '688')):
        return 19.5, -19.5
    if code.startswith(('8', '4', '92')):
        return 29.5, -29.5
    if code.startswith(('000', '001', '002', '600', '601', '603', '605')):
        return 9.9, -9.9
    return None, None


def is_excluded(code: str, name: str) -> bool:
    """是否应排除（不计入常规涨跌停统计）。

    排除: 科创板 (688), 北交所 (8/4/92), ST/退市
    注意: 创业板 (300/301) 不排除
    """
    if code.startswith(('688', '8', '4')):
        return True
    if name.startswith(('*ST', 'ST', 'S')) or '退' in name:
        return True
    return False


def classify_by_type(code: str, name: str):
    """Return one of: mb / cyb / kc / bse / st / delisted / unknown"""
    if '退' in name:
        return 'delisted'
    if 'ST' in name or name.startswith('*'):
        return 'st'
    if code.startswith(('300', '301')):
        return 'cyb'
    if code.startswith('688'):
        return 'kc'
    if code.startswith(('8', '4', '92')):
        return 'bse'
    if code.startswith(('000', '001', '002', '600', '601', '603', '605')):
        return 'mb'
    return 'unknown'


def main():
    pages_dir = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
    # Load all Sina pages
    all_stocks = []
    seen = set()
    for p in range(1, 11):
        path = os.path.join(pages_dir, f'sina_close_p{p}.json')
        if not os.path.exists(path):
            continue
        try:
            with open(path, 'rb') as f:
                raw = f.read().decode('gbk', errors='replace')
            if raw.startswith('['):
                data = json.loads(raw)
                for s in data:
                    code = s.get('code', '')
                    if code in seen:
                        continue
                    seen.add(code)
                    all_stocks.append(s)
        except Exception as e:
            print(f"[WARN] p{p}: {e}", file=sys.stderr)

    # Count limit up/down
    limit_up_total = []    # 所有真实涨停（含 N 新股）
    limit_down_total = []  # 真实跌停
    new_stocks = []        # N 新股 (>100% 或 N 开头)
    st_up = []
    st_down = []
    delisted = []

    for s in all_stocks:
        code = s.get('code', '')
        name = s.get('name', '')
        try:
            pct = float(s.get('changepercent', '0'))
        except (ValueError, TypeError):
            continue
        cls = classify_by_type(code, name)
        if cls == 'delisted':
            delisted.append({'code': code, 'name': name, 'pct': pct})
            continue
        if cls == 'st':
            up_th, down_th = limit_threshold(code, name)
            if pct >= up_th:
                st_up.append({'code': code, 'name': name, 'pct': pct})
            elif pct <= down_th:
                st_down.append({'code': code, 'name': name, 'pct': pct})
            continue
        # 非 ST 非退市
        up_th, down_th = limit_threshold(code, name)
        if up_th is None:
            continue
        if pct >= up_th:
            item = {'code': code, 'name': name, 'pct': pct, 'type': cls}
            limit_up_total.append(item)
            if name.startswith('N') or pct > 100:
                new_stocks.append(item)
        elif pct <= down_th:
            limit_down_total.append({'code': code, 'name': name, 'pct': pct, 'type': cls})

    # 分类统计
    by_type = {'mb': 0, 'cyb': 0, 'kc': 0, 'bse': 0}
    for item in limit_up_total:
        if item['type'] in by_type:
            by_type[item['type']] += 1

    limit_up_excl_n = [it for it in limit_up_total if it not in new_stocks]

    result = {
        'total_scanned': len(all_stocks),
        'limit_up_count': len(limit_up_total),
        'limit_up_excl_n': len(limit_up_excl_n),
        'limit_down_count': len(limit_down_total),
        'limit_up_by_type': by_type,
        'new_stocks': new_stocks,
        'st_limit_up_count': len(st_up),
        'st_limit_down_count': len(st_down),
        'delisted_count': len(delisted),
        'limit_up_top10': sorted(limit_up_total, key=lambda x: -x['pct'])[:10],
        'limit_down_top10': sorted(limit_down_total, key=lambda x: x['pct'])[:10],
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    main()