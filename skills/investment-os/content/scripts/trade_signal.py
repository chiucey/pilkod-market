#!/usr/bin/env python3
"""
涟漪投资操作系统 v15.3 - 交易信号识别
六信号买点 + 五阶段仓位 + v15.3参数
零依赖版本
"""
import json, urllib.request
from typing import List, Dict, Tuple, Optional

# ============================================================
# 35只核心股
# ============================================================
CORE_35 = [
    ("sh600036","招商银行"),("sh601318","中国平安"),("sh600016","民生银行"),
    ("sh600028","中国石化"),("sh600900","长江电力"),("sh601668","中国建筑"),
    ("sh600031","三一重工"),("sh600887","伊利股份"),("sh601012","隆基绿能"),
    ("sh600276","恒瑞医药"),("sh603259","药明康德"),("sh600690","海尔智家"),
    ("sz002475","立讯精密"),("sz000333","美的集团"),("sz002594","比亚迪"),
    ("sz300750","宁德时代"),("sh601888","中国中免"),("sh600519","贵州茅台"),
    ("sz300059","东方财富"),("sz300122","智飞生物"),("sz300760","迈瑞医疗"),
    ("sh688008","澜起科技"),("sh688111","金山办公"),("sz300124","汇川技术"),
    ("sz300142","沃森生物"),("sh688012","中微公司"),("sh688388","晶科能源"),
    ("sh688505","复旦张江"),("sz300015","爱尔眼科"),("sh688036","传音控股"),
    ("sz300033","锐捷网络"),("sh688981","中芯国际"),("sz300274","阳光电源"),
    ("sh688256","寒武纪"),("sh688522","纳芯微"),
]

# v15.3信号参数
SIGNAL_PARAMS = {
    'M1首板': {'hold_days': 2, 'take_profit': 0.15, 'stop_loss': 0.05, 'trailing': 0.08, 'pos': 0.80, 'cf_base': 92},
    'M2二板': {'hold_days': 5, 'take_profit': 0.22, 'stop_loss': 0.05, 'trailing': 0.12, 'pos': 0.80, 'cf_base': 88},
    'M3整理': {'hold_days': 7, 'take_profit': 0.25, 'stop_loss': 0.05, 'trailing': 0.15, 'pos': 0.65, 'cf_base': 78},
    'M4恐慌': {'hold_days': 3, 'take_profit': 0.15, 'stop_loss': 0.05, 'trailing': 0.08, 'pos': 0.55, 'cf_base': 70},
    'M5金叉': {'hold_days': 5, 'take_profit': 0.15, 'stop_loss': 0.05, 'trailing': 0.10, 'pos': 0.45, 'cf_base': 74},
    'M6尾盘': {'hold_days': 1, 'take_profit': 0.08, 'stop_loss': 0.05, 'trailing': 0.05, 'pos': 0.35, 'cf_base': 68},
}

PHASE_PARAMS = {
    'ice':     {'label': '冰点期', 'max_pos': 0.00, 'action': '空仓等待'},
    'start':   {'label': '启动期', 'max_pos': 0.25, 'action': 'M1/M4轻仓'},
    'ferment': {'label': '发酵期', 'max_pos': 0.80, 'action': 'M1-M6全开'},
    'climax':  {'label': '高潮期', 'max_pos': 0.40, 'action': 'M5减少追高'},
    'retreat': {'label': '退潮期', 'max_pos': 0.05, 'action': '全部停止'},
}

# ============================================================
# 数据获取
# ============================================================
def fetch(code: str, days: int = 90) -> List:
    url = (f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php"
           f"/CN_MarketData.getKLineData?symbol={code}&scale=240&ma=no&datalen={days}")
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
            timeout=10
        ) as r:
            d = json.loads(r.read().decode("utf-8"))
            return d if isinstance(d, list) else []
    except:
        return []

def parse_kline(raw: List) -> List[Dict]:
    r = []
    for k in raw:
        try:
            r.append({
                'd': k['day'], 'o': float(k['open']), 'c': float(k['close']),
                'h': float(k['high']), 'l': float(k['low']), 'v': int(k['volume'])
            })
        except:
            pass
    return r

def MA(ks: List, n: int, i: int) -> float:
    if i < 0 or i >= len(ks): return ks[i]['c']
    s = max(0, i - n + 1)
    return sum(ks[j]['c'] for j in range(s, i + 1)) / max(1, i - s + 1)

def VOL(ks: List, n: int, i: int) -> float:
    if i < 0 or i >= len(ks): return max(1, ks[0]['v'])
    s = max(0, i - n + 1)
    return sum(ks[j]['v'] for j in range(s, i + 1)) / max(1, i - s + 1)

# ============================================================
# 市场阶段
# ============================================================
def get_market_phase(date: str, HS: List) -> Tuple[str, float, Dict]:
    """返回(阶段, 当日涨跌幅, 阶段参数)"""
    hs_d = [k for k in HS if k['d'] <= date]
    if len(hs_d) < 20: return 'neutral', 0, PHASE_PARAMS['ice']
    m5 = sum(k['c'] for k in hs_d[-5:]) / 5
    m10 = sum(k['c'] for k in hs_d[-10:]) / 10
    pct = (hs_d[-1]['c'] - hs_d[-1]['o']) / max(0.001, hs_d[-1]['o']) * 100
    rets = [(hs_d[j]['c'] - hs_d[j-1]['c']) / max(0.001, hs_d[j-1]['c'])
             for j in range(max(1, len(hs_d) - 20), len(hs_d))]
    vol = (sum((r - sum(rets) / max(1, len(rets))) ** 2 for r in rets) ** 0.5 /
            max(1, len(rets))) if rets else 0
    if m5 < m10 and pct < -0.5: phase = 'bear'
    elif m5 > m10 and pct > 0.5: phase = 'bull'
    elif vol > 0.015: phase = 'hv'
    else: phase = 'neutral'
    ph_map = {'bear': 'bear', 'bull': 'bull', 'hv': 'climax', 'neutral': 'neutral'}
    ph = ph_map.get(phase, 'neutral')
    if hs_d[-1]['c'] < hs_d[-1]['o'] and phase == 'neutral': ph = 'start'
    pp = PHASE_PARAMS.get(ph, PHASE_PARAMS['neutral'])
    return ph, pct, pp

# ============================================================
# 信号识别
# ============================================================
def scan_all(date: str, D: Dict, DI: Dict, HS: List) -> List[Dict]:
    """扫描所有信号"""
    phase, pct, pp = get_market_phase(date, HS)
    phase_max_pos = pp['max_pos']

    results = []
    for code, sd in D.items():
        ki = DI.get((code, date))
        if ki is None or ki < 5: continue
        ks = sd['ks']
        k = ks[ki]
        p = ks[ki - 1] if ki >= 1 else k

        vr = k['v'] / max(1, VOL(ks, 5, ki))
        body = (k['c'] - k['o']) / max(0.001, k['o']) * 100
        sl5 = (k['c'] - ks[ki - 4]['c']) / max(0.001, ks[ki - 4]['c']) * 100 if ki >= 4 else 0
        ma5 = MA(ks, 5, ki)
        ma10 = MA(ks, 10, ki)
        ma5b = MA(ks, 5, ki - 1) if ki >= 5 else ma5
        ma10b = MA(ks, 10, ki - 1) if ki >= 10 else ma10
        ma20 = MA(ks, 20, ki)

        lu = k['c'] >= p['c'] * 1.095
        was_lu = ki >= 1 and ks[ki - 1]['c'] >= ks[ki - 2]['c'] * 1.095
        extreme = pct <= -1.5
        fear = pct <= -0.8
        bull = pct >= 1.0

        # M1首板（冰点/启动期精华）
        if extreme and lu and not was_lu and 1.2 <= vr <= 5.0:
            results.append(_make_signal(code, sd, k, 'M1首板', phase_max_pos))
        # M2二板（弱转强）
        if bull and ki >= 2:
            was1 = ks[ki - 1]['c'] >= ks[ki - 2]['c'] * 1.095
            was2 = ki >= 3 and ks[ki - 2]['c'] >= ks[ki - 3]['c'] * 1.095
            op = (k['o'] - p['c']) / max(0.001, p['c']) * 100
            if was1 and not was2 and 1 <= op <= 7 and vr > 1.2:
                results.append(_make_signal(code, sd, k, 'M2二板', phase_max_pos))
        # M3整理（精华！让利润奔跑）
        if 2.5 <= body <= 10 and vr < 0.90 and sl5 > 0:
            results.append(_make_signal(code, sd, k, 'M3整理', phase_max_pos))
        # M4恐慌（逆向信号）
        if extreme and vr < 0.80:
            results.append(_make_signal(code, sd, k, 'M4恐慌', phase_max_pos))
        # M5金叉（趋势确认）
        if ki >= 5 and ma5b <= ma10b and ma5 > ma10 and vr > 0.9:
            if abs(k['c'] - ma20) / ma20 < 5:
                results.append(_make_signal(code, sd, k, 'M5金叉', phase_max_pos))
        # M6尾盘（短线）
        if vr > 1.4 and sl5 > 0 and body > 1.5 and k['c'] > k['o']:
            results.append(_make_signal(code, sd, k, 'M6尾盘', phase_max_pos))

    results.sort(key=lambda x: -x['confidence'])
    return results

def _make_signal(code: str, sd: Dict, k: Dict, sig_name: str, phase_max_pos: float) -> Dict:
    sp = SIGNAL_PARAMS[sig_name]
    effective_pos = min(sp['pos'], phase_max_pos) if phase_max_pos > 0 else 0
    return {
        'code': code, 'name': sd['n'],
        'price': k['c'],
        'signal': sig_name,
        'confidence': sp['cf_base'],
        'hold_days': sp['hold_days'],
        'take_profit_pct': f"+{int(sp['take_profit']*100)}%",
        'trailing_pct': f"-{int(sp['trailing']*100)}%",
        'stop_loss_pct': f"-{int(sp['stop_loss']*100)}%",
        'position_pct': f"{int(effective_pos*100)}%" if effective_pos > 0 else "0%",
        'effective_pos': effective_pos,
        'entry_price': k['c'],
    }

# ============================================================
# 主程序
# ============================================================
if __name__ == "__main__":
    import datetime
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    print("=" * 60)
    print(f"🌊 涟漪 v15.3 交易信号扫描")
    print(f"   日期: {today}")
    print("=" * 60)

    print("\n加载数据...")
    D = {}
    for code, name in CORE_35:
        ks = parse_kline(fetch(code, 90))
        if len(ks) >= 30: D[code] = {'n': name, 'ks': ks}
    HS = parse_kline(fetch("sh000001", 90))
    print(f"核心股: {len(D)}只 | 沪深300: {len(HS)}条")

    DI = {}
    for code, d in D.items():
        for j, k in enumerate(d['ks']):
            DI[(code, k['d'])] = j

    # 获取今日信号
    today_kline = [k for k in HS if k['d'] == today]
    if today_kline:
        scan_date = today
    else:
        scan_date = HS[-1]['d'] if HS else today
        print(f"今日无数据，最新有数据日期: {scan_date}")

    phase, pct, pp = get_market_phase(scan_date, HS)
    phase_info = PHASE_PARAMS.get(phase, PHASE_PARAMS['neutral'])

    print(f"\n{'='*60}")
    print(f"📊 市场状态 ({scan_date})")
    print(f"{'='*60}")
    print(f"  阶段: {phase_info['label']} ({phase})")
    print(f"  沪深300今日: {pct:+.2f}%")
    print(f"  仓位上限: {int(phase_info['max_pos']*100)}%")
    print(f"  操作建议: {phase_info['action']}")

    signals = scan_all(scan_date, D, DI, HS)
    available = [s for s in signals if s['effective_pos'] > 0]
    disabled = [s for s in signals if s['effective_pos'] == 0]

    print(f"\n{'='*60}")
    print(f"📡 v15.3信号 ({len(available)}个可执行 / {len(disabled)}个暂停)")
    print(f"{'='*60}")

    if available:
        print(f"\n【可执行信号】")
        for idx, s in enumerate(available[:10], 1):
            tag = "★精华" if s['signal'] == 'M3整理' else ""
            print(f"  {idx}. {s['name']:<10} [{s['signal']:<6}] ¥{s['price']:.2f} "
                  f"| 持{s['hold_days']}天 | 止盈{s['take_profit_pct']} | 回撤{s['trailing_pct']} | 仓位{s['position_pct']} "
                  f"| 置信{s['confidence']} {tag}")

    if disabled:
        print(f"\n【当前暂停信号】")
        for s in disabled[:5]:
            print(f"  ✗ {s['name']:<10} [{s['signal']:<6}] 仓位0% (阶段限制)")

    if not signals:
        print(f"\n⚠️ 今日无信号！市场无机会，空仓等待。")

    print(f"\n{'='*60}")
    print(f"💡 v15.3 操作建议")
    print(f"{'='*60}")
    if phase == 'ice':
        print(f"  冰点期，空仓等待。涟漪在观察。")
    elif phase == 'retreat':
        print(f"  退潮期，禁止开新仓。涟漪在等待机会。")
    elif available:
        best = available[0]
        print(f"  最佳信号: {best['name']} {best['signal']}")
        print(f"  入场价: ¥{best['price']:.2f}")
        print(f"  持有: {best['hold_days']}天")
        print(f"  止盈: {best['take_profit_pct']} | 止损: {best['stop_loss_pct']}")
        print(f"  移动止盈: {best['trailing_pct']}回撤触发")
        print(f"  仓位: {best['position_pct']}")
        print(f"  ⚠️ 以上仅为系统信号，不构成投资建议")
        print(f"  ⚠️ 真实下单须V授权")
