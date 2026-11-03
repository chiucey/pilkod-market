#!/usr/bin/env python3
"""
stock-portfolio-advisor 持仓顾问核心脚本
支持多数据源 + 用户持仓输入
用法:
  python3 portfolio_advisor.py --analyze                       # 使用配置文件或示例持仓
  python3 portfolio_advisor.py --analyze --json '[{"code":"sh600519","name":"示例股票A","shares":500,"cost":1800.0}]'
  python3 portfolio_advisor.py --test                        # 打印当前配置和数据源状态
"""

import sys, re, json, urllib.request, urllib.error
from datetime import datetime
from typing import List, Dict, Optional

# =============================================================================
# 【用户配置区】填写您的持仓信息（不填则使用演示数据）
# =============================================================================
# 方式1：直接填写在这里
HOLDINGS: List[dict] = []

# 方式2：填写配置文件路径（脚本会从此文件读取持仓）
# 推荐通过 agent 动态传递 JSON，详见下方 --json 参数
HOLDINGS_FILE = "/workspace/config/user_holdings.json"

# =============================================================================
# 数据源配置（可按需启用）
# =============================================================================
# 优先级从高到低，脚本会自动选择第一个可用的源
DATA_SOURCES = {
    # 腾讯财经（A股主要数据源，速度快）
    "tencent": {
        "enabled": True,
        "priority": 1,
        "url_template": "http://qt.gtimg.cn/q={codes}",
        "headers": {"Referer": "https://finance.qq.com", "User-Agent": "Mozilla/5.0"},
        "encoding": "gbk",
        "key_format": "prefix_code",  # 返回 key 如 "sh600519"
    },
    # 新浪财经（备用）
    "sina": {
        "enabled": False,
        "priority": 2,
        "url_template": "https://hq.sinajs.cn/list={codes}",
        "headers": {"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"},
        "encoding": "gbk",
        "key_format": "plain_code",  # 返回 key 如 "sh600519"
    },
    # 东方财富（备用）
    "eastmoney": {
        "enabled": False,
        "priority": 3,
        "url_template": "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&fields=f1,f2,f3,f4,f12,f14&secids={codes}",
        "headers": {"User-Agent": "Mozilla/5.0"},
        "encoding": "utf-8",
        "key_format": "secid",  # 格式: 1.600176
    },
}

# =============================================================================
# 行业分类表
# =============================================================================
INDUSTRY_MAP = {
    "600176": {"industry": "玻纤/建材", "style": "大盘", "risk": "中"},
    "000657": {"industry": "有色/钨", "style": "中大盘", "risk": "高"},
    "600309": {"industry": "化工/周期", "style": "大盘", "risk": "中"},
    "601899": {"industry": "有色/黄金铜", "style": "大盘", "risk": "中"},
    "300766": {"industry": "互联网/软件", "style": "中盘", "risk": "高"},
    "002156": {"industry": "半导体/封测", "style": "中盘", "risk": "高"},
    "300308": {"industry": "光模块/通信", "style": "大盘", "risk": "中"},
    "600519": {"industry": "消费白酒", "style": "大盘", "risk": "低"},
    "601012": {"industry": "新能源/光伏", "style": "大盘", "risk": "中"},
    "300750": {"industry": "新能源/电池", "style": "大盘", "risk": "中"},
    "688981": {"industry": "半导体/晶圆", "style": "大盘", "risk": "高"},
    "600036": {"industry": "银行/零售", "style": "大盘", "risk": "低"},
}

# =============================================================================
# 持仓数据加载
# =============================================================================

def load_holdings_from_args() -> Optional[List[dict]]:
    """从命令行 --json 参数获取持仓"""
    for i, arg in enumerate(sys.argv):
        if arg == "--json" and i + 1 < len(sys.argv):
            try:
                return json.loads(sys.argv[i + 1])
            except json.JSONDecodeError:
                print(f"❌ JSON格式错误: {sys.argv[i+1][:100]}")
                return None
    return None


def load_holdings_from_file(path: str) -> Optional[List[dict]]:
    """从配置文件读取持仓（JSON格式）"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list) and len(data) > 0:
            return data
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        print(f"⚠️ 配置文件格式错误: {path}")
    return None


def get_holdings() -> List[dict]:
    """
    获取持仓数据的优先级：
    1. 命令行 --json 参数
    2. 配置文件 ~/.holdings.json
    3. 内置 HOLDINGS 配置
    4. 演示数据（示例持仓）
    """
    # 优先：命令行JSON
    holdings = load_holdings_from_args()
    if holdings:
        print(f"✅ 从命令行JSON加载了 {len(holdings)} 只持仓")
        return holdings

    # 其次：配置文件
    import os
    for fpath in [HOLDINGS_FILE, os.path.expanduser("~/.holdings.json")]:
        holdings = load_holdings_from_file(fpath)
        if holdings:
            print(f"✅ 从配置文件加载了 {len(holdings)} 只持仓: {fpath}")
            return holdings

    # 再次：内置配置
    if HOLDINGS:
        print(f"✅ 从内置配置加载了 {len(HOLDINGS)} 只持仓")
        return HOLDINGS

    # 最后：演示数据
    demo = [
        {"code": "sh600519", "name": "示例股票A", "shares": 500, "cost": 1800.0},
        {"code": "sz000858", "name": "示例股票B", "shares": 300, "cost": 150.0},
        {"code": "sh601012", "name": "示例股票C", "shares": 200, "cost": 50.0},
        {"code": "sh600036", "name": "示例股票D", "shares": 300, "cost": 35.0},
    ]
    print(f"ℹ️  未检测到持仓配置，使用演示数据（{len(demo)}只）进行演示")
    return demo

# =============================================================================
# 多数据源行情获取
# =============================================================================

def try_fetch(url: str, headers: dict, encoding: str, timeout: int = 10) -> Optional[str]:
    """带异常处理的HTTP请求"""
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode(encoding, errors="replace")
    except urllib.error.HTTPError as e:
        return None
    except Exception:
        return None


def fetch_tencent(codes: List[str]) -> Dict[str, dict]:
    """腾讯财经API"""
    q = ",".join(codes)
    url = f"http://qt.gtimg.cn/q={q}"
    raw = try_fetch(url, DATA_SOURCES["tencent"]["headers"], "gbk")
    if not raw:
        return {}
    results = {}
    for line in raw.strip().split("\n"):
        m = re.match(r'v_(\w+)="([^"]+)"', line)
        if not m:
            continue
        f = m.group(2).split("~")
        if len(f) < 35:
            continue
        price, yclose = float(f[3]), float(f[4])
        chg = round(price - yclose, 2)
        pct = round(chg / yclose * 100, 2) if yclose else 0
        results[m.group(1)] = {
            "name": f[1], "code": f[2], "price": price, "yclose": yclose,
            "vol": float(f[6]) * 100, "high": float(f[33]), "low": float(f[34]),
            "date": f[30], "change": chg, "pct": pct,
            "source": "tencent",
        }
    return results


def fetch_sina(codes: List[str]) -> Dict[str, dict]:
    """新浪财经API（备用）"""
    q = ",".join(codes)
    url = f"https://hq.sinajs.cn/list={q}"
    raw = try_fetch(url, DATA_SOURCES["sina"]["headers"], "gbk")
    if not raw:
        return {}
    results = {}
    for line in raw.strip().split("\n"):
        m = re.match(r'var (\w+)=\"([^"]+)\"', line)
        if not m:
            continue
        f = m.group(2).split(",")
        if len(f) < 10:
            continue
        try:
            price = float(f[3])
            yclose = float(f[2])
            chg = round(price - yclose, 2)
            pct = round(chg / yclose * 100, 2) if yclose else 0
            results[m.group(1)] = {
                "name": f[0], "code": m.group(1)[2:], "price": price,
                "yclose": yclose, "change": chg, "pct": pct,
                "vol": 0, "high": 0, "low": 0, "date": "", "source": "sina",
            }
        except (ValueError, IndexError):
            continue
    return results


def fetch_all(codes: List[str]) -> Dict[str, dict]:
    """
    尝试所有已启用的数据源，返回第一个成功的结果
    """
    sources = [
        ("腾讯财经", fetch_tencent),
        ("新浪财经", fetch_sina),
    ]

    for name, fetch_fn in sources:
        results = fetch_fn(codes)
        if len(results) >= len(codes) * 0.8:  # 至少80%的股票有数据
            print(f"✅ 行情来源：{name}（获取{len(results)}/{len(codes)}只）")
            return results
        print(f"⚠️  {name}数据不足，仅获取{len(results)}只，继续尝试...")

    print("❌ 所有数据源均失败")
    return {}


# =============================================================================
# 持仓计算
# =============================================================================

def calc_holding(holding: dict, price_data: dict) -> dict:
    s, c = holding["shares"], holding["cost"]
    p = price_data["price"]
    yc = price_data["yclose"]
    mv = round(s * p, 2)
    cost_t = round(s * c, 2)
    profit = round(mv - cost_t, 2)
    profit_pct = round(profit / cost_t * 100, 2) if cost_t else 0
    day_profit = round(s * price_data["change"], 2)

    m = re.match(r'(?:sh|sz)?(\d+)', holding["code"])
    code_key = m.group(1) if m else holding["code"]
    info = INDUSTRY_MAP.get(code_key, {})
    return {
        "name": holding["name"], "code": holding["code"],
        "shares": s, "cost": c, "price": p, "yclose": yc,
        "high": price_data["high"], "low": price_data["low"],
        "vol": price_data["vol"],
        "market_value": mv, "cost_total": cost_t,
        "profit": profit, "profit_pct": profit_pct,
        "day_profit": day_profit, "pct": price_data["pct"],
        "industry": info.get("industry", "其他"),
        "style": info.get("style", "未知"),
        "risk": info.get("risk", "中"),
    }


def analyze_structure(holdings: List[dict]) -> dict:
    total_mv = sum(h["market_value"] for h in holdings)
    industry_mv, style_mv = {}, {}
    for h in holdings:
        industry_mv[h["industry"]] = industry_mv.get(h["industry"], 0) + h["market_value"]
        style_mv[h["style"]] = style_mv.get(h["style"], 0) + h["market_value"]
    weights = [h["market_value"] / total_mv * 100 for h in holdings] if total_mv else []
    return {
        "total_mv": total_mv,
        "industry_pct": {k: round(v / total_mv * 100, 1) for k, v in industry_mv.items()},
        "style_pct": {k: round(v / total_mv * 100, 1) for k, v in style_mv.items()},
        "max_weight": max(weights) if weights else 0,
        "top3_weight": sum(sorted(weights, reverse=True)[:3]) if weights else 0,
        "hhi": round(sum(w ** 2 for w in weights), 1) if weights else 0,
        "num_stocks": len(holdings),
    }


def diagnose_position(holdings: List[dict], cash: float, struct: dict) -> dict:
    total_mv = struct["total_mv"]
    total_assets = total_mv + cash
    pos_ratio = round(total_mv / total_assets * 100, 1) if total_assets else 0
    score = 75
    issues = []
    if pos_ratio > 80:
        score -= 20
        issues.append(("🔴 仓位过重", f"{pos_ratio}%，建议减至60%以下"))
    elif pos_ratio > 70:
        score -= 10
        issues.append(("⚠️ 仓位偏高", f"{pos_ratio}%，适当控制"))
    elif pos_ratio < 30:
        score += 5
        issues.append(("🟢 仓位偏轻", f"{pos_ratio}%，可适度加仓"))
    mw = struct["max_weight"]
    if mw > 40:
        score -= 15
        issues.append(("🔴 集中度过高", f"单只最高{mw:.1f}%，超过40%"))
    elif mw > 30:
        score -= 8
        issues.append(("⚠️ 集中度偏高", f"单只最高{mw:.1f}%"))
    for ind, pct in struct["industry_pct"].items():
        if pct > 50:
            score -= 10
            issues.append(("🔴 行业过于集中", f"{ind}占{pct}%，超过50%"))
    score = max(0, min(100, score))
    label = "🟢 优秀" if score >= 80 else "🟡 良好" if score >= 65 else "🟠 需改善" if score >= 45 else "🔴 较差"
    return {"score": score, "label": label, "position_ratio": pos_ratio, "issues": issues}


def risk_radar(holdings: List[dict], struct: dict, pos: dict) -> list:
    total_mv = struct["total_mv"]
    mw = struct["max_weight"]
    conc = 25 if mw < 20 else 20 if mw < 30 else 15 if mw < 40 else 8 if mw < 50 else 3
    amps = [(h["high"] - h["low"]) / h["yclose"] * 100 if h["yclose"] else 0 for h in holdings]
    avg_amp = sum(amps) / len(amps) if amps else 0
    vol = 25 if avg_amp < 2 else 20 if avg_amp < 4 else 15 if avg_amp < 6 else 8
    total_vol = sum(h["vol"] for h in holdings)
    liq = 25 if total_vol > 20000 else 20 if total_vol > 10000 else 15 if total_vol > 5000 else 8
    w_avg = sum(h["profit_pct"] * h["market_value"] / total_mv for h in holdings) if total_mv else 0
    trend = 25 if w_avg >= 10 else 20 if w_avg >= 5 else 15 if w_avg >= 0 else 8 if w_avg >= -5 else 3
    pos_ratio = pos["position_ratio"]
    pos_risk = 25 if pos_ratio < 50 else 20 if pos_ratio < 65 else 15 if pos_ratio < 80 else 8 if pos_ratio < 90 else 3
    max_ind_pct = max(struct["industry_pct"].values()) if struct["industry_pct"] else 0
    corr = 25 if max_ind_pct < 30 else 20 if max_ind_pct < 45 else 15 if max_ind_pct < 60 else 8
    return [
        ("集中度风险", conc, "单只仓位集中程度"),
        ("波动性风险", vol, "持仓整体振幅"),
        ("流动性风险", liq, "成交活跃度"),
        ("趋势风险", trend, "整体浮盈方向"),
        ("仓位风险", pos_risk, "持仓占比健康度"),
        ("相关性风险", corr, "行业集中程度"),
    ]


def adjust_suggestions(holdings: List[dict], struct: dict, cash: float) -> tuple:
    total_mv = struct["total_mv"]
    suggestions = []
    for h in holdings:
        pp, pct = h["profit_pct"], h["pct"]
        w = h["market_value"] / total_mv * 100 if total_mv else 0
        if pp <= -10:
            act, priority, note = "🔴止损", "最高", f"浮亏{pp:.1f}%，逻辑破坏"
        elif pp <= -5:
            act, priority, note = "⚠️关注", "高", f"浮亏{pp:.1f}%，接近成本"
        elif pp >= 40:
            act, priority, note = "⚠️分批止盈", "高", f"浮盈{pp:.1f}%，建议出一半"
        elif pp >= 25:
            act, priority, note = "✅持有", "中", f"浮盈{pp:.1f}%，继续持有"
        elif pp <= -3 and pct >= 1.5:
            act, priority, note = "🟢逢低可加", "中", f"今日反弹{abs(pp):.1f}%，摊低成本"
        elif pp >= 10 and pct >= 2:
            act, priority, note = "🟢趋势向上", "中", f"基本面强+技术向上"
        else:
            act, priority, note = "✅继续持有", "低", "趋势平稳"
        if w > 30:
            note += f"；⚠️仓位{w:.1f}%偏高，建议减至25%以下"
        suggestions.append({"name": h["name"], "code": h["code"], "profit": h["profit"],
                             "profit_pct": pp, "weight": w, "action": act, "priority": priority, "reason": note})
    pos_ratio = total_mv / (total_mv + cash) * 100 if (total_mv + cash) else 0
    if pos_ratio < 50:
        cash_advice = f"可用资金{cash/10000:.0f}万，建议配置2-3只优质标的"
    elif pos_ratio < 70:
        cash_advice = f"仓位适中，保留现金{cash/10000:.0f}万，等待机会"
    else:
        cash_advice = f"仓位偏重，优先减仓高风险持仓，不建议加仓"
    return suggestions, cash_advice


def gen_report(holdings: list, struct: dict, pos: dict, radar: list,
               suggestions: list, cash_advice: str, cash: float = 100000) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_mv = struct["total_mv"]
    total_cost = sum(h["cost_total"] for h in holdings)
    total_profit = sum(h["profit"] for h in holdings)
    total_pct = round(total_profit / total_cost * 100, 2) if total_cost else 0
    total_day = sum(h["day_profit"] for h in holdings)
    total_assets = total_mv + cash
    total_radar = sum(r[1] for r in radar)

    lines = [
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📊 【持仓顾问报告】",
        f"🕐 {ts}",
        f"",
        f"【一、持仓全景】",
        f"  总持仓市值：  {total_mv:>12,.2f} 元",
        f"  持仓总成本：  {total_cost:>12,.2f} 元",
        f"  浮动盈亏：   {total_profit:>+12,.2f} 元（{total_pct:+.2f}%）",
        f"  当日盈亏：   {total_day:>+12,.2f} 元",
        f"  现金储备：   {cash:>12,.2f} 元",
        f"  总资产：     {total_assets:>12,.2f} 元",
        f"  实时仓位：   {pos['position_ratio']:>12.1f}%",
        f"",
        f"【二、持仓结构分析】",
    ]
    for ind, pct in sorted(struct["industry_pct"].items(), key=lambda x: -x[1]):
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        lines.append(f"  {ind:<10}[{bar}] {pct:>5.1f}%")
    lines.append(f"\n  市值风格：")
    for style, pct in sorted(struct["style_pct"].items(), key=lambda x: -x[1]):
        style_tag = "（稳健）" if style == "大盘" else "（平衡）" if style == "中大盘" else "（进取）"
        lines.append(f"    {style:<8}{pct:>5.1f}%  {style_tag}")
    lines.extend([f"", f"  集中度：单只最大{struct['max_weight']:.1f}%  前三{struct['top3_weight']:.1f}%  HHI={struct['hhi']}"])
    lines.extend([f"", f"【三、仓位健康度】  {pos['label']}  ({pos['score']}/100)"])
    if pos["issues"]:
        for lbl, detail in pos["issues"]:
            lines.append(f"  {lbl}：{detail}")
    else:
        lines.append(f"  ✅ 仓位配置健康，继续保持")
    lines.extend([f"", f"【四、六维风险评估】  综合：{total_radar}/150"])
    for name, score, desc in radar:
        bar = "█" * score + "░" * (25 - score)
        icon = "✅" if score >= 20 else "⚠️" if score >= 10 else "🔴"
        lines.append(f"  {name:<10}[{bar}] {score:>2}/25  {icon} {desc}")
    lines.extend([f"", f"【五、调仓建议】", f"  💰 {cash_advice}", f""])
    prio_order = {"最高": 0, "高": 1, "中": 2, "低": 3}
    for s in sorted(suggestions, key=lambda x: (prio_order.get(x["priority"], 9), -x["weight"])):
        sp = "+" if s["profit"] >= 0 else ""
        lines.append(f"  {s['name']:<6}{s['action']:<10}{sp}{s['profit']:>8,.0f}（{s['profit_pct']:+.1f}%）"
                     f"仓位{s['weight']:.1f}%  {s['reason']}")
    lines.extend([f"", f"【六、风险提示】",
        f"  ⚠️ 持仓以周期股为主，注意宏观经济和油价波动影响",
        f"  ⚠️ 有色（钨/金铜）价格波动大，请设好止损纪律",
        f"  ⚠️ 行业集中度较高，建议适当分散到消费或医药",
        f"  ✅ 建议保留30%以上现金，增强抗风险能力",
        f"", f"【七、研究声明】  AI生成，仅供参考，不构成投资建议。",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"])
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        return

    if "--test" in args:
        print("=== 数据源状态 ===")
        for name, cfg in DATA_SOURCES.items():
            status = "✅ 已启用" if cfg["enabled"] else "❌ 已禁用"
            print(f"  {status}  优先级{cfg['priority']}  {name}")
        print(f"\n=== 持仓数据来源 ===")
        holdings = get_holdings()
        print(f"将分析 {len(holdings)} 只持仓：")
        for h in holdings:
            print(f"  {h['name']} {h['code']} {h['shares']}股 成本{h['cost']}")
        return

    holdings = get_holdings()
    if not holdings:
        print("❌ 未找到持仓数据，请通过以下方式提供：")
        print("  1. 命令行 --json 参数：python3 portfolio_advisor.py --analyze --json '[{\"code\":\"sh600519\",\"name\":\"示例股票A\",\"shares\":500,\"cost\":1800.0}]'")
        print("  2. 配置文件：~/.holdings.json")
        return

    codes = [h["code"] for h in holdings]
    prices = fetch_all(codes)
    if not prices:
        print("❌ 所有数据源均失败，请检查网络连接")
        return

    metrics = []
    for h in holdings:
        pd = prices.get(h["code"])
        if not pd:
            suffix = h["code"].lstrip("sh").lstrip("sz").lstrip("0")
            pd = next((v for k, v in prices.items() if k.endswith(suffix)), None)
        if pd:
            metrics.append(calc_holding(h, pd))

    if not metrics:
        print("❌ 未能匹配到任何持仓行情")
        return

    cash = 100000
    struct = analyze_structure(metrics)
    pos = diagnose_position(metrics, cash, struct)
    radar = risk_radar(metrics, struct, pos)
    suggestions, cash_advice = adjust_suggestions(metrics, struct, cash)
    print(gen_report(metrics, struct, pos, radar, suggestions, cash_advice, cash))


if __name__ == "__main__":
    main()
