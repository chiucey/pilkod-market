#!/usr/bin/env python3
"""
涟漪止损监控 - urllib版
铁律: 止损-5% | 回撤-8% | 止盈+15% | 最大持仓15天
"""
import json, re, datetime, sys, urllib.request
from typing import List, Dict

HEADERS={"Referer":"https://finance.sina.com.cn","User-Agent":"Mozilla/5.0"}
SL=-0.05; DD=-0.08; TP=0.15; MAXD=15
POSITIONS=[{"code":"600036","name":"招商银行","shares":100,"cost":35.20,"date":"2026-03-25"},{"code":"000858","name":"五粮液","shares":50,"cost":145.80,"date":"2026-03-20"},{"code":"300750","name":"宁德时代","shares":30,"cost":220.50,"date":"2026-03-15"}]

def get(url,t=10):
    req=urllib.request.Request(url,headers=HEADERS)
    try:
        with urllib.request.urlopen(req,timeout=t) as r:
            return r.read().decode('gbk','replace')
    except: return None

def norm(c):
    c=c.strip().lower()
    return c if c.startswith(('sh','sz')) else (f"sh{c}" if c.startswith(('6','5')) else f"sz{c}")

def fetch_realtime(codes):
    if not codes: return {}
    raw=get(f"http://hq.sinajs.cn/list={','.join(codes)}")
    if not raw: return {}
    res={}
    for line in raw.strip().split('\n'):
        m=re.match(r'var hq_str_(\w+)="([^"]+)"',line)
        if not m: continue
        f=m.group(2).split(',')
        if len(f)<6: continue
        try: res[m.group(1)]={"name":f[0],"cur":float(f[3]),"high":float(f[4]),"low":float(f[5])}
        except: continue
    return res

def main():
    now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    print(f"\n{'='*55}\n🌊 涟漪止损监控 | {now.strftime('%Y-%m-%d %H:%M CST')}\n{'='*55}")
    codes=[norm(p["code"]) for p in POSITIONS]
    print(f"\n获取实时: {', '.join(codes)}...",end=" ",flush=True)
    rt=fetch_realtime(codes); print(f"✅ {len(rt)}只")
    total_pa=0.; total_cb=0.; urgent=[]; normal=[]
    for pos in POSITIONS:
        sc=norm(pos["code"]); d=rt.get(sc,{})
        cp=d.get("cur",pos["cost"]); ec=pos["cost"]; sh=pos["shares"]
        cb=ec*sh; cv=cp*sh; pa=cv-cb; pp=pa/cb
        total_pa+=pa; total_cb+=cb
        sigs=[]
        if pp>=TP: sigs.append(("止盈","目标达成","分批卖出1/3→1/3→1/3",False))
        if pp<=DD: sigs.append(("回撤止损","🔴强制清仓","清仓+系统检查",True))
        elif pp<=SL: sigs.append(("机械止损","🔴立即执行","立即止损不犹豫！",True))
        try:
            days=(now-datetime.datetime.strptime(pos["date"],"%Y-%m-%d")).days
            left=MAXD-days
            d_info=(f"到期⚠️","强制检视",left<=0) if left<=0 else (f"即将到期⏰",f"剩余{left}天",left<=3) if left<=3 else ("✅正常","持有观察",False)
        except: d_info=("?","日期错误",False)
        row={"code":pos["code"],"name":pos["name"],"shares":sh,"cost":ec,"cur":cp,"pnl_pct":pp*100,"pnl_abs":pa,"sigs":sigs,"days_info":d_info}
        if any(s[3] for s in sigs) or d_info[2]: urgent.append(row)
        else: normal.append(row)
    tp=total_pa/total_cb*100 if total_cb>0 else 0
    print(f"\n📊 汇总: 成本¥{total_cb:,.0f} | 市值¥{total_cb+total_pa:,.0f} | 盈亏{tp:+.2f}%")
    if urgent:
        print(f"\n🚨 紧急持仓 ({len(urgent)}个)")
        for p in urgent:
            print(f"  🔴 [{p['name']}({p['code']})] {p['pnl_pct']:+.1f}% | 持仓{p['days_info'][0]}")
            for s in p["sigs"]: print(f"     {s[1]} {s[0]}: {s[2]}")
    if normal:
        print(f"\n✅ 正常持仓 ({len(normal)}个)")
        for p in normal:
            action="可分批止盈" if p["pnl_pct"]>=TP*100 else ("⚠️关注止损" if p["pnl_pct"]<=SL*100 else "持有观察")
            print(f"  [{p['name']}({p['code']})] {p['pnl_pct']:+.1f}% | {p['days_info'][1]} | {action}")
    print(f"\n💡 铁律: 止损{SL*100:.0f}% | 回撤{DD*100:.0f}% | 止盈+{TP*100:.0f}% | 最大{MAXD}天")
    print(f"{'='*55}\n")
    print(json.dumps({"date":now.strftime("%Y-%m-%d"),"summary":{"cost":round(total_cb,2),"value":round(total_cb+total_pa,2),"pnl_pct":round(tp,2),"pnl_abs":round(total_pa,2)},"urgent":urgent,"normal":normal},ensure_ascii=False,indent=2))

if __name__=="__main__":
    try: main()
    except KeyboardInterrupt: print("\n[退出]")
    except Exception as e: print(f"[ERROR] {e}"); import traceback; traceback.print_exc()
