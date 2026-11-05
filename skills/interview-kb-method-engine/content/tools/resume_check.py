#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skill v3「简历修改」阶段 — 结构化简历的判定脚本（validate 雏形）。

校验一份"结构化简历源"(YAML) 是否符合 skill_v3_简历修改阶段_schema.md 的规则：

硬规则（fail，exit 1）:
  - 顶层要有 experiences[]，且每项是映射
  - 每个 experience:
      * company/role/period 至少 company 非空
      * headline 非空（soft：建议带数据，警告）
      * bullets 非空 且 >= MIN_BULLETS（默认 2）
      * 每条 bullet 含 action + metric，且 metric 必须含"对比/提升"语义（硬）
  - 可选 skills[] 应为 list

软规则（warn）:
  - headline 未带数据（→仅提示）
  - bullet 缺 goal（→提示挂靠目标）
  - metric 只有绝对数、无前后对比（这部分会走 FAIL，见下）

对比语义识别（metric）：
  命中任一即为"合格对比"：→ ｜ % ｜ 倍 ｜ + ｜ 提升 ｜ 增长 ｜ 翻 ｜ 涨 ｜ 从…至… ｜ 至
  若 metric 里只有纯数字且无上述标记 → 判 FAIL（"数据要看到提升"为硬规则）。

个人总结 / 技能特长（**只作用于这一部分**），5 条经验规则：
  ①【硬】无产出的性格空话一律不要
      反例：开朗大方 / 认真负责 / 做事踏实 / 有较强的团队精神
      理由：人人可写、无法验证、占篇幅且不加分。
  ②【软】性格可以写，但必须与"做事方式/工作场景"结合
      正例：习惯从团队与业务视角想问题，注重长期价值；带过 6 人小组，
            连续两个季度交付达标。
      反例：认真负责、性格开朗（只有性格，没有做事方式与结果）
      判据：出现性格词时，句内要有 工作/业务/团队/执行/目标 等场景词。
  ③【软】写"做了什么"要有结果。不必是硬指标，但要有产出。
      反例：「有 X 年经验，了解 A-B-C 全链路」——纯能力声明，零产出。
      注：已按规则②与做事结合的性格句会被豁免，不会被本条误伤。
  ④【软】第一条建议是"过去重点工作/亮点概述"
      让人先看到你的主线，而不是从零散的兴趣开始读。
  ⑤【软】兴趣爱好必须带产出或结果
      正例：数码自媒体主笔（某平台 10 万粉丝），单条曝光 50 万+
      反例：喜欢摄影、热爱旅行、爱好阅读

  ⚠️ 作用范围：只检查「总结/技能特长」类字段（见 SUMMARY_FIELDS）。
     字段叫法差异极大 —— summary / 个人总结 / 自我评价 / 技能特长 /
     个人优势 / 核心能力 / 自我描述 … 都在白名单里。
     **不做全字段扫描**：那会误伤经历块（实测经历 headline 写"认真负责"
     会被规则①误报）。你的简历若不用这些字段名，这部分就跳过不检查。

用法:
  python resume_check.py --file <resume_source.yaml>
  python resume_check.py --file <file> --min-bullets 2
  python resume_check.py --file <file> --suggest    # 额外输出"补料建议"
  python resume_check.py selftest                   # 自检规则与作用范围
"""
import sys, os, re, glob

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except Exception:
    print("[ERR] 需要 pyyaml: pip install pyyaml"); sys.exit(2)

BASE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.normpath(os.path.join(BASE, "..", "cards"))

# 对比/提升语义标记（用于判定 metric 是否是"对比数据"）
GAIN_RE = re.compile(r"(→|%|倍|\+ |提升|增长|上涨|翻|涨|从.{0,12}[至到]|至|\d+\s*→\s*\d+)")

DEFAULT_MIN_BULLETS = 2


def has_gain(metric: str) -> bool:
    """metric 是否体现 before→after 或 提升语义。"""
    if not metric:
        return False
    if GAIN_RE.search(metric):
        return True
    # 纯数字/孤数但无对比标记 → 不合格
    return False


def load(fp):
    with open(fp, encoding="utf-8") as f:
        return yaml.safe_load(f.read())


def load_card_gain_snippets(limit=12):
    """从 cards/*.yaml 召回"含对比/提升语义"的量化句式，作为补料参照。

    抽取来源：questions[].how_answered + result.reason + reflection 中命中 GAIN_RE 的短句。
    返回 [(card, snippet)]。纯参考，不改任何简历。
    """
    out = []
    for fp in glob.glob(os.path.join(CARDS, "I*.yaml")):
        try:
            with open(fp, encoding="utf-8") as f:
                d = yaml.safe_load(f.read())
        except Exception:
            continue
        cid = os.path.basename(fp).split("_")[0]
        inter = (d.get("interview", {}) or {}) if isinstance(d, dict) else {}
        company = inter.get("company", "") or ""
        parts = []
        for q in (d.get("questions", []) or []) if isinstance(d, dict) else []:
            if isinstance(q, dict) and q.get("how_answered"):
                parts.append(str(q["how_answered"]))
        res = d.get("result", {}) or {} if isinstance(d, dict) else {}
        for k in ("reason", "signal"):
            if res.get(k):
                parts.append(str(res[k]))
        ref = d.get("reflection", {}) or {} if isinstance(d, dict) else {}
        for k in ("strength", "improvement"):
            if ref.get(k):
                parts.append(str(ref[k]))
        for p in parts:
            for seg in re.split(r"[;；。\n]", p):
                seg = seg.strip()
                if len(seg) >= 8 and has_gain(seg):
                    out.append((f"{cid}·{company}", seg))
                    break
        if len(out) >= limit:
            break
    return out[:limit]


def suggest_fixes(data):
    """针对每条 metric 生成"补料建议"，并附召回的量词句式参考。"""
    refs = load_card_gain_snippets()
    tips = []
    for i, blk in enumerate((data.get("experiences") or []) or []):
        for j, b in enumerate(((blk.get("bullets") if isinstance(blk, dict) else []) or [])):
            if not isinstance(b, dict):
                continue
            met = str(b.get("metric", "") or "").strip()
            if not has_gain(met):
                tips.append(
                    f"experience[{i}].bullets[{j}] 补料建议：metric 需改成 before→after（如 X → X' 或 提升N%/N倍），"
                    f"不要只写一件事或一个孤数。可参考：把『做了什么』对到『哪个指标从不以什么变了』。"
                )
    return tips, refs


def _norm(s):
    return re.sub(r"[\s,，。;；/／·\-—()（）、]+", "", str(s)).lower()


def jdtips(data, jd):
    """可选：传入 JD 时，给"哪几条经历/哪个数据更该强调"的软建议（不做硬校验）。

    逻辑：JD 归一化后与每条 bullet 的 action/metric/goal 做关键词重合，命中多者排前。
    输出 [ (位置, 理由) ]。JD 为空返回 []。
    """
    if not jd:
        return []
    jd_n = _norm(jd)
    scored = []
    for i, blk in enumerate((data.get("experiences") or []) or []):
        if not isinstance(blk, dict):
            continue
        hl = _norm(blk.get("headline", "") or "")
        for j, b in enumerate((blk.get("bullets") or []) or []):
            if not isinstance(b, dict):
                continue
            act = _norm(b.get("action", "") or "")
            met = _norm(b.get("metric", "") or "")
            goal_n = _norm(b.get("goal", "") or "")
            # 与 JD 的 n-gram 重叠（2-gram）
            def grams(s):
                return {s[k:k + 2] for k in range(max(len(s) - 1, 0))}
            jg = grams(jd_n)
            overlap = len(jg & grams(act + met + goal_n))
            scored.append((overlap, i, j))
    scored.sort(key=lambda x: -x[0])
    tips = []
    for ov, i, j in scored:
        if ov <= 0:
            break
        tips.append(
            (f"experience[{i}].bullets[{j}]",
             f"与 JD 共现信号 {ov}，建议将此条成果的词/数靠前、对齐 JD 关键词")
        )
    return tips[:6]


def check(data, min_bullets=DEFAULT_MIN_BULLETS):
    errs, warns = [], []

    if not isinstance(data, dict):
        return [("[STRUCT]", "顶层不是映射")], []

    exps = data.get("experiences")
    if exps is None:
        errs.append(("[ERR]", "缺顶层 experiences[] 列表"))
        exps = []
    if not isinstance(exps, list):
        errs.append(("[ERR]", "experiences 应为列表"))
        return errs, warns

    n = 0
    for i, blk in enumerate(exps):
        n += 1
        tag = f"experience[{i}]"
        if not isinstance(blk, dict):
            errs.append((tag, "这一项不是映射(dict)")); continue
        # 必填：company
        if not str(blk.get("company", "")).strip():
            errs.append((tag, "缺 company"))
        # headline 非空
        hl = str(blk.get("headline", "") or "").strip()
        if not hl:
            errs.append((tag, "缺 headline（1-2 句全局概括）"))
        else:
            # headline 建议带数据（软）
            if not has_gain(hl):
                warns.append((tag + ".headline", "建议带数据（before→after 或提升%），当前未识别到对比语义"))

        bullets = blk.get("bullets")
        if not isinstance(bullets, list) or len(bullets) == 0:
            errs.append((tag, "缺 bullets[]（成果点）"))
            continue
        if len(bullets) < min_bullets:
            errs.append((tag, f"bullets 条数 {len(bullets)} < 最少 {min_bullets} 条"))
        for j, b in enumerate(bullets):
            btag = f"{tag}.bullets[{j}]"
            if not isinstance(b, dict):
                errs.append((btag, "这一项不是映射(dict)")); continue
            act = str(b.get("action", "") or "").strip()
            met = str(b.get("metric", "") or "").strip()
            goal = str(b.get("goal", "") or "").strip()
            if not act:
                errs.append((btag, "缺 action（动词开头，做了什么）"))
            if not met:
                errs.append((btag, "缺 metric（数据）"))
            else:
                if not has_gain(met):
                    errs.append((btag, f"metric「{met[:30]}」无对比/提升语义，需 before→after 或 提升N%/N倍"))
            if not goal:
                warns.append((btag, "建议补 goal（这条成果挂靠的目标/指标）"))

    sk = data.get("skills")
    if sk is not None and not isinstance(sk, list):
        warns.append(("skills", "应为 list"))

    # ── 个人总结 / 自我评价 / 兴趣爱好（规则见 SUMMARY_RULES 注释）──
    check_summary(data, errs, warns)

    return errs, warns


# ─────────────────────── 个人总结校验（5 条经验规则）───────────────────────
#
# 背景：个人总结/自我评价这一块最容易写"没产出的空话"。
# 下面 5 条来自真实修改经验，但**只有第 1 条是硬规则**，其余为软提示
# —— 因为它们属于"写法偏好"，不该卡住人。
#
#   ① 【硬】无产出的性格空话一律不要
#      反例：开朗大方 / 认真负责 / 做事踏实 / 吃苦耐劳 / 团队精神
#      理由：这些词人人可写，无法验证，占篇幅且不加分。
#
#   ② 【软】性格可以写，但必须与"做事方式/工作场景"结合
#      正例：习惯从团队与业务视角想问题，注重长期价值；带过 6 人小组，
#            连续两个季度交付达标。
#      判据：出现性格词时，同一句/相邻句里要有"工作/业务/团队/执行/目标"等场景词。
#
#   ③ 【软】写"做了什么"要有结果，不必是硬指标但要有产出
#      正例：做了个自媒体账号 → 涨粉 xxx、曝光 xxx
#
#   ④ 【软】建议第一条是"过去重点工作/亮点的概述"
#      —— 让人一眼看到你的主线，而不是从零散兴趣开始读。
#
#   ⑤ 【软】兴趣爱好必须带产出或结果
#      正例：数码自媒体主笔（某平台 10 万粉），单条曝光 50 万+
#      反例：喜欢摄影、热爱旅行、爱好阅读

# 第 1 条：典型空话词（命中即报错）
EMPTY_PRAISE = [
    "开朗", "大方", "认真负责", "做事踏实", "踏实", "吃苦耐劳", "团队精神",
    "有责任心", "责任心强", "积极向上", "乐观", "勤奋", "努力", "善于沟通",
    "沟通能力强", "性格好", "为人诚恳", "诚实守信", "抗压能力强", "学习能力强",
    "有较强的", "良好的", "具有一定的",
]

# 第 2 条：场景词 —— 出现这些说明性格与做事方式结合了
SCENE_WORDS = [
    "工作", "业务", "团队", "执行", "目标", "交付", "协作", "项目", "决策",
    "视角", "长期", "共赢", "落地", "推动", "结果", "价值", "复盘", "方法",
]

# 性格/人格词
TRAIT_WORDS = ["性格", "人格", "MBTI", "INFP", "INFJ", "INTJ", "ENTJ", "ENFP",
               "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ESTP", "INTP", "ENTP"]

# 第 3、5 条：产出/结果信号
OUTCOME_RE = re.compile(
    r"(→|%|倍|\+ |提升|增长|上涨|翻|涨|达到|产出|结果|累计|曝光|粉丝|粉|播放|"
    r"点赞|收藏|转化|变现|收入|完成|上线|落地|覆盖|服务|辅导|签约|offer|"
    r"\d)")

# 兴趣爱好类措辞
HOBBY_WORDS = ["兴趣爱好", "爱好", "兴趣"]

# ── 哪些字段算「个人总结 / 技能特长」区（5 条规则只作用在这里）──
#
# 为什么不按单个字段名匹配：各人简历这部分叫法差异极大 ——
# summary / 个人总结 / 自我评价 / 技能特长 / 个人优势 / 核心能力 / 自我描述 …
# 只认 4 个名字会漏掉一大半（实测：技能特长/个人优势/核心能力/自我描述/个人简介 全部不识别）。
#
# 也不做"猜测式"全字段扫描：那会误伤经历块（实测：经历 headline 里写
# "认真负责地完成项目"会被规则①误报为硬错误）。
# 所以：**只认这张白名单**，用户没写这些字段就不检查。
SUMMARY_FIELDS = [
    "summary", "个人总结", "自我评价", "自我描述", "个人简介", "个人评价",
    "技能特长", "个人优势", "核心能力", "核心优势", "专业技能", "专业特长",
    "self_evaluation", "self_summary", "profile", "about", "highlights",
    "strengths", "skills_summary",
]


def _is_summary_field(key):
    """字段名是否属于「总结/技能特长」区。"""
    k = str(key).strip().lower()
    if k in SUMMARY_FIELDS:
        return True
    # 中文包含式匹配：容忍「个人总结（可选）」「技能特长/优势」等写法
    for token in ("总结", "自我评价", "自我描述", "个人简介", "技能特长",
                  "个人优势", "核心能力", "核心优势", "专业技能", "专业特长"):
        if token in str(key):
            return True
    return False


def _blocks(data):
    """取出「总结/技能特长」区的文本块（只取白名单字段）。"""
    out = []
    for k, v in (data.items() if isinstance(data, dict) else []):
        if not _is_summary_field(k) or v is None:
            continue
        if isinstance(v, str):
            if v.strip():
                out.append((k, [v]))
        elif isinstance(v, list):
            items = []
            for it in v:
                if isinstance(it, str):
                    if it.strip():
                        items.append(it)
                elif isinstance(it, dict):
                    # 支持 {text: "..."} / {content: "..."} / {title, desc}
                    for kk in ("text", "content", "desc", "description", "value", "name"):
                        if it.get(kk):
                            items.append(str(it[kk]))
                            break
                    else:
                        items.append(str(it))
            if items:
                out.append((k, items))
    return out


def check_summary(data, errs, warns):
    """按 5 条经验规则检查个人总结/自我评价/兴趣爱好。"""
    if not isinstance(data, dict):
        return

    blocks = _blocks(data)
    if not blocks:
        return

    for tag, items in blocks:
        joined = " ".join(items)

        # 规则 ① 空话（硬）
        for it in items:
            for w in EMPTY_PRAISE:
                if w in it:
                    errs.append((
                        tag,
                        f"含无产出的性格空话「{w}」→ 删掉，或改成「做了什么 + 结果」。"
                        f"（规则①：凡是没有产出的形容词一律不要）"))

        # 规则 ② 性格要与做事方式结合（软）
        if any(t in joined for t in TRAIT_WORDS) and not any(s in joined for s in SCENE_WORDS):
            warns.append((
                tag,
                "写了性格/人格，但没和「做事方式/工作场景」结合 → 建议补"
                "「这种性格在工作里体现为…」（规则②）"))

        # 规则 ⑤ 兴趣爱好要带产出（软）
        for it in items:
            if any(h in it for h in HOBBY_WORDS) and not OUTCOME_RE.search(it):
                warns.append((
                    tag,
                    "兴趣爱好未体现产出/结果 → 建议补数据（如粉丝量/曝光量/作品数）（规则⑤）"))
                break

        # 规则 ③ 逐条检查："做了某事"要有结果（软）
        # 注意要【逐条】而不是整段 —— 否则一条有数据就会掩盖其他空条。
        # 典型漏网：「有 X 年经验，了解 A-B-C 全链路」这类纯能力声明，零产出。
        #
        # ⚠️ 但要豁免「性格 + 做事方式结合」的句子（规则②明确保留的写法）：
        #    例："INFJ 型人格，善于站在团队与业务视角思考，注重长期价值与共赢"
        #    这类句子本来就不该硬塞数据 —— 它讲的是特质，不是成果。
        for idx, it in enumerate(items):
            if len(it.strip()) < 8:
                continue
            if OUTCOME_RE.search(it):
                continue
            # 豁免：含性格/人格词 且 含场景词（= 已按规则②与做事方式结合）
            is_trait_bound = (any(t in it for t in TRAIT_WORDS)
                              and any(s in it for s in SCENE_WORDS))
            if is_trait_bound:
                continue
            warns.append((
                f"{tag}[{idx}]" if len(items) > 1 else tag,
                f"这条没有任何产出/结果信号：「{it[:26]}…」→ 规则③要求"
                f"「做了的事要有结果」，不一定是硬指标，但至少要有产出"))

    # 规则 ④ 第一条建议是"重点工作/亮点概述"（软）
    for tag, items in blocks:
        if tag in ("summary", "个人总结", "自我评价", "self_evaluation") and items:
            first = items[0]
            # 第一条若看起来是兴趣/性格，提示把它挪后
            if any(h in first for h in HOBBY_WORDS) or any(t in first for t in TRAIT_WORDS):
                warns.append((
                    f"{tag}[0]",
                    "第一条像是兴趣/性格 → 建议把「过去重点工作/亮点概述」放在第一条，"
                    "让人先看到你的主线（规则④）"))



def main(argv=None):
    argv = list(argv) if argv else sys.argv[1:]
    if "--file" not in argv:
        print("用法: python resume_check.py --file <简历源.yaml> [--min-bullets 2] [--suggest] [--jd '...'] [--jd-file jd.txt]")
        return 2
    fp = argv[argv.index("--file") + 1]
    min_b = DEFAULT_MIN_BULLETS
    if "--min-bullets" in argv:
        try:
            min_b = int(argv[argv.index("--min-bullets") + 1])
        except Exception:
            min_b = DEFAULT_MIN_BULLETS
    want_suggest = "--suggest" in argv
    jd = ""
    if "--jd" in argv:
        jd = argv[argv.index("--jd") + 1]
    elif "--jd-file" in argv:
        jfp = argv[argv.index("--jd-file") + 1]
        try:
            with open(jfp, encoding="utf-8") as f:
                jd = f.read()
        except Exception as e:
            print(f"[ERR] 读 JD 失败: {e}"); return 2
    if not os.path.exists(fp):
        print(f"[ERR] 文件不存在: {fp}"); return 2
    try:
        data = load(fp)
    except Exception as e:
        print(f"[ERR] YAML 解析失败: {str(e).split(chr(10))[0]}"); return 2

    errs, warns = check(data, min_b)
    print(f"校验简历源: {os.path.basename(fp)}  （每经历块 ≥{min_b} 条成果点）")
    if errs:
        print(f"\n[❌] {len(errs)} 个硬错误:")
        for tag, msg in errs:
            print(f"  - [{tag}] {msg}")
    if warns:
        print(f"\n[WARN] {len(warns)} 个建议:")
        for tag, msg in warns:
            print(f"  - [{tag}] {msg}")
    if jd:
        jtips = jdtips(data, jd)
        print("\n—— JD 针对性建议（可选开关，不影响校验）——")
        if jtips:
            for pos, why in jtips:
                print(f"  · [{pos}] {why}")
        else:
            print("  （未识别到明显 JD 关键词重合，按结构校验结果为准。）")
    if want_suggest:
        tips, refs = suggest_fixes(data)
        print("\n—— 补料建议（人主辅机，不改你的简历）——")
        if tips:
            for t in tips:
                print("  · " + t)
        if refs:
            print("\n  同向量化句式参考（来自你面经库，纯参考）:")
            for cid, snip in refs:
                print(f"    [{cid}] {snip[:70]}")
        elif not tips:
            print("  （本简历源硬规则已全过，无需补料。）")
    if not errs and not warns:
        print("[OK] 简历结构化完全符合规则。")
    elif not errs:
        print("[OK] 硬规则通过（存在上述建议项）。")
    return 1 if errs else 0


# ─────────────────────── 自检（内置真值） ───────────────────────
#
# 个人总结这 5 条规则是「按经验标定」的，容易被后续改动无意破坏
# （尤其规则②「性格可写」与规则③「要有产出」本身存在张力）。
# 这里用 3 个固定案例锁住行为：真实总结 / 空话版 / 性格结合做事。

SELFTEST_CASES = [
    # (名称, 必须报错的词, 必须不报错的词, 期望是否通过硬规则)
    ("真实总结", None, None, True),
]

_SELFTEST_SUMMARY = {
    "good_trait": ("习惯站在团队与业务视角思考问题，注重长期价值与合作；"
                   "带过 6 人小组，连续两个季度交付达标",
                   "规则②：性格与做事结合 → 不该被规则③误伤"),
    "empty_praise": ("性格开朗大方，认真负责，做事踏实，有较强的团队精神",
                     "规则①：无产出的性格空话 → 必须报硬错误"),
    "pure_claim": ("有过垂类、内容社区、内容产运等工作经验，了解各类内容生产-推荐分发-用户消费全链路",
                   "规则③：纯能力声明无产出 → 应给出软提示"),
    "hobby_with_data": ("兴趣爱好：数码自媒体主笔（微博170万粉丝），单条内容三天累计曝光100万+",
                        "规则⑤：兴趣爱好带产出 → 不该提示"),
    "hobby_no_data": ("兴趣爱好：喜欢摄影、热爱旅行、爱好阅读",
                      "规则⑤：兴趣爱好无产出 → 应给出软提示"),
}


def selftest():
    """验证个人总结的 5 条规则未被改坏。"""
    print("=" * 70)
    print("简历校验自检 —— 个人总结 5 条规则")
    print("=" * 70)
    fails = []
    ok = 0

    base = {"experiences": [{
        "company": "示例", "role": "运营", "period": "2023-2024",
        "headline": "产能提升 50%",
        "bullets": [
            {"action": "做 A", "metric": "40 → 5000", "goal": "提产能"},
            {"action": "做 B", "metric": "提升 30%", "goal": "提渗透"},
        ]}]}

    for key, (text, desc) in _SELFTEST_SUMMARY.items():
        d = dict(base)
        d["summary"] = [text]
        errs, warns = check(d, 2)
        msgs = " ".join(m for _, m in errs) + " " + " ".join(m for _, m in warns)

        if key == "good_trait":
            good = ("INFJ" not in msgs) and (not any("规则③" in m for _, m in warns))
            want = "不该被任何规则命中"
        elif key == "empty_praise":
            good = any("规则①" in m for _, m in errs)
            want = "必须报规则①硬错误"
        elif key == "pure_claim":
            good = any("规则③" in m for _, m in warns)
            want = "应报规则③软提示"
        elif key == "hobby_with_data":
            good = not any("规则⑤" in m for _, m in warns)
            want = "不该报规则⑤"
        else:  # hobby_no_data
            good = any("规则⑤" in m for _, m in warns)
            want = "应报规则⑤软提示"

        if good:
            ok += 1
            print(f"  ✓ {desc}")
        else:
            fails.append(f"{desc}（期望：{want}）")
            print(f"  ✗ {desc}  实际输出: {msgs[:100]}")

    # ── 作用范围自检（这一条防的是"规则跑到别的字段去"）──
    print()
    print("=" * 70)
    print("简历校验自检 —— 5 条规则的作用范围")
    print("=" * 70)
    scope_cases = [
        # (字段名, 是否应被视为总结区)
        ("summary", True), ("个人总结", True), ("自我评价", True),
        ("技能特长", True), ("个人优势", True), ("核心能力", True),
        ("自我描述", True), ("个人简介", True), ("highlights", True),
        ("工作经历", False), ("experiences", False), ("教育背景", False),
        ("projects", False),
    ]
    for field, expect in scope_cases:
        got = _is_summary_field(field)
        if got == expect:
            ok += 1
            print(f"  ✓ 字段「{field}」{'算' if expect else '不算'}总结区")
        else:
            fails.append(f"字段「{field}」作用范围判定错（期望 {'算' if expect else '不算'}）")
            print(f"  ✗ 字段「{field}」判定错（期望 {'算' if expect else '不算'}，实际相反）")

    # 反例：经历块里的 headline 不该被总结规则命中
    d2 = dict(base)
    d2["experiences"] = [{
        "company": "X", "role": "Y", "period": "2023",
        "headline": "认真负责地完成了项目，产能提升 50%",
        "bullets": [{"action": "a", "metric": "1 → 2", "goal": "g"},
                    {"action": "b", "metric": "提升 30%", "goal": "g"}]}]
    errs2, _ = check(d2, 2)
    if not any("规则①" in m for _, m in errs2):
        ok += 1
        print("  ✓ 经历 headline 写「认真负责」不被规则①误伤")
    else:
        fails.append("经历 headline 被规则①误伤（作用范围失控）")
        print("  ✗ 经历 headline 被规则①误伤")

    print()
    total = len(_SELFTEST_SUMMARY) + len(scope_cases) + 1
    if fails:
        print(f"自检失败：{len(fails)}/{total}")
        for f in fails:
            print(f"  ✗ {f}")
        print()
        print("提示：规则定义在 resume_check.py 的 EMPTY_PRAISE / SCENE_WORDS /")
        print("      TRAIT_WORDS / OUTCOME_RE / check_summary()；")
        print("      作用范围由 SUMMARY_FIELDS + _is_summary_field() 限定。")
        return 1
    print(f"[OK] 全部通过（{ok}/{total}）")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    if "selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main())
