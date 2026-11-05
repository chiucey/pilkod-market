---
name: stock-analyzer
description: Analyze US stock volume, options anomalies, and latest news. Use when users ask about stock analysis, volume trends, options activity, put/call ratios, unusual options contracts, or market sentiment for any US stock.
---

# Stock Analyzer Tool

## Overview

This tool provides comprehensive technical analysis and market sentiment analysis for US stocks:

1. **Volume Analysis** - Historical volume statistics, anomaly detection, trend analysis
2. **Options Analysis** - Put/Call ratios, open interest, unusual options activity detection
3. **News & Sentiment** - Latest news retrieval, news sentiment analysis
4. **Company Info** - Basic financial data, analyst ratings, price targets

## Usage

### Command Line

```bash
python3 scripts/analyze_stock.py --ticker <TICKER> [--period <TIME_RANGE>]
```

**Parameters:**
- `--ticker`: Stock symbol (e.g., ONDS, AAPL, TSLA)
- `--period`: Historical data range: 1mo, 3mo, 6mo, 1y (default: 3mo)

### Examples

```bash
# Analyze ONDS stock (default 3 months)
python3 scripts/analyze_stock.py --ticker ONDS

# Analyze AAPL stock with 1 year history
python3 scripts/analyze_stock.py --ticker AAPL --period 1y

# Analyze TSLA stock with 6 months history
python3 scripts/analyze_stock.py --ticker TSLA --period 6mo
```

## Output Content

The analysis report includes:

### Company Information
- Current price, market cap
- Industry, sector
- Financial metrics (revenue, profit margin, P/E ratio)
- 52-week price range
- Analyst price targets and expected change

### Volume Analysis
- Average/max/min volume statistics
- Recent volume trends (5-day/20-day averages)
- Unusual high volume detection (> 2 standard deviations above mean)
- Volume trend assessment (rising/falling/stable)

### Options Analysis
- Available expiration dates
- Call/Put volume and open interest statistics
- Put/Call ratio (volume and open interest)
- Market sentiment (Bull/Bear/Neutral)
- Unusual options activity detection (volume/open interest ratio > 3)
  - Unusual Call contract details (strike, volume, implied volatility)
  - Unusual Put contract details (strike, volume, implied volatility)

### News & Sentiment
- Latest news from Yahoo Finance
- News sentiment analysis (positive/negative/neutral counts)
- Fallback financial news links (Yahoo Finance, Google Finance, Seeking Alpha)

**Note**: Due to API rate limits, automatic news retrieval may be unstable. This tool can use web search for latest news when needed.

### Summary
- Quick overview of all key information

## Dependencies

Install required packages before first use:

```bash
pip install yfinance pandas numpy beautifulsoup4
```

## Disclaimer

This analysis is for reference only and does not constitute investment advice. Stock investing involves risk; trade carefully.

## Use Cases

- User asks about a stock's volume situation
- User wants to understand unusual options market activity
- User needs latest news and market sentiment for a stock
- User wants a quick overview of a stock's technicals
- Any US stock analysis scenario
