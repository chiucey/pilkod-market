#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""boss.py —— Boss直聘岗位：解码 / 筛选分级 / 合并 / 备战分析

合并自：boss.py + boss_merge.py + boss_to_job.py

设计原则
--------
* **抓取**不在本文件里做。抓取依赖浏览器与登录态，交给 `tools/boss.mjs`（Node + CDP）
  与 `tools/boss_jd.mjs`（抓 JD 正文）。本文件只做**解码、筛选、合并、备战**，
  纯本地、不联网、可单独测试。
* **解码**：Boss 把薪资数字替换成 Unicode 私用区(PUA)字符。映射**不是**码位偏移，
  必须用实测表（见下方 PUA_TO_DIGIT）。曾误用 `U+E030`+n = n，导致薪资整体偏高一位。
* **筛选**：基于能力关键词 + 排除词，不需要公司历史。

用法
----
    python boss.py filter   --file boss_jobs.json [--out boss_筛选.md]
    python boss.py merge    --files boss_*.json --out boss_all.json
    python boss.py tojob    --jd boss_jd.json --out boss_JD分析.md [--top 8]
    python boss.py selftest                       # 回归自检（退出码非0即有回归）
    python boss.py decode   --text "..."          # 单条解码
    python boss.py keywords                       # 查看词表
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ─────────────────────────── PUA 薪资解码 ───────────────────────────
#
# Boss 用自定义字体 kanzhun-mix 把薪资数字替换成 Unicode 私用区(PUA)字符。
# 映射**不是**简单的码位偏移，必须用实测表：
# （曾误以为是 E030->0，实际差一位，导致薪资整体偏高）
#
#     \uE031 -> 0    \uE032 -> 1    \uE033 -> 2    \uE034 -> 3    \uE035 -> 4
#     \uE036 -> 5    \uE037 -> 6    \uE038 -> 7    \uE039 -> 8    \uE03A -> 9
#
# 验证方式（13/13 全中）：以页面自身接口
#   /wapi/zpgeek/search/joblist.json 返回的**明文 salaryDesc** 作真值，
#   与 DOM 卡片的原始 PUA 码位逐条对齐比对。位图字形比对亦独立佐证。
#
# 注意：textContent / innerText 返回的**都是** PUA 字符，
# 所以任何"清理私用区"的正则（replace(/[\uE000-\uF8FF]/g,'')）都会把数字抹掉。

PUA_TO_DIGIT = {
    0xE031: "0", 0xE032: "1", 0xE033: "2", 0xE034: "3", 0xE035: "4",
    0xE036: "5", 0xE037: "6", 0xE038: "7", 0xE039: "8", 0xE03A: "9",
}


def decode_pua(s: str) -> str:
    """把 PUA 数字字符还原成真数字（映射表见上）。"""
    if not s:
        return ""
    out = []
    for ch in s:
        out.append(PUA_TO_DIGIT.get(ord(ch), ch))
    return re.sub(r"\s+", " ", "".join(out)).strip()


def salary_mid(s: str):
    """取月薪中值(K/月)。

    注意 '·27薪' 是**年度发放月数**，岗位标注的 31-51K 本身即月薪，
    所以中值仍取 (31+51)/2，只是额外给出年包倍数（见 months_bonus）。

    '元/月' 形式（兼职常见）直接换算；'元/天'、'元/时' 按 21 天/月、8 时/天折算。
    """
    if not s:
        return None
    m = re.search(r"(\d+)-(\d+)\s*K", s)
    if m:
        return (int(m.group(1)) + int(m.group(2))) / 2
    m = re.search(r"(\d+)-(\d+)\s*元/月", s)
    if m:
        return (int(m.group(1)) + int(m.group(2))) / 2 / 1000
    m = re.search(r"(\d+)-(\d+)\s*元/天", s)
    if m:
        return (int(m.group(1)) + int(m.group(2))) / 2 * 21 / 1000
    m = re.search(r"(\d+)-(\d+)\s*元/[时小時]", s)
    if m:
        return (int(m.group(1)) + int(m.group(2))) / 2 * 8 * 21 / 1000
    return None


def months_bonus(s: str) -> int:
    m = re.search(r"·(\d+)薪", s or "")
    return int(m.group(1)) if m else 12


# ─────────────────────────── 筛选词表（可改） ───────────────────────────

# 命中即加分：写你自己的能力关键词
CORE_KEYWORDS: dict[str, list[str]] = {
    "内容生态": ["内容生态", "生态", "内容标准", "内容质量", "内容治理"],
    "内容运营": ["内容运营", "内容策略", "内容策划"],
    "社区运营": ["社区", "社群", "圈子"],
    "创作者运营": ["创作者", "作者运营", "达人", "KOL", "MCN"],
    "垂类运营": ["垂类", "品类", "行业运营"],
    "用户增长": ["用户增长", "增长", "拉新", "留存"],
    "用户运营": ["用户运营", "会员", "私域", "用户分层"],
    "活动运营": ["活动运营", "活动策划", "话题"],
    "产品运营": ["产品运营", "策略运营"],
    "推荐分发": ["推荐", "分发", "算法策略", "内容池"],
    "短视频": ["短视频", "抖音", "快手", "视频号", "B站"],
    "数据": ["数据分析", "数据运营"],
}

# 命中即排除（降级/错配/风险）。注意：**用工性质**不在这里，
# 见下方 classify_nature()——外包/兼职/实习是"类别"而非单纯"该排除"，
# 混在一个排除项里会丢掉信息（比如你想专挑外包、或只看实习时就没办法了）。
EXCLUDE_PATTERNS: dict[str, list[str]] = {
    "销售": [r"销售", r"电销", r"BD经理", r"招商"],
    "纯工程": [r"测试工程师", r"开发工程师", r"算法工程师", r"运维"],
    "直播带货": [r"带货", r"直播运营主播"],
    "客服": [r"客服"],
}

# ─────────────────────────── 用工性质分类 ───────────────────────────
#
# 三类性质**互不相同**，必须分开：
#   · 外包：正式雇佣（五险一金通常有），但劳动合同签第三方劳务公司。
#           影响：履历归属、晋升、转正机会、被裁风险。
#   · 兼职：非全日制/按次结算，无正式劳动关系。
#   · 实习：面向在校生，通常是转正前置。
#
# 判定优先级：实习 > 兼职 > 外包 > 正编
# （一个"外包岗的实习生"应归为实习，因为对应聘者的实际要求是学生身份）
#
# ⚠️ 关键词要放在**岗位名**里判断，不要混进 tags。
#    实测踩过坑：`线上` 这个弱词命中了"内容增长运营"的正常 tag
#    （"线上运营"），把正编岗误判成兼职。

NATURE_PATTERNS: list[tuple[str, list[str]]] = [
    ("实习", [
        r"实习", r"intern", r"在校", r"应届", r"管培生", r"校招", r"实践生",
        # ⚠️ "转正" 曾经在这张表里 —— 方向是**反的**。
        #    "有转正机会/可转正/转正编" 说的是这个岗位**能转为正编**，
        #    是多见于外包/实习岗的一句卖点，但它本身不是"实习"的信号；
        #    实测 "内容运营经理（有转正机会）" 被判成实习并直接归 C 级。
        #    现在改为：只有明确写"实习/Intern"才算实习，"转正"不再单独触发。
    ]),
    ("兼职", [
        r"兼职", r"part[- ]?time", r"小时工", r"日结", r"周结",
        r"临时工", r"短期工", r"众包", r"远程兼职",
        r"写手",
        # ⚠️ "自由职业" 与 "投稿" 曾是裸词，误判面很大：
        #    "内容运营-自由职业者优先"（说的是**优先考虑**自由职业者，岗位是正编）
        #    "新媒体运营（投稿）"（投稿只是内容形式）
        #    现改为要求它们与"兼职/招募/合作"同现，或出现在明确的兼职语境里。
        r"(兼职|招募|招聘|长期|大量).{0,6}(自由职业|写手|投稿)",
        r"(自由职业|写手|投稿).{0,6}(兼职|招募|招聘|合作)",
    ]),
    ("外包", [
        r"外包", r"派遣", r"驻场", r"人力外派", r"劳务",
        r"第三方", r"乙方驻场", r"OD岗", r"OD 岗",
    ]),
]

# 薪资形态也能佐证性质（弱信号，仅当岗位名没命中时用于兜底）
NATURE_SALARY_HINTS: list[tuple[str, list[str]]] = [
    ("实习", [r"元/天"]),
    ("兼职", [r"元/时", r"元/小时", r"元/次", r"元/篇"]),
]


def classify_nature(job: dict) -> str:
    """判定用工性质：正编 / 外包 / 兼职 / 实习。

    只看**岗位名 + 公司名**，不看 tags —— tags 里的"线上运营"这类词会造成误判。
    """
    name = f"{job.get('jobName', '')} {job.get('company', '')}"
    low = name.lower()

    for nature, pats in NATURE_PATTERNS:
        if any(re.search(p, low) for p in pats):
            return nature

    # 薪资形态兜底（岗位名没写性质时）
    sal = job.get("salary", "") or ""
    for nature, pats in NATURE_SALARY_HINTS:
        if any(re.search(p, sal) for p in pats):
            return nature

    return "正编"


# 各级别对"性质"的默认态度：
#   正编：不惩罚
#   外包：**降权但不排除**（-1.0，包住一次核心能力命中；你想专找外包时也不至于全被埋掉）
#   兼职/实习：默认排除（对已有正式工作经历的人来说通常是降级）
#
# 降权幅度是标定过的：命中 2 个核心词(2.0)的外包岗降权后 1.0，
# 加上薪资加分后才够 B 级；只命中 1 个词的会落到 C。这个分界比较符合直觉。
NATURE_PENALTY = {"正编": 0.0, "外包": -1.0, "兼职": -3.0, "实习": -3.0}
NATURE_DEFAULT_REJECT = {"兼职", "实习"}


def score_job(job: dict, keep_nature: set | None = None) -> dict:
    """给单个岗位打分。返回原 job + hits/excl/nature/mid/score。

    keep_nature：这些性质**不参与降权**（用户显式要看某类时用）。
    """
    blob = " ".join([
        job.get("jobName", ""),
        job.get("company", ""),
        " ".join(job.get("tags", []) or []),
    ])
    hits = [k for k, kws in CORE_KEYWORDS.items() if any(kw in blob for kw in kws)]
    excl = [k for k, pats in EXCLUDE_PATTERNS.items()
            if any(re.search(p, blob) for p in pats)]
    nature = classify_nature(job)
    mid = salary_mid(job.get("salary", ""))

    score = float(len(hits))
    if excl:
        score -= 3 * len(excl)
    if nature not in (keep_nature or set()):
        score += NATURE_PENALTY.get(nature, 0.0)
    if mid is not None:
        if mid >= 30:
            score += 1.5
        elif mid >= 25:
            score += 1
        elif mid < 18:
            score -= 1
    return {**job, "hits": hits, "excl": excl, "nature": nature,
            "mid": mid, "score": score}


def tier_of(r: dict, keep_nature: set | None = None) -> str:
    """分级。keep_nature 指定"不要因为性质而排除"的类别（如 {'外包'}）。"""
    keep = keep_nature or set()
    if r.get("nature") in NATURE_DEFAULT_REJECT and r["nature"] not in keep:
        return "C"
    if r["excl"]:
        return "C"
    if r["score"] >= 3.5:
        return "A"
    if r["score"] >= 2:
        return "B"
    return "C"


# ─────────────────────────── 命令 ───────────────────────────

def cmd_decode(a):
    print(f"输入: {a.text!r}")
    print(f"解码: {decode_pua(a.text)!r}")
    return 0


def cmd_keywords(a):
    print("核心命中词表：")
    for k, v in CORE_KEYWORDS.items():
        print(f"  {k}: {'/'.join(v)}")
    print("\n排除词表：")
    for k, v in EXCLUDE_PATTERNS.items():
        print(f"  {k}: {'/'.join(v)}")
    print("\n改词表：直接编辑 boss.py 的 CORE_KEYWORDS / EXCLUDE_PATTERNS")
    return 0


def cmd_filter(a):
    src = Path(a.file)
    if not src.exists():
        print(f"找不到输入文件: {src}")
        return 2
    data = json.loads(src.read_text(encoding="utf-8"))
    jobs = data["jobs"] if isinstance(data, dict) else data

    # --nature 用法：只看某种性质；--keep 用法：某性质不要因降权掉级
    keep = set()
    only = None
    if getattr(a, "nature", None):
        only = a.nature
        # 显式点名要看某性质时，就不该再按默认规则把它排除掉，
        # 否则 --nature 实习 会得到"20 条全在 C 级"这种自相矛盾的结果。
        keep.add(a.nature)
    if getattr(a, "keep", None):
        keep |= set(a.keep)

    rows = [score_job(j, keep) for j in jobs]
    if only:
        rows = [r for r in rows if r["nature"] == only]
    rows.sort(key=lambda r: (-r["score"], -(r["mid"] or 0)))
    groups = {"A": [], "B": [], "C": []}
    for r in rows:
        groups[tier_of(r, keep)].append(r)

    # 性质分布（先给个总览，避免"怎么全是实习"的困惑）
    nat_count = {}
    for r in rows:
        nat_count[r["nature"]] = nat_count.get(r["nature"], 0) + 1
    if nat_count:
        print("性质分布: " + "  ".join(
            f"{k}={v}" for k, v in sorted(nat_count.items(), key=lambda x: -x[1])))
        print()

    for tag, title in (("A", "A 级：推荐投"), ("B", "B 级：可投"), ("C", "C 级：排除")):
        g = groups[tag]
        print("=" * 92)
        print(f"{title}（{len(g)} 个）")
        print("=" * 92)
        for r in g:
            s = f"{r['mid']:.0f}K" if r["mid"] else "?"
            nat = "" if r["nature"] == "正编" else f"[{r['nature']}]"
            print(f"  {s:>6} {nat:<6} {r['jobName'][:32]:<34} {r['company'][:14]:<16} "
                  f"{'/'.join(r['hits'][:3])}")
            if r["excl"]:
                print(f"          └ 排除: {', '.join(r['excl'])}")
        print()

    print(f"汇总: A={len(groups['A'])}  B={len(groups['B'])}  C={len(groups['C'])}  共 {len(rows)}")
    print("提示: 用 --nature 外包/兼职/实习 只看某类；--keep 外包 让外包不因降权掉级")

    if a.out:
        out = Path(a.out)
        L = [f"# Boss 岗位筛选（{len(rows)} 个）\n",
             f"> 来源：{src.name}｜关键词命中 + 用工性质 + 薪资分级（PUA 已解码）\n",
             f"> 性质分布：" + "、".join(f"{k} {v}" for k, v in
                                        sorted(nat_count.items(), key=lambda x: -x[1])) + "\n"]
        for tag, title in (("A", "✅ A 级：推荐投"), ("B", "🟡 B 级：可投"), ("C", "🔴 C 级：排除")):
            g = groups[tag]
            L.append(f"\n## {title}（{len(g)} 个）\n")
            L.append("| 月薪 | 性质 | 年包 | 岗位 | 公司 | 命中能力 | 备注 |")
            L.append("|---|---|---|---|---|---|---|")
            for r in g:
                s = f"{r['mid']:.0f}K" if r["mid"] else "?"
                mb = months_bonus(r.get("salary", ""))
                mb_s = f"{mb}薪" if mb != 12 else "—"
                nat = r["nature"]
                note = f"排除：{','.join(r['excl'])}" if r["excl"] else " / ".join(r["hits"][:4])
                L.append(f"| {s} | {nat} | {mb_s} | {r['jobName']} | {r['company']} | "
                         f"{'/'.join(r['hits'][:3])} | {note} |")
        out.write_text("\n".join(L), encoding="utf-8")
        print(f"\n已写出 -> {out}")
    return 0


# ─────────────────────────── 自检（内置真值） ───────────────────────────
#
# 真值来源：Boss 页面自身接口 /wapi/zpgeek/search/joblist.json 返回的**明文**
# salaryDesc，与 DOM 卡片的原始 PUA 码位按岗位名逐条对齐。
# 这组真值**内置**在代码里，因此换任何机器都能离线验证解码器是否被改坏。
#
# 之所以需要自检：PUA 映射曾经被写错成 `\uE030`+n = n（差一位），
# 导致所有薪资整体偏高约一倍（12-20K 被解成 23-31K），
# 而错误结果**看起来依然合理**，常识无法发现。必须有回归测试兜住。

# (PUA 原始串, 期望解码结果) —— 每条都对应一个真实抓到的 DOM 值
SELFTEST_CASES = [
    ("\ue032\ue033-\ue033\ue031K", "12-20K"),
    ("\ue032\ue036-\ue033\ue036K", "15-25K"),
    ("\ue036\ue031-\ue033\ue036\ue031\u5143/\u65f6", "50-250元/时"),
    ("\ue032\ue031-\ue032\ue036K", "10-15K"),
    ("\ue032\ue032-\ue033\ue033K\u00b7\ue032\ue037\u85aa", "11-22K·16薪"),
    ("\ue032\ue036-\ue034\ue031K\u00b7\ue032\ue036\u85aa", "15-30K·15薪"),
    ("\ue032\ue036-\ue032\ue039K", "15-18K"),
    ("\ue032\ue036-\ue033\ue031K", "15-20K"),
    ("\ue033\ue031-\ue035\ue031K", "20-40K"),
    ("\ue032\ue032-\ue033\ue031K", "11-20K"),
    ("\ue033\ue031-\ue034\ue031K", "20-30K"),
    ("\ue039-\ue032\ue034K", "8-13K"),
    ("\ue033\ue031-\ue035\ue031K\u00b7\ue032\ue037\u85aa", "20-40K·16薪"),
]

# 薪资解析的期望值：(原始串, 月薪中值 K, 年包倍数)
SELFTEST_SALARY = [
    ("12-20K", 16.0, 12),
    ("11-22K·16薪", 16.5, 16),
    ("20-40K", 30.0, 12),
    ("200-300元/天", 5.25, 12),
]


def cmd_selftest(a):
    """验证 PUA 解码器与薪资解析未被改坏。失败则非 0 退出，可用于 CI/pre-commit。"""
    fails = []

    print("=" * 70)
    print("Boss 模块自检 —— PUA 薪资解码")
    print("=" * 70)
    ok = 0
    for raw, want in SELFTEST_CASES:
        got = decode_pua(raw)
        if got == want:
            ok += 1
        else:
            fails.append(f"decode_pua({raw!r}) = {got!r}，期望 {want!r}")
    print(f"  解码用例 {ok}/{len(SELFTEST_CASES)} 通过")
    if ok != len(SELFTEST_CASES):
        for f in fails:
            print(f"    ✗ {f}")

    print()
    print("=" * 70)
    print("Boss 模块自检 —— 薪资解析")
    print("=" * 70)
    ok2 = 0
    for raw, want_mid, want_months in SELFTEST_SALARY:
        mid = salary_mid(raw)
        mb = months_bonus(raw)
        if mid is not None and abs(mid - want_mid) < 0.01 and mb == want_months:
            ok2 += 1
        else:
            fails.append(
                f"salary_mid({raw!r}) = {mid}（期望 {want_mid}），"
                f"months_bonus = {mb}（期望 {want_months}）")
    print(f"  薪资用例 {ok2}/{len(SELFTEST_SALARY)} 通过")
    if ok2 != len(SELFTEST_SALARY):
        for f in fails[len(SELFTEST_CASES) - ok:]:
            print(f"    ✗ {f}")

    print()
    print("=" * 70)
    print("Boss 模块自检 —— 用工性质分类")
    print("=" * 70)
    # 这些样本全部来自真实抓取结果，附期望性质
    nature_probes = [
        ({"jobName": "内容运营实习生", "company": "某科技公司",
          "tags": ["经验不限"], "salary": "200-300元/天"}, "实习"),
        ({"jobName": "27实习转正-内容运营 (MJ049845)", "company": "某教育公司",
          "tags": [], "salary": "10-15K·14薪"}, "实习"),
        ({"jobName": "（J71494）内容运营【实习】", "company": "某公司",
          "tags": [], "salary": "面议"}, "实习"),
        ({"jobName": "抖音图文内容运营(线上)", "company": "某OTA公司",
          "tags": [], "salary": "50-250元/时"}, "兼职"),
        ({"jobName": "新媒体内容运营（兼职）", "company": "某科技公司",
          "tags": [], "salary": "5000-15000元/月"}, "兼职"),
        ({"jobName": "内容运营/push 运营（外包）", "company": "某公司",
          "tags": [], "salary": "8-9K"}, "外包"),
        ({"jobName": "H94675岗 产品运营-J12809-大厂外包岗", "company": "某技术公司",
          "tags": [], "salary": "21-24K"}, "外包"),
        # 关键反例：tags 里有"线上运营"但这是正编岗（旧实现会误判成兼职）
        ({"jobName": "内容增长运营", "company": "某生活服务平台",
          "tags": ["线上运营", "数据分析"], "salary": "30-40K"}, "正编"),
        # 关键优先级：外包公司的实习岗应判为"实习"（对应聘者的实际要求是学生）
        ({"jobName": "内容运营实习生（外包项目）", "company": "某劳务",
          "tags": [], "salary": "150-200元/天"}, "实习"),
        ({"jobName": "社区内容运营", "company": "某互联网公司",
          "tags": ["5-10年"], "salary": "20-40K"}, "正编"),
        # ── 误判回归（2026 审计发现，均为"词表裸词"造成的假阳性）──
        # "有转正机会"说的是**能转正编**，方向与"实习"相反。
        # 旧词表里有裸词 r"转正"，直接把它判成实习并归 C 级。
        ({"jobName": "内容运营经理（有转正机会）", "company": "某公司",
          "tags": [], "salary": "15-25K"}, "正编"),
        # "自由职业者优先"是**优先条件**，不是岗位性质。
        ({"jobName": "内容运营-自由职业者优先", "company": "某公司",
          "tags": [], "salary": "12-20K"}, "正编"),
        # "投稿"只是内容形式。
        ({"jobName": "新媒体运营（投稿）", "company": "某公司",
          "tags": [], "salary": "10-18K"}, "正编"),
        # 但写手/自由职业出现在真实的兼职语境里仍要判出来。
        ({"jobName": "内容写手招募（兼职）", "company": "某公司",
          "tags": [], "salary": "面议"}, "兼职"),
    ]
    ok4 = 0
    for job, want in nature_probes:
        got = classify_nature(job)
        if got == want:
            ok4 += 1
        else:
            fails.append(f"classify_nature({job['jobName'][:20]!r}) = {got}，期望 {want}")
    print(f"  性质用例 {ok4}/{len(nature_probes)} 通过")
    for job, want in nature_probes:
        got = classify_nature(job)
        mark = "✓" if got == want else "✗"
        print(f"    {mark} [{got}] {job['jobName'][:34]:<36} (期望 {want})")

    print()
    print("=" * 70)
    print("Boss 模块自检 —— 分级")
    print("=" * 70)
    # 合成样本：验证分级与排除词是否按预期工作
    probes = [
        ({"jobName": "社区内容运营", "company": "某互联网公司", "tags": ["5-10年"],
          "salary": "20-40K"}, "A", "高薪+双命中核心能力"),
        ({"jobName": "内容运营", "company": "某小公司", "tags": [],
          "salary": "8-12K"}, "C", "低薪、仅单命中"),
        ({"jobName": "内容运营-大厂外包岗", "company": "某外包",
          "tags": [], "salary": "20-30K"}, "C", "外包降权(-1.0)，弱命中落到 C"),
        ({"jobName": "社区内容运营-外包岗", "company": "某外包",
          "tags": [], "salary": "20-30K"}, "B", "外包但命中双核心，仍可投"),
        ({"jobName": "内容运营实习生", "company": "某公司", "tags": [],
          "salary": "200-300元/天"}, "C", "实习默认排除"),
    ]
    ok3 = 0
    for job, want_tier, desc in probes:
        r = score_job(job)
        got = tier_of(r)
        if got == want_tier:
            ok3 += 1
        else:
            fails.append(f"{desc}: tier={got}，期望 {want_tier}（score={r['score']}）")
    print(f"  分级用例 {ok3}/{len(probes)} 通过")
    for job, want_tier, desc in probes:
        r = score_job(job)
        mark = "✓" if tier_of(r) == want_tier else "✗"
        print(f"    {mark} [{tier_of(r)}] nature={r['nature']:<4} score={r['score']:<6} {desc}")

    print()
    print("=" * 70)
    if fails:
        print(f"自检失败：{len(fails)} 项")
        for f in fails:
            print(f"  ✗ {f}")
        print()
        print("提示：PUA 映射表在 boss.py 顶部 PUA_TO_DIGIT；性质词表在 NATURE_PATTERNS；")
        print("      验证方法见 tools/BOSS.md「如何得到真值」。")
        return 1
    print("✅ 全部通过（解码 / 薪资解析 / 性质分类 / 分级）")
    print("=" * 70)
    return 0


# ─────────────────────────── merge：合并多轮抓取 ───────────────────────────
#
# 为什么需要：Boss 搜索接口返回 total≈300，但翻到第 6 页会被风控拦
# （{"code":37,"message":"您的环境存在异常."}）。即使每页间隔 3.5 秒、
# 被拦后退避 30 秒重试，第 6 页依然被拒。所以**单次查询上限 = 5 页 × 30 = 150 条**，
# 这是风控阈值而非配置项。
#
# 但风控是按"单次查询"计的 —— 换关键词/换筛选条件可各拿一份，合并去重后总量远超 150。

def cmd_merge(a):
    paths = []
    for f in a.files:
        hits = glob.glob(f)
        paths.extend(hits if hits else [f])

    merged = {}
    for p in paths:
        if not Path(p).exists():
            print(f"跳过（不存在）: {p}")
            continue
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
            jobs = d.get("jobs", d) if isinstance(d, dict) else d
        except Exception as e:
            print(f"跳过（解析失败 {e}）: {p}")
            continue

        added = 0
        dropped_nameless = 0
        dup_kept = 0
        for j in jobs:
            name = j.get("jobName") or ""
            comp = j.get("company") or ""
            if not name:
                # 没有岗位名的行无法去重也无法使用 —— 丢掉，但**必须报数**。
                # 旧版静默 continue，用户只看到"读入 5 新增 2"，
                # 会误以为差值是自己去重的结果（实测确有 3 条被无声丢弃）。
                dropped_nameless += 1
                continue
            key = f"{name}|{comp}"
            rec = {
                "jobName": name,
                "company": comp,
                "salary": j.get("salary") or j.get("salaryDesc") or "",
                "location": j.get("location") or "",
                "tags": j.get("tags") or [],
                "href": j.get("href") or "",
            }
            if not rec["location"]:
                loc = j.get("location") or ""
                if not loc and j.get("cityName"):
                    loc = j["cityName"] + ("·" + j["areaDistrict"] if j.get("areaDistrict") else "")
                rec["location"] = loc
            if not rec["tags"]:
                rec["tags"] = [t for t in [j.get("jobExperience"), j.get("jobDegree")] if t] + \
                    (j.get("skills") or [])
            if not rec["href"] and j.get("securityId"):
                rec["href"] = f"/job_detail/{j['securityId']}.html"

            if key not in merged:
                merged[key] = rec
                added += 1
            else:
                # ⚠️ 同 key 但薪资不同 = 很可能是同公司同名的**两个不同岗位**（高低配），
                #    旧版"先到先得"会静默丢掉后来的那条，而且结果依赖 --files 顺序
                #    （实测交换顺序后保留的从 10-20K 变成 90-100K）。
                #    这里改为保留**薪资更高**的那条（更可能是用户想看的），并计数；
                #    若薪资相同则视为真重复，静默跳过（正常去重）。
                dup_kept += 1
                old_mid = salary_mid(merged[key].get("salary") or "")
                new_mid = salary_mid(rec.get("salary") or "")
                if new_mid is not None and (old_mid is None or new_mid > old_mid):
                    merged[key] = rec
        note = f"读入 {len(jobs):>4} 条，新增 {added:>4}，累计 {len(merged)}"
        if dropped_nameless:
            note += f"，**丢弃无名 {dropped_nameless} 条**"
        if dup_kept:
            note += f"，同名同司重复 {dup_kept} 条（保留薪资更高者）"
        print(f"  {Path(p).name:<34} {note}")

    # 空结果不覆盖已有文件 —— 一次 glob 写错就能把辛苦合并的岗位池清空，
    # 而旧版会在 rc=0 的情况下照写不误。
    out = Path(a.out)
    if not merged and out.exists() and out.stat().st_size > 0:
        print(f"[中止] 本次合并结果为 0 条，而 {out.name} 已有内容 —— 不覆盖。")
        print("       若确实想清空，请先手动删除该文件，或另指定 --out。")
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "captured_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "sources": [Path(p).name for p in paths],
        "count": len(merged),
        "jobs": list(merged.values()),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"合并完成：{len(merged)} 条（去重后）-> {out}")
    print()
    print("说明：Boss 单次查询上限 150 条（第 6 页触发风控 code 37），")
    print("      想要更多岗位，正确做法是**换关键词多抓几轮再合并**。")
    return 0


# ─────────────────────────── tojob：JD → 备战分析 ───────────────────────────

def cmd_tojob(a):
    """把抓到的 JD 逐条喂给 skill 的 job 命令，产出备战分析。"""
    src = Path(a.jd)
    if not src.exists():
        print(f"找不到: {src}")
        return 2
    data = json.loads(src.read_text(encoding="utf-8"))
    jobs = [j for j in data.get("jobs", []) if j.get("jdLen", 0) > 150]
    jobs.sort(key=lambda j: -j["jdLen"])
    jobs = jobs[: a.top]

    if not jobs:
        print("没有可分析的 JD（jdLen>150 的为空）。先跑 node boss_jd.mjs 抓 JD。")
        return 2

    blocks = []
    for i, j in enumerate(jobs, 1):
        print("=" * 78)
        print(f"[{i}/{len(jobs)}] {j['jobName']} @ {j['company']}  {j['salary']}")
        print("=" * 78)

        # ⚠️ 临时文件两个问题，都改掉：
        #   ① 旧版写在 HERE（= tools/，skill 包内）—— skill 要分发给别人，
        #      不该往里写运行产物。改写到系统临时目录。
        #   ② 旧版只在成功路径 unlink，没有 try/finally：一旦 subprocess 抛异常
        #      或被 Ctrl-C，临时文件就留在包里。改成 finally 保证清理。
        tmp = Path(tempfile.gettempdir()) / f"mj_boss_jd_tmp_{os.getpid()}_{i}.txt"
        try:
            tmp.write_text(
                f"公司：{j['company']}\n岗位：{j['jobName']}\n薪资：{j['salary']}\n\n{j['jd']}\n",
                encoding="utf-8")
            r = subprocess.run([sys.executable, str(HERE / "main.py"), "job", "--file", str(tmp)],
                               capture_output=True, cwd=str(HERE))
            # Windows 子进程默认 GBK stdout，需按 UTF-8 优先解码，否则中文乱码
            out = ""
            for enc in ("utf-8", "gbk", "cp936"):
                try:
                    out = r.stdout.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if not out:
                out = r.stdout.decode("utf-8", errors="replace")
        finally:
            # finally 保证即使 subprocess 抛异常 / 被 Ctrl-C 也清掉临时文件
            try:
                tmp.unlink()
            except OSError:
                pass

        print(out[:1600])
        blocks.append(f"## {i}. {j['jobName']} @ {j['company']}（{j['salary']}）\n\n```\n{out[:2500]}\n```\n")

    if a.out:
        Path(a.out).write_text(
            f"# Boss JD 逐条备战分析\n\n> 来源：{src.name}｜共 {len(jobs)} 条\n\n" + "\n".join(blocks),
            encoding="utf-8")
        print(f"\n已写出 -> {a.out}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Boss直聘岗位：解码 PUA 薪资 + 筛选 + 合并 + 备战")
    sub = ap.add_subparsers(dest="cmd")

    d = sub.add_parser("decode", help="解码 PUA 薪资字符串（单条）")
    d.add_argument("--text", required=True)
    d.set_defaults(fn=cmd_decode)

    k = sub.add_parser("keywords", help="查看筛选词表")
    k.set_defaults(fn=cmd_keywords)

    f = sub.add_parser("filter", help="对抓取结果做分级筛选")
    f.add_argument("--file", required=True, help="boss.mjs 输出的 json")
    f.add_argument("--out", help="写出 markdown 报告")
    f.add_argument("--nature", choices=["正编", "外包", "兼职", "实习"],
                   help="只看某种用工性质（正编=排除兼职/实习，外包保留但降权）")
    f.add_argument("--keep", nargs="*", choices=["正编", "外包", "兼职", "实习"],
                   help="指定性质不因降权掉级，如 --keep 外包")
    f.set_defaults(fn=cmd_filter)

    m = sub.add_parser("merge", help="合并多轮抓取结果（突破单次 150 条上限）")
    m.add_argument("--files", nargs="+", required=True, help="抓取结果 json（支持通配符）")
    m.add_argument("--out", required=True)
    m.set_defaults(fn=cmd_merge)

    tj = sub.add_parser("tojob", help="把抓到的 JD 逐条喂给 job 做备战分析")
    tj.add_argument("--jd", required=True, help="boss_jd.mjs 的输出")
    tj.add_argument("--out", help="汇总 markdown")
    tj.add_argument("--top", type=int, default=8, help="只分析前 N 条")
    tj.set_defaults(fn=cmd_tojob)

    st = sub.add_parser("selftest", help="自检：验证 PUA 解码/薪资解析/分级未被改坏")
    st.set_defaults(fn=cmd_selftest)

    a = ap.parse_args()
    if not getattr(a, "fn", None):
        ap.print_help()
        return 1
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
