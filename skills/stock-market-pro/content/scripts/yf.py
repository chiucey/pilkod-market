#!/usr/bin/env python3
"""
Yahoo Finance 专用模块 - 备选方案
当 multi_source.py 中的 yfinance 功能需要独立使用时
"""

import sys
import argparse
import yfinance as yf
from datetime import datetime, timedelta


def get_realtime_quote(ticker):
    """获取实时报价"""
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info

        current = info.get('currentPrice') or info.get('regularMarketPrice')
        prev = info.get('regularMarketPreviousClose') or info.get('previousClose')
        open_price = info.get('open')
        high = info.get('dayHigh')
        low = info.get('dayLow')
        volume = info.get('volume')
        market_cap = info.get('marketCap')

        print(f"=== {ticker} Real-time Quote ===")
        print(f"Current Price: {current}")
        print(f"Previous Close: {prev}")
        if isinstance(current, (int, float)) and isinstance(prev, (int, float)):
            change = current - prev
            pct = (change / prev) * 100 if prev else 0
            print(f"Change: {change:+.2f} ({pct:+.2f}%)")
        print(f"Open: {open_price}")
        print(f"Day Range: {low} - {high}")
        print(f"Volume: {volume:,}" if volume else "Volume: N/A")
        if market_cap:
            print(f"Market Cap: ${market_cap/1e9:.2f}B")

    except Exception as e:
        print(f"Failed to get quote: {e}")


def get_history_data(ticker, period="6mo"):
    """获取历史数据"""
    try:
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period=period)

        if df.empty:
            print("No data available")
            return

        print(f"=== {ticker} Historical Data ({period}) ===")
        print(df.tail(30).to_string())

        # 简单统计
        print(f"\n=== Summary Statistics ===")
        print(f"Latest Close: {df['Close'].iloc[-1]:.2f}")
        print(f"30-Day High: {df['High'].tail(30).max():.2f}")
        print(f"30-Day Low: {df['Low'].tail(30).min():.2f}")
        print(f"Average Volume: {df['Volume'].tail(30).mean():,.0f}")

        return df
    except Exception as e:
        print(f"Failed to get history: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Yahoo Finance Stock Data")
    parser.add_argument("action", choices=["quote", "history"])
    parser.add_argument("ticker")
    parser.add_argument("--period", default="6mo")

    args = parser.parse_args()

    if args.action == "quote":
        get_realtime_quote(args.ticker)
    elif args.action == "history":
        get_history_data(args.ticker, args.period)


if __name__ == "__main__":
    main()
