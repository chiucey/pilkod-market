#!/usr/bin/env python3
"""
国际投行焦煤期货一体化分析工具
框架: Morgan Stanley + UBS 三大投行方法论
版本: v3.0 (投行一体化版)
"""

import json, urllib.request, math
from datetime import datetime, timedelta

TOKEN = '647ae54872bf0e3d064b4f61e8437c15c58a337c38a98e2b301a91aa'
TODAY = datetime.now().strftime('%Y%m%d')
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
REPORT_DATE = datetime.now().strftime('%Y-%m-%d')
USDCNY = 7.24

def call(api, params):
    body = json.dumps({'api_name': api, 'token': TOKEN, 'params': params, 'fields': ''}).encode()
    req = urllib.request.Request('http://api.tushare.pro', data=body, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read())
        if d.get('code') != 0:
            return {'error': d.get('msg', ''), 'data': {}}
        return {'data': d.get('data', {}) or {}, 'error': None}
    except Exception as e:
        return {'error': str(e), 'data': {}}

def sf(v):
    try:
        return float(v)
    except:
        return None

def get_contract():
    res = call('fut_basic', {'exchange': 'DCE', 'fut_code': 'JM'})
    if res.get('error') or not res['data'].get('items'):
        return 'JM2609.DCE'
    flds = res['data']['fields']
    items = res['data']['items']
    syms = [item[flds.index('symbol')] for item in items if '26' in str(item[flds.index('symbol')])]
    for c in ['JM2609', 'JM2608', 'JM2607', 'JM2606']:
        if c in syms:
            return c + '.DCE'
    return 'JM2609.DCE'

def get_daily(contract, start, days=20):
    res = call('fut_daily', {'ts_code': contract, 'start_date': start, 'end_date': YESTERDAY})
    if res.get('error'):
        return []
    flds = res['data'].get('fields', [])
    items = res['data'].get('items', [])
    return [{flds[i]: sf(item[i]) for i in range(len(flds))} for item in items[-days:]]

def get_holding(td, sym):
    res = call('fut_holding', {'trade_date': td, 'symbol': sym})
    if res.get('error'):
        return []
    flds = res['data'].get('fields', [])
    items = res['data'].get('items', [])
    if not items:
        return []
    idx = {flds[i]: i for i in range(len(flds))}
    return [{
        'broker': items[j][idx.get('broker', 0)],
        'long_hld': sf(items[j][idx.get('long_hld', 0)]),
        'long_chg': sf(items[j][idx.get('long_chg', 0)]),
        'short_hld': sf(items[j][idx.get('short_hld', 0)]),
        'short_chg': sf(items[j][idx.get('short_chg', 0)]),
    } for j in range(len(items))]

def sep(t=''):
    print('\n' + ('=' * 68))
    if t:
        print('  ' + t)
        print('=' * 68)

# ================================================================
# 子模块1: 钢铁供需校验
# ================================================================
def sub1():
    sep('子模块1: 中国钢铁供需高频量化校验 (Morgan Stanley周度框架)')
    print()
    print('[核心公式]')
    print('  表观消费 = 产量 + 进口 - 出口 + (期初库存 - 期末库存)')
    print('  库存消费比 = (贸易商库存 + 钢厂库存) / 周度表观消费')
    print('  地产边际影响 = 长材WoW% x (长材消费 / 钢材总消费)')
    print()

    # Morgan Stanley 2026-04-02 周报数据
    d = {
        'inv_traders': 13615, 'inv_mills': 4890,
        'cons_long': 3190, 'cons_flat': 5800,
        'out_long': 2919, 'out_flat': 5596,
        'util_247': 86.6, 'util_eaf': 58.9,
        'cons_long_wow': 0.5, 'cons_flat_wow': 1.6,
        'out_long_wow': 3.7,
        'cons_long_yoy': -5.9, 'cons_flat_yoy': -0.2,
        'inv_traders_yoy': 12.0, 'inv_mills_yoy': 3.0,
    }
    inv_total = d['inv_traders'] + d['inv_mills']
    cons_total = d['cons_long'] + d['cons_flat']
    out_total = d['out_long'] + d['out_flat']
    balance = out_total - cons_total
    inv_ratio = inv_total / cons_total
    prop_long = d['cons_long'] / cons_total * 100
    margin = d['cons_long_wow'] * prop_long / 100

    print('[供需三角校验]')
    print('  %-26s %8s  %8s' % ('指标', '当周(kt)', '周环比'))
    print('  ' + '-' * 46)
    rows = [
        ('贸易商库存', d['inv_traders'], -1.9),
        ('钢厂库存', d['inv_mills'], -4.2),
        ('总库存', inv_total, None),
        ('长材表观消费', d['cons_long'], d['cons_long_wow']),
        ('扁平材表观消费', d['cons_flat'], d['cons_flat_wow']),
        ('钢材总消费', cons_total, None),
        ('长材产量', d['out_long'], d['out_long_wow']),
        ('钢材总产量', out_total, None),
    ]
    for nm, v, w in rows:
        ws = '%+.1f%%' % w if w is not None else ''
        print('  %-26s %8.0f  %8s' % (nm, v, ws))

    print()
    print('[核心指标]')
    print('  供需差: %+.0f kt (%s)' % (balance, '供给过剩' if balance > 0 else '供给短缺'))
    print('  库存消费比: %.1f 周' % inv_ratio)
    sig = ('偏紧' if inv_ratio < 3 else '正常' if inv_ratio < 4.5 else
            '偏过剩' if inv_ratio < 6 else '严重过剩')
    print('  松紧度: %s' % sig)

    print()
    print('[YoY同比]')
    print('  长材消费 YoY: %+.1f%% (%s)' % (d['cons_long_yoy'], '需求萎缩' if d['cons_long_yoy'] < 0 else '需求扩张'))
    print('  扁平材 YoY: %+.1f%% (%s)' % (d['cons_flat_yoy'], '需求萎缩' if d['cons_flat_yoy'] < 0 else '需求扩张'))
    print('  地产长材占比: %.1f%%' % prop_long)
    print('  地产边际影响系数: %.4f%%' % margin)

    print()
    print('[Morgan Stanley信号规则]')
    c1 = d['cons_long_wow'] >= 0.5 and inv_ratio < 4.5
    c2 = d['cons_long_wow'] < 0 and inv_ratio > 6
    if c1:
        sig2 = '高炉开工率预测环比上行0.5~1pct (需求向好+库存正常)'
    elif c2:
        sig2 = '高炉开工率预测环比下行0.3~0.8pct (需求萎缩+库存过剩)'
    else:
        sig2 = '高炉开工率预计维持当前水平'
    print('  信号: %s' % sig2)

    return {
        'inv_ratio': inv_ratio, 'util_247': d['util_247'],
        'cons_long_yoy': d['cons_long_yoy'], 'margin': margin,
        'prop_long': prop_long, 'balance_kt': balance,
    }

# ================================================================
# 子模块2: 钢铁-焦煤需求传导
# ================================================================
def sub2(s1):
    sep('子模块2: 钢铁-焦煤需求传导量化测算 (UBS中国基础材料框架)')
    print()
    print('[核心公式]')
    print('  焦煤需求(高炉) = 铁水产量 x 0.56 t焦煤/t铁水')
    print('  焦煤总需求 = 高炉需求 + 焦化厂(18%%) + 其他(4%%)')
    print('  供需缺口 = 总需求 - 总供给')
    print()

    COKE = 0.56
    BF_PROD = 18000 * s1['util_247'] / 100  # kt铁水/周
    coke_bf = BF_PROD * COKE
    coke_plant = coke_bf * 0.18
    coke_other = coke_bf * 0.04
    total_demand = coke_bf + coke_plant + coke_other

    dom_prod = 4200
    mongolia = 850; russia = 180; other_imp = 50
    total_supply = dom_prod + mongolia + russia + other_imp
    gap = total_demand - total_supply
    gap_rate = gap / total_demand * 100

    port_inv = 12800; mill_inv = 4900; coke_inv = 3200
    total_inv = port_inv + mill_inv + coke_inv
    inv_ratio_wk = total_inv / total_demand

    print('[焦煤需求测算]')
    print('  高炉铁水周产量(估算): %.0f kt' % BF_PROD)
    print('  高炉耗焦煤: %.0f kt/周 | 焦化厂: %.0f kt/周 | 其他: %.0f kt/周' % (
        coke_bf, coke_plant, coke_other))
    print('  焦煤总需求: %.0f kt/周' % total_demand)

    print()
    print('[焦煤供给测算]')
    print('  国内产量: %.0f kt/周' % dom_prod)
    print('  蒙古进口: %.0f kt (~%.0fMt/年)' % (mongolia, mongolia * 52 / 1000))
    print('  俄罗斯进口: %.0f kt' % russia)
    print('  焦煤总供给: %.0f kt/周' % total_supply)

    print()
    print('[供需缺口]')
    print('  缺口: %+.0f kt/周 (%+.1f%%)' % (gap, gap_rate))
    print('  评估: %s' % ('供给缺口(短缺)' if gap > 0 else '供给盈余(过剩)'))

    print()
    print('[库存周期]')
    print('  港口:%.0f + 钢厂:%.0f + 焦化:%.0f = %.0f kt' % (
        port_inv, mill_inv, coke_inv, total_inv))
    print('  库存消费比: %.1f 周' % inv_ratio_wk)
    isig = '偏低' if inv_ratio_wk < 5 else '正常' if inv_ratio_wk < 7 else '偏高'
    print('  评估: %s' % isig)

    elas = 1.0
    prop_elas = s1['margin'] / (abs(s1['cons_long_yoy']) / 100 + 0.001) * elas
    cyc = ('主动去库' if gap > 0 and inv_ratio_wk < 5 else
            '被动建库' if gap < 0 and inv_ratio_wk > 7 else '均衡')
    print()
    print('[弹性与周期]')
    print('  钢铁-焦煤弹性系数: %.2f' % elas)
    print('  地产-焦煤边际影响: %.3f' % prop_elas)
    print('  补库周期: %s' % cyc)

    return {
        'demand_kt': total_demand, 'supply_kt': total_supply,
        'gap_kt': gap, 'gap_rate': gap_rate,
        'inv_weeks': inv_ratio_wk, 'elasticity': elas,
        'prop_elasticity': prop_elas, 'cycle': cyc,
    }

# ================================================================
# 子模块3: 全球供需平衡
# ================================================================
def sub3(s2):
    sep('子模块3: 全球冶金煤供需平衡量化分析 (UBS全球煤炭专家会框架)')
    print()
    print('[核心公式]')
    print('  全球供需缺口 = 总需求 - 总供给')
    print('  套利价差 = 中国CFR - 出口FOB - 海运费')
    print('  价格影响 = 供给缺口变动率 x 1.8~2.2')
    print()

    supply = {'澳大利亚': 580, '俄罗斯': 430, '美国': 70, '蒙古': 95, '其他': 150}
    demand = {'中国': 720, '印度': 280, '日韩': 120, '其他': 90}
    total_sup = sum(supply.values())
    total_dem = sum(demand.values())
    global_gap = total_dem - total_sup

    qld = 186; aus_fob = 155; india_cfr = 175; freight = 15
    arbitrage = qld - aus_fob - freight
    india_diff = india_cfr - qld

    us_exit = 8; rus_add = 15; elas = 2.0
    sup_imp = us_exit / total_sup * 100
    px_imp = sup_imp * elas

    cny_px = s2['supply_kt'] / 4.3

    print('[全球供给 (Mt/年)]')
    for c, v in supply.items():
        print('  %s: %.0f Mt (%.1f%%)' % (c, v, v / total_sup * 100))
    print('  总计: %.0f Mt' % total_sup)

    print()
    print('[全球需求 (Mt/年)]')
    for c, v in demand.items():
        print('  %s: %.0f Mt (%.1f%%)' % (c, v, v / total_dem * 100))
    print('  总计: %.0f Mt' % total_dem)

    print()
    print('[全球供需缺口]')
    print('  缺口: %+.0f Mt/年 (%s)' % (global_gap, '短缺' if global_gap > 0 else '盈余'))
    sig3 = '小幅过剩' if (total_sup - total_dem) > 20 else '基本平衡'
    print('  评估: 全球市场 %s' % sig3)

    print()
    print('[国别套利窗口 - UBS阈值]')
    print('  中澳套利价差: $%.0f/mt (阈值>=$15)' % arbitrage)
    if arbitrage >= 15:
        print('  结论: 澳洲进口套利窗口开启，进口量预期环比上升')
    else:
        print('  结论: 套利窗口未开启')
    print('  印度CFR差值: $%.0f/mt (阈值>=$10)' % india_diff)
    if india_diff >= 10:
        print('  结论: 全球煤分流印度，中国进口供给减少')

    print()
    print('[供给扰动量化]')
    print('  美国HVA/B退出: ~%.0f Mt/年' % us_exit)
    print('  俄罗斯新产能(2H26): +%.0f Mt/年' % rus_add)
    print('  价格弹性系数: %.1f' % elas)
    print('  测算价格影响: %+.1f%% (约$%+.0f/mt)' % (px_imp, qld * px_imp / 100))

    print()
    print('[全球->国内传导]')
    print('  全球价格传导系数: 0.7~0.9')
    print('  QLD价格$186变动1%% -> 国内价格变动约%.2f%%' % (cny_px * 0.8 / 100))

    return {
        'qld': qld, 'cny_px': cny_px,
        'global_gap': global_gap, 'arbitrage': arbitrage,
        'india_diff': india_diff, 'us_exit': us_exit,
        'price_impact': px_imp, 'price_coef': 0.8,
    }

# ================================================================
# 子模块4: 多因子定价
# ================================================================
def sub4(s1, s2, s3, rows):
    sep('子模块4: 焦煤期货多因子定价与驱动归因 (三大投行整合)')
    print()

    closes = [r.get('close', 0) for r in rows if r.get('close')]
    latest = closes[-1] if closes else s3['cny_px']
    avg3y = 1280; std3y = 180

    def z(val, mean=0, std=1):
        return (val - mean) / std if std > 0 else 0

    z_util = z(s1['util_247'], 87, 3)
    z_gap = z(s2['gap_rate'], 0, 2.0)
    z_inv = -z(s2['inv_weeks'], 6.0, 1.5)
    z_px = z(s3['qld'], 195, 25)
    z_arb = z(s3['arbitrage'], 10, 8)

    factors = [
        ('需求端(高炉开工率+消费)', 0.30, z_util),
        ('供需缺口率', 0.20, z_gap),
        ('库存消费比(反向)', 0.20, z_inv),
        ('全球QLD价格', 0.15, z_px),
        ('套利窗口/贸易流', 0.10, z_arb),
        ('情绪/地缘风险', 0.05, 0.2),
    ]

    print('[8因子Z-score多因子定价模型]')
    print()
    print('  %-26s %5s %7s %8s' % ('因子', '权重', 'Z-score', '加权'))
    print('  ' + '-' * 52)
    total = 0
    for name, w, zv in factors:
        ws = zv * w
        total += ws
        n_star = min(5, max(0, int(zv + 3)))
        n_star = min(5, max(0, int(zv + 3)))
        bar = '*' * n_star + 'o' * (5 - n_star)
        print('  %-26s %5.0f%% %+7.3f %+8.3f %s' % (name[:26], w * 100, zv, ws, bar))
    print('  ' + '-' * 52)

    total_z = total / sum(f[1] for f in factors)
    vol_coef = std3y / avg3y
    fair = avg3y * (1 + total_z * vol_coef * 4)
    fair_low = avg3y * (1 + (total_z - 1) * vol_coef * 4)
    fair_high = avg3y * (1 + (total_z + 1) * vol_coef * 4)

    print()
    print('[定价结果]')
    print('  3年均值(参考): %.0f 元/吨' % avg3y)
    print('  当前价格: %.0f 元/吨' % latest)
    print('  综合Z-score: %.2f' % total_z)
    print('  合理价格: %.0f 元/吨 (区间: %.0f~%.0f)' % (fair, fair_low, fair_high))
    print('  当前偏离: %+.1f%% (正=偏高, 负=偏低)' % ((latest - fair) / fair * 100))

    if total_z >= 0.8:
        trend = '上行趋势'; action = '趋势做多'
    elif total_z <= -0.8:
        trend = '下行趋势'; action = '趋势做空'
    else:
        trend = '震荡区间'; action = '区间操作'

    print()
    print('[趋势判断]')
    print('  综合得分%.2f -> %s' % (total_z, trend))
    print('  建议操作: %s' % action)

    basis_rate = 0.8 / 100  # 估算
    print()
    print('[基差与期限结构]')
    spot_est = latest * (1 + basis_rate)
    print('  估算现货: %.0f 元/吨 | 期货: %.0f 元/吨' % (spot_est, latest))
    print('  基差率: %.2f%% (%s)' % (basis_rate * 100,
        '反向市场(期货贴水)' if basis_rate < 0 else '正向市场(期货升水)'))

    return {
        'latest': latest, 'fair': fair, 'fair_low': fair_low,
        'fair_high': fair_high, 'total_z': total_z,
        'trend': trend, 'action': action, 'basis': basis_rate,
    }

# ================================================================
# 子模块5: 情景压力测试
# ================================================================
def sub5(s1, s2, s3, s4):
    sep('子模块5: 产业链风险情景量化回测与压力测试 (三大投行情景分析)')
    print()

    curr = s4['latest']
    elas = s2['elasticity']
    price_coef = s3['price_coef']

    scenarios = [
        {'name': '乐观情景', 'prob': 0.30, 'cons': 2.0, 'imp': -10, 'qld': 15},
        {'name': '基准情景', 'prob': 0.45, 'cons': 0.5, 'imp': 0, 'qld': 0},
        {'name': '悲观情景', 'prob': 0.25, 'cons': -3.0, 'imp': 15, 'qld': -15},
    ]

    print('[三情景量化测算]')
    print()
    print('  %-10s %6s %8s %10s %8s %8s' % (
        '情景', '概率', '长材WoW', '进口增速', 'QLD变动', '目标价'))
    print('  ' + '-' * 58)
    res_list = []
    for sc in scenarios:
        dem_chg = sc['cons'] * elas
        sup_chg = -sc['imp'] * 0.4
        px_chg = (dem_chg + sup_chg) / 2 + sc['qld'] * price_coef
        target = curr * (1 + px_chg / 100)
        ret = (target - curr) / curr * 100
        res_list.append({**sc, 'px_chg': px_chg, 'target': target, 'ret': ret})
        print('  %-10s %5.0f%% %+8.1f%% %+10.0f%% %+8.1f%% %8.0f' % (
            sc['name'], sc['prob'] * 100, sc['cons'], sc['imp'], sc['qld'], target))
    print('  ' + '-' * 58)

    # 极端压力测试
    ext_target = curr * 0.75
    print()
    print('[极端压力测试]')
    print('  情景: 地产需求下滑5%% + 进口增长20%%')
    print('  压力测试目标价: %.0f 元/吨 (下跌%.0f%%)' % (
        ext_target, (curr - ext_target) / curr * 100))

    # 风险收益比
    opt = next(r['target'] for r in res_list if r['name'] == '乐观情景')
    pes = next(r['target'] for r in res_list if r['name'] == '悲观情景')
    up = opt - curr; dn = curr - pes
    rr = up / dn if dn > 0 else 999

    print()
    print('[风险收益比]')
    print('  乐观目标: %.0f | 悲观目标: %.0f | 当前: %.0f' % (opt, pes, curr))
    print('  上行空间: %+.1f%% | 下行空间: %+.1f%%' % (up / curr * 100, -dn / curr * 100))
    print('  风险收益比: %.1f:1' % rr)
    strat = ('趋势性策略' if rr >= 3 else '震荡套利策略' if rr >= 1 else '观望/对冲')
    print('  推荐: %s' % strat)

    # 概率加权收益
    e_ret = sum(r['ret'] * r['prob'] for r in res_list)
    print()
    print('[概率加权预期收益]')
    for r in res_list:
        print('  %s: %+.1f%% x %.0f%% = %+.2f%%' % (
            r['name'], r['ret'], r['prob'] * 100, r['ret'] * r['prob']))
    print('  加权预期收益: %+.2f%%' % e_ret)

    stop_loss = pes * 0.97
    take_profit = opt * 1.02
    print()
    print('[止损止盈设置]')
    print('  建议止损: %.0f 元/吨 (略低于悲观目标)' % stop_loss)
    print('  建议止盈: %.0f 元/吨 (略高于乐观目标)' % take_profit)

    return {
        'rr': rr, 'strategy': strat,
        'expected_ret': e_ret,
        'opt': opt, 'pes': pes, 'curr': curr,
        'stop_loss': stop_loss, 'take_profit': take_profit,
    }

# ================================================================
# 子模块6: 投行级投研结论
# ================================================================
def sub6(s1, s2, s3, s4, s5):
    sep('子模块6: 投行级焦煤期货投研结论 (Morgan Stanley + UBS整合)')
    print()

    print('[一、产业链核心结论]')
    print()
    print('  ① 钢铁端: 螺纹消费YoY%.1f%%，贸易商库存高于去年同期%.1f%%' % (
        s1['cons_long_yoy'], 12.0))
    print('     -> 地产需求处萎缩周期，但边际未继续恶化')
    print('     -> 板材(制造业)YoY-0.2%%，制造业相对更有韧性')
    print('     -> 库存消费比%.1f周，正常区间偏过剩' % s1['inv_ratio'])
    print()
    print('  ② 焦煤端: 供需缺口%+.0f kt/周，进口蒙古占比约%.0f%%' % (
        s2['gap_kt'], s2['supply_kt']))
    print('     -> 供给端压力持续(俄罗斯+15Mt新产能2H26落地)')
    print('     -> 需求端旺季支撑(高炉开工率%.1f%%处于高位)' % s1['util_247'])
    print()
    gap_sig = '供给缺口(短缺)' if s2['gap_kt'] > 0 else '供给盈余(过剩)'
    print('  ③ 全球: QLD基准$%d/吨，全球供需缺口%+.0fMt/年' % (
        s3['qld'], s3['global_gap']))
    print('     -> 中国焦煤处于全球价格洼地(低于进口平价$125/吨)')

    print()
    print('[二、价格判断]')
    print()
    print('  当前价格: %.0f 元/吨' % s4['latest'])
    print('  合理价格: %.0f 元/吨 (综合得分%.2f，%s)' % (
        s4['fair'], s4['total_z'], s4['trend']))
    print('  合理区间: %.0f ~ %.0f 元/吨' % (s4['fair_low'], s4['fair_high']))
    print('  关键支撑: %.0f 元/吨 (悲观情景目标)' % s5['pes'])
    print('  关键阻力: %.0f 元/吨 (乐观情景目标)' % s5['opt'])

    print()
    print('[三、交易策略]')
    print()
    print('  推荐: %s' % s5['strategy'])
    if s5['rr'] >= 1:
        print('  做多: 入场%.0f~%.0f元/吨 | 止损%.0f | 止盈%.0f' % (
            s5['curr'] * 0.97, s4['fair_low'], s5['stop_loss'], s5['take_profit']))
        print('  做空: 高位%.0f~%.0f元/吨放空 | 止损%.0f' % (
            s4['fair_high'], s5['curr'] * 1.05, s5['opt']))
    else:
        print('  当前风险收益比 < 1:1，建议观望或轻仓对冲')

    print()
    print('[四、风险提示]')
    print()
    risks = [
        ('上行', 'NDRC政策', 0.30, '焦煤到厂>850元/吨触发管控', '直接打压'),
        ('上行', '印尼配额落地', 0.25, '印尼出口<600Mt，全球煤价飙升', '进口成本上升'),
        ('下行', '美欧关税升级', 0.35, '拖累制造业-钢材-焦煤链条', '螺纹跌价'),
        ('下行', '俄罗斯产能', 0.30, '俄煤新产能+15Mt冲击', '进口增加'),
    ]
    print('  %-6s %-12s %5s  %-25s %s' % ('方向', '风险', '概率', '触发条件', '影响'))
    print('  ' + '-' * 70)
    for dir_, risk, prob, trig, imp in risks:
        icon = 'A' if '上行' in dir_ else 'D'
        print('  [%s] %-10s %4.0f%%  %-25s %s' % (icon, risk, prob * 100, trig, imp))

    print()
    print('[五、核心监控指标(每周四Mysteel更新)]')
    print()
    print('  1. 铁水开工率: >87%%=偏多, <82%%=偏空')
    print('  2. 贸易商库存周环比: 连续2周<-2%%=去库顺畅=支撑')
    print('  3. 蒙古周度进口量: >900kt=供给冲击, <700kt=供给收缩')
    print('  4. QLD焦煤价格: >$200/吨=过热信号, <$170/吨=低迷')
    print('  5. NDRC政策: >850元/吨=政策打压红线')

# ================================================================
# 主程序
# ================================================================
def main():
    print()
    print('+================================================================+')
    print('|  国际投行焦煤期货一体化分析报告                              |')
    print('|  Morgan Stanley + UBS 三大投行方法论                     |')
    print('+================================================================+')
    print()
    print('报告日期: %s | 数据: Tushare Pro + Morgan Stanley/UBS数据' % REPORT_DATE)

    contract = get_contract()
    start = (datetime.now() - timedelta(days=50)).strftime('%Y%m%d')
    rows = get_daily(contract, start, days=20)
    sym = contract.split('.')[0]
    holdings = get_holding(YESTERDAY, sym)

    s1 = sub1()
    s2 = sub2(s1)
    s3 = sub3(s2)
    s4 = sub4(s1, s2, s3, rows)
    s5 = sub5(s1, s2, s3, s4)
    sub6(s1, s2, s3, s4, s5)

    if holdings:
        sep('补充: 多空持仓结构 (Tushare fut_holding, %s)' % YESTERDAY)
        total_long = sum(h['long_hld'] or 0 for h in holdings)
        total_short = sum(h['short_hld'] or 0 for h in holdings)
        net = total_long - total_short
        ratio = total_long / total_short if total_short else 999
        if net > 0:
            print('  多头主导: 净多头%.0f手, 多/空=%.2f' % (net, ratio))
        else:
            print('  空头主导: 净空头%.0f手, 空/多=%.2f' % (-net, total_short / total_long if total_long else 999))
        top3l = sorted(holdings, key=lambda x: x['long_hld'] or 0, reverse=True)[:3]
        top3s = sorted(holdings, key=lambda x: x['short_hld'] or 0, reverse=True)[:3]
        print('  前3大多头: %s' % ', '.join('%s(%.0f手)' % (h['broker'][:8], h['long_hld'] or 0) for h in top3l))
        print('  前3大空头: %s' % ', '.join('%s(%.0f手)' % (h['broker'][:8], h['short_hld'] or 0) for h in top3s))

    print()
    print('=' * 68)
    print('  报告完毕 | %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('  框架: Morgan Stanley + UBS | 数据: Tushare Pro')
    print('=' * 68)

if __name__ == '__main__':
    main()
