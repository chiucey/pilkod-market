#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cross_analysis.py — 跨场分析器

批量读取 cards/*.yaml，输出：
  1. 高频问题统计（按 theme 与同一问题出现频次）
  2. 能力标签聚合（skills 出现频次）
  3. 短板/优势排序（reflection.strength/weakness 聚合）
  4. 通过率统计（基于 result.outcome，若已填）
  5. 生成"备战手册"要点建议

用法：
    python cross_analysis.py                 # 全量分析，输出 Markdown
    python cross_analysis.py --out 备战手册.md  # 输出到文件
    python cross_analysis.py --theme 指标       # 只看某个主题

依赖：pymmound? 需要 yaml。若无，装 `pip install pyyaml`。
"""

import os
import sys
import glob
import argparse
from collections import Counter, defaultdict

# Windows 控制台默认 GBK；本模块输出含 emoji / 特殊符号，统一兜住编码。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("缺少 pyyaml，先安装: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

try:
    from industry_taxonomy import blocker_hits_from_text
except Exception:
    def blocker_hits_from_text(text, keywords=None): return []

CARDS_DIR = os.path.join(os.path.dirname(__file__), "..", "cards")
OUT = os.path.join(os.path.dirname(__file__), "..", "跨场分析.md")


def load_cards():
    cards = []
    for p in sorted(glob.glob(os.path.join(CARDS_DIR, "I*.yaml"))):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data is None:
                continue
            data["_file"] = os.path.basename(p)
            data["_id"] = data.get("id") or os.path.basename(p).split("_")[0]
            cards.append(data)
        except Exception as e:
            print(f"[解析失败] {os.path.basename(p)}: {e}", file=sys.stderr)
    return cards


def safe(d, k, default=""):
    v = d.get(k, default)
    return v if v else default


def analyze(cards):
    rep = []
    rep.append("# 面试跨场分析报告")
    rep.append("")
    rep.append(f"共 {len(cards)} 场。\n")

    # --- 基本列表 ---
    rep.append("## 一场次清单\n")
    rep.append("| 卡号 | 公司 | 岗位 | 日期 | 轮次 | 结果 |")
    rep.append("|---|---|---|---|---|---|")
    by_theme = defaultdict(list)
    question_counter = Counter()
    skill_counter = Counter()
    weakness_pool = []
    strength_pool = []
    outcome_counter = Counter()

    for c in cards:
        inter = c.get("interview", {}) or {}
        res = c.get("result", {}) or {}
        outcome = res.get("outcome", "待确认")
        outcome_counter[outcome] += 1
        rep.append(
            f"| {safe(c,'_id')} | {safe(inter,'company')} | {safe(inter,'position')} | "
            f"{safe(inter,'date')} | {safe(inter,'round')} | {outcome} |"
        )

        # questions
        for q in c.get("questions", []) or []:
            if not isinstance(q, dict):
                continue
            text = safe(q, "question")
            theme = safe(q, "theme", "其他")
            if text:
                # 归一化去掉常见口语开头
                key = text
                question_counter[key] += 1
            by_theme[theme].append(safe(q, "question"))

        # skills
        for s in c.get("skills", []) or []:
            skill_counter[str(s)] += 1

        # reflection
        ref = c.get("reflection", {}) or {}
        if ref.get("weakness"):
            weakness_pool.append(f"{safe(c,'_id')}({safe(inter,'company')}): {ref['weakness']}")
        if ref.get("strength"):
            strength_pool.append(f"{safe(c,'_id')}({safe(inter,'company')}): {ref['strength']}")

    # --- 通过率 ---
    rep.append("\n## 通过率（outcome 需人工补充后才准确）\n")
    for k, v in outcome_counter.most_common():
        rep.append(f"- {k}: {v} 场")
    if outcome_counter.get("待确认", 0) == len(cards):
        rep.append("\n> ⚠️ 所有卡片 outcome 均为待确认，请先用 `build_card.py --id --outcome --reason` 回填。")
    rep.append("")

    # --- 高频问题 ---
    rep.append("## 高频问题 / 主题分布\n")
    for theme, qs in sorted(by_theme.items(), key=lambda x: -len(x[1])):
        rep.append(f"### {theme}（{len(qs)} 次）")
        seen = Counter(qs)
        for q, n in seen.most_common(8):
            rep.append(f"- {q}" + (f"  ×{n}" if n > 1 else ""))
        rep.append("")

    # --- 能力标签 ---
    rep.append("## 能力标签聚合（出现频次）\n")
    if skill_counter:
        for s, n in skill_counter.most_common(25):
            rep.append(f"- {s}: {n}")
    else:
        rep.append("（暂无 skills 标签，先补充各卡片的 skills。）")
    rep.append("")

    # --- 短板 Top ---
    rep.append("## 短板 / 复用失误池（供备战消化）\n")
    # 统计跨场出现的共性短板关键词
    # ⚠️ 原为硬编码 16 词表，实测真实卡的 weakness 只有 74 张能命中，
    #    另外 68 张（约 48%）在这张表里完全不可见。改走共享的 blocker_hits，
    #    与 diagnosis/report_all 用同一套词表与"最长优先"规则。
    weak_counter = Counter()
    for w in weakness_pool:
        for kw in blocker_hits_from_text(w):
            weak_counter[kw] += 1
    if weak_counter:
        rep.append("| 短板关键词 | 出现次数 |")
        rep.append("|---|---|")
        for kw, n in weak_counter.most_common(20):
            rep.append(f"| {kw} | {n} |")
    rep.append("")
    rep.append("明细：")
    for w in weakness_pool:
        rep.append(f"- {w}")
    rep.append("")

    # --- 优势池 ---
    rep.append("## 优势 / 可复制内容池\n")
    for s in strength_pool:
        rep.append(f"- {s}")
    rep.append("")

    # --- 备战要点 ---
    rep.append("## 备战手册建议\n")
    if weak_counter:
        top = weak_counter.most_common(3)
        rep.append("**优先攻坚**：")
        for kw, n in top:
            rep.append(f"- `{kw}` 反复被点（{n} 场），准备统一话术/统一动作。")
    rep.append("- 准备精简、可量化的自我介绍（按目标公司/岗位微调）。")
    rep.append("- 每个 case 备好：北极星指标 → 拆解 → 手段 → 结果（数据闭环）。")
    rep.append("- 离职/GAP/外包叙事统一、正面化。")
    return "\n".join(rep)


def main():
    ap = argparse.ArgumentParser(description="跨场分析")
    ap.add_argument("--out", default=OUT, help="输出 Markdown 路径")
    ap.add_argument("--theme", default=None, help="仅看某主题")
    args = ap.parse_args()

    cards = load_cards()
    if not cards:
        print("[提示] cards/ 下还没有卡片 —— 这是正常的「初始空库」状态，先建一场再来分析：")
        print("       python main.py record new --company 公司 --position 岗位 --round 一面 --nature 正编")
        return 0
    report = analyze(cards)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[OK] 已生成 {len(cards)} 场分析报告 -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
