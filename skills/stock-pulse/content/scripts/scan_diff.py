#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
盘中变化扫描（diff模式）
只报告和上次扫描相比的实质性变化，过滤噪音
"""

import json, os, sys, urllib.request, urllib.parse
from datetime import datetime

API_KEY  = "sk-proj-01-C6zO2mA6au--akYsqVvtHnvmamnoh90wVpNR0Nh9KICl8Rf6CTAtz5BZPOyLJsK_M3Zn529iX3OorzAhJP_HdYi83fbZGfSNEFewJ0sKXmDpAWfsZkeWu3lZ7YK-Dl6MiBdzuw"
API_HOST = "https://openapi.iwencai.com"
STATE_FILE = "/workspace/周期女王战法/daily/.scan_state.json"
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)


def q(query_str, page=1, per_page=30):
    params = urllib.parse.urlencode({
        "query": query_str, "page": page, "per_page": per_page,
        "source": "ths", "cache": 0, "expand_index": "true",
    })
    req = urllib.request.Request(
        f"{API_HOST}/v1/query2data?{params}",
        headers={"Authorization": f"Bearer {API_KEY}"},
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"[WARN] {e}", file=sys.stderr)
        return {"success": False, "datas": []}


def get_lianban_map():
    r = q("A股涨停统计 连板 股票代码 股票简称 连续涨停天数", per_page=100)
    result = {}
    for d in r.get("datas", []):
        code = d.get("股票代码", "")
        lb = next((v for k, v in d.items() if "连续涨停天数" in k), 0)
        reason = next((v for k, v in d.items() if "涨停原因" in k), "")
        if code and lb:
            result[code] = {"lianban": int(lb), "reason": str(reason)}
    return result


def _date_key(d, prefix):
    for k in d:
        if prefix in k:
            return k
    return None


def parse(s):
    c10_k = _date_key(s, "涨跌幅")
    t10_k = _date_key(s, "换手率")
    return {
        "code":  s.get("股票代码", ""),
        "name":  s.get("股票简称", ""),
        "price": s.get("最新价", 0),
        "c10":   s.get(c10_k, 0) if c10_k else 0,
        "t10":   s.get(t10_k, 0) if t10_k else 0,
        "today": s.get("最新涨跌幅", 0),
        "turn_d": s.get("换手率[20260420]", 0),
    }


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(current):
    with open(STATE_FILE, "w") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)


def run_diff():
    now = datetime.now()
    now_str = now.strftime("%H:%M")
    prev = load_state()

    # ── 真实连板 ──
    lb_map = get_lianban_map()
    lb_stocks = {code: info for code, info in lb_map.items() if info["lianban"] >= 2}
    prev_lb = prev.get("lianban", {})

    # ── 今日涨停统计（判断封板状态）──
    r_up = q("A股涨停统计 连板 股票代码 股票简称 连续涨停天数", per_page=100)
    today_limitup = set(d.get("股票代码","") for d in r_up.get("datas",[])
                       if any("涨停" in k and "2026" in k for k in d.keys())
                       or d.get("股票简称","") in [s.get("股票简称","") for s in r_up.get("datas",[])])

    # ── 池1: 10日涨幅TOP30（含真实连板数据）──
    r1 = q("A股10日涨幅排行榜前30名 股票代码 股票名称 涨跌幅 换手率", per_page=30)
    pool1 = {d.get("股票代码",""): parse(d) for d in r1.get("datas",[]) if d.get("股票代码")}
    pool1 = {**pool1, **{code: {**v, "lianban": lb_map.get(code,{}).get("lianban",0), "reason": lb_map.get(code,{}).get("reason","")}
                          for code,v in pool1.items() if code in lb_map}}

    # ── 成交额TOP30（监控资金变化）──
    r2 = q("A股成交额排行榜前30名 股票代码 股票简称 涨跌幅 换手率 成交额", per_page=30)
    pool2 = {d.get("股票代码",""): parse(d) for d in r2.get("datas",[]) if d.get("股票代码")}

    prev_pool1 = prev.get("pool1", {})
    prev_pool2 = prev.get("pool2", {})
    prev_lb    = prev.get("lianban", {})

    changes = []

    # ── ① 连板数变化（新增/升级）──
    for code, info in lb_stocks.items():
        lb = info["lianban"]
        prev_lb_val = prev_lb.get(code, {}).get("lianban", 0)
        if code not in prev_lb:
            changes.append(("🆕新晋连板", code, f"{info.get('name', code)} 今日{info['lianban']}连板｜{info['reason'][:30]}"))
        elif lb > prev_lb_val:
            changes.append(("⬆️连板升级", code, f"{info.get('name', code)} {prev_lb_val}连板→{lb}连板｜{info['reason'][:30]}"))

    # ── ② 炸板警报：上次涨停→今不涨停 ──
    prev_limitup = prev.get("limitup_set", set())
    for code in prev_limitup:
        if code not in today_limitup and code in pool1:
            today_chg = pool1[code].get("today", 0)
            name = pool1[code].get("name","")
            changes.append(("💥炸板警报", code, f"{name} 涨停→{today_chg:+.2f}%"))

    # ── ③ 新晋涨停：上次未涨停→今涨停 ──
    for code in today_limitup:
        if code not in prev_limitup and code in pool1:
            name = pool1[code].get("name","")
            lb = pool1[code].get("lianban", 0)
            changes.append(("🔴新晋涨停", code, f"{name} {'['+str(lb)+'连板]' if lb>=2 else ''} 今日封板"))

    # ── ④ 换手率突变：>30%变化 → 主力异动 ──
    for code, v in pool1.items():
        prev_v = prev_pool1.get(code, {})
        if prev_v:
            t10 = v.get("turn_d",0) or v.get("t10",0)
            prev_t10 = prev_v.get("turn_d",0) or prev_v.get("t10",0)
            if t10 > 0 and prev_t10 > 0:
                delta = abs(t10 - prev_t10)
                if delta > 30:  # 换手变化>30个百分点
                    direction = "↑" if t10 > prev_t10 else "↓"
                    name = v.get("name","")
                    changes.append(("⚡换手{d}".format(d=direction), code,
                                   f"{name} 换手{prev_t10:.0f}%{direction}{t10:.0f}%"))

    # ── ⑤ 新进入10日涨幅TOP5（真龙信号）──
    prev_top5 = set(prev.get("top5_codes", []))
    curr_top5_codes = sorted(pool1.keys(),
                             key=lambda c: (pool1[c].get("today",0), pool1[c].get("lianban",0)),
                             reverse=True)[:5]
    curr_top5 = set(curr_top5_codes)
    for code in curr_top5 - prev_top5:
        name = pool1[code].get("name","")
        today = pool1[code].get("today",0)
        lb = pool1[code].get("lianban",0)
        changes.append(("🏆新晋TOP5", code,
                       f"{name} 今日+{today:.2f}%{'['+str(lb)+'连板]' if lb>=2 else ''} 进入今日强势前5"))

    # ── ⑥ 成交额TOP5新进入 ──
    prev_amt_top5 = set(prev.get("amt_top5", []))
    curr_amt = sorted(pool2.keys(),
                     key=lambda c: pool2[c].get("turn_d",0), reverse=True)[:5]
    for code in set(curr_amt) - prev_amt_top5:
        name = pool2[code].get("name","")
        changes.append(("💰资金涌入", code, f"{name} 进入成交额TOP5"))

    # ── 保存当前状态 ──
    curr_state = {
        "time": now_str,
        "lianban": {code: {"lianban": v["lianban"], "reason": v["reason"]}
                    for code, v in lb_stocks.items()},
        "limitup_set": list(today_limitup),
        "pool1": {code: {"today": v.get("today"), "turn_d": v.get("turn_d") or v.get("t10"),
                         "lianban": v.get("lianban")}
                  for code, v in pool1.items()},
        "pool2": {code: {"today": v.get("today"), "turn_d": v.get("turn_d") or v.get("t10")}
                  for code, v in pool2.items()},
        "top5_codes": curr_top5_codes,
        "amt_top5": curr_amt,
    }
    save_state(curr_state)

    # ── 输出报告 ──
    print(f"\n[{now_str}] 盘中扫描（变化模式）")
    print(f"连板监控: {len(lb_stocks)}只 ≥2连板 | 涨停: {len(today_limitup)}只")

    if not changes:
        print("\n✅ 无重大变化，连板稳固")
        return

    print(f"\n{'='*50}")
    print(f"📢 本次扫描发现 {len(changes)} 项变化:")
    print(f"{'='*50}")
    for tag, code, msg in sorted(changes, key=lambda x: (
        0 if "炸板" in x[0] else
        1 if "新晋涨停" in x[0] else
        2 if "连板" in x[0] else
        3)):
        print(f"  {tag} {msg}")

    print(f"\n{'='*50}")
    print("当前连板真龙：")
    for code, info in sorted(lb_stocks.items(), key=lambda x: -x[1]["lianban"])[:5]:
        name = pool1.get(code, {}).get("name","") or pool2.get(code,{}).get("name","") or code
        print(f"  【{info['lianban']}连板】{name}｜{info['reason'][:35]}")


if __name__ == "__main__":
    run_diff()
