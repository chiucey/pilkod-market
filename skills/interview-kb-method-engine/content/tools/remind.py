#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
remind.py — "回填真值"闹钟：找出该确认但还没回填的场。

用法: python main.py remind          # 只看已到期(记录日+7)但仍无实际结果的
      python main.py remind --all    # 也包含还没到期的 unknown（提前预告）

═══ v3.4.0：从"只催 outcome"改成"催真正缺的那几项" ═══
实测使用者的真实卡的填充率：
    outcome 100%  ← 根本不用催
    offer    28.9%（56 张 pass 卡里 55 张没填！）
    why_ended 28.2%（86 张 fail 卡里 69 张没填）
旧版只盯 outcome=unknown，于是**该催的一个都没催到**，
而这两个空字段恰是报告里最有价值两节的数据源：
    offer 空     → 「业务全过但 offer=no」基本是空的
    why_ended 空 → 「挂了但不是当场表现」「反复挂根源」失真

现在的判据（按 outcome 决定该要哪一项，而不是一刀切）：
    outcome=pass  → 需要 offer（拿到没？got/no/ongoing）
    outcome=fail  → 需要 why_ended（为什么没推进）
    两者都空     → 两条都列
并给出**可直接复制的命令**，不用去翻文档查参数。
"""
import os, re, glob, sys
from datetime import date as _dt, datetime as _dtx
if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8', errors='replace')
try:
    import yaml
except Exception:
    yaml=None
BASE=os.path.dirname(os.path.abspath(__file__))
CARDS=os.path.join(BASE,"..","cards")
INBOX=os.path.join(CARDS,"_inbox")

def outcome_flag(res):
    s=str((res or {}).get("outcome") or "").strip()
    low=s.lower()
    if "pass" in low: return "pass"
    if "fail" in low or "挂" in s: return "fail"
    if "no_offer" in low: return "no_offer"
    if "unknown" in low or "待" in s or "未知" in s: return "unknown"
    return "missing"

def is_actual(flag): return flag in ("pass","fail","no_offer")


def _has_offer(res):
    """offer 填了没有 —— 必须走共享的 offer_flag，不能自己 str() 判空。

    ⚠️ 坑：YAML 1.1 把裸 `no` 解析成**布尔 False**，`got`/`ongoing` 才是字符串。
    所以 `offer: no` 在内存里是 `False`；任何 `if not res.get("offer")`
    式的判空都会把 False 当成"没填"。这正是本项目 v3.2.x 踩过的坑
    （当时 40 张卡全落进死分支，正编/外包一度算出 17/18/19/15 四个数）。
    共享实现见 industry_taxonomy.offer_flag —— 直接复用，不自己再写一遍。

    注意入参形状：offer_flag 要的是**整张卡**（它自己取 card["result"]["offer"]），
    不是 result 子字典。这里包一层适配，避免调用方搞错。
    """
    try:
        sys.path.insert(0, BASE)
        from industry_taxonomy import offer_flag
        return bool(offer_flag({"result": res or {}}))
    except Exception:
        # 兜底：显式区分 False / 空串 / None
        v = (res or {}).get("offer")
        if isinstance(v, bool):
            return True          # False 是「no」这个**有效取值**，不是空
        return bool(str(v or "").strip())


def missing_truths(res):
    """这一场还缺哪些真值？按 outcome 判断该要哪一项。

    返回缺失字段名列表（可能为空）。判据见模块 docstring。
    """
    flag = outcome_flag(res)
    if flag == "pass":
        # 过了 → 得知道最终有没有 offer（pass≠拿到）
        return [] if _has_offer(res) else ["offer"]
    if flag == "fail":
        # 挂了 → 得知道为什么没推进（能力问题还是匹配问题，改进方向完全不同）
        return [] if str((res or {}).get("why_ended") or "").strip() else ["why_ended"]
    if flag == "no_offer":
        # 业务过了但没 offer → 原因最重要
        return [] if str((res or {}).get("why_ended") or "").strip() else ["why_ended"]
    # unknown / missing → outcome 本身就没填
    return ["outcome"]


_FIX_HINT = {
    "offer": '--offer got|no|ongoing   # 最终拿到 / 没拿到 / 还在走',
    "why_ended": '--why-ended "横向对比|审批|薪资|base|外包无转正|能力…"',
    "outcome": '--outcome pass|fail',
}


def _fmt_fix(cid, fields):
    """给一条可直接复制的命令（只带缺的那几个参数）。"""
    if not fields:
        return ""
    parts = []
    for f in fields:
        parts.append(_FIX_HINT.get(f, f))
    return f"       python main.py record fix {cid} " + " ".join(parts)

def scan(all_flag=False):
    today=_dt.today().isoformat()
    rows=[]
    gaps=[]      # v3.4.0：已定结果的卡里，仍缺 offer / why_ended 的
    # formal
    for p in sorted(glob.glob(os.path.join(CARDS,"I*.yaml"))):
        try: c=yaml.safe_load(open(p,encoding="utf-8"))
        except Exception: continue
        if not isinstance(c,dict): continue
        fname=os.path.basename(p).split('.')[0]
        cid=str(c.get("id") or fname.split("_")[0])
        res=c.get("result") or {}
        meta=c.get("meta") or {}
        cb=str(meta.get("confirm_by") or "").strip()
        flag=outcome_flag(res)
        due = (not is_actual(flag)) and (not cb or cb <= today)
        if all_flag and not is_actual(flag) and cb and cb> today:
            due_pending = f"[{cb}] {fname} · {c.get('interview',{}).get('company','')}  (outcome=unknown, confirm_by 未到)"
            rows.append(due_pending)
        if due:
            rows.append(f"[CRIT] {fname} · {str((c.get('interview') or {}).get('company',''))[:20]} — confirm_by {cb if cb else '未设'}；仍 outcome={str(res.get('outcome','')) or '空'}")
        # ★ outcome 已定，但 offer/why_ended 仍缺 —— 这才是实测最常见的缺口
        elif is_actual(flag):
            miss = missing_truths(res)
            if miss:
                gaps.append((cid, str((c.get("interview") or {}).get("company",""))[:16], flag, miss))
    # inbox pending
    if os.path.isdir(INBOX):
        for p in sorted(glob.glob(os.path.join(INBOX,"P*.yaml"))):
            try: c=yaml.safe_load(open(p,encoding="utf-8"))
            except Exception: continue
            if not isinstance(c,dict): continue
            fname=os.path.basename(p).split('.')[0]; res=c.get("result") or {}; meta=c.get("meta") or {}
            cb=str(meta.get("confirm_by") or "").strip(); flag=outcome_flag(res)
            if not is_actual(flag) and (not cb or cb <= today):
                rows.append(f"[CRIT/pending] {fname} · {str((c.get('interview') or {}).get('company',''))[:20]} — confirm_by {cb or '未设'}; 请回填 actual")

    if rows:
        print(f"共 {len(rows)} 场需要跟进回填真实结果：")
        print("\n".join(rows))
        print("\n请对每一场用合口语答复，agent 会帮写 result。核心三把钥匙：")
        print("  outcome = pass/fail（实际过没过）  why_ended = 没推进原因  offer = got/no/ongoing")
        print("若无实际结果但仍确认中，请把卡 meta.confirm_by 往后改，或明确标‘待实际’。")
    else:
        print("[OK] 暂无需要跟进回填的场（记录日+7 已过且仍 unknown 无 → 没有）。")

    # ── 第二部分：结果已定、但关键字段仍空 ──
    if gaps:
        print()
        print(f"⚠️ 另有 {len(gaps)} 场**结果已填、但这些字段还是空的**（会让报告相应章节失真）：")
        _of = sum(1 for g in gaps if "offer" in g[3])
        _wy = sum(1 for g in gaps if "why_ended" in g[3])
        if _of:
            print(f"   缺 offer 的 {_of} 场 → 影响「业务全过但 offer=no」一节")
        if _wy:
            print(f"   缺 why_ended 的 {_wy} 场 → 影响「挂了但不是当场表现」「反复挂根源」")
        print()
        for cid, comp, flag, miss in gaps[:20]:
            mark = "过" if flag == "pass" else ("挂" if flag == "fail" else flag)
            print(f"   [{mark}] {cid} {comp:<16} 缺：{', '.join(miss)}")
            print(_fmt_fix(cid, miss))
        if len(gaps) > 20:
            print(f"   …另有 {len(gaps)-20} 场（只列前 20）")
        print()
        print("   （不补也能用，只是报告里对应那几节会少这些场；逐条补更准。）")
    else:
        print()
        print("[OK] 所有已定结果的场，offer / why_ended 都齐了。")

if __name__=="__main__":
    scan(all_flag=("--all" in sys.argv))
