#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股指数分析器 v4.0（搜索优先版）
数据策略：
  1. 通过 baidu/google 搜索获取实时价格
  2. 通过 eastmoney/sina 历史接口获取收盘价（回退）
  3. 腾讯财经历史K线（回退）
计算 MA / RSI(14) / MACD，输出分析报告
"""

import sys
import json
import re
import os
import subprocess
from datetime import datetime

# ── 常量 ────────────────────────────────────────────────────────────────────
INDICES = [
    {"Name": "上证指数", "Code": "000001", "Market": "sh"},
    {"Name": "深证成指", "Code": "399001", "Market": "sz"},
    {"Name": "创业板指", "Code": "399006", "Market": "sz"},
    {"Name": "上证50",  "Code": "000016", "Market": "sh"},
    {"Name": "沪深300", "Code": "000300", "Market": "sh"},
    {"Name": "中证500", "Code": "000905", "Market": "sh"},
]

ETF_POOL = {
    "000001": [
        {"code": "510210", "name": "富国上证指数ETF",  "scale": "4.5亿",  "fee": "0.60%"},
        {"code": "000159", "name": "华夏上证指数ETF",  "scale": "3.2亿",  "fee": "0.50%"},
    ],
    "399001": [
        {"code": "159903", "name": "南方深证成指ETF",  "scale": "5.1亿",  "fee": "0.60%"},
    ],
    "399006": [
        {"code": "159915", "name": "易方达创业板ETF",  "scale": "82亿",   "fee": "0.15%"},
        {"code": "159952", "name": "嘉实创业板ETF",    "scale": "3.8亿",  "fee": "0.50%"},
    ],
    "000016": [
        {"code": "510100", "name": "易方达上证50ETF",  "scale": "18亿",   "fee": "0.15%"},
        {"code": "510710", "name": "博时上证50ETF",    "scale": "6.3亿",  "fee": "0.30%"},
    ],
    "000300": [
        {"code": "510300", "name": "华泰柏瑞沪深300ETF","scale": "320亿",  "fee": "0.15%"},
        {"code": "159919", "name": "华夏沪深300ETF",   "scale": "38亿",   "fee": "0.50%"},
    ],
    "000905": [
        {"code": "510500", "name": "南方中证500ETF",   "scale": "86亿",   "fee": "0.15%"},
        {"code": "159922", "name": "华夏中证500ETF",   "scale": "8.2亿",  "fee": "0.50%"},
    ],
}


# ── 数据获取：搜索方式 ───────────────────────────────────────────────────────

def fetch_via_web_search():
    """
    通过 MCP batch_web_search 工具搜索各指数实时价格
    由于 subprocess 调用受限，改为直接 HTTP 请求
    """
    results = {}
    # 搜索queries
    queries = [
        ("上证指数 000001 实时", "000001"),
        ("深证成指 399001 实时", "399001"),
        ("创业板指 399006 实时", "399006"),
        ("沪深300 000300 实时",  "000300"),
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
    }

    import urllib.request, ssl
    ctx = ssl.create_default_context()

    # 通过 eastmoney 指数实时行情 API
    secids = ";".join(
        f"{'1' if idx['Market']=='sh' else '0'}{idx['Code']}"
        for idx in INDICES
    )
    url = (
        f"https://push2.eastmoney.com/api/qt/ulist.np/get"
        f"?fltt=2&invt=4&secids={secids}"
        f"&fields=f2,f3,f4,f5,f6,f12,f14,f15,f16,f17,f18&cb="
    )
    try:
        req = urllib.request.Request(url, headers={
            **headers,
            "Referer": "https://quote.eastmoney.com/",
        })
        resp = urllib.request.urlopen(req, timeout=8, context=ctx)
        raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
        for item in data.get("data", {}).get("diff", []):
            code = item.get("f12", "")
            pct  = item.get("f3", 0)
            chg  = item.get("f4", 0)
            price = item.get("f2", 0)
            results[code] = {
                "price": float(price) if price else None,
                "pct":   float(pct)   if pct   is not None else 0,
                "chg":   float(chg)   if chg   is not None else 0,
            }
        return results
    except Exception as e:
        print(f"[WARN] eastmoney failed: {e}", file=sys.stderr)
        return {}


def fetch_historical_prices():
    """获取各指数历史收盘价（腾讯财经接口）"""
    import urllib.request, ssl
    ctx = ssl.create_default_context()
    hist = {}

    for idx in INDICES:
        code   = idx["Code"]
        market = idx["Market"]
        full   = f"{market}{code}"
        # 腾讯财经历史K线
        url = (
            f"https://web.ifzq.gtimg.cn/appstock/app/kline/mkline"
            f"?param={full},day,,,,,65,qfq"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=6, context=ctx)
            raw = resp.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
            day_data = (
                data.get("data", {})
                .get(full, {})
                .get("qfqday") or
                data.get("data", {})
                .get(full, {})
                .get("day", [])
            )
            prices = []
            for d in day_data:
                if len(d) >= 2:
                    try: prices.append(float(d[1]))
                    except: continue
            hist[code] = prices
        except Exception as e:
            print(f"[WARN] qq hist failed for {code}: {e}", file=sys.stderr)
            hist[code] = []

    return hist


# ── 技术指标 ─────────────────────────────────────────────────────────────────

def calc_tech(prices):
    if not prices or len(prices) < 5:
        return {}
    p = prices[-60:]

    def ma(n):
        return round(sum(p[-n:]) / n, 3) if len(p) >= n else None

    def rsi14():
        if len(p) < 15: return None
        g, l = 0.0, 0.0
        for i in range(1, 15):
            d = p[-i] - p[-i-1]
            if d > 0: g += d
            else:    l -= d
        return round(100 - 100 / (1 + g / l), 1) if l else 100.0

    def ema_(data, n):
        k = 2 / (n + 1)
        r = [data[0]]
        for v in data[1:]: r.append(v * k + r[-1] * (1 - k))
        return r

    def macd_():
        if len(p) < 35: return None, None, None
        e12 = ema_(p, 12); e26 = ema_(p, 26)
        dif = [a - b for a, b in zip(e12, e26)]
        dea = ema_(dif, 9)
        hist = [2 * (d - e) for d, e in zip(dif, dea)]
        return round(dif[-1], 3), round(dea[-1], 3), round(hist[-1], 3)

    ma5  = ma(5);  ma10 = ma(10)
    ma20 = ma(20); ma60 = ma(60)
    rsi  = rsi14()
    dif, dea, hist = macd_()

    bull_ma   = bool(ma20 and ma60 and p[-1] > ma20 > ma60)
    bull_rsi  = bool(rsi and rsi < 70)
    bull_macd = bool(dif and dea and dif > dea)
    score = sum([bull_ma, bull_rsi, bull_macd])

    if ma20 and ma60 and p[-1] > ma20 > ma60: trend = "多头排列"
    elif ma20 and ma60: trend = "均线纠缠"
    elif ma20: trend = "弱势"
    else: trend = "数据不足"

    return {
        "ma5": ma5, "ma10": ma10, "ma20": ma20, "ma60": ma60,
        "rsi": rsi, "dif": dif, "dea": dea, "hist": hist,
        "bull_ma": bull_ma, "bull_rsi": bull_rsi, "bull_macd": bull_macd,
        "score": score, "trend": trend, "price": p[-1],
    }


def judge(score, rsi):
    if score >= 3:
        if rsi and rsi < 60: return "🟢 积极布局", 5, "各项指标向好，可考虑建仓"
        elif rsi and rsi < 70: return "🟡 轻仓介入", 2, "趋势向好但 RSI 已偏高，轻仓试探"
        return "🟢 积极布局", 3, "技术面整体向好，可适当布局"
    elif score == 2: return "🟡 轻仓介入", 2, "部分指标向好，谨慎乐观"
    elif score == 1: return "🟡 谨慎观望", 1, "技术面偏弱，建议等待"
    return "🔴 谨慎观望", 0, "技术指标偏空，建议回避"


# ── 报告构建 ────────────────────────────────────────────────────────────────

def build_report():
    today = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 获取实时数据
    rt_data = fetch_via_web_search()

    # 获取历史数据
    hist_data = fetch_historical_prices()

    # 计算技术指标
    tech = {}
    for idx in INDICES:
        code = idx["Code"]
        prices = hist_data.get(code, [])
        t = calc_tech(prices)
        t["realtime"] = rt_data.get(code, {})
        tech[code] = t

    out = []
    out.append(f"# 📊 今日指数分析\n")
    out.append(f"**分析时间：{today}**  |  数据仅供参考，不构成投资建议\n\n")

    # ── 指数一览 ───────────────────────────────────────────────────
    out.append("---\n## 一，主要指数一览\n\n")
    out.append("| 指数 | 代码 | 最新价 | 涨跌幅 | RSI(14) | 趋势 | 操作建议 |\n")
    out.append("|------|------|--------|--------|---------|------|----------|\n")
    for idx in INDICES:
        c  = idx["Code"]
        t  = tech[c]
        r  = t.get("realtime", {})
        price = r.get("price")
        pct   = r.get("pct", 0)
        score = t.get("score", 0)
        rsi   = t.get("rsi")
        act, _, _ = judge(score, rsi)
        if price:
            arrow = "📈" if pct > 0 else "📉" if pct < 0 else "➡️"
            out.append(
                f"| {idx['Name']} | `{c}` | {price:.2f} {arrow} | "
                f"{pct:+.2f}% | {f'{rsi:.1f}' if rsi else '—'} | "
                f"{t.get('trend','—')} | {act} |\n"
            )
        else:
            out.append(
                f"| {idx['Name']} | `{c}` | — | — | "
                f"{f'{rsi:.1f}' if rsi else '—'} | "
                f"{t.get('trend','—')} | 🔴 数据获取失败 |\n"
            )

    # ── 技术指标详情 ─────────────────────────────────────────────
    out.append("\n## 二，技术指标详情\n\n")
    out.append("| 指数 | MA5 | MA20 | MA60 | DIF | DEA | MACD柱 | 均线状态 | RSI |\n")
    out.append("|------|-----|------|------|-----|-----|--------|---------|-----|\n")
    for idx in INDICES:
        c = idx["Code"]
        t = tech[c]
        out.append(
            f"| {idx['Name']} | "
            f"{t.get('ma5','—')} | {t.get('ma20','—')} | {t.get('ma60','—')} | "
            f"{t.get('dif','—')} | {t.get('dea','—')} | {t.get('hist','—')} | "
            f"{t.get('trend','—')} | "
            f"{f'{t.get('rsi'):.1f}' if t.get('rsi') else '—'} |\n"
        )

    # ── 强势指数 ──────────────────────────────────────────────────
    strong = [
        (idx, tech[idx["Code"]])
        for idx in INDICES
        if tech[idx["Code"]].get("score", 0) >= 2
        and not tech[idx["Code"]].get("rsi", 100) >= 70
    ]
    out.append("\n## 三、强势指数（重点关注）\n\n")
    if strong:
        out.append("| 指数 | 操作建议 | 建议仓位 | 理由 |\n")
        out.append("|------|----------|---------|------|\n")
        for idx, t in strong:
            act, pos, reason = judge(t.get("score", 0), t.get("rsi"))
            out.append(f"| **{idx['Name']}** | {act} | 约{pos}成仓 | {reason} |\n")
        out.append("\n> 💡 以上指数满足 2 项以上技术向好条件，可作为近期重点关注\n")
    else:
        out.append("今日暂无指数满足强势条件，建议整体保持谨慎。\n")

    # ── ETF 推荐 ──────────────────────────────────────────────────
    out.append("\n## 四、对应当日ETF推荐\n\n")
    out.append("| 关联指数 | ETF代码 | 基金名称 | 规模 | 费率 | 今日涨跌 | 操作 |\n")
    out.append("|---------|---------|---------|------|------|---------|------|\n")
    for idx in INDICES:
        c = idx["Code"]
        etfs = ETF_POOL.get(c, [])
        t = tech[c]
        r  = t.get("realtime", {})
        pct = r.get("pct", 0)
        act, _, _ = judge(t.get("score", 0), t.get("rsi"))
        if not etfs:
            out.append(f"| {idx['Name']} | — | — | — | — | — | 🔴 无 |\n")
        for etf in etfs:
            pct_s = f"{pct:+.2f}%" if pct else "—"
            out.append(
                f"| {idx['Name']} | `{etf['code']}` | {etf['name']} | "
                f"{etf['scale']} | {etf['fee']} | {pct_s} | {act} |\n"
            )

    # ── 综合建议 ──────────────────────────────────────────────────
    all_scores = [tech[idx["Code"]].get("score", 0) for idx in INDICES]
    all_rsis   = [tech[idx["Code"]].get("rsi") for idx in INDICES
                  if tech[idx["Code"]].get("rsi")]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    avg_rsi   = sum(all_rsis) / len(all_rsis) if all_rsis else 50
    strong_n  = sum(1 for s in all_scores if s >= 3)
    weak_n    = sum(1 for s in all_scores if s <= 1)

    out.append("\n---\n## 五，综合操作建议\n\n")
    if avg_score >= 2.5 and avg_rsi < 70:
        level  = "🟢 整体积极，可适度布局"
        reason = (f"技术面向好（{strong_n}个指数强势），平均RSI {avg_rsi:.1f}，"
                  f"建议仓位 3~5 成，沪深300 + 中证500 组合优先。")
    elif avg_score >= 1.5:
        level  = "🟡 整体中性，轻仓试探"
        reason = (f"市场分化（积极{strong_n}个，偏弱{weak_n}个），平均RSI {avg_rsi:.1f}，"
                  f"建议仓位 1~2 成，不追高。")
    else:
        level  = "🔴 整体谨慎，观望为主"
        reason = (f"技术面偏弱（积极仅{strong_n}个，平均RSI {avg_rsi:.1f}），"
                  f"建议仓位 0~1 成，耐心等待机会。")

    out.append(f"### {level}\n\n{reason}\n\n")
    out.append("**操作原则：**\n")
    out.append("- 📈 沪深主板关注回调低吸，不追高\n")
    out.append("- ⚠️ 创业板 RSI 偏高时避免追涨\n")
    out.append("- 📊 沪深300 + 中证500 组合分散风险\n")
    out.append("- 💰 分批建仓，总仓位不超过 5 成\n\n")

    # ── ETF 速查 ──────────────────────────────────────────────────
    out.append("---\n## 六、ETF代码速查表\n\n")
    out.append("| 指数 | 代码 | 首选ETF | ETF代码 |\n")
    out.append("|------|------|---------|--------|\n")
    for idx in INDICES:
        c    = idx["Code"]
        etfs = ETF_POOL.get(c, [])
        main = etfs[0] if etfs else None
        if main:
            out.append(f"| {idx['Name']} | `{c}` | {main['name']} | `{main['code']}` |\n")

    out.append("\n> ⚠️ **免责声明**：本分析仅基于历史价格的技术指标计算，"
               "不构成投资建议。市场有风险，入市需谨慎。\n")

    return "".join(out)


if __name__ == "__main__":
    try:
        print(build_report())
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
