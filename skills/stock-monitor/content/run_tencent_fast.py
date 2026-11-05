#!/usr/bin/env python3
"""
run_tencent_fast.py
====================
Stock Scout 腾讯版 - 多线程并发版
- 10个线程并发请求，速率提升~8倍
- 641只股票预计8-10分钟完成
"""
import os, sys, logging, time, json, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import MIN_SCORE
from score import calculate_score, get_signal_description

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

POOL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "stock_pool.json")

# ─── 线程安全的结果收集器 ──────────────────────────────────────────────
_results_lock = threading.Lock()
_scored: list = []
_errors = 0
_done_count = 0
_total = 0
_start_time = time.time()

def load_pool():
    if os.path.exists(POOL_FILE):
        with open(POOL_FILE, encoding="utf-8") as f:
            stocks = json.load(f)
        result = []
        for s in stocks:
            ts = s.get("ts_code", "")
            code = ts.lstrip("shszbjSHZBJ") or s.get("code", "")
            if code:
                result.append({"ts_code": code, "name": s.get("name", ""),
                                "industry": s.get("industry", "")})
        print(f"加载 {len(result)} 只候选股票（来自 {POOL_FILE}）")
        return result
    print(f"⚠️ {POOL_FILE} 不存在，请先运行 python build_pool.py")
    return []


def process_one(stock: dict) -> dict:
    """单只股票评分（在线程中执行）"""
    global _done_count, _errors

    ts_code = stock["ts_code"]
    name = stock["name"]

    try:
        from providers.intelligence.tencent import TencentIntelligenceProvider
        provider = TencentIntelligenceProvider()

        # 并发场景下每个线程用自己的 provider 实例（避免共享状态冲突）
        northbound = provider.get_northbound_hold(ts_code)
        moneyflow  = provider.get_moneyflow(ts_code)
        margin     = provider.get_margin(ts_code)
        holder     = provider.get_holder_trade(ts_code, days=30)
        broker     = provider.get_broker_rating(ts_code)
        rt         = provider._fetch_realtime(ts_code)
        klines     = provider._fetch_klines(ts_code, 60)

        price = rt.get("current", 0)
        prev_close = rt.get("prev_close", price)
        change_pct = (price - prev_close) / prev_close * 100 if prev_close > 0 else 0

        avg_vol = sum(k["volume"] for k in klines[-20:]) / 20 if len(klines) >= 20 else 1
        turnover_rate = (rt.get("volume", 0) / avg_vol) if avg_vol > 0 else 0

        price_5d = 0.0
        if len(klines) >= 5:
            price_5d = (klines[-1]["close"] - klines[-5]["close"]) / klines[-5]["close"] * 100

        stock_data = {
            "ts_code": ts_code, "name": name,
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
        sig._industry = stock.get("industry", "")

        with _results_lock:
            _done_count += 1
            if _done_count % 30 == 0:
                elapsed = time.time() - _start_time
                rate = _done_count / elapsed
                eta = (_total - _done_count) / rate if rate > 0 else 0
                logger.info(f"进度: {_done_count}/{_total} ({rate:.1f}只/秒, 剩余约{eta:.0f}秒)")

        return sig

    except Exception as e:
        with _results_lock:
            _errors += 1
            _done_count += 1
        logger.debug(f"评分出错 {ts_code}: {e}")
        return None


def main():
    global _total, _scored, _errors, _done_count, _start_time
    _start_time = time.time()

    today_str = datetime.now().strftime("%Y-%m-%d")
    print("=" * 70)
    print(f"📊 Stock Scout 腾讯版 | 多线程并发 | {today_str}")
    print("=" * 70)

    candidates = load_pool()
    if not candidates:
        return []
    _total = len(candidates)

    # ── 多线程并发评分（10个线程）────────────────────────────────────
    print(f"启动 10 线程并发处理 {_total} 只股票...")
    scored = []
    errors = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_one, s): s for s in candidates}
        for future in as_completed(futures):
            result = future.result()
            if result:
                scored.append(result)

    elapsed = time.time() - _start_time
    print(f"\n✅ 评分完成: {len(scored)} 只成功, {errors} 只出错, 耗时 {elapsed:.0f}秒")

    # ── 筛选 ──────────────────────────────────────────────────────
    candidates_out = [s for s in scored if s.score >= MIN_SCORE]
    candidates_out.sort(key=lambda x: x.score, reverse=True)

    # ── 持仓股 ─────────────────────────────────────────────────────
    PORTFOLIO_CODES = {
        "510500","588080","600410","600497","601618",
        "601788","603501","000538","002230","002950",
        "300172","09988","02015",
    }
    portfolio_scores = [s for s in scored if s.ts_code.lstrip("shszbjSHZBJH") in
                       [c.lstrip("shszbjSHZBJH") for c in PORTFOLIO_CODES]]
    portfolio_scores.sort(key=lambda x: x.score, reverse=True)

    # ── 输出 ──────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"📊 Stock Scout 结果 | {today_str} {datetime.now().strftime('%H:%M')}")
    print(f"候选股票: {len(scored)} 只 | 入围阈值: ≥{MIN_SCORE}分 | 入围: {len(candidates_out)} 只")
    print("=" * 70)

    if candidates_out:
        print(f"\n🎯 入围股票（≥{MIN_SCORE}分，共{len(candidates_out)}只）：\n")
        for i, s in enumerate(candidates_out, 1):
            emoji = "🟢" if s.change_pct >= 0 else "🔴"
            industry = getattr(s, '_industry', '')
            desc = get_signal_description(s.signal_type)
            print(f"  {i:2d}. {s.name}({s.ts_code}) [{s.score}分] {s.phase}" +
                  (f" [{industry}]" if industry else ""))
            print(f"       ¥{s.price:.3f} {emoji}{s.change_pct:+.2f}%")
            print(f"       信号:{s.signal_type} | {desc}")
            print()
    else:
        top10 = sorted(scored, key=lambda x: x.score, reverse=True)[:10]
        print(f"\n今日无入围股票（市场偏弱），Top10供参考：\n")
        for i, s in enumerate(top10, 1):
            emoji = "🟢" if s.change_pct >= 0 else "🔴"
            industry = getattr(s, '_industry', '')
            print(f"  {i:2d}. {s.name}({s.ts_code}) [{s.score}分] {s.phase}" +
                  (f" [{industry}]" if industry else ""))
            print(f"       ¥{s.price:.3f} {emoji}{s.change_pct:+.2f}% | {s.signal_type}")

    print("\n" + "=" * 70)
    print("📋 升爷持仓股评分")
    print("=" * 70)
    if portfolio_scores:
        for s in portfolio_scores:
            emoji = "🟢" if s.change_pct >= 0 else "🔴"
            tag = "🎯入围" if s.score >= MIN_SCORE else ""
            print(f"  [{s.score:3d}分] {s.name}({s.ts_code}) | {s.phase} {tag}")
            print(f"       ¥{s.price:.3f} {emoji}{s.change_pct:+.2f}% | 信号:{s.signal_type} | 融资:{s.margin_change_pct:+.1f}%")
    else:
        print("  今日无持仓股数据")

    print(f"\n⏰ 完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 耗时{elapsed:.0f}秒")
    print("⚠️  仅供参考，不构成投资建议")
    print("=" * 70)

    return candidates_out


if __name__ == "__main__":
    main()
