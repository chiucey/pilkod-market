#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""report2.py — 按【轮次口径】与【正编/外包】拆分求职通过率，输出一份补充定位报告。

说明（口径）：
- 轮次口径通过率 = outcome=pass 的轮次卡数 /（pass+fail 的轮次卡数）。
  （一张卡记一轮。同一流程的多轮若分别建卡，会自然合成分子分母。）
- 正编/外包：以 interview.nature 或公司/岗位/reason 含“外包”为外包，否则默认按正编口径近似。
- “非业务卡点”：reason 里含 二面挂/老板/简历pass/外包无转正/薪资/base/回流/gap 等信号，虽 pass 但最终未必 offer —— 单独列出警示。

用法: python report2.py [--out 路径]
"""
import os, glob, re, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
try:
    import yaml
except Exception:
    yaml = None

try:
    from industry_taxonomy import offer_flag, nature_of as _nature_of
except Exception:
    def offer_flag(card): return ''
    def _nature_of(card, default="正编"): return default

BASE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(BASE, "..", "cards")
DEFAULT_OUT = os.path.join(BASE, "..", "求职定位报告_轮次正编.md")

def outcome_of(c):
    try:
        s = str((c.get("result") or {}).get("outcome") or "")
    except Exception:
        s = ""
    if "pass" in s.lower(): return "pass"
    if "fail" in s.lower() or "挂" in s: return "fail"
    return "unknown"

def nature_of(c):
    """用工性质。统一走共享的 nature_of（见 industry_taxonomy）。

    ⚠️ 旧版只认"正编/正式/外包"，遇到真实数据里的 `nature: 兼职`
    会返回第四种值 "未知nature"，于是在报表里冒出一行
    `| 未知nature | 0 | 1 | 0.0% |` —— 典型的"封闭集合吞掉新类别"。
    现在兼职/实习都各自归位。
    """
    return _nature_of(c)

def blocker_hint(c):
    rs = str((c.get("result") or {}).get("reason", "") or "")
    hits = [w for w in ["二面挂","二面老板","简历直接 pass","简历pass","老板 pass","外包无转正",
                         "无转正","职级","薪资","base","南京","回流","gap","家庭","二面被","卡薪资"]
            if w in rs]
    return ";".join(hits) if hits else ""

def norm_company(c):
    try:
        return str(c.get("interview").get("company", ""))
    except Exception:
        return "?"

def load():
    out=[]
    if yaml is None: return out
    for p in sorted(glob.glob(os.path.join(CARDS,"I*.yaml"))):
        try: c=yaml.safe_load(open(p,encoding="utf-8"))
        except Exception: continue
        if isinstance(c,dict): c["_id"]=c.get("id"); out.append(c)
    return out

def build(cards):
    L=[]
    L.append("# 求职定位（轮次口径 / 正编外包拆分）\n")
    marked=[c for c in cards if outcome_of(c)!="unknown"]
    n_all=len(cards); n_mark=len(marked)
    p=sum(1 for c in marked if outcome_of(c)=="pass"); f=n_mark-p
    L.append(f"> 基于 {n_all} 张卡（已标记 {n_mark}）｜ 轮次通过率 = 通过轮次/总轮次 = **{p}/{n_mark} = {round(p/max(n_mark,1)*100,1)}%**  (每张卡=该场某一轮)\n")
    L.append("> 例:面两岗(一岗二面挂=含一轮过,一岗一面挂) → 过1/总3 = 33%。本表把每张有 outcome 的卡当 1 轮。\n")

    # 1) 正编/外包分开
    from collections import defaultdict
    bynat=defaultdict(lambda:{"pass":0,"fail":0,"cards":[]})
    for c in marked:
        nt=nature_of(c); o=outcome_of(c)
        bynat[nt]["pass" if o=="pass" else "fail"]+=1
        bynat[nt]["cards"].append((c["_id"], norm_company(c)))
    L.append("## 1) 按岗位属性（正编 vs 外包）轮次通过率\n")
    L.append("| 属性 | 通过轮 | 挂轮 | 通过率 |")
    L.append("|---|---|---|---|")
    for nt,st in sorted(bynat.items(), key=lambda x:- (x[1]["pass"]/(x[1]["pass"]+x[1]["fail"]) if (x[1]["pass"]+x[1]["fail"]) else -1)):
        pn,fn=st["pass"],st["fail"]; tot=pn+fn
        L.append(f"| {nt} | {pn} | {fn} | {round(pn/max(tot,1)*100,1)}% |")
    L.append("")
    L.append("> ⚠️ 外包通过率往往偏高但 offer 性价比/转正存疑；建议以【正编】通过率衡量真实主战场。\n" )

    # 2) 按公司正编口径 (排除外包)
    bycomp=defaultdict(lambda:{"pass":0,"fail":0})
    for c in marked:
        if nature_of(c).startswith("外包"): continue
        o=outcome_of(c); comp=norm_company(c).split('·')[0]
        bycomp[comp]["pass" if o=="pass" else "fail"]+=1
    L.append("## 2) 优势公司（正编口径通过率）\n")
    L.append("| 公司 | 通过 | 挂 | 通过率 |")
    L.append("|---|---|---|---|")
    for comp,st in sorted(bycomp.items(),key=lambda x:- (x[1]["pass"]/(x[1]["pass"]+x[1]["fail"]) if (x[1]["pass"]+x[1]["fail"]) else -1)):
        pn,fn=st["pass"],st["fail"];L.append(f"| {comp} | {pn} | {fn} | {round(pn/max(pn+fn,1)*100,1)}% |")
    L.append("")

    # 3) pass 但实际可能无 offer（非业务卡点）——优先看结构化 offer/why_ended，其次 reason 关键词
    # ⚠️ offer 判定走共享的 offer_flag：YAML 布尔 `offer: False` 用
    #    str().startswith("no") 永远匹配不上（str(False)=='False'），
    #    实测 40 张卡全落在这个死分支里。详见 industry_taxonomy.offer_flag。
    risk=[]
    for c in marked:
        if outcome_of(c) != "pass": continue
        res = c.get("result") or {}
        why = str(res.get("why_ended") or "").strip()
        is_no = offer_flag(c) == "no"
        if blocker_hint(c) or is_no or why:
            note = blocker_hint(c) or (why if why else ("offer=no" if is_no else "n/a"))
            risk.append((c, note))
    L.append("## 3) 标 pass 但 offer=no / 含非业务卡点（业务过了≠拿到 offer）\n")
    if risk:
        for c, note in risk:
            L.append(f"- {c['_id']} {norm_company(c)} — {note}")
    else:
        L.append("-（无）\n")
    return "\n".join(L)

def main():
    out=DEFAULT_OUT
    if "--out" in sys.argv: out=sys.argv[sys.argv.index("--out")+1]
    rep=build(load())
    with open(out,"w",encoding="utf-8") as f: f.write(rep)
    print("[OK] 已生成 →", out)

if __name__=="__main__":
    main()
