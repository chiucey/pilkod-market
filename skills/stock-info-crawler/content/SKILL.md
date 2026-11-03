---
name: stock-info-crawler
description: Professional stock information crawler that retrieves real-time stock prices, market data, and fundamental data from web sources. Used when users need to query stock prices, analyze fundamental data, obtain financial indicators, or conduct stock research.
---

# Stock Information Crawler

## Tool Overview

This tool provides comprehensive stock information retrieval capabilities, supporting access to accurate real-time stock prices and fundamental data from multiple authoritative financial data sources.

### Core Features

1. **Real-time Data Retrieval**: Latest stock prices, closing prices, price changes, market cap, trading volume, and other market data
2. **Fundamental Data Retrieval**: Revenue, profits, ROIC, cash flow, debt ratios, profit margins, and other financial metrics
3. **Multi-Market Support**: Stocks from A-shares, Hong Kong stocks, US stocks, and other major markets

## Usage Methods

### 1. Real-time Market Data Retrieval

Use `stocks_price` tool to obtain stock price time series data:

```json
{
  "queries": [{
    "symbol": "AAPL",
    "start_date": "2024-01-01",
    "end_date": "2024-03-25",
    "interval": "1d"
  }]
}
```

**Supported Parameters**

- `symbol`: Stock ticker symbol
  - A-shares: e.g., `600519.SS` (Kweichow Moutai), `000001.SZ` (Ping An Bank)
  - Hong Kong: e.g., `0700.HK` (Tencent), `9988.HK` (Alibaba)
  - US stocks: e.g., `AAPL`, `TSLA`, `GOOGL`
- `start_date`: Start date in YYYY-MM-DD format
- `end_date`: End date in YYYY-MM-DD format
- `interval`: Data interval, supports `1m` (minutes), `1h` (hours), `1d` (daily), `1wk` (weekly), `1mo` (monthly)

### 2. Stock Basic Information Query

Use `stocks_info` tool to obtain basic stock information and real-time data:

```json
{
  "queries": [{
    "symbol": "AAPL"
  }]
}
```

**Returned Data Fields**

| Field Name | Description | Data Type |
|-----------|-------------|-----------|
| symbol | Stock ticker symbol | String |
| shortName | Short company name | String |
| longName | Full company name | String |
| sector | Industry sector | String |
| industry | Specific industry | String |
| currentPrice | Current stock price | Number |
| previousClose | Previous closing price | Number |
| priceChange | Price change amount | Number |
| priceChangePercent | Price change percentage (%) | Number |
| marketCap | Total market capitalization | Number |
| peRatio | Price-to-Earnings ratio (PE) | Number |
| pbRatio | Price-to-Book ratio (PB) | Number |
| volume | Trading volume | Number |
| averageVolume | Average trading volume | Number |
| dividendYield | Dividend yield | Number |
| beta | Beta coefficient | Number |

### 3. Stock Financial Data Query

Use `stocks_financial_data` tool to obtain detailed financial data:

```json
{
  "queries": [{
    "symbol": "AAPL"
  }]
}
```

**Returned Financial Metrics**

| Metric Category | Specific Fields | Description |
|----------------|-----------------|-------------|
| **Profitability** | totalRevenue | Total operating revenue |
| | revenue | Operating revenue |
| | grossProfit | Gross profit |
| | operatingIncome | Operating income |
| | netIncome | Net income |
| | earningsGrowth | Earnings growth rate |
| **Valuation** | peRatio | Price-to-Earnings ratio |
| | pegRatio | Price/Earnings to Growth ratio |
| | pbRatio | Price-to-Book ratio |
| | psRatio | Price-to-Sales ratio |
| **Financial Health** | totalDebt | Total debt |
| | debtToEquity | Debt-to-Equity ratio |
| | currentRatio | Current ratio |
| | quickRatio | Quick ratio |
| **Cash Flow** | operatingCashflow | Operating cash flow |
| | investingCashflow | Investing cash flow |
| | financingCashflow | Financing cash flow |
| | freeCashflow | Free cash flow |
| **Efficiency Metrics** | roe | Return on Equity (ROE) |
| | roa | Return on Assets (ROA) |
| | roic | Return on Invested Capital (ROIC) |
| | profitMargin | Profit margin |
| | operatingMargin | Operating margin |
| | grossMargin | Gross margin |

### 4. Stock Statistics Analysis

Use `stocks_statistics` tool to obtain statistical and analytical data:

```json
{
  "queries": [{
    "symbol": "AAPL",
    "region": "US"
  }]
}
```

### 5. Stock News Query

Use `stocks_news` tool to obtain the latest news related to stocks:

```json
{
  "queries": [{
    "symbol": "AAPL",
    "region": "US",
    "snippet_count": 10
  }]
}
```

### 6. Stock Insights Analysis

Use `stocks_insights` tool to obtain professional analysis insights:

```json
{
  "queries": [{
    "symbol": "AAPL"
  }]
}
```

## Practical Application Examples

### Example 1: Query Complete Apple Inc. Stock Information

```python
# Get Apple Inc. real-time price data
stock_price = stocks_price(
    queries=[{
        "symbol": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-03-25",
        "interval": "1d"
    }]
)

# Get Apple Inc. basic information
stock_info = stocks_info(
    queries=[{"symbol": "AAPL"}]
)

# Get Apple Inc. financial data
financial_data = stocks_financial_data(
    queries=[{"symbol": "AAPL"}]
)
```

### Example 2: Query A-share Kweichow Moutai Stock

```python
# Kweichow Moutai stock code is 600519.SS
maotai_info = stocks_info(
    queries=[{"symbol": "600519.SS"}]
)
```

### Example 3: Batch Query Multiple Stocks

```python
# Batch get real-time data for multiple stocks
batch_data = stocks_info(
    queries=[
        {"symbol": "AAPL"},
        {"symbol": "GOOGL"},
        {"symbol": "MSFT"},
        {"symbol": "AMZN"}
    ]
)
```

### Example 4: Hong Kong Stock Query

```python
# Tencent Holdings stock code is 0700.HK
tencent_info = stocks_info(
    queries=[{"symbol": "0700.HK"}]
)
```

## Data Output Format

All tool-returned data is in JSON format, facilitating subsequent processing and analysis:

```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "shortName": "Apple Inc.",
    "currentPrice": 172.45,
    "previousClose": 170.20,
    "priceChangePercent": 1.32,
    "marketCap": 2700000000000,
    "peRatio": 28.5,
    "pbRatio": 45.2,
    "volume": 58000000,
    "totalRevenue": 394328000000,
    "netIncome": 97015000000,
    "roic": 45.2,
    "freeCashflow": 73000000000
  }
}
```

## Important Notes

1. **Data Latency**: Real-time data may have slight delays; recommend validating with multiple data sources
2. **Market Hours**: Data obtained during non-trading hours reflects the most recent trading day's data
3. **Symbol Format**: Ensure correct stock symbol format; different markets may have different formats
4. **API Limits**: Be aware of query frequency limits; avoid too many requests in a short period
5. **Data Validation**: Recommend performing reasonableness checks on obtained data to exclude anomalies

## Frequently Asked Questions

**Q: How to query US stocks?**
A: Use the stock ticker directly, e.g., `AAPL`, `TSLA`, `NVDA`, etc.

**Q: How to query A-shares?**
A: A-shares require exchange suffixes: `.SS` for Shanghai Exchange or `.SZ` for Shenzhen Exchange, e.g., `600519.SS`, `000001.SZ`.

**Q: How to query Hong Kong stocks?**
A: Hong Kong stocks use `.HK` suffix, e.g., `0700.HK` (Tencent), `9988.HK` (Alibaba).

**Q: What to do if ROIC data is incomplete?**
A: If ROIC field is empty, try calculating it from financial data: ROIC = Net Income / Invested Capital.

**Q: How far back can historical data go?**
A: Historical data typically covers recent years, depending on the stock and market.

## Technical Specifications

- **Data Source**: Yahoo Finance API
- **Supported Markets**: US stocks, A-shares (Shanghai, Shenzhen), Hong Kong stocks
- **Data Format**: JSON
- **Update Frequency**: Real-time updates
- **Error Handling**: Automatic retry mechanism with error information on failure
