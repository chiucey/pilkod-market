#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# report_all.py — 生成唯一《求职总报》，合并定位/诊断/痛点/趋势为一份持续更新的全局总报。
# 用法: python main.py report
import os, glob, re, sys, argparse
from datetime import date as _d
if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")
try:
    import yaml
except Exception:
    yaml=None
BASE=os.path.dirname(os.path.abspath(__file__))
try:
    from industry_taxonomy import (classify, scale_of, main_tracks,
                                   blocker_keywords, offer_flag, is_first_round,
                                   track_of_card, SCALE_TIERS)
except Exception:
    def classify(text, fallback='其他'): return fallback
    def scale_of(company, explicit=''): return ''
    def main_tracks(): return []
    def blocker_keywords(): return []
    def offer_flag(card): return ''
    def is_first_round(card): return False
    def track_of_card(card, fallback='其他'): return fallback
    SCALE_TIERS=["大厂","中厂","小厂","创业团队"]
CARDS=os.path.join(BASE,"..","cards")
OUT=os.path.join(BASE,"..","求职总报.md")

CONTRACT_WORDS=("外包","兼职","实习")

# 「挂了但原因不是当场表现」的识别关键词（report 第 4b 节用）。
#
# ⚠️ 定义在**模块级**而不是 main() 内部 —— 放函数里的话 validate 的自检
#    没法 import 它来锁住行为（实测踩到：from report_all import _NONCAP_KW 报
#    ImportError）。凡是被别处引用/需要被自检覆盖的常量，都该放模块级。
#
# 用途：区分"我答得不好"和"他们要的人不是我这类"。两者改进方向完全不同 ——
#   前者要练表达/补知识，后者要换投递方向或等 HC。混在一起会让人
#   把自己的方向问题误当成能力短板。
_NONCAP_KW = ["非能力", "匹配", "能力缺口", "能力组合", "无hc", "没hc", "hc",
              "编制", "名额", "审批", "横向", "横比", "内部", "回流",
              "薪资", "职级", "base", "地域", "headcount"]

# 挂因关键词默认表。
#
# ⚠️ 这里**不再是**自己的一份词表（V3.7 修）。
#    原来本文件写了 28 个词的 DEFAULT_BLOCKER_KW，而 industry_taxonomy 里
#    另有一份 77 词的 DEFAULT_BLOCKER_KEYWORDS —— 两份长期漂移：
#    实测 **21 张卡**能被 77 词表命中、却对 28 词表不可见
#    （如「方法论」「审批」「表达」「没做过」）。
#    当 config.yaml 没写 blocker_keywords 时，report_all 会退回那 28 词，
#    于是**新用户**看到的"反复挂根源"比实际少 21 场。
#
#    现在统一：config 优先 → 其次是共享的内置表（从 industry_taxonomy 取）。
#    这样两边永远不会再漂，且老环境（config 有值）行为完全不变。
def _default_blocker_kw():
    """共享的挂因词表（来自 industry_taxonomy，config 会并进去）。"""
    try:
        return list(blocker_keywords())
    except Exception:
        return []

def outcome(c): s=str((c.get("result") or {}).get("outcome") or ""); return "pass" if "pass" in s.lower() else ("fail" if ("fail" in s.lower() or "挂" in s) else "?")
def cmp(c): return str((c.get("interview") or {}).get("company",""))
def pos(c): return str((c.get("interview") or {}).get("position",""))
def offer_no(c):
    """最终没拿到 offer 的原因（优先用 why_ended 原文）。offer 归一逻辑见 industry_taxonomy.offer_flag。"""
    r=c.get("result") or {}; why=str(r.get("why_ended") or "").strip()
    return (why or ("offer=no" if offer_flag(c)=="no" else ""))
def blocker_hint(c):
    rs=str((c.get("result") or {}).get("reason","") or "")
    hits=[w for w in ["横向对比","横比","审批流程不通过","审批不通过","无下文","年龄被拒","简历直接 pass","简历pass","老板 pass","无转正","职级","回流","南京","外包","卡薪资","名额有限","HR 后无正文"] if w in rs]
    return ";".join(hits) if hits else ""
def nature(c):
    iv=c.get("interview") or {}; n=str(iv.get("nature") or "").strip().lower()
    if n in ("正编","正式","全职"): return "正编"
    if "外包" in n: return "外包"
    if "兼职" in n: return "兼职"
    if "实习" in n: return "实习"
    # n 为空或未知 → 文本启发(仅 serve 兜底)
    blob=" ".join([cmp(c),pos(c),str((c.get("result") or {}).get("reason",""))])
    low=blob.lower()
    if "外包" in low: return "外包"
    if "兼职" in low: return "兼职"
    if "实习" in low: return "实习"
    return "正编"
def slug(c): return cmp(c).split("·")[0]
def scale(c):
    """卡的体量档位：卡里 interview.company_scale 优先，其次 config.company_scale，认不出返回 ''。"""
    return scale_of(cmp(c), str((c.get("interview") or {}).get("company_scale","") or ""))
def weakness(c): return str((c.get("reflection") or {}).get("weakness","") or "")
def blocker_hits(c):
    """从 weakness 里抽出挂因关键词，**最长优先且不重叠**。

    返回去重后的列表（按出现顺序）。改自旧版逐词 in 判断：
    旧版 "行业gap" 会被拆成 "行业"+"gap" 两条，且 "gap" 单独成格看不到是哪种 gap。
    """
    w = weakness(c).lower()
    # config 优先；没配时用**共享**内置表（不再用本文件自己那份，见上方注释）
    kws = blocker_keywords() or _default_blocker_kw()
    kws = sorted(set(str(k).lower() for k in kws if str(k).strip()),
                 key=len, reverse=True)
    hits, consumed = [], w
    for k in kws:
        if k and k in consumed:
            hits.append(k)
            consumed = consumed.replace(k, "\u0000" * len(k))  # 占位，防短词重复命中
    return hits
def bucket(c):
    """把一张卡归到一个赛道桶。

    ⚠️ 不要硬编码赛道白名单 —— 之前这里写死了 5 个赛道名，
    其余全部塞进「中厂/新方向」。结果：词表里后加的「出海/国际化」
    「用户增长」「B端/商家」等真实方向全被吞掉，报表上看不出它们。
    现在改为：**词表里有什么赛道，就按什么赛道统计**，
    只把真正判不出来的单独留一个「其他」桶。

    ⚠️ 走 `track_of_card` 而不是自己拼文本 —— 那样 config.yaml 里
    按卡号写的 `card_track` 强制指定才会在报表里生效。
    （否则"我手动指定了但报表没变"，正是本会话踩过的坑。）
    """
    ind = track_of_card(c, fallback="其他")
    if not ind or ind in ("其他", "其他/未分类"):
        return "其他"
    return ind
def nid(c):
    m=re.search(r'(\d+)',str(c.get("id",""))); return int(m.group(1)) if m else 0
def load():
    o=[]
    if yaml:
        for p in sorted(glob.glob(os.path.join(CARDS,"I*.yaml"))):
            try: c=yaml.safe_load(open(p,encoding="utf-8"))
            except Exception: continue
            if isinstance(c,dict): c["_id"]=c.get("id"); o.append(c)
    o.sort(key=nid); return o

def main(recent=20):
    cards=load(); marked=[c for c in cards if outcome(c)!="?"]; total=len(marked)
    p=sum(1 for c in marked if outcome(c)=="pass"); fail=total-p
    # 到期未回填实际结果(due)：confirm_by<=今天 且 outcome 非实际
    today=_d.today().isoformat()
    def _actual(c):
        return outcome(c) in ("pass","fail","no_offer")
    due_ok=[c for c in cards
            if not _actual(c)
            and str((c.get("meta") or {}).get("confirm_by","")).strip()
            and str((c.get("meta") or {}).get("confirm_by","")).strip() <= today]
    from collections import defaultdict, Counter
    L=[]
    L.append("# 求职总报（持续更新）\n")
    L.append(f"> 由 {len(cards)} 张卡（标记 {total}）自动推导。新增面经后 `python main.py report` 刷新即可。正编口径为准，轮次口径＝每卡1轮。\n")
    if due_ok:
        L.append(f"> ⏰ 有 **{len(due_ok)} 场** 已到确认日但仍未回填实际结果（`python main.py remind` 查看清单）。请回填 outcome/why_ended/offer 后再信这份总报的这些场。\n")
    # 0 总览
    L.append(f"## 0) 轮次通过率（总览）\n- 通过轮 {p} ｜ 未过轮 {fail} ｜ 通过率 **{round(p/max(total,1)*100,1)}%**\n")
    # 1 正编 vs 外包
    sp=defaultdict(lambda:[0,0])
    for c in marked: sp[nature(c)][0 if outcome(c)=="pass" else 1]+=1
    L.append("## 1) 正编 vs 外包（别被假高通过骗）\n| 属性 | 过 | 挂 | 通过率 |\n|---|---|---|---|")
    for k,(a,b_) in sp.items(): L.append(f"| {k} | {a} | {b_} | {round(a/max(a+b_,1)*100,1)}% |")
    L.append("")
    # 2 主场赛道 正编 top
    bc=defaultdict(lambda:[0,0])
    for c in marked:
        if outcome(c)=="pass" and nature(c) in ("外包","兼职","实习"): continue
        b=bucket(c); bc[b][0 if outcome(c)=="pass" else 1]+=1
    L.append("## 2) 主场赛道（正编口径）\n| 赛道 | 过 | 挂 | 通过率 |\n|---|---|---|---|")
    for b,(a,b_) in sorted(bc.items(),key=lambda x:-(x[1][0]/max(sum(x[1]),1)))[:8]:
        L.append(f"| {b} | {a} | {b_} | {round(a/max(a+b_,1)*100,1)}% |")
    L.append("")
    # 2b 公司体量（正编口径）—— 赛道名会把大厂和小厂混在一格，体量必须单看
    sc=defaultdict(lambda:[0,0]); unscaled=0
    for c in marked:
        if outcome(c)=="pass" and nature(c) in ("外包","兼职","实习"): continue
        k=scale(c)
        if not k: unscaled+=1; continue
        sc[k][0 if outcome(c)=="pass" else 1]+=1
    L.append("## 2b) 公司体量（正编口径）\n")
    if sc:
        L.append("| 体量 | 过 | 挂 | 通过率 |\n|---|---|---|---|")
        for k in SCALE_TIERS:
            if k not in sc: continue
            a,b_=sc[k]; L.append(f"| {k} | {a} | {b_} | {round(a/max(a+b_,1)*100,1)}% |")
    else:
        L.append("- 还没有任何一场标了体量。在 config.yaml 的 `company_scale` 里写（例：`枫叶互动: 小厂`），"
                 "或在卡的 `interview.company_scale` 上逐场标。\n")
    if unscaled:
        L.append(f"\n> ⚠️ 另有 **{unscaled} 场正编**未标体量，未计入上表。"
                 f"体量无法从岗位/JD 文本推断，只能人工标注 —— 别把它当「没有小厂」。\n")
    L.append("")
    # 2c 体量 × 赛道 交叉（只列样本 ≥2 的格子，避免噪音）
    cross=defaultdict(lambda:[0,0])
    for c in marked:
        if outcome(c)=="pass" and nature(c) in ("外包","兼职","实习"): continue
        k=scale(c)
        if not k: continue
        cross[(k,bucket(c))][0 if outcome(c)=="pass" else 1]+=1
    rows=[(k,t,a,b_,a/max(a+b_,1)*100) for (k,t),(a,b_) in cross.items() if a+b_>=2]
    if rows:
        L.append("### 2c) 体量 × 赛道 交叉（样本 ≥2 的格子）\n| 体量 | 赛道 | 过 | 挂 | 通过率 |\n|---|---|---|---|---|")
        for k,t,a,b_,r in sorted(rows,key=lambda x:(SCALE_TIERS.index(x[0]) if x[0] in SCALE_TIERS else 9,-x[4])):
            L.append(f"| {k} | {t} | {a} | {b_} | {round(r,1)}% |")
        L.append("")
    # 3 反复挂根源
    w=[]
    for c in marked:
        if outcome(c)!="fail": continue
        w.extend(blocker_hits(c))
    cnt=Counter(w)
    L.append("## 3) 反复挂根源（fail 场 weakness 提频词）\n")
    if cnt:
        L.append("> 最长词优先匹配：`行业gap` 只记 `行业gap`，不再被拆成 `行业`+`gap`。"
                 "改关键词表见 config.yaml 的 `blocker_keywords`。\n")
        L.append("| 关键词 | 次数 |"); L.append("|---|---|")
        for k,v in cnt.most_common(12): L.append(f"| {k} | {v} |")
    else: L.append("- 暂未统计出")
    L.append("")
    # 3b) 针对 top 缘由，给曾 pass 卡里的高分回答作"话术小抄"(供练表达/复盘改法)
    # ⚠️ 匹配必须落在 **question 字段**，不能扫 how_answered：
    #    旧版扫整段回答，于是关键词 "不足" 命中了「…→供给不足」（在讲成绩）
    #    这种**褒义/成就句**，小抄就抄错了。挂因问的是"你哪里欠缺"，
    #    对应的应该是**被问到的那个问题**，而不是答案里恰好出现的字面。
    _tip=0
    if cnt:
        _seen=set()
        for _k,_v in cnt.most_common():
            _best=None
            for _c in marked:
                if outcome(_c)!="pass": continue
                for _q in (_c.get("questions") or []):
                    _blob=str(_q.get("question","")).lower()
                    if _k in _blob:
                        _sc=_q.get("score",0)
                        if _best is None or _sc> _best["sc"]:
                            _best={"sc":_sc,"q":str(_q.get("question","")),
                                   "txt":str(_q.get("how_answered","")),
                                   "who":f"{_c['_id']} {slug(_c)} {pos(_c)[:16]}"}
            if _best and _best["txt"] and _best["who"] not in _seen:
                _seen.add(_best["who"])
                L.append(f"- **{_k}**（问：{_best['q'][:40]}）\n  > {_best['txt'][:180]}\n  > 源自 {_best['who']} 曾 pass 的回答")
                _tip+=1
                if _tip>=3: break
        if not _tip:
            L.append("- 这些挂因词在 pass 卡的**问题**里没有对应题（多出现在 weakness 描述中），"
                     "所以给不出可直接照搬的话术 —— 说明该挂因不是「答得不好」，而是「没被问到 / 答不上」。")
    if _tip:
        L.append("")
    # 4 正编业务全过但 no offer（外包不属于"无offer"，单列不混）
    noff=[c for c in marked if nature(c)=="正编" and outcome(c)=="pass" and (offer_no(c) or blocker_hint(c))]
    L.append("## 4) 业务全过但 offer=no（后端/非能力卡点，重点看）\n")
    if noff:
        for c in noff:
            why=offer_no(c) or blocker_hint(c)
            L.append(f"- {c['_id']} {slug(c)} · {pos(c)[:32]} — {why}")
    else: L.append("- 当前无。请为 new 卡填 result.offer/why_ended 使此区生效。")
    L.append("")

    # 4b 挂了，但**原因不是当场表现**（匹配/需求变化等非能力因素）
    #
    # ⚠️ 为什么单列这一节（实测暴露的缺口）：
    #    上面的第 4 节要求 outcome=="pass"（"业务过了才叫非能力卡点"）。
    #    但真实情况里有另一种：**这一轮确实没过（fail），可原因不是答得差** ——
    #    例 I007 某内容社区：面试官明确说"经验确实比较丰富"，但要的是
    #    "能补齐团队能力缺口的人选"。这是**能力组合与团队需求的匹配问题**，
    #    不是当场表现问题。
    #    这类卡如果只由 weakness 参与"反复挂根源"统计，会让人误以为
    #    那是自己的短板 —— 而其实是方向不匹配，改进方向完全不同
    #    （前者要练表达/补知识，后者要换投递方向）。
    # 判据：outcome=fail 且 why_ended 写明了非能力性原因（见模块级 _NONCAP_KW）。
    noncap = []
    for c in marked:
        if outcome(c) != "fail":
            continue
        why = offer_no(c)
        if not why:
            continue
        low = why.lower()
        if any(k.lower() in low for k in _NONCAP_KW):
            noncap.append((c, why))
    if noncap:
        L.append("## 4b) 挂了，但原因不是当场表现（匹配/需求类 · 别当成能力短板）\n")
        L.append("> 这些场 outcome=fail，但 `why_ended` 写明了是**匹配/流程**原因。")
        L.append("> 它们的 weakness 仍保留（自我复盘有价值），但**改进方向不同**：")
        L.append("> 不是「练表达/补知识」，而是「调整投递方向」或「等 HC」。\n")
        for c, why in noncap:
            L.append(f"- {c['_id']} {slug(c)} · {pos(c)[:32]} — {why[:80]}")
        L.append("")
    # 5 该投/慎投/别投
    bc2=defaultdict(lambda:[0,0])
    for c in marked:
        if outcome(c)=="pass" and nature(c) in ("外包","兼职","实习"): continue
        k=slug(c); bc2[k][0 if outcome(c)=="pass" else 1]+=1
    good=[]; mid=[]; bad=[]
    for k,(a,b_) in bc2.items():
        if a>=2: pass
        tot=a+b_; rate=a/tot*100 if tot else 0
        if rate>=40 and tot>=2: good.append((k,a,b_,rate))
        elif tot<2 or rate>=20: mid.append((k,a,b_,rate))
        else: bad.append((k,a,b_,rate))
    L.append("## 5) 该投 / 慎投 / 别投（正编口径 · 附样本&置信）\n")
    def _ev(n):
        if n>=8: return "高置信"
        if n>=3: return "中置信"
        return "样本少·仅参考"
    L.append("✅ 该投（其中 ≥2 场）")
    for k,a,b_,r in sorted(good,key=lambda x:-x[3])[:12]:
        n=a+b_; L.append(f"- {k}（{round(r,1)}% {a}/{n} · {_ev(n)}）")
    L.append("\n⚠️ 慎投")
    for k,a,b_,r in sorted(mid,key=lambda x:-x[3])[:12]:
        n=a+b_; L.append(f"- {k}（{round(r,1)}% {a}/{n} · {_ev(n)}）")
    L.append("\n🚫 别投（通过率 <20% 且 ≥2 场）")
    for k,a,b_,r in sorted(bad,key=lambda x:x[3])[:10]:
        n=a+b_; L.append(f"- {k}（{round(r,1)}% {a}/{n} · {_ev(n)}）")
    L.append("\n> *样本≤2 只作趋势参考，别当单场/单家硬结论。若该公司你面很少，看图说话更稳。*")
    L.append("")
    # 6 最近趋势
    if len(marked)>=10:
        rc=marked[-min(recent,len(marked)):]; oc=marked[:-min(recent,len(marked))] if len(marked)>recent else []
        rp=sum(1 for c in rc if outcome(c)=="pass"); op=sum(1 for c in oc if outcome(c)=="pass")
        L.append("## 6) 最近 vs 之前 趋势\n")
        L.append(f"- 最近 {len(rc)} 场通过率：{round(rp/max(len(rc),1)*100,1)}%")
        if oc: L.append(f"- 之前 {len(oc)} 场通过率：{round(op/max(len(oc),1)*100,1)}%")
        L.append("")
    # 7 跨界一面挂告警
    # ⚠️ 主场赛道从 config.main_tracks 读，**不再写死**。
    #    旧版写死 ("生活服务/点评","内容/社区大厂") 当主场，于是词表后加的
    #    「出海/国际化」「用户增长」「B端/商家」等真实主场全被判成"跨界"、全被点名。
    #    未配置 main_tracks 时按「该赛道历史通过率 ≥ 40%」自动视为主场，不预设人名。
    _mt = set(main_tracks())
    if not _mt:
        _tr = defaultdict(lambda:[0,0])
        for c in marked:
            if outcome(c)=="pass" and nature(c) in ("外包","兼职","实习"): continue
            _tr[bucket(c)][0 if outcome(c)=="pass" else 1]+=1
        _mt = {t for t,(a,b_) in _tr.items() if a+b_>=2 and a/(a+b_)>=0.4}
    # ⚠️ 轮次判定改为语义解析（is_first_round），不再用枚举白名单。
    #    白名单只有全角写法，真实数据里有"业务面(一面)""一面(业务)"等半角/带后缀写法，
    #    实测 87 张 fail 卡会被漏掉 38 张（详见 industry_taxonomy.round_no）。
    c1=[c for c in marked if outcome(c)=="fail" and is_first_round(c) and bucket(c) not in _mt]
    if c1:
        L.append("## 7) 跨界/新方向一面挂告警（慎投）\n")
        L.append(f"> 主场赛道（{'config.main_tracks 指定' if main_tracks() else '按历史通过率 ≥40% 自动推断'}）：{'、'.join(sorted(_mt)) or '无'}\n")
        L.append(", ".join([f"{c['_id']} {slug(c)}" for c in c1[:30]]) + ("…" if len(c1)>30 else ""))
        L.append("")

    # 可信度自述 / 边界
    L.append("\n----\n## 可信度自述 / 边界")
    caveat = ("总样本 ≥20：可当真值趋势参考；单场仍建议用 apply/evaluate 而非百分比下结论。"
              if total >= 20 else "样本 <20 场：本报告只用于看趋势/方向，**不要**用单个百分比做该投/该场的硬决策。")
    L.append(f"- 样本：已标记 {total} 场（正编口径为准；外包单独看）。{caveat}")
    if due_ok:
        L.append(f"- ⚠️ 有 {len(due_ok)} 场已到 confirm_by 仍未回填实际结果 → 这些以 unknown 计可能失真。先 `python main.py remind` 回填 outcome/why_ended/offer 再信这几格。")
    L.append("- 这些数字随新场动态变化，是『相对谁/哪一批』的参考，不是唯一事实；能自证的是『历史通过率>纯猜测』(backtest)。")
    L.append("- 行业/正编/外包词用的是当前默认；若你的行业/市场不同，先在 config 里调整，再信对应维度。")
    L.append("- **体量（大厂/中厂/小厂/创业团队）只能人工标注**，引擎不猜：从岗位/JD 文本推不出公司多大。"
             "未标注的场次如实排除在 2b/2c 之外，不要读成「没有小厂」。")

    with open(OUT,"w",encoding="utf-8") as out: out.write("\n".join(L))
    print("[OK] 已更新唯一总报 →", OUT)

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--recent",type=int,default=20); a=ap.parse_args(); main(a.recent)
