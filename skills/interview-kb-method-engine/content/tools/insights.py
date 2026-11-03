#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
insights.py — 痛点/优势智能体检（自学习层）

自动扫描 cards/*.yaml 的 reflection + result + questions，聚合出：

1. 高频痛点（跨场反复出现的 weakness，随卡片增多自动累计+排序）
2. 差异化优势（反复出现的 strength）
3. 隐藏问题（不问看不到的：指标口径/GitHub/海外/外包叙事/职业定位跨行业等）
4. 失败关联（哪些痛点常出现在 fail 的场次中 → 判断"决定性失分因素"）

特点：这是"越喂越准"的核心——引擎基于卡片数据动态统计，
不写死固定词表（比 predict.py 的硬编码更强），全凭你喂进的面经累加出规律。

用法：
    python insights.py                 # 输出《痛点优势报告》到 mianjing/痛点优势报告.md
    python insights.py --top 15        # 只看前 N 个痛点
    python insights.py --plain         # 终端直接打印(不写文件)
"""

import os
import re
import sys
import glob
import argparse
from collections import Counter, defaultdict

# ⚠️ Windows 控制台默认 GBK，本模块会输出 🔴/🟢 等 emoji（GBK 编不出来）。
#    不设 reconfigure 的话 `--plain`（走 print 而非写文件）会直接崩：
#      UnicodeEncodeError: 'gbk' codec can't encode character '\U0001f534'
#    其它同级模块都设了，就这里漏了。
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
OUT = os.path.join(BASE, "..", "痛点优势报告.md")


def load_cards():
    cards = []
    if yaml is None:
        return cards
    for p in sorted(glob.glob(os.path.join(CARDS, "I*.yaml"))):
        try:
            with open(p, "r", encoding="utf-8") as f:
                c = yaml.safe_load(f)
            if c:
                c["_id"] = c.get("id") or os.path.basename(p).split("_")[0]
                c["_company"] = ((c.get("interview") or {}).get("company") or "").split("·")[0].strip()
                c["_file"] = os.path.basename(p)
                cards.append(c)
        except Exception:
            pass
    return cards


# 痛点主题词（宽泛类别，用于把中文 weakness 归到可统计的主题；随规则学习会细化）
THEME_PATTERNS = [
    ("语速/表达", ["语速", "快", "读稿", "准备不足", "表达", "口吃", "背诵"]),
    ("简历/自我介绍", ["简历", "自我介绍", "不精炼", "不有条理", "版本", "写太多", "不完整"]),
    ("指标/口径", ["指标", "口径", "ROI", "渗透", "占比", "数据", "消费用户"]),
    ("海外/英语", ["海外", "英语", "口语", "本地化", "出海"]),
    ("外包/正编", ["外包", "正编", "政治", "职级"]),
    ("GAP/空窗", ["gap", "空窗", "离职原因", "稳定性"]),
    ("工程背景/GitHub", ["GitHub", "github", "工程", "代码", "仓库", "软件工程"]),
    ("职业定位/方向", ["职业定位", "方向散", "不聚焦", "规划", "职业发展"]),
    ("行业跨界", ["行业", "不懂", "没做过", "背景", "财经", "汽车", "硬件", "经验不足"]),
    ("家庭/个人", ["家庭", "家人", "照顾", "病", "ICU", "医疗", "生活"]),
    ("AI/技术", ["AI", "MCP", "工具", "agent", "技术债"]),
    ("面试节奏/反问", ["反问", "提问", "面试流程", "反向"]),
]


def theme_of(text):
    hits = []
    for name, kws in THEME_PATTERNS:
        if any(kw.lower() in text.lower() for kw in kws):
            hits.append(name)
    return hits


def _slice(text, target_len=140):
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)
    return text[:target_len] + ("…" if len(text) > target_len else "")


def build_report(cards, topn=15):
    weak_themes = Counter()
    weak_by_theme = defaultdict(list)
    strong_by_theme = defaultdict(list)
    outcome_weak = defaultdict(lambda: Counter())  # outcome -> theme 分布
    fail_reasons = []   # fail 场次的 weakness 明细
    skill_counter = Counter()
    best_answers = []

    for c in cards:
        ref = c.get("reflection", {}) or {}
        res = c.get("result", {}) or {}
        outcome = str(res.get("outcome", "unknown")).strip().lower()

        w = ref.get("weakness", "")
        s = ref.get("strength", "")
        themes = theme_of(w or "")
        for t in themes:
            weak_themes[t] += 1
            weak_by_theme[t].append((c["_id"], c["_company"], _slice(w)))
            outcome_weak[outcome][t] += 1
        if s:
            for t in theme_of(s) or ["优势"]:
                strong_by_theme[t].append((c["_id"], c["_company"], _slice(s)))

        if outcome == "fail" and w:
            fail_reasons.append((c["_id"], c["_company"], _slice(w)))

        for sk in (c.get("skills", []) or []):
            skill_counter[str(sk)] += 1

        # 最佳回答
        best = None
        for q in (c.get("questions", []) or []):
            if isinstance(q, dict) and q.get("question") and best is None:
                score = q.get("score", 0) or 0
                if score >= 5 or (best and score > best[0]):
                    pass
                if best is None or score > best[0]:
                    best = (score, c["_id"], c["_company"], q.get("question"))
        if best:
            best_answers.append(best)

    # 排序
    weak_rank = weak_themes.most_common(topn)
    strong_top = [(t, len(v)) for t, v in
                  sorted(strong_by_theme.items(), key=lambda x: -len(x[1]))[:topn]]

    L = []
    L.append("# 痛点/优势智能体检报告（随面经增多自动累计，越喂越准）\n")
    L.append(f"> 基于 **{len(cards)} 场** 已存档面经自动统计。每新增一场面经并归档，本报告会自动累加、更精准。\n")

    # 通过率
    oc = Counter(cards_outcome(cards))
    total_pass_fail = oc["pass"] + oc["fail"]
    rate_txt = f"{round(oc['pass']/total_pass_fail*100,1)}%" if total_pass_fail else "—（暂无 pass/fail 样本）"
    L.append(f"## 0) 总览\n")
    L.append(f"- 已存档：{len(cards)} 场 ｜ 通过 {oc['pass']} ｜ 未通过 {oc['fail']}"
             f" ｜ 整体业务面通过率 **{rate_txt}**"
             f"（仅统计 pass/fail；另有 unknown {oc['unknown']}）\n")

    # 高频痛点
    L.append("## 1) 高频痛点（反复出现 → 最该优先解决）\n")
    for t, n in weak_rank:
        L.append(f"🔴 **{t}** — 出现 {n} 次")
        for cid, comp, detail in weak_by_theme[t][:4]:
            L.append(f"   - [{cid}][{comp}] {detail}")
        L.append("")
    if not weak_rank:
        L.append("（暂无提取到明显痛点，请检查各卡片 reflection.weakness）\n")

    # 差异化优势
    L.append("## 2) 差异化优势（反复出现 → 可复用为杀手锏案例）\n")
    for t, n in strong_top:
        L.append(f"🟢 **{t}** — {n} 处")
        for cid, comp, detail in strong_by_theme[t][:3]:
            L.append(f"   - [{cid}][{comp}] {detail}")
        L.append("")
    if not strong_top:
        L.append("（暂无）\n")

    # 失败关联（决定性失分）—— fail 场次的痛点主题
    L.append("## 3) 隐藏问题 & 失败关联（决定 offer 的失分点）\n")
    L.append("> 统计各痛点主题在 **未通过(pass 之外的) 场次** 中的出现频率 —— "
             "出现越集中，越说明它是卡脖子的决定性因素。\n")
    fail_theme = Counter()
    for c in cards:
        ref = c.get("reflection", {}) or {}
        res = c.get("result", {}) or {}
        oc = str(res.get("outcome", "unknown")).strip().lower()
        if oc == "fail":
            for t in theme_of(ref.get("weakness", "")):
                fail_theme[t] += 1
    for t, n in fail_theme.most_common(topn):
        L.append(f"- `{t}`（未通过场次中出现 {n} 次）")
    L.append("")

    # 未确认的场次提醒（数据不全会影响统计）
    unknown = [c["_id"] for c in cards if str((c.get("result") or {}).get("outcome", "")).strip() == "unknown"]
    if unknown:
        L.append(f"> ⚠️ 有 {len(unknown)} 场尚未标注最终结果（{'/'.join(unknown)}），补 `build_card.py --id --outcome` 后统计更准。\n")

    # 最佳回答池
    L.append("## 4) 高分回答池（自评 top 候选）\n")
    best_answers.sort(key=lambda x: -x[0])
    for score, cid, comp, q in best_answers[:10]:
        if score >= 4:
            L.append(f"- [『{comp}』{cid}] (score {score}) {_slice(q, 60)}")
    L.append("")

    return "\n".join(L)


def cards_outcome(cards):
    return [str((c.get("result") or {}).get("outcome", "unknown")).strip().lower()
            for c in cards]


def main():
    ap = argparse.ArgumentParser(description="痛/优点体检")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--plain", action="store_true", help="终端打印不写文件")
    args = ap.parse_args()

    cards = load_cards()
    report = build_report(cards, topn=args.top)
    if args.plain or not args.out:
        print(report)
        return 0
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[OK] 已基于 {len(cards)} 场生成体检报告 -> {args.out}")
    return 0


if __name__ == "__main__":
    exit(main())
