#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_card.py — 单场面试卡片生成与规范化

功能：
1. 读取 source/ 下一个新的面试文本(或粘贴文本/PDF文本路径)，解析出"已知真实信息"。
2. 规整到 schema.yaml 定义的卡片结构。
3. 自动分配下一个卡片 ID (I001, I002, ...)。
4. 写出一张"骨架卡片"，把【只有用户才知道的真值】(outcome/真实公司/真实岗位/
   gap原因/通过or未通过) 显式标为待补，供用户/AI 填充。

用法（命令行）：
    python build_card.py --text "面试逐字稿或摘要..." [--company 公司] [--position 岗位]
    python build_card.py --pdf "path/to/1.pdf"        # 若有 pdf 文本提取（依赖工具）
    python build_card.py --id I016 --outcome fail --reason "..."   # 补结果

说明：
- 本脚本只负责"骨架/编号/文件"与"结果回填"，真正的内容提炼由 AI 在拿到
  source 文本后按 schema 完成。脚本保证每张卡结构统一、可被 cross_analysis 聚合。
"""

import os
import re
import sys
import glob
import argparse
from datetime import date

CARDS_DIR = os.path.join(os.path.dirname(__file__), "..", "cards")
INBOX_DIR = os.path.join(CARDS_DIR, "_inbox")
TEMPLATE = os.path.join(CARDS_DIR, "_template.yaml")
BACKUP_DIR = os.path.join(CARDS_DIR, "_bak")


def backup_before_write(path, why="write"):
    """改写任何卡片**之前**，先留一份副本到 cards/_bak/。

    ═══ 为什么加这个（真实事故）═══
    使用者 真实面经卡是这套工具的核心资产，而 `result` 等命令
    是**原地覆盖**（`re.sub` 后直接 `write`）。实测发生过：
    在真实数据目录上跑一句 `result --id I007 --outcome pass --reason "验证用"`，
    就把该卡原本的 reason **覆盖掉了，且没有任何副本可还原**
    （数据目录不在版本控制里）。

    规则：**只要会改卡，就先备份**。备份名带时间戳，不覆盖旧备份。
    损坏一张卡 vs 多一个 _bak 目录，后者便宜得多。
    """
    try:
        import shutil
        from datetime import datetime
        if not os.path.exists(path):
            return None
        os.makedirs(BACKUP_DIR, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base = os.path.basename(path)
        dst = os.path.join(BACKUP_DIR, f"{stamp}__{base}")
        n = 1
        while os.path.exists(dst):           # 同一秒内多次写也不互相覆盖
            dst = os.path.join(BACKUP_DIR, f"{stamp}_{n}__{base}")
            n += 1
        shutil.copy2(path, dst)
        return dst
    except Exception as e:                    # 备份失败不能阻断主流程，但必须吼一声
        print(f"[WARN] 备份失败（{why}）：{e}")
        print("       继续写入，但**这次改动将无法从 _bak 还原**。")
        return None


def find_card(cid):
    """按 id 找卡，**同时搜正式卡与 _inbox 暂存卡**。

    ⚠️ 修的是一个真实的流程断裂（建档链路端到端实测发现）：
      旧版只搜 cards/I*.yaml，并且对任何不以 I 开头的 id 强加 I 前缀，于是：
        · `record new` 建的是 cards/_inbox/P###.yaml（文档教的主流程）
        · 但 `result --id P146` 被拼成 **IP146**，且压根不看 _inbox
        → **pending 卡无法回填结果**。
      而 ENGINE.md 写着"有实际结果请立刻回填"，remind 也会催你回填 ——
      催的却是一张你填不了的卡。唯一出路是先 `merge formalize` 转正，
      但没有任何地方提示这一点。

    现在：P### 与 I### 都认，两个目录都搜；带不带 .yaml 后缀都行。
    """
    raw = str(cid or "").strip()
    if not raw:
        return None
    stem = raw[:-5] if raw.lower().endswith(".yaml") else raw
    stem = stem.upper()
    if not stem:
        return None

    # 搜索顺序：原样 → 原标题 → 加 I 前缀（兼容只写数字的情况）
    cands = [stem]
    if stem.startswith("IP"):
        cands.append(stem[1:])          # IP146 -> P146（旧版错误的拼法，顺手兼容）
    if not stem.startswith(("I", "P")):
        cands.append("I" + stem)
        cands.append("P" + stem)
    elif stem.startswith("P"):
        cands.append("I" + stem[1:])    # P146 也可能已经转正成 I146
    elif stem.startswith("I"):
        cands.append("P" + stem[1:])    # I146 还没转正时实际是 P146

    for base in cands:
        for d in (CARDS_DIR, INBOX_DIR):
            hits = sorted(glob.glob(os.path.join(d, base + "_*.yaml")))
            if hits:
                return hits[0]
            direct = os.path.join(d, base + ".yaml")
            if os.path.exists(direct):
                return direct
    return None


def next_id(existing=None):
    """计算下一个卡片 ID，如 某张卡。"""
    if existing is None:
        existing = glob.glob(os.path.join(CARDS_DIR, "I*.yaml"))
    nums = []
    for p in existing:
        m = re.search(r"\bI(\d{3})", os.path.basename(p))
        if m:
            nums.append(int(m.group(1)))
    n = max(nums) + 1 if nums else 1
    return f"I{n:03d}"


def make_skeleton(cid, company="", position="", date_str="", round_="",
                  interviewer="", channel=""):
    today = date.today().isoformat()
    skeleton = (
        "# 面试卡片 — " + (company or "公司待补") + "·" + (position or "岗位待补") + "\n"
        f"id: {cid}\n\n"
        "meta:\n"
        f"  create_date: {today}\n"
        "  review_date: \"\"\n\n"
        "interview:\n"
        f"  company: \"{company}\"          # 真实公司名（用户确认为准）\n"
        f"  position: \"{position}\"         # 目标岗位\n"
        "  level: \"\"                # 中级 / 高级 / 负责人\n"
        f"  date: {date_str or 'YYYY-MM-DD'}" + "         # 面试日期\n"
        f"  round: \"{round_}\"                # 一轮/二面/HR面/终面\n"
        f"  interviewer_role: \"{interviewer}\"      # 业务/产品/HR/负责人\n"
        f"  channel: \"{channel}\"             # 内推/海投/猎头\n\n"
        "questions:\n"
        "  - question: \"\"           # 面试官问的问题\n"
        "    theme: \"\"              # 项目复盘/方法论/指标/行为/反问\n"
        "    how_answered: \"\"       # 你的回答要点\n"
        "    score: 3               # 自评 1-5\n"
        "    note: \"\"               # 备注/面试官反馈\n\n"
        "result:\n"
        "  outcome: 待确认           # pass / fail / no_offer / 待确认\n"
        "  reason: \"\"               # 你认为通过/未通过的真实原因\n"
        "  signal: \"\"               # 面试官给到的反馈信号\n\n"
        "reflection:\n"
        "  strength: \"\"             # 做得好、可复制的点\n"
        "  weakness: \"\"             # 暴露的短板、踩坑点\n"
        "  improvement: \"\"          # 下次的改进动作\n\n"
        "skills: []                  # 能力标签\n"
    )
    return skeleton


# 可复用的能力标签库（跨场聚合用）
SKILL_TAGS = [
    "项目复盘STAR", "自我介绍", "简历优化", "方法论表达", "内容运营", "推荐策略",
    "内容池", "冷启动", "创作者运营", "社群运营", "作者策略", "用户洞察", "竞品分析",
    "指标口径", "数据分析", "ROI", "场景迁移", "行为面试", "反问", "期望薪资",
    "面试语速", "离职原因", "空窗期表达", "职业规划", "AI工具", "MCP", "增长",
    "用户增长", "产品洞察", "跨团队推动", "海外经验", "本地化", "出海",
]


def _set_yaml_field(content, key, value):
    """把 YAML 文本里 `key:` 的值设成 value，返回 (新文本, 是否真的改了)。

    ═══ 为什么要重写（真实 bug）═══
    旧实现是 `re.sub(r'reason:\\s*\\"[^\\"]*\\"', ...)` —— **要求原值被双引号包住**。
    而真实卡里大量字段是**无引号裸文本**（`reason: 挂（…）`）或空值（`reason:`），
    于是正则**根本不匹配**，函数却照样打印 `[OK] 已更新` 并返回 0。
    实测：在 I007 上跑 `result --reason "验证用"`，reason 一个字节都没变，
    命令却说"已更新" —— **用户以为填上了，实际什么都没发生**。
    这与 v3.2.x 修过的"pending 卡填不了结果"是同一类病：**静默失败**。

    现在：
      · 值里含特殊字符（引号/冒号/井号）→ 双引号包并转义
      · 否则写裸文本（与真实卡既有风格一致，不打乱 diff）
      · `key:` 后为空 → 视为占位，直接填
      · **匹配不到返回 False**，由调用方如实报告"没写进去"
    """
    pat = re.compile(r"^([ \t]*" + re.escape(key) + r":)([^\n]*)$", re.M)
    m = pat.search(content)
    if not m:
        return content, False

    body = m.group(2).strip()
    comment = ""
    if "#" in body and not body.startswith(('"', "'")):
        idx = body.index("#")
        comment = "  " + body[idx:]
        body = body[:idx].strip()

    needs_quote = any(ch in value for ch in ':#"\'') or value.strip() != value
    new_val = '"' + value.replace('"', '\\"') + '"' if needs_quote else value
    new_line = m.group(1) + " " + new_val + comment

    new_content = content[:m.start()] + new_line + content[m.end():]
    return new_content, (new_content != content)


def _get_yaml_field(content, key):
    """读字段当前值（用于打印「旧 → 新」）。兼容带引号/裸文本/空值。

    ⚠️ 用 `[^\\n]*` 而不是 `.*`：`\\s*` 会**吃掉换行**，于是一个空值字段
    （`reason:` 后面什么都没有）会把**下一行**当成自己的值
    （实测：空的 reason 读出来是 `signal: ""`）。只匹配行内字符即可避免。
    """
    m = re.search(r"^[ \t]*" + re.escape(key) + r":[^\n]*", content, re.M)
    if not m:
        return ""
    v = m.group(0).split(":", 1)[1].strip()
    if "#" in v and not v.startswith('"'):
        v = v[:v.index("#")].strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v


def fill_outcome(cid, outcome, reason="", signal=""):
    """回填某卡片的结果（正式卡与 _inbox 暂存卡都支持）。"""
    path = find_card(cid)
    if path is None:
        print(f"[错误] 未找到卡片 {cid}")
        print(f"       已搜索 {os.path.normpath(CARDS_DIR)} 与 _inbox/")
        # 把现有卡列出来，省得用户猜 —— 之前只回一句"未找到"，用户不知道该怎么办
        have = sorted(os.path.basename(p) for p in glob.glob(os.path.join(CARDS_DIR, "I*.yaml")))
        pend = sorted(os.path.basename(p) for p in glob.glob(os.path.join(INBOX_DIR, "P*.yaml")))
        if pend:
            print(f"       _inbox 暂存卡（{len(pend)}）: {', '.join(pend[:6])}"
                  + ("…" if len(pend) > 6 else ""))
        if have:
            print(f"       正式卡共 {len(have)} 张，如: {', '.join(have[:3])}…")
        return 1

    is_pending = os.path.basename(path).startswith("P")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 覆盖前先备份，并把"旧值"记下来 —— 改错了能回退，改了什么也看得见
    bak = backup_before_write(path, why="回填结果")
    old_outcome = _get_yaml_field(content, "outcome")
    old_reason = _get_yaml_field(content, "reason")
    old_signal = _get_yaml_field(content, "signal")

    new_content, _ = _set_yaml_field(content, "outcome", outcome)
    applied, missing = ["outcome"], []
    for fld, val in (("reason", reason), ("signal", signal)):
        if not val:
            continue
        new_content, ok = _set_yaml_field(new_content, fld, val)
        (applied if ok else missing).append(fld)

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # ⚠️ 只有真的写进去了才说"已更新"。否则必须明确报错 ——
    #    旧版无论匹配与否都打印 [OK]，这正是那个静默 bug 的根源。
    if missing:
        print(f"[警告] {os.path.basename(path).split('.')[0]}: 已写入 {', '.join(applied)}，"
              f"但这些字段**没找到位置、未写入**：{', '.join(missing)}")
        print("       该卡可能缺这些字段（或字段名不同）。请打开卡片确认：")
        print(f"         {os.path.relpath(path, os.path.dirname(CARDS_DIR))}")
        print("       （本次改动已备份，可用 _bak 还原）")
        rc = 1
    else:
        print(f"[OK] 已更新 {os.path.basename(path).split('.')[0]}: outcome={outcome}")
        rc = 0

    # 被覆盖的旧值要显式打出来：用户才能立刻发现"是不是填错了/覆盖了不该覆盖的"
    changed = []
    if old_outcome != outcome:
        changed.append(f"outcome: {old_outcome or '(空)'} → {outcome}")
    if reason and old_reason != reason:
        changed.append(f"reason: 「{old_reason[:36]}{'…' if len(old_reason) > 36 else ''}」"
                       f" → 「{reason[:36]}{'…' if len(reason) > 36 else ''}」")
    if signal and old_signal != signal:
        changed.append(f"signal: 「{old_signal[:36]}」 → 「{signal[:36]}」")
    if changed:
        print("     改动明细（旧 → 新）:")
        for c in changed:
            print("       · " + c)
    elif not missing:
        print("     改动明细：（无变化 —— 值本来就是这样，未产生实际改动）")
    if bak:
        print(f"     已备份原卡：{os.path.relpath(bak, os.path.dirname(CARDS_DIR))}")
        print("     （改错了就用它还原：把它复制回 cards/ 覆盖即可）")
    if is_pending:
        print("     ⚠️ 这是 _inbox 里的**暂存卡**，还没有正式 I 号，")
        print("        因此**不会进总报统计**。要让 `report` 吃进去，先转正：")
        print("           python main.py merge formalize")
    return rc


def main():
    ap = argparse.ArgumentParser(description="面经卡片生成/回填工具")
    ap.add_argument("--text", help="面试内容文本（转写稿/摘要），用于生成骨架")
    ap.add_argument("--pdf", help="PDF 路径（若已有文本提取工具）")
    ap.add_argument("--company", default="", help="真实公司名")
    ap.add_argument("--position", default="", help="目标岗位")
    ap.add_argument("--date", default="", help="面试日期 YYYY-MM-DD")
    ap.add_argument("--round", default="", help="轮次")
    ap.add_argument("--interviewer", default="", help="面试官角色")
    ap.add_argument("--channel", default="", help="渠道")
    ap.add_argument("--id", help="卡片 ID，配合 --outcome 回填结果")
    ap.add_argument("--outcome", help="结果 pass/fail/no_offer")
    ap.add_argument("--reason", default="", help="真实原因")
    ap.add_argument("--signal", default="", help="面试官信号")
    args = ap.parse_args()

    if args.id and args.outcome:
        # ⚠️ 校验 outcome 取值。旧版完全不校验，`--outcome 也许吧` 会
        #    原样写进卡里并返回 0 —— 用户以为填好了，而 report/validate
        #    都不认这个值，该场会从所有统计里**静默消失**。
        #    合法的只有 pass / fail / no_offer / unknown / 待确认。
        ok = {"pass", "fail", "no_offer", "unknown", "待确认", "待实际"}
        if str(args.outcome).strip() not in ok:
            print(f"[错误] outcome 取值非法：{args.outcome!r}")
            print(f"       只能是：pass / fail / no_offer / unknown（或 '待确认'）")
            print(f"       含义：pass=本轮过  fail=本轮挂  no_offer=业务过但最终没 offer")
            return 2
        return fill_outcome(args.id, args.outcome, args.reason, args.signal)

    if args.company or args.position or args.text or args.pdf:
        cid = next_id()
        skeleton = make_skeleton(
            cid, args.company, args.position, args.date,
            args.round, args.interviewer, args.channel
        )
        fname = f"{cid}_{(args.company or '新场次') or '新场次'}.yaml"
        fpath = os.path.join(CARDS_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(skeleton)
        print(f"[OK] 已生成骨架卡片: {fpath}")
        print(f"[提示] content 提炼由 AI 按 schema.yaml 完成；outcome 等真值由你用 --id --outcome 回填。")
        print("  下一步: 提供逐字稿/摘要，我会为你填充 questions/reflection 等。")
        return 0

    print("用法：python build_card.py --text '<内容>' --company 公司 --position 岗位")
    print("  或  python build_card.py --id I016 --outcome fail --reason '...'")
    return 1


if __name__ == "__main__":
    sys.exit(main())
