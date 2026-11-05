#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
predict.py — 新面经评估（功能 5 & 6）

功能5：基于新面经(转写稿/摘要) + 历史参考，判断"通过可能性"。
功能6：逐段/逐题判断"哪里答得好、哪里答得差"。

设计：脚本提供结构化上下文 + 启发式信号（自评、硬伤词、outcome 校准基线），
最终"通过可能性/回答好坏"的判断由调用方(AI)结合语义给出。脚本负责把
新面经规整成逐题形式 + 汇总历史 outcome 校准 + 标出常见硬伤词。

依赖：pyyaml。新面经文本可从文件读或直接传。
"""

import os
import re
import glob
import argparse
from collections import Counter

try:
    import yaml
except ImportError:
    yaml = None

BASE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(BASE, "..", "cards")

# 常见硬伤/风险信号词
RISK_WORDS = [
    "语速", "快", "读稿", "简历", "自我介绍", "不完整", "没做过海外", "外包",
    "gap", "空窗", "决策", "口径", "ROI", "Github", "github", "GitHub",
]
POSITIVE_WORDS = [
    "方法论", "case", "数据", "留存", "渗透", "内容池", "三进一反", "冷启动",
    "作者", "创作者", "社群", "标签", "AI", "MCP", "跨团队",
]


def load_cards():
    cards = []
    if yaml is None:
        return cards
    for p in sorted(glob.glob(os.path.join(CARDS, "I*.yaml"))):
        try:
            with open(p, "r", encoding="utf-8") as f:
                d = yaml.safe_load(f)
            if d:
                d["_id"] = d.get("id") or os.path.basename(p).split("_")[0]
                cards.append(d)
        except Exception:
            pass
    return cards


def outcome_kind(outcome_text):
    """把卡片的 outcome 文本归一化为 pass/fail/unknown。"""
    t = str(outcome_text or "待确认")
    if "待确认" in t or "无最终结果" in t or "未明说" in t or "后续" in t:
        return "unknown"
    if any(k in t for k in ["pass", "通过", "过了", "offer", "passed"]):
        return "pass"
    if any(k in t for k in ["fail", "失败", "未通过", "挂了", "没通过", "被拒"]):
        return "fail"
    return "unknown"


def calib(cards):
    """汇总历史 outcome，作为通过可能性校准基线。"""
    outcome = Counter()
    for c in cards:
        res = c.get("result", {}) or {}
        outcome[outcome_kind(res.get("outcome"))] += 1
    total = outcome["pass"] + outcome["fail"]
    base = (outcome["pass"] / total if total else None)
    return outcome, base


def parse_new_questions(text):
    """粗切：尽量把新面经切成若干 '问题' 段。启发式，AI 可覆盖。"""
    if not text.strip():
        return [], text
    # 尝试按发言人/问答分隔——转写稿复杂，这里返回整段，供 AI 逐题
    qas = []
    # 尝试找 'q' 或 'question:' 标记
    segments = re.split(r"(?m)^(?:\d+[.、)]|Q[:：]|问[:：]|问题[:：])", text)
    for s in segments:
        s = s.strip()
        if len(s) < 10:
            continue
        qas.append(s)
    if not qas:
        qas = [text[:2000]]
    return qas, None


def assess(text):
    cards = load_cards()
    outcome, base = calib(cards)
    risk_hits = [w for w in RISK_WORDS if w in text]
    pos_hits = [w for w in POSITIVE_WORDS if w in text]
    # 逐题切分
    qas, _ = parse_new_questions(text)
    per_qa = []
    for i, qa in enumerate(qas[:30]):
        risk = [w for w in RISK_WORDS if w in qa]
        pos = [w for w in POSITIVE_WORDS if w in qa]
        length = len(qa)
        per_qa.append({
            "段": i + 1,
            "长度": length,
            "命中风险词": risk,
            "命中正向词": pos,
        })
    return {
        "历史校准": {
            "outcome统计": dict(outcome),
            "基准通过率": (round(base * 100, 1) if base is not None
                          else "需先补已知结果的卡片才能建立基线"),
        },
        "新面经信号": {
            "命中风险词": risk_hits,
            "命中正向词": pos_hits,
            "风险词数": len(risk_hits),
            "正向词数": len(pos_hits),
        },
        "逐段(粗)": per_qa,
        "提示": "最终通过可能性与答题好坏判断需由 AI 结合语义、历史最佳回答对照给出；"
                "本脚本提供风险/正向信号与 outcome 校准基线。",
    }


def main():
    ap = argparse.ArgumentParser(description="新面经评估")
    ap.add_argument("text", nargs="?", help="新面经文本（或贴入）")
    ap.add_argument("--file", help="从文件读取新面经文本")
    ap.add_argument("--report", help="输出到文件")
    args = ap.parse_args()

    text = args.text
    if args.file and os.path.exists(args.file):
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    if not text:
        print("请传入新面经文本或 --file。")
        return 1

    result = assess(text)
    output = yaml.dump(result, allow_unicode=True, sort_keys=False) if yaml else str(result)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(output)
        print("[OK] 已生成:", args.report)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    exit(main())
