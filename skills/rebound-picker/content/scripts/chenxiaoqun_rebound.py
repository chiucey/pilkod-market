#!/usr/bin/env python3
"""
超跌反弹选股脚本 v3（腾讯API版）
"""

import urllib.request
import time

HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"}

def tencent_quote(codes):
    if isinstance(codes, str):
        codes = [codes]
    url = f"https://qt.gtimg.cn/q={','.join(codes)}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=8) as r:
        raw = r.read().decode("gbk", errors="replace")
    results = {}
    for line in raw.strip().split("\n"):
        if "=" not in line:
            continue
        raw_code = line.split("=")[0].strip()  # e.g. "v_sh601600"
        data_str = line.split("=")[1].strip('"\n; ')  # e.g. "1~中国铝业~..."
        parts = data_str.split("~")
        if len(parts) > 32:
            code = raw_code.replace("v_", "")  # "sh601600"
            results[code] = {
                "name": parts[1],
                "price": float(parts[3]) if parts[3] else 0,
                "yclose": float(parts[4]) if parts[4] else 0,
                "open": float(parts[5]) if parts[5] else 0,
                "high": float(parts[33]) if parts[33] else 0,
                "low": float(parts[34]) if parts[34] else 0,
                "changePct": float(parts[32]) if parts[32] else 0,
            }
    return results

def main():
    print("=== 超跌反弹选股扫描 | 腾讯API ===")
    
    # 候选板块代表股票（主板）
    stocks = [
        ("sh601600", "中国铝业"),
        ("sz000858", "五粮液"),
        ("sh601012", "隆基绿能"),
        ("sz002475", "立讯精密"),
        ("sh600036", "招商银行"),
        ("sz000333", "美的集团"),
        ("sh601318", "中国平安"),
        ("sh600519", "贵州茅台"),
        ("sz002594", "比亚迪"),
        ("sh601166", "兴业银行"),
        ("sz000002", "万科A"),
        ("sh600900", "长江电力"),
    ]
    
    codes = [s[0] for s in stocks]
    data = tencent_quote(codes)
    
    results = []
    for code, ref_name in stocks:
        if code not in data:
            continue
        d = data[code]
        name = d["name"] or ref_name
        price = d["price"]
        yclose = d["yclose"]
        change = d["changePct"]
        high = d["high"]
        
        if yclose > 0 and price > 0:
            drop_from_high = (high - price) / high * 100 if high > 0 else 0
            results.append({
                "name": name, "code": code,
                "price": price, "yclose": yclose,
                "changePct": change,
                "dropFromHigh": drop_from_high,
            })
    
    # 按今日跌幅排序（找空头衰竭候选）
    results.sort(key=lambda x: x["changePct"])
    
    print(f"{'名称':<10} {'代码':<10} {'现价':<8} {'今日涨跌':<10} {'距今日高点':<12}")
    print("-" * 55)
    for r in results:
        print(f"{r['name']:<10} {r['code']:<10} {r['price']:<8.2f} {r['changePct']:>+7.2f}%   {r['dropFromHigh']:>+7.2f}%")
    
    print()
    print("=== 超跌候选（今日跌幅大 + 从高点跌幅深）===")
    strong = [r for r in results if r["changePct"] < -2 and r["dropFromHigh"] > 10]
    strong.sort(key=lambda x: x["dropFromHigh"], reverse=True)
    
    for i, r in enumerate(strong[:5], 1):
        stars = "⭐⭐⭐" if r["dropFromHigh"] >= 30 else "⭐⭐" if r["dropFromHigh"] >= 20 else "⭐"
        print(f"{i}. {r['name']}({r['code']}): 今日{r['changePct']:.1f}% | 从高点跌{r['dropFromHigh']:.1f}% {stars}")

if __name__ == "__main__":
    main()
