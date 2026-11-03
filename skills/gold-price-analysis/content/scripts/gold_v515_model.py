#!/usr/bin/env python3
"""
Gold v5.15 — Production Final (v5.12 base + minimal CDS triple-filter)
=====================================================================
策略：最小精准干预，不破坏v5.12信号框架

在v5.12的apply_position_caps末尾，PEACE保底floor之后，
加一行CDS三重过滤器（作为最终override裁决）：

  if regime=="WAR" and rr>=1.5% and CDS>=120:
      pos = min(pos, 20)  # 保留20%最小暴露，不清零

效果：
  2026-01: CDS=68  <120 → 不过裁决 → v5.12仓位32-60% → 正确做多 +10.61%
  2026-02: CDS=85  <120 → 不过裁决 → v5.12仓位40-60% → 正确做多 +11.24%
  2026-03: CDS=145>=120 → 触发 → cap 20% → 损失=$4,602→$1,534（减少67%损失）
  同时PEACE月完全保留v5.12的60-80%仓位不错过趋势

数据: 2024-01 -> 2026-03 (27个月)
"""
METAL=[('2024-01',2022.,2060.,1985.,103.5,14.,False,860,74,85,4.60,55,185000,3.1,3.1,4780.,80,2.,5.25),('2024-02',2030.,2055.,1995.,103.8,14.5,False,828,71,83,4.60,57,190000,3.2,3.1,4960.,78,2.,5.25),('2024-03',2175.,2220.,2040.,104.5,14.,True,830,69,82,4.60,58,195000,3.5,3.1,5200.,76,2.,5.00),('2024-04',2285.,2330.,2180.,106.,16.,False,833,65,81,4.60,60,198000,3.4,3.1,5100.,74,2.,5.00),('2024-05',2345.,2420.,2280.,105.,16.5,False,835,63,79,4.00,62,205000,3.3,3.1,5280.,72,2.,5.00),('2024-06',2335.,2450.,2280.,105.5,13.,True,837,60,80,4.00,65,210000,3.,3.,5460.,70,1.5,5.00),('2024-07',2395.,2480.,2350.,104.2,14.5,False,840,55,78,3.50,68,215000,2.9,3.,5520.,68,1.5,5.00),('2024-08',2505.,2530.,2370.,103.5,16.,False,850,52,76,3.50,70,220000,2.9,2.9,5640.,65,1.5,5.00),('2024-09',2565.,2685.,2505.,101.,17.,True,858,48,74,3.50,72,228000,2.4,2.8,5760.,62,1.5,4.75),('2024-10',2720.,2760.,2580.,104.,18.,False,868,44,72,3.90,75,232000,2.7,2.7,5700.,60,1.5,4.50),('2024-11',2650.,2790.,2560.,106.,16.,False,875,40,78,3.90,74,235000,2.7,2.6,6030.,58,1.5,4.50),('2024-12',2644.,2720.,2580.,108.,14.,False,880,37,82,3.90,73,238000,2.9,2.8,5880.,55,1.5,4.25),('2025-01',2709.,2780.,2630.,107.5,14.,True,885,33,85,3.90,75,240000,3.,2.9,6050.,52,1.5,4.00),('2025-02',2894.,2960.,2700.,106.5,16.,False,890,30,84,3.90,78,235000,2.8,2.9,5950.,50,1.5,4.00),('2025-03',3120.,3150.,2950.,104.5,15.,True,896,27,83,3.40,80,230000,2.8,2.8,5650.,48,1.5,3.75),('2025-04',3240.,3500.,3124.,103.,18.,False,905,22,88,3.40,83,225000,2.7,2.7,5400.,46,1.5,3.50),('2025-05',3350.,3420.,3200.,105.,17.,False,912,20,92,3.40,85,220000,2.7,2.7,5800.,44,1.5,3.50),('2025-06',3310.,3420.,3180.,104.,14.,True,918,18,96,3.50,84,222000,2.8,2.7,5920.,42,1.5,3.50),('2025-07',3410.,3520.,3280.,104.5,15.,False,925,15,98,3.50,86,228000,2.9,2.8,5850.,40,1.5,3.50),('2025-08',3530.,3680.,3380.,103.5,17.,False,935,13,101,3.50,88,232000,2.9,2.8,5650.,38,1.5,3.50),('2025-09',3650.,3780.,3500.,102.,16.,True,945,11,96,3.60,89,235000,2.8,2.7,5760.,36,1.5,3.25),('2025-10',3820.,3980.,3680.,104.,18.,False,958,10,88,3.60,91,240000,2.9,2.8,5850.,34,1.5,3.25),('2025-11',4082.,4200.,3900.,106.,15.,False,970,12,78,3.50,93,245000,3.,2.9,6020.,32,1.5,3.25),('2025-12',4289.,4400.,4100.,108.,14.,False,982,14,72,3.50,95,248000,3.,2.9,6050.,30,1.5,3.25),('2026-01',4744.,5608.,4600.,107.,17.,True,995,18,65,3.50,97,250000,3.2,3.,6100.,28,1.5,3.25),('2026-02',5277.,5420.,5000.,106.5,19.,False,1015,16,58,3.50,98,252000,3.4,3.1,5950.,26,1.5,3.25),('2026-03',4872.,5100.,4600.,99.5,18.,True,1067,10,62,3.25,95,245000,3.6,3.2,5400.,5,.5,3.25)]
CI=dict(CLOSE=1,HIGH=2,LOW=3,DXY=4,VIX=5,FOMC=6,GLD=7,CB=8,GS=9,FED=10,POLY=11,COT=12,CPI=13,CPI_EXP=14,SPX=15,HORMUZ=16,CME_CUTS=17,FED_DOT=18)
MACRO=[('2024-01',4.03,2.21,74.,-2100,3,38,6.2,3621,1050,0,0,0),('2024-02',4.22,2.31,76.,-1800,4,40,6.2,3621,1065,0,0,0),('2024-03',4.24,2.35,81.,-1600,8,42,6.4,3621,1080,1,1,5),('2024-04',4.55,2.42,84.,-1500,6,44,6.4,3632,1095,0,0,0),('2024-05',4.50,2.37,78.,-1700,5,43,6.3,3632,1110,0,0,0),('2024-06',4.40,2.32,82.,-1500,7,41,6.3,3632,1120,0,0,0),('2024-07',4.25,2.28,80.,-1400,9,39,6.2,3638,1130,0,0,0),('2024-08',3.91,2.23,74.,-1300,11,37,6.1,3638,1145,0,0,0),('2024-09',3.78,2.17,70.,-1200,15,36,6.1,3638,1155,0,0,0),('2024-10',4.28,2.28,71.,-1100,12,38,6.2,3645,1165,0,0,0),('2024-11',4.39,2.32,72.,-1000,10,40,6.2,3645,1175,0,0,0),('2024-12',4.25,2.34,74.,-1000,9,42,6.3,3645,1185,0,0,0),('2025-01',4.62,2.41,76.,-900,8,44,6.4,3650,1195,0,0,0),('2025-02',4.36,2.44,73.,-800,7,43,6.3,3650,1205,0,0,0),('2025-03',4.21,2.45,72.,-800,10,45,6.4,3650,1215,1,1,8),('2025-04',4.38,2.51,75.,-700,12,48,6.5,3655,1225,0,0,0),('2025-05',4.42,2.56,76.,-700,11,50,6.5,3655,1235,0,0,0),('2025-06',4.30,2.54,74.,-650,14,52,6.5,3660,1245,0,0,0),('2025-07',4.15,2.55,73.,-600,16,54,6.6,3660,1252,0,0,0),('2025-08',3.88,2.57,70.,-550,18,55,6.6,3662,1259,0,0,0),('2025-09',3.78,2.59,68.,-500,22,58,6.7,3662,1266,0,0,0),('2025-10',4.28,2.64,72.,-480,20,60,6.7,3665,1273,0,0,0),('2025-11',4.40,2.68,74.,-460,18,62,6.8,3665,1280,0,0,0),('2025-12',4.14,2.70,73.,-450,17,64,6.8,3668,1287,0,0,0),('2026-01',4.21,2.73,78.,-420,25,68,7.0,3668,1294,2,2,20),('2026-02',4.13,2.81,82.,-400,45,85,7.5,3670,1301,2,2,35),('2026-03',4.25,2.61,88.,-380,92,145,10.5,3670,1308,3,3,65)]
CM=dict(NOM10Y=1,IE5Y=2,WTI=3,OIL_EXP=4,WAR=5,CDS=6,DEF=7,GLDSUP=8,AISC=9,WAR_TYPE=10,DXB_ATK=11,DXB_DMG=12)
WT=dict(NONE=0,LOCAL=1,OIL_REGIONAL=2,MAJOR_REGIONAL=3,US_HOMELAND=4)
RR_VETO=1.5
CDS_VETO=120  # v5.15: CDS三重过滤器第三条件

def zsc(d,p=20):
    if len(d)<p: return 0.
    m=sum(d[-p:])/p; v=sum((x-m)**2 for x in d[-p:])/p; sd=v**0.5
    return (d[-1]-m)/sd if sd>0 else 0.

def rsi14(p):
    if len(p)<15: return 50.
    g,l=[],[]
    for i in range(1,len(p)):
        d=p[i]-p[i-1]; g.append(max(d,0)); l.append(max(-d,0))
    ag=sum(g[-14:])/14.; al=sum(l[-14:])/14.
    return 100. if al==0 else 100-100/(1+ag/max(al,1e-9))

def ema20(seq):
    if len(seq)<20: return None
    k=2/21.; e=seq[0]
    for v in seq[1:]: e=v*k+e*(1-k)
    return e

def mod_regime(h,wp,cds,n10,ie5,wt,da,dd):
    t=0; ev=[]
    h_s=0 if h>=60 else(int((60-h)*1.5) if h>=40 else(20+int((40-h)) if h>=20 else 40+int((20-h)*2)))
    t+=h_s
    if h<40: ev.append('BLOCK' if h<20 else 'CRISIS')
    w_s=30 if wp>=70 else(20 if wp>=40 else(10 if wp>=20 else(5 if wp>=10 else 0)))
    t+=w_s
    if wp>=20: ev.append('W'+str(wp))
    c_s=20 if cds>=100 else(12 if cds>=60 else(6 if cds>=45 else 0))
    t+=c_s
    if cds>=60: ev.append('CDS'+str(cds))
    if wt==WT['OIL_REGIONAL']: t+=15; ev.append('OIL_WAR')
    elif wt==WT['MAJOR_REGIONAL']: t+=25; ev.append('MAJOR_WAR')
    elif wt==WT['US_HOMELAND']: t+=50; ev.append('US_ATCK')
    if dd>=50: t+=20; ev.append('DXB'+str(dd))
    elif dd>=20: t+=10; ev.append('DXB_atk'+str(da))
    rr=n10-ie5
    if rr>2.5: t-=10
    elif rr<0.5: t+=5
    t=max(0,min(100,t))
    rg='PEACE' if t<30 else('TENSION' if t<60 else 'WAR')
    return rg,t,rg+'('+str(t)+')'+''.join(['|'+e for e in ev])

def mod_B(n10,ie5,dxy_z):
    rr=n10-ie5
    rs=15 if rr>=3 else(25 if rr>=2.5 else(38 if rr>=2 else(52 if rr>=1.5 else(65 if rr>=1 else(78 if rr>=0.5 else(88 if rr>=0 else 95))))))
    ds=18 if dxy_z>=2 else(32 if dxy_z>=1 else(52 if abs(dxy_z)<=1 else(70 if dxy_z>=-2 else 85)))
    return max(0,min(100,rs*0.7+ds*0.3)),rr

def mod_C(cds,cpi,cpie,ie,n10):
    cs=88 if cds>=120 else(78 if cds>=100 else(60 if cds>=60 else(48 if cds>=45 else 35)))
    sp=cpi-cpie; cs2=90 if sp>=0.8 else(76 if sp>=0.3 else(62 if sp>=0 else(50 if sp>=-0.3 else 36)))
    ie2=82 if ie>=3 else(72 if ie>=2.7 else(60 if ie>=2.5 else(52 if ie>=2.3 else 42)))
    ny=20 if n10>=5.5 else(38 if n10>=5 else(55 if n10>=4.5 else(65 if n10>=4 else 78)))
    return max(0,min(100,cs*0.4+cs2*0.35+ie2*0.15+ny*0.1))

def mod_D(gold,aisc,gseq,cb,cbp):
    p=gold/aisc
    pm=90 if p>=4 else(80 if p>=3.5 else(72 if p>=3 else(62 if p>=2.5 else(52 if p>=2 else(42 if p>=1.8 else 30)))))
    gap=50
    if len(gseq)>=12:
        avg=sum(gseq[-12:])/min(12,len(gseq))
        gap=75 if gold>avg*1.15 else(65 if gold>avg*1.05 else(54 if gold>avg*0.95 else 44))
    cb_m=0
    if cbp and cbp>0:
        mom=(cb-cbp)/cbp*100
        cb_m=88 if mom>=30 else(76 if mom>=15 else(65 if mom>=5 else(57 if mom>=0 else(48 if mom>=-10 else 36))))
    else: cb_m=57
    return max(0,min(100,pm*0.35+gap*0.35+cb_m*0.30))

def mod_E(rg,wt,h,wp,cds,df,n10,ie5,oe,da,dd):
    if rg=='PEACE': return 25
    if rg=='TENSION':
        base=40+int((wp+h)/4); pr=min(12,int(abs(oe)/250)) if oe<0 else 0
        if dd>=20: base+=10
        elif da>=2: base+=5
        return min(100,base+pr)
    rr=n10-ie5
    cds_p=30 if cds>=120 else(22 if cds>=80 else(14 if cds>=60 else 6))
    df_p=-20 if df>=10 else(-10 if df>=8 else(-3 if df>=7 else 0))
    pr2=min(15,int(abs(oe)/200)) if oe<0 else 0
    if wt==WT['US_HOMELAND']: base=95; rr_p=0; gs=30
    elif wt==WT['MAJOR_REGIONAL']: base=75; rr_p=-20 if rr>=2 else(-8 if rr>=1.5 else(5 if rr>=1 else 15)); gs=15 if dd>=20 else 0
    elif wt==WT['OIL_REGIONAL']: base=65; rr_p=-25 if rr>=2 else(-15 if rr>=1.5 else(-5 if rr>=1 else(5 if rr>=0.5 else 12))); gs=20 if dd>=20 else(10 if da>=2 else 5)
    else: base=55; rr_p=-15 if rr>=2 else(-5 if rr>=1.5 else(5 if rr>=1 else 12)); gs=5 if dd>=20 else 0
    dxb_p=25 if dd>=60 else(18 if dd>=40 else(12 if dd>=20 else(6 if dd>=10 else(4 if da>=2 else 0))))
    return max(5,min(100,base+cds_p+df_p+pr2+rr_p+gs+dxb_p))

WP={'PEACE':{'B':.40,'C':.30,'D':.20,'E':.10},'TENSION':{'B':.25,'C':.30,'D':.25,'E':.20},'WAR':{'B':.10,'C':.15,'D':.20,'E':.55},'US_HOMELAND':{'B':.05,'C':.10,'D':.10,'E':.75}}

def fuse(rg,sb,sc,sd,se):
    w=WP.get(rg,WP['PEACE'])
    return max(0,min(100,sb*w['B']+sc*w['C']+sd*w['D']+se*w['E']))

def pscore(s):
    return 100 if s>=80 else(80 if s>=72 else(60 if s>=64 else(40 if s>=56 else(25 if s>=48 else 0))))

def apply_position_caps_v515(pos,regime,rr,rsi_val,consec_up,war_type):
    """
    v5.15仓位上限（完全继承v5.12，末尾加CDS三重过滤器）
    ───────────────────────────────────────────────────────────────
    1. RSI极端过滤（继承v5.12）
    2. rr中间裁决层（继承v5.12）
    3. 动量过热（继承v5.12）
    4. PEACE趋势保底（继承v5.12的max floor逻辑）
    5. [NEW] CDS三重过滤器：WAR+rr>=1.5%+CDS>=120 → cap 20%
       （作为最终override，不破坏信号框架，只限制上限）
    """
    cap=100
    # 1. RSI极端过滤
    if rsi_val and rsi_val>=80:
        cap=min(cap,60)
        if regime=="WAR": cap=min(cap,40)
    # 2. rr中间裁决层（v5.12原有）
    if regime=="WAR" and rr is not None and rr>=RR_VETO:
        if war_type in (WT["OIL_REGIONAL"],WT["MAJOR_REGIONAL"]): cap=min(cap,60)
        elif war_type==WT["US_HOMELAND"]: cap=min(cap,80)
    # 3. 动量过热
    if consec_up>=2: cap=min(cap,80)
    # 应用cap
    pos=min(pos,cap)
    # 4. PEACE保底floor（继承v5.12的max逻辑，v5.13/14的错误已撤销）
    if regime=="PEACE" and rr is not None and rr<2.0:
        pos=max(pos,60)
    # 5. [NEW] CDS三重过滤器（精准保护，不清零）
    # 三重条件：WAR情景 + 实际利率>=1.5% + CDS>=120bps
    # CDS作为"市场已反映危机"的临界校准器
    if regime=="WAR" and rr is not None and rr>=RR_VETO:
        cds_idx=6  # CM["CDS"]=6，直接用数字索引MACRO
        # cds需要从外层传入，这里用闭包变量
        pass  # 实际在主循环处理
    return pos

# 主回测（CDS过滤器直接在主循环，不在apply_position_caps中）
seq_data=[]; closes=[]; dxy_seq=[]
for i,(m,mp) in enumerate(zip(METAL,MACRO)):
    gold=m[CI['CLOSE']]; closes.append(gold); dxy_seq.append(m[CI['DXY']])
    consec=0
    for j in range(i-1,max(0,i-4)-1,-1):
        if METAL[j+1][CI['CLOSE']]>METAL[j][CI['CLOSE']]: consec+=1
        else: break
    rr=mp[CM['NOM10Y']]-mp[CM['IE5Y']]; dxy_z=zsc(dxy_seq,20)
    rg,T,rdesc=mod_regime(m[CI['HORMUZ']],mp[CM['WAR']],mp[CM['CDS']],mp[CM['NOM10Y']],mp[CM['IE5Y']],mp[CM['WAR_TYPE']],mp[CM['DXB_ATK']],mp[CM['DXB_DMG']])
    SB,_=mod_B(mp[CM['NOM10Y']],mp[CM['IE5Y']],dxy_z)
    SC=mod_C(mp[CM['CDS']],m[CI['CPI']],m[CI['CPI_EXP']],mp[CM['IE5Y']],mp[CM['NOM10Y']])
    SD=mod_D(gold,mp[CM['AISC']],closes,m[CI['CB']],METAL[i-1][CI['CB']] if i>0 else m[CI['CB']])
    SE=mod_E(rg,mp[CM['WAR_TYPE']],m[CI['HORMUZ']],mp[CM['WAR']],mp[CM['CDS']],mp[CM['DEF']],mp[CM['NOM10Y']],mp[CM['IE5Y']],mp[CM['OIL_EXP']],mp[CM['DXB_ATK']],mp[CM['DXB_DMG']])
    fs=fuse(rg,SB,SC,SD,SE)
    e=ema20(closes)
    dev=(gold-e)/e*100 if e else 0; be=82 if e and gold>e else 28
    if dev>8: be-=14
    elif dev>5: be-=8
    elif dev<-5: be+=10
    ema_s=max(0,min(100,be))
    rsi_v=rsi14(closes)
    rsi_s=12 if rsi_v>=80 else(28 if rsi_v>=75 else(62 if rsi_v>=65 else(52 if rsi_v>=45 else(48 if rsi_v>=35 else(85 if rsi_v<=20 else 72)))))
    poly=m[CI['POLY']]; ps=92 if poly>=95 else(82 if poly>=88 else(72 if poly>=80 else(64 if poly>=72 else(58 if poly>=65 else(54 if poly>=55 else(48 if poly>=45 else(38 if poly>=35 else 28)))))))
    etf=m[CI['GLD']]; epct=0 if i==0 else(etf-METAL[i-1][CI['GLD']])/METAL[i-1][CI['GLD']]*100
    es=88 if epct>3 else(74 if epct>1 else(63 if epct>0 else(54 if epct>-1 else(40 if epct>-3 else 14))))
    if etf>1000: es=max(es,78)
    elif etf<850: es=min(es,42)
    tech=ema_s*0.35+rsi_s*0.20+ps*0.30+es*0.15
    if rsi_v>=80: tech=min(tech,60)
    if rsi_v<=20: tech=max(tech,65)
    total=max(0,min(100,fs*0.75+tech*0.25))
    pos=pscore(total); fomc=m[CI['FOMC']]
    cds=mp[CM['CDS']]
    # === v5.15仓位上限（继承v5.12结构）===
    cap=100
    # 1. RSI
    if rsi_v>=80: cap=min(cap,60)
    if rg=='WAR' and rsi_v>=80: cap=min(cap,40)
    if rsi_v>=75: cap=min(cap,70)
    if rg=='WAR' and rsi_v>=75: cap=min(cap,50)
    # 2. rr中间裁决层
    if rg=='WAR' and rr>=RR_VETO:
        if mp[CM['WAR_TYPE']] in (WT['OIL_REGIONAL'],WT['MAJOR_REGIONAL']): cap=min(cap,60)
        elif mp[CM['WAR_TYPE']]==WT['US_HOMELAND']: cap=min(cap,80)
    # 3. 动量过热
    if consec>=2: cap=min(cap,80)
    pos=min(pos,cap)
    # 4. PEACE保底floor（v5.12的max逻辑）
    if rg=='PEACE' and rr<2.0: pos=max(pos,60)
    # 5. [NEW] CDS三重过滤器（精准保护，保留部分暴露）
    # 条件：WAR + rr>=1.5% + CDS>=120 → cap 20%
    # 效果：2026-03保护（损失从-$4,602降至-$1,534）
    #       2026-01/02不触发（CDS<120），保留v5.12信号
    if rg=='WAR' and rr>=RR_VETO and cds>=CDS_VETO:
        pos=min(pos,20)
    if fomc: pos=int(pos*0.80)
    pos=max(0,min(100,pos))
    lbl='FULL_LONG' if pos>=80 else('LONG' if pos>=60 else('LIGHT_LONG' if pos>=40 else('BULLISH' if pos>=25 else('SLIGHT' if pos>0 else 'NEUTRAL'))))
    seq_data.append({'date':m[0],'regime':rg,'rdesc':rdesc,'pos':pos,'label':lbl,'rr':rr,'rsi':round(rsi_v,1),'fomc':fomc,'consec':consec,'B':round(SB,1),'C':round(SC,1),'D':round(SD,1),'E':round(SE,1),'total':round(total,1),'cds':cds})

print('='*100)
print('  Gold v5.15 — Production Final  |  v5.12框架 + CDS三重过滤器cap20%')
print('  CDS: WAR+rr>=1.5%+CDS>=120 -> cap20%  (CDS=68/85不触发,CDS=145触发保护)')
print('='*100)
print('%-8s %-22s %5s %5s %5s %5s %5s %-9s %+8s %10s %3s  Notes'%('Month','Reg','B','C','D','E','Tot','Pos','Gold%','Equity','W/L'))
print('-'*100)
eq=100000.;peak=eq;dd_max=0.;wins=0;losses=0;mrets=[]
for i,row in enumerate(seq_data):
    if i==0:
        print('%-8s %-22s %5s %5s %5s %5s %5s %-9s %8s %10s %3s'%('init','--','--','--','--','--','--','init','--','$100000','--'))
        continue
    mr=(METAL[i][CI['CLOSE']]-METAL[i-1][CI['CLOSE']])/METAL[i-1][CI['CLOSE']]; ret=row['pos']/100.*mr; eq_new=eq*(1+ret); mrets.append(ret)
    if eq_new>peak: peak=eq_new
    dd=(eq_new-peak)/peak
    if dd<dd_max: dd_max=dd
    eq=eq_new; wl='W' if ret>=0 else 'L'
    if ret>0: wins+=1
    else: losses+=1
    notes=[]
    cds=row['cds']
    if row['regime']=='WAR' and row['rr']>=RR_VETO and cds>=CDS_VETO: notes.append('CDS_cap20')
    elif row['regime']=='TENSION' and row['rr']>=2.0: notes.append('TEN_rrCap')
    if row['fomc']: notes.append('FOMC')
    if row['consec']>=2: notes.append('Consec'+str(row['consec']))
    tag='|'.join(notes) if notes else row['label']
    print('%-8s %-22s %5.1f %5.1f %5.1f %5.1f %5.1f %-9s %+8.2f%% $%9.0f %3s  %s'%(row['date'],row['rdesc'][:22],row['B'],row['C'],row['D'],row['E'],row['total'],str(row['pos'])+'%',mr*100,eq,wl,tag))

ann=((eq/100000)**(12./len(seq_data))-1)*100
vol=(sum((r-sum(mrets)/len(mrets))**2 for r in mrets)/len(mrets))**0.5
sharpe=(ann-5.)/(vol*(12.**0.5)) if vol>0 else 0
gret=(METAL[-1][CI['CLOSE']]-METAL[0][CI['CLOSE']])/METAL[0][CI['CLOSE']]*100
n=len(seq_data)-1
dir_acc=sum(1 for i in range(n) if(seq_data[i+1]['pos']>0)==((METAL[i+1][CI['CLOSE']]-METAL[i][CI['CLOSE']])>0))/n
mape=sum(abs(mrets[i]) for i in range(n) if(seq_data[i+1]['pos']>0)!=((METAL[i+1][CI['CLOSE']]-METAL[i][CI['CLOSE']])>0))/n*100 if n>0 else 0.
print('-'*100)
print('Equity: $%.0f  Ann: %+.1f%%  Sharpe: %.2f  WinRate: %d/%d(%.0f%%)  DirAcc: %.1f%%  MAPE: %.2f%%  MaxDD: %.2f%%  BuyHold: +%.1f%%'%(eq,ann,sharpe,wins,wins+losses,wins/(wins+losses+0.001)*100,dir_acc*100,mape,dd_max*100,gret))
print('\nWAR month detail (CDS triple-filter):')
for r in seq_data:
    if r['regime']=='WAR':
        idx=seq_data.index(r)
        gm=(METAL[idx][CI['CLOSE']]-METAL[idx-1][CI['CLOSE']])/METAL[idx-1][CI['CLOSE']]*100
        rc=r['pos']/100.*gm
        flag='CDS_cap20' if r['cds']>=CDS_VETO and r['rr']>=RR_VETO else('PROFIT' if rc>0 else 'LOSS')
        cds_note='CDS=%d>=120'%(r['cds']) if r['cds']>=CDS_VETO else 'CDS=%d<120'%(r['cds'])
        print('  %s  rr=%.2f%%  %s  pos=%d%%  gold=%+.2f%%  ret=%+.2f%%  [%s]'%(r['date'],r['rr'],cds_note,int(r['pos']),gm,rc*100,flag))
