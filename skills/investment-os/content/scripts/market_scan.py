#!/usr/bin/env python3
"""
涟漪投资操作系统 v15.3 - 市场扫描
五阶段仓位 + 市场情绪 + 仓位建议
零依赖版本
"""
import json, urllib.request, datetime

def fetch(code: str, days: int = 60) -> list:
    url = (f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
           f"/CN_MarketData.getKLineData?symbol={code}&scale=240&ma=no&datalen={days}")
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
            timeout=10
        ) as r:
            d = json.loads(r.read().decode("utf-8"))
            return d if isinstance(d, list) else []
    except: return []

def parse(raw: list) -> list:
    r = []
    for k in raw:
        try:
            r.append({'d': k['day'], 'o': float(k['open']), 'c': float(k['close']),
                      'h': float(k['high']), 'l': float(k['low']), 'v': int(k['volume'])})
        except: pass
    return r

def MA(ks, n, i):
    if i < 0 or i >= len(ks): return ks[i]['c']
    s = max(0, i - n + 1)
    return sum(ks[j]['c'] for j in range(s, i + 1)) / max(1, i - s + 1)

PHASE_INFO = {
    'ice':     {'label': '冰点期', 'color': '🔵', 'max_pos': 0.00,
                'action': '空仓等待', 'desc': '涨停<15家，市场冰点'},
    'start':   {'label': '启动期', 'color': '🟢', 'max_pos': 0.25,
                'action': 'M1首板/M4恐慌试错', 'desc': 'MA5>MA10，趋势初现'},
    'ferment': {'label': '发酵期', 'color': '🟠', 'max_pos': 0.80,
                'action': 'M1-M6全开，重仓持有', 'desc': '主线明确，积极参与'},
    'climax':  {'label': '高潮期', 'color': '🔴', 'max_pos': 0.40,
                'action': 'M5趋势为主，逐步兑现', 'desc': '情绪高潮，小心退潮'},
    'retreat': {'label': '退潮期', 'color': '⚫', 'max_pos': 0.05,
                'action': '全面停止，等待机会', 'desc': '炸板率高，严禁开仓'},
}

if __name__ == "__main__":
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    print("=" * 60)
    print(f"🌊 涟漪 v15.3 市场扫描")
    print(f"   日期: {today}")
    print("=" * 60)

    print("\n加载数据...")
    HS = parse(fetch("sh000001", 60))
    if not HS:
        print("无法获取沪深300数据")
        exit(1)
    print(f"沪深300: {len(HS)}条 {HS[0]['d']}~{HS[-1]['d']}")

    # 最新数据
    latest = HS[-1]
    date = latest['d']
    c, o, h, l = latest['c'], latest['o'], latest['h'], latest['l']
    pct_day = (c - o) / max(0.001, o) * 100

    # MA
    m5 = MA(HS, 5, -1)
    m10 = MA(HS, 10, -1)
    m20 = MA(HS, 20, -1)

    # 涨跌家数估算（用沪深300模拟）
    zt_count = 0; dt_count = 0
    for k in HS[-5:]:
        pct_k = (k['c'] - k['o']) / max(0.001, k['o']) * 100
        if pct_k > 5: zt_count += 1
        elif pct_k < -5: dt_count += 1

    # 波动率
    rets = [(HS[j]['c'] - HS[j-1]['c']) / max(0.001, HS[j-1]['c'])
             for j in range(max(1, len(HS)-20), len(HS))]
    vol = (sum((r - sum(rets)/max(1,len(rets)))**2 for r in rets)**0.5 /
           max(1, len(rets))) if rets else 0

    # 市场阶段判断
    pct_ma = (HS[-1]['c'] - HS[-1]['o']) / max(0.001, HS[-1]['o']) * 100
    if m5 < m10 and pct_ma < -0.5: phase = 'bear'
    elif m5 > m10 and pct_ma > 0.5: phase = 'bull'
    elif vol > 0.015: phase = 'hv'
    else: phase = 'neutral'

    ph_map = {'bear': 'bear', 'bull': 'bull', 'hv': 'climax', 'neutral': 'neutral'}
    ph = ph_map.get(phase, 'neutral')
    # 如果MA多头但大盘跌 = 启动期
    if m5 > m10 and pct_ma < 0: ph = 'start'
    # 如果MA空头但大盘涨 = 高潮期反弹
    if m5 < m10 and pct_ma > 0: ph = 'climax'
    # 如果连续下跌 = 冰点
    recent_5 = [(HS[j]['c'] - HS[j-1]['c'])/max(0.001, HS[j-1]['c']) for j in range(max(1,len(HS)-5), len(HS))]
    if sum(1 for r in recent_5 if r < 0) >= 4: ph = 'ice'

    pi = PHASE_INFO.get(ph, PHASE_INFO['neutral'])

    print(f"\n{'='*60}")
    print(f"📊 市场状态 ({date})")
    print(f"{'='*60}")
    print(f"  沪深300: {c:.2f} ({pct_day:+.2f}%)")
    print(f"  MA5: {m5:.2f} | MA10: {m10:.2f} | MA20: {m20:.2f}")
    print(f"  趋势: {'多头' if m5 > m10 else '空头'}")
    print(f"  波动率: {vol:.4f} ({'高波动' if vol > 0.015 else '正常'})")

    print(f"\n{'='*60}")
    print(f"🔮 市场阶段: {pi['color']} {pi['label']}")
    print(f"{'='*60}")
    print(f"  描述: {pi['desc']}")
    print(f"  仓位上限: {int(pi['max_pos']*100)}%")
    print(f"  操作: {pi['action']}")

    print(f"\n{'='*60}")
    print(f"💡 v15.3 仓位建议")
    print(f"{'='*60}")

    pos_display = int(pi['max_pos'] * 100)
    print(f"\n  【{pi['label']}】仓位上限: {pos_display}%")
    if ph == 'ice':
        print(f"  → 空仓等待，不建仓")
        print(f"  → 涟漪在观察，等待启动信号")
    elif ph == 'start':
        print(f"  → 轻仓试错，只做M1/M4")
        print(f"  → 仓位1-3成，止损要严格")
    elif ph == 'ferment':
        print(f"  → 重仓参与，M1-M6全开")
        print(f"  → 仓位最高8成，积极操作")
        print(f"  → 这是涟漪的主战场！")
    elif ph == 'climax':
        print(f"  → 逐步减仓，只做M5趋势")
        print(f"  → 仓位3-5成，不要追高")
        print(f"  → 注意龙头股退潮风险")
    else:
        print(f"  → 全面停止，等待机会")
        print(f"  → 涟漪在看，但不出手")

    print(f"\n{'='*60}")
    print(f"📡 v15.3 信号预告")
    print(f"{'='*60}")
    sig_list = []
    if ph in ('start', 'ferment'):
        sig_list += ['M1首板(精华)', 'M4恐慌']
    if ph == 'ferment':
        sig_list += ['M2二板', 'M3整理', 'M5金叉', 'M6尾盘']
    if ph == 'climax':
        sig_list += ['M5金叉(趋势)']
    for s in sig_list:
        print(f"  ✓ {s}")

    if not sig_list:
        print(f"  ✗ 当前阶段无推荐信号")

    print(f"\n⚠️ 以上仅为系统分析，不构成投资建议")
    print(f"⚠️ 真实下单须V授权")
