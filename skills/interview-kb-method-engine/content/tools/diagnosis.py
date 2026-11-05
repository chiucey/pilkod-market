#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnosis.py — 求职自我诊断（四大核心问题）

自动扫描所有卡片，回答：
  1. 通过率最高的是哪类岗位/公司？
  2. 反复挂掉的根源是什么？
  3. 能力标签分布？
  4. 该投什么/慎投什么/别投什么？

用法：python diagnosis.py [--out 文件.md] [--plain]
"""

import os, sys, re, glob
import argparse
from collections import Counter, defaultdict

# Windows 控制台默认 GBK；本模块输出含 emoji / 特殊符号，
# 不设 reconfigure 时在部分终端会 UnicodeEncodeError。统一兜住。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    yaml = None

BASE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(BASE, "..", "cards")
OUT = os.path.join(BASE, "..", "求职诊断报告.md")

# ── 行业/赛道分类 ──────────────────────────────────────────────
# ⚠️ 这里曾经自己维护一张 INDUSTRY_MAP 关键词表（内容平台/工具/硬件/生活服务…），
#    与 industry_taxonomy.py 是**两套彼此独立、结论不同**的分类：
#    它的词表几乎全是品类词（"内容社区""到店""旅游"），而真实卡片里
#    interview.company 存的是公司名（"某本地生活平台""某短视频平台""B站（bilibili）"），
#    于是 绝大多数卡（96%）落进"其他"，报告第一张表退化成一行无意义的兜底，
#    并且 Q4 会输出「✅ 该投（通过率最高的行业类型）：其他」——
#    拿垃圾桶当建议。这正是本项目反复出现的"硬编码封闭集合"病。
#    现在统一走 industry_taxonomy.classify（岗位方向优先，公司名兜底）。
from industry_taxonomy import classify as _classify_track, blocker_hits


def industry_of(company, position):
    """把「公司 + 岗位」归到一个赛道；判不出来才返回"其他"。"""
    return _classify_track(f"{company} {position}", fallback="其他")


# ── 岗位类型分类（按 position 关键词）─────────────────────────────
ROLE_MAP = {
    "内容/社区运营": ["内容运营", "社区运营", "社群运营", "圈子", "活动运营", "UGC", "PGC"],
    "策略/中台": ["策略", "中台", "产运", "标签", "分发", "推荐", "数据", "增长", "效率"],
    "创作者/作者运营": ["创作者", "作者", "达人", "KOL", "IP"],
    "垂类/品类": ["垂类", "品类", "美食", "数码", "体育", "影视", "科技", "金融"],
    "产品/工具": ["产品", "工具", "平台", "系统", "电商", "招商", "选品"],
    "活动/营销": ["活动", "营销", "campaign", "赛事"],
    "商业/变现": ["商业", "变现", "带货", "投放", "广告"],
}


def classify(position):
    """把岗位归入 ROLE_MAP 中最匹配的一个类型。"""
    for role, keywords in ROLE_MAP.items():
        for kw in keywords:
            if kw in position:
                return role
    return "其他"


def classify_industry(company, position=""):
    """兼容旧调用签名：只传公司名时也尽量判对。

    ⚠️ 只按公司名判会退化成 96% "其他"（真实数据里公司名是"某本地生活平台""某短视频平台"这类
    品牌名，不含任何品类词）。所以有 position 时优先用岗位方向。
    """
    return industry_of(company, position)


def load():
    cards = []
    if yaml is None:
        return cards
    for p in sorted(glob.glob(os.path.join(CARDS, "I*.yaml"))):
        try:
            c = yaml.safe_load(open(p, encoding="utf-8"))
            if c:
                c["_file"] = os.path.basename(p)
                c["_id"] = c.get("id", "")
                cards.append(c)
        except Exception:
            pass
    return cards


def safe_str(v):
    return str(v) if v else ""


def build(cards):
    # ── 统计 ─────────────────────────────────────────────
    industry_stats = defaultdict(lambda: {"pass": 0, "fail": 0})
    role_stats = defaultdict(lambda: {"pass": 0, "fail": 0})
    weakness_counter = Counter()
    skill_counter = Counter()
    high_pass_companies = []
    high_fail_companies = []

    for c in cards:
        inter = c.get("interview") or {}
        res = c.get("result") or {}
        ref = c.get("reflection") or {}

        company = safe_str(inter.get("company"))
        position = safe_str(inter.get("position"))
        outcome = safe_str(res.get("outcome")).lower()
        weakness = safe_str(ref.get("weakness"))
        skills = c.get("skills") or []

        # 只看 pass/fail
        if "pass" in outcome:
            tag = "pass"
        elif "fail" in outcome:
            tag = "fail"
        else:
            continue

        # 行业：必须把 position 一起传进去 —— 只按公司名判会 96% 落"其他"
        industry = classify_industry(company, position)
        industry_stats[industry][tag] += 1

        # 岗位类型
        role = classify(position)
        role_stats[role][tag] += 1

        # 短板关键词：走共享的 blocker_hits（最长优先、不重叠，且与其它报告同源）。
        # ⚠️ 这里原来是硬编码 27 个词的白名单（还带个错字"基读"），
        #    实测 87 张 fail 卡里只有 67 张能命中 —— 其余 20 张的 weakness
        #    在"反复挂掉的根源"表里**完全不可见**。而且 cross_analysis(16 词)、
        #    decision(14 词) 各自还有一份不同的表，同一份数据三份挂因排行。
        if tag == "fail" and weakness:
            for kw in blocker_hits(c):
                weakness_counter[kw] += 1

        # 能力标签
        for sk in skills:
            skill_counter[sk] += 1

    # ── 通过率最高公司类型 ─────────────────────────────────────
    sorted_industry = sorted(
        industry_stats.items(),
        key=lambda x: (x[1]["pass"] / max(x[1]["pass"] + x[1]["fail"], 1), x[1]["pass"]),
        reverse=True
    )

    # ── 挂掉根源聚类 ─────────────────────────────────────────
    top_weakness = weakness_counter.most_common(8)

    # ── 能力标签 TOP10（排除非能力标签：面试类型/轮次/公司名）──────
    # 轮次类固定词 + 从卡里动态收集的"公司名"（避免把公司当能力标签）
    EXCLUDE_SKILLS = {
        "HR面", "二面", "三面", "四面", "五面", "一面", "终面", "交叉面",
    }
    for _c in cards:
        _comp = str((_c.get("interview") or {}).get("company", "") or "")
        for _part in re.split(r"[·/|、\s]+", _comp):
            if _part:
                EXCLUDE_SKILLS.add(_part)
    filtered_skills = {k: v for k, v in skill_counter.items() if k not in EXCLUDE_SKILLS}
    top_skills = sorted(filtered_skills.items(), key=lambda x: -x[1])[:12]

    # ── 投递建议（基于通过率）────────────────────────────────
    # ⚠️ 必须排除"其他"桶：它是**判不出赛道**的兜底，不是一类机会。
    #    旧版把它当普通赛道参与评选，于是输出
    #    「✅ 该投（通过率 ≥ 40% 的行业类型）：- 其他」——
    #    相当于建议你"去投那些我说不清是什么的岗位"。
    adv_pass = [k for k, v in industry_stats.items()
                if k != "其他" and v["pass"] > 0
                and v["pass"] / max(v["pass"] + v["fail"], 1) >= 0.4]
    adv_caution = [k for k, v in industry_stats.items()
                   if k != "其他" and v["fail"] > 0 and v["pass"] == 0 and v["fail"] >= 2]

    # ── 组装报告 ─────────────────────────────────────────────
    L = []
    L.append("# 求职自我诊断报告\n")
    L.append(f"> 基于 {len(cards)} 场面经自动生成。\n")

    # Q1: 通过率最高的是哪类岗位/公司
    L.append("## 1. 通过率最高的是哪类岗位/公司\n")
    L.append("| 公司类型 | 通过 | 未过 | 通过率 |")
    L.append("|---|---|---|---|")
    for ind, st in sorted_industry:
        total = st["pass"] + st["fail"]
        if total == 0:
            continue
        rate = round(st["pass"] / total * 100)
        L.append(f"| {ind} | {st['pass']} | {st['fail']} | {rate}% |")
    L.append("")

    # 按岗位类型
    L.append("**按岗位类型：**\n")
    L.append("| 岗位类型 | 通过 | 未过 | 通过率 |")
    L.append("|---|---|---|---|")
    for role, st in sorted(role_stats.items(), key=lambda x: (x[1]["pass"] / max(x[1]["pass"] + x[1]["fail"], 1), x[1]["pass"]), reverse=True):
        total = st["pass"] + st["fail"]
        if total == 0:
            continue
        rate = round(st["pass"] / total * 100)
        L.append(f"| {role} | {st['pass']} | {st['fail']} | {rate}% |")
    L.append("")

    # Q2: 反复挂掉的根源
    L.append("## 2. 反复挂掉的根源是什么\n")
    L.append("从失败场次的 `weakness` 中提取高频关键词：\n")
    for kw, cnt in top_weakness:
        L.append(f"- **{kw}** — 出现 {cnt} 次")
    L.append("")
    L.append("> 若某些短板在 fail 场次反复出现，说明它是'决定性因素'，而非偶发。\n")

    # Q3: 能力标签分布
    L.append("## 3. 能力标签分布\n")
    L.append("你所有卡片中 `skills[]` 字段的聚合统计（出现次数越多，代表你越频繁地被看到有这个能力）：\n")
    L.append("| 标签 | 出现次数 |")
    L.append("|---|---|")
    for sk, cnt in top_skills:
        L.append(f"| {sk} | {cnt} |")
    L.append("")

    # Q4: 该投什么/慎投什么/别投什么
    L.append("## 4. 该投什么 / 慎投什么 / 别投什么\n")
    if adv_pass:
        L.append("✅ **该投**（通过率 ≥ 40% 的行业类型）：")
        for a in adv_pass:
            L.append(f"- {a}")
    else:
        L.append("✅ **该投**：（暂无通过率≥40%的类型，请补充更多已知结果场次）")
    L.append("")
    if adv_caution:
        L.append("⚠️ **慎投/别投**（0 pass 且 fail ≥ 1 的行业类型）：")
        for a in adv_caution:
            L.append(f"- {a}")
    else:
        L.append("⚠️ **慎投/别投**：（暂无明显应避免的类型）")
    L.append("")
    # 按岗位类型补充建议
    adv_pass_role = [k for k, v in role_stats.items()
                     if v["pass"] > 0 and v["pass"] / max(v["pass"] + v["fail"], 1) >= 0.4]
    adv_caution_role = [k for k, v in role_stats.items()
                        if v["fail"] > 0 and v["pass"] == 0 and v["fail"] >= 1]
    if adv_pass_role:
        L.append("✅ **岗位类型该投**（通过率≥40%）：")
        for a in adv_pass_role:
            L.append(f"- {a}")
    if adv_caution_role:
        L.append("⚠️ **岗位类型慎投**（0 pass 且 fail ≥ 1）：")
        for a in adv_caution_role:
            L.append(f"- {a}")
    L.append("")

    L.append("---\n")
    L.append("## 五、使用说明\n")
    L.append("本报告每次新增/回填卡片后重新跑，会自动更新。\n")
    L.append("核心逻辑：按`result.outcome`聚类，缺`outcome`的卡片不参与统计。\n")
    L.append("如需更细粒度分析（如按公司具体名称、按轮次），请用 `insights.py` 或让 AI 结合原始卡片逐场解读。\n")
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="求职自我诊断报告")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--plain", action="store_true")
    args = ap.parse_args()

    cards = load()
    report = build(cards)
    if args.plain:
        print(report)
    else:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[OK] 已生成诊断报告 -> {args.out}")
    return 0


if __name__ == "__main__":
    exit(main())
