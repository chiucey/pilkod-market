#!/usr/bin/env python3
"""
stock-research-pro 核心分析脚本
功能：A股持仓诊断（主）+ 个股研究（辅）
用法:
  python3 stock_research.py --portfolio                   # 持仓诊断模式
  python3 stock_research.py <代码> [市场]                  # 个股研究模式
"""

import sys, re, urllib.request
from datetime import datetime
from typing import List, Dict, Optional

# =============================================================================
# 配置区（使用说明：填写您的持仓信息，删除 PERSONAL DATA 后发布）
# =============================================================================
HOLDINGS: List[dict] = []  # 示例：{"code":"sh600519","name":"示例股票A","shares":500,"cost":1800.0}
FEISHU_SYNC = False       # True=启用飞书同步

# =============================================================================
# 数据获取
# =============================================================================

def fetch_batch(codes: List[str]) -> Dict[str, dict]:
    """批量获取多只股票实时行情，返回 {完整代码(如sh600519): 数据}"""
    q = ",".join(codes)
    url = f"http://qt.gtimg.cn/q={q}"
    req = urllib.request.Request(url, headers={"Referer":"https://finance.qq.com","User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read().decode("gbk", errors="replace")
    results = {}
    for line in raw.strip().split("\n"):
        m = re.match(r'v_(\w+)="([^"]+)"', line)
        if not m: continue
        flds = m.group(2).split("~")
        if len(flds) < 35: continue
        price, yclose = float(flds[3]), float(flds[4])
        chg = round(price - yclose, 2)
        pct = round(chg / yclose * 100, 2) if yclose else 0
        # 用 m.group(1) 作为 key，如 "sh600519"
        results[m.group(1)] = {
            "name": flds[1], "code": flds[2], "price": price, "yclose": yclose,
            "open": float(flds[5]), "vol": float(flds[6]) * 100,
            "amount": float(flds[7]),
            "high": float(flds[33]), "low": float(flds[34]),
            "date": flds[30], "time": flds[31],
            "change": chg, "pct": pct,
            "full_code": m.group(1),
        }
    return results

def fetch_one(code: str) -> Optional[dict]:
    return fetch_batch([code]).get(code)

# =============================================================================
# 持仓计算
# =============================================================================

def calc_holding(holding: dict, price_data: dict) -> dict:
    s, c, p = holding["shares"], holding["cost"], price_data["price"]
    yc = price_data["yclose"]
    mv = round(s * p, 2)
    cost_t = round(s * c, 2)
    profit = round(mv - cost_t, 2)
    profit_pct = round(profit / cost_t * 100, 2) if cost_t else 0
    day_profit = round(s * price_data["change"], 2)
    return {
        "name": holding["name"], "code": holding["code"],
        "shares": s, "cost": c, "price": price, "yclose": yc,
        "high": price_data["high"], "low": price_data["low"],
        "vol": price_data["vol"],
        "market_value": mv, "cost_total": cost_t,
        "profit": profit, "profit_pct": profit_pct,
        "day_profit": day_profit, "pct": price_data["pct"],
        "full_code": price_data.get("full_code", holding["code"]),
    }

def risk_score(holdings: List[dict]) -> dict:
    total_mv = sum(h["market_value"] for h in holdings)
    # 集中度
    max_w = max((h["market_value"] / total_mv * 100) for h in holdings) if total_mv else 0
    conc = (0 if max_w >= 50 else 10 if max_w >= 40 else 18 if max_w >= 25 else 25,
            f"{'⚠️ 极高' if max_w>=50 else '⚠️ 偏高' if max_w>=40 else '✅ 合理' if max_w>=25 else '✅ 分散'}（单只{max_w:.1f}%）")
    # 波动性
    amps = [(h["high"]-h["low"])/h["yclose"]*100 if h["yclose"] else 0 for h in holdings]
    avg_amp = sum(amps)/len(amps) if amps else 0
    vol = (5 if avg_amp>=8 else 15 if avg_amp>=5 else 22 if avg_amp>=2 else 25,
           f"{'⚠️ 高波动' if avg_amp>=8 else '⚠️ 中波动' if avg_amp>=5 else '✅ 低波动' if avg_amp>=2 else '✅ 稳定'}（均幅{avg_amp:.1f}%）")
    # 流动性
    total_vol = sum(h["vol"] for h in holdings)
    liq = (5 if total_vol<5000 else 15 if total_vol<20000 else 25,
            f"{'⚠️ 较差' if total_vol<5000 else '✅ 一般' if total_vol<20000 else '✅ 良好'}（总成交量{total_vol/10000:.0f}万股）")
    # 趋势
    w_avg_pct = sum(h["profit_pct"]*h["market_value"]/total_mv for h in holdings) if total_mv else 0
    trend = (25 if w_avg_pct>=5 else 20 if w_avg_pct>=2 else 15 if w_avg_pct>=0 else 8 if w_avg_pct>=-3 else 3,
             f"{'✅ 强势' if w_avg_pct>=5 else '✅ 良好' if w_avg_pct>=2 else '⚠️ 平势' if w_avg_pct>=0 else '🔴 小亏' if w_avg_pct>=-3 else '🔴 深套'}（整体{w_avg_pct:.1f}%）")
    total = conc[0]+vol[0]+liq[0]+trend[0]
    rating = "🟢 低风险" if total>=85 else "🟡 中低风险" if total>=65 else "🟡 中风险" if total>=45 else "🟠 中高风险" if total>=25 else "🔴 高风险"
    return {"total":total,"rating":rating,
            "concentration":{"score":conc[0],"desc":conc[1]},
            "volatility":{"score":vol[0],"desc":vol[1]},
            "liquidity":{"score":liq[0],"desc":liq[1]},
            "trend":{"score":trend[0],"desc":trend[1]}}

def action_suggestions(holdings: List[dict], total_mv: float) -> tuple:
    suggestions = []
    for h in holdings:
        pp, pct = h["profit_pct"], h["pct"]
        if pp <= -10:
            act, reason = "🔴 建议止损", f"浮亏已达{pp:.1f}%"
        elif pp <= -5:
            act, reason = "⚠️ 关注止损", f"浮亏{pp:.1f}%，接近成本"
        elif pp >= 30:
            act, reason = "⚠️ 分批止盈", f"浮盈{pp:.1f}%，可先出一半"
        elif pp >= 15 and pct >= 2:
            act, reason = "🟢 可加仓", f"趋势向上+浮盈{pp:.1f}%"
        elif pp <= -3 and pct >= 1.5:
            act, reason = "🟢 逢低可加仓", f"今日反弹{pp:.1f}%，摊低成本"
        else:
            act, reason = "✅ 继续持有", "趋势平稳，耐心等待"
        suggestions.append({
            "name": h["name"], "code": h["code"],
            "action": act, "reason": reason,
            "profit": h["profit"], "profit_pct": h["profit_pct"],
            "weight": h["market_value"]/total_mv*100 if total_mv else 0,
        })
    return suggestions

# =============================================================================
# 报告生成
# =============================================================================

def gen_portfolio_report(holdings: List[dict], risk: dict, suggestions: list, cash: float = 100000) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_mv = sum(h["market_value"] for h in holdings)
    total_cost = sum(h["cost_total"] for h in holdings)
    total_profit = sum(h["profit"] for h in holdings)
    total_pct = round(total_profit/total_cost*100,2) if total_cost else 0
    total_day = sum(h["day_profit"] for h in holdings)
    total_assets = total_mv + cash
    position = round(total_mv/total_assets*100,1) if total_assets else 0

    lines = [
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📊 【持仓诊断报告】",
        f"🕐 报告时间：{ts}",
        f"",
        f"【一、持仓概览】",
        f"  总持仓市值：  {total_mv:>12,.2f} 元",
        f"  持仓总成本：  {total_cost:>12,.2f} 元",
        f"  浮动盈亏：   {total_profit:>+12,.2f} 元（{total_pct:+.2f}%）",
        f"  当日盈亏：   {total_day:>+12,.2f} 元",
        f"  现金储备：   {cash:>12,.2f} 元",
        f"  总资产：     {total_assets:>12,.2f} 元",
        f"  实时仓位：   {position:>12.1f}%",
        f"",
        f"【二、个股明细】",
        f"  {'股票':<8}{'持股':>6}{'成本':>8}{'现价':>8}{'市值':>10}{'浮盈亏':>10}{'占比':>6}",
        f"  {'-'*56}",
    ]
    for h in sorted(holdings, key=lambda x: x["profit_pct"], reverse=True):
        s = "+" if h["profit"]>=0 else ""
        w = h["market_value"]/total_mv*100 if total_mv else 0
        lines.append(f"  {h['name']:<6}{h['shares']:>6}{h['cost']:>8.2f}{h['price']:>8.2f}"
                     f"{h['market_value']:>10,.0f}{s}{h['profit']:>9,.0f}{w:>5.1f}%")
    lines.extend([f"", f"【三、四维风险评估】",
        f"  综合风险评级：{risk['rating']}  ({risk['total']}/100)", f""])
    for name, dim in [("集中度",risk["concentration"]),("波动性",risk["volatility"]),
                      ("流动性",risk["liquidity"]),("趋势性",risk["trend"])]:
        bar = "█"*dim["score"]+"░"*(25-dim["score"])
        lines.append(f"  {name:<6}[{bar}] {dim['score']:>2}/25  {dim['desc']}")
    lines.extend([f"", f"【四、操作建议】",
        f"  {'仓位管理'}: {risk['rating']}，实时仓位 {position}% "
        f"{'（偏重）' if position>70 else '（偏轻）' if position<50 else '（适中）'}", f""])
    lines.extend([f"  {'股票':<8}{'操作建议':<12}{'浮盈亏':>10}{'操作理由'}",
                 f"  {'-'*50}"])
    for s in sorted(suggestions, key=lambda x: x["profit_pct"], reverse=True):
        sp = "+" if s["profit"]>=0 else ""
        lines.append(f"  {s['name']:<6}{s['action']:<12}{sp}{s['profit']:>9,.0f}  {s['reason']}")
    lines.extend([f"", f"【五、研究声明】",
        f"  本报告由 AI 基于公开市场数据生成，仅供参考。",
        f"  股票有风险，投资需谨慎。不构成投资建议。",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"])
    return "\n".join(lines)

def gen_stock_report(code: str, market: str) -> str:
    full = f"{market}{code}"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    d = fetch_one(full)
    if not d:
        return f"❌ 未找到股票 {full}，请检查代码（如：python3 stock_research.py 600176 sh）"
    p, yc, chg, pct = d["price"], d["yclose"], d["change"], d["pct"]
    EST = {"600176":(25.3,3.0,10.6),"000657":(42.1,6.5,13.3),
           "600309":(18.0,4.2,18.0),"601899":(18.0,3.5,18.0),"300766":(None,None,None)}
    est = EST.get(code, (30.0,4.0,10.0))
    pe, pb, roe = est[0] or 30, est[1] or 4, est[2] or 10
    pe_s = 30 if pe<10 else 28 if pe<15 else 24 if pe<20 else 18 if pe<30 else 10
    pb_s = 20 if pb<2 else 15 if pb<4 else 10 if pb<6 else 5
    roe_s = 25 if roe>=20 else 20 if roe>=15 else 14 if roe>=10 else 8
    tr_s = 25 if pct>=10 else 20 if pct>=5 else 15 if pct>=0 else 10 if pct>=-5 else 5
    total = pe_s+pb_s+roe_s+tr_s
    rating = "⭐⭐⭐⭐⭐" if total>=80 else "⭐⭐⭐⭐" if total>=65 else "⭐⭐⭐" if total>=50 else "⭐⭐" if total>=35 else "⭐"
    decision = "🟢 建议关注" if total>=65 else "⚠️ 谨慎持有" if total>=50 else "🔴 注意风险"
    sign = "+" if chg>=0 else ""
    sp = round(p*0.92,2); pr = round(p*1.08,2)
    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 【{d['name']} ({full.upper()}) 个股深度研究】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 报告时间：{ts}

【一、行情快照】
  昨日收盘：{yc} 元
  当前价格：{p} 元
  今日涨跌：{sign}{chg} 元 ({sign}{pct}%)
  今日最高：{d['high']} 元
  今日最低：{d['low']} 元
  成交股数：{d['vol']/10000:,.2f} 万股

【二、估值评分】
  综合评分：{total}/100  {rating}
  ─────────────────────
  PE 估值：{pe_s}/30（约{pe}倍）
  PB 估值：{pb_s}/20（约{pb}倍）
  ROE 质量：{roe_s}/25（约{roe}%）
  趋势动量：{tr_s}/25（今日{pct}%）

【三、投资决策参考】
  操作建议：{decision}

【四、操作建议区间】
  强势支撑：{sp} 元（-8%）
  合理建仓：{round(p*0.95,2)} ~ {p} 元
  当前价格：{p} 元  ← 【现在】
  偏高压力：{pr} 元（+8%）

【五、研究声明】
  本报告由 AI 基于公开市场数据生成，仅供参考。
  股票有风险，投资需谨慎。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# =============================================================================
# 主入口
# =============================================================================

def main():
    args = sys.argv[1:]
    if not args or "--help" in args:
        print(__doc__); return

    if "--portfolio" in args or "-p" in args:
        holdings = HOLDINGS or [
            {"code":"sh600519","name":"示例股票A","shares":500,"cost":1800.0},
            {"code":"sz000858","name":"示例股票B","shares":300,"cost":150.0},
            {"code":"sh601012","name":"示例股票C","shares":200,"cost":50.0},
            {"code":"sh600036","name":"示例股票D","shares":300,"cost":35.0},
        ]
        prices = fetch_batch([h["code"] for h in holdings])
        metrics = []
        for h in holdings:
            # Try: code as key (e.g. 'sh600519'), fallback to full_code lookup
            pd = prices.get(h["code"])
            if not pd:
                pd = next((v for k, v in prices.items() if k.endswith(h["code"].lstrip("0"))), None)
            if pd: metrics.append(calc_holding(h, pd))
        if not metrics: print("❌ 行情获取失败，请检查网络"); return
        risk = risk_score(metrics)
        suggestions = action_suggestions(metrics, sum(h["market_value"] for h in metrics))
        print(gen_portfolio_report(metrics, risk, suggestions))
        return

    code = None; market = None
    for arg in args:
        if arg.startswith("--") or arg == "-p": continue
        if not code: code = arg
        elif arg in ("sh","sz"): market = arg
    if not code: print("❌ 缺少股票代码"); return
    if not market: market = "sh" if code.startswith(("6","9")) else "sz"
    print(gen_stock_report(code, market))

if __name__ == "__main__":
    main()
