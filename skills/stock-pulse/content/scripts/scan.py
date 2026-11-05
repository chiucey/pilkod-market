#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stock-pulse v8 MAX: 三池扫描 + 真实连板数据
池1: 10日涨幅TOP30  |  池2: 成交额TOP100  |  池3: 成交额∩人气共振
真实连板数据来源: iwencai "A股涨停统计 连板"
"""

import json, os, sys, urllib.request, urllib.parse
from datetime import datetime

API_KEY  = "sk-proj-01-C6zO2mA6au--akYsqVvtHnvmamnoh90wVpNR0Nh9KICl8Rf6CTAtz5BZPOyLJsK_M3Zn529iX3OorzAhJP_HdYi83fbZGfSNEFewJ0sKXmDpAWfsZkeWu3lZ7YK-Dl6MiBdzuw"
API_HOST = "https://openapi.iwencai.com"
OUT_DIR  = "/workspace/周期女王战法/daily"
os.makedirs(OUT_DIR, exist_ok=True)


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


# ── 真实连板数据查询 ─────────────────────────────────────
def get_lianban_map():
    """获取今日真实连板数据: {code: {lianban:int, reason:str}}"""
    r = q("A股涨停统计 连板 股票代码 股票简称 连续涨停天数", per_page=100)
    result = {}
    for d in r.get("datas", []):
        code = d.get("股票代码", "")
        lb = next((v for k, v in d.items() if "连续涨停天数" in k), 0)
        reason = next((v for k, v in d.items() if "涨停原因" in k), "")
        if code and lb:
            result[code] = {"lianban": int(lb), "reason": str(reason)}
    return result


# ── 解析iwencai带日期字段 ─────────────────────────────────
def _date_key(d, prefix):
    """找d中键名包含prefix的日期字段"""
    for k in d:
        if prefix in k:
            return k
    return None


def parse(s, pool=None):
    c10_k = _date_key(s, "涨跌幅")
    t10_k = _date_key(s, "换手率")
    end_k = _date_key(s, "20260")
    return {
        "code":     s.get("股票代码", ""),
        "name":     s.get("股票简称", ""),
        "price":    s.get("最新价", 0),
        "c10":      s.get(c10_k, 0) if c10_k else 0,
        "t10":      s.get(t10_k, 0) if t10_k else 0,
        "today":    s.get("最新涨跌幅", 0),
        "pool":     pool,
        "hot":      s.get("个股热度[20260420]"),
        "amount":   s.get("成交额[20260420]", 0),
        "turn_d":   s.get("换手率[20260420]", 0),
        "amplitude": s.get("振幅[20260420]", 0),
        "lianban":  0,
        "reason":   "",
    }


# ── 统一评分 ─────────────────────────────────────────────
def score_all(pool1, pool2, pool3, cross_codes, lianban_map):
    all_stocks = {}
    for s in pool1:
        all_stocks[s["code"]] = {**s, "in_10day": True}
    for s in pool2:
        code = s["code"]
        if code in all_stocks:
            all_stocks[code]["in_amount"] = True
        else:
            all_stocks[code] = {**s, "in_amount": True}
    for s in pool3:
        code = s["code"]
        if code in all_stocks:
            all_stocks[code]["in_hot"] = True
        else:
            all_stocks[code] = {**s, "in_hot": True}
    for code in cross_codes:
        if code in all_stocks:
            all_stocks[code]["in_cross"] = True

    results = []
    for code, s in all_stocks.items():
        c10    = s.get("c10", 0)
        t10    = s.get("t10", 0)
        today  = s.get("today", 0)
        hot    = s.get("hot")
        turn_d = s.get("turn_d") or (t10 / 10)
        amp    = s.get("amplitude") or 0

        # 真实连板数据
        lb_info = lianban_map.get(code, {})
        lianban = lb_info.get("lianban", 0)
        reason  = lb_info.get("reason", "")

        pos = "低位" if c10 < 30 else ("中位" if c10 <= 80 else "高位")

        # 风险
        risk = ""
        if   lianban >= 5:               risk = "🔴妖股连板"
        elif lianban >= 3:               risk = "🔴强势连板"
        elif pos == "高位" and t10 > 150: risk = "🔴高位派发"
        elif pos == "高位":               risk = "⚠️高位警戒"
        elif t10 > 200:                 risk = "⚠️超活跃换手"

        # ── v6量价分 ──
        vp = 2.0 if today >= 9.5 else 1.5 if today >= 7 else 1.0 if today >= 4 else 0.5 if today >= 0 else -1.5
        pot = min(40, c10 / 5 * 8)
        kin_t = min(30, today * 3) if today > 0 else max(-15, today * 2)
        kin = min(45, kin_t + 10)
        if c10 < 15:
            ma = max(20, 30 + c10 / 15 * 20)
        elif 15 <= c10 <= 50:
            ma = 70
        elif c10 < 80:
            ma = max(30, 70 - (c10 - 50) / 30 * 40)
        else:
            ma = 25
        f4 = round(ma * 0.3 + 80 * 0.25 + kin * 0.25 + pot * 0.2, 1)
        v6 = round((vp + 3) / 6 * 10 * 0.55 + f4 / 10 * 0.45, 1)

        # ── 龙头地位 ──
        fund = (5.0 if 15 <= turn_d <= 40 else
                4.0 if 8  <= turn_d <  15 else
                3.5 if 40 <  turn_d <= 60 else
                2.0 if turn_d > 60 else
                2.5 if 3  <= turn_d <   8 else 1.0)
        lead = (3.0 if today >= 9.5 else
                2.5 if today >= 7 else
                2.0 if today >= 5 else
                1.5 if today >= 3 else
                1.0 if today >= 0 else 0.0)
        amp_s = 1.5 if 5 <= amp <= 20 else 0.8 if amp > 20 else 0.5
        dragon = round((fund + lead + amp_s) / 10 * 10, 1)
        dlabel = "🐉真龙" if dragon >= 8.5 else "🐲准龙" if dragon >= 7.0 else "🔔龙套" if dragon >= 5.5 else "🐟杂鱼"

        # 连板符号
        lb_tag = f"【{lianban}连板】" if lianban >= 2 else ("涨停" if today >= 9.5 else "")

        # ── 池共振加分 ──
        pool_score = 0
        pools_bonus = []
        if s.get("in_10day"):     pool_score += 3; pools_bonus.append("10日")
        if s.get("in_cross"):     pool_score += 4; pools_bonus.append("成交∩人气")
        elif s.get("in_amount"):  pool_score += 2; pools_bonus.append("成交额")
        elif s.get("in_hot"):     pool_score += 1; pools_bonus.append("人气")

        # 连板额外加分：每连板一天+0.5分，上限3分
        lb_bonus = min(3.0, lianban * 0.5) if lianban >= 2 else 0.0

        # ── 综合分 ──
        final = round(v6 * 0.48 + dragon * 0.34 + pool_score * 0.13 / 6 * 10 + lb_bonus, 1)

        if   lianban >= 3: action = "✅强烈买入"
        elif final >= 8.5: action = "✅强烈买入"
        elif final >= 7.5: action = "✅买入"
        elif final >= 6.5: action = "⚠️谨慎买入"
        elif final >= 5.5: action = "⚠️观望"
        else:              action = "❌回避"

        results.append({
            **s,
            "pos": pos, "risk": risk, "lb_tag": lb_tag,
            "v6": v6, "dragon": dragon, "dlabel": dlabel,
            "pool_score": pool_score,
            "pools": "/".join(pools_bonus) if pools_bonus else "独立",
            "final": final, "action": action,
            "lianban": lianban, "lb_bonus": round(lb_bonus, 1),
            "reason": reason,
        })

    results.sort(key=lambda x: x["final"], reverse=True)
    return results


# ── 行业归属 ─────────────────────────────────────────────
def get_sectors(codes):
    raw = q(" ".join(codes) + " 所属同花顺行业", per_page=60)
    if isinstance(raw, dict):
        return {d["股票代码"]: (d.get("所属同花顺行业") or ["其它"])[0]
                for d in raw.get("datas", [])}
    return {}


# ── 主程序 ───────────────────────────────────────────────
def main():
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M")
    today_str = now.strftime("%Y-%m-%d")

    print(f"[{now_str}] 三池扫描开始...", flush=True)

    # 池1: 10日涨幅
    r1 = q("A股10日涨幅排行榜前30名 股票代码 股票名称 涨跌幅 换手率", per_page=30)
    pool1 = [parse(d, "10日涨幅") for d in r1.get("datas", []) if d.get("股票代码")]
    print(f"[{now_str}] 池1(10日涨幅): {len(pool1)}只", flush=True)

    # 池2: 成交额TOP100
    r2 = q("A股成交额排行榜前100名 股票代码 股票简称 涨跌幅 换手率 成交额", per_page=100)
    pool2_all = {d.get("股票代码") for d in r2.get("datas", []) if d.get("股票代码")}
    pool2 = [parse(d, "成交额") for d in r2.get("datas", []) if d.get("股票代码")]
    print(f"[{now_str}] 池2(成交额TOP100): {len(pool2)}只", flush=True)

    # 池3: 人气TOP20
    r3 = q("A股人气排行榜前20名 股票代码 股票简称 涨跌幅 个股热度", per_page=20)
    pool3_all = {d.get("股票代码") for d in r3.get("datas", []) if d.get("股票代码")}
    pool3 = [parse(d, "人气") for d in r3.get("datas", []) if d.get("股票代码")]
    print(f"[{now_str}] 池3(人气TOP20): {len(pool3)}只", flush=True)

    # 共振池 = 成交额TOP100 ∩ 人气TOP20
    cross_codes = pool2_all & pool3_all
    print(f"[{now_str}] 池2∩3共振: {len(cross_codes)}只", flush=True)

    # 真实连板数据
    lianban_map = get_lianban_map()
    lb_count = sum(1 for v in lianban_map.values() if v["lianban"] >= 2)
    print(f"[{now_str}] 真实连板(≥2天): {lb_count}只", flush=True)
    for code, info in sorted(lianban_map.items(), key=lambda x: x[1]["lianban"], reverse=True)[:5]:
        print(f"  {code} {info['lianban']}连板: {info['reason'][:40]}", flush=True)

    results = score_all(pool1, pool2, pool3, cross_codes, lianban_map)

    # 行业归属
    top30_codes = [s["code"] for s in results[:30]]
    sector_map = get_sectors(top30_codes)

    sec_groups = {}
    for s in results[:30]:
        sec = sector_map.get(s["code"], "其它")
        sec_groups.setdefault(sec, []).append(s)

    sec_info = {}
    for sec, members in sec_groups.items():
        leader = max(members, key=lambda x: x["final"])
        for s in members:
            is_ld = s["code"] == leader["code"]
            sec_info[s["code"]] = {
                "sector": sec,
                "is_leader": is_ld,
                "peers": len(members),
                "badge": "★行业龙头" if (is_ld and len(members) >= 2) else
                         (f"↑跟风{len(members)}只" if len(members) >= 2 else "独立题材"),
            }

    board_map = {"SZ": "深", "SH": "沪", "BJ": "北"}

    # ── 输出报告 ──
    lines = [
        f"📊 **v8 MAX+连板 · 三池共振扫描** | {now_str}",
        "`池1: 10日涨幅TOP30  |  池2: 成交额TOP100  |  池3: 成交额∩人气共振  |  ★=真实连板数据`",
        "",
        "```",
        f"  #   名称       板  今日涨跌   10日涨幅   10日换   v6   龙头  池共振           综合   信号      操作",
        "  " + "─" * 110,
    ]

    for i, x in enumerate(results[:20], 1):
        brd   = board_map.get(x["code"][-2:], "?")
        risk  = f" {x['risk']}" if x.get("risk") else ""
        sec   = sec_info.get(x["code"], {})
        badge = sec.get("badge", "")
        pools = f"[{x['pools']}]"
        lb_str = x.get("lb_tag", "")
        c10_str = f"{x['c10']:>+7.1f}%" if x.get("c10") else "     N/A"
        t10_str = f"{x['t10']:>5.1f}%" if x.get("t10") else "  N/A"
        v6_str  = f"{x['v6']:>4.1f}" if x.get("v6") else " N/A"
        dr_str  = f"{x['dragon']:>4.1f}" if x.get("dragon") else " N/A"
        lines.append(
            f" {i:>2}  {x['name']:<8} {brd}  {x['today']:>+8.2f}%  "
            f"{c10_str}  {t10_str}  {v6_str}   {dr_str}  {pools:<12} "
            f"{x['final']:>5.1f}  {x['dlabel']:<5}{badge:<12}{lb_str:<8}{x['action']}{risk}"
        )
    lines.append("```")

    # 三池共振
    cross = [x for x in results if x.get("pool_score", 0) >= 5]
    lines.extend(["", "🔥 **三池共振（同时在多个池）**"])
    if cross:
        for x in cross[:8]:
            sec = sec_info.get(x["code"], {})
            lb_str = f"[{x['lianban']}连板]" if x.get("lianban", 0) >= 2 else ""
            lines.append(
                f"  {x['dlabel']} {x['name']}（{x['code']}）{lb_str}"
                f" 今日{x['today']:+.2f}%｜{x['pools']}｜龙头{x['dragon']}｜"
                f"{sec.get('sector','')}｜综合{x['final']}分"
            )
    else:
        lines.append("  暂无三池共振股票")

    # 池1专属
    top10_only = [x for x in results if "10日" in x.get("pools","")]
    lines.extend(["", "📈 **10日涨幅专属机会**（趋势最强但资金/人气未必最强）"])
    for x in top10_only[:6]:
        lb_str = f"[{x['lianban']}连板]" if x.get("lianban", 0) >= 2 else ""
        lines.append(
            f"  {x['dlabel']} {x['name']}（{x['code']}）{lb_str}"
            f" 今日{x['today']:+.2f}%｜10日+{x.get('c10',0):.0f}%｜"
            f"换手{x.get('t10',0):.0f}%｜{x['action']}"
        )

    # 真实连板TOP
    lb_stocks = sorted(results, key=lambda x: x.get("lianban", 0), reverse=True)
    lb_top = [x for x in lb_stocks if x.get("lianban", 0) >= 2]
    if lb_top:
        lines.extend(["", f"🔴 **真实连板（来自iwencai涨停统计）**"])
        for x in lb_top[:8]:
            lines.append(
                f"  【{x['lianban']}连板】{x['name']}（{x['code']}）"
                f" 今日{x['today']:+.2f}%｜10日+{x.get('c10',0):.0f}%｜"
                f"换手{x.get('t10',0):.0f}%｜{x['action']}｜{x.get('reason','')[:30]}"
            )

    # 风险
    risky = [x for x in results if x.get("risk")]
    lines.extend(["", "⚠️ **风险警示**"])
    for x in risky[:6]:
        reason_str = f"｜{x['reason'][:20]}" if x.get("reason") else ""
        lines.append(f"  🔸 {x['name']} {x['risk']} 10日+{x.get('c10',0):.0f}%{reason_str}")

    lines.extend(["", "---",
                  f"_📁 `/workspace/周期女王战法/daily/{today_str}.json`_"])
    print("\n".join(lines))

    # 保存
    for x in results:
        x.update(sec_info.get(x["code"], {}))
    out = f"{OUT_DIR}/{today_str}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"time": now_str, "stocks": results,
                   "pool1_count": len(pool1),
                   "pool2_count": len(pool2),
                   "pool3_count": len(pool3),
                   "lianban_map": lianban_map},
                  f, ensure_ascii=False, indent=2)
    print(f"\n[OK] saved → {out}", flush=True)


if __name__ == "__main__":
    main()
