#!/usr/bin/env python3
"""
市场综合监控脚本（修复版）
✅ 强势板块（东方财富/证监会行业）  ✅ 涨停/跌停  ✅ 大资金活跃 TOP30
数据源：新浪财经 + 东方财富（均免费无限）
"""
import urllib.request, json, re, sys
from datetime import datetime

SINA_H = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'}
EM_H   = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Referer': 'https://www.eastmoney.com'}


def sina_get(url):
    req = urllib.request.Request(url, headers=SINA_H)
    with urllib.request.urlopen(req, timeout=12) as r:
        return r.read().decode('utf-8', errors='replace')


# ════════════════════════════════════════════════════════════════
#  1. 强势板块 TOP5 — 东方财富（证监会行业90）
# ════════════════════════════════════════════════════════════════
def get_sector_top5():
    """
    东方财富证监会行业涨幅榜，取前5
    f12=代码 f14=名称 f3=涨跌幅
    """
    url = (
        "https://push2.eastmoney.com/api/qt/clist/get"
        "?fid=f3&po=1&pz=20&pn=1&np=1&fltt=2&invt=2"
        "&fid=f3&fs=m:90+t:2"
        "&fields=f12,f14,f3"
    )
    req = urllib.request.Request(url, headers=EM_H)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode('utf-8', errors='replace')
    except Exception:
        return []

    m = re.search(r'jQuery\((.*)\)', raw, re.DOTALL)
    if not m:
        return []
    try:
        obj = json.loads(m.group(1))
        diff = obj.get('data', {}).get('diff', [])
    except Exception:
        return []

    results = []
    for it in diff:
        try:
            pct = float(it.get('f3', 0))
        except Exception:
            pct = 0
        results.append({'name': it.get('f14', ''), 'pct': round(pct, 2)})

    results.sort(key=lambda x: x['pct'], reverse=True)
    return [{'rank': i+1, **r} for i, r in enumerate(results[:5])]


# ════════════════════════════════════════════════════════════════
#  2. 涨停 / 跌停 — 新浪涨幅榜（全市场A股）
# ════════════════════════════════════════════════════════════════
def get_limit_stocks():
    """
    新浪涨幅榜，分页取全市场，按涨跌幅过滤
    返回 (up_list, down_list)
    """
    all_stocks = {}
    for page in range(1, 10):
        url = (
            f"https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
            f"Market_Center.getHQNodeData?num=80&sort=changepercent&asc=0"
            f"&node=hs_a&symbol=&_s_r_a=page&p={page}"
        )
        try:
            items = json.loads(sina_get(url))
            if not items:
                break
            for it in items:
                sym = it.get('symbol', '')
                if not sym or sym in all_stocks:
                    continue
                try:
                    pct = float(it.get('changepercent') or 0)
                except Exception:
                    pct = 0
                all_stocks[sym] = {
                    'name':  it.get('name', ''),
                    'code':  sym,
                    'price': float(it.get('trade') or 0),
                    'pct':   pct,
                    'amount': float(it.get('amount') or 0),
                }
        except Exception:
            break

    up, down = [], []
    for s in all_stocks.values():
        (up if s['pct'] >= 9.90 else down).append(s)
    return up, down


# ════════════════════════════════════════════════════════════════
#  3. 大资金活跃 TOP30 — 按成交额/市值比排序
# ════════════════════════════════════════════════════════════════
def get_top30_by_ratio():
    """
    新浪成交额排序，取成交额/市值比最高的30只
    市值 mktcap(万元)，成交额 amount(元)
    ratio = amount / (mktcap*10000) — 资金/市值比
    """
    all_stocks = {}
    for page in range(1, 10):
        url = (
            f"https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
            f"Market_Center.getHQNodeData?num=80&sort=amount&asc=0"
            f"&node=hs_a&symbol=&_s_r_a=page&p={page}"
        )
        try:
            items = json.loads(sina_get(url))
            if not items:
                break
            for it in items:
                sym = it.get('symbol', '')
                if not sym or sym in all_stocks:
                    continue
                try:
                    amt    = float(it.get('amount') or 0)
                    mktcap = float(it.get('mktcap') or 0)
                    if mktcap <= 0:
                        continue
                    ratio = amt / (mktcap * 10000)
                except Exception:
                    ratio = 0
                try:
                    pct = float(it.get('changepercent') or 0)
                except Exception:
                    pct = 0
                all_stocks[sym] = {
                    'name':   it.get('name', ''),
                    'code':   sym,
                    'price':  float(it.get('trade') or 0),
                    'pct':    pct,
                    'amount': amt,
                    'ratio':  ratio,
                }
        except Exception:
            break

    return sorted(all_stocks.values(), key=lambda x: x['ratio'], reverse=True)[:30]


# ════════════════════════════════════════════════════════════════
#  工具
# ════════════════════════════════════════════════════════════════
def fmt_yi(yuan):
    try:
        v = float(yuan)
        if abs(v) >= 1e8: return f"{v/1e8:.2f}亿"
        if abs(v) >= 1e4: return f"{v/1e4:.0f}万"
        return f"{v:.0f}元"
    except Exception:
        return str(yuan)


# ════════════════════════════════════════════════════════════════
#  主函数
# ════════════════════════════════════════════════════════════════
def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    print(f"\n{'='*60}")
    print(f"📊 市场综合监控  |  {now}")
    print(f"{'='*60}\n")

    # 1. 强势板块
    print("🏭 强势板块 TOP5（证监会行业）")
    print('─'*44)
    sectors = get_sector_top5()
    if sectors:
        for s in sectors:
            pct = s['pct']
            sign = '+' if pct >= 0 else ''
            print(f"  {s['rank']}. {s['name']:<14} {sign}{pct:.2f}%")
    else:
        print("  ⚠️ 板块数据暂时不可用")

    # 2. 涨停
    print(f"\n🔺 涨停股")
    print('─'*44)
    up, down = get_limit_stocks()
    if up:
        print(f"  共 {len(up)} 只涨停\n")
        for s in sorted(up, key=lambda x: -x['pct'])[:20]:
            pct = s['pct']
            sign = '+' if pct >= 0 else ''
            print(f"  📈 {s['name']:<10} {s['code']}  价{s['price']:.2f}  {sign}{pct:.2f}%")
        if len(up) > 20:
            print(f"  ... 还有 {len(up)-20} 只")
    else:
        print("  暂无涨停数据")

    # 3. 跌停
    print(f"\n🔻 跌停股")
    print('─'*44)
    if down:
        print(f"  共 {len(down)} 只跌停\n")
        for s in sorted(down, key=lambda x: x['pct'])[:20]:
            pct = s['pct']
            print(f"  📉 {s['name']:<10} {s['code']}  价{s['price']:.2f}  {pct:.2f}%")
        if len(down) > 20:
            print(f"  ... 还有 {len(down)-20} 只")
    else:
        print("  暂无跌停数据")

    # 4. 大资金活跃 TOP30
    print(f"\n💰 大资金活跃 TOP30（资金/市值比）")
    print('─'*55)
    stocks = get_top30_by_ratio()
    if stocks:
        for i, s in enumerate(stocks, 1):
            pct = s['pct']
            sign = '+' if pct >= 0 else ''
            ratio_pct = s['ratio'] * 100
            print(f"  {i:2}. {s['name']:<10} {s['code']}  {sign}{pct:.2f}%  "
                  f"成交{fmt_yi(s['amount'])}  占比{ratio_pct:.2f}%")
    else:
        print("  暂无数据")

    print(f"\n{'='*60}\n")


if __name__ == '__main__':
    main()
