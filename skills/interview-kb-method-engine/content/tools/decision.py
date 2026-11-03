#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
decision.py — 一次生成两份“真正决策用”的浓缩报告：
A. 求职定位_v2.md（主战场/短板/非业务卡点/该投表/接下来 3 件事）
B. pulse_v2.md（最近 N 场 vs 全量/跨界告警/趋势）

用法: python decision.py [--recent 20]
"""
import os, glob, re, sys, argparse
if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")
try:
    import yaml
except Exception:
    yaml=None
BASE=os.path.dirname(os.path.abspath(__file__))
try:
    from industry_taxonomy import (classify, offer_flag, nature_of as _nature_of,
                                   is_first_round, blocker_hits, track_of_card)
except Exception:
    def classify(text, fallback='其他'): return fallback
    def offer_flag(card): return ''
    def _nature_of(card, default="正编"): return default
    def is_first_round(card): return False
    def blocker_hits(card): return []
    def track_of_card(card, fallback='其他'): return fallback
CARDS=os.path.join(BASE,"..","cards")
OUT1=os.path.join(BASE,"..","求职定位_v2.md")
OUT2=os.path.join(BASE,"..","pulse_v2.md")

# 通用 helpers (尽量与现有 scripts 同逻辑)
VALID_OUT={"pass","fail","no_offer","unknown","待确认",None,""}
CONTRACT_WORDS=("外包","兼职","实习")

def outcome(c):
    s=str((c.get("result") or {}).get("outcome") or "")
    if "pass" in s.lower(): return "pass"
    if "fail" in s.lower() or "挂" in s: return "fail"
    return "?"

def cmp(c):
    return str((c.get("interview") or {}).get("company",""))

def pos(c):
    return str((c.get("interview") or {}).get("position",""))



def nature(c):
    # 统一走共享的 nature_of（见 industry_taxonomy）。
    # 本模块关心的是"是否该排除出正编统计"，所以把外包/兼职/实习合并成"外包"口径。
    return "外包" if _nature_of(c) in ("外包", "兼职", "实习") else "正编"

def offer_no(c):
    """最终没拿 offer 的原因。offer 归一走共享的 offer_flag（见 industry_taxonomy）。

    ⚠️ 旧写法 `str(offer).lower().startswith("no")` 对 YAML 布尔 `offer: False`
    永远为假（str(False)=='False'），是死分支 —— 实测 40 张卡全落在这里，
    只是碰巧 why_ended 有值才没漏。详见 industry_taxonomy.offer_flag 的注释。
    """
    r=c.get("result") or {}
    why=str(r.get("why_ended") or "").strip()
    if offer_flag(c)=="no" or why: return why or "offer=no"
    return ""

def blocker_hint(c):
    rs=str((c.get("result") or {}).get("reason", "") or "")
    hits=[w for w in ["二面挂","二面老板","简历直接 pass","简历pass","老板 pass","外包无转正",
                       "无转正","职级","薪资","base","南京","回流","gap","家庭","二面被","卡薪资",
                       "横向对比","横比","审批流程不通过","审批不通过","无下文","年龄被拒","名额有限"]
          if w in rs]
    return ";".join(hits) if hits else ""

def nid(c):
    m=re.search(r'(\d+)',str(c.get("id",""))); return int(m.group(1)) if m else 0

def slug(c):
    return cmp(c).split("·")[0]

def weakness(c):
    return str((c.get("reflection") or {}).get("weakness","") or "")

def load():
    if yaml is None: return []
    out=[]
    for p in sorted(glob.glob(os.path.join(CARDS,"I*.yaml"))):
        try: c=yaml.safe_load(open(p,encoding="utf-8"))
        except Exception: continue
        if isinstance(c,dict): c["_id"]=c.get("id"); out.append(c)
    out.sort(key=nid)
    return out

# 赛道桶：**直接采用 industry_taxonomy 的赛道名**，不再自己分档。
#
# ⚠️ 旧版这里写死两段白名单（5 个"保留原名" + 5 个"塞进中厂/新方向"），
#    于是词表里后加的「出海/国际化」「用户增长」「B端/商家」等真实方向
#    全部掉进 "其他"。实测：与 report_all.bucket 有 **有相当比例不一致** ——
#    同一批卡，总报说"出海/国际化"，这份决策报告说"其他"。
#    这与之前 report3.py 修掉的是同一个病（封闭枚举 vs 开放词表）。
def bucket(c):
    # 走 track_of_card（而不是自己拼文本）：这样 config.yaml 里按卡号写的
    # `card_track` 强制指定才会在决策报告里生效。
    return track_of_card(c, fallback="其他")

def top_kw(words, n=8):
    from collections import Counter
    c=Counter(words); return c.most_common(n)

def main(recent=20):
    cards=load()
    marked=[c for c in cards if outcome(c)!="?"]
    # ===== A: 求职定位_v2 =====
    A=[]
    A.append("# 求职定位（浓缩决策版）\n")
    A.append(f"> 由 {len(cards)} 张卡（标记 {len(marked)}）自动推导。**正编口径为准，轮次口径=每卡1轮**。\n")
    # 0 总览
    total=len(marked); p=sum(1 for c in marked if outcome(c)=="pass"); fail=total-p
    A.append(f"## 0) 轮次通过率总览\n- 通过轮 {p} ｜ 未过轮 {fail} ｜ 轮次通过率 **{round(p/max(total,1)*100,1)}%**\n")

    # 1) 正编 vs 外包
    from collections import defaultdict
    split=defaultdict(lambda:[0,0])
    for c in marked: split[nature(c)][0 if outcome(c)=="pass" else 1]+=1
    A.append("## 1) 正编 vs 外包（别被假高通过骗）\n| 属性 | 过 | 挂 | 通过率 |\n|---|---|---|---|")
    for k,(pn,fn) in split.items(): A.append(f"| {k} | {pn} | {fn} | {round(pn/max(pn+fn,1)*100,1)}% |")
    A.append("")

    # 2) 主场赛道（正编口径 Top 8）
    buck=defaultdict(lambda:[0,0])
    for c in marked:
        if outcome(c)=="pass" and nature(c)=="外包": continue  # 纯正编
        b=bucket(c); buck[b][0 if outcome(c)=="pass" else 1]+=1
    A.append("## 2) 主场赛道（正编口径 Top 8）\n| 赛道 | 过 | 挂 | 通过率 |\n|---|---|---|---|")
    for b,(pn,fn) in sorted(buck.items(),key=lambda x:-(x[1][0]/max(sum(x[1]),1)))[:8]:
        A.append(f"| {b} | {pn} | {fn} | {round(pn/max(pn+fn,1)*100,1)}% |")
    A.append("")

    # 3) 反复挂根源（fail weakness 提关键词）
    # 走共享的 blocker_hits（最长优先/不重叠），与 report_all、diagnosis、
    # cross_analysis 同源 —— 原来这里是第四份互不相同的硬编码短词表（14 词）。
    weak_all=[]
    for c in marked:
        if outcome(c)!="fail": continue
        weak_all.extend(blocker_hits(c))
    top_weak=top_kw(weak_all)
    A.append("## 3) 反复挂根源（fail场 weakness 提频词 Top）")
    if top_weak:
        A.append("| 关键词 | 出现次数 |")
        A.append("|---|---|")
        for k,v in top_weak: A.append(f"| {k} | {v} |")
    else:
        A.append("- 样本不足或未填 weakness")
    A.append("")

    # 4) 非业务卡点（pass但 offer=no / 有 why_ended）
    noff=[c for c in marked if outcome(c)=="pass" and offer_no(c)]
    A.append("## 4) 业务全过但 offer=no（非能力卡点，重点看）\n")
    if noff:
        for c in noff: A.append(f"- {c['_id']} {slug(c)} · {pos(c)[:30]} — {offer_no(c)}")
    else:
        A.append("-（当前无，新面经请补 result.offer/why_ended）")
    A.append("")

    # 5) 该投/慎投/别投（正编口径，阈值 40%/20%/0%）
    bycomp={}
    for c in marked:
        if outcome(c)=="pass" and nature(c)=="外包": continue
        k=slug(c); bycomp.setdefault(k,[0,0]); bycomp[k][0 if outcome(c)=="pass" else 1]+=1
    good=[]; mid=[]; bad=[]
    for k,(pn,fn) in bycomp.items():
        tot=pn+fn; rate=pn/tot*100 if tot else 0
        if rate>=40 and tot>=2: good.append((k,pn,fn,round(rate,1)))
        elif rate>=20 or tot<2: mid.append((k,pn,fn,round(rate,1)))
        else: bad.append((k,pn,fn,round(rate,1)))
    A.append("## 5) 该投 / 慎投 / 别投（正编口径，阈值 40%/20%/0%，且样本≥2）\n")
    A.append("✅ 该投（通过率 ≥ 40%）")
    for k,pn,fn,r in sorted(good,key=lambda x:-x[3])[:12]: A.append(f"- {k}（{r}%，{pn}/{pn+fn}）")
    A.append("")
    A.append("⚠️ 慎投（通过率 20%-40% 或样本不足）")
    for k,pn,fn,r in sorted(mid,key=lambda x:-x[3])[:12]: A.append(f"- {k}（{r}%，{pn}/{pn+fn}）")
    A.append("")
    A.append("🚫 别投（通过率 < 20% 且 ≥ 2 场）")
    for k,pn,fn,r in sorted(bad,key=lambda x:x[3])[:12]: A.append(f"- {k}（{r}%，{pn}/{pn+fn}）")
    A.append("")

    # 6) 接下来 2 周最该做的 3 件事（动态推导）
    acts=[]
    if good:
        # ⚠️ 这里原来写的是 good[0][0] —— 而 good 是**按字典插入顺序**建的
        #    （见上面 for c in marked 的构建处），根本没有排序。
        #    于是"通过率最高"实际等于"卡文件里最先出现的那家公司"。
        #    实测：报告印出"你在 某大厂 等地通过率最高"，而同一份报告下面
        #    排好序的表里 某招聘社区/饭团/某内容平台/昆仑万维 都是 100%、某大厂只有 83.3%。
        #    必须显式按通过率排序，并在并列时优先样本量大的（更可信）。
        ranked = sorted(good, key=lambda x: (-x[3], -(x[1] + x[2])))
        top_rate = ranked[0][3]
        # 只把**真的达到最高档**的公司列出来，避免"最高"其实跟别人一样
        names = [k for k, pn, fn, r in ranked if r == top_rate]
        shown = "、".join(names[:3])
        acts.append(
            f"主攻正编主流大厂内容/垂类（通过率最高的是 {shown}，{top_rate}%），少投跨界新行业")
    if top_weak: acts.append(f"优先解决“{top_weak[0][0]}”这个 fail 场最高频短板（{top_weak[0][1]} 次）")
    if noff: acts.append(f"对已标“业务全过但 offer=no”的 {len(noff)} 场复盘：整理非业务卡点话术/找别的相似但 HC 稳的公司")
    if not acts: acts=["先补 5-10 场已知结果面经到卡里 → 再重跑 decision 拿真实定位"]
    A.append("## 6) 接下来 2 周最该做的 3 件事\n")
    for i,a in enumerate(acts[:3],1): A.append(f"{i}. {a}")
    A.append("")
    with open(OUT1,"w",encoding="utf-8") as outA: outA.write("\n".join(A))

    # ===== B: pulse_v2 =====
    B=[]
    B.append("# 求职脉搏（动态趋势版）\n")
    B.append(f"> 新面经归档后 `python main.py decision` 重跑即刷新。默认看最近 {recent} 场趋势 vs 全量。\n")

    # 0 总览（轮次口径）
    B.append(f"## 0) 轮次通过率（全量）\n- 通过轮 {p} ｜ 未过轮 {fail} ｜ 通过率 **{round(p/max(total,1)*100,1)}%**\n")

    # 1) 正编 vs 外包
    B.append("## 1) 正编 vs 外包\n| 属性 | 过 | 挂 | 通过率 |\n|---|---|---|---|")
    for k,(pn,fn) in split.items(): B.append(f"| {k} | {pn} | {fn} | {round(pn/max(pn+fn,1)*100,1)}% |")
    B.append("")

    # 2) 趋势：最近 N 场 vs 之前的
    if len(marked)>=10:
        recent_cards=marked[-min(recent,len(marked)):]
        old_cards=marked[:-min(recent,len(marked))] if len(marked)>recent else []
        rp=sum(1 for c in recent_cards if outcome(c)=="pass"); rf=len(recent_cards)-rp
        op=sum(1 for c in old_cards if outcome(c)=="pass"); of_=len(old_cards)-op
        B.append(f"## 2) 趋势：最近 {len(recent_cards)} 场 vs 之前的 {len(old_cards)} 场（轮次口径）")
        B.append(f"- 最近：{rp}/{len(recent_cards)} = {round(rp/max(len(recent_cards),1)*100,1)}%")
        if old_cards: B.append(f"- 之前：{op}/{len(old_cards)} = {round(op/max(len(old_cards),1)*100,1)}%")
        if rp/max(len(recent_cards),1)*100 > op/max(len(old_cards),1)*100 + 5:
            B.append("- 📈 最近有进步（至少 +5pp）")
        elif rp/max(len(recent_cards),1)*100 < op/max(len(old_cards),1)*100 - 5:
            B.append("- 📉 最近偏低，注意是否跨界/外包太多")
        else:
            B.append("- → 基本持平（±5pp 内）")
        B.append("")

    # 3) 跨界一面挂 top 告警
    cross_one=[]
    for c in marked:
        # ⚠️ 这里原来是**枚举白名单**比对 round 字段，而该字段是自由文本
        #    （真实数据 58 种写法）。实测 87 张 fail 卡只命中 49 张，
        #    38 张被静默丢弃；白名单里是全角"一面（业务面）"，
        #    数据里却有半角"一面(业务)"——一个括号宽度差异就废掉整条规则。
        #    改为解析轮次语义（is_first_round），全角/半角/中文数字都能认。
        #    同时排除"其他"桶：那是判不出赛道的兜底，不是一类机会。
        #    ⚠️ 原来还排除了 ("生活服务/点评","内容/社区大厂")，但这两个内置
        #    赛道已被用户删除（泛内容类收敛为「内容运营」），保留它们只会
        #    让读者以为还存在这两个桶。现只排除真正的兜底「其他」。
        if (outcome(c)=="fail" and is_first_round(c)
                and bucket(c) not in ("其他",)):
            cross_one.append(f"{c['_id']} {slug(c)}")
    if cross_one:
        B.append("## 3) 跨界/新方向一面挂 top 告警（多为一面即挂，慎投）\n")
        B.append(", ".join(cross_one[:30]) + ("…" if len(cross_one)>30 else ""))
        B.append("")

    # 4) pass但offer=no最新
    noff2=noff[-12:] if noff else []
    B.append("## 4) pass 但 offer=no（最新 12 张）\n")
    if noff2:
        for c in noff2: B.append(f"- {c['_id']} {slug(c)} · {pos(c)[:35]} — {offer_no(c)}")
    else:
        B.append("-（无）")
    B.append("\n> `result.offer/why_ended` 填好后这里会自动体现，持续迭代即可。\n")

    with open(OUT2,"w",encoding="utf-8") as outB: outB.write("\n".join(B))
    print(f"[OK] 已生成 ① {OUT1}  ② {OUT2}")

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--recent",type=int,default=20)
    a=p.parse_args(); main(a.recent)
