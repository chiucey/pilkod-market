"""
fetch.py
=========
数据获取脚本

从 Tushare 按 Provider 抽象接口拉取数据，
组装后传给 score.py 进行评分。

执行流程：
    1. 加载配置
    2. 初始化 Tushare Provider
    3. 获取科技股列表（申万行业分类）
    4. 遍历每只股票，并行获取5个维度数据
    5. 组装结果传给 score.py
    6. 写入 SQLite 缓存
"""

import os
import sys
import logging
import sqlite3
import time as time_mod
from datetime import datetime, timedelta
from dataclasses import asdict
from typing import Optional

# 确保项目根目录在 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tushare as ts
from config import (
    TUSHARE_TOKEN, DB_PATH, SECTOR, MAX_FLOAT_MILLION,
    MIN_SCORE
)
from score import calculate_score, score_batch, get_signal_description
from providers.intelligence.tushare import TushareIntelligenceProvider
from rate_limiter import get_limiter, with_rate_limit

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────
# SQLite 缓存
# ───────────────────────────────────────────────

def init_db(db_path: str):
    """初始化 SQLite 表结构"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS stocks_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            ts_code TEXT NOT NULL,
            name TEXT,
            score INTEGER,
            signal_type TEXT,
            phase TEXT,
            northbound_pct REAL,
            margin_change_pct REAL,
            moneyflow_net REAL,
            broker_rating REAL,
            target_gap_pct REAL,
            price REAL,
            change_pct REAL,
            turnover_rate REAL,
            UNIQUE(date, ts_code)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS signal_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            ts_code TEXT NOT NULL,
            signal_type TEXT,
            score INTEGER,
            UNIQUE(date, ts_code)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_code TEXT UNIQUE NOT NULL,
            name TEXT,
            added_date TEXT,
            active INTEGER DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS trade_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            ts_code TEXT NOT NULL,
            action TEXT NOT NULL,
            price REAL NOT NULL,
            phase TEXT,
            status TEXT DEFAULT 'open'
        )
    """)
    conn.commit()
    conn.close()
    logger.info(f"数据库初始化完成: {db_path}")


def save_to_db(signal, db_path: str):
    """单条信号写入 SQLite"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    today = datetime.now().strftime("%Y%m%d")
    try:
        c.execute("""
            INSERT OR REPLACE INTO stocks_daily
            (date, ts_code, name, score, signal_type, phase,
             northbound_pct, margin_change_pct, moneyflow_net,
             broker_rating, target_gap_pct, price, change_pct, turnover_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            today, signal.ts_code, signal.name, signal.score,
            signal.signal_type, signal.phase,
            signal.northbound_pct, signal.margin_change_pct,
            signal.moneyflow_net, signal.broker_rating,
            signal.target_gap_pct, signal.price,
            signal.change_pct, signal.turnover_rate
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"写入DB失败 {signal.ts_code}: {e}")
    conn.close()


# ───────────────────────────────────────────────
# 数据获取主逻辑
# ───────────────────────────────────────────────

def get_5d_price_change(provider: TushareIntelligenceProvider, ts_code: str) -> float:
    """获取近5日价格变动%"""
    try:
        today = datetime.now().strftime("%Y%m%d")
        start = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
        df = provider.pro.daily(ts_code=ts_code, start_date=start, end_date=today)
        if df is not None and len(df) >= 2:
            df = df.sort_values("trade_date")
            latest = float(df.iloc[-1]["close"])
            oldest = float(df.iloc[0]["close"])
            return (latest - oldest) / oldest * 100
    except Exception:
        pass
    return 0.0


def get_latest_price_change(provider: TushareIntelligenceProvider, ts_code: str) -> tuple[float, float, float]:
    """获取最新价格、涨跌幅、换手率"""
    try:
        today = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        df = provider.pro.daily(ts_code=ts_code, trade_date=today)
        if df is not None and not df.empty:
            row = df.iloc[0]
            return (
                float(row.get("close", 0)),
                float(row.get("pct_chg", 0)),
                float(row.get("turnover_rate", 0))
            )
    except Exception:
        pass
    return 0.0, 0.0, 0.0


def fetch_and_score(
    provider: TushareIntelligenceProvider,
    db_path: str,
    limit: int = 200,
) -> list:
    """
    主流程：获取科技股数据 → 评分 → 写入DB → 返回高分股

    Returns:
        list[StockSignal]: 评分 ≥ MIN_SCORE 的股票列表，按评分降序
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"[{today_str}] 开始获取科技股数据...")

    # Step 1：获取科技股列表
    stocks = provider.get_sector_stocks(sector=SECTOR, limit=limit)
    logger.info(f"获取到 {len(stocks)} 只科技股，开始逐个评分...")
    if not stocks:
        logger.error("未获取到任何股票，请检查 Tushare Token 或网络")
        return []

    scored = []
    errors = 0
    margin_skipped = 0

    # Step 2：逐只获取数据并评分
    for i, stock in enumerate(stocks):
        ts_code = stock["ts_code"]
        name = stock["name"]

        if i % 20 == 0:
            logger.info(f"进度: {i}/{len(stocks)} | 已评分:{len(scored)} | 限速模式:199calls/61s")

        try:
            # ── 限速调用：每 61 秒 199 个 token（约每 0.307 秒1次）─────────
            # 7 个接口 × ~200 只股票 ≈ 1400 calls
            limiter = get_limiter()

            def limited(fn, *a, **kw):
                """对 provider 方法包装：等 token + 指数退避重试"""
                return with_rate_limit(fn, *a, **kw)

            northbound = limited(provider.get_northbound_hold, ts_code)
            moneyflow  = limited(provider.get_moneyflow, ts_code)
            margin     = limited(provider.get_margin, ts_code)
            holder     = limited(provider.get_holder_trade, ts_code, days=30)
            broker     = limited(provider.get_broker_rating, ts_code)
            sector     = limited(provider.get_sector_momentum, ts_code)

            # 价格/涨跌幅/换手率（2个 API calls）
            price, change_pct, turnover_rate = get_latest_price_change(provider, ts_code)
            price_5d_trend = get_5d_price_change(provider, ts_code)

            # 构造评分输入
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
                "price_5d_trend": price_5d_trend,
                "broker_target_gap_pct": broker.get("target_gap_pct", 0),
            }

            sig = calculate_score(**stock_data)

            # 全部保存（无论分数高低）
            save_to_db(sig, db_path)
            scored.append(sig)

        except Exception as e:
            errors += 1
            logger.debug(f"评分出错 {ts_code}: {e}")

    logger.info(f"评分完成：{len(scored)} 只成功，{errors} 只出错")

    # Step 3：筛选高分股
    candidates = [s for s in scored if s.score >= MIN_SCORE]
    candidates.sort(key=lambda x: x.score, reverse=True)
    logger.info(f"入围 Scout 结果（≥{MIN_SCORE}分）：{len(candidates)} 只")

    return candidates


# ───────────────────────────────────────────────
# 入口
# ───────────────────────────────────────────────

if __name__ == "__main__":
    from rate_limiter import BUCKET_SIZE, REFILL_SEC
    ts.set_token(TUSHARE_TOKEN)
    init_db(DB_PATH)

    logger.info(f"限速策略：{BUCKET_SIZE} calls / {REFILL_SEC}s "
                f"(≈{BUCKET_SIZE/REFILL_SEC:.4f} calls/s，间隔≈{REFILL_SEC/BUCKET_SIZE:.4f}s/call)")

    provider = TushareIntelligenceProvider(token=TUSHARE_TOKEN)
    candidates = fetch_and_score(provider, DB_PATH)

    if candidates:
        logger.info("===== Scout 结果 =====")
        for i, s in enumerate(candidates[:20]):
            desc = get_signal_description(s.signal_type)
            print(f"{i+1}. {s.name}({s.ts_code}) 评分:{s.score} 信号:{s.signal_type} {s.phase}")
            print(f"   北向:{s.northbound_pct}% | 主力净流入:{s.moneyflow_net}万 | 融资变化:{s.margin_change_pct}% | 换手率:{s.turnover_rate}%")
            print(f"   {desc}")
    else:
        print("今日无符合条件的候选股")
