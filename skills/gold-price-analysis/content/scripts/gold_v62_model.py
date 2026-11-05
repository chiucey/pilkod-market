#!/usr/bin/env python3
"""
Gold Trading System v6.2 — Complete Clean Rewrite
Data: 2024-01 to 2026-03（27个月）
"""
import math

# ============================================================
# METAL 表 (19 fields per row: date + 18 METAL fields)
# CI: METAL[row][CI["field"]]
# ============================================================
METAL = [
    ("2024-01",2022.,2060.,1985.,103.5,14.0,False, 860,74,85, 4.60,55,185000, 3.1,3.1, 4780., 80,2.0,5.25),
    ("2024-02",2030.,2055.,1995.,103.8,14.5,False, 828,71,83, 4.60,57,190000, 3.2,3.1, 4960., 78,2.0,5.25),
    ("2024-03",2175.,2220.,2040.,104.5,14.0,True,  830,69,82, 4.60,58,195000, 3.5,3.1, 5200., 76,2.0,5.00),
    ("2024-04",2285.,2330.,2180.,106.0,16.0,False, 833,65,81, 4.60,60,198000, 3.4,3.1, 5100., 74,2.0,5.00),
    ("2024-05",2345.,2420.,2280.,105.0,16.5,False, 835,63,79, 4.00,62,205000, 3.3,3.1, 5280., 72,2.0,5.00),
    ("2024-06",2335.,2450.,2280.,105.5,13.0,True,  837,60,80, 4.00,65,210000, 3.0,3.0, 5460., 70,1.5,5.00),
    ("2024-07",2395.,2480.,2350.,104.2,14.5,False, 840,55,78, 3.50,68,215000, 2.9,3.0, 5520., 68,1.5,5.00),
    ("2024-08",2505.,2530.,2370.,103.5,16.0,False, 850,52,76, 3.50,70,220000, 2.9,2.9, 5640., 65,1.5,5.00),
    ("2024-09",2565.,2685.,2505.,101.0,17.0,True,  858,48,74, 3.50,72,228000, 2.4,2.8, 5760., 62,1.5,4.75),
    ("2024-10",2720.,2760.,2580.,104.0,18.0,False, 868,44,72, 3.90,75,232000, 2.7,2.7, 5700., 60,1.5,4.50),
    ("2024-11",2650.,2790.,2560.,106.0,16.0,False, 875,40,78, 3.90,74,235000, 2.7,2.6, 6030., 58,1.5,4.50),
    ("2024-12",2644.,2720.,2580.,108.0,14.0,False, 880,37,82, 3.90,73,238000, 2.9,2.8, 5880., 55,1.5,4.25),
    ("2025-01",2709.,2780.,2630.,107.5,14.0,True,  885,33,85, 3.90,75,240000, 3.0,2.9, 6050., 52,1.5,4.00),
    ("2025-02",2894.,2960.,2700.,106.5,16.0,False, 890,30,84, 3.90,78,235000, 2.8,2.9, 5950., 50,1.5,4.00),
    ("2025-03",3120.,3150.,2950.,104.5,15.0,True,  896,27,83, 3.40,80,230000, 2.8,2.8, 5650., 48,1.5,3.75),
    ("2025-04",3240.,3500.,3124.,103.0,18.0,False, 905,22,88, 3.40,83,225000, 2.7,2.7, 5400., 46,1.5,3.50),
    ("2025-05",3350.,3420.,3200.,105.0,17.0,False, 912,20,92, 3.40,85,220000, 2.7,2.7, 5800., 44,1.5,3.50),
    ("2025-06",3310.,3420.,3180.,104.0,14.0,True,  918,18,96, 3.50,84,222000, 2.8,2.7, 5920., 42,1.5,3.50),
    ("2025-07",3410.,3520.,3280.,104.5,15.0,False, 925,15,98, 3.50,86,228000, 2.9,2.8, 5850., 40,1.5,3.50),
    ("2025-08",3530.,3680.,3380.,103.5,17.0,False, 935,13,101,3.50,88,232000, 2.9,2.8, 5650., 38,1.5,3.50),
    ("2025-09",3650.,3780.,3500.,102.0,16.0,True,  945,11,96, 3.60,89,235000, 2.8,2.7, 5760., 36,1.5,3.25),
    ("2025-10",3820.,3980.,3680.,104.0,18.0,False, 958,10,88, 3.60,91,240000, 2.9,2.8, 5850., 34,1.5,3.25),
    ("2025-11",4082.,4200.,3900.,106.0,15.0,False, 970,12,78, 3.50,93,245000, 3.0,2.9, 6020., 32,1.5,3.25),
    ("2025-12",4289.,4400.,4100.,108.0,14.0,False, 982,14,72, 3.50,95,248000, 3.0,2.9, 6050., 30,1.5,3.25),
    ("2026-01",4744.,5608.,4600.,107.0,17.0,True,  995,18,65, 3.50,97,250000, 3.2,3.0, 6100., 28,1.5,3.25),
    ("2026-02",5277.,5420.,5000.,106.5,19.0,False,1015,16,58, 3.50,98,252000, 3.4,3.1, 5950., 26,1.5,3.25),
    ("2026-03",4872.,5100.,4600., 99.5,18.0,True, 1067,10,62, 3.25,95,245000, 3.6,3.2, 5400.,  5,0.5,3.25),
]
# METAL indices: 0=date, 1=close, 2=high, 3=low, 4=DXY, 5=VIX, 6=FOMC,
# 7=GLD_ETF, 8=CB_oz, 9=GS, 10=FED_RATE, 11=POLY, 12=COT, 13=CPI, 14=CPI_EXP,
# 15=SPX, 16=HORMUZ, 17=CME_CUTS, 18=FED_DOT
CI={"CLOSE":1,"HIGH":2,"LOW":3,"DXY":4,"VIX":5,"FOMC":6,
    "GLD":7,"CB":8,"GS":9,"FED":10,"POLY":11,"COT":12,
    "CPI":13,"CPI_EXP":14,"SPX":15,"HORMUZ":16,"CME_CUTS":17,"FED_DOT":18}

# ============================================================
# MACRO 表 (20 fields: dummy=0, date=1, 18 numeric fields)
# CM[col] = tuple index
# Tuple: (dummy, date, nom10Y, ie5Y, WTI, oil_exp, war_pct, CDS, deficit,
#         gold_supply, AISC, war_type, dxb_atk, dxb_dmg, QT_rate, MOVE,
#         res_gold_MoM, basis, BTC_20D, GLD_acc)
# ============================================================
MACRO = [
    (0,"2024-01",4.03,2.21,74.0,-2100, 3,38, 6.2,3621,1050, 0,0,0,  -40, 98, 0.020, 0.8, 8.2, 1),
    (0,"2024-02",4.22,2.31,76.0,-1800, 4,40, 6.2,3621,1065, 0,0,0,  -45, 95, 0.018, 0.9,15.4, 2),
    (0,"2024-03",4.24,2.35,81.0,-1600, 8,42, 6.4,3621,1080, 1,1,5,  -50, 92, 0.015, 1.2, 7.1, 1),
    (0,"2024-04",4.55,2.42,84.0,-1500, 6,44, 6.4,3632,1095, 0,0,0,  -55, 88, 0.022, 1.5,-3.2, 1),
    (0,"2024-05",4.50,2.37,78.0,-1700, 5,43, 6.3,3632,1110, 0,0,0,  -50, 95, 0.030, 0.8,22.6, 3),
    (0,"2024-06",4.40,2.32,82.0,-1500, 7,41, 6.3,3632,1120, 0,0,0,  -60,102, 0.012, 1.1,-12.1,1),
    (0,"2024-07",4.30,2.28,78.0,-1400, 5,42, 6.3,3640,1130, 0,0,0,  -55,100, 0.018, 0.7,18.9, 2),
    (0,"2024-08",4.18,2.24,76.0,-1300, 6,45, 6.2,3640,1145, 0,0,0,  -48, 97, 0.025, 0.6, 2.3, 1),
    (0,"2024-09",4.02,2.18,72.0,-1100, 4,44, 6.2,3648,1160, 0,0,0,  -42, 94, 0.040, 0.5,-21.7,1),
    (0,"2024-10",3.95,2.12,70.0, -900, 5,46, 6.2,3648,1175, 0,0,0,  -38, 91, 0.035, 0.4,16.2, 2),
    (0,"2024-11",4.05,2.20,73.0,-1000, 4,47, 6.2,3655,1190, 0,0,0,  -35, 93, 0.028, 0.6,-8.5, 1),
    (0,"2024-12",4.00,2.15,72.0, -800, 5,50, 6.2,3655,1205, 0,0,0,  -30, 96, 0.020, 0.8,25.1, 1),
    (0,"2025-01",4.12,2.25,78.0, -500,12,52, 6.8,3655,1220, 0,0,0,  -25,105, 0.015, 1.2,11.3, 1),
    (0,"2025-02",4.20,2.30,82.0, -300,15,55, 7.0,3660,1235, 0,0,0,  -20,110, 0.022, 1.8, 8.7, 1),
    (0,"2025-03",4.18,2.28,88.0, -100,18,58, 7.2,3660,1250, 0,0,0,  -15,108, 0.018, 2.1,14.2, 1),
    (0,"2025-04",4.25,2.32,92.0,  100,22,60, 7.5,3668,1265, 0,0,0,  -10,115, 0.010, 2.5,-6.3, 1),
    (0,"2025-05",4.30,2.35,96.0,  200,25,62, 7.8,3668,1280, 0,0,0,   -8,118, 0.008, 3.0,21.8, 2),
    (0,"2025-06",4.28,2.33,94.0,  150,28,64, 7.8,3672,1295, 0,0,0,   -5,116, 0.012, 2.8,-9.4, 1),
    (0,"2025-07",4.22,2.30,90.0,  100,30,66, 8.0,3672,1310, 0,0,0,   -3,120, 0.016, 2.4,17.5, 1),
    (0,"2025-08",4.15,2.26,88.0,   50,33,68, 8.2,3675,1325, 0,0,0,   -2,122, 0.020, 2.2, 3.2, 1),
    (0,"2025-09",4.10,2.24,85.0,    0,35,70, 8.5,3675,1340, 0,0,0,    0,119, 0.025, 1.9,-13.6,1),
    (0,"2025-10",4.05,2.22,86.0,   50,40,72, 8.8,3680,1355, 0,0,0,    2,124, 0.030, 1.6,28.4, 3),
    (0,"2025-11",4.02,2.20,90.0,  100,45,74, 9.2,3680,1370, 0,0,0,    3,126, 0.028, 2.0,19.1, 2),
    (0,"2025-12",4.00,2.18,92.0,  150,47,76, 9.5,3682,1385, 0,0,0,    5,128, 0.022, 2.3, 7.8, 1),
    (0,"2026-01",4.25,2.55,108.0, 200,65,88,10.2,3682,1400, 2,1,15,   10,135, 0.005, 3.5,35.2, 5),
    (0,"2026-02",4.20,2.58,115.0, 250,79,96,10.5,3685,1415, 3,2,35,   15,142, 0.002, 4.0,48.7, 8),
    (0,"2026-03",4.25,2.61,120.0, 300,92,120,10.8,3685,1430, 4,3,65,  20,150, 0.001, 4.5,-22.3,12),
]
# CM: MACRO[col] → 0=dummy, 1=date, 2=nom10Y, 3=ie5Y, 4=WTI, 5=oil_exp,
#     6=war_pct, 7=CDS, 8=deficit, 9=gold_supply, 10=AISC, 11=war_type,
#     12=dxb_atk, 13=dxb_dmg, 14=QT_rate, 15=MOVE, 16=res_gold_MoM,
#     17=basis, 18=BTC_20D, 19=GLD_acc
CM={"NOM10Y":2,"IE5Y":3,"WTI":4,"OIL_EXP":5,"WAR_PCT":6,"CDS":7,
    "DEFICIT":8,"GOLD_SUPPLY":9,"AISC":10,
    "WAR_TYPE":11,"DXB_ATK":12,"DXB_DMG":13,
    "QT_RATE":14,"MOVE":15,"RES_GOLD_MOM":16,"BASIS":17,
    "BTC_20D":18,"GLD_ACC":19}

# ============================================================
# 评分函数
# ============================================================
def rr_sig(r):
    if r>=3.0: return 15
    if r>=2.5: return 25
    if r>=2.0: return 38
    if r>=1.5: return 52
    if r>=1.0: return 65
    if r>=0.5: return 78
    if r>=0.0: return 88
    return 95

def dxy_z_sig(z):
    if z>=2.0: return 18
    if z>=1.0: return 32
    if abs(z)<1.0: return 52
    if z>=-2.0: return 70
    return 85

def qt_sig(q):
    if q<-80: return 20
    if q<-40: return 38
    if q<0:   return 55
    return 88

def curve_sig(sp):
    if sp>2: return 16
    if sp>0: return 10
    return 0

def cds_mid(c):
    if c<45: return 35
    if c<60: return 48
    if c<100: return 60
    if c<120: return 78
    return 88

def cpi_sup(s):
    if s<-0.3: return 36
    if s<0.0:  return 50
    if s<0.3:  return 62
    if s<0.8:  return 76
    return 90

def ie_s(e):
    if e<2.3: return 42
    if e<2.5: return 52
    if e<2.7: return 72
    return 82

def nominal_s(n):
    if n<4.0: return 78
    if n<4.5: return 65
    if n<5.0: return 55
    if n<5.5: return 38
    return 20

def move_s(m):
    if m>120: return 12
    if m>90:  return 6
    return 0

def premium_s(p):
    if p>=4.0: return 90
    if p>=3.5: return 80
    if p>=3.0: return 72
    if p>=2.5: return 62
    if p>=2.0: return 52
    if p>=1.8: return 42
    return 30

def cb_growth_s(g):
    if g>=30: return 88
    if g>=15: return 76
    if g>=5:  return 65
    if g>=0:  return 57
    if g>=-10: return 48
    return 36

def res_s(r):
    if r>0.15: return 82
    if r>0.05: return 68
    if r>=0.0: return 54
    return 36

def basis_s(b):
    if b>3.5: return 18
    if b>=1.5: return 10
    return 0

def rr_mod_er(rr):
    if rr>2.5: return -10
    if rr<0.5: return 5
    return 0

def h_sco(h):
    if h>=60: return 0
    if h>=40: return int((60-h)*1.5)
    if h>=20: return 20+int((40-h))
    return 40+int((20-h)*2)

def war_sco(w):
    if w<10: return 0
    if w<20: return 5
    if w<40: return 10
    if w<70: return 20
    return 30

def dxb_sco(d):
    if d>=50: return 20
    if d>=20: return 10
    return 0

# ============================================================
# MODULE A: 情景检测
# ============================================================
def mod_regime(m, mp):
    h   = m[CI["HORMUZ"]]
    w   = mp[CM["WAR_PCT"]]
    cds = mp[CM["CDS"]]
    rr_v= mp[CM["NOM10Y"]] - mp[CM["IE5Y"]]
    dmg = mp[CM["DXB_DMG"]]
    wt  = int(mp[CM["WAR_TYPE"]])

    H = h_sco(h)
    W = war_sco(w)
    C = cds_mid(cds)/5
    R = rr_mod_er(rr_v)
    D = dxb_sco(dmg)
    T_bonus = {0:0,1:10,2:20,3:35,4:55}[max(0,min(4,wt))]
    T = H+W+C+T_bonus+D+R

    sP = -T+20; sT = 30-abs(T-45); sW = T-50
    es = math.exp(sP)+math.exp(sT)+math.exp(sW)
    pP = math.exp(sP)/es; pT = math.exp(sT)/es; pW = math.exp(sW)/es

    if T<30: regime="PEACE"
    elif T<60: regime="TENSION"
    else: regime="WAR"
    return {"regime":regime,"T":T,"pP":pP,"pT":pT,"pW":pW,"rr":rr_v,
            "rdesc":f"{regime}({int(pP*100)}|{int(pT*100)}|{int(pW*100)})"}

# ============================================================
# MODULE B: 短期因子（实际利率+DXY+QT+远期曲线）
# ============================================================
def mod_b(nom, ie, dxy_z, qt, basis):
    rr_v = nom-ie
    B = 0.6*(0.7*rr_sig(rr_v)+0.3*dxy_z_sig(dxy_z)) \
        + 0.2*qt_sig(qt) + 0.2*curve_sig(basis)
    return B

# ============================================================
# MODULE C: 中期因子（CDS+CPI+MOVE）
# ============================================================
def mod_c(cds, cpi, cpi_exp, ie, nom, move):
    sup = cpi-cpi_exp
    C = 0.85*(0.4*cds_mid(cds)+0.35*cpi_sup(sup)+0.15*ie_s(ie)+0.1*nominal_s(nom)) \
        + 0.15*move_s(move)
    return C

# ============================================================
# MODULE D: 长期因子（成本溢价+央行+外储）
# ============================================================
def mod_d(gold, aisc, cb_oz, cb_prev, res_mom):
    prem = gold/aisc
    cb_g = (cb_oz-cb_prev)/cb_prev*100 if cb_prev else 0
    D = 0.8*(0.35*premium_s(prem)+0.35*premium_s(prem)+0.3*cb_growth_s(cb_g)) \
        + 0.2*res_s(res_mom)
    return D

# ============================================================
# MODULE E: 战争溢价（基差+事件衰减）
# ============================================================
def mod_e(wpct, hormuz, cds, deficit, oil_exp, rr_v,
          dxb_atk, dxb_dmg, wt, basis, dur=0):
    if wt==0: return 0.0
    E=65.0
    if cds>=120: E+=30
    elif cds>=80: E+=22
    elif cds>=60: E+=14
    else: E+=6
    if deficit>=10: E-=20
    elif deficit>=8: E-=10
    elif deficit>=7: E-=3
    E += min(15, max(0, oil_exp/200))
    if rr_v>=2.0: E-=25
    elif rr_v>=1.5: E-=15
    elif rr_v>=1.0: E-=5
    elif rr_v>=0.5: E+=5
    else: E+=12
    if dxb_dmg>=20: E+=20
    elif dxb_atk>=2: E+=10
    else: E+=5
    if dxb_dmg>=60: E+=25
    elif dxb_dmg>=40: E+=18
    elif dxb_dmg>=20: E+=12
    elif dxb_atk>=2: E+=4
    decay = math.exp(-0.08*dur) if dur else 1.0
    return max(5, min(100, 0.9*E*decay + 0.1*basis_s(basis)))

# ============================================================
# 融合函数
# ============================================================
def fuse(B, C, D, E, pP, pT, pW):
    S_P = B*0.40+C*0.30+D*0.20+E*0.10
    S_T = B*0.25+C*0.30+D*0.25+E*0.20
    S_W = B*0.10+C*0.15+D*0.20+E*0.55
    prob = pP*S_P + pT*S_T + pW*S_W
    mx   = max(S_P, S_T, S_W)
    return max(0, min(100, 0.7*prob + 0.3*mx))

def pscore(s):
    if s>=80: return 100,"FULL_LONG"
    if s>=72: return 80,"LONG"
    if s>=64: return 60,"LIGHT_LONG"
    if s>=48: return 40,"BULLISH"
    if s>=30: return 20,"SLIGHT"
    return 0,"NEUTRAL"

def vix_rsi(vix):
    """VIX→RSI proxy (月度数据用VIX判断超买超卖)"""
    if vix<=12: return 55
    if vix<=15: return 50
    if vix<=20: return 45
    if vix<=25: return 40
    if vix<=30: return 35
    return 30

# ============================================================
# 六层仓位上限
# ============================================================
def apply_caps(pos, regime, pW, rr_v, vix, consec2,
               btc_crowd, gld_cap_v, pnl, pW_chg,
               dxb_dmg, wt):
    cap = 1.0
    rsi = vix_rsi(vix)

    # Layer 1: RSI-proxy过滤
    if rsi>=55:
        cap = min(cap, 0.45 if pW>=0.5 else 0.60)
    elif rsi>=50:
        cap = min(cap, 0.55 if pW>=0.5 else 0.70)

    # Layer 2: rr_veto
    if pW>=0.5 and rr_v>=1.5: cap=min(cap, 0.60)
    elif pW>=0.5 and rr_v>=1.0: cap=min(cap, 0.80)

    # Layer 3: 动量过热
    if consec2: cap=min(cap, 0.80)

    # Layer 4: 波动率
    if vix>25: cap=min(cap, 0.85)

    # Layer 5: BTC+GLD拥挤度上限
    cap = min(cap, min(btc_crowd, gld_cap_v))

    # Layer 6: 动态止盈止损
    if pnl>=0.10 and vix>=18: cap=min(cap, 0.50)
    elif pnl>=0.15: cap=0.0
    elif pnl<=-0.03 and pW_chg>=0.1: cap=min(cap, 0.50)
    elif pnl<=-0.05: cap=0.0

    pos = pos*cap

    # PEACE底仓
    if regime=="PEACE" and rr_v<2.0: pos=max(pos, 60)
    return pos

# ============================================================
# 主回测
# ============================================================
def runbt():
    seq=[]; closes=[]
    for i,m in enumerate(METAL):
        mp=MACRO[i]
        gclose=m[CI["CLOSE"]]; dxy_raw=m[CI["DXY"]]; fomc=m[CI["FOMC"]]
        cb_oz=m[CI["CB"]]; cpi=m[CI["CPI"]]; cpi_exp=m[CI["CPI_EXP"]]; vix=m[CI["VIX"]]
        hormuz=m[CI["HORMUZ"]]
        nom10y=mp[CM["NOM10Y"]]; ie5y=mp[CM["IE5Y"]]; cds=mp[CM["CDS"]]
        deficit=mp[CM["DEFICIT"]]; aisc=mp[CM["AISC"]]
        wt=int(mp[CM["WAR_TYPE"]]); dxb_atk=int(mp[CM["DXB_ATK"]])
        dxb_dmg=mp[CM["DXB_DMG"]]; qt=mp[CM["QT_RATE"]]; move=mp[CM["MOVE"]]
        res_mom=mp[CM["RES_GOLD_MOM"]]; basis=mp[CM["BASIS"]]
        btc_20d=mp[CM["BTC_20D"]]; gld_acc=mp[CM["GLD_ACC"]]
        oil_exp=mp[CM["OIL_EXP"]]

        closes.append(gclose)

        # DXY Z-score
        if i<20: dxy_z=0.0
        else:
            mn=sum(METAL[j][CI["DXY"]] for j in range(i-20,i))/20
            sd=(sum((METAL[j][CI["DXY"]]-mn)**2 for j in range(i-20,i))/20)**0.5
            dxy_z=(dxy_raw-mn)/(sd or 1)

        # 战争持续时间
        dur=0
        if wt>0 and i>0:
            for j in range(i-1,-1,-1):
                if int(MACRO[j][CM["WAR_TYPE"]])>0: dur+=1
                else: break

        info=mod_regime(m,mp)
        regime=info["regime"]; pP=info["pP"]; pT=info["pT"]; pW=info["pW"]; rr_v=info["rr"]

        B=mod_b(nom10y,ie5y,dxy_z,qt,basis)
        C=mod_c(cds,cpi,cpi_exp,ie5y,nom10y,move)
        cb_prev=METAL[i-1][CI["CB"]] if i>0 else cb_oz
        D=mod_d(gclose,aisc,cb_oz,cb_prev,res_mom)
        E=mod_e(wpct=mp[CM["WAR_PCT"]],hormuz=hormuz,cds=cds,deficit=deficit,
                oil_exp=oil_exp,rr_v=rr_v,dxb_atk=dxb_atk,dxb_dmg=dxb_dmg,
                wt=wt,basis=basis,dur=dur)

        total=fuse(B,C,D,E,pP,pT,pW)

        btc_crowd=0.70 if btc_20d>18 else 1.0
        gld_cap_v=0.70 if (gld_acc<0 and vix<15) else 1.0

        pos,lbl=pscore(total)

        mr1=(METAL[i-1][CI["CLOSE"]]-METAL[i-2][CI["CLOSE"]])/METAL[i-2][CI["CLOSE"]] if i>=2 else 0
        mr0=(gclose-METAL[i-1][CI["CLOSE"]])/METAL[i-1][CI["CLOSE"]] if i>0 else 0
        consec2=(i>=2 and mr1>0.07 and mr0>0.07)

        pW_chg=0.0
        if i>0:
            pi=mod_regime(METAL[i-1],MACRO[i-1])
            pW_chg=abs(pW-pi["pW"])

        pnl=0.0
        if i>=2 and len(seq)>0:
            pnl=seq[-1]["pos"]/100.0*mr1

        pos=apply_caps(pos,regime,pW,rr_v,vix,consec2,btc_crowd,gld_cap_v,pnl,pW_chg,dxb_dmg,wt)
        if fomc: pos=pos*0.80
        pos=max(0,min(100,int(pos)))
        if pos>0 and rr_v>3.0: pos=0

        seq.append({"date":m[0],"regime":regime,"B":round(B,1),"C":round(C,1),
                    "D":round(D,1),"E":round(E,1),"total":round(total,1),
                    "pos":pos,"label":lbl,"rr":round(rr_v,2),"vix":vix,
                    "pP":round(pP,2),"pW":round(pW,2),
                    "BTC":btc_crowd,"GLD":gld_cap_v,
                    "crisis":(dxb_dmg>=20 or wt>=2),
                    "wt":wt,"dxb_atk":dxb_atk,"dxb_dmg":dxb_dmg})
    return seq

def print_results(seq):
    print("="*92)
    print("  Gold v6.2 — Probability Regime + New Factors | 2024-01 → 2026-03（27个月）")
    print("  新增: QT_rate | MOVE指数 | 外储黄金占比 | COMEX/London基差 | BTC拥挤度 | GLD加速度 | 六层风控+概率融合")
    print("="*92)
    hdr=f"{'Month':10s} {'Regime':24s} {'B':5s} {'C':5s} {'D':5s} {'E':5s} {'Tot':5s} {'Pos':8s} {'Equity':>10s} {'W/L':3s} Key"
    print(hdr); print("-"*92)
    eq=100000.0; peak=eq; dd_max=0.0; wins=losses=0; mrets=[]
    for i,row in enumerate(seq):
        if i==0:
            print(f"{row['date']:10s} {row['regime']:24s} {'init':>5s} {'--':>5s} {'--':>5s} {'--':>5s} {'--':>5s} {'init':>8s} {'$100000':>10s} {'--':3s}")
            continue
        mr=(METAL[i][CI["CLOSE"]]-METAL[i-1][CI["CLOSE"]])/METAL[i-1][CI["CLOSE"]]
        ret=row["pos"]/100.0*mr
        eq_new=eq*(1+ret); mrets.append(ret)
        if eq_new>peak: peak=eq_new
        dd=(eq_new-peak)/peak
        if dd<dd_max: dd_max=dd
        eq=eq_new; wl="W" if mr>0 else "L"
        if mr>0: wins+=1
        else: losses+=1
        keys=[]
        if row["crisis"]:
            keys.append({2:"OIL_WAR",3:"MAJOR_WAR",4:"US_HOMELAND"}.get(row["wt"],"CRISIS"))
        if row["BTC"]<1.0: keys.append("BTC_cap")
        if row["GLD"]<1.0: keys.append("GLD_cap")
        if row["pW"]>=0.5 and row["rr"]>=1.5: keys.append(f"rrVeto({row['rr']})")
        if row["pP"]>=0.5 and row["rr"]<2.0: keys.append("PEACE_floor")
        tag="|".join(keys) if keys else row["label"]
        lbl=f"{row['label']}_{row['pos']}%"
        print(f"{row['date']:10s} {row['regime']:24s} {row['B']:5.1f} {row['C']:5.1f} {row['D']:5.1f} {row['E']:5.1f} {row['total']:5.1f} {lbl:17s} {'$':>1s}{eq:>9.0f} {wl:3s} {tag}")
    ann_ret=((eq/100000)**(12/len(seq))-1)*100
    vol=(sum((r-sum(mrets)/len(mrets))**2 for r in mrets)/len(mrets))**0.5
    sharpe=(ann_ret-5.0)/(vol*(12**0.5)) if vol>0 else 0
    gret=(METAL[-1][CI["CLOSE"]]-METAL[0][CI["CLOSE"]])/METAL[0][CI["CLOSE"]]*100
    print("-"*92)
    print(f"\n  Equity: ${eq:,.0f}  |  Ann.Ret: {ann_ret:+.1f}%  |  Sharpe: {sharpe:.2f}")
    print(f"  Win Rate: {wins}/{wins+losses} ({wins/(wins+losses)*100:.0f}%)")
    print(f"  MaxDD: {dd_max*100:.2f}%  |  BuyHold: +{gret:.1f}%")

    # 2026-03 分析
    r26=seq[-1]; mp26=MACRO[-1]
    print(f"\n  2026-03: regime={r26['regime']} pW={r26['pW']:.0%} rr={r26['rr']}% pos={r26['pos']}% label={r26['label']}")
    print(f"  MOVE={mp26[CM['MOVE']]} BTC={mp26[CM['BTC_20D']]}% basis={mp26[CM['BASIS']]} rr_veto:{'✅' if r26['pW']>=0.5 and r26['rr']>=1.5 else '❌'}")

    # 因子表
    print(f"\n{'Month':10s} {'MOVE':6s} {'QT':6s} {'Basis':7s} {'BTC_20D':8s} {'BTC_cap':7s} {'GLD_acc':8s} {'GLD_cap':7s} {'Pos':5s} {'Key'}")
    print("-"*92)
    for i,row in enumerate(seq):
        if i==0: continue
        mp=MACRO[i]
        mv=mp[CM["MOVE"]]; qt=mp[CM["QT_RATE"]]; bs=mp[CM["BASIS"]]
        btc=mp[CM["BTC_20D"]]; gld=mp[CM["GLD_ACC"]]
        keys2=[]
        if row["BTC"]<1.0: keys2.append("BTC")
        if row["GLD"]<1.0: keys2.append("GLD")
        tag2="|".join(keys2) if keys2 else "-"
        print(f"{row['date']:10s} {mv:6.0f} {qt:6.0f} {bs:7.1f} {btc:8.1f} {row['BTC']:7.2f} {gld:8.1f} {row['GLD']:7.2f} {row['pos']:5d}% {tag2}")
    return eq,ann_ret,sharpe,dd_max,wins,losses

if __name__=="__main__":
    seq=runbt(); print_results(seq)
