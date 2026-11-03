#!/usr/bin/env python3
"""
Gold v8 — Full Macro-Integrated Model
8 modules: A(地缘) B(实际利率) C(通胀) D(供需) E(石油联动) F(BB均值回归) G(季节性) H(趋势)
Data: 2024-01 → 2026-03 (27 months)
"""
METAL=[
 ('2024-01',2022.,2060.,1985.,103.5,14.,False,860,74,85,4.60,55,185000,3.1,3.1,4780.,80,2.,5.25),
 ('2024-02',2030.,2055.,1995.,103.8,14.5,False,828,71,83,4.60,57,190000,3.2,3.1,4960.,78,2.,5.25),
 ('2024-03',2175.,2220.,2040.,104.5,14.,True,830,69,82,4.60,58,195000,3.5,3.1,5200.,76,2.,5.00),
 ('2024-04',2285.,2330.,2180.,106.,16.,False,833,65,81,4.60,60,198000,3.4,3.1,5100.,74,2.,5.00),
 ('2024-05',2345.,2420.,2280.,105.,16.5,False,835,63,79,4.00,62,205000,3.3,3.1,5280.,72,2.,5.00),
 ('2024-06',2335.,2450.,2280.,105.5,13.,True,837,60,80,4.00,65,210000,3.,3.,5460.,70,1.5,5.00),
 ('2024-07',2395.,2480.,2350.,104.2,14.5,False,840,55,78,3.50,68,215000,2.9,3.,5520.,68,1.5,5.00),
 ('2024-08',2505.,2530.,2370.,103.5,16.,False,850,52,76,3.50,70,220000,2.9,2.9,5640.,65,1.5,5.00),
 ('2024-09',2565.,2685.,2505.,101.,17.,True,858,48,74,3.50,72,228000,2.4,2.8,5760.,62,1.5,4.75),
 ('2024-10',2720.,2760.,2580.,104.,18.,False,868,44,72,3.90,75,232000,2.7,2.7,5700.,60,1.5,4.50),
 ('2024-11',2650.,2790.,2560.,106.,16.,False,875,40,78,3.90,74,235000,2.7,2.6,6030.,58,1.5,4.50),
 ('2024-12',2644.,2720.,2580.,108.,14.,False,880,37,82,3.90,73,238000,2.9,2.8,5880.,55,1.5,4.25),
 ('2025-01',2709.,2780.,2630.,107.5,14.,True,885,33,85,3.90,75,240000,3.,2.9,6050.,52,1.5,4.00),
 ('2025-02',2894.,2960.,2700.,106.5,16.,False,890,30,84,3.90,78,235000,2.8,2.9,5950.,50,1.5,4.00),
 ('2025-03',3120.,3150.,2950.,104.5,15.,True,896,27,83,3.40,80,230000,2.8,2.8,5650.,48,1.5,3.75),
 ('2025-04',3240.,3500.,3124.,103.,18.,False,905,22,88,3.40,83,225000,2.7,2.7,5400.,46,1.5,3.50),
 ('2025-05',3350.,3420.,3200.,105.,17.,False,912,20,92,3.40,85,220000,2.7,2.7,5800.,44,1.5,3.50),
 ('2025-06',3310.,3420.,3180.,104.,14.,True,918,18,96,3.50,84,222000,2.8,2.7,5920.,42,1.5,3.50),
 ('2025-07',3410.,3520.,3280.,104.5,15.,False,925,15,98,3.50,86,228000,2.9,2.8,5850.,40,1.5,3.50),
 ('2025-08',3530.,3680.,3380.,103.5,17.,False,935,13,101,3.50,88,232000,2.9,2.8,5650.,38,1.5,3.50),
 ('2025-09',3650.,3780.,3500.,102.,16.,True,945,11,96,3.60,89,235000,2.8,2.7,5760.,36,1.5,3.25),
 ('2025-10',3820.,3980.,3680.,104.,18.,False,958,10,88,3.60,91,240000,2.9,2.8,5850.,34,1.5,3.25),
 ('2025-11',4082.,4200.,3900.,106.,15.,False,970,12,78,3.50,93,245000,3.,2.9,6020.,32,1.5,3.25),
 ('2025-12',4289.,4400.,4100.,108.,14.,False,982,14,72,3.50,95,248000,3.,2.9,6050.,30,1.5,3.25),
 ('2026-01',4744.,5608.,4600.,107.,17.,True,995,18,65,3.50,97,250000,3.2,3.,6100.,28,1.5,3.25),
 ('2026-02',5277.,5420.,5000.,106.5,19.,False,1015,16,58,3.50,98,252000,3.4,3.1,5950.,26,1.5,3.25),
 ('2026-03',4872.,5100.,4600.,99.5,18.,True,1067,10,62,3.25,95,245000,3.6,3.2,5400.,5,.5,3.25),
]
CI=dict(CLOSE=1,HIGH=2,LOW=3,DXY=4,VIX=5,FOMC=6,GLD=7,CB=8,GS=9,FED=10,POLY=11,COT=12,CPI=13,CPI_EXP=14,SPX=15,HORMUZ=16,CME_CUTS=17,FED_DOT=18)
M=[
 (4.03,2.21,74.,-2100,3,38,6.2,3621,1050,0,0,0,-40,98,0.020,0.8,8.2,1),
 (4.22,2.31,76.,-1800,4,40,6.2,3621,1065,0,0,0,-45,95,0.018,0.9,15.4,2),
 (4.24,2.35,81.,-1600,8,42,6.4,3621,1080,1,1,5,-50,92,0.015,1.2,7.1,1),
 (4.55,2.42,84.,-1500,6,44,6.4,3632,1095,0,0,0,-55,88,0.022,1.5,-3.2,1),
 (4.50,2.37,78.,-1700,5,43,6.3,3632,1110,0,0,0,-50,95,0.030,0.8,22.6,3),
 (4.40,2.32,82.,-1500,7,41,6.3,3632,1120,0,0,0,-60,102,0.012,1.1,-12.1,1),
 (4.30,2.28,78.,-1400,5,42,6.3,3640,1130,0,0,0,-55,100,0.018,0.7,18.9,2),
 (4.18,2.24,76.,-1300,6,45,6.2,3640,1145,0,0,0,-48,97,0.025,0.6,2.3,1),
 (4.02,2.18,72.,-1100,4,44,6.2,3648,1160,0,0,0,-42,94,0.040,0.5,-21.7,1),
 (3.95,2.12,70.,-900,5,46,6.2,3648,1175,0,0,0,-38,91,0.035,0.4,16.2,2),
 (4.05,2.20,73.,-1000,4,47,6.2,3655,1190,0,0,0,-35,93,0.028,0.6,-8.5,1),
 (4.00,2.15,72.,-800,5,50,6.2,3655,1205,0,0,0,-30,96,0.020,0.8,25.1,1),
 (4.12,2.25,78.,-500,12,52,6.8,3655,1220,0,0,0,-25,105,0.015,1.2,11.3,1),
 (4.20,2.30,82.,-300,15,55,7.0,3660,1235,0,0,0,-20,110,0.022,1.8,8.7,1),
 (4.18,2.28,88.,-100,18,58,7.2,3660,1250,0,0,0,-15,108,0.018,2.1,14.2,1),
 (4.25,2.32,92.,100,22,60,7.5,3668,1265,0,0,0,-10,115,0.010,2.5,-6.3,1),
 (4.30,2.35,96.,200,25,62,7.8,3668,1280,0,0,0,-8,118,0.008,3.0,21.8,2),
 (4.28,2.33,94.,150,28,64,7.8,3672,1295,0,0,0,-5,116,0.012,2.8,-9.4,1),
 (4.22,2.30,90.,100,30,66,8.0,3672,1310,0,0,0,-3,120,0.016,2.4,17.5,1),
 (4.15,2.26,88.,50,33,68,8.2,3675,1325,0,0,0,-2,122,0.020,2.2,3.2,1),
 (4.10,2.24,85.,0,35,70,8.5,3675,1340,0,0,0,0,119,0.025,1.9,-13.6,1),
 (4.05,2.22,86.,50,40,72,8.8,3680,1355,0,0,0,2,124,0.030,1.6,28.4,3),
 (4.02,2.20,90.,100,45,74,9.2,3680,1370,0,0,0,3,126,0.028,2.0,19.1,2),
 (4.00,2.18,92.,150,47,76,9.5,3682,1385,0,0,0,5,128,0.022,2.3,7.8,1),
 (4.25,2.55,108.,200,65,88,10.2,3682,1400,2,1,15,10,135,0.005,3.5,35.2,5),
 (4.20,2.58,115.,250,79,96,10.5,3685,1415,3,2,35,15,142,0.002,4.0,48.7,8),
 (4.25,2.61,120.,300,92,120,10.8,3685,1430,4,3,65,20,150,0.001,4.5,-22.3,12),
]
CM=dict(NOM10Y=0,IE5Y=1,WTI=2,OIL_EXP=3,WAR_PCT=4,CDS=5,DEFICIT=6,GOLD_SUPPLY=7,AISC=8,WAR_TYPE=9,DXB_ATK=10,DXB_DMG=11,QT_RATE=12,MOVE=13,RES_GOLD_MOM=14,BASIS=15,BTC_20D=16,GLD_ACC=17)

def h_sco(h):
    if h >= 60: return 0
    if h >= 40: return int((60 - h) * 1.5)
    if h >= 20: return 20 + int((40 - h))
    return 40 + int((20 - h) * 2)

def war_score(w):
    if w < 10: return 0
    if w < 20: return 5
    if w < 40: return 10
    if w < 70: return 20
    return 30

def dxb_sc(dmg, atk):
    s = 0
    if dmg >= 60: s += 25
    elif dmg >= 40: s += 18
    elif dmg >= 20: s += 12
    if atk >= 2: s += 4
    return s

def detect_regime(hormuz, war_pct, cds, nom10y, ie5y, war_type, dxb_dmg):
    H = h_sco(hormuz); W = war_score(war_pct)
    cds_v = 35 if cds < 45 else 48 if cds < 60 else 60 if cds < 100 else 78 if cds < 120 else 88
    C = cds_v / 5.0; rr_v = nom10y - ie5y
    R = -10 if rr_v > 2.5 else (5 if rr_v < 0.5 else 0)
    D = dxb_sc(dxb_dmg, 0)
    wt_b = {0:0,1:10,2:20,3:35,4:55}[max(0,min(4,int(war_type)))]
    T = H + W + C + D + R + wt_b
    if T < 30: rg = "PEACE"
    elif T < 60: rg = "TENSION"
    else: rg = "WAR"
    return rg, T, rr_v

def mod_A(ho, wp, cds, wt, da, dd, rr):
    s = h_sco(ho) * 0.30 + war_score(wp) * 0.25
    cds_v = 35 if cds < 45 else 48 if cds < 60 else 60 if cds < 100 else 78 if cds < 120 else 88
    s += cds_v * 0.20
    wt_b = {0:0,1:10,2:20,3:35,4:55}[max(0,min(4,int(wt)))]
    s += wt_b * 0.15 + dxb_sc(dd, da) * 0.10
    return max(0.0, min(100.0, s))

def mod_B(nom, ie, dxy_z):
    rr_v = nom - ie
    r_s = 15 if rr_v >= 3 else 25 if rr_v >= 2.5 else 38 if rr_v >= 2 else 52 if rr_v >= 1.5 else 65 if rr_v >= 1 else 78 if rr_v >= 0.5 else 88 if rr_v >= 0 else 95
    d_s = 18 if dxy_z >= 2 else 32 if dxy_z >= 1 else 52 if abs(dxy_z) < 1 else 70 if dxy_z >= -2 else 85
    return 0.70 * r_s + 0.30 * d_s, rr_v

def mod_C(cpi, cpie, ie, nom, cb, cbp):
    surprise = cpi - cpie
    cpi_s = 36 if surprise < -0.3 else 50 if surprise < 0 else 62 if surprise < 0.3 else 76 if surprise < 0.8 else 90
    ie_s = 42 if ie < 2.3 else 52 if ie < 2.5 else 72 if ie < 2.7 else 82
    n_s = 78 if nom < 4 else 65 if nom < 4.5 else 55 if nom < 5 else 38 if nom < 5.5 else 20
    cb_g = (cb - cbp) / cbp * 100.0 if cbp else 0.0
    cb_s = 88 if cb_g >= 30 else 76 if cb_g >= 15 else 65 if cb_g >= 5 else 57 if cb_g >= 0 else 48 if cb_g >= -10 else 36
    return 0.40 * cpi_s + 0.20 * ie_s + 0.20 * n_s + 0.20 * cb_s

def mod_D(gold, aisc, gld_acc, cot, etf):
    p = gold / aisc
    p_s = 90 if p >= 4 else 80 if p >= 3.5 else 72 if p >= 3 else 62 if p >= 2.5 else 52 if p >= 2 else 42 if p >= 1.8 else 30
    etf_s = 70 if gld_acc > 0 else 35 if gld_acc < -10 else 55
    cot_s = min(100.0, max(0.0, 50.0 + cot / 5000.0))
    return 0.45 * p_s + 0.30 * etf_s + 0.25 * cot_s

def mod_E(wti, oe, rr, cds, df, ho, wp):
    wti_s = 90 if wti >= 120 else 80 if wti >= 100 else 72 if wti >= 90 else 62 if wti >= 80 else 52 if wti >= 70 else 42 if wti >= 60 else 30
    adj = -15 if oe > 200 else -5 if oe > 0 else 0 if oe > -1000 else 5
    geo = 20 if wp >= 70 and ho <= 30 else 12 if wp >= 40 else 8 if ho <= 30 else 0
    rr_adj = -20 if rr >= 2 else -12 if rr >= 1.5 else -5 if rr >= 1 else 0
    df_adj = -10 if df >= 10 else -5 if df >= 8 else 0 if df >= 7 else 3
    return max(0.0, min(100.0, wti_s + adj + geo + rr_adj + df_adj))

def mod_F(bb, rsi, vix):
    bb_s = 88 if bb <= 0.10 else 76 if bb <= 0.25 else 65 if bb <= 0.40 else 52 if bb <= 0.60 else 42 if bb <= 0.75 else 30 if bb <= 0.90 else 15
    rsi_s = 15 if rsi >= 80 else 30 if rsi >= 75 else 48 if rsi >= 65 else 60 if rsi >= 50 else 72 if rsi >= 35 else 88
    vix_s = 80 if vix >= 30 else 65 if vix >= 20 else 52 if vix >= 15 else 40
    return 0.40 * bb_s + 0.30 * rsi_s + 0.30 * vix_s

def mod_G(m):
    s = {1:75,2:60,3:55,4:55,5:58,6:50,7:45,8:50,9:70,10:85,11:65,12:75}[m]
    if m == 10: s = 85
    if m == 1: s = 80
    if m == 12: s = 75
    if m in (7,8): s = max(35, s - 15)
    return s

def mod_H(gold, ma5, ma10, mom3):
    ma_s = 85 if gold > ma5 > ma10 else 65 if gold > ma5 else 48 if gold > ma10 else 25
    mom_s = 85 if mom3 >= 0.15 else 72 if mom3 >= 0.08 else 58 if mom3 >= 0.03 else 52 if mom3 >= 0 else 38 if mom3 >= -0.05 else 20
    return 0.55 * ma_s + 0.45 * mom_s

def fuse(A, B, C, D, E, F, G, H, rg):
    if rg == "PEACE": return B*0.40 + C*0.25 + D*0.20 + E*0.08 + F*0.05 + G*0.02
    if rg == "TENSION": return B*0.25 + C*0.20 + D*0.20 + E*0.15 + F*0.08 + G*0.05 + H*0.07
    return E*0.45 + A*0.30 + B*0.10 + C*0.10 + F*0.03 + G*0.02

def pscore(s):
    if s >= 80: return 100,"FULL_LONG"
    if s >= 72: return 80,"LONG"
    if s >= 64: return 60,"LIGHT_LONG"
    if s >= 48: return 40,"BULLISH"
    if s >= 30: return 20,"SLIGHT"
    return 0,"NEUTRAL"

def rsi14(clses):
    n = len(clses)
    if n < 15: return 50.0
    g,l = [],[]
    for i in range(1,n):
        d = clses[i] - clses[i-1]
        g.append(max(d,0)); l.append(max(-d,0))
    ag=sum(g[-14:])/14.; al=sum(l[-14:])/14.
    return 100.-100./(1.+ag/al) if al!=0 else 100.

def bb_pos(closes, cur, p=20, n=2):
    n=len(closes)
    if n<p: return 0.5
    rec=closes[-p:]; sma=sum(rec)/p
    vari=sum((x-sma)**2 for x in rec)/p; std=vari**0.5
    lower=sma-n*std; upper=sma+n*std
    return max(0.,min(1.,(cur-lower)/(upper-lower))) if upper>lower else 0.5

def consec_up(i):
    c=0
    for j in range(i-1,max(0,i-4)-1,-1):
        if METAL[j+1][CI["CLOSE"]]>METAL[j][CI["CLOSE"]]: c+=1
        else: break
    return c

seq=[]; closes=[]
for i,(m,mp) in enumerate(zip(METAL,M)):
    g=m[CI["CLOSE"]]; closes.append(g)
    mnum=int(m[0].split("-")[1])
    ma5=sum(closes[-5:])/min(5,len(closes))
    ma10=sum(closes[-10:])/min(10,len(closes))
    mom3=(g-METAL[i-3][CI["CLOSE"]])/METAL[i-3][CI["CLOSE"]] if i>=3 else 0.
    rr_v=mp[CM["NOM10Y"]]-mp[CM["IE5Y"]]
    dxy_z=0. if i<20 else(g-METAL[i-20][CI["CLOSE"]])/(METAL[i-1][CI["CLOSE"]]-METAL[i-20][CI["CLOSE"]])*20 if METAL[i-1][CI["CLOSE"]]!=METAL[i-20][CI["CLOSE"]] else 0.
    rsi_v=rsi14(closes); bb_v=bb_pos(closes,g)
    cs=consec_up(i)
    rg,T,rr_v=detect_regime(m[CI["HORMUZ"]],mp[CM["WAR_PCT"]],mp[CM["CDS"]],mp[CM["NOM10Y"]],mp[CM["IE5Y"]],mp[CM["WAR_TYPE"]],mp[CM["DXB_DMG"]])
    A=mod_A(m[CI["HORMUZ"]],mp[CM["WAR_PCT"]],mp[CM["CDS"]],mp[CM["WAR_TYPE"]],int(mp[CM["DXB_ATK"]]),int(mp[CM["DXB_DMG"]]),rr_v)
    B,rr_v=mod_B(mp[CM["NOM10Y"]],mp[CM["IE5Y"]],dxy_z)
    C=mod_C(m[CI["CPI"]],m[CI["CPI_EXP"]],mp[CM["IE5Y"]],mp[CM["NOM10Y"]],m[CI["CB"]],METAL[i-1][CI["CB"]] if i>0 else m[CI["CB"]])
    D=mod_D(g,mp[CM["AISC"]],mp[CM["GLD_ACC"]],m[CI["COT"]],m[CI["GLD"]])
    E=mod_E(mp[CM["WTI"]],mp[CM["OIL_EXP"]],rr_v,mp[CM["CDS"]],mp[CM["DEFICIT"]],m[CI["HORMUZ"]],mp[CM["WAR_PCT"]])
    F=mod_F(bb_v,rsi_v,m[CI["VIX"]])
    G=mod_G(mnum)
    H=mod_H(g,ma5,ma10,mom3)
    total=fuse(A,B,C,D,E,F,G,H,rg)
    base,label=pscore(total)
    cap1=0.40 if rg=="WAR" and rsi_v>=80 else 0.50 if rg=="WAR" and rsi_v>=75 else 0.65 if rg=="WAR" and rsi_v>=70 else 0.60 if rsi_v>=80 else 0.70 if rsi_v>=75 else 0.85 if rsi_v>=70 else 1.0
    cap2=0.60 if rg=="WAR" and rr_v>=1.5 else 1.0
    cap3=0.60 if cs>=3 else 0.80 if cs>=2 else 1.0
    btc=mp[CM["BTC_20D"]]; gac=mp[CM["GLD_ACC"]]
    cap4=min(0.70 if btc>18 else 1.0, 0.80 if gac<0 and rsi_v>70 else 0.65 if gac<-20 else 1.0)
    cap5=0.55 if bb_v>0.90 else 0.70 if bb_v>0.80 else 0.85 if bb_v>0.70 else 1.0
    cap6=0.50 if mp[CM["DXB_DMG"]]>=60 else 0.70 if mp[CM["DXB_DMG"]]>=40 else 1.0
    cap7=0.80 if m[CI["FOMC"]] else 1.0
    pos=base*min(cap1,cap2,cap3,cap4,cap5,cap6,cap7)
    if rg=="PEACE" and rr_v<2.0: pos=max(pos,60)
    if rg=="TENSION" and rr_v<1.0: pos=max(pos,30)
    if rg=="WAR" and rr_v>=1.5: pos=0
    if rg=="TENSION" and rr_v>=2.0: pos=min(pos,20)
    pos=max(0,min(100,pos))
    seq.append({"date":m[0],"regime":rg,"A":round(A,1),"B":round(B,1),"C":round(C,1),"D":round(D,1),"E":round(E,1),"F":round(F,1),"G":round(G,1),"H":round(H,1),"total":round(total,1),"pos":pos,"label":label,"rr":round(rr_v,2),"rsi":round(rsi_v,1),"bb":round(bb_v,2),"fomc":m[CI["FOMC"]],"consec":cs,"ddmg":int(mp[CM["DXB_DMG"]])})

print("="*105)
print("  Gold v8 — Full Macro-Integrated | 8模块 | 石油联动 | 布林MR | 季节性 | 2024-01->2026-03 (27mo)")
print("="*105)
print("%-8s %-7s %4s %4s %4s %4s %4s %4s %4s %4s %5s %-8s %+8s %10s %3s  Notes"%("Month","Reg","A","B","C","D","E","F","G","H","Tot","Pos","Gold%","Equity","W/L"))
print("-"*105)
eq=100000.;peak=eq;dd_max=0.;wins=0;losses=0;mrets=[]
pd=[];ad=[]
for i,row in enumerate(seq):
    if i==0:
        print("%-8s %-7s %4s %4s %4s %4s %4s %4s %4s %4s %5s %-8s %8s %10s %3s"%("init","--","--","--","--","--","--","--","--","--","--","init","--","$100000","--"))
        continue
    mr=(METAL[i][CI["CLOSE"]]-METAL[i-1][CI["CLOSE"]])/METAL[i-1][CI["CLOSE"]]; ret=row["pos"]/100.*mr
    eq_new=eq*(1+ret); mrets.append(ret)
    if eq_new>peak: peak=eq_new
    dd=(eq_new-peak)/peak
    if dd<dd_max: dd_max=dd
    eq=eq_new; wl="W" if ret>=0 else "L"
    if ret>0: wins+=1
    else: losses+=1
    pd.append(1 if row["pos"]>0 else 0); ad.append(1 if mr>0 else 0)
    notes=[]
    if row["regime"]=="WAR" and row["rr"]>=1.5: notes.append("WAR_zero")
    elif row["regime"]=="TENSION" and row["rr"]>=2.0: notes.append("TEN_rrCap")
    if row["fomc"]: notes.append("FOMC")
    if row["consec"]>=2: notes.append("ConsecUp"+str(row["consec"]))
    if row["bb"]>0.80: notes.append("BBover")
    if row["ddmg"]>=40: notes.append("DXB"+str(row["ddmg"]))
    tag="|".join(notes) if notes else row["label"]
    print("%-8s %-7s %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %4.0f %5.1f %-8s %+8.2f%% $%9.0f %3s  %s"%(row["date"],row["regime"],row["A"],row["B"],row["C"],row["D"],row["E"],row["F"],row["G"],row["H"],row["total"],"%"+str(int(row["pos"])),mr*100,eq,wl,tag))

ann=((eq/100000)**(12./len(seq))-1)*100
vol=(sum((r-sum(mrets)/len(mrets))**2 for r in mrets)/len(mrets))**0.5
sharpe=(ann-5.)/(vol*(12.**0.5)) if vol>0 else 0
gret=(METAL[-1][CI["CLOSE"]]-METAL[0][CI["CLOSE"]])/METAL[0][CI["CLOSE"]]*100
n=len(seq)-1
dir_acc=sum(1 for p,a in zip(pd,ad) if p==a)/n if n>0 else 0
mape=sum(abs(mrets[i]) for i in range(n) if (pd[i]>0)!=(ad[i]>0))/n*100 if n>0 else 0.
print("-"*105)
print("Equity: $%.0f  Ann: %+.1f%%  Sharpe: %.2f  WinRate: %d/%d(%.0f%%)  DirAcc: %.1f%%  MAPE: %.2f%%  MaxDD: %.2f%%  BuyHold: +%.1f%%"%(eq,ann,sharpe,wins,wins+losses,wins/(wins+losses+0.001)*100,dir_acc*100,mape,dd_max*100,gret))
print("\nRegime summary:")
for rg in ["PEACE","TENSION","WAR"]:
    months=[r for r in seq if r["regime"]==rg]
    if not months: continue
    avg_pos=sum(r["pos"] for r in months)/len(months)
    wz=sum(1 for r in months if r["pos"]==0)
    print("  %s: %d months | avg_pos=%.0f%% | zero_position_months=%d"%(rg,len(months),avg_pos,wz))
print("\nWAR month detail:")
for r in seq:
    if r["regime"]=="WAR":
        idx=seq.index(r)
        gm=(METAL[idx][CI["CLOSE"]]-METAL[idx-1][CI["CLOSE"]])/METAL[idx-1][CI["CLOSE"]]*100
        rc=r["pos"]/100.*gm
        flag="ZERO_PROTECTED" if r["pos"]==0 else("LOSS" if rc<0 else "PROFIT")
        print("  %s  rr=%.2f%%  pos=%d%%  gold=%+.2f%%  ret=%+.2f%%  [%s]"%(r["date"],r["rr"],int(r["pos"]),gm,rc*100,flag))
