#!/usr/bin/env python3
"""
run_tencent.py
===============
Stock Scout 腾讯财经版 - 纯免费API，完整评分+选股
"""
import os, sys, logging, time, json
from datetime import datetime

# 项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MIN_SCORE
from score import calculate_score, get_signal_description

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# ─── 科技股候选池：自动从东方财富股票池读取 ─────────────────────────
POOL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "stock_pool.json")

def load_candidate_pool():
    """从 stock_pool.json 读取候选股票池"""
    if os.path.exists(POOL_FILE):
        with open(POOL_FILE, encoding="utf-8") as f:
            stocks = json.load(f)
        result = []
        for s in stocks:
            ts = s.get("ts_code", "")
            code = ts.lstrip("shszbjSHZBJ") or s.get("code", "")
            result.append({
                "ts_code": code,
                "name": s.get("name", ""),
                "industry": s.get("industry", ""),
            })
        print(f"从 {POOL_FILE} 加载 {len(result)} 只候选股票")
        return result
    else:
        print(f"⚠️ {POOL_FILE} 不存在，使用硬编码备用池")
        return []


def main():
    from providers.intelligence.tencent import TencentIntelligenceProvider

    today_str = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"[{today_str}] Stock Scout 腾讯版启动")
    provider = TencentIntelligenceProvider()

    candidates = load_candidate_pool()
    if not candidates:
        logger.error("无候选股票，请先运行 python build_pool.py 构建股票池")
        return []

    scored = []
    errors = 0

    for i, stock in enumerate(candidates):
        ts_code = stock["ts_code"]
        name = stock["name"]

        if i % 30 == 0:
            logger.info(f"进度: {i}/{len(candidates)} ...")

        try:
            northbound = provider.get_northbound_hold(ts_code)
            moneyflow  = provider.get_moneyflow(ts_code)
            margin     = provider.get_margin(ts_code)
            holder     = provider.get_holder_trade(ts_code, days=30)
            broker     = provider.get_broker_rating(ts_code)
            sector     = provider.get_sector_momentum(ts_code)

            rt = provider._fetch_realtime(ts_code)
            klines = provider._fetch_klines(ts_code, 60)

            price = rt.get("current", 0)
            prev_close = rt.get("prev_close", price)
            change_pct = (price - prev_close) / prev_close * 100 if prev_close > 0 else 0

            # 计算量比
            avg_vol = sum(k["volume"] for k in klines[-20:]) / 20 if len(klines) >= 20 else 1
            today_vol = rt.get("volume", 0)
            turnover_rate = (today_vol / (rt.get("current", 1) * 1e6) * 100) if rt.get("current", 0) > 0 else 0

            # 近5日价格趋势
            price_5d = 0.0
            if len(klines) >= 5:
                price_5d = (klines[-1]["close"] - klines[-5]["close"]) / klines[-5]["close"] * 100

            stock_data = {
                "ts_code": ts_code,
                "name": name,
                "northbound_pct": northbound.get("northbound_pct", 0),
                "margin_balance": margin.get("margin_balance", 0),
                "margin_change_pct": margin.get("margin_change_pct", 0),
                "moneyflow_net": moneyflow.get("moneyflow_net", 0),
                "moneyflow_large": moneyflow.get("moneyflow_large", 0),
                "broker_rating": broker.get("broker_rating", 0),
                "broker_target": broker.get("broker_target", 0),
                "price": price if price > 0 else northbound.get("close", 0),
                "change_pct": change_pct,
                "turnover_rate": turnover_rate,
                "price_5d_trend": price_5d,
                "broker_target_gap_pct": broker.get("target_gap_pct", 0),
            }

            sig = calculate_score(**stock_data)
            scored.append(sig)

            # 限速：30 calls/10s ≈ 3 calls/s，安全余量
            time.sleep(0.05)

        except Exception as e:
            errors += 1
            logger.debug(f"评分出错 {ts_code}: {e}")

    logger.info(f"评分完成：{len(scored)} 只成功，{errors} 只出错")

    # ── 筛选高分股 ───────────────────────────────────────────────────
    candidates_out = [s for s in scored if s.score >= MIN_SCORE]
    candidates_out.sort(key=lambda x: x.score, reverse=True)

    # ── 打印结果 ─────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print(f"📊 Stock Scout 结果 | 腾讯财经 API | {today_str} {datetime.now().strftime('%H:%M')}")
    print(f"候选股票: {len(scored)} 只 | 入围阈值: ≥{MIN_SCORE}分 | 入围: {len(candidates_out)} 只")
    print("=" * 72)

    if not candidates_out:
        print("\n今日无符合条件股票（可能市场整体偏弱）")
        # 打印 Top10 供参考
        top10 = sorted(scored, key=lambda x: x.score, reverse=True)[:10]
        print("\n--- Top10 评分（供参考）---")
        for s in top10:
            print(f"  [{s.score:3d}分] {s.name}({s.ts_code}) | {s.phase} | {s.signal_type}")
    else:
        print(f"\n🎯 入围股票（≥{MIN_SCORE}分，共{len(candidates_out)}只）：\n")
        for i, s in enumerate(candidates_out, 1):
            emoji = "🟢" if s.change_pct >= 0 else "🔴"
            desc = get_signal_description(s.signal_type)
            print(f"  {i:2d}. {s.name}({s.ts_code}) [{s.score}分] {s.phase}")
            print(f"       价格: ¥{s.price:.3f} {emoji}{s.change_pct:+.2f}%")
            print(f"       信号: {s.signal_type} | {desc}")
            print(f"       北向信号: {s.northbound_pct:.1f} | 融资变化: {s.margin_change_pct:+.1f}% | 主力净流入: {s.moneyflow_net:+.0f}万")
            print()

    # ── 持仓股评分（标记）────────────────────────────────────────────
    PORTFOLIO_CODES = {
        "510500", "588080", "600410", "600497", "601618",
        "601788", "603501", "000538", "002230", "002950",
        "300172", "09988", "02015",
    }
    portfolio_scores = [s for s in scored if s.ts_code in PORTFOLIO_CODES]
    portfolio_scores.sort(key=lambda x: x.score, reverse=True)

    print("=" * 72)
    print("📋 升爷持仓股评分（本次 Scout 结果）")
    print("=" * 72)
    if portfolio_scores:
        for s in portfolio_scores:
            emoji = "🟢" if s.change_pct >= 0 else "🔴"
            tag = "🎯入围" if s.score >= MIN_SCORE else ""
            print(f"  [{s.score:3d}分] {s.name}({s.ts_code}) | {s.phase} {tag}")
            print(f"       ¥{s.price:.3f} {emoji}{s.change_pct:+.2f}% | 信号:{s.signal_type} | 融资:{s.margin_change_pct:+.1f}%")
    else:
        print("  今日无持仓股数据")

    print(f"\n⏰ 报告生成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⚠️  本报告仅供参考，不构成投资建议")
    print("=" * 72)

    # 返回高分股列表（供外部调用）
    return candidates_out


if __name__ == "__main__":
    main()
