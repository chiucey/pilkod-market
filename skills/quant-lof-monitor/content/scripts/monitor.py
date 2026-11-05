# -*- coding: utf-8 -*-
"""
Quantitative LOF Fund Monitor
Auto-fetch real-time data for quantitative LOF funds and calculate buy signals.
"""
import requests
import json
import sys
from datetime import datetime

# Default fund list - quant LOF funds to monitor
DEFAULT_FUNDS = [
    {"code": "166107", "name": "信澳量化多因子LOF-A", "strategy": "多因子量化", "benchmark": "中证500", "sharpe": 2.48, "max_dd": 48.9},
    {"code": "166108", "name": "信澳量化多因子LOF-C", "strategy": "多因子量化", "benchmark": "中证500", "sharpe": 2.48, "max_dd": 48.9},
    {"code": "166109", "name": "信澳量化先锋LOF-A", "strategy": "统计套利", "benchmark": "中证500", "sharpe": 2.20, "max_dd": 45.0},
    {"code": "161039", "name": "富国中证1000增强LOF-A", "strategy": "指数增强(1000)", "benchmark": "中证1000", "sharpe": 1.80, "max_dd": 35.0},
    {"code": "161035", "name": "富国中证500增强LOF", "strategy": "指数增强(500)", "benchmark": "中证500", "sharpe": 1.60, "max_dd": 32.0},
    {"code": "501059", "name": "西部利得国企红利增强LOF", "strategy": "红利增强", "benchmark": "中证国企红利", "sharpe": 1.40, "max_dd": 25.0},
    {"code": "160644", "name": "鹏华港美互联LOF", "strategy": "跨境量化", "benchmark": "恒生科技+纳指", "sharpe": 0.81, "max_dd": 33.9},
]

def fetch_jisilu_data():
    """Fetch LOF real-time data from Jisilu."""
    url = "https://www.jisilu.cn/data/lof/stock_lof_list/"
    params = {
        "___jsl": "LST___t=" + str(int(datetime.now().timestamp() * 1000)),
        "rp": "50", "page": "1"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        data = resp.json()
        result = {}
        for row in data.get("rows", []):
            cell = row.get("cell", {})
            code = cell.get("fund_id", "")
            result[code] = {
                "name": cell.get("fund_nm", ""),
                "price": float(cell.get("price", 0) or 0),
                "pre_close": float(cell.get("pre_close", 0) or 0),
                "nav": float(cell.get("fund_nav", 0) or 0),
                "nav_date": cell.get("nav_dt", ""),
                "nav_change": float(cell.get("nav_incr_rt", 0) or 0),
                "amount": float(cell.get("amount", 0) or 0),
                "volume": float(cell.get("volume", 0) or 0),
                "turnover": float(cell.get("turnover_rt", 0) or 0),
                "fund_size": float(cell.get("all_amount", 0) or 0),
                "stock_ratio": float(cell.get("stock_ratio", 0) or 0),
                "apply_status": cell.get("apply_status", ""),
                "discount": float(cell.get("nav_discount_rt", 0) or 0),
            }
        return result
    except Exception as e:
        print(f"Jisilu fetch error: {e}", file=sys.stderr)
        return {}

def calculate_premium(price, nav):
    """Calculate premium/discount rate."""
    if price > 0 and nav > 0:
        return round((price - nav) / nav * 100, 2)
    return None

def calculate_score(fund_info, premium, fund_meta):
    """Calculate composite buy score (0-100)."""
    score = 0
    details = []

    # 1. Premium/Discount (25 pts)
    if premium is not None:
        if premium < -3:
            score += 25; details.append(f"deep_discount:{premium}%")
        elif premium < -1:
            score += 20; details.append(f"discount:{premium}%")
        elif premium < 2:
            score += 15; details.append(f"fair:{premium}%")
        elif premium < 5:
            score += 5; details.append(f"expensive:{premium}%")
        else:
            details.append(f"prohibit:{premium}%")

    # 2. Fund size & liquidity (20 pts)
    size = fund_info.get("fund_size", 0)
    amount = fund_info.get("amount", 0)
    if size > 10 and amount > 1000:
        score += 20; details.append("size:large")
    elif size > 5 and amount > 500:
        score += 15; details.append("size:medium")
    elif size > 2 and amount > 300:
        score += 10; details.append("size:small_ok")
    elif size > 1:
        score += 5; details.append("size:mini")
    else:
        details.append("size:risk")

    # 3. Turnover/activity (10 pts)
    turnover = fund_info.get("turnover", 0)
    if turnover > 3:
        score += 10; details.append("active:high")
    elif turnover > 1:
        score += 7; details.append("active:normal")
    elif turnover > 0.3:
        score += 4; details.append("active:low")
    else:
        details.append("active:illiquid")

    # 4. Sharpe ratio from meta (20 pts)
    sharpe = fund_meta.get("sharpe", 0)
    if sharpe > 2.0:
        score += 20; details.append(f"sharpe:excellent({sharpe})")
    elif sharpe > 1.5:
        score += 15; details.append(f"sharpe:good({sharpe})")
    elif sharpe > 1.0:
        score += 10; details.append(f"sharpe:ok({sharpe})")
    elif sharpe > 0.8:
        score += 5; details.append(f"sharpe:weak({sharpe})")
    else:
        details.append(f"sharpe:poor({sharpe})")

    # 5. NAV trend - using discount field as proxy (15 pts)
    nav_change = fund_info.get("nav_change", 0)
    if nav_change < -2:
        score += 15; details.append(f"nav:deep_drop({nav_change}%)")
    elif nav_change < -1:
        score += 10; details.append(f"nav:moderate_drop({nav_change}%)")
    elif nav_change < 0:
        score += 7; details.append(f"nav:mild_drop({nav_change}%)")
    elif nav_change < 1:
        score += 5; details.append(f"nav:flat({nav_change}%)")
    else:
        score += 3; details.append(f"nav:rising({nav_change}%)")

    # 6. Stock ratio - high ratio means full investment (10 pts)
    stock_ratio = fund_info.get("stock_ratio", 0)
    if stock_ratio > 85:
        score += 10; details.append(f"position:full({stock_ratio}%)")
    elif stock_ratio > 70:
        score += 7; details.append(f"position:high({stock_ratio}%)")
    elif stock_ratio > 50:
        score += 4; details.append(f"position:medium({stock_ratio}%)")
    else:
        details.append(f"position:low({stock_ratio}%)")

    return score, details

def check_buy_signals(fund, fund_info, premium, score):
    """Check if buy conditions are triggered."""
    signals = []

    # Signal 1: Deep discount
    if premium is not None and premium < -1.5:
        signals.append({
            "type": "deep_discount",
            "level": "🔥强买入",
            "reason": f"折价率{premium}% (<-1.5%)"
        })

    # Signal 2: Good score + fair premium
    if score >= 65 and (premium is not None and premium < 2):
        signals.append({
            "type": "strong_buy",
            "level": "✅积极买入",
            "reason": f"综合评分{score}分 + 溢价率{premium}%"
        })

    # Signal 3: Moderate score + discount
    if score >= 50 and (premium is not None and premium < 0):
        signals.append({
            "type": "moderate_buy",
            "level": "⭐谨慎买入",
            "reason": f"综合评分{score}分 + 折价{premium}%"
        })

    # Signal 4: Prohibit - high premium
    if premium is not None and premium > 5:
        signals.append({
            "type": "prohibit",
            "level": "❌回避",
            "reason": f"溢价率{premium}% (>5%) 严重高估"
        })

    return signals

def run_monitor(fund_list=None):
    """Main monitor function. Returns structured data for AI analysis."""
    if fund_list is None:
        fund_list = DEFAULT_FUNDS

    print(f"Fetching LOF data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...", file=sys.stderr)
    data = fetch_jisilu_data()

    if not data:
        return {"error": "Failed to fetch data", "timestamp": datetime.now().isoformat()}

    results = []
    for fund in fund_list:
        code = fund["code"]
        info = data.get(code)
        if not info:
            continue

        premium = calculate_premium(info.get("price", 0), info.get("nav", 0))
        score, score_details = calculate_score(info, premium, fund)
        signals = check_buy_signals(fund, info, premium, score)

        result = {
            "code": code,
            "name": fund["name"],
            "strategy": fund["strategy"],
            "benchmark": fund["benchmark"],
            "price": info.get("price", 0),
            "nav": info.get("nav", 0),
            "premium": premium,
            "nav_change": info.get("nav_change", 0),
            "nav_date": info.get("nav_date", ""),
            "amount": info.get("amount", 0),
            "turnover": info.get("turnover", 0),
            "fund_size": info.get("fund_size", 0),
            "stock_ratio": info.get("stock_ratio", 0),
            "apply_status": info.get("apply_status", ""),
            "sharpe": fund.get("sharpe", 0),
            "max_dd": fund.get("max_dd", 0),
            "score": score,
            "score_details": score_details,
            "signals": signals,
        }
        results.append(result)

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    output = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market_status": "trading" if 9 <= datetime.now().hour <= 15 else "closed",
        "fund_count": len(results),
        "funds": results,
        "summary": {
            "strong_buy": len([f for f in results if f["score"] >= 65 and f.get("premium", 99) < 2]),
            "moderate_buy": len([f for f in results if 50 <= f["score"] < 65]),
            "watch": len([f for f in results if 35 <= f["score"] < 50]),
            "avoid": len([f for f in results if f["score"] < 35 or (f.get("premium") and f["premium"] > 5)]),
        }
    }
    return output

if __name__ == "__main__":
    result = run_monitor()
    print(json.dumps(result, ensure_ascii=False, indent=2))
