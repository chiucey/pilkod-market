#!/usr/bin/env python3
"""
Gold Smart Money Analysis v5.1 — 修复版
修复: ①资金类型分类 ②加权值计算 ③COT按时周期分类 ④数据更新日期
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import argparse, json

# ═══════════════════════════════════════════════════════════════════════
# DATA BLOCK — 所有数据 + 更新日期
# ═══════════════════════════════════════════════════════════════════════

# 【短期资金】日频
GOLD_PRICE = {
    'price': 4725.0,
    'prev': 4712.0,
    'ma5': 4711.7, 'ma20': 4650.0, 'ma60': 4580.0,
    'chg_d': 13.0, 'chg_d_pct': 0.28,
    'chg_5d': 27.0, 'chg_20d': 75.0, 'chg_60d': 145.0,
    'updated': '2026-04-25',
}

GLD_HOLDINGS = {
    'current_t': 1049.19, 'yest_t': 1047.33,
    'wk_prev_t': 1051.0, 'mo_prev_t': 1062.0,
    'ytd_start_t': 1098.0, 'high_t': 1070.0,
    'd_chg': 1.86, 'wk_chg': -1.81, 'mo_chg': -12.81, 'ytd_chg': -48.71,
    'pct_high': 1.94, 'pct_high_prev': 1.78,
    'updated': '2026-04-25',
}

CN_ETF = {
    'huaan_aum': 939.63, 'yest_aum': 942.0,
    'huaan_flow': -2.37, 'mkt_flow': -10.0,
    'flow_5d': [1.82, -0.45, -1.23, -2.37, -2.37],
    'outflow_days': 4, 'inflow_days': 0,
    'updated': '2026-04-25',
}

# 【短期资金】周频 — COT 非报告(散户) + 非商业(机构)
COT_NON_REPORT = {          # 散户 — 放在短期(周频)
    'net': 164006, 'prev_net': 150000,
    'long': 212893, 'short': 48887,
    'net_pct': 62.7, 'index': 88,
    'wk_chg': 14006,
    'report_date': '2026-04-21', 'week': 'W17',
}

COT_NON_COMMERCIAL = {      # 非商业(机构/投机) — 放在短期(周频)
    'net': 162500, 'prev_net': 156300, 'prev2_net': 163200,
    'long': 206000, 'short': 43500,
    'index': 60, 'index_prev': 57,
    'wk_chg': 6200, 'biwk_chg': -700,
    'report_date': '2026-04-21', 'week': 'W17',
}

ETF_WEEKLY = {              # 全球ETF周流 — 短期
    'net_flow_t': 5.0, 'prev_t': 8.2, 'prev2_t': 3.1,
    'wk_chg': -3.2, 'biwk_chg': 1.9,
    'updated': '2026-04-24',
}

# 【中期资金】月频 — 资管(CTA) + 商业(矿商) + ETF月流
CFT_C_MANAGED_MONEY = {     # 资管(CTA子集) — 中期(月频)
    'end_pct': 20.94, 'start_pct': 24.62,
    'mo_chg': -3.68,        # 本月变化
    'prev_mo_chg': 2.52,    # 上月变化
    'delta_momentum': -6.20, # 动量变化
    'updated': '2026-03',
}

CFT_C_COMMERCIAL = {        # 商业(矿商对冲) — 中期(月频)
    'net': -85000, 'prev_net': -78000, 'prev2_net': -82000,
    'pct_oi': -28.5, 'pct_oi_prev': -26.8,
    'mo_chg': -7000, 'bimo_chg': -3000,
    'updated': '2026-03',
}

ETF_MONTHLY = {             # ETF月流 — 中期
    'net_flow_t': 18.5, 'prev_t': 31.0, 'prev2_t': 22.0,
    'mo_chg': -12.5, 'bimo_chg': -3.5,
    'q1_total': 62.0,
    'note': '亚洲净流入\$14亿，北美净流出\$13亿',
    'updated': '2026-03',
}

# 【长期资金】季频 — 央行购金 + 供需缺口
CENTRAL_BANK = {            # 央行购金 — 长期(季频)
    'q4_2025': 312, 'q3_2025': 286, 'q2_2025': 295, 'q4_2024': 241,
    'qoq': 26, 'yoy': 71,
    'q1_2026_partial': 58,   # 仅1-2月
    'top_buyers': ['波兰+20t', '土耳其+18t', '印度+15t', '中国央行+12t', '乌兹别克+8t'],
    'top_sellers': ['哈萨克-3t', '土耳其换仓-5t'],
    'trend': '加速购金',
    'cb_index': 72,
    'updated': '2026-02',
}

SUPPLY_DEMAND = {           # WGC供需 — 长期(季频)
    'report_quarter': 'Q4 2025',
    'total_demand': 1599, 'total_supply': 1189,
    'gap': 410,
    'gap_q3': 358, 'gap_q4_prev': 289,
    'gap_qoq': 52, 'gap_yoy': 121,
    'jewelry': 876, 'investment': 329, 'cb_demand': 312, 'etf_demand': 240,
    'etf_qoq': -162.0, 'etf_yoy': -46.0,
    'mine_supply': 895, 'recycled': 312,
    'china_demand': 620, 'india_demand': 280, 'asia_share': 0.57,
    'updated': '2026-02-05',
}

# ═══════════════════════════════════════════════════════════════════════
# SCORING MODEL
# ═══════════════════════════════════════════════════════════════════════

# 权重定义
WEIGHTS = {'long': 0.40, 'medium': 0.35, 'short': 0.25}

def band(v: float, thresholds: list, scores: list) -> float:
    for t, s in zip(thresholds, scores):
        if v >= t: return s
    return scores[-1]

# ── 短期评分（25%）
def score_short() -> Dict:
    """
    权重分配:
      COT非商业(周)       20% — 机构净多头方向 + COT Index
      COT非报告(周)       15% — 散户净多头COT Index(反向)
      GLD持仓(日)         20% — 持仓距高点% + 周变化
      华安ETF(日)         25% — 连续流出天数 + 日流方向
      全球ETF周流         20% — 周净流入方向
    公式: short = NC×0.20 + NR×0.15 + GLD×0.20 + CN×0.25 + EW×0.20
    """
    cot_nc = COT_NON_COMMERCIAL
    cot_nr = COT_NON_REPORT
    gld   = GLD_HOLDINGS
    cn    = CN_ETF
    ew    = ETF_WEEKLY

    # NC: 非商业机构
    nc_base = band(cot_nc['index'], [85, 75, 60, 50, 40, 20], [35, 50, 70, 80, 65, 40])
    if cot_nc['wk_chg'] > 10000: nc_base = min(nc_base + 8, 100)
    elif cot_nc['wk_chg'] > 5000: nc_base = min(nc_base + 4, 100)
    elif cot_nc['wk_chg'] < -10000: nc_base = max(nc_base - 8, 0)

    # NR: 散户(反向)
    nr_base = band(cot_nr['index'], [85, 75, 65, 50, 35, 0], [25, 40, 55, 70, 60, 45])
    nr_chg = cot_nr['net'] - cot_nr['prev_net']
    if nr_chg > 10000: nr_base = max(nr_base - 10, 0)
    elif nr_chg < -10000: nr_base = min(nr_base + 8, 100)

    # GLD
    gld_base = band(gld['pct_high'], [5, 3, 1, -1, -3, -10], [70, 75, 80, 70, 55, 30])
    if gld['wk_chg'] > 0: gld_base = min(gld_base + 5, 100)
    elif gld['wk_chg'] < -5: gld_base = max(gld_base - 8, 0)

    # 华安ETF
    if cn['outflow_days'] >= 3 and cn['huaan_flow'] < -2: cn_score = 35
    elif cn['outflow_days'] >= 2 and cn['huaan_flow'] < -1: cn_score = 45
    elif cn['huaan_flow'] > 2: cn_score = 55
    else: cn_score = 55

    # ETF周流
    ew_base = band(ew['net_flow_t'], [10, 5, 2, -2, -5, -10], [80, 70, 60, 50, 40, 25])
    if ew['wk_chg'] > 0: ew_base = min(ew_base + 3, 100)
    elif ew['wk_chg'] < -8: ew_base = max(ew_base - 5, 0)

    total = nc_base*0.20 + nr_base*0.15 + gld_base*0.20 + cn_score*0.25 + ew_base*0.20
    total = max(0, min(100, total))

    return {
        'score': round(total, 1),
        'nc_score': round(nc_base, 1), 'nr_score': round(nr_base, 1),
        'gld_score': round(gld_base, 1), 'cn_score': round(cn_score, 1),
        'ew_score': round(ew_base, 1),
        'signal': sig(total),
    }

# ── 中期评分（35%）
def score_medium() -> Dict:
    """
    权重分配:
      商业净空头(月)      35% — 净空绝对水平 + 月变化
      资管净多头%(月)     35% — 净多头% + 月变化
      全球ETF月流        30% — 月流入方向 + 绝对水平
    公式: medium = COMM×0.35 + MM×0.35 + ETF_M×0.30
    """
    comm = CFT_C_COMMERCIAL
    mm   = CFT_C_MANAGED_MONEY
    etf  = ETF_MONTHLY

    comm_abs = abs(comm['net'])
    comm_base = band(comm_abs, [100000, 90000, 80000, 70000, 60000, 0], [20, 35, 50, 65, 75, 85])
    if comm['mo_chg'] > 0: comm_base = min(comm_base + 5, 100)
    elif comm['mo_chg'] < -5000: comm_base = max(comm_base - 8, 0)

    mm_base = band(mm['end_pct'], [30, 25, 22, 18, 15, 10], [60, 75, 85, 70, 55, 40])
    if mm['mo_chg'] > 1: mm_base = min(mm_base + 5, 100)
    elif mm['mo_chg'] < -2: mm_base = max(mm_base - 8, 0)

    etf_base = band(etf['net_flow_t'], [25, 15, 10, 5, 0, -10], [90, 75, 65, 55, 45, 25])
    if etf['mo_chg'] > 0: etf_base = min(etf_base + 5, 100)
    elif etf['mo_chg'] < -15: etf_base = max(etf_base - 5, 0)

    total = comm_base*0.35 + mm_base*0.35 + etf_base*0.30
    total = max(0, min(100, total))

    return {
        'score': round(total, 1),
        'comm_score': round(comm_base, 1),
        'mm_score': round(mm_base, 1),
        'etf_score': round(etf_base, 1),
        'signal': sig(total),
    }

# ── 长期评分（40%）
def score_long() -> Dict:
    """
    权重分配:
      央行购金(季)       50% — Q4购金量 + YoY变化
      供需缺口(季)       50% — 缺口绝对量 + QoQ + YoY
    公式: long = CB×0.50 + SD×0.50
    """
    cb = CENTRAL_BANK
    sd = SUPPLY_DEMAND

    cb_base = band(cb['q4_2025'], [350, 300, 250, 200, 150, 0], [95, 85, 75, 60, 45, 30])
    if cb['yoy'] > 100: cb_base = min(cb_base + 5, 100)
    elif cb['yoy'] > 50: cb_base = min(cb_base + 3, 100)

    sd_base = band(sd['gap'], [400, 300, 200, 100, 0, -100], [95, 80, 65, 50, 35, 15])
    if sd['gap_qoq'] > 50: sd_base = min(sd_base + 5, 100)
    elif sd['gap_qoq'] > 0: sd_base = min(sd_base + 2, 100)
    elif sd['gap_qoq'] < -50: sd_base = max(sd_base - 5, 0)

    total = cb_base * 0.50 + sd_base * 0.50
    total = max(0, min(100, total))

    return {
        'score': round(total, 1),
        'cb_score': round(cb_base, 1),
        'sd_score': round(sd_base, 1),
        'signal': sig(total),
    }

def sig(score: float) -> tuple:
    if score >= 75: return ('强烈看多', '🟢')
    if score >= 60: return ('偏多', '🟢')
    if score >= 50: return ('中性', '⚪')
    if score >= 40: return ('偏空', '🔴')
    return ('强烈看空', '🔴')

def bar(score: float, w: int = 16) -> str:
    return '█' * int(round(score/100*w)) + '░' * (w - int(round(score/100*w)))

# ═══════════════════════════════════════════════════════════════════════
# CONTRADICTION DETECTION
# ═══════════════════════════════════════════════════════════════════════

def detect_issues() -> List[Dict]:
    issues = []
    cot_nr = COT_NON_REPORT
    cot_nc = COT_NON_COMMERCIAL
    gld   = GLD_HOLDINGS
    cn    = CN_ETF
    comm  = CFT_C_COMMERCIAL
    mm    = CFT_C_MANAGED_MONEY
    cb    = CENTRAL_BANK

    if cot_nr['index'] > 80 and cot_nc['index'] > 60:
        issues.append({
            'type': '🔴 短期见顶预警',
            'desc': f'散户COT Index={cot_nr["index"]}(追多极端) + 机构Index={cot_nc["index"]}(中性偏多) → 交易拥挤',
            'action': '短期减仓/止盈，回调后再加仓'
        })
    if gld['pct_high'] < 2 and cn['outflow_days'] >= 3:
        issues.append({
            'type': '🔴 阶段性顶部',
            'desc': f'GLD距高点{gld["pct_high"]:.1f}%(<2%) + 华安连续{cn["outflow_days"]}天流出 → 接近顶部',
            'action': '多头保护利润，跌破\$4,650减仓'
        })
    if comm['mo_chg'] < -5000 and cot_nc['wk_chg'] > 0:
        issues.append({
            'type': '⚠️ 机构分歧',
            'desc': f'商业净空月增{comm["mo_chg"]:+,}(矿商对冲↑) + 非商业周增{cot_nc["wk_chg"]:+,}(机构看多)',
            'action': '中期震荡，等方向确认'
        })
    if mm['mo_chg'] < -3 and gld['d_chg'] > 0:
        issues.append({
            'type': '🔴 机构撤退/散户接盘',
            'desc': f'MM净多头%月减{mm["mo_chg"]:.1f}%(机构减仓) + 金价日涨{gld["d_chg"]:+.0f} → 散户接盘',
            'action': '⚠️ 见顶风险，警惕快速回调'
        })
    if cb['yoy'] > 50 and cn['outflow_days'] >= 3:
        issues.append({
            'type': '🟡 长短矛盾',
            'desc': f'央行Q4购金YoY+{cb["yoy"]}吨(加速) + 华安连续{cn["outflow_days"]}天流出 → 长期强/短期弱',
            'action': '长期不改，回调是核心加仓机会'
        })
    if comm['net'] < -90000 and gld['chg_20d'] > 50:
        issues.append({
            'type': '⚠️ 逼仓风险监控',
            'desc': f'商业净空头{comm["net"]:,}(极端高位) + 金价20日+{gld["chg_20d"]:.0f}美元',
            'action': '关注商业空头被迫平仓信号'
        })
    return issues

# ═══════════════════════════════════════════════════════════════════════
# REPORT GENERATION
# ═══════════════════════════════════════════════════════════════════════

def hr(char='═', width=74):
    print(f"╔{'═'*width}╗")

def print_full():
    sl = score_long()
    sm = score_medium()
    ss = score_short()
    short_s = score_short()
    combined = sl['score']*0.40 + sm['score']*0.35 + ss['score']*0.25

    print()
    hr(); print(f"║  黄金聪明钱与长期资金流向分析报告  v5.1  |  {datetime.now().strftime('%Y-%m-%d')}"); hr()
    print(f"║"); hr('─')

    # ── 综合评分
    print(f"║  综合评分: {combined:.0f}/100  [{bar(combined)}]  信号: {'🟢买入' if combined>=65 else '⚪持有' if combined>=45 else '🔴减仓'}")
    print(f"║")
    print(f"║  加权公式: 综合分 = 长期分×0.40 + 中期分×0.35 + 短期分×0.25")
    print(f"║           综合分 = {sl['score']:.1f}×0.40 + {sm['score']:.1f}×0.35 + {ss['score']:.1f}×0.25 = {combined:.1f}")
    print(f"║")
    print(f"║  三周期评分:")
    print(f"║    长期(3M-1Y)  {sl['score']:.0f}分  {sl['signal'][1]}{sl['signal'][0]:<6}  [███████░░░] 权重40%")
    print(f"║    中期(1-3M)   {sm['score']:.0f}分  {sm['signal'][1]}{sm['signal'][0]:<6}  [█████░░░░░] 权重35%")
    print(f"║    短期(1-4W)   {ss['score']:.0f}分  {ss['signal'][1]}{ss['signal'][0]:<6}  [█████░░░░░] 权重25%")
    print(f"║"); hr('─')

    # ════════════════════════════════════════════════════════════════════════
    print(f"║  【短期资金】 权重25%  |  周频/日频  更新日:{CN_ETF['updated']}"); hr('─')
    # ① 黄金价格
    ch = GOLD_PRICE['chg_d']
    print(f"║  ① 黄金现货价格          更新:{GOLD_PRICE['updated']}")
    print(f"║     现价 ${GOLD_PRICE['price']:,.0f}/盎司  {'🟢' if ch>0 else '🔴'}{ch:+.0f}({GOLD_PRICE['chg_d_pct']:+.2f}%)  5日{'🟢' if GOLD_PRICE['chg_5d']>0 else '🔴'}{GOLD_PRICE['chg_5d']:+.0f}美元")
    print(f"║     MA5=${GOLD_PRICE['ma5']:,.0f}  MA20=${GOLD_PRICE['ma20']:,.0f}  MA60=${GOLD_PRICE['ma60']:,.0f}")
    print(f"║")
    # ② GLD
    print(f"║  ② SPDR GLD 持仓(日频)   更新:{GLD_HOLDINGS['updated']}")
    print(f"║     {GLD_HOLDINGS['current_t']:.1f}吨  {'🟢' if GLD_HOLDINGS['d_chg']>0 else '🔴'}{GLD_HOLDINGS['d_chg']:+.2f}/日  {'🟢' if GLD_HOLDINGS['wk_chg']>0 else '🔴'}{GLD_HOLDINGS['wk_chg']:+.1f}/周  {'🟢' if GLD_HOLDINGS['mo_chg']>0 else '🔴'}{GLD_HOLDINGS['mo_chg']:+.1f}/月")
    print(f"║     距高点: {GLD_HOLDINGS['pct_high']:.2f}%  YTD:{GLD_HOLDINGS['ytd_chg']:+.1f}吨")
    print(f"║")
    # ③ 华安ETF
    print(f"║  ③ 华安黄金ETF情绪(日)   更新:{CN_ETF['updated']}")
    mkt_flow = CN_ETF['mkt_flow']
    print(f"║     规模{CN_ETF['huaan_aum']:.1f}亿  {'🔴' if CN_ETF['huaan_flow']<0 else '🟢'}{CN_ETF['huaan_flow']:+.2f}亿/日  全市场{mkt_flow:+.1f}亿")
    print(f"║     5日流:{CN_ETF['flow_5d']}  连续流出{CN_ETF['outflow_days']}天  连续流入{CN_ETF['inflow_days']}天")
    print(f"║")
    # ④ COT散户(周)
    print(f"║  ④ COT 非报告(散户)      报告日:{COT_NON_REPORT['report_date']} {COT_NON_REPORT['week']}")
    print(f"║     净多头{COT_NON_REPORT['net']:,}({COT_NON_REPORT['wk_chg']:+,}/周)  Index={COT_NON_REPORT['index']}")
    print(f"║     → {'追多极端⚠️' if COT_NON_REPORT['index']>80 else '追多' if COT_NON_REPORT['index']>60 else '中性' if COT_NON_REPORT['index']>40 else '看空'}")
    print(f"║")
    # ⑤ COT非商业机构(周)
    print(f"║  ⑤ COT 非商业(机构/投机) 报告日:{COT_NON_COMMERCIAL['report_date']} {COT_NON_COMMERCIAL['week']}")
    print(f"║     净多头{COT_NON_COMMERCIAL['net']:,}({COT_NON_COMMERCIAL['wk_chg']:+,}/周)  Index={COT_NON_COMMERCIAL['index']}  两周{COT_NON_COMMERCIAL['biwk_chg']:+,}")
    print(f"║     → {'看多' if COT_NON_COMMERCIAL['index']>60 else '中性' if COT_NON_COMMERCIAL['index']>40 else '看空'}")
    print(f"║")
    # ⑥ ETF周流
    print(f"║  ⑥ 全球Gold ETF周净流入  更新:{ETF_WEEKLY['updated']}")
    print(f"║     +{ETF_WEEKLY['net_flow_t']:.1f}吨({'🟢' if ETF_WEEKLY['net_flow_t']>0 else '🔴'})  上周+{ETF_WEEKLY['prev_t']:.1f}t({ETF_WEEKLY['wk_chg']:+.1f})  两周{ETF_WEEKLY['biwk_chg']:+.1f}t")
    print(f"║"); hr('─')

    # ════════════════════════════════════════════════════════════════════════
    print(f"║  【中期资金】 权重35%  |  月频  更新月:{CFT_C_MANAGED_MONEY['updated']}"); hr('─')
    # ⑦ 商业(矿商)
    print(f"║  ⑦ CFTC 商业(矿商对冲)   月份:{CFT_C_COMMERCIAL['updated']}")
    print(f"║     净空头{CFT_C_COMMERCIAL['net']:,}  {CFT_C_COMMERCIAL['mo_chg']:+,}/月  占OI{CFT_C_COMMERCIAL['pct_oi']:.1f}%")
    print(f"║     → {'净空增加→中期供应压力⚠️' if CFT_C_COMMERCIAL['mo_chg']<-2000 else '净空减少→中期改善✅'}")
    print(f"║")
    # ⑧ 资管(CTA)
    print(f"║  ⑧ CFTC 资管(CTA动量)   月份:{CFT_C_MANAGED_MONEY['updated']}")
    print(f"║     净多头{CFT_C_MANAGED_MONEY['end_pct']:.2f}%  {CFT_C_MANAGED_MONEY['mo_chg']:+.2f}/月  上月{CFT_C_MANAGED_MONEY['prev_mo_chg']:+.2f}  动量变化{CFT_C_MANAGED_MONEY['delta_momentum']:+.2f}")
    print(f"║     → {'机构减仓/动量减弱⚠️' if CFT_C_MANAGED_MONEY['mo_chg']<-1 else '机构加仓/动量增强✅'}")
    print(f"║")
    # ⑨ ETF月流
    print(f"║  ⑨ 全球Gold ETF月净流入  月份:{ETF_MONTHLY['updated']}")
    print(f"║     +{ETF_MONTHLY['net_flow_t']:.1f}吨({'🟢' if ETF_MONTHLY['net_flow_t']>0 else '🔴'})  上月+{ETF_MONTHLY['prev_t']:.1f}t({ETF_MONTHLY['mo_chg']:+.1f})  Q1累计+{ETF_MONTHLY['q1_total']:.0f}t")
    print(f"║     注:{ETF_MONTHLY['note']}")
    print(f"║"); hr('─')

    # ════════════════════════════════════════════════════════════════════════
    print(f"║  【长期资金】 权重40%  |  季频  更新:{CENTRAL_BANK['updated']}"); hr('─')
    # ⑩ 央行购金
    print(f"║  ⑩ 央行购金             季度:{CENTRAL_BANK['updated']}")
    print(f"║     Q4={CENTRAL_BANK['q4_2025']}吨({'🟢' if CENTRAL_BANK['q4_2025']>250 else '🟡'})  Q3={CENTRAL_BANK['q3_2025']}t(QoQ{CENTRAL_BANK['qoq']:+})  YoY{CENTRAL_BANK['yoy']:+}t")
    print(f"║     Q1暂计{CENTRAL_BANK['q1_2026_partial']}吨  买家:{', '.join(CENTRAL_BANK['top_buyers'][:3])}")
    print(f"║     → {CENTRAL_BANK['trend']}(YoY+{CENTRAL_BANK['yoy']}吨)")
    print(f"║")
    # ⑪ 供需缺口
    print(f"║  ⑪ WGC 供需缺口         季度:{SUPPLY_DEMAND['updated']}")
    print(f"║     {SUPPLY_DEMAND['gap']}t({'🟢' if SUPPLY_DEMAND['gap']>300 else '🟡'})  Q3={SUPPLY_DEMAND['gap_q3']}t(QoQ{SUPPLY_DEMAND['gap_qoq']:+})  YoY{SUPPLY_DEMAND['gap_yoy']:+}t")
    print(f"║     总需求{SUPPLY_DEMAND['total_demand']}t  总供给{SUPPLY_DEMAND['total_supply']}t")
    print(f"║     珠宝{SUPPLY_DEMAND['jewelry']}t  投资{SUPPLY_DEMAND['investment']}t  央行{SUPPLY_DEMAND['cb_demand']}t  ETF{SUPPLY_DEMAND['etf_demand']:.0f}t")
    print(f"║     中国{SUPPLY_DEMAND['china_demand']}t  印度{SUPPLY_DEMAND['india_demand']}t  亚洲需求{int(SUPPLY_DEMAND['asia_share']*100)}%")
    print(f"║"); hr('─')

    # ── 评分计算明细
    print(f"║  【评分计算明细】")
    print(f"║")
    print(f"║  ★ 短期评分({ss['score']:.1f}分×0.25权重={ss['score']*0.25:.2f}):")
    print(f"║     COT非商业(周)×0.20 = {ss['nc_score']:.1f}×0.20 = {ss['nc_score']*0.20:.2f}")
    print(f"║     COT非报告(周)×0.15 = {ss['nr_score']:.1f}×0.15 = {ss['nr_score']*0.15:.2f}")
    print(f"║     GLD持仓(日)×0.20    = {ss['gld_score']:.1f}×0.20 = {ss['gld_score']*0.20:.2f}")
    print(f"║     华安ETF(日)×0.25    = {ss['cn_score']:.1f}×0.25 = {ss['cn_score']*0.25:.2f}")
    print(f"║     ETF周流×0.20        = {ss['ew_score']:.1f}×0.20 = {ss['ew_score']*0.20:.2f}")
    print(f"║     合计: {ss['nc_score']*0.20+ss['nr_score']*0.15+ss['gld_score']*0.20+ss['cn_score']*0.25+ss['ew_score']*0.20:.2f}")
    print(f"║")
    print(f"║  ★ 中期评分({sm['score']:.1f}分×0.35权重={sm['score']*0.35:.2f}):")
    print(f"║     商业净空头(月)×0.35 = {sm['comm_score']:.1f}×0.35 = {sm['comm_score']*0.35:.2f}")
    print(f"║     资管净多头%(月)×0.35= {sm['mm_score']:.1f}×0.35 = {sm['mm_score']*0.35:.2f}")
    print(f"║     ETF月流×0.30        = {sm['etf_score']:.1f}×0.30 = {sm['etf_score']*0.30:.2f}")
    print(f"║     合计: {sm['comm_score']*0.35+sm['mm_score']*0.35+sm['etf_score']*0.30:.2f}")
    print(f"║")
    print(f"║  ★ 长期评分({sl['score']:.1f}分×0.40权重={sl['score']*0.40:.2f}):")
    print(f"║     央行购金(季)×0.50   = {sl['cb_score']:.1f}×0.50 = {sl['cb_score']*0.50:.2f}")
    print(f"║     供需缺口(季)×0.50   = {sl['sd_score']:.1f}×0.50 = {sl['sd_score']*0.50:.2f}")
    print(f"║     合计: {sl['cb_score']*0.50+sl['sd_score']*0.50:.2f}")
    print(f"║")
    print(f"║  综合分 = {sl['score']:.1f}×0.40 + {sm['score']:.1f}×0.35 + {ss['score']:.1f}×0.25 = {combined:.1f}")
    print(f"║"); hr('─')

    # ── 矛盾
    issues = detect_issues()
    print(f"║  【矛盾识别】")
    if not issues:
        print(f"║    本周期无明显矛盾，多周期方向一致 ✅")
    else:
        for iss in issues[:5]:
            print(f"║  {iss['type']}  {iss['desc'][:45]}")
            print(f"║    → {iss['action']}")
    print(f"║"); hr('─')

    # ── 综合研判
    sd_map = {'强烈看多':'偏多','偏多':'偏多','中性':'中性','偏空':'偏空','强烈看空':'偏空'}
    print(f"║  【综合研判】")
    print(f"║    短期({sd_map[ss['signal'][0]]}) × 中期({sd_map[sm['signal'][0]]}) × 长期({sd_map[sl['signal'][0]]}) → 综合{combined:.0f}分")
    print(f"║    信号: {'🟢买入' if combined>=65 else '⚪持有' if combined>=45 else '🔴减仓'}")
    if issues:
        print(f"║    ⚠️ 存在矛盾，建议谨慎，关注关键价位突破")
    else:
        print(f"║    多周期共振，趋势方向明确")
    print(f"║    多头回调加仓参考位: MA60 ${GOLD_PRICE['ma60']:,.0f} / MA20 ${GOLD_PRICE['ma20']:,.0f}")
    print(f"║"); hr('─')

    print(f"║  数据更新日期汇总:")
    print(f"║    日频: 金价({GOLD_PRICE['updated']}) GLD({GLD_HOLDINGS['updated']}) 华安ETF({CN_ETF['updated']})")
    print(f"║    周频: COT({COT_NON_REPORT['report_date']}) ETF周流({ETF_WEEKLY['updated']})")
    print(f"║    月频: 商业({CFT_C_COMMERCIAL['updated']}) 资管({CFT_C_MANAGED_MONEY['updated']}) ETF月流({ETF_MONTHLY['updated']})")
    print(f"║    季频: 央行({CENTRAL_BANK['updated']}) 供需({SUPPLY_DEMAND['updated']})")
    print(f"║")
    print(f"║  ⚠️ 仅供参考，非投资建议")
    hr(); print()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--format', default='full', choices=['full', 'brief', 'json'])
    ap.add_argument('--output', default=None)
    args = ap.parse_args()

    sl = score_long()
    sm = score_medium()
    ss = score_short()
    combined = sl['score']*0.40 + sm['score']*0.35 + ss['score']*0.25
    issues = detect_issues()

    if args.format == 'json':
        data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'combined_score': round(combined, 1),
            'score_formula': f"{sl['score']:.1f}×0.40 + {sm['score']:.1f}×0.35 + {ss['score']:.1f}×0.25 = {combined:.1f}",
            'weights': WEIGHTS,
            'scores': {
                'long': {**sl, 'weight': 0.40, 'weighted': round(sl['score']*0.40, 2),
                          'components': {'central_bank': round(sl['cb_score'],1), 'supply_demand': round(sl['sd_score'],1)}},
                'medium': {**sm, 'weight': 0.35, 'weighted': round(sm['score']*0.35, 2),
                           'components': {'commercial': round(sm['comm_score'],1), 'managed_money': round(sm['mm_score'],1), 'etf_monthly': round(sm['etf_score'],1)}},
                'short': {**ss, 'weight': 0.25, 'weighted': round(ss['score']*0.25, 2),
                           'components': {'cot_noncommercial': round(ss['nc_score'],1), 'cot_nonreport': round(ss['nr_score'],1),
                                          'gld': round(ss['gld_score'],1), 'huaan_etf': round(ss['cn_score'],1), 'etf_weekly': round(ss['ew_score'],1)}},
            },
            'data': {
                'gold_price': GOLD_PRICE,
                'gld': GLD_HOLDINGS,
                'cn_etf': CN_ETF,
                'cot_non_report': COT_NON_REPORT,
                'cot_non_commercial': COT_NON_COMMERCIAL,
                'etf_weekly': ETF_WEEKLY,
                'cftc_commercial': CFT_C_COMMERCIAL,
                'cftc_managed_money': CFT_C_MANAGED_MONEY,
                'etf_monthly': ETF_MONTHLY,
                'central_bank': CENTRAL_BANK,
                'supply_demand': SUPPLY_DEMAND,
            },
            'contradictions': issues,
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif args.format == 'brief':
        print(f"[{datetime.now().strftime('%Y-%m-%d')}] 黄金 ${GOLD_PRICE['price']:,.0f}  {GOLD_PRICE['chg_d_pct']:+.2f}%  GLD:{GLD_HOLDINGS['current_t']:.1f}t  华安ETF:{CN_ETF['huaan_flow']:+.2f}亿  综合分:{combined:.0f}分 {'🟢' if combined>=65 else '⚪' if combined>=45 else '🔴'}")
    else:
        print_full()
        if args.output:
            import io, sys, os
            old = sys.stdout
            sys.stdout = io.StringIO()
            print_full()
            sys.stdout.seek(0)
            with open(args.output, 'w') as f:
                f.write(sys.stdout.read())
            sys.stdout = old

if __name__ == '__main__':
    main()