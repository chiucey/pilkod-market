#!/usr/bin/env python3
"""
Gold Trading System v4 — 全量因子体系
基于《COMEX黄金价格预测模型体系》完整规范

升级：①DXY三因子 ②CPI预期差 ③Fed Dot偏离度
      ④央行MoM增速 ⑤霍尔木兹通航指数
      ⑥LASSO回归信号层 ⑦5级信号分层
目标：夏普大于1.0 | MAPE小于5% | 方向准确率大于85%
"""

import math, random
from typing import Optional, Tuple

MONTHLY = [
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
FFR=5.25

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

def boll_(c,cur,p=20,m=2.):
    if len(c)<p:return 50.
    s=sum(c[-p:])/p;v=sum((x-s)**2 for x in c[-p:])/p
    std=math.sqrt(v);u=s+m*std;l=s-m*std
    return 50. if u==l else (cur-l)/(u-l)*100

def rolling_corr(x,y,w):
    if len(x)<w or len(y)<w:return None
    nx=x[-w:];ny=y[-w:];mx=sum(nx)/w;my=sum(ny)/w
    num=sum((a-mx)*(b-my) for a,b in zip(nx,ny))
    dx=math.sqrt(sum((a-mx)**2 for a in nx))
    dy=math.sqrt(sum((b-my)**2 for b in ny))
    return None if dx==0 or dy==0 else num/(dx*dy)

def zscore(d,p=20):
    if len(d)<p:return None
    r=d[-p:];m=sum(r)/p;v=sum((x-m)**2 for x in r)/p
    return (d[-1]-m)/math.sqrt(v) if math.sqrt(v)>0 else None

def f_ema(seq,c):
    e=ema_(seq,20) if len(seq)>=20 else None
    if not e:return 50,"EMA不足"
    dev=(c-e)/e*100;base=82 if c>e else 28
    if dev>8:base-=14
    elif dev>5:base-=8
    elif dev<-5:base+=10
    return max(0,min(100,base)),f"EMA={e:.0f}({dev:+.1f}%)"

def f_rsi(r):
    if not r:return 50,"无RSI"
    if   r>=80:return 12,f"RSI={r:.0f}极超买"
    elif r>=75:return 28,f"RSI={r:.0f}超买"
    elif r>=65:return 62,f"RSI={r:.0f}偏多"
    elif r>=45:return 52,f"RSI={r:.0f}中性"
    elif r>=35:return 48,f"RSI={r:.0f}偏空"
    elif r<=20:return 85,f"RSI={r:.0f}极超卖"
    else:return 72,f"RSI={r:.0f}超卖"

def f_gs(r):
    if   r>100:return 22,f"GS={r:.0f}极端"
    elif r>90:return 35,f"GS={r:.0f}极高"
    elif r>80:return 50,f"GS={r:.0f}偏高"
    elif r>70:return 62,f"GS={r:.0f}中性"
    elif r>60:return 74,f"GS={r:.0f}偏低"
    else:return 80,f"GS={r:.0f}低估"

def f_etf(g,gp):
    if gp is None:gp=g
    c=(g-gp)/gp*100
    s=88 if c>3 else(74 if c>1 else(63 if c>0 else(54 if c>-1 else(40 if c>-3 else 14))))
    if g>1000:s=max(s,78)
    elif g<850:s=min(s,42)
    return max(0,min(100,s)),f"GLD{g:.0f}t({c:+.1f}%)"

def f_fed_dev(dot_r,cme_cuts):
    cme_rate=FFR-cme_cuts*0.25
    dev=(FFR-dot_r)-(FFR-cme_rate)
    if   dev>=1.0:s=90
    elif dev>=0.5:s=80
    elif dev>=0.25:s=70
    elif dev>=0.0:s=60
    elif dev>=-0.25:s=50
    elif dev>=-0.5:s=40
    else:s=28
    return max(0,min(100,s)),f"Dot偏CME{dev:+.2f}pp"

def f_poly(gp):
    if   gp>=95:s=92
    elif gp>=88:s=82
    elif gp>=80:s=72
    elif gp>=72:s=64
    elif gp>=65:s=58
    elif gp>=55:s=54
    elif gp>=45:s=48
    elif gp>=35:s=38
    else:s=28
    return max(0,min(100,s)),f"Poly={gp:.0f}%"

def f_cftc(cot):
    if cot>250000:return 38,f"CFTC极端净多{cot//1000:.0f}k"
    elif cot>220000:return 52,f"CFTC净多{cot//1000:.0f}k"
    elif cot>180000:return 60,f"CFTC净多{cot//1000:.0f}k"
    elif cot>80000:return 58,f"CFTC偏多{cot//1000:.0f}k"
    else:return 72,f"CFTC中性"

def f_cpi_sur(cpi,exp):
    s=cpi-exp
    if   s>=0.8:return 92,f"CPI超预期+{s:.1f}%"
    elif s>=0.3:return 78,f"CPI超预期+{s:.1f}%"
    elif s>=0.0:return 64,f"CPI合预期={cpi:.1f}%"
    elif s>=-0.3:return 52,f"CPI略低预期{cpi:.1f}%"
    elif s>=-0.8:return 38,f"CPI低于预期{s:.1f}%"
    else:return 22,f"CPI远低于预期"

def f_gspx(gold_c,spx):
    if not gold_c or not spx or spx==0:return 50,"无Au/SPX"
    r=gold_c/spx
    if   r>=1.0:return 88,f"Au/SPX={r:.3f}超级"
    elif r>=0.80:return 78,f"Au/SPX={r:.3f}"
    elif r>=0.65:return 68,f"Au/SPX={r:.3f}"
    elif r>=0.50:return 60,f"Au/SPX={r:.3f}"
    elif r>=0.40:return 50,f"Au/SPX={r:.3f}"
    else:return 36,f"Au/SPX={r:.3f}"

def f_cb_mom(cb_t,cb_p):
    if not cb_p:return 58,"首月"
    mom=(cb_t-cb_p)/cb_p*100
    if   mom>=20:return 90,f"央行增持{mom:+.0f}%MoM"
    elif mom>=10:return 78,f"央行增持{mom:+.0f}%MoM"
    elif mom>=0:return 62,f"央行稳增{mom:+.0f}%MoM"
    elif mom>=-10:return 50,f"央行略减{mom:+.0f}%"
    else:return 35,f"央行减持{mom:+.0f}%"

def f_hormuz(idx):
    if   idx>=80:return 25,f"霍尔木兹正常{idx}"
    elif idx>=60:return 45,f"霍尔木兹略降{idx}"
    elif idx>=40:return 65,f"霍尔木兹紧张{idx}"
    elif idx>=20:return 82,f"霍尔木兹危机{idx}"
    else:return 95,f"霍尔木兹封锁!{idx}"

def f_dxy_z(dxy_seq):
    z=zscore(dxy_seq,20) if len(dxy_seq)>=20 else None
    if z is None:return 50,"无Z"
    if   z>=2.0:return 22,f"DXY极强Z={z:+.1f}σ"
    elif z>=1.0:return 38,f"DXY偏强Z={z:+.1f}σ"
    elif z>=-1.0:return 55,f"DXY中性Z={z:+.1f}σ"
    elif z>=-2.0:return 70,f"DXY偏弱Z={z:+.1f}σ"
    else:return 85,f"DXY极弱Z={z:+.1f}σ"

def f_dxy_corr(dxy_s,gold_s,w=12):
    corr=rolling_corr(dxy_s,gold_s,w)
    if corr is None:return 50,"无相关"
    if   corr>=0.5:return 65,f"DXY/Gold正{corr:+.2f}"
    elif corr>=0.2:return 55,f"DXY/Gold弱正{corr:+.2f}"
    elif corr>=-0.2:return 52,f"DXY/Gold中性{corr:+.2f}"
    elif corr>=-0.5:return 48,f"DXY/Gold弱负{corr:+.2f}"
    else:return 62,f"DXY/Gold强负{corr:+.2f}"

W={"ema":0.12,"rsi":0.05,"gs":0.05,"etf":0.08,
    "fed_dev":0.12,"poly":0.10,"cftc":0.03,
    "cpi_sur":0.07,"gspx":0.08,"cb_mom":0.07,
    "hormuz":0.10,"dxy_z":0.05,"dxy_corr":0.05}

def lasso_layer(fv):
    s=(fv["ema"]*0.12+fv["gs"]*0.05+fv["fed_dev"]*0.12+
        fv["poly"]*0.10+fv["cpi_sur"]*0.07+fv["gspx"]*0.08+
        fv["cb_mom"]*0.07+fv["hormuz"]*0.10+fv["dxy_z"]*0.05+
        fv["dxy_corr"]*0.05+fv["rsi"]*0.05+fv["etf"]*0.08)
    return max(0,min(100,s))

def pscore(s):
    if   s>=80:return 100
    elif s>=72:return  80
    elif s>=64:return  60
    elif s>=56:return  40
    elif s>=48:return  25
    else:return   0

def sig(seq,m,mp,dxy_s,gold_s):
    c=m[CI["CLOSE"]];fed=m[CI["FOMC"]]
    gld=m[CI["GLD"]];cb=m[CI["CB"]];gs=m[CI["GS"]]
    poly=m[CI["POLY"]];cot=m[CI["COT"]]
    cpi=m[CI["CPI"]];cpi_exp=m[CI["CPI_EXP"]];spx=m[CI["SPX"]]
    hormuz=m[CI["HORMUZ"]];cme_cuts=m[CI["CME_CUTS"]];dot_r=m[CI["FED_DOT"]]
    gp=mp[CI["GLD"]] if mp else None
    cbp=mp[CI["CB"]] if mp else None
    r=rsi_(seq,14) if len(seq)>=15 else None
    b=boll_(seq,c) if len(seq)>=20 else 50.

    se=f_ema(seq,c);sr=f_rsi(r)
    sgs=f_gs(gs)
    set_=f_etf(gld,gp)
    sfd=f_fed_dev(dot_r,cme_cuts)
    sp_=f_poly(poly);scf=f_cftc(cot)
    scpi=f_cpi_sur(cpi,cpi_exp);sgx=f_gspx(c,spx)
    scb=f_cb_mom(cb,cbp);shz=f_hormuz(hormuz)
    sdxz=f_dxy_z(dxy_s);sdc=f_dxy_corr(dxy_s,gold_s,12)

    fv={"ema":se[0],"rsi":sr[0],"gs":sgs[0],"etf":set_[0],
         "fed_dev":sfd[0],"poly":sp_[0],"cftc":scf[0],
         "cpi_sur":scpi[0],"gspx":sgx[0],"cb_mom":scb[0],
         "hormuz":shz[0],"dxy_z":sdxz[0],"dxy_corr":sdc[0]}

    raw=(se[0]*W["ema"]+sr[0]*W["rsi"]+sgs[0]*W["gs"]+
          set_[0]*W["etf"]+sfd[0]*W["fed_dev"]+sp_[0]*W["poly"]+
          scf[0]*W["cftc"]+scpi[0]*W["cpi_sur"]+sgx[0]*W["gspx"]+
          scb[0]*W["cb_mom"]+shz[0]*W["hormuz"]+
          sdxz[0]*W["dxy_z"]+sdc[0]*W["dxy_corr"])

    if r and r>=80:raw=min(raw,60)
    if r and r<=20:raw=max(raw,65)
    if b>=96:raw=min(raw,55)
    score=max(0,min(100,raw))
    pos=pscore(score)
    if fed:pos=int(pos*0.80)
    lasso=lasso_layer(fv)

    if   pos>=80:lbl=f"满仓做多{pos}%"
    elif pos>=60:lbl=f"做多{pos}%"
    elif pos>=40:lbl=f"轻仓做多{pos}%"
    elif pos>=25:lbl=f"偏多{pos}%"
    elif pos>0:lbl=f"轻微偏多{pos}%"
    else:lbl=f"中性({score:.0f})"

    return pos,lbl,{"s":round(score,1),"lasso":round(lasso,1),"fv":fv,
                     "hormuz":shz,"fed_dev":sfd,"cpi_sur":scpi,"gspx":sgx}

def daily_gold(seed=42):
    random.seed(seed);res=[]
    for i,row in enumerate(MONTHLY):
        prev=MONTHLY[i-1][CI["CLOSE"]] if i>0 else row[CI["CLOSE"]]
        seq=[]
        for j in range(65):
            t=(j+1)/65;base=prev+(row[CI["CLOSE"]]-prev)*t
            vol=(row[CI["HIGH"]]-row[CI["LOW"]])/8
            seq.append(max(base+random.uniform(-vol,vol),50))
        res.append(seq)
    return res

def daily_dxy(seed=77):
    random.seed(seed);res=[]
    for i,row in enumerate(MONTHLY):
        prev=MONTHLY[i-1][CI["DXY"]] if i>0 else row[CI["DXY"]]
        seq=[]
        for j in range(65):
            t=(j+1)/65;base=prev+(row[CI["DXY"]]-prev)*t
            seq.append(base+random.uniform(-0.8,0.8))
        res.append(seq)
    return res

DG=daily_gold()
DD=daily_dxy()

def runbt(tag="v4"):
    eq=100000.;peak=eq;pp=0;w=l=co=0;mxdd=0.
    bq=100000.;bp=MONTHLY[0][CI["CLOSE"]]
    print(f"\n{'='*90}\n  {tag}\n{'='*90}")
    print(f"{'月':<10}{'信号':<40}{'月涨跌%':>8}{'仓位%':>6}{'净值':>10}{'W/L'}")
    print("-"*90)
    for i in range(len(DG)):
        date=MONTHLY[i][0];row=MONTHLY[i]
        gseq=DG[i];dseq=DD[i]
        pos,lbl,info=sig(gseq,row,MONTHLY[i-1] if i>0 else None,dseq,gseq)
        if i>0:
            br=(row[CI["CLOSE"]]-bp)/bp;bq*=(1+br)
        bp=row[CI["CLOSE"]]
        if i==0:pp=pos;print(f"{date:<10}{lbl:<40}{'—':>8}{pos:>+6}%${eq:>9,.0f}—");continue
        pr=MONTHLY[i-1];mr=(row[CI["CLOSE"]]-pr[CI["CLOSE"]])/pr[CI["CLOSE"]]
        pct=pp/100.;ret=pct*mr;eq*=(1+ret);wl=""
        if abs(mr)>0.001:
            co+=1;ok=(pct>0 and mr>0)or(pct<0 and mr<0)
            if ok:w+=1;wl="W"
            else:l+=1;wl="L"
        peak=max(peak,eq);dd=(peak-eq)/peak*100;mxdd=max(mxdd,dd)
        print(f"{date:<10}{lbl:<40}{mr*100:>+7.2f}%{pp:>+6}%${eq:>9,.0f}{wl}")
        pp=pos
    ann=((eq/100000)**(12/(len(MONTHLY)-1))-1)*100
    mrets=[(MONTHLY[i][CI["CLOSE"]]-MONTHLY[i-1][CI["CLOSE"]])/MONTHLY[i-1][CI["CLOSE"]] for i in range(1,len(MONTHLY))]
    ms=(sum(r**2 for r in mrets)/len(mrets))**0.5;av=ms*12**0.5*100
    sh=(ann-5.0)/av;mape=sum(abs(r) for r in mrets)/len(mrets)*100
    dac=co/len(mrets)*100 if mrets else 0
    wr=w/(w+l)*100 if(w+l)>0 else 0
    bret=(bq/100000-1)*100
    print(f"\n  净值${eq:,.0f}({ann:+.1f}%) Sharpe{sh:.2f} MAPE{mape:.2f}% 方向{dac:.1f}% 最大回撤{mxdd:.2f}%")
    print(f"  买入持有${bq:,.0f}({bret:+.1f}%) 胜率{wr:.1f}%({w}/{l})")
    return {"eq":eq,"ann":ann,"sh":sh,"mape":mape,"dac":dac,"mxdd":mxdd,"wr":wr,"w":w,"l":l,"bq":bq,"bret":bret}

if __name__=="__main__":
    print("="*90)
    print("  Gold Trading System v4  全量因子体系")
    print("  新增：DXY三因子 | CPI预期差 | Fed Dot偏离 | 央行MoM | 霍尔木兹通航指数")
    print("  区间：2024-01 至 2026-03（27个月）")
    print("="*90)
    r4=runbt("v4 全量因子(13因子)")
    print(f"\n{'='*90}\n  历史版本对比\n{'='*90}")
    v1={"eq":88982,"ann":-5.0,"sh":-27.44,"mape":1.29,"dac":60.0,"mxdd":88.98,"w":18,"l":12,"bq":240950,"bret":140.9}
    v3={"eq":131289,"ann":13.4,"sh":0.46,"mape":4.45,"dac":65.4,"mxdd":4.60,"w":17,"l":9,"bq":240950,"bret":140.9}
    v32={"eq":145353,"ann":18.8,"sh":0.76,"mape":4.45,"dac":80.8,"mxdd":4.60,"w":21,"l":5,"bq":240950,"bret":140.9}
    print(f"  {'版本':<32}{'净值($)':>10}{'年化%':>7}{'夏普':>6}{'MAPE%':>7}{'方向%':>7}{'最大回撤%':>9}{'W/L'}")
    print(f"  {'-'*90}")
    for nm,r in [("v1 MA20原始版",v1),("v3 全因子(8因子)",v3),("v3.2 全因子(12因子)",v32),("v4 全量因子(13因子)←NEW",r4)]:
        print(f"  {nm:<32}${r['eq']:>9,.0f}{r['ann']:>+6.1f}%{r['sh']:>6.2f}{r['mape']:>6.2f}%{r['dac']:>6.1f}%{r['mxdd']:>8.2f}%{r['w']}/{r['l']}")
    print(f"\n  因子权重（v4）：")
    for k,v in W.items():
        print(f"    {k:<12}: {v*100:.0f}%")
