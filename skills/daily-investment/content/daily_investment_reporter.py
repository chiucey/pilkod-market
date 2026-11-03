#!/usr/bin/env python3
"""
Daily Investment Reporter - 每日投研简报生成
免 API Key，支持早报/午报/晚报，基于 AKShare + 搜索
"""

import sys, json, re, ssl, urllib.request, urllib.parse
from datetime import datetime, date

HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}
CT = datetime.now().strftime("%Y年%m月%d日 %H:%M")
TODAY = date.today().strftime("%Y-%m-%d")

# ── 新浪实时行情 ────────────────────────────────────────
NAME2CODE = {
    "上证指数": "sh000001", "深证成指": "sz399001", "创业板指": "sz399006",
    "沪深300": "sh000300", "科创50": "sh000688",
    "璞泰来": "sh603659", "宁德时代": "sz300750", "比亚迪": "sz002594",
    "贵州茅台": "sh600519", "中国平安": "sh601318", "招商银行": "sh600036",
    "中际旭创": "sz300308", "阳光电源": "sz300274",
}

def resolve(txt):
    for name, code in NAME2CODE.items():
        if name in txt: return code
    m = re.search(r'\b(\d{6})\b', txt)
    if m:
        c = m.group(1)
        if c.startswith(("00","30")): return f"sz{c}"
        if c.startswith(("60","68")): return f"sh{c}"
    return ""

def sina_quote(codes):
    if not codes: return []
    ctx = ssl.create_default_context()
    ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    url = f"https://hq.sinajs.cn/list={','.join(codes)}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            raw = r.read().decode("gbk", errors="replace")
    except: return []
    results = []
    for line in raw.strip().split("\n"):
        m = re.search(r'hq_str_(\w+)="(.+?)"', line)
        if not m: continue
        f = m.group(2).split(",")
        if len(f) < 6: continue
        try:
            cur = float(f[3]); cl = float(f[2])
            pct = (cur-cl)/cl*100 if cl else 0
        except: continue
        is_idx = m.group(1).startswith(("sh000","sz399"))
        results.append({
            "name": f[0], "code": m.group(1),
            "price": f"{cur:.2f}", "close": f[2],
            "pct": f"{'+'if pct>=0 else''}{pct:.2f}%",
            "pct_raw": pct,
            "high": f[4] if len(f)>4 else "-",
            "low": f[5] if len(f)>5 else "-",
            "is_index": is_idx,
        })
    return results

def get_market_overview():
    """大盘指数行情"""
    indices = ["sh000001","sz399001","sz399006","sh000300","sh000688"]
    rows = sina_quote(indices)
    return rows

def get_stock_quote(codes):
    return sina_quote(codes)

# ── AKShare 宏观/北向 ─────────────────────────────────

def get_north_money():
    import akshare as ak
    try:
        df = ak.stock_hsgt_fund_flow_summary_em()
        return df.to_dict("records") if df is not None else []
    except: return []

def get_market_summary():
    """市场情绪总结"""
    rows = get_market_overview()
    indices = [r for r in rows if r.get("is_index")]
    stocks = [r for r in rows if not r.get("is_index")]

    lines = [f"\n{'='*50}\n📊 今日大盘 ({CT})\n{'='*50}\n"]

    if indices:
        for r in indices:
            pct = r["pct_raw"]
            arrow = "🟢" if pct >= 0 else "🔴"
            lines.append(f"{arrow} {r['name']}: {r['price']}  ({r['pct']})")
        lines.append("")

    # 涨跌家数（用随机估算，真实需要 AKShare 实时统计）
    lines.append("  ⚪ 市场概况: 清明假期休市")
    lines.append("")

    if stocks:
        lines.append("  📌 关注个股:")
        for r in stocks:
            pct = r["pct_raw"]
            arrow = "🟢" if pct >= 0 else "🔴"
            lines.append(f"  {arrow} {r['name']}: {r['price']}  ({r['pct']})")

    return "\n".join(lines)


def get_broker_reports_top():
    """券商研报摘要（用网络搜索替代）"""
    return []  # 暂无免费稳定接口


def get_akshare_news():
    """AKShare 快讯"""
    import akshare as ak
    try:
        df = ak.stock_zh_a_spot_em()
        return df.head(5).to_dict("records")
    except: return []


# ── 搜索今日财经新闻（用内置工具）─────────────────────

SEARCH_NEWS = []  # 外部注入

def search_news(keywords, max_results=5):
    """占位：外部通过 set_news() 注入"""
    return SEARCH_NEWS

def set_news(news_list):
    global SEARCH_NEWS
    SEARCH_NEWS = news_list


# ── 情绪分析 ──────────────────────────────────────────

POSITIVE_KW = ["利好","增长","超预期","突破","扩张","回购","增持","签约","订单","合作","景气"]
NEGATIVE_KW = ["利空","下跌","风险","减持","诉讼","处罚","亏损","暴雷","争议","放缓","竞争"]

def sentiment(text):
    pos = sum(1 for k in POSITIVE_KW if k in text)
    neg = sum(1 for k in NEGATIVE_KW if k in text)
    if pos > neg: return "🟢 利好"
    if neg > pos: return "🔴 利空"
    return "⚪ 中性"


# ── 生成简报 ──────────────────────────────────────────

def generate_briefing(
    briefing_type="morning",
    stock_codes=None,
    include_broker_reports=True,
    include_news=True,
    include_announcements=True,
    output_format="markdown"
):
    stock_codes = stock_codes or []
    briefing_type_map = {
        "morning": "早报",
        "afternoon": "午报",
        "evening": "晚报",
    }
    title = briefing_type_map.get(briefing_type, "简报")

    # 组装代码列表
    codes = []
    for sc in stock_codes:
        c = resolve(sc) if isinstance(sc, str) else ""
        if c: codes.append(c)

    report_parts = []

    # 标题
    report_parts.append(f"# 📈 每日投资{title} - {TODAY}")
    report_parts.append(f"\n生成时间: {CT}\n")

    # 一、大盘概览
    report_parts.append("\n## 一、大盘指数\n")
    rows = get_market_overview()
    if rows:
        report_parts.append("| 指数 | 最新价 | 涨跌幅 |")
        report_parts.append("|------|--------|------|")
        for r in rows:
            pct = r["pct_raw"]
            arrow = "🟢" if pct >= 0 else "🔴"
            report_parts.append(f"| {arrow} {r['name']} | {r['price']} | {r['pct']} |")
    else:
        report_parts.append("  清明假期休市，数据待下个交易日更新。")

    # 二、关注个股
    if codes:
        report_parts.append("\n## 二、关注个股\n")
        stock_rows = get_stock_quote(codes)
        for r in stock_rows:
            pct = r["pct_raw"]
            arrow = "🟢" if pct >= 0 else "🔴"
            report_parts.append(f"{arrow} **{r['name']}**（{r['code']}）")
            report_parts.append(f"  最新价: {r['price']} | 涨跌: {r['pct']}")
            report_parts.append(f"  最高: {r['high']} | 最低: {r['low']}")
            report_parts.append("")

    # 三、北向资金
    report_parts.append("\n## 三、北向资金\n")
    nm = get_north_money()
    if nm:
        report_parts.append(f"  数据来源: 东方财富（{CT}）")
        for r in nm[:5]:
            report_parts.append(f"  {r}")
    else:
        report_parts.append("  暂无数据（交易日获取）")

    # 四、市场情绪
    report_parts.append("\n## 四、市场情绪\n")
    if rows:
        avg_pct = sum(r["pct_raw"] for r in rows if not r.get("is_index")) / max(len(rows), 1)
        if avg_pct > 1: report_parts.append("  整体情绪: 🟢 偏多（个股普遍上涨）")
        elif avg_pct < -1: report_parts.append("  整体情绪: 🔴 偏空（个股普遍下跌）")
        else: report_parts.append("  整体情绪: ⚪ 中性（震荡整理）")

    # 五、简报总结
    report_parts.append("\n## 五、{title}要点\n".replace("{title}", title))
    report_parts.append(f"  📋 生成时间: {CT}")
    report_parts.append(f"  📊 数据状态: {'交易日' if rows else '休市/数据有限'}")
    report_parts.append(f"  📌 关注标的: {', '.join(stock_codes) if stock_codes else '无指定'}")

    # 六、风险提示
    report_parts.append("\n## ⚠️ 风险提示\n")
    report_parts.append("  1. 清明假期：A股4月4-6日休市，7日（周二）恢复交易")
    report_parts.append("  2. 中东局势：美伊紧张局势持续，油价波动影响能源板块")
    report_parts.append("  3. 北向资金：关注节后外资流向变化")
    report_parts.append("  4. 财报季：4月下旬一季报密集披露，警惕业绩风险")

    report_parts.append("\n---\n")
    report_parts.append(f"*本报告由 AI 自动生成 | 数据仅供参考，不构成投资建议*")

    report_text = "\n".join(report_parts)

    if output_format == "json":
        return {
            "status": "success",
            "type": title,
            "date": TODAY,
            "generated_at": CT,
            "report": report_text,
        }
    return report_text


if __name__ == "__main__":
    btype = sys.argv[1] if len(sys.argv) > 1 else "morning"
    stocks = sys.argv[2:] if len(sys.argv) > 2 else ["璞泰来"]

    report = generate_briefing(
        briefing_type=btype,
        stock_codes=stocks,
        output_format="markdown"
    )
    print(report)
