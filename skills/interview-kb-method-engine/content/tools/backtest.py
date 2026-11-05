#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# backtest.py — 对「公司/赛道历史通过率」做留一法(leave-one-out)回归，看能不能预测一场的结果。
# 评价的是启发式基线（只看历史 pass 占比是否>阈值 → 预测该场通过与否），不是完美证明，而是给你一个“我该信多少”的天花板。
# 用法: python main.py backtest
import os, glob, re, sys
if hasattr(sys.stdout,"reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")
try:
    import yaml
except Exception:
    yaml=None
BASE=os.path.dirname(os.path.abspath(__file__))
CARDS=os.path.join(BASE,"..","cards")
try:
    from industry_taxonomy import classify
except Exception:
    def classify(text, fallback="其他"): return fallback
def outcome(c):
    s=str((c.get("result") or {}).get("outcome") or "")
    if "pass" in s.lower(): return "pass"
    if "fail" in s.lower() or "挂" in s: return "fail"
    return "?"
def cmp(c): return str((c.get("interview") or {}).get("company","")).split("·")[0]

# 把赛道粗分成 强/中/弱 三档，供本模块的留一法回归使用。
#
# ⚠️ 旧版是**写死的两组赛道名**（生活服务/硬件系算"强"、内容/游戏算"中"、
#    其余一律算"弱-跨界"）。这等于把一个主观判断固化进代码，而且
#    词表里后加的「出海/国际化」「用户增长」「B端/商家」等全部被归进"弱"，
#    直接扭曲了下面那个"能不能预测单场"的结论。
#    更根本的问题是：**"强/中/弱"本就该由数据算出来，而不是由人写死。**
#    现在改为按各赛道的**实际通过率排序**动态分档（样本不足的归入"中"）。
_STRENGTH_CACHE = {}

def strength_tiers(cards):
    """按赛道实际通过率返回 {赛道: '强'|'中'|'弱'}。

    规则：样本 >= 3 的赛道参与分档，通过率前 1/3 为"强"、后 1/3 为"弱"、
    中间为"中"；样本 < 3 的赛道不参与排序，统一给"中"（不武断判强弱）。
    结果按 (赛道集合) 缓存，避免留一法里 O(n²) 反复重算。
    """
    from collections import defaultdict
    stat = defaultdict(lambda: [0, 0])
    for c in cards:
        t = classify(str((c.get("interview") or {}).get("company", ""))
                     + str((c.get("interview") or {}).get("position", "")), fallback="其他")
        stat[t][0 if outcome(c) == "pass" else 1] += 1
    ranked = sorted(
        [(t, p / max(p + f, 1)) for t, (p, f) in stat.items() if p + f >= 3],
        key=lambda x: -x[1])
    tiers = {}
    n = len(ranked)
    for i, (t, _) in enumerate(ranked):
        if n >= 3:
            tiers[t] = "强" if i < n / 3 else ("弱" if i >= 2 * n / 3 else "中")
        else:
            tiers[t] = "中"
    return tiers

def bucket(c):
    """返回 '强-…' / '中-…' / '弱-…'。档位由 strength_tiers 动态给出。"""
    t = classify(str((c.get("interview") or {}).get("company", ""))
                 + str((c.get("interview") or {}).get("position", "")), fallback="其他")
    if not _STRENGTH_CACHE:
        _STRENGTH_CACHE["loaded"] = True   # 占位：未提供 cards 时退回"中"
        _STRENGTH_CACHE["tiers"] = {}
    tier = _STRENGTH_CACHE["tiers"].get(t, "中")
    return "%s-%s" % (tier, t)
def load():
    o=[]
    if yaml:
        for p in sorted(glob.glob(os.path.join(CARDS,"I*.yaml"))):
            try: c=yaml.safe_load(open(p,encoding="utf-8"))
            except Exception: continue
            if isinstance(c,dict): o.append(c)
    return o

def main():
    cards=[c for c in load() if outcome(c)!="?"]
    # only正编 (外包通过率虚高,会污染) — 同主题聚焦
    def is_out(c):
        blob=cmp(c)+ str((c.get("result") or {}).get("reason",""))
        return "外包" in blob or "兼职" in blob
    pool=[c for c in cards if not is_out(c)]
    from collections import defaultdict

    # 用整个 pool 先算出各赛道的强/中/弱档位，供 bucket() 使用。
    # 注意：分档用全量、预测用留一 —— 这是刻意的：
    #   "哪些赛道算我的强项"是**描述性统计**（用全量没问题），
    #   而"预测这张卡过不过"才需要留一（不能让自己的标签参与）。
    _STRENGTH_CACHE["tiers"] = strength_tiers(pool)

    # ⚠️ 这个模块此前输出的"准确率"是**空的**（2026 审计发现），两个原因：
    #
    #   ① 它自称"留一法"，但先验是用**含该卡自己**的全量算的 ——
    #      自己的标签参与了对自己的预测。
    #   ② 更要命：所有桶的通过率**全都低于 0.5**，于是 `rate>0.5`
    #      对每一张卡都预测"挂"。所谓"启发式模型"因此退化成
    #      "永远猜挂"这个朴素基线，两者准确率**逐位相同** ——
    #      不是巧合，是构造使然。
    #
    # 所以旧输出里那个 66.1% 看起来像"模型有 66% 准确率"，
    # 实际只是"你挂的场占比 66.1%"。下面把真·留一法算出来并显式说明，
    # 而不是继续给一个会被误读成"启发式有用"的数字。

    def bucket_rates(exclude=None):
        g=defaultdict(lambda:[0,0])
        for c in pool:
            if exclude is not None and c is exclude:
                continue
            g[bucket(c)][0 if outcome(c)=="pass" else 1]+=1
        return g

    # A) 真·留一法：预测每张卡时把它从先验里剔除
    tp_loo=0
    for c in pool:
        g=bucket_rates(exclude=c)
        p,f=g[bucket(c)]
        if ("pass" if p/max(p+f,1)>0.5 else "fail")==outcome(c): tp_loo+=1
    acc_loo=tp_loo/max(len(pool),1)

    good=bucket_rates()
    n_pass_pred=sum(1 for c in pool
                    if good[bucket(c)][0]/max(sum(good[bucket(c)]),1)>0.5)
    naive=sum(1 for c in pool if outcome(c)=="fail")/max(len(pool),1)

    lines=[]
    lines.append("## backtest：这套启发式到底能不能预测单场？")
    lines.append("")
    lines.append(f"- 样本（仅正编、有结果）：{len(pool)}")
    lines.append("")
    lines.append("| 赛道桶 | 过 | 挂 | 通过率 |")
    lines.append("|---|---|---|---|")
    for b,(p,f) in sorted(good.items(),key=lambda x:-(x[1][0]/max(sum(x[1]),1))):
        lines.append(f"| {b} | {p} | {f} | {round(p/max(p+f,1)*100,1)}% |")
    lines.append("")
    lines.append(f"- 真·留一法准确率：**{round(acc_loo*100,1)}%**")
    lines.append(f"- 朴素基线（永远猜「挂」）：**{round(naive*100,1)}%**")
    lines.append(f"- 本模型预测「通过」的卡数：**{n_pass_pred}** / {len(pool)}")
    lines.append("")
    if n_pass_pred == 0:
        lines.append("> ⚠️ **本模型一张都没预测「通过」** —— 因为所有桶的通过率都低于 50%，")
        lines.append("> `rate>0.5` 恒为假，它等价于「永远猜挂」。上面两个准确率")
        lines.append("> **必然相同**（构造使然，不是巧合）。")
        lines.append(">")
        lines.append("> 所以这个数字**不能**用来证明「看历史通过率能预测单场」。")
        lines.append("> 它只说明：在你当前样本里，单看赛道先验没有任何预测力 ——")
        lines.append("> 真正有信息量的是题面质量/面试官/题目类型，由 apply / evaluate 承担。")
    else:
        lines.append("> 若留一法准确率**不高于**朴素基线，说明单看历史通过率不足以预测单场；")
        lines.append("> 若高于，也只是弱证据 —— 小样本下留一法本身波动很大。")
    lines.append("")
    lines.append("> 另注：桶按**公司+岗位**文本归类，同一家公司可能落进不同桶")
    lines.append("> （例：同一家公司在「内容运营」「B端/商家」「用户增长」都有卡）。")
    lines.append("> 这是刻意的（同公司会跨赛道招人），但也意味着「桶」不等于「公司」。")
    print("\n".join(lines))

if __name__=="__main__":
    main()
