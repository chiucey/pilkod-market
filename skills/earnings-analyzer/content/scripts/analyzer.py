#!/usr/bin/env python3
"""
财报效应分析器
Usage:
  python analyzer.py --symbol XPEV.US --output /tmp/earnings_XPEV.html
  python analyzer.py --symbol TSLA.US --dates "2024-01-24,2024-04-23,2024-07-23,2024-10-23" --output /tmp/out.html
"""

import subprocess, json, argparse, sys, math
from datetime import datetime, timedelta

# ── 内置历史财报日期（可被 --dates 参数覆盖）────────────────────────────────
EARNINGS_DATES = {
    "XPEV.US": ["2024-03-19","2024-05-21","2024-08-20","2024-11-19",
                "2025-03-18","2025-05-21","2025-08-19","2025-11-17",
                "2026-03-20"],
    "TSLA.US": ["2024-01-24","2024-04-23","2024-07-23","2024-10-23",
                "2025-01-29","2025-04-22","2025-07-23","2025-10-22",
                "2026-01-28","2026-04-22"],
    "NVDA.US": ["2024-02-21","2024-05-22","2024-08-28","2024-11-20",
                "2025-02-26","2025-05-28","2025-08-27","2025-11-19",
                "2026-02-25"],
    "AAPL.US": ["2024-02-01","2024-05-02","2024-08-01","2024-10-31",
                "2025-01-30","2025-05-01","2025-07-31","2025-10-30",
                "2026-01-29"],
    "MSFT.US": ["2024-01-30","2024-04-25","2024-07-30","2024-10-30",
                "2025-01-29","2025-04-30","2025-07-30","2025-10-29",
                "2026-01-28"],
    "META.US":  ["2024-02-01","2024-04-24","2024-07-31","2024-10-30",
                 "2025-01-29","2025-04-30","2025-07-30","2025-10-29",
                 "2026-01-28"],
    "GOOGL.US": ["2024-01-30","2024-04-25","2024-07-23","2024-10-29",
                 "2025-02-04","2025-04-24","2025-07-23","2025-10-29",
                 "2026-02-04"],
    "AMZN.US":  ["2024-02-01","2024-04-30","2024-08-01","2024-10-31",
                 "2025-02-06","2025-05-01","2025-07-31","2025-10-30",
                 "2026-02-05"],
    "700.HK":   ["2024-03-20","2024-05-14","2024-08-14","2024-11-13",
                 "2025-03-19","2025-05-14","2025-08-13","2025-11-13",
                 "2026-03-18"],
    "9988.HK":  ["2024-02-07","2024-05-14","2024-08-15","2024-11-15",
                 "2025-02-20","2025-05-15","2025-08-29","2025-11-25",
                 "2026-03-19"],
    "1810.HK":  ["2024-03-19","2024-05-23","2024-08-21","2024-11-18",
                 "2025-03-18","2025-05-27","2025-08-19","2025-11-18",
                 "2026-03-24"],
    "UNH.US":   ["2024-01-12","2024-04-16","2024-07-16","2024-10-15",
                 "2025-01-16","2025-04-17","2025-07-29","2025-10-28",
                 "2026-01-27","2026-04-21"],
    "1211.HK":  ["2024-03-26","2024-04-29","2024-08-28","2024-10-30",
                 "2025-03-24","2025-04-25","2025-08-29","2025-10-30",
                 "2026-03-27"],
}

STOCK_NAMES = {
    "XPEV.US": "小鹏汽车", "TSLA.US": "特斯拉", "NVDA.US": "英伟达",
    "AAPL.US": "苹果",    "MSFT.US": "微软",   "META.US": "Meta",
    "GOOGL.US":"谷歌",    "AMZN.US": "亚马逊", "UNH.US":  "联合健康",
    "700.HK":  "腾讯",   "9988.HK": "阿里巴巴","1810.HK": "小米",
    "1211.HK": "比亚迪",
}

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout.strip()

def fetch_next_earnings_from_longbridge(symbol):
    """从 Longbridge finance-calendar 拉取未来已公告的下次财报日期"""
    today_str = datetime.today().strftime("%Y-%m-%d")
    end_str   = (datetime.today() + timedelta(days=365)).strftime("%Y-%m-%d")
    code = symbol.split(".")[0]
    out = run(["longbridge","finance-calendar","report",
               "--symbol", symbol, "--date", today_str,
               "--end-date", end_str, "--count", "20", "--format", "json"])
    try:
        data = json.loads(out)
        for day in data.get("list", []):
            for info in day.get("infos", []):
                if code in info.get("counter_id", ""):
                    return day["date"]
    except:
        pass
    return None

def fetch_past_earnings_from_longbridge(symbol):
    """从 Longbridge finance-calendar 拉取历史财报日期（非内置股票用）"""
    start_str = (datetime.today() - timedelta(days=900)).strftime("%Y-%m-%d")
    today_str = datetime.today().strftime("%Y-%m-%d")
    code = symbol.split(".")[0]
    out = run(["longbridge","finance-calendar","report",
               "--symbol", symbol, "--date", start_str,
               "--end-date", today_str, "--count", "50", "--format", "json"])
    try:
        data = json.loads(out)
        dates = []
        for day in data.get("list", []):
            for info in day.get("infos", []):
                if code in info.get("counter_id", ""):
                    dates.append(day["date"])
        return sorted(set(dates))
    except:
        return []

def fetch_earnings_from_web(symbol):
    """网页备选：用 yfinance 拉取历史财报日期"""
    try:
        import yfinance as yf
        if symbol.endswith(".US"):
            ticker_sym = symbol.replace(".US", "")
        elif symbol.endswith(".HK"):
            ticker_sym = symbol.replace(".HK", "").zfill(4) + ".HK"
        else:
            ticker_sym = symbol.split(".")[0]
        t = yf.Ticker(ticker_sym)
        hist = t.earnings_dates
        if hist is not None and len(hist) > 0:
            today_str = datetime.today().strftime("%Y-%m-%d")
            dates = []
            for idx in hist.index:
                try:
                    d = idx.strftime("%Y-%m-%d")
                    if d <= today_str:
                        dates.append(d)
                except:
                    pass
            return sorted(set(dates))
    except ImportError:
        print("[analyzer] 提示：安装 yfinance 可启用网页备选（pip install yfinance）")
    except Exception:
        pass
    return []

def get_klines(symbol):
    end   = datetime.today().strftime("%Y-%m-%d")
    start = (datetime.today() - timedelta(days=900)).strftime("%Y-%m-%d")
    out = run(["longbridge","kline","history",symbol,
               "--start",start,"--end",end,"--period","day","--format","json"])
    try:
        return json.loads(out)
    except:
        return []

def get_positions():
    out = run(["longbridge","positions","--format","json"])
    try:
        return json.loads(out)
    except:
        return []

def price_on_or_after(klines_map, date_str, offset=0):
    """取 date_str 后 offset 个交易日的收盘价，offset=0 为当天或最近一个交易日"""
    target = datetime.strptime(date_str, "%Y-%m-%d")
    dates  = sorted(klines_map.keys())
    # 找到 >= target 的日期
    target_str = target.strftime("%Y-%m-%d")
    after = [d for d in dates if d >= target_str]
    if not after:
        return None
    base_idx = dates.index(after[0])
    idx = base_idx + offset
    if 0 <= idx < len(dates):
        return klines_map[dates[idx]]
    return None

def analyze(symbol, earnings_dates, klines):
    klines_map = {k["time"][:10]: float(k["close"]) for k in klines}

    events = []
    for d in earnings_dates:
        p_pre5  = price_on_or_after(klines_map, d, -5)
        p_day   = price_on_or_after(klines_map, d,  0)
        p_post5 = price_on_or_after(klines_map, d,  5)
        p_post10= price_on_or_after(klines_map, d, 10)
        if not all([p_pre5, p_day, p_post5]):
            continue
        ret5  = (p_post5  / p_pre5 - 1) * 100
        ret10 = ((p_post10 / p_pre5 - 1) * 100) if p_post10 else None
        events.append({
            "date": d, "p_pre5": p_pre5, "p_day": p_day,
            "p_post5": p_post5, "p_post10": p_post10,
            "ret5": round(ret5, 1),
            "ret10": round(ret10, 1) if ret10 is not None else None,
            "up": ret5 > 0,
        })
    return events

def get_position_for(symbol, positions):
    for p in positions:
        if p.get("symbol") == symbol:
            return p
    return None

def build_strategies(symbol, events, position, name):
    if not events:
        return []

    up_prob  = sum(1 for e in events if e["up"]) / len(events) * 100
    avg_ret5 = sum(e["ret5"] for e in events) / len(events)
    bullish  = up_prob >= 50
    bearish  = up_prob < 40
    qty      = float(position.get("quantity", 0)) if position else 0
    cost     = float(position.get("cost_price", 0)) if position else 0
    has_pos  = qty > 0

    strategies = []

    # 策略1：基于历史胜率
    if bullish:
        s1_title = "观望等待，财报后追入"
        s1_desc  = f"{name} 历史财报上涨概率 {up_prob:.0f}%，但平均涨幅仅 {avg_ret5:+.1f}%，波动风险仍存在。建议财报发布后观察市场反应，若价格稳定在财报日收盘价上方，再考虑建仓或加仓，避免直接押注财报方向。"
        s1_risk  = "中"
    elif bearish:
        s1_title = "财报前适度减持，控制仓位"
        s1_desc  = f"{name} 历史财报下跌概率偏高（上涨概率仅 {up_prob:.0f}%），平均表现 {avg_ret5:+.1f}%。若当前持有仓位，可考虑在财报发布前5日内部分减持，保留核心仓位，降低单一事件风险。"
        s1_risk  = "低"
    else:
        s1_title = "维持现有仓位，不做方向性押注"
        s1_desc  = f"{name} 历史财报方向性不明确（上涨概率 {up_prob:.0f}%），在财报发布前不建议单边加仓或减仓，维持现有仓位，等待财报结果再决策。"
        s1_risk  = "低"

    # 策略2：基于持仓情况
    if has_pos:
        unrealized = (float(position.get("current_price", cost)) - cost) / cost * 100 if cost > 0 else 0
        if unrealized > 15:
            s2_title = "锁定部分浮盈，保护利润"
            s2_desc  = f"您持有 {qty:.0f} 股 {name}，浮盈约 {unrealized:.1f}%。财报是高波动事件，建议在财报前卖出 1/3 持仓锁定利润，剩余仓位持续持有，避免因财报不及预期导致浮盈大幅回吐。"
        else:
            s2_title = "设置止损位，控制下行风险"
            s2_desc  = f"您持有 {qty:.0f} 股 {name}，成本约 ${cost:.2f}。建议在财报前设置止损位（如跌破成本价 8% 触发），一旦财报后价格大幅下跌，及时止损，避免损失扩大。"
        s2_risk = "中"
    else:
        s2_title = "小仓试探，财报后再决策"
        s2_desc  = f"您当前未持有 {name}。若看好该公司基本面，可在财报发布前建立小仓位（不超过计划仓位的 1/3），财报后根据市场反应决定是否继续加仓，控制单次事件风险敞口。"
        s2_risk  = "中"

    # 策略3：期权/对冲（教育性）
    s3_title = "通过期权工具对冲财报波动"
    s3_desc  = (f"财报前隐含波动率（IV）通常升高，{name} 历史财报平均波动约 {abs(avg_ret5):.1f}%。"
                f"若持仓较重，可考虑购买保护性认沽期权（Protective Put）对冲下行风险；"
                f"若判断财报后波动率将回落，也可考虑卖出跨式组合（Short Straddle）获取 IV 压缩收益。期权操作适合有一定经验的投资者。")
    s3_risk  = "高"

    strategies = [
        {"title": s1_title, "desc": s1_desc, "risk": s1_risk, "num": 1},
        {"title": s2_title, "desc": s2_desc, "risk": s2_risk, "num": 2},
        {"title": s3_title, "desc": s3_desc, "risk": s3_risk, "num": 3},
    ]
    return strategies

def generate_html(symbol, name, events, strategies, position, output_path, klines=None,
                  next_earnings=None, days_until=None, last_earnings=None, days_since=None,
                  next_earnings_estimated=False, web_source_used=False):
    if not events:
        print(f"[analyzer] 无有效财报事件数据，退出")
        sys.exit(1)

    up_count  = sum(1 for e in events if e["up"])
    dn_count  = len(events) - up_count
    up_prob   = round(up_count / len(events) * 100)
    avg_ret5  = round(sum(e["ret5"] for e in events) / len(events), 1)
    valid10   = [e["ret10"] for e in events if e["ret10"] is not None]
    avg_ret10 = round(sum(valid10) / len(valid10), 1) if valid10 else None
    date_str  = datetime.today().strftime("%Y-%m-%d")
    mkt       = "HK" if symbol.endswith(".HK") else "US"
    currency  = "HK$" if mkt == "HK" else "$"

    # Chart data
    bar_labels  = json.dumps([e["date"] for e in events])
    bar_values  = json.dumps([e["ret5"] for e in events])
    bar_colors  = json.dumps(["#3fb950" if e["up"] else "#f85149" for e in events])

    # Line chart: last 4 events, price indexed to 100 at earnings day
    klines_map = {k["time"][:10]: float(k["close"]) for k in klines} if klines else {}
    recent4 = events[-4:]
    line_colors_list = ["#3fb950","#f85149","#79c0ff","#ffa657"]
    x_offsets = list(range(-5, 11))
    x_labels_py = [str(o) if o != 0 else "发布日" for o in x_offsets]
    line_datasets_list = []
    for i, ev in enumerate(recent4):
        color = line_colors_list[i % len(line_colors_list)]
        base_price = ev["p_day"]
        prices = []
        for offset in x_offsets:
            p = price_on_or_after(klines_map, ev["date"], offset) if klines_map else None
            prices.append(round(p / base_price * 100, 2) if p and base_price else None)
        line_datasets_list.append({
            "label": f"{ev['date']} ({ev['ret5']:+.1f}%)",
            "data": prices,
            "borderColor": color,
            "backgroundColor": "transparent",
            "borderWidth": 2,
            "pointRadius": 3,
            "tension": 0.3,
            "spanGaps": True,
        })
    line_labels = json.dumps(x_labels_py)
    line_datasets = json.dumps(line_datasets_list)

    # Donut
    donut_data = json.dumps([dn_count, up_count])

    # Distribution buckets
    buckets = {"<-10%":0, "-10~-5%":0, "-5~0%":0, "0~5%":0, "5~10%":0, ">10%":0}
    for e in events:
        r = e["ret5"]
        if r < -10:   buckets["<-10%"] += 1
        elif r < -5:  buckets["-10~-5%"] += 1
        elif r < 0:   buckets["-5~0%"] += 1
        elif r < 5:   buckets["0~5%"] += 1
        elif r < 10:  buckets["5~10%"] += 1
        else:         buckets[">10%"] += 1
    dist_labels = json.dumps(list(buckets.keys()))
    dist_values = json.dumps(list(buckets.values()))
    dist_colors = json.dumps(["#f85149","#f85149","#f85149","#3fb950","#3fb950","#3fb950"])

    # Table rows
    table_rows = ""
    for e in events:
        ret5_cls  = "green" if e["up"] else "red"
        ret10_cls = "green" if (e["ret10"] or 0) > 0 else "red"
        ret10_str = f"{e['ret10']:+.1f}%" if e["ret10"] is not None else "—"
        result    = "上涨" if e["up"] else "下跌"
        res_cls   = ret5_cls
        table_rows += f"""<tr>
          <td>{e['date']}</td>
          <td>{currency}{e['p_pre5']:.2f}</td>
          <td>{currency}{e['p_day']:.2f}</td>
          <td>{currency}{e['p_post5']:.2f}</td>
          <td>{f"{currency}{e['p_post10']:.2f}" if e['p_post10'] else '—'}</td>
          <td class="{ret5_cls}">{e['ret5']:+.1f}%</td>
          <td class="{ret10_cls}">{ret10_str}</td>
          <td class="{res_cls} bold">{result}</td>
        </tr>"""

    # Strategy cards
    risk_colors = {"低": "#3fb950", "中": "#d29922", "高": "#f85149"}
    strat_html = ""
    for s in strategies:
        rc = risk_colors.get(s["risk"], "#8b949e")
        strat_html += f"""
        <div class="strategy-card">
          <div class="strat-header">
            <span class="strat-num">情景 {s['num']}</span>
            <span class="strat-title">{s['title']}</span>
            <span class="risk-badge" style="color:{rc};border-color:{rc}">风险：{s['risk']}</span>
          </div>
          <div class="strat-body">{s['desc']}</div>
        </div>"""

    # Position info
    pos_html = ""
    if position:
        qty  = float(position.get("quantity", 0))
        cost = float(position.get("cost_price", 0))
        curr = float(position.get("current_price", cost))
        pnl  = (curr - cost) * qty
        pnl_pct = (curr/cost - 1)*100 if cost > 0 else 0
        pnl_cls = "green" if pnl >= 0 else "red"
        pos_html = f"""
        <div class="pos-bar">
          <span class="pos-label">📦 您当前持有</span>
          <span class="pos-item">{qty:.0f} 股</span>
          <span class="pos-item">成本 {currency}{cost:.2f}</span>
          <span class="pos-item">现价 {currency}{curr:.2f}</span>
          <span class="pos-item {pnl_cls}">浮盈亏 {'+' if pnl>=0 else ''}{pnl:.0f} ({pnl_pct:+.1f}%)</span>
        </div>"""
    else:
        pos_html = '<div class="pos-bar"><span class="pos-label">📦 您当前未持有该股票</span></div>'

    # KPI color
    kpi5_cls  = "kpi-green" if avg_ret5  > 0 else "kpi-red"
    kpi10_cls = "kpi-green" if (avg_ret10 or 0) > 0 else "kpi-red"

    # 财报日期 banner — 同时显示最近已发布 + 下次预计
    banner_parts = []
    if last_earnings and days_since is not None:
        banner_parts.append(f'<span class="eb-item past">📅 最近财报：<strong>{last_earnings}</strong> · 已发布 {days_since} 天前</span>')
    if next_earnings and days_until is not None:
        if days_until == 0:
            banner_parts.append(f'<span class="eb-item upcoming">🔴 今日发布财报：<strong>{next_earnings}</strong> · 正在发布</span>')
        else:
            banner_parts.append(f'<span class="eb-item upcoming">⏳ 下次财报：<strong>{next_earnings}</strong> · 还有 <strong>{days_until} 天</strong></span>')
    else:
        banner_parts.append(f'<span class="eb-item no-date">📭 下次财报：暂无已公告日期</span>')
    if banner_parts:
        earnings_banner = f'<div class="earnings-banner">{"".join(banner_parts)}</div>'
    else:
        earnings_banner = ""

    # 数据来源提示（仅当回落到 yfinance 时显示）
    if web_source_used:
        web_notice = (
            '<div class="web-notice">'
            '⚠️ 由于该标的为小众/非主流票，Longbridge 暂无完整历史财报日期记录，'
            '以下分析数据来源于 <strong>Yahoo Finance (yfinance)</strong>，'
            '可能存在日期偏差，请以官方公告为准。'
            '</div>'
        )
    else:
        web_notice = ""

    # 样本量不足提示（有效财报事件 < 5 次时显示）
    n_events = len(events)
    if n_events < 5:
        # 提取年份范围用于描述
        years = sorted(set(e['date'][:4] for e in events))
        if len(years) == 1:
            year_range = years[0] + " 年"
        else:
            year_range = years[0] + "–" + years[-1] + " 年"
        sample_notice = (
            f'<div class="sample-notice">'
            f'<span class="sn-icon">⚠️</span>'
            f'<span><strong>样本量提示：</strong>{symbol.split(".")[0]} 为小众票，'
            f'Longbridge 仅检索到 <strong>{n_events} 次</strong>历史财报记录（{year_range}），'
            f'样本量偏少，统计结论参考价值有限，请结合更多信息审慎决策。'
            f'历史数据不构成投资建议。</span>'
            f'</div>'
        )
    else:
        sample_notice = ""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} · 财报效应分析</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,'PingFang SC',sans-serif;background:#f0f2f6;color:#1a1d23;font-size:13px}}
.topbar{{background:#fff;padding:14px 28px;display:flex;align-items:center;justify-content:space-between;border-bottom:3px solid #e5e7eb;box-shadow:0 1px 4px rgba(0,0,0,0.06)}}
.topbar-left{{display:flex;align-items:center;gap:14px}}
.logo{{width:36px;height:36px;background:#1a56db;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900;font-size:14px}}
.stock-title{{font-size:17px;font-weight:800;color:#111827}}
.stock-sub{{font-size:11px;color:#9ca3af;margin-top:2px}}
.topbar-right{{font-size:12px;color:#fff;font-weight:800;background:{'#10b981' if up_prob>=50 else '#ef4444'};padding:5px 14px;border-radius:20px}}
.container{{max-width:1140px;margin:0 auto;padding:22px 28px}}

/* Hero forecast — 三色块 */
.hero{{margin-bottom:18px}}
.hero-title{{font-size:11px;font-weight:700;color:#6b7280;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;padding-left:2px}}
.hero-metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:10px}}
.hero-metric{{border-radius:14px;padding:24px 28px}}
.hero-metric.m1{{background:#00C4A7}}
.hero-metric.m2{{background:#FFD600}}
.hero-metric.m3{{background:#FF6B1A}}
.hero-m-label{{font-size:11px;font-weight:600;color:rgba(0,0,0,0.55);margin-bottom:12px;letter-spacing:0.3px}}
.hero-m-value{{font-size:42px;font-weight:900;color:#111;line-height:1;margin-bottom:8px;letter-spacing:-1.5px}}
.hero-m-sub{{font-size:11px;color:rgba(0,0,0,0.5);font-weight:500}}
.hero-warning{{background:#fff8ed;border:1px solid #fbbf24;border-left:3px solid #f59e0b;border-radius:0 10px 10px 0;padding:11px 16px;font-size:11px;color:#92400e;line-height:1.8}}
.hero-warning strong{{color:#d97706}}

/* KPI */
.kpi-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}}
.kpi-card{{background:#fff;border-radius:12px;padding:18px 22px;border:1px solid #e8eaed;box-shadow:0 1px 4px rgba(0,0,0,0.05)}}
.kpi-label{{font-size:11px;color:#6b7280;margin-bottom:8px}}
.kpi-value{{font-size:28px;font-weight:800;margin-bottom:4px;letter-spacing:-0.5px}}
.kpi-red{{color:#ef4444}}.kpi-green{{color:#10b981}}.kpi-blue{{color:#3b82f6}}.kpi-gray{{color:#374151}}
.kpi-sub{{font-size:11px;color:#9ca3af}}

/* Charts */
.charts-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}}
.charts-row3{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}}
.chart-card{{background:#fff;border-radius:12px;padding:18px 22px;border:1px solid #e8eaed;box-shadow:0 1px 4px rgba(0,0,0,0.05)}}
.chart-card.wide{{grid-column:1/-1}}
.chart-title{{font-size:12px;font-weight:700;margin-bottom:3px;color:#1f2937}}
.chart-sub{{font-size:10px;color:#9ca3af;margin-bottom:12px}}
.chart-wrap{{position:relative;height:180px}}
.chart-wrap.tall{{height:250px}}
.section-title{{font-size:13px;font-weight:700;margin-bottom:10px;color:#111827;border-left:3px solid #1a56db;padding-left:10px}}

/* Table */
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{background:#f8fafc;color:#6b7280;padding:9px 12px;text-align:left;border-bottom:2px solid #e8eaed;font-weight:600;font-size:11px;letter-spacing:0.3px}}
td{{padding:9px 12px;border-bottom:1px solid #f1f3f6}}
tr:hover td{{background:#fafbff}}
.green{{color:#10b981;font-weight:700}}.red{{color:#ef4444;font-weight:700}}.bold{{font-weight:700}}

/* Position bar */
.pos-bar{{background:#fff;border-radius:12px;padding:14px 22px;border:1px solid #e8eaed;box-shadow:0 1px 4px rgba(0,0,0,0.05);margin-bottom:14px;display:flex;align-items:center;gap:24px;flex-wrap:wrap}}
.pos-label{{font-size:12px;color:#6b7280;font-weight:700}}
.pos-item{{font-size:12px;color:#374151}}

/* Situation cards */
.strategy-section{{background:#fff;border-radius:12px;padding:20px 24px;border:1px solid #e8eaed;box-shadow:0 1px 4px rgba(0,0,0,0.05);margin-bottom:14px}}
.strategy-card{{border:1px solid #e8eaed;border-radius:10px;padding:14px 18px;margin-bottom:10px;background:#fafbff}}
.strategy-card:last-child{{margin-bottom:0}}
.strat-header{{display:flex;align-items:center;gap:10px;margin-bottom:8px}}
.strat-num{{background:#1a56db;color:#fff;border-radius:5px;padding:2px 8px;font-size:11px;font-weight:800;flex-shrink:0}}
.strat-title{{font-size:13px;font-weight:700;flex:1;color:#111827}}
.risk-badge{{font-size:10px;padding:2px 10px;border-radius:10px;border:1px solid;flex-shrink:0;font-weight:600}}
.strat-body{{font-size:12px;color:#4b5563;line-height:1.8}}
.compliance{{background:#fff5f5;border:1px solid #fecaca;border-radius:10px;padding:12px 16px;font-size:11px;color:#7f1d1d;line-height:1.8;margin-top:12px}}

/* Earnings banner */
.earnings-banner{{display:flex;align-items:center;gap:24px;padding:10px 28px;background:#f8fafc;border-bottom:1px solid #e8eaed;font-size:12px;flex-wrap:wrap}}
.eb-item{{display:flex;align-items:center;gap:6px;color:#374151}}
.eb-item strong{{font-weight:700;color:#111827}}
.eb-item.past{{color:#6b7280}}
.eb-item.past strong{{color:#374151}}
.eb-item.upcoming{{color:#1d4ed8}}
.eb-item.upcoming strong{{color:#1d4ed8}}
.eb-item.no-date{{color:#9ca3af}}
.eb-divider{{width:1px;height:14px;background:#e5e7eb}}

/* Web source notice */
.web-notice{{display:flex;align-items:center;gap:8px;padding:8px 28px;background:#fffbeb;border-bottom:1px solid #fde68a;font-size:11.5px;color:#92400e;line-height:1.6}}
.web-notice strong{{color:#78350f}}

/* Sample size notice */
.sample-notice{{display:flex;align-items:flex-start;gap:10px;padding:10px 28px;background:#fef3c7;border-bottom:2px solid #f59e0b;font-size:12px;color:#78350f;line-height:1.7}}
.sample-notice .sn-icon{{font-size:15px;flex-shrink:0;margin-top:1px}}
.sample-notice strong{{color:#92400e;font-weight:700}}

/* Footer */
.footer{{text-align:center;font-size:10px;color:#9ca3af;padding:18px 0 28px;border-top:1px solid #e8eaed;margin-top:10px}}
.table-wrap{{overflow-x:auto}}
</style>
</head>
<body>

<div class="topbar">
  <div class="topbar-left">
    <div class="logo">{name[0]}</div>
    <div>
      <div class="stock-title">{name} · 财报效应分析</div>
      <div class="stock-sub">{symbol} &nbsp;·&nbsp; 基于 SEC EDGAR &amp; Longbridge CLI 历史财报数据</div>
    </div>
  </div>
  <div class="topbar-right">📈 历史上涨概率 {up_prob}%</div>
</div>

{earnings_banner}
{web_notice}
{sample_notice}

<div class="container">

  <!-- Hero Forecast -->
  <div class="hero">
    <div class="hero-title">📊 下次财报预测（基于历史规律）</div>
    <div class="hero-metrics">
      <div class="hero-metric m1">
        <div class="hero-m-label">历史上涨概率</div>
        <div class="hero-m-value">{up_prob}%</div>
        <div class="hero-m-sub">{len(events)}次财报中 {up_count}次上涨</div>
      </div>
      <div class="hero-metric m2">
        <div class="hero-m-label">预期幅度（后5日）</div>
        <div class="hero-m-value">{avg_ret5:+.1f}%</div>
        <div class="hero-m-sub">历史平均，极端情况可达 {min(e['ret5'] for e in events):.1f}%</div>
      </div>
      <div class="hero-metric m3">
        <div class="hero-m-label">预期幅度（后10日）</div>
        <div class="hero-m-value">{f'{avg_ret10:+.1f}%' if avg_ret10 is not None else 'N/A'}</div>
        <div class="hero-m-sub">10日效应比5日{"更显著" if abs(avg_ret10 or 0)>abs(avg_ret5) else "收窄"}</div>
      </div>
    </div>
    <div class="hero-warning">
      <strong>⚠️ 操作提示：</strong>{name}历史财报效应{"偏空" if avg_ret5<0 else "偏多"}。若持有该股，建议在财报发布前5日关注价格异动，考虑适当控制仓位或设置止损。历史规律不代表未来，仅供参考。
    </div>
  </div>

  <!-- KPI -->
  <div class="kpi-row">
    <div class="kpi-card">
      <div class="kpi-label">前5→后5日 平均涨跌幅</div>
      <div class="kpi-value {kpi5_cls}">{avg_ret5:+.1f}%</div>
      <div class="kpi-sub">财报发布后普遍{"上涨" if avg_ret5>0 else "承压"}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">前5→后10日 平均涨跌幅</div>
      <div class="kpi-value {kpi10_cls}">{f'{avg_ret10:+.1f}%' if avg_ret10 is not None else 'N/A'}</div>
      <div class="kpi-sub">10日效应{"扩大" if (avg_ret10 or 0) < avg_ret5 else "收窄"}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">历史上涨概率</div>
      <div class="kpi-value kpi-{'blue' if up_prob>=50 else 'red'}">{up_prob}%</div>
      <div class="kpi-sub">{up_count}次中{up_count}次上涨</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">分析样本</div>
      <div class="kpi-value kpi-gray">{len(events)}</div>
      <div class="kpi-sub">次财报文件（历史）</div>
    </div>
  </div>

  <!-- Charts row 1: bar + line -->
  <div class="charts-grid">
    <div class="chart-card">
      <div class="chart-title">每次财报前后5日涨跌幅</div>
      <div class="chart-sub">绿色=上涨 红色=下跌</div>
      <div class="chart-wrap tall"><canvas id="barChart"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">财报前后价格走势对比</div>
      <div class="chart-sub">最近4次财报，前5日到后10日价格指数（发布日=100）</div>
      <div class="chart-wrap tall"><canvas id="lineChart"></canvas></div>
    </div>
  </div>

  <!-- Charts row 2: 3 charts -->
  <div class="charts-row3">
    <div class="chart-card">
      <div class="chart-title">涨跌分布</div>
      <div class="chart-sub">前5→后5日区间分布</div>
      <div class="chart-wrap"><canvas id="distChart"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">5日 vs 10日效应</div>
      <div class="chart-sub">短期 vs 中期财报影响</div>
      <div class="chart-wrap"><canvas id="compareChart"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">上涨 vs 下跌次数</div>
      <div class="chart-sub">{len(events)}次财报胜负统计</div>
      <div style="display:flex;justify-content:center;align-items:center;height:180px;">
        <canvas id="donutChart" style="max-width:180px;max-height:180px;"></canvas>
      </div>
      <div id="donutLegend" style="display:flex;justify-content:center;gap:20px;margin-top:10px;font-size:11px;color:#374151"></div>
    </div>
  </div>

  <!-- Table -->
  <div class="chart-card" style="margin-bottom:16px">
    <div class="section-title">财报事件明细</div>
    <div class="chart-sub" style="margin-bottom:10px">各次财报发布前后价格变化（按时间排序）</div>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th>日期</th><th>前5日价</th><th>发布日价</th><th>后5日价</th><th>后10日价</th>
          <th>前5→后5</th><th>前5→后10</th><th>结果</th>
        </tr></thead>
        <tbody>{table_rows}</tbody>
      </table>
    </div>
  </div>

  <!-- Position -->
  {pos_html}

  <!-- Strategies -->
  <div class="strategy-section">
    <div class="section-title" style="margin-bottom:12px">📋 持仓情景参考（基于历史规律）</div>
    {strat_html}
    <div class="compliance">
      <strong>⚠️ 合规风险提示：</strong>以上情景参考仅基于历史财报统计规律与用户持仓数据自动生成，<strong>不构成任何投资建议或邀约</strong>。投资者应结合自身风险承受能力、投资目标及市场实际情况独立决策。历史表现不代表未来收益，股票投资存在本金损失风险，请谨慎决策。如需专业意见，请咨询持牌投资顾问。
    </div>
  </div>

</div>

<div class="footer">
  数据来源：Longbridge CLI &nbsp;·&nbsp; K线数据 &nbsp;·&nbsp; 截至 {date_str} &nbsp;&nbsp;&nbsp;&nbsp; 仅供参考，不构成投资建议 &nbsp;·&nbsp; {name.upper()} EARNINGS EFFECT ANALYSIS
</div>

<script>
const barLabels = {bar_labels};
const barValues = {bar_values};
const barColors = {bar_colors};
const distLabels = {dist_labels};
const distValues = {dist_values};
const distColors = {dist_colors};
const donutData  = {donut_data};
const avg5 = {avg_ret5};
const avg10 = {avg_ret10 if avg_ret10 is not None else 0};
const upProb = {up_prob};
const lineLabels = {line_labels};
const lineDatasets = {line_datasets};

const chartDefaults = {{
  plugins: {{ legend: {{ display: false }}, tooltip: {{ mode: 'index' }} }},
  scales: {{ x: {{ grid: {{ display:false }}, ticks: {{ maxRotation:45, font:{{ size:9 }} }} }},
             y: {{ grid: {{ color:'#f3f4f6' }}, ticks: {{ font:{{ size:10 }} }} }} }}
}};

// Bar chart
new Chart(document.getElementById('barChart'), {{
  type: 'bar',
  data: {{ labels: barLabels, datasets: [{{
    data: barValues, backgroundColor: barColors, borderRadius: 3,
  }}] }},
  options: {{ ...chartDefaults, plugins: {{ ...chartDefaults.plugins,
    annotation: {{ annotations: {{ line1: {{ type:'line', yMin:0, yMax:0, borderColor:'#9ca3af', borderWidth:1 }} }} }}
  }} }}
}});

// Line chart
new Chart(document.getElementById('lineChart'), {{
  type: 'line',
  data: {{
    labels: lineLabels,
    datasets: lineDatasets.map(ds => ({{
      ...ds,
      pointHoverRadius: 5,
    }}))
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: true, position: 'bottom', labels: {{ font: {{ size: 10 }}, padding: 8, boxWidth: 12 }} }},
      tooltip: {{ mode: 'index', intersect: false }},
      annotation: {{ annotations: {{ vline: {{ type:'line', xMin:'发布日', xMax:'发布日', borderColor:'#9ca3af', borderWidth:1, borderDash:[4,3] }} }} }}
    }},
    scales: {{
      x: {{ grid: {{ display:false }}, ticks: {{ font:{{ size:9 }}, maxRotation:0 }} }},
      y: {{ grid: {{ color:'#f3f4f6' }}, ticks: {{ font:{{ size:10 }},
        callback: v => v + '' }} }}
    }}
  }}
}});

// Distribution
new Chart(document.getElementById('distChart'), {{
  type: 'bar',
  data: {{ labels: distLabels, datasets: [{{ data: distValues, backgroundColor: distColors, borderRadius:3 }}] }},
  options: {{ ...chartDefaults, scales: {{ x: {{ grid:{{display:false}}, ticks:{{font:{{size:9}}}} }}, y: {{ grid:{{color:'#f3f4f6'}}, ticks:{{stepSize:1, font:{{size:10}}}} }} }} }}
}});

// Compare 5d vs 10d
new Chart(document.getElementById('compareChart'), {{
  type: 'bar',
  data: {{
    labels: ['平均涨幅', '上涨概率'],
    datasets: [
      {{ label: '前后5日', data: [avg5, upProb-50], backgroundColor: avg5>0?'rgba(16,185,129,0.7)':'rgba(239,68,68,0.7)', borderRadius:3 }},
      {{ label: '前后10日', data: [avg10, (upProb-50)*0.9], backgroundColor: avg10>0?'rgba(59,130,246,0.7)':'rgba(251,146,60,0.7)', borderRadius:3 }},
    ]
  }},
  options: {{ ...chartDefaults, plugins: {{ legend: {{ display:true, labels:{{ font:{{size:10}} }} }} }},
    scales: {{ x:{{grid:{{display:false}}}}, y:{{grid:{{color:'#f3f4f6'}}}} }} }}
}});

// Donut
new Chart(document.getElementById('donutChart'), {{
  type: 'doughnut',
  data: {{ labels:['下跌','上涨'], datasets:[{{ data: donutData,
    backgroundColor:['#ef4444','#10b981'], borderWidth:0, hoverOffset:4 }}] }},
  options: {{
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{ callbacks: {{ label: (ctx) => ctx.label + ': ' + ctx.raw + '次' }} }}
    }},
    cutout: '65%'
  }}
}});
// 自定义居中图例
(function(){{
  const colors = ['#ef4444','#10b981'];
  const labels = ['下跌','上涨'];
  const counts = donutData;
  const el = document.getElementById('donutLegend');
  labels.forEach((l,i) => {{
    el.innerHTML += `<span style="display:flex;align-items:center;gap:5px;">
      <span style="width:12px;height:12px;border-radius:2px;background:${{colors[i]}};flex-shrink:0"></span>
      ${{l}} (${{counts[i]}}次)</span>`;
  }});
}})();
</script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol",  required=True)
    parser.add_argument("--dates",   default=None, help="逗号分隔的财报日期，如 2024-01-24,2024-04-23")
    parser.add_argument("--output",  default="/tmp/earnings_analysis.html")
    args = parser.parse_args()

    symbol = args.symbol.upper()
    name   = STOCK_NAMES.get(symbol, symbol)

    web_source_used = False
    if args.dates:
        earnings_dates = [d.strip() for d in args.dates.split(",")]
    elif symbol in EARNINGS_DATES:
        earnings_dates = EARNINGS_DATES[symbol]
    else:
        print(f"[analyzer] {symbol} 非内置股票，尝试从 Longbridge 拉取历史财报日期...")
        earnings_dates = fetch_past_earnings_from_longbridge(symbol)
        if not earnings_dates:
            print(f"[analyzer] Longbridge 无历史财报数据，尝试从网页获取（yfinance）...")
            earnings_dates = fetch_earnings_from_web(symbol)
            if earnings_dates:
                web_source_used = True
                print(f"[analyzer] ✅ yfinance 获取到 {len(earnings_dates)} 个历史财报日期：{', '.join(earnings_dates)}")
        if not earnings_dates:
            print(f"[analyzer] ❌ 无法获取 {symbol} 财报日期，请用 --dates 参数提供")
            sys.exit(1)
        print(f"[analyzer] 获取到 {len(earnings_dates)} 个历史财报日期：{', '.join(earnings_dates)}")

    print(f"[analyzer] 分析 {name} ({symbol})，共 {len(earnings_dates)} 次财报...")
    print("[analyzer] 获取 K 线数据...")
    klines = get_klines(symbol)
    if not klines:
        print("[analyzer] ❌ 无法获取 K 线数据")
        sys.exit(1)

    print("[analyzer] 计算财报效应...")
    events = analyze(symbol, earnings_dates, klines)
    print(f"[analyzer] 有效财报事件：{len(events)} 次")

    print("[analyzer] 读取持仓...")
    positions = get_positions()
    position  = get_position_for(symbol, positions)
    if position:
        print(f"[analyzer] 发现持仓：{position.get('quantity')} 股")
    else:
        print("[analyzer] 未持有该股票")

    print("[analyzer] 生成策略建议...")
    strategies = build_strategies(symbol, events, position, name)

    # 计算下次/最近财报日期
    today_date = datetime.today().date()
    today_str  = today_date.strftime("%Y-%m-%d")
    next_earnings, days_until, last_earnings, days_since = None, None, None, None

    # 最近已发布财报
    for d in sorted(earnings_dates, reverse=True):
        if d <= today_str:
            last_earnings = d
            days_since = (today_date - datetime.strptime(d, "%Y-%m-%d").date()).days
            break

    # 下次财报：①内置未来日期 → ②Longbridge已公告 → ③暂无公告
    for d in sorted(earnings_dates):
        if d >= today_str:
            next_earnings = d
            days_until = (datetime.strptime(d, "%Y-%m-%d").date() - today_date).days
            break

    next_earnings_estimated = False
    if not next_earnings:
        print("[analyzer] 查询 Longbridge 是否有已公告的下次财报日期...")
        lb_next = fetch_next_earnings_from_longbridge(symbol)
        if lb_next:
            next_earnings = lb_next
            days_until = (datetime.strptime(lb_next, "%Y-%m-%d").date() - today_date).days
            print(f"[analyzer] 找到已公告财报日期：{lb_next}")
        else:
            print("[analyzer] 暂无已公告的下次财报日期")

    print("[analyzer] 生成 HTML 报告...")
    generate_html(symbol, name, events, strategies, position, args.output, klines=klines,
                  next_earnings=next_earnings, days_until=days_until,
                  last_earnings=last_earnings, days_since=days_since,
                  next_earnings_estimated=next_earnings_estimated,
                  web_source_used=web_source_used)
    print(f"[analyzer] ✅ 完成：{args.output}")

if __name__ == "__main__":
    main()
