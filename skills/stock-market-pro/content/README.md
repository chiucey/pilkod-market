# Stock Market Pro - Multi-Source Stock Analysis Tool

## Overview

Stock Market Pro is a professional multi-source stock analysis tool that supports **Yahoo Finance, 东方财富 (dfcf), 富途牛牛 (futu), 新浪财经 (sina), Wind, Tushare, AkShare** seven mainstream data sources. It provides real-time quotes, fundamental data, technical charts, and comprehensive reports, covering **A-shares, HK stocks, US stocks, and global markets**.

## Features

- **Real-time Quotes**: Multi-source acquisition of latest price, change percentage
- **Fundamentals**: Market cap, PE, EPS, ROE, etc. (Most comprehensive from 东方财富)
- **Historical Data**: ASCII table output
- **Professional Charts**: PNG format, supports RSI, MACD, Bollinger Bands, VWAP, ATR
- **Comprehensive Reports**: One-click output of price + fundamentals + chart
- **News Search** (DuckDuckGo)
- **Options Links** (US stocks)

## Data Source Selection Guide

| User Type | Recommended Source | Description |
|-----------|-------------------|-------------|
| A-share investors | 东方财富 (dfcf) | Most comprehensive, free, no barriers |
| HK/US cross-border | 富途牛牛 (futu) | Requires OpenD running, strong analysis |
| Global news coverage | 新浪财经 (sina) | 40+ markets, fast news |
| Quant trading beginners | Tushare | Requires token, free tier sufficient |
| Institutional/professional | Wind | Requires Wind terminal and account |
| Free and open source | AkShare | No configuration, wide coverage |
| International/crypto/forex | Yahoo Finance (yfinance) | Global markets |

## Installation

### Required Dependencies

```bash
pip install yfinance akshare efinance pandas numpy matplotlib
```

### Optional Dependencies

```bash
pip install tushare                 # Tushare data source
pip install futu-api                # 富途牛牛 (requires OpenD running)
# Wind requires WindPy (from Wind terminal)
```

### Environment Variables (Optional)

```bash
export TUSHARE_TOKEN="your_token"
export WIND_USERNAME="username"
export WIND_PASSWORD="password"
```

## Usage

### Command Line

```bash
# 东方财富
python scripts/multi_source.py price 600519 --source=dfcf

# 富途牛牛 (requires OpenD)
python scripts/multi_source.py price 00700 --source=futu

# 新浪
python scripts/multi_source.py history 000001 --source=sina --period=3mo

# Tushare (requires token)
python scripts/multi_source.py pro 000001 --source=tushare --rsi --macd

# AkShare
python scripts/multi_source.py report 00700 --source=akshare

# Yahoo Finance
python scripts/multi_source.py price AAPL --source=yfinance
```

### Python API

```python
from src.main import run

# Get real-time quote
result = run({
    "action": "price",
    "ticker": "AAPL",
    "data_source": "yfinance"
})

# Generate technical chart
result = run({
    "action": "pro",
    "ticker": "600519",
    "data_source": "dfcf",
    "period": "6mo",
    "indicators": ["rsi", "macd", "bb"]
})

# Generate comprehensive report
result = run({
    "action": "report",
    "ticker": "00700",
    "data_source": "futu",
    "period": "1y"
})
```

## Supported Operations

| Action | Description |
|--------|-------------|
| `price` | Get real-time quote |
| `fundamentals` | Get fundamental data |
| `history` | Get historical data |
| `pro` | Generate professional charts |
| `report` | Generate comprehensive report |
| `news` | Search related news |
| `options` | Get options links (US stocks) |

## Technical Indicators

- **RSI** - Relative Strength Index (14-day default)
- **MACD** - Moving Average Convergence Divergence (12/26/9)
- **BB** - Bollinger Bands (20-day, 2x standard deviation)
- **VWAP** - Volume Weighted Average Price
- **ATR** - Average True Range (14-day)

## Stock Code Formats

- **US stocks**: Direct code, e.g., `AAPL`, `TSLA`
- **A-shares**: 6-digit number, e.g., `600519` (Shanghai), `000001` (Shenzhen)
- **HK stocks**: 4-5 digit number, e.g., `00700`

## Project Structure

```
stock-market-pro/
├── SKILL.md                    # Skill definition
├── README.md                   # This file
├── src/
│   ├── __init__.py
│   └── main.py               # Main entry point
├── scripts/
│   ├── __init__.py
│   ├── multi_source.py       # Multi-source unified interface
│   ├── news.py                # News search
│   ├── options_links.py      # Options links
│   ├── yf.py                  # Yahoo Finance backup
│   ├── uw.py                  # Utility functions
│   └── ddg_search.py          # DuckDuckGo search
├── instructions/
│   └── system_prompt.md       # System prompt
├── config/
│   └── settings.yaml         # Configuration
├── tests/
│   ├── __init__.py
│   └── test_main.py          # Unit tests
└── assets/
    └── .gitkeep
```

## Important Notes

- 富途牛牛 requires OpenD gateway running (default port 11111).
- Tushare free version has API call frequency limits.
- Wind data source requires Wind terminal purchase.
- Chart files are saved in `/tmp` directory.
- This tool is for reference only and does not constitute investment advice.
- Please respect the terms of service of each data platform.

## License

MIT-0

---

**Optimized**: This skill supports multi-source intelligent routing, allowing users to choose the optimal data source based on their needs, truly achieving "one tool, covering the globe".
