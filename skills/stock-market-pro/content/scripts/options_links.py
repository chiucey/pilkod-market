#!/usr/bin/env python3
"""
Stock Options Links - 获取美股期权相关链接
"""

import sys
import argparse


def get_options_links(ticker):
    """
    生成美股期权相关链接

    Args:
        ticker: 股票代码 (如 AAPL, TSLA)
    """
    ticker = ticker.upper().strip()

    links = {
        'yahoo_options': f"https://finance.yahoo.com/quote/{ticker}/options",
        'yahoo_chain': f"https://finance.yahoo.com/quote/{ticker}/options?straddle=true",
        'cboe': f"https://www.cboe.com/tradable_products/vix/options_vix/",
        'barchart': f"https://www.barchart.com/stocks/quotes/{ticker}/overview",
        'investpy': f"https://www.investing.com/equities/{ticker.lower()}-call-put-options",
        'stockanalysis': f"https://stockanalysis.com/stocks/{ticker.lower()}/options",
        'finviz': f"https://finviz.com/quote.ashx?t={ticker}",
    }

    print(f"=== {ticker} Options Links ===\n")
    print(f"Yahoo Finance Options:")
    print(f"  - Options Page: {links['yahoo_options']}")
    print(f"  - Straddle View: {links['yahoo_chain']}\n")
    print(f"Other Resources:")
    print(f"  - Barchart: {links['barchart']}")
    print(f"  - StockAnalysis: {links['stockanalysis']}")
    print(f"  - Finviz: {links['finviz']}\n")

    # 检查是否为有效期权标的
    # 蓝筹股通常有更多期权合约
    blue_chips = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'AMD', 'INTC']
    if ticker in blue_chips:
        print(f"Note: {ticker} is a popular options target with high liquidity.")
    else:
        print(f"Note: {ticker} may have limited options contracts.")

    return links


def main():
    parser = argparse.ArgumentParser(description="Get stock options links")
    parser.add_argument("ticker", help="Stock ticker symbol (e.g., AAPL, TSLA)")

    args = parser.parse_args()
    get_options_links(args.ticker)


if __name__ == "__main__":
    main()
