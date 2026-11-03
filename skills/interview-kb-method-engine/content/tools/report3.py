#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pulse 动态求职洞察 — 从最新 cards 自动推导的“反直觉/趋势”结论区，随新面经归档后重跑即刷新。
用法: python main.py pulse   （或 python report3.py）
重点回答:
① 轮次口径总通过率（正编 vs 外包）是不是被拉高/拉低
② “业务全过但 offer=no”的场（非业务卡点）集中在哪——通常不是你能力问题，是横向/审批/横比
③ 你的“主场赛道”（正编高过率 <行业×岗位>）与“跨界一面挂”的重复告警
④ 趋势：前一半 vs 后一半卡的(轮次)通过率，看最近有没有进步/恶化
"""
import os, glob, re, sys
if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")
try:
    import yaml
except Exception:
    yaml=None
BASE=os.path.dirname(os.path.abspath(__file__))
try:
    from industry_taxonomy import classify, offer_flag, track_of_card
except Exception:
    def classify(text, fallback='其他'): return fallback
    def offer_flag(card): return ''
    def track_of_card(card, fallback='其他'): return fallback
CARDS=os.path.join(BASE,"..","cards")
DEFAULT_OUT=os.path.join(BASE,"..","求职动态洞察_pulse.md")
FROM_AOI=5  # 防伪要段数少时也够

# 赛道桶：**直接采用 industry_taxonomy 的赛道名**，不再自己分档。
#
# ⚠️ 旧版在这里写死了两段白名单：
#      if ind in ("硬件系内容/商店","电商/种草","内容/社区大厂","游戏/泛娱乐"): 原样保留
#      if ind in ("教育/医疗","汽车/出行","金融/财经","招聘/人力","AI/工具"): 塞进"中厂/新方向"
#    结果是：① 词表里后加的「出海/国际化」「用户增长」「B端/商家」等真实方向
#    全部掉进 "其他/未分类"；② 下游用它判断"跨界"，于是把这些**主流平台**
#    （某本地生活平台/某短视频平台/B站/字节/某OTA平台/百度…）当成跨界告警对象 —— 实测 33 张告警里
#    19 张是主流平台。③ 它把"生活服务/点评"改名成"生活服务/点评&旅企"，
#    又导致别的模块拿原名去比对时永远匹配不上。
#    现在一律返回词表里的赛道名，判不出才给"其他"。
#    此外走 track_of_card，让 config 的 card_track 强制指定也能生效。
def bucket(c):
    return track_of_card(c, fallback="其他")

def cmp_slug(c): return str(c.get("interview",{}).get("company","")).split("·")[0]
def outc(c):
    s=str((c.get("result") or {}).get("outcome") or "")
    if "pass" in s.lower(): return "pass"
    if "fail" in s.lower() or "挂" in s: return "fail"
    return "?"
def contract(c):
    blob=" ".join([cmp_slug(c),str(c.get("interview",{}).get("position","")),str((c.get("result") or {}).get("reason","")),str((c.get("interview",{}).get("nature","")))] )
    return "外包" in blob or "兼职" in blob
def no_offer(c):
    """最终没拿 offer 的原因。offer 归一走共享的 offer_flag。

    ⚠️ 旧写法对 YAML 布尔 `offer: False` 是死分支（str(False)=='False'），
    实测 40 张卡全落在这里。详见 industry_taxonomy.offer_flag。
    """
    r=c.get("result") or {}
    why=str(r.get("why_ended") or "").strip()
    if offer_flag(c)=="no" or why: return why or "offer=no"
    return ""

def load():
    if yaml is None: return []
    out=[]
    for p in sorted(glob.glob(os.path.join(CARDS,"I*.yaml"))):
        try: c=yaml.safe_load(open(p,encoding="utf-8"))
        except Exception: continue
        if isinstance(c,dict): c["_id"]=c.get("id"); out.append(c)
    # sort by numeric id for trend
    def nid(c):
        m=re.search(r'(\d+)',str(c.get("_id",""))); return int(m.group(1)) if m else 0
    out.sort(key=nid)
    return out

def main(out=DEFAULT_OUT):
    cards=load()
    marked=[c for c in cards if outc(c)!="?"]
    L=[]
    L.append("# 求职动态洞察（pulse）\n")
    L.append(f"> 由最新 {len(cards)} 张卡自动推导。**新面经归档后重跑本命令即刷新**：`python main.py pulse`\n")
    if not marked:
        print("(无已标记结果卡)"); return
    total=len(marked); tot_p=sum(1 for c in marked if outc(c)=="pass"); tot_f=total-tot_p
    L.append(f"## 0）总览（轮次口径）\n- 已标记 {total} 张 ｜ 通过轮 {tot_p} ｜ 未过轮 {tot_f} ｜ 轮次通过率 **{round(tot_p/max(total,1)*100,1)}%**\n")
    # 正编/外包
    from collections import defaultdict
    split=defaultdict(lambda:[0,0])
    for c in marked:
        o=outc(c); split["外包" if contract(c) else "正编(近似)"][0 if o=="pass" else 1]+=1
    L.append("### 1）正编 vs 外包 —— 别被假高通过骗\n| 属性 | 过 | 挂 | 通过率 |")
    L.append("|---|---|---|---|")
    for k,(p,f) in split.items():
        L.append(f"| {k} | {p} | {f} | {round(p/max(p+f,1)*100,1)}% |")
    L.append("")
    # 非业务卡点 pass-but-no-offer
    noff=[c for c in marked if outc(c)=="pass" and no_offer(c)]
    L.append("### 2）业务全过但 offer=no（横向/审批/无下文…）——不是能力问题，看浓度")
    if noff:
        for c in noff:
            L.append(f"- {c['_id']} {cmp_slug(c)} — {no_offer(c)}")
    else:
        L.append("-（当前无；新场请填 result.offer/why_ended 以纳入）")
    L.append("")
    # 主场赛道（正编）vs 跨界一面挂
    # ⚠️ 旧版把 "中厂/新方向" 和 "其他/未分类" 当作"跨界"的信号 ——
    #    但那两个桶是它自己硬编码白名单的副产品，不是语义上的"跨界"。
    #    于是某本地生活平台/某短视频平台/B站/字节/某OTA平台/百度 这些主流平台只要没命中它那 9 个词，
    #    就被打成"跨界，慎投"（实测 33 条告警里 19 条是主流平台）。
    #    现在按"该赛道历史通过率"判定主场，与 report_all/decision 口径一致；
    #    判不出赛道的（"其他"）不参与告警 —— 那是缺数据，不是跨界。
    buck=defaultdict(lambda:[0,0]); crosslist=[]
    for c in marked:
        if outc(c)=="pass" and contract(c): continue  # 只看正编
        b=bucket(c); o=outc(c)
        buck[b][0 if o=="pass" else 1]+=1
    # ⚠️ "主场"必须按**投放/面试量**定义，不能按通过率定义。
    #    第一版用"通过率 ≥40%"判主场，结果把 内容/社区大厂 排除了 ——
    #    它是你面试量最大的赛道（59 场，占正编口径约 46%），
    #    只是通过率 32.2%，于是该赛道 40 张 fail 全被打成"跨界"，
    #    连某短视频平台/B站/字节/某种草社区 这些绝对的主场公司都在告警名单里。
    #    "我在这里打得多"和"我在这里赢得多么"是两件事：
    #    前者是主场（判定跨界用），后者是优势（该投/慎投用）。
    #    这里要的是前者。
    total_marked = sum(p + f for p, f in buck.values()) or 1
    home = {b for b, (p, f) in buck.items()
            if (p + f) >= 3 and (p + f) / total_marked >= 0.05}   # 占面试量 ≥5%
    # 再补上通过率明显高的（哪怕量不大，也是你的舒适区）
    home |= {b for b, (p, f) in buck.items()
             if (p + f) >= 2 and p / max(p + f, 1) >= 0.4}
    # 只在**有足够样本**的赛道上谈跨界 —— 样本 1-2 的赛道通过率几乎必然
    # 是 0% 或 100%，拿它判"跨界"只会制造假告警。缺数据 ≠ 你跨界。
    known = {b for b, (p, f) in buck.items() if (p + f) >= 3}
    for c in marked:
        if outc(c)=="pass" and contract(c): continue
        b=bucket(c)
        if outc(c)=="fail" and b in known and b not in home:
            crosslist.append(f"{c['_id']} {cmp_slug(c)}")
    L.append("### 3）正编主场赛道（通过率排序）")
    L.append("| 赛道桶 | 过 | 挂 | 通过率 |")
    L.append("|---|---|---|---|")
    for b,(p,f) in sorted(buck.items(),key=lambda x:-(x[1][0]/max(sum(x[1]),1))):
        L.append(f"| {b} | {p} | {f} | {round(p/max(p+f,1)*100,1)}% |")
    L.append("")
    if crosslist:
        L.append("⚠️ 新方向/跨界一面挂重复告警：")
        L.append(",".join(crosslist))
        L.append("")
    # 趋势：前一半 vs 后一半
    half=max(1,len(marked)//2)
    A=marked[:half]; B=marked[half:]
    rA=lambda arr: round(sum(1 for c in arr if outc(c)=="pass")/max(len(arr),1)*100,1)
    L.append(f"### 4）趋势：前 {len(A)} 张 vs 后 {len(B)} 张 轮次通过率")
    L.append(f"- 前段（老面试）≈ **{rA(A)}%** ｜ 后段（最近）≈ **{rA(B)}%**")
    if rA(B)>rA(A)+5: L.append("- 📈 最近有进步")
    elif rA(B)<rA(A)-5: L.append("- 📉 最近偏低，注意是不是跨界/外包或后端卡多")
    else: L.append("- → 持平")
    L.append("\n> 说明：pass=该轮通过(轮次口径)。offer=no 请在新卡 result 里标 offer/no、why_ended/横向…，pulse 会自动把它归到第 ② 区。")
    with open(out,"w",encoding="utf-8") as f: f.write("\n".join(L))
    print("[OK] 已生成 pulse 洞察 →", out)

if __name__=="__main__":
    o=DEFAULT_OUT
    if "--out" in sys.argv: o=sys.argv[sys.argv.index("--out")+1]
    main(o)
