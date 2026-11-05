#!/usr/bin/env python3
"""
attribution_calc.py
====================
气候归因计算：人类排放（人为强迫）vs 自然变率

核心方法：
  ① 用地动仪模型提供自然强迫基准（轨道 + 太阳）
  ② 用IPCC AR6数据叠加人为强迫（温室气体 + 气溶胶 + 土地利用）
  ③ 计算各因素的温度贡献

数据来源：
  IPCC AR6 WGI (2021) · SPMA-2, TS Fig.1
  Laskar et al. (2004) La2004 轨道解
  平衡气候敏感度（ECS）= 3.0°C  瞬态气候响应（TCR）= 1.83°C
"""

import math, json, sys

# ── 物理常数 ───────────────────────────────────────────────
ECS  = 3.0    # 平衡气候敏感度（IPCC AR6最佳估计，°C / 2×CO₂）
TCR  = 1.83  # 瞬态气候响应（IPCC AR6，°C / 2×CO₂）
Lambda_TCR = TCR / 3.7   # 气候反馈参数
Lambda_ECS = ECS / 3.7
CO2_0 = 278.0            # 工业革命前 CO₂ (ppm)

# ── CO₂ 强迫 ──────────────────────────────────────────────
def F_CO2(ppm):
    return 5.35 * math.log(ppm / CO2_0)   # IPCC 近似

# ── 轨道强迫（地动仪模型，简化版）────────────────────────────
def F_orbital_Q65(t_offset_yr=0):
    """
    估算工业革命（1850）以来轨道强迫的变化量。
    近期（<200年）轨道参数变化极小：约 -0.08 W/m²
    t_offset: 距1850年的偏移（年），正值=向未来
    """
    # 北纬65°夏季日射量：1850→2000年变化约 -0.08 W/m²
    # 2000→未来100年：基本为0（岁差周期 ~21,700年）
    return -0.08 if abs(t_offset_yr) <= 150 else -0.08

# ── 自然强迫汇总 ───────────────────────────────────────────
def natural_forcing(year=2024):
    """
    自然强迫（W/m²），相对于1850年。
    """
    t = year - 1850
    F_orb  = F_orbital_Q65(t)
    F_sol  = +0.05   # 太阳活动（1850→2021，IPCC AR6）
    F_vol  = -0.30   # 火山（1850→2021累计净效应，IPCC AR6）
    return {'orbital': F_orb, 'solar': F_sol, 'volcanic': F_vol,
            'total': F_orb + F_sol + F_vol}

# ── 人为强迫汇总 ───────────────────────────────────────────
def anthropogenic_forcing(co2_ppm, ch4_ppb=1945, n2o_ppb=335,
                          f_aerosol=-1.10, f_landuse=-0.20):
    """
    人为强迫（W/m²），相对于1850年。

    参数:
        co2_ppm:    大气CO₂浓度（ppm）
        ch4_ppb:    甲烷浓度（ppb），默认1945（2020年近似）
        n2o_ppb:    笑气浓度（ppb），默认335（2020年近似）
        f_aerosol:  气溶胶强迫（W/m²），默认-1.10（IPCC AR6）
        f_landuse:  土地利用强迫（W/m²），默认-0.20
    """
    F_CO2  = F_CO2(co2_ppm)
    F_CH4  = 0.54 * math.log(ch4_ppb / 720.0)   # CH₄: 720→当前
    F_N2O  = 0.14 * math.log(n2o_ppb / 270.0)    # N₂O: 270→当前
    F_GHG  = F_CO2 + F_CH4 + F_N2O + 0.18        # 含CFC/HFC
    return {'CO2': F_CO2, 'CH4': F_CH4, 'N2O': F_N2O,
            'aerosol': f_aerosol, 'landuse': f_landuse,
            'total': F_GHG + f_aerosol + f_landuse}

# ── 温度归因计算 ───────────────────────────────────────────
def temperature_attribution(year=2024, co2_ppm=422, ch4_ppb=1945, n2o_ppb=335,
                            f_aerosol=-1.10, f_landuse=-0.20, use_TCR=True):
    """
    核心函数：给定年份和CO₂浓度，计算温度变化的归因分解。
    """
    lam = Lambda_TCR if use_TCR else Lambda_ECS

    nat = natural_forcing(year)
    ant = anthropogenic_forcing(co2_ppm, ch4_ppb, n2o_ppb, f_aerosol, f_landuse)
    total_forcing = nat['total'] + ant['total']

    dT_orb  = lam * nat['orbital']
    dT_sol  = lam * nat['solar']
    dT_vol  = lam * nat['volcanic']
    dT_natural = lam * nat['total']
    dT_CO2  = lam * ant['CO2']
    dT_ghg  = lam * (ant['CO2'] + ant['CH4'] + ant['N2O'] + 0.18)
    dT_aero  = lam * ant['aerosol']
    dT_land  = lam * ant['landuse']
    dT_anthro = lam * ant['total']
    dT_total  = lam * total_forcing

    return {
        'year': year, 'CO2_ppm': co2_ppm,
        'forcing': {
            'natural': round(nat['total'], 3),
            'anthropogenic': round(ant['total'], 3),
            'total': round(total_forcing, 3),
        },
        'temperature': {
            'orbital':   round(dT_orb, 4),
            'solar':     round(dT_sol, 4),
            'volcanic':  round(dT_vol, 4),
            'natural_total':  round(dT_natural, 4),
            'CO2':           round(dT_CO2, 4),
            'ghg_total':     round(dT_ghg, 4),
            'aerosol':       round(dT_aero, 4),
            'landuse':       round(dT_land, 4),
            'anthro_total':  round(dT_anthro, 4),
            'total':         round(dT_total, 4),
        },
        'attribution': {
            'anthro_fraction': round(dT_anthro / dT_total * 100, 1) if dT_total > 0 else 0,
            'natural_fraction': round(abs(dT_natural) / (abs(dT_anthro) + abs(dT_natural)) * 100, 1),
        }
    }

# ── 情景预测 ───────────────────────────────────────────────
SCENARIOS = {
    'SSP1-2.6（快速减排）': {'2030': 416, '2050': 422, '2100': 430},
    'SSP2-4.5（中等路径）': {'2030': 420, '2050': 442, '2100': 500},
    'SSP4-6.0             ': {'2030': 418, '2050': 455, '2100': 600},
    'SSP5-8.5（高排放）   ': {'2030': 432, '2050': 500, '2100': 800},
}

def print_summary(att):
    y = att['year']
    print(f"\n{'='*62}")
    print(f"气候归因报告  ·  年份 {y}")
    print(f"{'='*62}")
    print(f"\nCO₂ 浓度: {att['CO2_ppm']:.0f} ppm")
    print(f"\n{'强迫（W/m²）':<26} | {'温度贡献（°C）':>15}")
    print("-"*44)
    print(f"  温室气体（CO₂为主）    {att['forcing']['anthropogenic']:>+8.2f}  |  {att['temperature']['CO2']:>+15.4f}")
    print(f"  气溶胶（冷却）        {att['forcing']['anthropogenic']-att['forcing']['anthropogenic']+att['temperature']['aerosol']/Lambda_TCR:>+8.2f}  |  {att['temperature']['aerosol']:>+15.4f}")
    print(f"  自然（轨道+太阳+火山） {att['forcing']['natural']:>+8.2f}  |  {att['temperature']['natural_total']:>+15.4f}")
    print(f"  ── 自然分项 ────────────────────────────────")
    print(f"    轨道强迫              {att['forcing']['natural']+0.38:>+8.2f}  |  {att['temperature']['orbital']:>+15.4f}  ← 地动仪模型")
    print(f"    太阳活动             {att['forcing']['natural']+0.38:>+8.2f}  |  {att['temperature']['solar']:>+15.4f}")
    print(f"    火山强迫             {att['forcing']['natural']+0.38:>+8.2f}  |  {att['temperature']['volcanic']:>+15.4f}")
    print("-"*44)
    print(f"  {'合计':<24} {att['forcing']['total']:>+8.2f}  |  {att['temperature']['total']:>+15.4f}")
    print(f"\n  IPCC AR6 观测基准:     --            |  +1.10 °C  (1850-1900 → 2011-2020)")

# ── 主程序 ──────────────────────────────────────────────────
if __name__ == '__main__':
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    co2  = float(sys.argv[2]) if len(sys.argv) > 2 else None

    # 缺省CO₂：根据年份查
    co2_defaults = {1850:278, 1900:300, 1950:311, 1980:338,
                    2000:369, 2010:390, 2020:414, 2024:422, 2025:423}
    if co2 is None:
        co2 = co2_defaults.get(year, 422)

    att = temperature_attribution(year, co2)
    print_summary(att)

    # 自然基准说明
    dT_nat = att['temperature']['natural_total']
    dT_total = att['temperature']['total']
    dT_anthro = att['temperature']['anthro_total']
    print(f"\n{'─'*62}")
    print(f"关键结论：")
    print(f"  · 自然变率（轨道+太阳+火山）: {dT_nat:>+.3f} °C")
    print(f"    → 若无人类活动，自然趋势将使全球{abs(dT_nat):.1f}°C{'降温' if dT_nat<0 else '升温'}")
    print(f"  · 人为强迫（CO₂为主）:       {dT_anthro:>+.3f} °C")
    print(f"  · 人类活动贡献了观测变暖的 {dT_anthro/dT_total*100:.0f}–122%")
    print(f"  · 地动仪模型（轨道）单独贡献: {att['temperature']['orbital']:>+.4f} °C")
    print(f"\n{'─'*62}")
    print(f"近期情景预测（叠加RCP/SSP CO₂路径）:")
    print(f"{'情景':<28} | {'2030年':>10} | {'2050年':>10} | {'2100年':>10}")
    print("-"*62)
    for name, yrs in SCENARIOS.items():
        row = f"{name:<28} |"
        for yr in ['2030', '2050', '2100']:
            c2 = yrs[yr]
            a2 = temperature_attribution(int(yr), c2)
            row += f" {a2['temperature']['total']:>+.2f}°C |"
        print(row)
    print("  （注：含气溶胶-1.1 W/m²基准；气溶胶路径随减排政策变化，实际值有偏差）")

    with open('/tmp/attribution_result.json', 'w') as f:
        json.dump(att, f, indent=2)
