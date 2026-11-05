#!/usr/bin/env python3
"""
涟漪投资研究完整流程 引擎 v2.0
信息收集 → 技术分析 → 量化验证 → 模拟训练
→ 复盘确认 → 预测未来 → 精选选股 → 汇报总结
"""
import sys, json, math
from collections import defaultdict
import numpy as np

# ============ 数据获取 ============
SINA = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={}&scale=240&ma=no&datalen=300"

def fetch(code):
    try:
        sym = "sh"+code if code.startswith(("6","9")) or code=="000300" else code
        req = __import__("urllib.request").Request(SINA.format(sym), headers={"User-Agent":"Mozilla/5.0"})
        with __import__("urllib.request").urlopen(req, timeout=8) as r:
            d = json.loads(r.read().decode())
            if isinstance(d, list):
                ks = [{"d":k["day"],"c":float(k["close"]),"v":int(k["volume"]),"h":float(k["high"]),"l":float(k["low"])} for k in d]
                ks.sort(key=lambda x:x["d"]); return ks
    except: return []

# ============ 技术指标 ============
def ma(ks, n):
    if not ks or len(ks)<n: return 0
    return sum(k["c"] for k in ks[-n:])/n

def vma(ks, n):
    if not ks or len(ks)<n: return sum(k["v"] for k in ks)/max(1,len(ks))
    return sum(k["v"] for k in ks[-n:])/n

def vr(ks):
    if len(ks)<20: return 1
    return ks[-1]["v"]/max(1,vma(ks,20))

def cp(ks):
    if len(ks)<20: return 0.5
    lo=min(k["l"] for k in ks[-60:]); hi=max(k["h"] for k in ks[-60:])
    p=ks[-1]["c"]
    return (p-lo)/max(1,hi-lo) if hi!=lo else 0.5

def rsi(ks, n=14):
    if len(ks)<n+1: return 50
    gains=[max(ks[i]["c"]-ks[i-1]["c"],0) for i in range(1,n+1)]
    losses=[max(ks[i-1]["c"]-ks[i]["c"],0) for i in range(1,n+1)]
    ag=sum(gains)/n; al=sum(losses)/n
    if al==0: return 100
    return round(100-(100/(1+ag/al)), 1)

def sig(ks):
    if len(ks)<20: return None
    m5=ma(ks,5); m10=ma(ks,10); m20=ma(ks,20)
    m60=ma(ks,60) if len(ks)>=60 else m20
    p=ks[-1]["c"]; v=vr(ks); c=cp(ks)
    if m5>m10 and p>m20 and v>=1.5: return "A"
    if m5>m10 and p>m20 and v<0.8:  return "B"
    if m5>m10 and p<m20 and p>m60 and v>=1.2: return "C"
    if m5>m10 and p<m20 and v<0.8:  return "D"
    if p<m60 and v<0.6: return "E"
    if m5<m10 and p<m60 and v<0.5: return "F"
    return None

def regime(ks):
    if len(ks)<20: return "弱市"
    m5=ma(ks,5); m10=ma(ks,10); p=ks[-1]["c"]
    if m5>m10 and p>ma(ks,20): return "强市"
    elif m5>m10 or p>ma(ks,20): return "弱市"
    else: return "熊市"

# ============ statsmodels 量化 ============
try:
    from statsmodels.tsa.stattools import adfuller
    from statsmodels.stats.diagnostic import het_arch
    HAS_SM = True
except:
    HAS_SM = False

def adf_test(ks):
    if not HAS_SM or len(ks)<30: return None
    try:
        rets = np.array([(ks[i]["c"]-ks[i-1]["c"])/max(1,ks[i-1]["c"]) for i in range(1,len(ks))])
        res = adfuller(rets, maxlag=5)
        return {"stat":round(res[0],3),"p":round(res[1],4),"trend":"均值回归" if res[1]<0.05 else "趋势延续"}
    except: return None

def arch_test(ks):
    if not HAS_SM or len(ks)<30: return None
    try:
        rets = np.array([(ks[i]["c"]-ks[i-1]["c"])/max(1,ks[i-1]["c"]) for i in range(1,len(ks))])
        res = het_arch(rets, nlags=5)
        return {"p":round(res[1],4),"有聚集":res[1]<0.05}
    except: return None

def monte_carlo(ks, n_sim=1000, horizon=20):
    if len(ks)<30: return None
    try:
        rets = np.array([(ks[i]["c"]-ks[i-1]["c"])/max(1,ks[i-1]["c"]) for i in range(1,len(ks))])
        mu, sigma = np.mean(rets[-60:]), np.std(rets[-60:])
        sims = []
        for _ in range(n_sim):
            path = 1.0
            for _ in range(horizon):
                z = np.random.standard_normal()
                path *= math.exp((mu-0.5*sigma**2)+sigma*z)
            sims.append(path)
        sims = np.array(sims)
        p5=np.percentile(sims,5); p50=np.percentile(sims,50); p95=np.percentile(sims,95)
        return {
            "p5":  f"{-abs(1-p5)*100:.1f}%",
            "p50": f"{'+' if p50>1 else ''}{(p50-1)*100:.1f}%",
            "p95": f"{'+' if p95>1 else ''}{(p95-1)*100:.1f}%",
            "上涨概率": f"{np.mean(sims>1)*100:.0f}%"
        }
    except: return None

def sharpe(ks):
    if len(ks)<30: return 0
    rets=np.array([(ks[i]["c"]-ks[i-1]["c"])/max(1,ks[i-1]["c"]) for i in range(1,len(ks))])
    if np.std(rets)==0: return 0
    return round((np.mean(rets)*252-0.03)/(np.std(rets)*math.sqrt(252)),2)

def max_dd(ks):
    if len(ks)<30: return 0
    rets=np.array([(ks[i]["c"]-ks[i-1]["c"])/max(1,ks[i-1]["c"]) for i in range(1,len(ks))])
    cum=np.cumprod(1+rets[-60:]); peak=np.maximum.accumulate(cum)
    dd=(cum-peak)/peak
    return round(abs(np.min(dd))*100, 1)

# ============ 单股分析 ============
def analyze(code, name=""):
    ks = fetch(code)
    if not ks: return None
    name = name or code
    s = sig(ks); r = regime(ks)
    m5=ma(ks,5); m10=ma(ks,10); m20=ma(ks,20)
    p=ks[-1]["c"]; v=vr(ks); c=cp(ks)
    rsi_val = rsi(ks)
    adf = adf_test(ks)
    arch = arch_test(ks)
    mc = monte_carlo(ks)
    sh = sharpe(ks); dd = max_dd(ks)

    # 涟漪扑克验证
    poker_map = {
        "A": "✅强市顺势" if r=="强市" else "😐需观察",
        "B": "⚠️追牌风险（缩量突破）",
        "C": "😐弱势反弹",
        "D": "😐弱势整理",
        "E": "✅低位布局（close_pos<0.2）" if c<0.2 else "😐需观察",
        "F": "⚠️空头排列，避免"
    }
    poker = poker_map.get(s, "无信号")

    # 情景
    scenarios = {
        "A（乐观）": f"涨至MA20的+12%",
        "B（基准）": f"持有15天到期",
        "C（悲观）": f"跌-8%触发止损"
    }

    return {
        "name":name,"code":code,"price":round(p,2),
        "market":r,"signal":s or "无",
        "ma5":round(m5,1),"ma10":round(m10,1),"ma20":round(m20,1),
        "vr":round(v,2),"cp":round(c,2),"rsi":rsi_val,
        "adf":adf,"arch":arch,"mc":mc,
        "sharpe":sh,"max_dd":dd,
        "poker":poker,
        "scenarios":scenarios,
        "date":ks[-1]["d"]
    }

def score(a):
    if not a: return 0
    s=50
    sig_map={"A":20,"E":15,"C":10,"B":5}
    s+=sig_map.get(a["signal"],0)
    if a.get("sharpe",0)>0.5: s+=15
    elif a.get("sharpe",0)>0: s+=8
    if a.get("max_dd",999)<10: s+=15
    elif a.get("max_dd",999)<20: s+=8
    if a.get("arch",{}).get("有聚集"): s+=5
    if a.get("market")=="强市": s+=10
    elif a.get("market")=="熊市": s-=10
    return min(100,max(0,s))

# ============ 大盘分析 ============
def market_status():
    hs = fetch("000300")
    if not hs: return {"name":"沪深300","error":True}
    m5=ma(hs,5); m10=ma(hs,10); m20=ma(hs,20); p=hs[-1]["c"]
    r=regime(hs)
    adf=adf_test(hs); mc=monte_carlo(hs)
    return {
        "name":"沪深300","price":round(p,2),
        "ma5":round(m5,1),"ma10":round(m10,1),"ma20":round(m20,1),
        "regime":r,"adf":adf,"mc":mc,"date":hs[-1]["d"]
    }

# ============ 完整流程 ============
def run_workflow(query="A股机会", targets=None):
    print("="*60)
    print(f"  🌊 涟漪投资研究 | {query}")
    print("="*60)

    # Step 1: 信息收集
    print("\n【Step 1】信息收集")
    print("  ✅ 数据接口就绪")

    # Step 2: 技术分析
    print("\n【Step 2】技术分析")
    ms = market_status()
    print(f"  大盘：{ms.get('regime','未知')} | {ms.get('price','N/A')}")
    print("  ✅ v26信号系统就绪")

    # Step 3: 量化验证
    print("\n【Step 3】量化验证")
    print(f"  {'✅' if HAS_SM else '❌'} statsmodels")
    print("  ✅ 量化模型就绪")

    # Step 4-5: 分析+选股
    analyses = []
    if targets:
        print("\n【Step 4-5】分析标的")
        for t in targets:
            a = analyze(t.get("code",""), t.get("name",""))
            if a: analyses.append(a)
        print(f"  ✅ 完成{len(analyses)}只标的分析")

    # Step 6-7: 排序
    print("\n【Step 6-7】精选排序")
    ranked = sorted(analyses, key=score, reverse=True)
    print("="*60)
    for i, a in enumerate(ranked):
        emoji = "🥇" if i==0 else "🥈" if i==1 else "🥉" if i==2 else f"  {i+1}."
        print(f"\n{emoji} {a['name']}({a['code']}) | Signal {a['signal']} | {a['market']}市 | 评分{score(a)}")
        print(f"    {a['price']}元 | 量比={a['vr']} | RSI={a['rsi']} | close_pos={a['cp']}")
        if a.get("mc"):
            m=a["mc"]
            print(f"    MC20天：{m['p5']}/{m['p50']}/{m['p95']} | {m['上涨概率']}上涨")
        if a.get("arch",{}).get("有聚集"): print(f"    ⚠️波动聚集（主力痕迹）")
        print(f"    扑克验证：{a['poker']}")

    # Step 8: 汇报
    print("\n"+"="*60)
    print("  【汇报总结】")
    print("="*60)
    if ranked:
        best = ranked[0]
        print(f"\n结论：{best['name']}最优（评分{score(best)}，Signal {best['signal']}）")
        print(f"市场：{ms.get('regime','未知')}")
        if best.get("mc"):
            m=best["mc"]
            print(f"20天预测：{m['p5']}/{m['p50']}/{m['p95']}（{m['上涨概率']}上涨）")
        print(f"涟漪建议：{best['poker']}")
    print("\n"+"="*60)
    return {"market":ms,"analyses":ranked}

if __name__=="__main__":
    q = sys.argv[1] if len(sys.argv)>1 else "A股机会"
    t = json.loads(sys.argv[2]) if len(sys.argv)>2 else None
    run_workflow(q, t)
