#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyzer.py — 面经智能分析引擎（功能 1-6）

1. 根据岗位 JD 判断岗位做什么（职责画像）
2. 根据 JD 判断我的简历匹配度
3. 从历史面经定位最匹配的面试、问题、最佳回答
4. 预判面试会问的问题
5. 基于新面经判断通过可能性（需真实 outcome 校准）
6. 基于新面经判断哪里答得好、哪里差

设计说明：本模块产出"结构化上下文 + 判断依据"，供调用方（AI / 命令行）结合
模型做最终报告。脚本内置启发式（关键词匹配、score 聚合、outcome 校准）给出可跑
的基础版答案，需要在会话中由 AI 注入更强的语义判断。

依赖：pyyaml；简历文件在**包根目录**的 resume.md（由 resume.example.md 复制而来）。
"""

import os
import re
import sys
import glob
import argparse
from collections import Counter, defaultdict

try:
    import yaml
except ImportError:
    yaml = None

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, ".."))
CARDS = os.path.join(ROOT, "cards")
# ⚠️ 简历与 JD 都在**包根目录**，不是 tools/ 下。
#    之前这里写的是 os.path.join(BASE, "resume.md")（即 tools/resume.md），
#    与全包其它模块（一律 BASE/../）以及文档里的目录树都不一致 ——
#    结果是用户按文档把 resume.md 放在根目录时，job 的「简历匹配度」整段
#    静默失效，只吐一句 error: 缺 JD 或简历。这是实测确认过的 bug。
#    tools/ 下的旧位置仍然兼容（万一有人已经放在那儿）。
def _first_existing(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[0]


RESUME = _first_existing(os.path.join(ROOT, "resume.md"),
                         os.path.join(BASE, "resume.md"))
JD_FILE = _first_existing(os.path.join(ROOT, "jd.txt"),
                          os.path.join(BASE, "jd.txt"))


# ---------- 数据加载 ----------

def load_cards():
    cards = []
    if yaml is None:
        return cards
    for p in sorted(glob.glob(os.path.join(CARDS, "I*.yaml"))):
        try:
            with open(p, "r", encoding="utf-8") as f:
                d = yaml.safe_load(f)
            if d:
                d["_file"] = os.path.basename(p)
                d["_id"] = d.get("id") or os.path.basename(p).split("_")[0]
                cards.append(d)
        except Exception as e:
            print(f"[warn] 解析失败 {os.path.basename(p)}: {e}", file=sys.stderr)
    return cards


def load_resume():
    if os.path.exists(RESUME):
        with open(RESUME, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def load_jd_text(jd=None):
    if jd:
        return jd
    if os.path.exists(JD_FILE):
        with open(JD_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# ---------- 工具 ----------

def _norm(s):
    return re.sub(r"[\s,，。;；/／·\-—()（）、]+", "", str(s)).lower()


# 领域关键词表（内容运营/社区方向）
COMMON_KW = [
    "内容", "社区", "创作者", "作者", "运营", "用户", "增长", "推荐", "分发",
    "策略", "冷启动", "社群", "活动", "标签", "内容池", "供给", "留存", "渗透",
    "UGC", "PGC", "MCN", "电商", "商业化", "付费", "出海", "本地化", "创作者激励",
]


class Analyzer:
    def __init__(self, jd=None):
        self.jd = jd or load_jd_text()
        self.resume = load_resume()
        self.cards = load_cards()

    # ---- 功能1: JD → 岗位职责画像 ----
    def analyze_job(self):
        """从 JD 提炼岗位职责/要求/目标（启发式+返回给AI补充）。"""
        jd = self.jd
        if not jd:
            return {"error": "未提供 JD"}
        tokens = _norm(jd)
        hits = [k for k in COMMON_KW if _norm(k) in tokens]
        # 尝试抽取"职责/要求"分节
        sections = {}
        for marker in ["岗位职责", "工作职责", "职位描述", "职责", "任职要求", "岗位要求", "工作内容"]:
            m = re.search(rf"{marker}[:：\n](.*?)(?=\n\n|$)", jd, re.S)
            if m:
                sec = m.group(1).strip()[:400]
                sections[marker] = sec
        return {
            "关键词命中": hits,
            "字数": len(jd),
            "疑似职责段落": sections,
            "提示": "以上为启发式提取，最终岗位职责画像需结合 AI 语义判断补充。"
        }

    # ---- 功能2: JD ↔ 简历匹配度 ----
    def match_resume(self):
        jd = self.jd
        resume = self.resume
        if not jd or not resume:
            missing = []
            if not jd:
                missing.append("JD")
            if not resume:
                missing.append("简历")
            return {
                "error": "缺 " + " 和 ".join(missing),
                "怎么修": (
                    "简历：把 resume.example.md 复制成 {}（包根目录），填好内容。"
                    .format(os.path.normpath(os.path.join(BASE, "..", "resume.md")))
                    if not resume else
                    "JD：用 --file <路径> 指定，或把 JD 存成 {}。"
                    .format(os.path.normpath(os.path.join(BASE, "..", "jd.txt")))
                ),
            }
        jd_n = _norm(jd)
        rs_n = _norm(resume)
        kv = [_norm(k) for k in COMMON_KW]
        jd_hit = [k for k in kv if k in jd_n]
        both = [k for k in jd_hit if k in rs_n]
        # 经历覆盖
        exp_keywords = ["UGC", "推荐策略", "内容池", "冷启动", "社群", "创作者",
                        "MCN", "渗透", "用户增长", "数据分析", "AI", "出海"]
        exp_hit = [k for k in exp_keywords if _norm(k) in jd_n and _norm(k) in rs_n]
        jd_only = [k for k in jd_hit if _norm(k) not in rs_n]
        score = round(len(both) / max(len(jd_hit), 1) * 100)
        return {
            "岗位需求关键词": jd_hit,
            "简历已覆盖": both,
            "简历缺(需补齐/软性)": jd_only,
            "关键经历覆盖": exp_hit,
            "粗匹配度%": score,
            "提示": "启发式评分；请结合 AI 语义、并从 reflection.weakness 补正面叙事。"
        }

    # ---- 功能3: 定位最匹配面经/问题/最佳回答 ----
    def most_relevant(self, topn=3, question_kw=None):
        """按 JD 与卡片 skills/question 相似度排序，找出最匹配的非场+问题+最佳回答。"""
        jd = self.jd
        if not jd:
            return {"error": "缺 JD"}
        jd_n = _norm(jd)
        scored = []
        for c in self.cards:
            inter = c.get("interview", {}) or {}
            text = (str(inter.get("company", "")) + " " +
                    str(inter.get("position", "")) + " " +
                    " ".join(str(s) for s in (c.get("skills", []) or [])) +
                    " " + " ".join(str(q.get("question", "")) for q in
                                   (c.get("questions", []) or []) if isinstance(q, dict)))
            txt_n = _norm(text)
            # 字符 bigram（Jaccard）相似度
            def _bigrams(s):
                return {s[i:i + 2] for i in range(max(len(s) - 1, 0))}
            jd_bg = _bigrams(jd_n)
            txt_bg = _bigrams(txt_n)
            inter = jd_bg & txt_bg
            union = jd_bg | txt_bg
            overlap = len(inter) / max(len(union), 1) * 100 if union else 0
            # 关键词命中
            kws = [_norm(k) for k in COMMON_KW]
            hit = sum(1 for k in kws if k in jd_n and k in txt_n)
            scored.append((hit, overlap, c))

        scored.sort(key=lambda x: (-x[0], -x[1]))
        top = scored[:topn]

        # 最佳回答：从最匹配场里挑 score 最高的问题
        out = []
        for hit, ov, c in top:
            inter = c.get("interview", {}) or {}
            qs = []
            for q in (c.get("questions", []) or []):
                if isinstance(q, dict) and q.get("question"):
                    qs.append(q)
            best = max(qs, key=lambda q: q.get("score", 0), default=None)
            out.append({
                "卡号": "{}_{}".format(c["_id"], inter.get("company", "")),
                "岗位": inter.get("position", ""),
                "匹配度信号": "强" if hit >= 3 else ("中" if hit >= 1 else "弱"),
                "命中共现词": hit,
                "最佳回答问题": best.get("question") if best else None,
                "该题自评": best.get("score") if best else None,
                "该题回答": best.get("how_answered") if best else None,
                "该题备注": best.get("note") if best else None,
            })
        return {"最匹配面试": out, "提示": "最佳回答基于卡片自评分最高的问题；可结合 AI 判断真正最能复用的。",
                "全部候选数": len(scored)}

    # ---- 功能4: 预判面试问题 ----
    def predict_questions(self, limit=12):
        freq = Counter()
        theme_q = defaultdict(list)
        for c in self.cards:
            for q in (c.get("questions", []) or []):
                if isinstance(q, dict) and q.get("question"):
                    theme = q.get("theme", "其他")
                    theme_q[theme].append(q["question"])
                    freq[q["question"]] += 1
        # 高频通用问题（跨场反复）
        common = [q for q, n in freq.most_common(20) if n >= 2]
        # 按 JD 关键词筛选题
        jd = self.jd
        pred = []
        if jd:
            jd_n = _norm(jd)
            for q, n in list(freq.items()):
                if any(k in jd_n for k in projectable()):
                    # 粗略：把含"内容/社区/增长"等主题的问题优先
                    if any(k in _norm(q) for k in ["指标", "怎么", "如何", "为什么", "case", "案例", "策略"]):
                        pred.append(q)
        # 主题分布
        theme_rank = sorted(theme_q.items(), key=lambda x: -len(x[1]))
        return {
            "反复出现的高频问题": common[:limit],
            "按主题分布": {t: len(qs) for t, qs in theme_rank},
            "可能被追问的方向(共现/主题)": list(dict(theme_rank).keys()),
            "提示": "建议在会话中由 AI 结合 JD 语义精调预测结果",
        }


def projectable():
    return ["内容", "社区", "增长", "策略", "运营", "用户"]
