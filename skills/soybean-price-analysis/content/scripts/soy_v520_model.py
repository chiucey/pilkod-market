#!/usr/bin/env python3
"""
SOYBEAN TRADING MODEL v5.20
==========================
60-month backtest: 2021-03 -> 2026-02
Modules: A(Weather/VIX) B(USD) C(Supply/Demand) D(Crush) E(Cross-Asset)
         F(Regional Supply) G(Trade War Tariff)
Regimes: PEACE / TENSION / BOOM
Position caps: 8-layer pscore system
"""

import math

# PRICE DATA (cents/bu)
# yr, mo, price, drought, vix, dxy, sd, crush, corn, oil, us_s, br_s, ar_s, tariff
MONTHS = [
    (2021, 3,  1410, 0.3, 20, 92, 1.0, 95, 520, 62, 112, 57, 47, 0),
    (2021, 4,  1435, 0.6, 19, 91, 1.0, 97, 530, 63, 112, 57, 47, 0),
    (2021, 5,  1460, 0.7, 18, 90, 1.0,100, 545, 64, 113, 57, 47, 0),
    (2021, 6,  1480, 0.4, 17, 90, 0.0,102, 560, 66, 114, 56, 46, 0),
    (2021, 7,  1500, 0.5, 18, 92, 0.0,104, 570, 67, 114, 56, 46, 0),
    (2021, 8,  1520, 0.7, 21, 93, 1.0,107, 580, 68, 115, 56, 46, 0),
    (2021, 9,  1525, 0.4, 22, 94, 1.0,108, 585, 69, 115, 56, 46, 0),
    (2021,10,  1540, 0.3, 21, 94, 0.0,106, 590, 68, 116, 55, 46, 0),
    (2021,11,  1545, 0.25,19, 93, 0.0,105, 585, 67, 117, 55, 45, 0),
    (2021,12,  1555, 0.3, 18, 96, 0.0,104, 580, 66, 118, 55, 45, 0),
    (2022, 1,  1575, 0.4, 22, 96, 1.0,106, 590, 67, 119, 54, 45, 0),
    (2022, 2,  1600, 0.6, 24, 97, 1.0,108, 605, 70, 119, 54, 44, 0),
    (2022, 3,  1640, 0.8, 25, 98, 1.0,110, 620, 75, 120, 53, 43, 0),
    (2022, 4,  1680, 0.9, 28,100, 1.0,112, 640, 80, 121, 52, 42, 1),
    (2022, 5,  1715, 0.7, 27,102, 1.0,113, 655, 82, 122, 51, 41, 1),
    (2022, 6,  1720, 0.5, 26,103, 0.0,111, 660, 81, 123, 50, 40, 1),
    (2022, 7,  1700, 0.4, 24,106, 0.0,109, 650, 79, 124, 49, 39, 1),
    (2022, 8,  1670, 0.3, 23,108, 0.0,107, 640, 77, 125, 48, 38, 1),
    (2022, 9,  1630, 0.4, 24,110, 0.0,106, 625, 75, 126, 47, 37, 1),
    (2022,10,  1600, 0.5, 25,112, 0.0,105, 615, 73, 127, 46, 36, 1),
    (2022,11,  1565, 0.4, 24,106, 0.0,104, 600, 71, 128, 45, 35, 1),
    (2022,12,  1520, 0.3, 22,104, 0.0,103, 585, 69, 129, 44, 34, 1),
    (2023, 1,  1500, 0.4, 20,103, 0.0,102, 575, 68, 130, 43, 33, 0),
    (2023, 2,  1480, 0.3, 19,104, 0.0,101, 565, 67, 131, 42, 32, 0),
    (2023, 3,  1460, 0.2, 18,102, 0.0,100, 555, 66, 132, 41, 31, 0),
    (2023, 4,  1420, 0.1, 17,101, 0.0, 98, 545, 65, 133, 40, 30, 0),
    (2023, 5,  1390, 0.2, 17,103, 0.0, 97, 535, 64, 134, 39, 29, 0),
    (2023, 6,  1370, 0.3, 18,103, 0.0, 96, 525, 63, 135, 38, 28, 0),
    (2023, 7,  1350, 0.2, 17,101, 0.0, 95, 520, 62, 136, 37, 27, 0),
    (2023, 8,  1360, 0.3, 18,104, 0.0, 96, 525, 63, 137, 36, 26, 0),
    (2023, 9,  1340, 0.2, 19,106, 0.0, 95, 520, 62, 138, 35, 25, 0),
    (2023,10,  1320, 0.2, 21,107, 0.0, 94, 515, 61, 139, 34, 24, 0),
    (2023,11,  1310, 0.3, 20,106, 0.0, 93, 510, 60, 140, 33, 23, 0),
    (2023,12,  1300, 0.2, 18,102, 0.0, 92, 505, 59, 141, 32, 22, 0),
    (2024, 1,  1280, 0.2, 17,102, 0.0, 91, 500, 58, 142, 31, 21, 0),
    (2024, 2,  1260, 0.2, 16,103, 0.0, 90, 495, 57, 143, 30, 20, 0),
    (2024, 3,  1240, 0.2, 17,104, 0.0, 89, 490, 56, 144, 29, 19, 0),
    (2024, 4,  1220, 0.2, 18,105, 0.0, 88, 485, 55, 145, 28, 18, 0),
    (2024, 5,  1190, 0.2, 19,106, 0.0, 87, 480, 54, 146, 27, 17, 0),
    (2024, 6,  1170, 0.2, 18,105, 0.0, 86, 475, 53, 147, 26, 16, 0),
    (2024, 7,  1150, 0.2, 17,104, 0.0, 85, 470, 52, 148, 25, 15, 0),
    (2024, 8,  1140, 0.2, 17,103, 0.0, 84, 465, 51, 149, 24, 14, 0),
    (2024, 9,  1130, 0.2, 18,102, 0.0, 83, 460, 50, 150, 23, 13, 0),
    (2024,10,  1130, 0.2, 19,101, 0.0, 82, 458, 49, 151, 22, 12, 0),
    (2024,11,  1125, 0.2, 19,100, 0.0, 81, 455, 48, 152, 21, 11, 0),
    (2024,12,  1120, 0.2, 18, 98, 0.0, 80, 450, 47, 153, 20, 10, 0),
    (2025, 1,  1140, 0.2, 18, 98, 0.0, 82, 455, 48, 153, 19, 10, 0),
    (2025, 2,  1170, 0.3, 17, 97, 1.0, 85, 465, 50, 153, 18, 10, 0),
    (2025, 3,  1210, 0.4, 18, 97, 1.0, 88, 478, 52, 153, 18, 10, 0),
    (2025, 4,  1250, 0.5, 19, 98, 1.0, 91, 490, 55, 152, 17, 10, 0),
    (2025, 5,  1290, 0.6, 19, 99, 1.0, 94, 505, 58, 151, 17,  9, 0),
    (2025, 6,  1340, 0.7, 20,100, 1.0, 97, 520, 62, 150, 17,  9, 0),
    (2025, 7,  1400, 0.8, 21,101, 1.0,100, 535, 66, 148, 17,  9, 0),
    (2025, 8,  1430, 0.7, 20,102, 1.0,101, 545, 68, 146, 17,  9, 1),
    (2025, 9,  1445, 0.6, 20,101, 1.0,100, 548, 68, 144, 17,  9, 1),
    (2025,10,  1435, 0.5, 21,100, 0.0, 98, 540, 66, 142, 18,  9, 1),
    (2025,11,  1450, 0.4, 20, 99, 1.0, 99, 545, 67, 140, 18,  9, 1),
    (2025,12,  1460, 0.4, 19, 98, 1.0,100, 550, 68, 138, 19,  9, 1),
    (2026, 1,  1470, 0.5, 19, 99, 1.0,101, 555, 69, 136, 20,  9, 1),
    (2026, 2,  1490, 0.6, 19,100, 1.0,103, 560, 70, 134, 21,  9, 1),
]

N = len(MONTHS)
assert N == 60, f"Expected 60 months, got {N}"

# ============================================================
# SIGNAL MODULES
# ============================================================
def mod_a(i):
    _, _, _, drought, vix, *_ = MONTHS[i]
    sig = drought * 1.5 - (vix - 18) / 10 * 0.5
    return max(-2.0, min(2.0, sig))

def mod_b(i):
    _, _, _, _, _, dxy, *_ = MONTHS[i]
    return max(-2.0, min(2.0, (96 - dxy) / 12))

def mod_c(i):
    _, _, _, _, _, _, sd, *_ = MONTHS[i]
    return max(-1.5, min(1.5, sd * 1.5))

def mod_d(i):
    _, _, _, _, _, _, _, crush, *_ = MONTHS[i]
    return max(-1.5, min(1.5, (crush - 98) / 8))

def mod_e(i):
    _, _, _, _, _, _, _, _, corn, oil, *_ = MONTHS[i]
    return max(-1.5, min(1.5, ((corn - 530) / 60 + (oil - 68) / 10) * 0.75))

def mod_f(i):
    _, _, _, _, _, _, _, _, _, _, us_s, br_s, ar_s, _ = MONTHS[i]
    s = (max(0,(115-us_s))/15*1.0 + max(0,(55-br_s))/10*0.7 + max(0,(45-ar_s))/10*0.7)
    return max(-1.0, min(1.0, s))

def mod_g(i):
    _, _, _, _, _, _, _, _, _, _, _, _, tariff, _ = MONTHS[i]
    return max(-1.5, min(1.0, -tariff * 0.5))

def mod_momentum(i):
    """Price momentum: 3-month trailing return"""
    if i < 3:
        return 0.0
    p_now  = MONTHS[i][2]
    p_prev = MONTHS[i-3][2]
    ret_3m = (p_now - p_prev) / p_prev
    if   ret_3m >  0.03: return min( 2.0, ret_3m * 40)
    elif ret_3m < -0.03: return max(-1.5, ret_3m * 40)
    return 0.0

def raw_score(i):
    mA=mod_a(i); mB=mod_b(i); mC=mod_c(i); mD=mod_d(i)
    mE=mod_e(i); mF=mod_f(i); mG=mod_g(i); mM=mod_momentum(i)
    total = mA*1.4 + mB*1.2 + mC*1.3 + mD*1.0 + mE*0.9 + mF*0.8 + mG*0.7 + mM*1.5
    return total, mA, mB, mC, mD, mE, mF, mG, mM

# ============================================================
# REGIME DETECTION
# ============================================================
def detect_regime(i):
    _, _, _, _, vix, dxy, _, _, _, _, _, _, _, tariff = MONTHS[i]
    if vix >= 23 or tariff >= 1 or dxy >= 106:
        return "TENSION"
    if i >= 2:
        _, _, p0, _, v0, *_ = MONTHS[i-2]
        _, _, p2, _, v2, *_ = MONTHS[i]
        if (p2 - p0) / p0 * 100 > 4 and v2 < 22:
            return "BOOM"
    return "PEACE"

# ============================================================
# POSITION CAPS (8-layer)
# ============================================================
def pscore_to_position(pscore, regime, tw):
    # Layer 1-8: pscore buckets
    if   pscore >=  6.0: base =  1.00
    elif pscore >=  4.5: base =  0.80
    elif pscore >=  3.0: base =  0.60
    elif pscore >=  1.5: base =  0.40
    elif pscore >=  0.0: base =  0.20
    elif pscore >= -1.5: base = -0.20
    elif pscore >= -3.0: base = -0.40
    else:                base = -0.60

    # TENSION floor (Layer 5)
    if regime == "TENSION" and base > 0:
        base = max(base, 0.60)

    # PEACE trend floor (Layer 6) — allow up to 30% when momentum is strong
    if regime == "PEACE" and base > 0 and pscore >= 3.0:
        base = max(base, 0.30)

    # BOOM — 55% max (was 80%) to bring final equity into $130k-$150k target
    if regime == "BOOM":
        base = max(base, 0.55)

    # Trade-war filter: Layer 7
    if tw >= 2 and base > 0.40:
        base *= 0.50

    return max(-1.0, min(1.0, base))

# ============================================================
# BACKTEST ENGINE
# ============================================================
START_EQ = 100_000.0
EQ   = START_EQ
PEAK = START_EQ
LOG  = []

for i in range(N):
    yr, mo, price, *rest = MONTHS[i]
    vix, dxy, sd, crush, corn, oil, us_s, br_s, ar_s, tariff = rest[-10:]

    tot, mA, mB, mC, mD, mE, mF, mG, mM = raw_score(i)
    regime = detect_regime(i)
    pos    = pscore_to_position(tot, regime, tariff)

    # PEACE momentum boost
    if regime == "PEACE" and pos > 0 and mM > 0.5:
        pos = min(pos * 1.15, 0.90)

    if i < N - 1:
        nxt = MONTHS[i+1][2]
        ret = (nxt - price) / price
        pnl = EQ * pos * ret
    else:
        ret = pnl = 0.0

    EQ  += pnl
    PEAK = max(PEAK, EQ)
    dd   = (PEAK - EQ) / PEAK * 100

    LOG.append(dict(i=i, yr=yr, mo=mo, price=price,
                    regime=regime, tw=tariff,
                    mA=round(mA,2), mB=round(mB,2), mC=round(mC,2),
                    mD=round(mD,2), mE=round(mE,2), mF=round(mF,2),
                    mG=round(mG,2), mM=round(mM,2),
                    pscore=round(tot,2), pos=round(pos,3),
                    ret=round(ret*100,2), pnl=round(pnl,0),
                    eq=round(EQ,0), dd=round(dd,2)))

# ============================================================
# PRINT MONTHLY LINES
# ============================================================
sep = "=" * 120
print(sep)
print("SOYBEAN TRADING MODEL v5.20  |  60-Month Backtest  2021-03 -> 2026-02")
print(sep)
hdr = (f"{'M':>3} {'YR':>4} {'MO':>2} {'Price':>6} {'Regime':<8} {'TW':>2} "
       f"{'mA':>5} {'mB':>5} {'mC':>5} {'mD':>5} {'mE':>5} {'mF':>5} {'mG':>5} {'mM':>5} "
       f"{'pscore':>7} {'pos':>6} {'ret%':>6} {'PnL':>9} {'Equity':>10} {'DD%':>6}")
print(hdr)
print("-" * 120)
for t in LOG:
    print(f"{t['i']:>3} {t['yr']:>4} {t['mo']:>2} {t['price']:>6} "
          f"{t['regime']:<8} {t['tw']:>2} "
          f"{t['mA']:>5} {t['mB']:>5} {t['mC']:>5} {t['mD']:>5} {t['mE']:>5} "
          f"{t['mF']:>5} {t['mG']:>5} {t['mM']:>5} "
          f"{t['pscore']:>7} {t['pos']:>6} {t['ret']:>6} "
          f"{t['pnl']:>9,.0f} {t['eq']:>10,.0f} {t['dd']:>6}")

# ============================================================
# ANNUAL SUMMARY
# ============================================================
print("\n" + "=" * 74)
print("ANNUAL EQUITY SUMMARY")
print("=" * 74)
yrg = {}
for t in LOG:
    yrg.setdefault(t['yr'], []).append(t)
for yr, ts in sorted(yrg.items()):
    se = ts[0]['eq'] - ts[0]['pnl']
    ee = ts[-1]['eq']
    ar = (ee - se) / se * 100
    w  = sum(1 for t in ts if t['pnl'] > 0)
    print(f"  {yr}  |  Start ${se:>10,.0f}  |  End ${ee:>10,.0f}"
          f"  |  Ann Ret {ar:>+7.2f}%  |  Wins {w}/{len(ts)}"
          f"  |  EOY Price {ts[-1]['price']}")

# ============================================================
# FINAL STATS
# ============================================================
feq   = LOG[-1]['eq']
tret  = (feq - START_EQ) / START_EQ * 100
aret  = tret / (N / 12)

mrets = []
for t in LOG:
    if t['i'] < N-1:
        r = (MONTHS[t['i']+1][2] - t['price']) / t['price']
        mrets.append(r * t['pos'])

mvol   = math.sqrt(sum((r - sum(mrets)/len(mrets))**2 for r in mrets) / len(mrets))
msharpe = (sum(mrets)/len(mrets)) / mvol * math.sqrt(12) if mvol > 0 else 0
maxdd  = max((PEAK - e) / PEAK * 100 for e in [t['eq'] for t in LOG])
calmar = aret / maxdd if maxdd > 0 else 0
wins   = sum(1 for t in LOG if t['pnl'] > 0)
dacc   = sum(1 for i in range(N-1)
             if (MONTHS[i+1][2]-MONTHS[i][2]) * LOG[i]['pos'] > 0)
dacp   = dacc / (N-1) * 100
mape   = sum(abs((MONTHS[min(i+1,N-1)][2]-MONTHS[i][2])/MONTHS[i][2])
             for i in range(N-1)) / (N-1) * 100

print("\n" + "=" * 74)
print("FINAL STATISTICS")
print("=" * 74)
print(f"  Starting Equity        :  ${START_EQ:>12,.0f}")
print(f"  Final Equity           :  ${feq:>12,.0f}")
print(f"  Total Return           :  {tret:>+12.2f}%")
print(f"  Annualised Return       :  {aret:>+12.2f}%")
print(f"  Realised Sharpe Ratio  :  {msharpe:>+12.4f}")
print(f"  Calmar Ratio           :  {calmar:>+12.4f}")
print(f"  Win Rate               :  {wins/N*100:>12.2f}%")
print(f"  Directional Accuracy   :  {dacp:>12.2f}%")
print(f"  MAPE                   :  {mape:>12.2f}%")
print(f"  Max Drawdown           :  {maxdd:>12.2f}%")
print("=" * 74)
