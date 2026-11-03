#!/usr/bin/env python3
"""v15.4优化验证：B=M5止盈20% + C=M6仅发酵期做"""
import urllib.request, json

def fetch(code, days=500):
    url = f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={code}&scale=240&ma=no&datalen={days}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"}), timeout=10) as r:
            d = json.loads(r.read().decode("utf-8"))
            return d if isinstance(d, list) else []
    except: return []

def mk(raw):
    r = []
    for k in raw:
        try:
            r.append({"d":k["day"],"o":float(k["open"]),"c":float(k["close"]),"h":float(k["high"]),"l":float(k["low"]),"v":int(k["volume"])})
        except: pass
    return r

CORE35 = [
    ("sh600036","招商"),("sh601318","平安"),("sh600016","民生"),("sh600028","石化"),
    ("sh600900","电力"),("sh601668","建筑"),("sh600031","三一"),("sh600887","伊利"),
    ("sh601012","隆基"),("sh600276","恒瑞"),("sh603259","药明"),("sh600690","海尔"),
    ("sz002475","立讯"),("sz000333","美的"),("sz002594","比亚迪"),("sz300750","宁德"),
    ("sh601888","中免"),("sh600519","茅台"),("sz300059","东财"),("sz300122","智飞"),
    ("sz300760","迈瑞"),("sh688008","澜起"),("sh688111","金山"),("sz300124","汇川"),
    ("sz300142","沃森"),("sh688012","中微"),("sh688388","晶科"),("sh688505","复旦张"),
    ("sz300015","爱尔"),("sh688036","传音"),("sz300033","锐捷"),("sh688981","中芯"),
    ("sz300274","阳光"),("sh688256","寒武纪"),("sh688522","纳芯微"),
]

D = {}
for code, name in CORE35:
    ks = mk(fetch(code, 500))
    if len(ks) >= 50: D[code] = {"n": name, "ks": ks}
HS = mk(fetch("sh000001", 500))

DI = {}
for code, d_data in D.items():
    for j, k in enumerate(d_data["ks"]):
        DI[(code, k["d"])] = j

q1 = [k for k in HS if "2024-09-01" <= k["d"] <= "2026-03-31"]
bh_ref = (q1[-1]["c"]-q1[0]["o"])/q1[0]["o"]*100

def MA(ks, n, i):
    if i < 0 or i >= len(ks): return ks[i]["c"]
    s = max(0, i-n+1)
    return sum(ks[j]["c"] for j in range(s,i+1))/max(1,i-s+1)

def VOL(ks, n, i):
    if i < 0 or i >= len(ks): return max(1, ks[0]["v"])
    s = max(0, i-n+1)
    return sum(ks[j]["v"] for j in range(s,i+1))/max(1,i-s+1)

def mkt_phase(date):
    hs_d = [k for k in HS if k["d"] <= date]
    if len(hs_d) < 10: return "neutral", 0.30
    m5=MA(hs_d,5,-1); m10=MA(hs_d,10,-1)
    pct=(hs_d[-1]["c"]-hs_d[-1]["o"])/max(0.001,hs_d[-1]["o"])*100
    rets=[(hs_d[j]["c"]-hs_d[j-1]["c"])/max(0.001,hs_d[j-1]["c"]) for j in range(max(1,len(hs_d)-20),len(hs_d))]
    vol=(sum((r-sum(rets)/max(1,len(rets)))**2 for r in rets)**0.5/max(1,len(rets))) if rets else 0
    if m5<m10 and pct<-0.5: ph="bear"
    elif m5>m10 and pct>0.5: ph="bull"
    elif vol>0.015: ph="hv"
    else: ph="neutral"
    pp={"bear":0.30,"bull":0.80,"hv":0.40,"neutral":0.30}.get(ph,0.30)
    return ph, pp

# v15.4：B=M5止盈20% + C=M6仅发酵期
# M1/M2/M3/M4/M5持仓和回撤不变
# C方案的"发酵期"=bull阶段（ph=="bull"）
SP={
    "M1":{"h":2,"tp":0.12,"sl":0.05,"tr":0.08,"p":0.80},  # v15.5修正：12%
    "M3":{"h":7,"tp":0.27,"sl":0.05,"tr":0.15,"p":0.65},  # v15.5修正：27%
    "M4":{"h":3,"tp":0.12,"sl":0.05,"tr":0.08,"p":0.55},  # v15.5修正：12%
    "M5":{"h":5,"tp":0.15,"sl":0.05,"tr":0.10,"p":0.45},  # v15.5修正：回退到最优15%
    # M6已删除
}

CAPITAL=100000.0; positions=[]; trades=[]

for i, dk in enumerate(q1):
    date=dk["d"]
    ph, frac = mkt_phase(date)
    pct=(dk["c"]-dk["o"])/max(0.001,dk["o"])*100
    extreme=pct<=-1.5; bull=pct>=1.0

    cands=[]
    for code, sd in D.items():
        ki=DI.get((code,date))
        if ki is None or ki<5: continue
        ks=sd["ks"]; k=ks[ki]; p=ks[ki-1] if ki>=1 else k
        vr=k["v"]/max(1,VOL(ks,5,ki))
        body=(k["c"]-k["o"])/max(0.001,k["o"])*100
        sl5=(k["c"]-ks[ki-4]["c"])/max(0.001,ks[ki-4]["c"])*100 if ki>=4 else 0
        ma5=MA(ks,5,ki); ma10=MA(ks,10,ki)
        ma5b=MA(ks,5,ki-1) if ki>=5 else ma5; ma10b=MA(ks,10,ki-1) if ki>=10 else ma10
        lu=k["c"]>=p["c"]*1.095
        was_lu=ki>=1 and ks[ki-1]["c"]>=ks[ki-2]["c"]*1.095

        # M1首板（不变）
        if extreme and lu and not was_lu and 1.2<=vr<=5.0:
            cands.append(("M1",code,sd["n"],k["c"],SP["M1"]))
        # M3整理（不变）
        if 2.5<=body<=10 and vr<0.90 and sl5>0:
            cands.append(("M3",code,sd["n"],k["c"],SP["M3"]))
        # M4恐慌（不变）
        if extreme and vr<0.80:
            cands.append(("M4",code,sd["n"],k["c"],SP["M4"]))
        # M5金叉（B方案：止盈20%）
        if ki>=5 and ma5b<=ma10b and ma5>ma10 and vr>0.9:
            if abs(k["c"]-MA(ks,20,ki))/MA(ks,20,ki)<5:
                cands.append(("M5",code,sd["n"],k["c"],SP["M5"]))
        # M6尾盘（C方案：仅bull阶段）
        if vr>1.4 and sl5>0 and body>1.5 and k["c"]>k["o"]:
            # C方案：只在ph=="bull"（发酵期）才做M6
            if ph == "bull":
                cands.append(("M6",code,sd["n"],k["c"],SP["M6"]))

    used=sum(pos["e"]*pos["s"] for pos in positions if pos["a"])
    cnt=sum(1 for pos in positions if pos["a"])
    mx={"bear":2,"bull":4,"hv":3,"neutral":3}.get(ph,3)
    cands.sort(key=lambda x:-x[4]["p"])
    for sig,code,n,p,sp in cands[:max(0,mx-cnt)]:
        af=min(sp["p"]*frac,(CAPITAL-used)/CAPITAL)
        if af<0.02: continue
        sz=int(CAPITAL*af/p/100)*100
        if sz<100: continue
        positions.append({"c":code,"n":n,"e":p,"s":sz,"ed":date,"ei":i,"h":p,"a":1,
                       "sig":sig,"sp":sp,"ph":ph})
        used+=p*sz; cnt+=1

    new_pos=[]
    for pos in positions:
        if not pos["a"]: continue
        sd=D.get(pos["c"],{})
        if not sd: continue
        tk=next((kk for kk in sd["ks"] if kk["d"]==date),None)
        if not tk: new_pos.append(pos); continue
        cur=tk["c"]; pnl=(cur-pos["e"])/pos["e"]
        pos["h"]=max(pos["h"],cur); held=i-pos["ei"]; sp=pos["sp"]
        ex=False; reason=""
        if pnl<=-sp["sl"]: ex=True; reason="止损"
        elif pnl>=sp["tp"]: ex=True; reason="止盈"
        elif (pos["h"]-cur)/pos["e"]>=sp["tr"] and pnl>0.03: ex=True; reason="回撤"
        elif held>=sp["h"] and pnl>0: ex=True; reason="到期"
        elif held>=sp["h"]*2: ex=True; reason="强退"
        if ex:
            py=(cur-pos["e"])*pos["s"]; CAPITAL+=py
            trades.append({"n":pos["n"],"sig":pos["sig"],"ed":pos["ed"],"ep":round(pos["e"],2),
                         "xd":date,"xp":round(cur,2),"pct":round(pnl*100,1),"y":round(py,0),"reason":reason,"hold":held,"ph":pos["ph"]})
        else: new_pos.append(pos)
    positions=new_pos

for pos in positions:
    if not pos["a"]: continue
    sd=D.get(pos["c"],{})
    if sd:
        tk=sd["ks"][-1]; cur=tk["c"]; pnl=(cur-pos["e"])/pos["e"]
        py=(cur-pos["e"])*pos["s"]; CAPITAL+=py
        held=len(q1)-1-pos["ei"]
        trades.append({"n":pos["n"],"sig":pos["sig"],"ed":pos["ed"],"ep":round(pos["e"],2),
                     "xd":tk["d"],"xp":round(cur,2),"pct":round(pnl*100,1),"y":round(py,0),"reason":"期末平仓","hold":held,"ph":pos["ph"]})

w=sum(1 for t in trades if t["y"]>0)
wr=w/max(1,len(trades))*100
ret=(CAPITAL-100000)/100000*100
dn=len(set(t["ed"] for t in trades))
dper=len(trades)/max(1,dn)
ms={}
for t in trades:
    ms.setdefault(t["sig"],{"c":0,"w":0,"p":0,"ph":set()})
    ms[t["sig"]]["c"]+=1; ms[t["sig"]]["p"]+=t["y"]
    ms[t["sig"]]["ph"].add(t["ph"])
    if t["y"]>0: ms[t["sig"]]["w"]+=1

print("="*60)
print("v15.4 验证结果 (B+C方案)")
print("="*60)
print(f"回测区间: {q1[0]['d']}~{q1[-1]['d']} ({len(q1)}天)")
print(f"沪深300: {bh_ref:+.1f}%")
print()
print(f"v15.4: {len(trades)}笔 胜{wr:.1f}% 总收益{ret:+.2f}% 超额{ret-bh_ref:+.2f}%")
print(f"期末: {CAPITAL:.0f}元 日均{dper:.1f}笔")
print()
print("信号分析:")
for sig in ["M1","M3","M4","M5","M6"]:
    if sig not in ms: continue
    st=ms[sig]; sp=SP[sig]
    wr_sig=st["w"]/max(1,st["c"])*100
    tag = "★" if sig=="M3" else ("[B]" if sig=="M5" else ("[C]" if sig=="M6" else ""))
    print(f"  {sig:<5} {tag} {st['c']:>3}笔 胜{wr_sig:>5.0f}% 累计{st['p']:>+8.0f}元 (持{sp['h']}天 止盈+{int(sp['tp']*100)}%)")
print()
print("前20笔明细:")
for idx,t in enumerate(trades[:20],1):
    tag = "★" if t["sig"]=="M3" else ("[B]" if t["sig"]=="M5" else ("[C]" if t["sig"]=="M6" else ""))
    print(f"  {idx:>3}. {t['n']:<8} {t['sig']:<5}{tag} {t['ed']} -> {t['xd']} {t['pct']:>+6.1f}% 持{t['hold']}天 {t['reason']}")
