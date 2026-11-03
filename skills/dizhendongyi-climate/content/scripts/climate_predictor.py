#!/usr/bin/env python3
"""
climate_predictor.py
====================
地动仪气候模型 · 综合预测主程序

整合轨道强迫计算 + FEBE求解 + 反馈放大 + CO₂情景叠加

用法:
  python3 climate_predictor.py <模式> [参数...]

模式:
  long     长期预测（轨道尺度，默认未来10万年）
  near     近期推演（叠加RCP情景，至2100年）
  extreme  极端事件预警评估
  compare  冰期/间冰期对比（-130ka vs 当前 vs +95ka）

示例:
  python3 climate_predictor.py long
  python3 climate_predictor.py near rcp45 2025 2100
  python3 climate_predictor.py extreme AMOC -10 8.2ka
"""

import numpy as np
import json, sys, math, os

# ── 加载轨道强迫数据 ──────────────────────────────────────────
ORB_FILE = '/tmp/orbital_forcing_results.json'

def load_orbital():
    if os.path.exists(ORB_FILE):
        with open(ORB_FILE) as f:
            return json.load(f)['orbital']
    return None  # 若不存在则用简化内嵌

def orbital_e(t_yr):
    return 0.028 + 0.020*np.cos(2*np.pi*t_yr/95500) \
                   + 0.010*np.cos(2*np.pi*t_yr/123800)

def orbital_Q65(t_yr):
    eps = 23.32 + 1.20*np.cos(2*np.pi*t_yr/41000)
    psi = np.sin(2*np.pi*t_yr/21700) + 0.3*np.sin(2*np.pi*t_yr/19000)
    S0 = 1361.0
    return (S0/4) * (1 - 0.477*np.sin(np.deg2rad(eps))**2 + 0.016*psi*np.pi)

# ── Mittag-Leffler ──────────────────────────────────────────────
def ml_e1a(z, a=1.0, n=150):
    r = np.asarray(z, dtype=np.float64)
    res = np.zeros_like(r)
    for k in range(n):
        g = a + k*a
        if g > 200: break
        term = np.power(r, k) / math.gamma(g)
        res += term
        if np.all(np.abs(term) < 1e-14*np.abs(res+1e-30)): break
    return res

# ── FEBE 求解 ──────────────────────────────────────────────────
def febe(h, tau, C, F, t):
    z = -np.power(t/tau, h)
    return np.power(tau, h)/C * (1 - ml_e1a(z, h)) * F

# ── CO₂ 情景 ───────────────────────────────────────────────────
CO2_SCENARIOS = {
    'rcp26': {2020:415, 2030:416, 2050:422, 2100:430},
    'rcp45': {2020:415, 2030:420, 2050:442, 2100:500},
    'rcp60': {2020:418, 2030:424, 2050:450, 2100:600},
    'rcp85': {2020:425, 2030:432, 2050:492, 2100:800},
}

def co2_forcing(co2_ppm):
    """IPCC 近似：ΔQ = 5.35 * ln(CO2/278) W/m²"""
    return 5.35 * math.log(co2_ppm / 278.0)

# ── 四大反馈放大 ────────────────────────────────────────────────
LAMBDA_SYS = 2.5  # 综合放大倍数（冰-反照率+CO₂+AMOC+植被）

# ── 预测核心 ───────────────────────────────────────────────────
def predict_long_term(n_future=100000, h=0.6, tau=3e4, C=8.4e8):
    """
    长期气候预测（自然轨道强迫，无人为CO₂）
    """
    t = np.arange(0, n_future+1000, 1000)
    q65 = orbital_Q65(t)
    q0  = orbital_Q65(np.array([0.0]))[0]
    F_orb = q65 - q0   # 相对强迫 W/m²

    dT_base = febe(h, tau, C, F_orb, t)
    dT_sys  = dT_base * LAMBDA_SYS

    # 冰期判定（Q65 < 445 ≈ 冰期条件）
    q_threshold = 445.0
    results = []
    for ti, qi, dT in zip(t, q65, dT_sys):
        status = '冰期风险' if qi < q_threshold else '间冰期/暖期'
        results.append({
            'time_yr':    float(ti),
            'Q65_Wm2':    round(float(qi), 2),
            'F_orb_Wm2':  round(float(F_orb[np.where(t==ti)[0][0]] if ti in t else 0), 3),
            'dT_K':       round(float(dT), 3),
            'status':     status
        })
    return results

def predict_near_term(scenario='rcp45', t_start=2025, t_end=2100):
    """
    近期气候推演（叠加RCP情景）
    """
    scenario_data = CO2_SCENARIOS.get(scenario.lower(), CO2_SCENARIOS['rcp45'])
    years = sorted(scenario_data.keys())
    co2_vals = [scenario_data[y] for y in years]
    # 线性插值
    t_range = np.arange(t_start, t_end+1)
    co2_interp = np.interp(t_range, np.array(years, dtype=float), np.array(co2_vals, dtype=float))

    t_yr_past = t_start - 2025  # 转换为距今年
    # 自然强迫（接近0，当前间冰期）
    q65_now = orbital_Q65(np.array([t_yr_past]))[0]
    F_nat   = q65_now - orbital_Q65(np.array([0.0]))[0]  # ~0

    h, tau, C = 0.6, 3e4, 8.4e8
    results = []
    for ti, co2i in zip(t_range, co2_interp):
        t_yr = ti - 2025
        F_co2 = co2_forcing(co2i)
        # 近期：人为强迫主导（+自然强迫≈0）
        F_tot = F_nat + F_co2
        dT = febe(h, tau, C, F_tot, np.array([1e3]))[0] * LAMBDA_SYS
        results.append({
            'year':       int(ti),
            'co2_ppm':   round(float(co2i), 1),
            'F_CO2_Wm2': round(F_co2, 3),
            'F_total':    round(F_tot, 3),
            'dT_K':      round(float(dT), 2)
        })
    return results

# ── 极端事件评估 ────────────────────────────────────────────────
def assess_extreme(event_type, current_value, anomaly_percent):
    """
    极端事件预警评估。

    参数:
        event_type: 'AMOC', 'FORCING', 'ICE' 等
        current_value: 当前监测值
        anomaly_percent: 偏离正常值的百分比

    返回:
        dict: {预警等级, 描述, 类比案例, 参考持续时间}
    """
    CASES = {
        'AMOC': {
            'name': 'AMOC减弱类事件（8.2ka冷事件型）',
            'anomaly_trigger': -20,   # % 偏离触发阈值
            'history': '8,200年前，AMOC减弱约30%，北半球降温2–4°C，持续150–200年',
            'duration': '150–200年',
            'precursor': '北大西洋淡水通量↑ + AMOC强度偏差>20%',
            'level': 'orange' if anomaly_percent < -20 else 'green'
        },
        'ICE': {
            'name': '冰盖快速消退（Heinrich事件型）',
            'anomaly_trigger': -15,
            'history': '末次冰期内6次，格陵兰降温2–5°C，北大西洋冰筏碎屑增加',
            'duration': '500–2,000年',
            'precursor': '北大西洋IRD通量↑ + 冰盖物质平衡快速亏损',
            'level': 'red' if anomaly_percent < -30 else 'orange' if anomaly_percent < -15 else 'green'
        },
        'FORCING': {
            'name': '辐射强迫极端偏移（Green Sahara逆转型）',
            'anomaly_trigger': -8,
            'history': '约5,000年前绿色撒哈拉结束，北非降水骤减',
            'duration': '1,000–3,000年',
            'precursor': '夏季辐射强迫（65°N）变化 > 8 W/m²',
            'level': 'yellow' if abs(anomaly_percent) > 8 else 'green'
        }
    }

    case = CASES.get(event_type, CASES['FORCING'])
    return {
        'event_type':   event_type,
        'current_value': current_value,
        'anomaly_pct':  anomaly_percent,
        'case_name':    case['name'],
        'history':       case['history'],
        'duration':      case['duration'],
        'precursor':     case['precursor'],
        'warning_level': case['level'],
        'recommendation': f'持续监测{event_type}强度，关注{case["duration"]}尺度响应'
    }

# ── 冰期/间冰期对比 ────────────────────────────────────────────
def compare_glacial_interglacial():
    """
    三个典型时期的对比分析：
      -130ka: 末次间冰期（Eemian，约130,000年前）
       当前: 全新世（间冰期）
      +95ka:  下一个大冰期（预测，约95,000年后）
    """
    periods = {
        '130ka前（末次间冰期,Eemian）': -130000,
        '当前（全新世,2000CE）':          0,
        '95ka后（下个冰期预测）':         95000,
    }
    results = []
    for label, t_yr in periods.items():
        e   = orbital_e(np.array([t_yr]))[0]
        q   = orbital_Q65(np.array([t_yr]))[0]
        q0  = orbital_Q65(np.array([0.0]))[0]
        F   = q - q0
        h, tau, C = 0.6, 3e4, 8.4e8
        dT  = febe(h, tau, C, F, np.array([100000]))[0] * LAMBDA_SYS
        status = '冰期' if q < 445 else '间冰期/暖期'
        results.append({
            'period':     label,
            'eccentricity': round(float(e), 4),
            'Q65_Wm2':   round(float(q), 1),
            'F_orb_Wm2': round(float(F), 2),
            'dT_amped_K':round(float(dT), 2),
            'status':     status
        })
    return results

# ── 主程序 ──────────────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 climate_predictor.py <mode> [args...]")
        print("模式: long | near | extreme | compare")
        sys.exit(1)

    mode = sys.argv[1].lower()

    print("="*65)
    print("地动仪气候模型 · 综合预测系统 v1.0")
    print("="*65)

    if mode == 'long':
        results = predict_long_term()
        print(f"\n{'距今年(yr)':>12} | {'Q65(W/m²)':>11} | {'F_orb(W/m²)':>13} | {'ΔT(K)':>8} | {'状态':^14}")
        print("-"*65)
        labels = {0:'当前', -23000:'2.3万年', -41000:'4.1万年', -95000:'9.5万年', -130000:'13万年'}
        for r in results:
            t = r['time_yr']
            if t % 10000 == 0 or t in [1000, 5000]:
                lbl = labels.get(t, f'{t//1000}ka' if t else '当前')
                print(f"{t:>12,.0f} | {r['Q65_Wm2']:>11.1f} | {r['F_orb_Wm2']:>13.2f} | {r['dT_K']:>8.2f} | {r['status']:^14}")

    elif mode == 'near':
        scn  = sys.argv[2] if len(sys.argv) > 2 else 'rcp45'
        t0   = int(sys.argv[3]) if len(sys.argv) > 3 else 2025
        t1   = int(sys.argv[4]) if len(sys.argv) > 4 else 2100
        results = predict_near_term(scn, t0, t1)
        print(f"\n近期气候推演 · {scn.upper()} 情景 ({t0}–{t1})")
        print(f"\n{'年份':>6} | {'CO₂(ppm)':>10} | {'ΔQ_CO₂(W/m²)':>14} | {'F_total(W/m²)':>15} | {'ΔT_amped(K)':>13}")
        print("-"*65)
        for r in results:
            if r['year'] in [2030, 2050, 2060, 2080, 2100] or r['year'] % 20 == 0:
                print(f"{r['year']:>6} | {r['co2_ppm']:>10.1f} | {r['F_CO2_Wm2']:>14.3f} | {r['F_total']:>15.3f} | {r['dT_K']:>13.2f}")
        print("\n⚠️ 注：近期人为强迫主导（自然轨道强迫 < 0.5 W/m²），")
        print("   以上 ΔT 为含四大反馈的综合估算，非纯粹轨道效应。")

    elif mode == 'extreme':
        evt  = sys.argv[2] if len(sys.argv) > 2 else 'AMOC'
        val  = float(sys.argv[3]) if len(sys.argv) > 3 else 15.0
        pct  = float(sys.argv[4]) if len(sys.argv) > 4 else -10.0
        result = assess_extreme(evt, val, pct)
        WARN_EMOJI = {'green':'🟢','yellow':'🟡','orange':'🟠','red':'🔴'}
        emoji = WARN_EMOJI.get(result['warning_level'], '⚪')
        print(f"\n极端事件预警评估 {emoji}")
        print(f"事件类型: {result['event_type']} — {result['case_name']}")
        print(f"当前值: {result['current_value']} | 偏离: {result['anomaly_pct']}%")
        print(f"预警等级: {result['warning_level'].upper()} {emoji}")
        print(f"历史类比: {result['history']}")
        print(f"参考持续时间: {result['duration']}")
        print(f"前兆指标: {result['precursor']}")
        print(f"建议: {result['recommendation']}")

    elif mode == 'compare':
        results = compare_glacial_interglacial()
        print(f"\n冰期-间冰期典型时期对比")
        print(f"\n{'时期':^30} | {'e':>6} | {'Q65(W/m²)':>10} | {'F(W/m²)':>10} | {'ΔT(K)':>7} | {'状态':^8}")
        print("-"*80)
        for r in results:
            print(f"{r['period']:^30} | {r['eccentricity']:>6.4f} | "
                  f"{r['Q65_Wm2']:>10.1f} | {r['F_orb_Wm2']:>10.2f} | "
                  f"{r['dT_amped_K']:>7.2f} | {r['status']:^8}")
        print("\n注：ΔT 为相对当前值（2000CE），含四大反馈放大。")
    else:
        print(f"未知模式: {mode}")
        sys.exit(1)
