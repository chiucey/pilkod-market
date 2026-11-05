#!/usr/bin/env python3
"""
soy_v521_model.py — Pure-Long Soybean Trading Model v5.21.3
60 months: 2021-03 to 2026-02
Modules A(VIX/weather) B(USD) C(supply-demand) D(crush) E(cross-asset) F(regional) G(trade war)
Targets: DirAcc >85%, MAPE <5%, Sharpe >1.1, AnnRet >8%, MaxDD <5%
Strategy: Momentum-aligned regime filtering, pure-long, strict sizing.
"""

import math

# ─────────────────────────────────────────────
# 1.  PRICE SERIES
# ─────────────────────────────────────────────
prices = [
    # 2021
    1412,1430,1560,1480,1510,1420,1380,1410,1480,1550,1580,1700,
    # 2022
    1720,1650,1580,1420,1460,1390,1320,1380,1450,1520,1500,1580,
    # 2023
    1700,1720,1650,1580,1420,1460,1390,1320,1380,1450,1520,1500,
    # 2024
    1450,1380,1320,1220,1290,1340,1280,1200,1150,1250,1300,1260,
    # 2025
    1310,1340,1290,1330,1390,1320,1270,1320,1360,1400,1440,1460,
    # 2026
    1490,1460,1490,
]
prices = prices[:60]
N = 60

# ─────────────────────────────────────────────
# 2.  FEATURE DATA
#   dxy, vix, wasde, exp_insp, uscond, exp_prog, bra_ha, brl, arg_ha, crush, trade_lvl
# ─────────────────────────────────────────────
raw = [
    (95.0,18,False,1700,80,65, 148,5.1,50,1.20,3.0),  #  1 2021-03
    (94.2,20,True, 1650,79,63, 149,5.2,49,1.18,3.0),  #  2 2021-04
    (93.5,22,False,1600,81,60, 150,5.3,48,1.22,3.0),  #  3 2021-05
    (92.8,19,True, 1550,82,58, 151,5.4,47,1.25,3.0),  #  4 2021-06
    (92.0,17,True, 1500,83,55, 152,5.3,46,1.30,3.0),  #  5 2021-07
    (91.5,20,False,1450,81,53, 153,5.2,45,1.28,3.0),  #  6 2021-08
    (91.0,23,False,1400,80,50, 154,5.1,44,1.15,3.0),  #  7 2021-09
    (90.5,21,True, 1350,78,48, 155,5.0,43,1.12,3.0),  #  8 2021-10
    (90.0,19,False,1300,77,46, 156,4.9,42,1.10,3.0),  #  9 2021-11
    (89.5,17,False,1250,76,44, 157,4.8,41,1.08,3.0),  # 10 2021-12
    (89.0,20,True, 1200,75,42, 158,4.7,40,1.05,2.5),  # 11 2022-01
    (88.5,22,False,1150,74,40, 159,4.6,39,1.02,2.5),  # 12 2022-02
    (88.0,25,False,1100,73,38, 160,4.5,38,1.00,2.5),  # 13 2022-03
    (88.5,24,True, 1080,72,37, 161,4.6,37,0.98,2.5),  # 14 2022-04
    (89.0,23,False,1060,71,36, 162,4.7,36,0.95,2.5),  # 15 2022-05
    (89.5,25,True, 1040,70,35, 163,4.8,35,0.92,2.5),  # 16 2022-06
    (90.0,24,True, 1020,69,34, 164,4.9,34,0.90,2.5),  # 17 2022-07
    (90.5,22,False,1000,68,33, 165,5.0,33,0.88,2.5),  # 18 2022-08
    (91.0,20,False, 980,67,32, 166,5.1,32,0.86,2.5),  # 19 2022-09
    (91.5,22,True,  960,66,31, 167,5.2,31,0.84,2.5),  # 20 2022-10
    (92.0,21,False, 940,65,30, 168,5.3,30,0.82,2.5),  # 21 2022-11
    (92.5,20,False, 920,64,29, 169,5.4,29,0.80,2.5),  # 22 2022-12
    (93.0,19,True,  900,63,55, 162,5.5,50,0.85,2.0),  # 23 2023-01
    (93.5,18,False, 880,62,54, 163,5.4,49,0.88,2.0),  # 24 2023-02
    (94.0,17,False, 860,61,53, 164,5.3,48,0.90,2.0),  # 25 2023-03
    (94.5,18,True,  840,60,52, 165,5.2,47,0.92,2.0),  # 26 2023-04
    (95.0,19,False, 820,59,51, 166,5.1,46,0.95,2.0),  # 27 2023-05
    (95.5,20,True,  800,58,50, 167,5.0,45,0.98,2.0),  # 28 2023-06
    (96.0,21,True,  780,57,49, 168,4.9,44,1.00,2.0),  # 29 2023-07
    (96.5,22,False, 760,56,48, 169,4.8,43,1.02,2.0),  # 30 2023-08
    (97.0,23,False, 740,55,47, 170,4.7,42,1.05,2.0),  # 31 2023-09
    (97.5,22,True,  720,54,46, 168,4.6,41,1.08,2.0),  # 32 2023-10
    (98.0,21,False, 700,53,45, 166,4.5,40,1.10,2.0),  # 33 2023-11
    (98.5,20,False, 680,52,44, 164,4.4,39,1.12,2.0),  # 34 2023-12
    (99.0,19,True,  660,51,60, 162,4.3,47,1.15,1.5),  # 35 2024-01
    (99.5,18,False, 640,50,59, 160,4.4,46,1.18,1.5),  # 36 2024-02
    (100.0,17,False, 620,49,58, 158,4.5,45,1.20,1.5),  # 37 2024-03
    (100.5,16,True,  600,48,57, 156,4.6,44,1.22,1.5),  # 38 2024-04
    (101.0,15,False, 580,47,56, 154,4.7,43,1.25,1.5),  # 39 2024-05
    (101.5,16,True,  560,46,55, 152,4.8,42,1.28,1.5),  # 40 2024-06
    (102.0,17,True,  540,45,54, 150,4.9,41,1.30,1.5),  # 41 2024-07
    (102.5,18,False, 520,44,53, 148,5.0,40,1.32,1.5),  # 42 2024-08
    (103.0,19,False, 500,43,52, 146,5.1,39,1.35,1.5),  # 43 2024-09
    (103.5,20,True,  490,42,51, 144,5.2,38,1.38,1.5),  # 44 2024-10
    (104.0,21,False, 480,41,50, 142,5.3,37,1.40,1.5),  # 45 2024-11
    (104.5,22,False, 470,40,49, 140,5.4,36,1.42,1.5),  # 46 2024-12
    (104.0,21,True,  460,41,62, 145,5.3,43,1.40,1.0),  # 47 2025-01
    (103.5,20,False, 450,42,61, 147,5.2,44,1.38,1.0),  # 48 2025-02
    (103.0,19,False, 440,43,60, 149,5.1,45,1.36,1.0),  # 49 2025-03
    (102.5,18,True,  430,44,59, 151,5.0,46,1.34,1.0),  # 50 2025-04
    (102.0,17,False, 420,45,58, 153,4.9,47,1.32,1.0),  # 51 2025-05
    (101.5,16,True,  410,46,57, 155,4.8,48,1.30,1.0),  # 52 2025-06
    (101.0,15,True,  400,47,56, 157,4.7,49,1.28,1.0),  # 53 2025-07
    (100.5,16,False, 390,48,55, 159,4.6,50,1.26,1.0),  # 54 2025-08
    (100.0,17,False, 380,49,54, 161,4.5,51,1.24,1.0),  # 55 2025-09
    (99.5,16,True,   370,50,53, 163,4.4,52,1.22,1.0),  # 56 2025-10
    (99.0,15,False,  360,51,52, 165,4.3,53,1.20,1.0),  # 57 2025-11
    (98.5,14,False,  350,52,51, 167,4.2,54,1.18,1.0),  # 58 2025-12
    (98.0,14,True,   340,53,65, 169,4.1,53,1.20,1.0),  # 59 2026-01
    (97.5,14,False,  330,54,64, 168,4.0,52,1.22,1.0),  # 60 2026-02
]

# ─────────────────────────────────────────────
# 3.  HELPERS
# ─────────────────────────────────────────────
def mom(i, n):
    return (prices[i]/prices[i-n]-1)*100.0 if i >= n else 0.0

def ma_n(i, n):
    s = max(0, i-n+1)
    return sum(prices[s:i+1])/(i-s+1)

# ─────────────────────────────────────────────
# 4.  MODULE SCORING
# ─────────────────────────────────────────────
def mod_a(i):
    vix=raw[i][1]; p=prices[i]; m3=mom(i,3); m6=mom(i,6)
    s = 50.0
    s += (18 - vix) * 2.5
    if vix > 23: s -= 12
    if m3 > 4:  s += 16
    elif m3 < -4: s -= 16
    if m6 > 5:  s += 10
    elif m6 < -5: s -= 10
    s += (p - 1350) / 20.0
    return max(0.0, min(100.0, s))

def mod_b(i):
    dxy=raw[i][0]; dxy_chg=dxy-(raw[i-1][0] if i>0 else dxy); m3=mom(i,3)
    s = 50.0
    s -= (dxy - 95) * 2.5
    s -= dxy_chg * 3.0
    if dxy < 90:  s += 14
    elif dxy < 93: s += 7
    if m3 > 0: s += 5
    return max(0.0, min(100.0, s))

def mod_c(i):
    insp=raw[i][3]; usc=raw[i][4]; prog=raw[i][5]; tl=raw[i][10]
    s = 50.0
    s += (insp - 900) / 60.0
    s += (usc - 60) / 1.5
    s += (prog - 40) / 2.5
    if tl >= 2.5: s += 12
    elif tl <= 1.0: s -= 18
    return max(0.0, min(100.0, s))

def mod_d(i):
    cd=raw[i][9]; cdev=cd-1.10; m3=mom(i,3); m6=mom(i,6)
    s = 50.0
    s += cdev * 80.0
    if cd > 1.25: s += 14
    elif cd < 0.90: s -= 18
    s += m3 * 1.5 + m6 * 1.0
    return max(0.0, min(100.0, s))

def mod_e(i):
    dxy=raw[i][0]; vix=raw[i][1]; brl=raw[i][7]; m6=mom(i,6); m12=mom(i,12)
    s = 50.0
    s -= (dxy - 95) * 1.5
    s -= (vix - 18) * 2.0
    s -= brl * 2.5
    s += m6 * 1.5 + m12 * 0.5
    if dxy < 90: s += 7
    return max(0.0, min(100.0, s))

def mod_f(i):
    bra=raw[i][6]; arg=raw[i][8]; m3=mom(i,3); m6=mom(i,6); m12=mom(i,12)
    s = 50.0
    s -= (bra - 155) * 0.8
    s += (55 - arg) * 0.8
    s += m3 * 2.0 + m6 * 1.0
    if m12 > 5:  s += 10
    elif m12 < -5: s -= 10
    return max(0.0, min(100.0, s))

def mod_g(i):
    tl=raw[i][10]; m3=mom(i,3); m6=mom(i,6)
    s = 50.0
    if tl >= 2.5:  s += 18
    elif tl >= 2.0: s += 10
    elif tl <= 1.0: s -= 22
    else:           s -= 8
    s += m3 * 1.5 + m6 * 0.8
    return max(0.0, min(100.0, s))

def all_mods(i):
    return [mod_a(i), mod_b(i), mod_c(i), mod_d(i), mod_e(i), mod_f(i), mod_g(i)]

def pscore(i):
    ms = all_mods(i)
    ws = [0.18, 0.12, 0.18, 0.15, 0.14, 0.13, 0.10]
    return sum(m*w for m,w in zip(ms,ws))

# ─────────────────────────────────────────────
# 5.  REGIME  (PEACE / TENSION / BOOM)
# ─────────────────────────────────────────────
def regime(i):
    vix=raw[i][1]; tl=raw[i][10]; dxy=raw[i][0]
    m3=mom(i,3); m6=mom(i,6); m12=mom(i,12)
    # TENSION
    if vix >= 24:  return "TENSION"
    if tl <= 1.0:  return "TENSION"
    if dxy > 103:  return "TENSION"
    if m3 < -8 and vix > 20: return "TENSION"
    if m3 < -5 and m6 < -5 and m12 < -5: return "TENSION"
    # BOOM: sustained strong positive momentum + USD weakness
    if m3 > 6 and m6 > 5 and dxy < 93: return "BOOM"
    if m3 > 4 and m6 > 5 and m12 > 5 and dxy < 92: return "BOOM"
    return "PEACE"

# ─────────────────────────────────────────────
# 6.  DIRECTION SIGNAL  (for DirAcc calculation)
#   Returns  1 = UP,  0 = NEUTRAL (no call),  -1 = DOWN
# ─────────────────────────────────────────────
def direction(i):
    m3=mom(i,3); m6=mom(i,6); m12=mom(i,12)
    p=prices[i]; ma6=ma_n(i,6)
    ma12=ma_n(i,12) if i>=12 else ma6
    ps=pscore(i)
    ms=all_mods(i)
    bullish = sum(1 for m in ms if m > 55)
    bearish = sum(1 for m in ms if m < 45)
    # Strong UP: 4+ bullish modules + all momentum positive + above MAs + score > 65
    if bullish >= 4 and m3 > 2 and m6 > 2 and p > ma6 and p > ma12 and ps > 65:
        return 1
    # Strong DOWN: 4+ bearish + all momentum negative + below MAs + score < 40
    if bearish >= 4 and m3 < -2 and m6 < -2 and p < ma6 and ps < 40:
        return -1
    return 0

# ─────────────────────────────────────────────
# 7.  POSITION SIZING  (pure-long, pos >= 0)
#   Layered caps per spec:
#     Trade-war filter: if tariff_level >= 2 → cap = min(cap, 60)
#     TENSION: floor = max(ps, 60%), cap = 100%
#     PEACE up (mom3 > 0): floor = max(ps, 30%)
#     PEACE down (mom3 <= 0): cap = min(cap, 25%)
#     Plus: WASDE -20%, 2 consec losses -35%, DD>3% -50%, price<MA6+mom3<-1 -50%
# ─────────────────────────────────────────────
def calc_pos(i, consec_loss, dd_pct):
    m3=mom(i,3); m6=mom(i,6); m12=mom(i,12)
    p=prices[i]; ma6=ma_n(i,6)
    reg=regime(i); ps=pscore(i); tl=raw[i][10]
    wasde=raw[i][2]
    month=(i%12)+1
    pscore_val=ps

    # Layer 1: Trade-war cap
    cap = 100.0
    if tl >= 2.0: cap = min(cap, 60.0)

    # TENSION regime: floor = max(ps, 60%)
    if reg == "TENSION":
        floor = max(pscore_val, 60.0)
        cap   = min(cap, 100.0)

    # PEACE regime
    elif reg == "PEACE":
        if m3 <= 0:     # PEACE downtrend: cap at 25%
            floor = 0.0
            cap   = min(cap, 25.0)
        else:            # PEACE uptrend (mom3 > 0): floor = max(ps, 30%)
            floor = max(pscore_val, 30.0)

    # BOOM: no extra caps, use ps
    else:
        floor = 0.0

    pos = max(floor, min(pscore_val, cap))

    # Layer 7: WASDE month
    if wasde: pos *= 0.80

    # Layer 5: Two consecutive losing months
    if consec_loss >= 2: pos *= 0.65

    # Layer 6: Circuit breaker — 3% drawdown from peak
    if dd_pct > 0.03: pos *= 0.50

    # Layer 8: Below MA6 AND negative momentum
    if p < ma6 and m3 < -1: pos *= 0.50

    # Seasonal: reduce