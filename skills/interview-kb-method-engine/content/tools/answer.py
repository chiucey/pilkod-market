#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""answer.py — 基于真实经历的「结构化应答框架 + 缺口标注」。

═══ 这个模块不做什么 ═══
它**不生成"完美答案"**。原因：AI 凭空写的答案一定好听，但你到了现场
说不出来 —— 因为它不来自你的真实经历，细节经不起追问。

═══ 这个模块做什么 ═══
把问题拆成四类，分别给不同处理：

  ① 你面过 & 答得好（历史 pass 场里自评高）→ **直接复用**，附出处
  ② 你面过 & 答砸了（历史 fail 场里自评低）→ **给改写方向**，用同题材
     答得好的那条做参照（横比"你这次差在哪"）
  ③ 你没面过，但同题材有素材 → **拼装框架**：从多场抽骨架，标出每条
     素材来自哪场、当时结果如何
  ④ 你没面过，也没有素材 → **明确标成「缺口」**，并给出补法

关键：④ 必须如实说出来。**框架的价值一半在"有什么"，一半在"缺什么"**。
把缺口藏起来、用漂亮话填满，就等于把面试官会戳穿的地方提前藏起来，
到现场炸得更响。

═══ 结构从哪来 ═══
框架骨架不预设模板，而是**从你自己的高分回答里归纳频次**：
你答得好的那些回答普遍覆盖了哪几层（背景/动作/数据/结果/反思），
就把那几层作为你的默认骨架。这样框架长得像你，而不是像范文。
"""
import os, sys, re, glob, argparse
from collections import Counter, defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except Exception:
    yaml = None

BASE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.normpath(os.path.join(BASE, "..", "cards"))

# ── 作答要素：用于从你的高分回答里归纳骨架 ──────────────────────────
# 每条 = (要素名, 命中特征)。命中即认为你的回答覆盖了这一层。
ELEMENTS = [
    ("背景/场景", ["当时", "背景", "业务是", "负责", "场景", "我们组", "接手", "接手时",
                 "当时是", "这块", "盘子"]),
    ("目标/问题", ["目标", "要解决", "痛点", "问题是", "难点", "挑战", "诉求", "最难",
                 "瓶颈", "卡点", "为什么做"]),
    ("动作/方法", ["我做了", "先", "然后", "拆", "定义", "搭建", "流程", "机制",
                 "策略", "方法", "分", "步骤", "路径", "手段", "打法", "对策",
                 "做了", "通过", "一是", "二是", "①", "②", "③", "1)", "2)"]),
    ("数据/指标", ["%", "％", "DAU", "GMV", "ROI", "转化", "留存", "曝光", "点击",
                 "涨", "降", "提升", "增长", "量级", "翻", "倍", "万", "千",
                 "个到", "占比", "同比", "环比"]),
    ("结果/产出", ["最终", "结果", "产出", "上线", "落地", "拿到", "做到", "完成",
                 "达成", "成功", "输了", "赢了", "被裁", "跑通"]),
    ("反思/迁移", ["复盘", "反思", "如果重来", "学到", "沉淀", "可复用", "迁移",
                 "下次", "改进", "教训"]),
]

# ── 高风险词：出现即为"回答里没有可验证的东西"，是缺口信号 ────────────
VAGUE_WORDS = ["大概", "差不多", "应该是", "可能吧", "忘了", "好像", "记不清",
               "挺好的", "还不错", "比较多", "一定的", "尽量", "努力"]

# ── 通用能力词：用于问题间"同题材"匹配 ────────────────────────────
TOPIC_KW = ["数据", "指标", "策略", "方法论", "复盘", "项目", "case", "案例",
            "动机", "规划", "稳定性", "业务理解", "情境", "自我认知", "反问",
            "创作者", "作者", "社区", "内容", "增长", "商业化", "团队", "协作",
            "冲突", "失败", "优点", "缺点", "薪资", "离职", "gap", "外包",
            "标签", "推荐", "分发", "冷启动", "活动", "用户", "运营", "产品"]


def load_cards():
    out = []
    if not yaml:
        return out
    for p in sorted(glob.glob(os.path.join(CARDS, "I*.yaml"))):
        try:
            d = yaml.safe_load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict):
            d["_id"] = d.get("id") or os.path.basename(p).split(".")[0]
            out.append(d)
    return out


def outcome_of(c):
    s = str((c.get("result") or {}).get("outcome") or "")
    if "pass" in s.lower():
        return "pass"
    if "fail" in s.lower() or "挂" in s:
        return "fail"
    return "?"


def company_of(c):
    return str((c.get("interview") or {}).get("company", ""))


def position_of(c):
    return str((c.get("interview") or {}).get("position", ""))


def _norm(s):
    return re.sub(r"\s+", "", str(s or "")).lower()


def _tokens(s):
    """中文按 2-gram + 英文/数字词切分，用于粗粒度相似度。"""
    s = _norm(s)
    bg = {s[i:i + 2] for i in range(max(len(s) - 1, 0))}
    words = set(re.findall(r"[a-z0-9]+", s))
    return bg | words


def similarity(a, b):
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta | tb), 1)


def elements_of(text):
    """判断一段回答覆盖了哪些作答要素。"""
    t = str(text or "")
    return [name for name, kws in ELEMENTS if any(k in t for k in kws)]


def vague_hits(text):
    t = str(text or "")
    return [w for w in VAGUE_WORDS if w in t]


def answer_quality(q):
    """单条回答的质量分（0-100）。

    组成：
      · 自评分（1-5 → 0-50）：这是最可信的一手信号
      · 要素覆盖（最多 30）：回答了"哪几层"
      · 具体性（最多 20）：有没有数字/专有细节
      · 空话扣分（−8/个）
    """
    sc = q.get("score")
    base = (float(sc) / 5.0 * 50.0) if isinstance(sc, (int, float)) else 25.0
    txt = str(q.get("how_answered") or "")
    els = elements_of(txt)
    cov = min(len(els), 6) / 6.0 * 30.0
    spec = min(len(re.findall(r"\d+", txt)), 6) / 6.0 * 20.0
    pen = len(vague_hits(txt)) * 8.0
    return max(0.0, min(100.0, base + cov + spec - pen)), els


def collect_qas(cards):
    """把所有卡的问答摊平成记录（带出处与结果）。"""
    rows = []
    for c in cards:
        out = outcome_of(c)
        for q in (c.get("questions") or []):
            if not isinstance(q, dict) or not q.get("question"):
                continue
            qual, els = answer_quality(q)
            rows.append({
                "卡号": c.get("_id"),
                "公司": company_of(c),
                "岗位": position_of(c),
                "轮次": str((c.get("interview") or {}).get("round", "")),
                "结果": out,
                "问题": str(q.get("question")),
                "主题": str(q.get("theme") or ""),
                "自评": q.get("score"),
                "回答": str(q.get("how_answered") or ""),
                "备注": str(q.get("note") or ""),
                "要素": els,
                "质量": round(qual, 1),
            })
    return rows


def infer_skeleton(rows, top_frac=0.25):
    """从**高质量回答**里归纳出你的默认作答骨架（按覆盖频次排序）。

    ═══ v3.6 改：不再按「那场过没过」筛样本，改成按**回答质量** ═══
    旧版：
        good = [r for r in rows if r["结果"] == "pass" and r["回答"]]
    这条规则是错的，而且错得很隐蔽 —— 它假设「场挂了 ⇒ 题答得差」。
    但真实情况是：**一场挂了不等于每道题都差**（可能输在 HC / 横向对比 /
    薪资），而且**答得好也可能挂**。

    实测反例（使用者指出）：
      「提升内容量的手段有哪些」这题，他答的是「话题活动 + 社群活动（社群为主力）」——
      这在**点评**的语境下是对的。缺的是成熟内容平台才有的
      「MCN 支撑 / 超头部达人供稿 / 定向邀约」，
      那是**业务形态的差异**，不是他的表达缺陷。
      但那场挂了 → 旧版把这套经验**排除在骨架之外**，
      于是"你答对的那套"反而不算数，只剩"答得弱"的被拿来参照。

    新规则：**只按质量分取**，与那场的成败解耦。
    理由与 build_one 的分栏口径一致（那里本来就写着
    "质量够高 → 可复用（即便那场最终挂了，这条回答本身是好的）"）——
    现在骨架也统一到这个口径，不再自相矛盾。

    仍保留 `结果` 字段供输出标注来源，但**不参与筛选**。
    """
    good = [r for r in rows if r["回答"]]
    if not good:
        return [], "无数据"
    # 按质量排序取头部；质量相同再看自评
    good.sort(key=lambda r: (-r["质量"], -(r["自评"] or 0)))
    k = max(3, int(len(good) * top_frac))
    sample = good[:k]
    # 标注样本里有几场其实是挂的 —— 让使用者知道"骨架不全是 pass 场的产物"
    _pf = sum(1 for r in sample if r["结果"] == "pass")
    basis = "高质量回答（%d 条中 %d 条来自 pass 场）" % (len(sample), _pf)
    cnt = Counter()
    for r in sample:
        for e in set(r["要素"]):
            cnt[e] += 1
    order = [name for name, _ in ELEMENTS]
    ranked = sorted(cnt.items(), key=lambda x: (-x[1], order.index(x[0]) if x[0] in order else 99))
    return ([{"要素": n, "覆盖率": round(v / max(len(sample), 1) * 100, 1),
              "样本数": len(sample)} for n, v in ranked], basis)


def find_material(rows, question, topn=5, exclude_cards=None):
    """为一句话找出你历史上最相关的问答素材。

    ⚠️ 相似度必须**夹在 [0,1]**。
      旧版把各种加权项直接 `sim += 0.25` / `sim += 0.06`（每个命中词一次，
      没有上限）加到 bigram 相似度上，于是出现 **1.06 / 1.37** 这种值 ——
      而下游的阈值判断写的是 `>= 0.40`「高置信」、`< 0.12`「缺口」，
      这些数字全部是按 0~1 区间标定的。超过 1 之后：
        · "低置信"区间（0.22~0.40）永远进不去 → 一律报"可直接复用"
        · 报告里显示的相似度数字也对用户失去意义
      实测：拿 某张真实卡 某电商垂类平台的真实题目跑，三条全是 1.0~1.37。
      现在改为：各项加权合计封顶，最终 clip 到 [0,1]。

    ⚠️ exclude_cards：把某些卡排除出素材池。
      用途是**避免自己匹配自己**：拿 I007 自己的题目去查，
      最相似的那条必然是 I007 里那道原题（base=1.0），于是报告说
      "可直接复用 —— 素材来自 I007"，而那句话本来就是从 I007 抄来的，
      等于什么都没告诉你。准备二战同一家公司时，应该看的是
      **别处**有没有可迁移的素材。所以要能把"当前这场"排除掉。
    """
    excl = set(exclude_cards or ())
    scored = []
    for r in rows:
        if excl and r.get("卡号") in excl:
            continue
        base = similarity(question, r["问题"])
        bonus = 0.0
        # 同主题加权：主题是人工标注的强信号
        if r["主题"] and r["主题"] in question:
            bonus += 0.25
        # 命中同题材词加权（每个词一次，但**总额封顶**）
        kw_hits = sum(1 for kw in TOPIC_KW
                      if kw in question and kw in (r["问题"] + r["主题"]))
        bonus += min(kw_hits * 0.06, 0.24)
        sim = max(0.0, min(1.0, base + bonus))
        if sim > 0:
            scored.append((sim, r))
    scored.sort(key=lambda x: (-x[0], -x[1]["质量"]))
    return scored[:topn]


def platform_gap_hint(question, ref_answer, mat=None):
    """判断这道题的缺口是不是**「业务形态差异」**而非「你没答好」。

    ═══ 为什么要单独判这一种（使用者指出的真实场景）═══
    面试题：「提升内容量的手段有哪些」
    他的答：「话题活动 + 社群活动（社群为主力）」
      —— 这在**点评**的语境下是对的。
    但那道题在**成熟内容平台**的语境下还应该有：
      MCN 支撑 / 超头部达人供稿 / 定向邀约
      —— 这些手段**点评没有**（业务形态不同）。

    这是**平台能力差异**，不是表达缺陷。两者改进方向完全相反：
      · 表达/结构问题 → 重写答案、补数据锚点
      · 业务形态问题 → 补业务认知，或意识到"该换到有这类手段的平台"

    旧版把这类卡一律判成「② 答得弱·需改写」，
    会让人去练一个**本来不需要练**的东西 —— 正是本项目
    反复强调的"别把方向问题误当能力短板"。

    判据（任一成立即提示，作为**附加说明**而非覆盖原判定）：
      ① 参照回答里出现了「话题/社群/活动」这类**通用打法**，但没提
         机构化/头部化手段（MCN、超头、定向邀约、供应商）——
         说明答的是"轻平台"的打法；
      ② 使用者自己在**别的卡**里答过这些重手段（说明不是不会，
         而是当时那个平台的形态用不上）。
    返回提示文本，或 None（不适用）。
    """
    HEAVY = ["MCN", "超头", "头部达人", "头部作者", "头部大V", "头部作者",
             "定向邀约", "供应商", "机构化", "签约作者", "代理商",
             "服务商", "经纪"]
    LIGHT = ["话题活动", "社群", "活动运营", "站内活动", "征文", "约稿"]

    def _has_placeholder(t):
        """判断回答是不是**占位摘要**（如「(列内容供给/作者/活动等手段)」）。

        真实卡里不少 how_answered 只写了摘要，没有全文 ——
        对这种素材不能凭空断言"他没提 MCN"，那会误报。
        """
        s = str(t or "").strip()
        return bool(s) and (s.startswith("(") or s.startswith("（")) and len(s) < 40

    txt = str(ref_answer or "")
    has_heavy = any(k in txt for k in HEAVY)
    has_light = any(k in txt for k in LIGHT)

    # 素材池里有没有"重手段"的证据（更可靠的信号）
    elsewhere = 0
    heavy_examples = []
    for _, r in (mat or []):
        a = str(r.get("回答") or "")
        if any(k in a for k in HEAVY):
            elsewhere += 1
            if len(heavy_examples) < 2 and not _has_placeholder(a):
                heavy_examples.append(a[:60])

    # 触发条件（放宽，覆盖真实数据形态）：
    #   ① 参照回答明确是"轻打法"（提到活动/社群但没提重手段）
    #   ② 参照回答只是占位摘要，但使用者在**别处**答过重手段
    trigger = (has_light and not has_heavy) or \
              (_has_placeholder(txt) and elsewhere > 0)
    if not trigger:
        return None

    msg = ("**可能是「业务形态差异」，不一定是答得不好**："
           "这道题在**原平台**的语境下用的多是话题/社群/活动这类**通用打法**，"
           "而成熟内容平台还会用 **MCN 支撑 / 超头部达人供稿 / 定向邀约** 这类"
           "**机构化、头部化**手段。两者的有无往往是**平台能力差异**"
           "（原平台可能根本不具备这些抓手），不是你的表达问题 —— "
           "补的是**业务认知**，别只重写句子。")
    if elsewhere:
        msg += ("\n  > 你在**其他 {} 条素材**里答过这类重手段（如：{}）—— "
                "说明你本身会，更可能是当时那个平台的业务形态用不上。"
                ).format(elsewhere,
                         "；".join(heavy_examples) if heavy_examples else "见相关卡")
    return msg


def classify_gap(question, material):
    """判定这个问题属于四类里的哪一类。
    一场挂了，不代表那场每道题都答得差（可能只是最后薪资没谈拢，
    或者横向对比输给了别人）。反过来，一场过了也可能有答得糟糕的题。
    所以这里的判定以**回答自身的质量分为主**，卡的结果只作旁证。

    ⚠️ 相似度阈值定得偏高，是因为中文 2-gram 很容易在**共用一个泛词**
    （"用户""内容""项目"）时虚高 —— 实测「你如何用SQL做用户分层」会以
    0.23 匹配上一条毫不相关的运营回答。宁可多报"缺口"，也别让人拿着一份
    不相关的素材上考场。低置信区间会显式标出来。
    """
    if not material:
        return "④ 无素材·缺口"
    best_sim, best = material[0]
    if best_sim < 0.12:
        return "④ 无素材·缺口"

    strong = [r for _, r in material if r["质量"] >= 60]
    weak = [r for _, r in material if r["质量"] < 45]
    solid = best_sim >= 0.40          # 高置信：字面确实像同一道题
    loose = 0.22 <= best_sim < 0.40   # 低置信：可能是泛词撞的
    if strong and solid:
        return "① 可直接复用"
    if strong and loose:
        return "① 可复用（低置信·先核对是不是同一道题）"
    if weak and not strong:
        return "② 答过但答得弱·需改写"
    if strong:
        return "③ 有同题材素材·可拼装"
    return "③ 有同题材素材·可拼装"


def _ref_pick(mat):
    """挑一条"参照回答"来对照骨架 —— 返回**行记录**（rows 里的原始 dict）。

    优先挑**质量最高**的。旧版直接取 mat[0]（相似度最高那条），
    可能是一条很弱的回答，于是骨架对照表满屏 ❌ ——
    那反映的是"这条素材弱"，不是"你没有这些层"，会误导。
    """
    if not mat:
        return None
    return max((r for _, r in mat), key=lambda r: r["质量"])


def build_one(rows, question, skeleton, exclude_cards=None):
    """对单条问题产出「框架 + 复用素材 + 缺口」。"""
    mat = find_material(rows, question, exclude_cards=exclude_cards)
    kind = classify_gap(question, mat)

    reuse, avoid = [], []
    for sim, r in mat:
        item = {
            "卡号": r["卡号"], "公司": r["公司"], "岗位": r["岗位"], "轮次": r["轮次"],
            "结果": r["结果"], "自评": r["自评"], "质量": r["质量"],
            "问题": r["问题"], "回答": r["回答"], "相似度": round(sim, 3),
            "命中要素": r["要素"], "缺失要素": [e["要素"] for e in skeleton if e["要素"] not in r["要素"]]
            if skeleton else [],
        }
        # 分栏按**回答质量**，不按卡的成败：
        #   质量够高 → 可复用（即便那场最终挂了，这条回答本身是好的）
        #   质量低   → 反面教材
        if r["质量"] >= 55:
            reuse.append(item)
        else:
            avoid.append(item)

    # 骨架：用**最强的那条**素材来对照，而不是相似度最高的那条
    ref = _ref_pick(mat)
    ref_els = ref["要素"] if ref else []
    skel_view = []
    for e in skeleton:
        covered = e["要素"] in ref_els
        skel_view.append({"层": e["要素"], "你历史上常见": e["覆盖率"], "此素材已覆盖": covered})

    gaps = []
    if kind.startswith("④"):
        gaps.append("**完全没有素材** —— 这题你从没被问过，库里也没有可迁移的内容。"
                    "不要临场编：编出来的细节一追问就塌。建议按下面的补法先造素材。")
    else:
        miss = [s["层"] for s in skel_view if not s["此素材已覆盖"]]
        if miss:
            gaps.append("最强的那条素材也缺这些层：**{}** —— 现场大概率被追问的就是它们。"
                        .format("、".join(miss)))
    if ref:
        v = vague_hits(ref["回答"])
        if v:
            gaps.append("参照回答里有含糊词：**{}** —— 这些位置在面试官听来就是"
                        "「他没真做过」，建议换成具体时空/数字。".format("、".join(sorted(set(v)))))
        if not re.search(r"\d", ref["回答"]):
            gaps.append("参照回答**一个数字都没有** —— 讲结果时缺可验证的锚点。")
        # 一条回答很好但整场挂了 —— 这是最容易被误读的情况，必须说清
        if ref["质量"] >= 60 and ref["结果"] == "fail":
            gaps.append("注意：上面这条回答**本身不差**（自评{}），但那一场整体是挂的 —— "
                        "说明问题不一定在这道题上，可能是同场别的环节、或横向对比/薪资等非能力因素。"
                        "别因为「场挂了」就把这条好回答也丢掉。".format(ref["自评"]))
        # ⚠️ 业务形态差异 —— 与"答得不好"分开，避免练错方向
        pg = platform_gap_hint(question, ref.get("回答"), mat)
        if pg:
            gaps.append(pg)
    if avoid and not reuse:
        gaps.append("相近的题你历史上答得都偏弱（见下方「答得弱的版本」），"
                    "改写时按新骨架重排，不要只在原答案上润色。")

    return {"问题": question, "归类": kind, "可复用": reuse, "别再这样答": avoid,
            "骨架对照": skel_view, "缺口": gaps,
            "素材数": len(mat), "最佳相似度": round(mat[0][0], 3) if mat else 0.0}


def _read_text(path):
    """读文本文件并**去掉 BOM**。

    ⚠️ Windows 上用 PowerShell 的 `Out-File -Encoding utf8` 存的文件带 BOM，
    而 BOM 会让 `^岗位职责$` 这类行首锚点全部失配 —— 实测直接把
    「岗位职责：」当成了 JD 的一条职责描述。用 utf-8-sig 兜住。
    """
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()


def extract_questions_from_jd(jd):
    """从 JD 文本里挑出值得准备的题。

    JD 本身是"要求"不是"问题"，所以这里做的是**要求 → 会被怎么问**的转换。

    ⚠️ 必须过滤掉**栏目名/标题行**：JD 里普遍有「岗位职责：」「任职要求：」
    「工作内容」这类小标题，它们不是职责描述。旧版只看长度，
    于是「岗位职责：」被当成一条职责，生成了"你过去有没有做过「岗位职责：」"
    这种荒唐的题。
    """
    # 栏目名/标题：冒号结尾的短语、或本身就是标题词
    HEADER_RE = re.compile(
        r"^(岗位职责|工作职责|职位描述|任职要求|任职资格|岗位要求|工作内容|"
        r"职位要求|我们希望你|加分项|福利待遇|薪资|薪酬|你将负责|要求|职责)"
        r"[\s:：]*$")
    # ⚠️ BOM 必须在这里剥掉，不能只在读文件时剥 —— 调用方可能直接把 JD
    #    字符串传进来（粘贴的、或从别的接口拿的），同样可能带 \ufeff。
    #    而 str.strip() **不会**去掉 \ufeff（它不是空白符），于是带 BOM 的
    #    第一行永远匹配不上 ^ 锚点 —— 实测「岗位职责：」就是这么漏成一道题的。
    jd = str(jd or "").replace("\ufeff", "")
    lines = [l.strip() for l in re.split(r"[\n。；;•·\-—\*]", jd) if l.strip()]
    duties = []
    for l in lines:
        if HEADER_RE.match(l):
            continue
        # 去掉行首编号（"1." "1、" "（1）" 等）后再判断
        body = re.sub(r"^[\(（]?\d+[\)）\.、,，:：]?\s*", "", l).strip()
        if len(body) < 6:
            continue
        if re.match(r"^[\d\.、\s]+$", body):
            continue
        # 纯"要求"句（含"以上经验/优先/熟悉/掌握"且没有动作词的），
        # 仍然可以生成题 —— 但问法不同（见下），所以标记出来
        is_req = bool(re.search(r"(以上|优先|熟悉|掌握|精通|具备|了解)", body)) and \
            not bool(re.search(r"(负责|推动|制定|搭建|优化|提升|策划|运营)", body))
        duties.append((body, is_req))

    out = []
    for body, is_req in duties[:24]:
        d_short = body[:60]
        if is_req:
            asks = [
                "你在这方面（「{}」）的经验具体到什么程度？举个例子。".format(d_short),
                "如果没有直接经验，你打算怎么补上「{}」这一块？".format(d_short),
            ]
        else:
            asks = [
                "你过去有没有做过「{}」？具体怎么做的？".format(d_short),
                "如果让你在我们这里从 0 做「{}」，你的前三个月怎么排？".format(d_short),
                "「{}」这件事，你觉得最难的点在哪？".format(d_short),
            ]
        out.append({"源自JD": d_short, "大概率会问": asks})
    return out


def selftest():
    """内置案例自检。锁住几条被改错过的行为。"""
    ok = 0
    bad = 0

    def chk(name, cond):
        nonlocal ok, bad
        if cond:
            print("  ✓ " + name); ok += 1
        else:
            print("  ✗ " + name); bad += 1

    # ① 要素识别
    rich = ("当时我负责点评的美食内容生态。难点是作者增长有瓶颈。"
            "我先拆了供给来源，一是转化评价作者，二是站外建联社群。"
            "结果是月产出1500+篇，日均曝光700万+，渗透17%。"
            "复盘下来这套方法可以复用到其他垂类。")
    els = elements_of(rich)
    chk("要素识别：六层齐全的回答能被识别出全部六层", len(els) == 6)

    poor = "就是做一些内容运营的工作，还挺好的。"
    chk("要素识别：空泛回答识别出的层数明显更少", len(elements_of(poor)) <= 2)

    # ② 质量分：具体 > 空泛
    q_rich = {"score": 5, "how_answered": rich}
    q_poor = {"score": 3, "how_answered": poor}
    q_vague = {"score": 3, "how_answered": "大概是做一些运营吧，好像还行，记不清了。"}
    s_rich, _ = answer_quality(q_rich)
    s_poor, _ = answer_quality(q_poor)
    s_vague, _ = answer_quality(q_vague)
    chk("质量分：丰富回答 > 空泛回答", s_rich > s_poor)
    chk("质量分：含糊词会拉低分数", s_poor > s_vague)

    # ③ 归类：卡挂了但回答好 → 仍应可复用（这是最容易搞错的一条）
    rows = [
        {"卡号": "T1", "公司": "A", "岗位": "内容运营", "轮次": "一面", "结果": "fail",
         "问题": "讲一个你从0到1做内容生态的项目", "主题": "项目复盘",
         "自评": 5, "回答": rich, "备注": "", "要素": els, "质量": s_rich},
    ]
    one = build_one(rows, "讲一个你从0到1做内容生态的项目", [])
    chk("归类：回答质量高时，即便所在场是 fail 也进「可复用」",
        len(one["可复用"]) == 1 and "卡的结果" not in one["归类"])
    chk("缺口：会显式提示「这条回答不差但整场挂了」",
        any("整体是挂的" in g for g in one["缺口"]))

    # ④ 无素材 → 缺口
    far = build_one(rows, "请用 Kubernetes 设计高可用架构", [])
    chk("归类：完全无关的问题被判为缺口", far["归类"].startswith("④"))

    # ⑤ JD 解析要滤掉栏目名（含 BOM 的情况）
    jd = "\ufeff岗位职责：\n1. 负责社区内容生态建设\n任职要求：\n1. 熟悉数据分析"
    qs = extract_questions_from_jd(jd)
    flat = " ".join(q for g in qs for q in g["大概率会问"])
    chk("JD 解析：栏目名「岗位职责：」不会变成一道题", "岗位职责" not in flat)
    chk("JD 解析：栏目名「任职要求：」不会变成一道题", "任职要求" not in flat)
    chk("JD 解析：真实的职责描述会被转成问题", "负责社区内容生态建设" in flat)
    chk("JD 解析：要求类句子用另一种问法",
        any("经验具体到什么程度" in q for q in (g["大概率会问"][0] for g in qs)))

    # ⑥ 相似度要能区分
    chk("相似度：同题高分 > 无关题",
        similarity("讲一个从0到1的项目", "讲一个从0到1的项目")
        > similarity("讲一个从0到1的项目", "Kubernetes高可用架构"))

    # ⑦ 相似度必须落在 [0,1]（曾经出现 1.06 / 1.37，导致"低置信"档永远进不去）
    _rw = [{"卡号": "X1", "公司": "A", "岗位": "内容运营", "轮次": "一面",
            "结果": "pass", "问题": "讲一个从0到1的项目", "主题": "项目复盘",
            "自评": 5, "回答": rich, "备注": "", "要素": els, "质量": s_rich}]
    _sims = [s for s, _ in find_material(_rw, "讲一个从0到1的项目 项目 复盘 内容 运营")]
    chk("相似度夹在 [0,1]（加权不会溢出）", all(0.0 <= s <= 1.0 for s in _sims))

    # ⑧ exclude 必须真的把指定卡排除掉（避免"自己匹配自己"）
    #    实测场景：拿 I007 自己的题目去查，不排除时相似度 1.0、报"可直接复用"，
    #    而那素材就是题目本身 —— 等于什么都没说。
    _with = find_material(_rw, "讲一个从0到1的项目")
    _without = find_material(_rw, "讲一个从0到1的项目", exclude_cards={"X1"})
    chk("--exclude 能排除指定卡（不再自己匹配自己）",
        len(_with) == 1 and len(_without) == 0)

    print()
    if bad:
        print("  [WARN] 应答框架自检 {} 项未通过".format(bad))
        return 1
    print("  ✅ 全部通过（要素识别 / 质量分 / 归类 / 缺口 / JD 解析 / 相似度 / 排除）")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        return selftest()
    ap = argparse.ArgumentParser(description="基于真实经历的结构化应答框架 + 缺口标注")
    ap.add_argument("--q", action="append", help="要准备的问题（可多次传）")
    ap.add_argument("--file", help="从文件读问题清单（每行一条）")
    ap.add_argument("--jd", help="JD 文本（自动生成该准备的题）")
    ap.add_argument("--jd-file", help="从文件读 JD")
    ap.add_argument("--report", help="输出 markdown 到文件")
    ap.add_argument("--top", type=int, default=3, help="每题展示几条素材（默认3）")
    ap.add_argument("--expand", action="store_true",
                    help="JD 模式下把每条职责的所有问法都展开（默认只展开第一问，报告更短）")
    ap.add_argument("--exclude", action="append", default=[],
                    help="排除这些卡号不作为素材（如 --exclude I007）。"
                         "用途：准备二战同一家公司时，避免拿这场自己的题目匹配自己")
    args = ap.parse_args()

    cards = load_cards()
    if not cards:
        print("[提示] cards/ 下还没有卡 —— 无真实经历可依，本模块的「框架」会是空的。")
        print("       先建几场：python main.py record new --company 公司 --position 岗位 --round 一面 --nature 正编")
        return 0
    rows = collect_qas(cards)
    skeleton, skel_basis = infer_skeleton(rows)

    questions = list(args.q or [])
    if args.file:
        questions += [l.strip() for l in open(args.file, encoding="utf-8") if l.strip()]
    jd = args.jd
    if args.jd_file:
        jd = _read_text(args.jd_file)
    from_jd = extract_questions_from_jd(jd) if jd else []
    # JD 模式下：每条职责默认只展开**第一问**（最贴近"你做过吗"），
    # 其余问法压缩进末尾的映射表。否则 12 条职责 × 3 问法 = 36 题、
    # 每题又展开 5 条素材，报告会长到没法看（实测 1114 行）。
    jd_mode = bool(jd) and not questions
    if jd_mode:
        for grp in from_jd:
            questions.append(grp["大概率会问"][0])
        if args.expand:
            for grp in from_jd:
                questions.extend(grp["大概率会问"][1:])

    if not questions:
        ap.print_help()
        return 1

    L = ["# 应答框架 & 缺口清单\n"]
    L.append("> 由 {} 张卡的 {} 条真实问答推导。**不生成漂亮答案** —— "
             "只从**你答得好的**回答里复用（按回答质量判断，**不看那场过没过**："
             "挂掉的一场不代表每道题都差，可能输在 HC/横向对比/薪资），"
             "答不上来的地方直接标成缺口。\n"
             .format(len(cards), len(rows)))

    if skeleton:
        L.append("## 0) 你的作答骨架（归纳自 {}）\n".format(skel_basis))
        L.append("| 层 | 你在高分回答里覆盖的比例 | 样本 |")
        L.append("|---|---|---|")
        for s in skeleton:
            L.append("| {} | {}% | {} |".format(s["要素"], s["覆盖率"], s["样本数"]))
        L.append("\n> 这是**从你自己的高分回答里长出来的**骨架，不是通用范文模板。"
                 "样本按**回答质量**取（不看那场过没过）。"
                 "准备新题时按这个顺序组织，听起来才像你。\n")

    for idx, q in enumerate(questions, 1):
        r = build_one(rows, q, skeleton, exclude_cards=set(args.exclude or []))
        L.append("## {}) {}\n".format(idx, q))
        L.append("**归类**：{}　（素材 {} 条，最佳相似度 {}）\n"
                 .format(r["归类"], r["素材数"], r["最佳相似度"]))
        if "低置信" in r["归类"]:
            L.append("> ⚠️ 相似度只有 {}，中文 2-gram 常因共用泛词（用户/内容/项目）虚高。"
                     "**先点开下面那条素材确认是不是同一道题**，别直接套。\n"
                     .format(r["最佳相似度"]))

        if r["骨架对照"]:
            L.append("| 骨架层 | 此素材是否覆盖 |")
            L.append("|---|---|")
            for s in r["骨架对照"]:
                L.append("| {} | {} |".format(s["层"], "✅" if s["此素材已覆盖"] else "❌ 缺"))
            L.append("")

        if r["可复用"]:
            L.append("### ✅ 可以复用（回答本身质量够高）")
            for it in r["可复用"][:args.top]:
                tag = "" if it["结果"] == "pass" else "　⚠️ 该场整体挂了，但这条回答不差"
                L.append("- **{}-{}** · {} · {} · 自评{} · 质量{}{}"
                         .format(it["卡号"], it["公司"], it["岗位"][:28], it["轮次"],
                                 it["自评"], it["质量"], tag))
                L.append("  - 问：{}".format(it["问题"][:90]))
                L.append("  - 答：{}".format(it["回答"][:260]))
            L.append("")
        if r["别再这样答"]:
            L.append("### ⚠️ 答得弱的版本（可当反面参照）")
            for it in r["别再这样答"][:2]:
                L.append("- **{}-{}** · {} · 自评{} · 质量{}"
                         .format(it["卡号"], it["公司"], it["轮次"], it["自评"], it["质量"]))
                L.append("  - 问：{}".format(it["问题"][:90]))
                L.append("  - 当时的答：{}".format(it["回答"][:200]))
            L.append("")
        if r["缺口"]:
            L.append("### 🕳 缺口（面试官会戳这里）")
            for g in r["缺口"]:
                L.append("- {}".format(g))
            L.append("")

    # JD → 题目映射
    if from_jd:
        L.append("---\n\n## 附：JD 要求 → 大概率会怎么问\n")
        L.append("> 上面只展开每条的**第一问**；下表是全部问法，按需自取。\n")
        L.append("| JD 原句 | 大概率会问 |")
        L.append("|---|---|")
        for grp in from_jd[:16]:
            L.append("| {} | {} |".format(grp["源自JD"], "<br>".join(grp["大概率会问"])))

    # 缺口总览
    allgaps = [q for q in questions if build_one(rows, q, skeleton)["归类"].startswith("④")]
    L.append("\n---\n\n## 缺口总览\n")
    if allgaps:
        L.append("以下 {} 题**库里完全没有素材**，属于要提前造素材的：\n".format(len(allgaps)))
        for q in allgaps:
            L.append("- {}".format(q))
        L.append("\n补法：找一段你真实做过、能对上这题的事（哪怕是副业/外包/协作里的），"
                 "按骨架六层写成一段可讲的 60 秒叙述，写进 card 的 `how_answered`。"
                 "**不要背范文** —— 背的会被追问打穿。")
    else:
        L.append("本次无完全空白的题。但请留意每题下「缺口」里标出的**缺失层** —— "
                 "那是现场最可能被追问的地方。")

    L.append("\n---\n\n## 诚实声明\n")
    L.append("- 本文件**不含任何 AI 编造的答案**。所有「可复用」都注明出自哪张卡、当时什么结果。")
    L.append("- 相似度是字面 bigram 匹配，只用来**找素材**，不代表两题真的等价 —— 复用前自己判断。")
    L.append("- 缺口部分是这套方法最值钱的部分：**知道自己哪里空，比背一段漂亮话有用得多**。")

    text = "\n".join(L)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(text)
        print("[OK] 已生成:", args.report)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
