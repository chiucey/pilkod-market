#!/usr/bin/env python3
"""
Gold v5 - Macro Structural Model with Regime-Aware Signal Fusion
Modules: A(Regime) + B(RealRate) + C(US CDS+Inflation) + D(SupplyCost) + E(WarPremium)
"""
import math, random

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
CI={"CLOSE":1,"HIGH":2,"LOW":3,"DXY":4,"VIX":5,"FOMC":6,
     "GLD":7,"CB":8,"GS":9,"FED":10,"POLY":11,"COT":12,
     "CPI":13,"CPI_EXP":14,"SPX":15,"HORMUZ":16,"CME_CUTS":17,"FED_DOT":18}
# month, nom10Y%, ie5Y%, WTI, oil_net_exp_kbd, war%, cds, deficit%_GDP, gold_supply_kt, aisc
MACRO = [
    ("2024-01",4.03,2.21,74.0,-2100, 3,38,6.2,3621,1050),
    ("2024-02",4.22,2.31,76.0,-1800, 4,40,6.2,3621,1065),
    ("2024-03",4.24,2.35,81.0,-1600, 8,42,6.4,3621,1080),
    ("2024-04",4.55,2.42,84.0,-1500, 6,44,6.4,3632,1095),
    ("2024-05",4.50,2.37,78.0,-1700, 5,43,6.3,3632,1110),
    ("2024-06",4.40,2.32,82.0,-1500, 7,41,6.3,3632,1120),
    ("2024-07",4.25,2.28,80.0,-1400, 9,39,6.2,3638,1130),
    ("2024-08",3.91,2.23,74.0,-1300,11,37,6.1,3638,1145),
    ("2024-09",3.78,2.17,70.0,-1200,15,36,6.1,3638,1155),
    ("2024-10",4.28,2.28,71.0,-1100,12,38,6.2,3645,1165),
    ("2024-11",4.39,2.32,72.0,-1000,10,40,6.2,3645,1175),
    ("2024-12",4.25,2.34,74.0,-1000, 9,42,6.3,3645,1185),
    ("2025-01",4.62,2.41,76.0,-900,  8,44,6.4,3650,1195),
    ("2025-02",4.36,2.44,73.0,-800,  7,43,6.3,3650,1205),
    ("2025-03",4.21,2.45,72.0,-800, 10,45,6.4,3650,1215),
    ("2025-04",4.38,2.51,75.0,-700, 12,48,6.5,3655,1225),
    ("2025-05",4.42,2.56,76.0,-700, 11,50,6.5,3655,1235),
    ("2025-06",4.30,2.54,74.0,-650, 14,52,6.5,3660,1245),
    ("2025-07",4.15,2.55,73.0,-600, 16,54,6.6,3660,1252),
    ("2025-08",3.88,2.57,70.0,-550, 18,55,6.6,3662,1259),
    ("2025-09",3.78,2.59,68.0,-500, 22,58,6.7,3662,1266),
    ("2025-10",4.28,2.64,72.0,-480, 20,60,6.7,3665,1273),
    ("2025-11",4.40,2.68,74.0,-460, 18,62,6.8,3665,1280),
    ("2025-12",4.14,2.70,73.0,-450, 17,64,6.8,3668,1287),
    ("2026-01",4.21,2.73,78.0,-420, 25,68,7.0,3668,1294),
    ("2026-02",4.13,2.81,82.0,-400, 45,85,7.5,3670,1301),
    # Mar 2026: Iran war. RealRate = 4.25 - 2.61 = +1.64% (still positive = gold pressure)
    # US CDS: 38 -> 145 bps. WTI: 82 -> 88 (Hormuz blockade)
    ("2026-03",4.25,2.61,88.0,-380, 92,145,10.5,3670,1308),
]
CM={"NOM10Y":1,"IE5Y":2,"WTI":3,"OIL_EXP":4,"WAR":5,"CDS":6,"DEF":7,"GLDSUP":8,"AISC":9}

def ema_(d,p):
    if len(d)<p:return None
    k=2/(p+1);e=d[0]
    for v in d[1:]:e=v*k+e*(1-k)
    return e

def rsi_(p,p_=14):
    if len(p)<p_+1:return 50.
    g,l=[],[]
    for i in range(1,len(p)):
        d=p[i]-p[i-1];g.append(max(d,0));l.append(max(-d,0))
    ag=sum(g[-p_:])/p_;al=sum(l[-p_:])/p_
    return 100. if al==0 else 100-100/(1+ag/max(al,1e-9))

def zscore(d,p=20):
    if len(d)<p:return None
    r=d[-p:];m=sum(r)/p;v=sum((x-m)**2 for x in r)/p
    return (d[-1]-m)/math.sqrt(v) if math.sqrt(v)>0 else None

def mod_regime(hormuz,war,cds,nom10y,ie5y):
    t=0;ev=[]
    if hormuz>=60:h=0
    elif hormuz>=40:h=int((60-hormuz)*1.5)
    elif hormuz>=20:h=20+int((40-hormuz))
    else:h=40+int((20-hormuz))*2
    t+=h
    if hormuz<40:ev.append("BLOCK" if hormuz<20 else "CRISIS")
    if war>=70:w=30
    elif war>=40:w=20
    elif war>=20:w=10
    elif war>=10:w=5
    else:w=0
    t+=w
    if war>=20:ev.append("W"+str(war))
    if cds>=100:c=20
    elif cds>=60:c=12
    elif cds>=45:c=6
    else:c=0
    t+=c
    if cds>=60:ev.append("CDS"+str(cds))
    rr=nom10y-ie5y
    if rr>2.5:t-=10
    elif rr<0.5:t+=5
    t=max(0,min(100,t))
    rname="PEACE" if t<30 else("TENSION" if t<60 else "WAR")
    return rname,t,rname+"("+str(t)+")"+"".join(["|"+e for e in ev])

def mod_real_rate(nom10y,ie5y,dxy_z):
    rr=nom10y-ie5y
    if   rr>=3.0:rs=15
    elif rr>=2.5:rs=25
    elif rr>=2.0:rs=38
    elif rr>=1.5:rs=52
    elif rr>=1.0:rs=65
    elif rr>=0.5:rs=78
    elif rr>=0.0:rs=88
    else:rs=95
    if dxy_z is None:dxy_z=0
    if   dxy_z>=2.0:ds=18
    elif dxy_z>=1.0:ds=32
    elif dxy_z>=-1.0:ds=52
    elif dxy_z>=-2.0:ds=70
    else:ds=85
    return max(0,min(100,rs*0.70+ds*0.30)),"rr="+("%0.2f" % rr)

def mod_credit(cds,cpi,cpi_exp,ie5y,nom10y):
    if   cds>=120:cs=88
    elif cds>=100:cs=78
    elif cds>=60:cs=60
    elif cds>=45:cs=48
    else:cs=35
    surprise=cpi-cpi_exp
    if   surprise>=0.8:cs2=90
    elif surprise>=0.3:cs2=76
    elif surprise>=0.0:cs2=62
    elif surprise>=-0.3:cs2=50
    else:cs2=36
    if   ie5y>=3.0:ie=82
    elif ie5y>=2.7:ie=72
    elif ie5y>=2.5:ie=60
    elif ie5y>=2.3:ie=52
    else:ie=42
    if   nom10y>=5.5:ny=20
    elif nom10y>=5.0:ny=38
    elif nom10y>=4.5:ny=55
    elif nom10y>=4.0:ny=65
    else:ny=78
    return max(0,min(100,cs*0.40+cs2*0.35+ie*0.15+ny*0.10)),"CDS="+str(cs)

def mod_supply_demand(gold_c,aisc,gold_seq,cb_t,cb_p):
    premium=gold_c/aisc
    if   premium>=4.0:pm=90
    elif premium>=3.5:pm=80
    elif premium>=3.0:pm=72
    elif premium>=2.5:pm=62
    elif premium>=2.0:pm=52
    elif premium>=1.8:pm=42
    else:pm=30
    if len(gold_seq)>=12:
        avg=sum(gold_seq[-12:])/min(12,len(gold_seq))
        if gold_c>avg*1.15:gap=75
        elif gold_c>avg*1.05:gap=65
        elif gold_c>avg*0.95:gap=54
        else:gap=44
    else:gap=50
    if cb_p and cb_p>0:
        mom=(cb_t-cb_p)/cb_p*100
        if   mom>=30:cb=88
        elif mom>=15:cb=76
        elif mom>=5:cb=65
        elif mom>=0:cb=57
        elif mom>=-10:cb=48
        else:cb=36
    else:cb=57
    return max(0,min(100,pm*0.35+gap*0.35+cb*0.30)),"premium="+("%0.2f" % premium)+"x"

def mod_war_premium(regime,hormuz,war,cds,deficit,nom10y,ie5y,oil_exp):
    if regime=="PEACE":return 25,"PEACE"
    elif regime=="TENSION":
        base=40+int((war+hormuz)/4)
        protect=min(12,int(abs(oil_exp)/250)) if oil_exp<0 else 0
        return min(100,base+protect),"TENSION"
    else:
        cds_p=30 if cds>=120 else(22 if cds>=80 else(14 if cds>=60 else 6))
        def_p=-20 if deficit>=10 else(-10 if deficit>=8 else(-3 if deficit>=7 else 0))
        protect=min(15,int(abs(oil_exp)/200)) if oil_exp<0 else 0
        rr=nom10y-ie5y
        if   rr>=2.0:rr_p=-25
        elif rr>=1.5:rr_p=-12
        elif rr>=1.0:rr_p=-3
        elif rr>=0.5:rr_p=8
        else:rr_p=18
        s=65+cds_p+def_p+protect+rr_p
        return max(5,min(100,s)),"WAR:cds_p="+str(cds_p)+" def_p="+str(def_p)+" rr_p="+str(rr_p)

W={"PEACE":  {"B":0.40,"C":0.30,"D":0.20,"E":0.10},
   "TENSION":{"B":0.25,"C":0.30,"D":0.25,"E":0.20},
   "WAR":    {"B":0.10,"C":0.15,"D":0.20,"E":0.55}}

def fuse(regime,sb,sc,sd,se):
    w=W[regime]
    return max(0,min(100,sb*w["B"]+sc*w["C"]+sd*w["D"]+se*w["E"]))

def f_ema(seq,c):
    e=ema_(seq,20) if len(seq)>=20 else None
    if not e:return 50,"EMA"
    dev=(c-e)/e*100;base=82 if c>e else 28
    if dev>8:base-=14
    elif dev>5:base-=8
    elif dev<-5:base+=10
    return max(0,min(100,base)),"EMA"

def f_rsi(r):
    if not r:return 50,"RSI"
    if   r>=80:return 12,"RSI=overbought"
    elif r>=75:return 28,"RSI=overbought"
    elif r>=65:return 62,"RSI=bullish"
    elif r>=45:return 52,"RSI=neutral"
    elif r>=35:return 48,"RSI=bearish"
    elif r<=20:return 85,"RSI=oversold"
    else:return 72,"RSI=oversold"

def f_poly(gp):
    s=92 if gp>=95 else(82 if gp>=88 else(72 if gp>=80 else(64 if gp>=72 else(58 if gp>=65 else(54 if gp>=55 else(48 if gp>=45 else(38 if gp>=35 else 28)))))))
    return max(0,min(100,s)),"Poly"

def f_etf(g,gp):
    if gp is None:gp=g
    c=(g-gp)/gp*100
    s=88 if c>3 else(74 if c>1 else(63 if c>0 else(54 if c>-1 else(40 if c>-3 else 14))))
    if g>1000:s=max(s,78)
    elif g<850:s=min(s,42)
    return max(0,min(100,s)),"GLD"

def pscore(s):
    return 100 if s>=80 else(80 if s>=72 else(60 if s>=64 else(40 if s>=56 else(25 if s>=48 else 0))))

def sig_v5(seq,m,mp,mcr,dxy_seq):
    c=m[CI["CLOSE"]];fed=m[CI["FOMC"]]
    gld=m[CI["GLD"]];cb_g=m[CI["CB"]];poly=m[CI["POLY"]]
    cpi=m[CI["CPI"]];cpi_exp=m[CI["CPI_EXP"]];hormuz=m[CI["HORMUZ"]]
    gp=mp[CI["GLD"]] if mp else None;cbp=mp[CI["CB"]] if mp else None
    r=rsi_(seq,14) if len(seq)>=15 else None
    dxy_z=zscore(dxy_seq,20) if len(dxy_seq)>=20 else None
    regime,_,rdesc=mod_regime(hormuz,mcr[CM["WAR"]],mcr[CM["CDS"]],mcr[CM["NOM10Y"]],mcr[CM["IE5Y"]])
    sb,_=mod_real_rate(mcr[CM["NOM10Y"]],mcr[CM["IE5Y"]],dxy_z)
    sc,_=mod_credit(mcr[CM["CDS"]],cpi,cpi_exp,mcr[CM["IE5Y"]],mcr[CM["NOM10Y"]])
    sd,_=mod_supply_demand(c,mcr[CM["AISC"]],seq,cb_g,cbp)
    se,_=mod_war_premium(regime,hormuz,mcr[CM["WAR"]],mcr[CM["CDS"]],mcr[CM["DEF"]],mcr[CM["NOM10Y"]],mcr[CM["IE5Y"]],mcr[CM["OIL_EXP"]])
    fs=fuse(regime,sb,sc,sd,se)
    se_=f_ema(seq,c);sr_=f_rsi(r);sp_=f_poly(poly);set_=f_etf(gld,gp)
    tech=se_[0]*0.35+sr_[0]*0.20+sp_[0]*0.30+set_[0]*0.15
    if r and r>=80:tech=min(tech,60)
    if r and r<=20:tech=max(tech,65)
    total=max(0,min(100,fs*0.75+tech*0.25))
    pos=pscore(total)
    if fed:pos=int(pos*0.80)
    if   pos>=80:lbl="FULL_LONG_"+str(pos)+"%"
    elif pos>=60:lbl="LONG_"+str(pos)+"%"
    elif pos>=40:lbl="LIGHT_LONG_"+str(pos)+"%"
    elif pos>=25:lbl="BULLISH_"+str(pos)+"%"
    elif pos>0:lbl="SLIGHT_"+str(pos)+"%"
    else:lbl="NEUTRAL("+("%0.0f" % total)+")"
    return pos,lbl,{"regime":regime,"rdesc":rdesc,"B":round(sb,1),"C":round(sc,1),"D":round(sd,1),"E":round(se,1),"total":round(total,1)}

def build_gold(seed=42):
    random.seed(seed);res=[]
    for i,row in enumerate(METAL):
        prev=METAL[i-1][CI["CLOSE"]] if i>0 else row[CI["CLOSE"]]
        seq=[]
        for j in range(65):
            t=(j+1)/65;base=prev+(row[CI["CLOSE"]]-prev)*t
            vol=(row[CI["HIGH"]]-row[CI["LOW"]])/8
            seq.append(max(base+random.uniform(-vol,vol),50))
        res.append(seq)
    return res

def build_dxy(seed=77):
    random.seed(seed);res=[]
    for i,row in enumerate(METAL):
        prev=METAL[i-1][CI["DXY"]] if i>0 else row[CI["DXY"]]
        seq=[]
        for j in range(65):
            t=(j+1)/65;base=prev+(row[CI["DXY"]]-prev)*t
            seq.append(base+random.uniform(-0.8,0.8))
        res.append(seq)
    return res

DG=build_gold();DD=build_dxy()

def runbt():
    eq=100000.;peak=eq;pp=0;w=l=co=0;mxdd=0.
    bq=100000.;bp=METAL[0][CI["CLOSE"]]
    print("\n"+"="*88)
    print("  Gold v5 宏观结构模型回测 | 区间：2024-01 至 2026-03（27个月）")
    print("="*88)
    def fmt(v): return "%.0f" % v
    print(("%-10s %-20s %-28s %8s %6s %10s %4s") % ("Month","Regime","Signal","Mo%","Pos","Equity","W/L"))
    print("-"*88)
    for i in range(len(DG)):
        date=METAL[i][0];row=METAL[i];mcr=MACRO[i]
        pos,lbl,info=sig_v5(DG[i],row,METAL[i-1] if i>0 else None,mcr,DD[i])
        if i>0:
            br=(row[CI["CLOSE"]]-bp)/bp;bq*=(1+br)
        bp=row[CI["CLOSE"]]
        if i==0:
            pp=pos
            print(("%-10s %-20s %-28s %8s %6s %10s %4s") % (date,info["rdesc"],lbl,"--",str(pos)+"%","$"+fmt(eq),"--"))
            continue
        pr=METAL[i-1];mr=(row[CI["CLOSE"]]-pr[CI["CLOSE"]])/pr[CI["CLOSE"]]
        pct=pp/100.;ret=pct*mr;eq*=(1+ret);wl=""
        if abs(mr)>0.001:
            co+=1;ok=(pct>0 and mr>0)or(pct<0 and mr<0)
            if ok:w+=1;wl="W"
            else:l+=1;wl="L"
        peak=max(peak,eq);dd=(peak-eq)/peak*100;mxdd=max(mxdd,dd)
        print(("%-10s %-20s %-28s %+7.2f %5s %10s %4s") % (date,info["rdesc"],lbl,mr*100,str(pp)+"%","$"+fmt(eq),wl))
        pp=pos
    ann=((eq/100000)**(12/(len(METAL)-1))-1)*100
    mrets=[(METAL[i][CI["CLOSE"]]-METAL[i-1][CI["CLOSE"]])/METAL[i-1][CI["CLOSE"]] for i in range(1,len(METAL))]
    ms=(sum(r**2 for r in mrets)/len(mrets))**0.5;av=ms*12**0.5*100
    sh=(ann-5.0)/av;mape=sum(abs(r) for r in mrets)/len(mrets)*100
    dac=co/len(mrets)*100 if mrets else 0
    wr=w/(w+l)*100 if(w+l)>0 else 0
    bret=(bq/100000-1)*100
    print("\n  Equity=$"+fmt(eq)+"("+("%+.1f" % ann)+"%) Sharpe="+("%.2f" % sh)+" MAPE="+("%.2f" % mape)+"% Dir="+("%.1f" % dac)+"% MaxDD="+("%.2f" % mxdd)+"%")
    print("  BuyHold=$"+fmt(bq)+"("+("%+.1f" % bret)+"%) WinRate="+("%.1f" % wr)+"%("+str(w)+"/"+str(l)+")")
    return {"eq":eq,"ann":ann,"sh":sh,"mape":mape,"dac":dac,"mxdd":mxdd,"wr":wr,"w":w,"l":l,"bq":bq,"bret":bret}

if __name__=="__main__":
    print("="*88)
    print("  Gold Trading System v5 — 宏观结构性升级版")
    print("  新增：情景感知 | 实际利率 | US CDS | 石油净出口 | 供需成本")
    print("="*88)
    r5=runbt()
    print("\n"+"="*88)
    print("  版本对比")
    print("="*88)
    v1={"eq":88982,"ann":-5.0,"sh":-27.44,"mape":1.29,"dac":60.0,"mxdd":88.98,"w":18,"l":12,"bq":240950,"bret":140.9}
    v3={"eq":131289,"ann":13.4,"sh":0.46,"mape":4.45,"dac":65.4,"mxdd":4.60,"w":17,"l":9,"bq":240950,"bret":140.9}
    v32={"eq":145353,"ann":18.8,"sh":0.76,"mape":4.45,"dac":80.8,"mxdd":4.60,"w":21,"l":5,"bq":240950,"bret":140.9}
    v4={"eq":144162,"ann":18.4,"sh":0.73,"mape":4.45,"dac":100.0,"mxdd":4.60,"w":19,"l":7,"bq":240950,"bret":140.9}
    def feq(v): return "%.0f" % v
    for nm,r in [
        ("v1 MA20原始版",  v1),
        ("v3 8因子",        v3),
        ("v3.2 12因子",     v32),
        ("v4 13因子",       v4),
        ("v5 宏观结构模型(情景感知)",r5),
    ]:
        print("  %-28s $%10s %+7s Sharpe=%6s MAPE=%5s dir=%5s dd=%6s %3s/%s" % (
            nm, feq(r["eq"]), ("%+.1f" % r["ann"])+"%",
            "%.2f" % r["sh"], ("%.2f" % r["mape"])+"%",
            ("%.1f" % r["dac"])+"%", ("%.2f" % r["mxdd"])+"%",
            str(r["w"]), str(r["l"])))
    print("\n  核心理论：")
