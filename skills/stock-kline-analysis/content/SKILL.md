---
name: stock-kline-analysis
description: Stock K-line analysis skill for calculating technical indicators (risk metrics, liquidity metrics, valuation metrics) and providing buy/sell recommendations. Use when users request stock K-line analysis, buy/sell suggestions, technical indicator calculations (volatility, Beta, VaR, turnover rate), stock risk evaluation, or individual stock valuation analysis (PE, PB, dividend yield).
---

# Stock K-line Analysis Skill

## Overview

This skill retrieves stock K-line data from the web, calculates multi-dimensional technical indicators (risk indicators, liquidity indicators, valuation indicators), and provides buy/sell recommendations based on these metrics.

## Trigger Conditions

The skill is triggered when users request:
- Analyze stock K-line data
- Get stock buy/sell recommendations
- Calculate risk indicators (volatility, Beta, VaR)
- Analyze liquidity (turnover rate, fund flow)
- Valuation analysis (PE, PB, dividend yield)
- Comprehensive stock diagnosis

## Workflow

### Step 1: Collect Stock Symbols

1. Parse stock symbols provided by the user
2. Identify the market (A-share, Hong Kong, US)
3. Convert to API format:
   - A-share (Shanghai): add .SS (e.g., 600519.SS)
   - A-share (Shenzhen): add .SZ (e.g., 000858.SZ)
   - Hong Kong: use directly (e.g., 1211.HK)
   - US: use directly (e.g., AAPL)

### Step 2: Get K-line Data

Use `stocks_price` tool to retrieve historical K-line data:
- Time range: at least 60 trading days for accurate indicator calculation
- Data interval: daily (1d)

### Step 3: Calculate Market Risk Indicators

Calculate the following based on daily returns:

```
Daily Return = (Today's Close - Yesterday's Close) / Yesterday's Close

1. Volatility = STD(Daily Returns) × √252
   - Annualized volatility, reflects stock price fluctuation level

2. Beta = COV(Stock Daily Returns, Market Daily Returns) / VAR(Market)
   - Use CSI 300 Index (000300.SS) as A-share market benchmark
   - Beta > 1 indicates higher volatility than market, Beta < 1 indicates lower

3. VaR(95%) = Mean(Daily Returns) - 1.65 × STD(Daily Returns)
   - Maximum possible single-day loss at 95% confidence level
```

### Step 4: Calculate Liquidity Indicators

```
1. Turnover Rate = Trading Volume / Circulating Shares × 100%
   - Reflects stock trading activity

2. Turnover Change = (Today's Amount - Yesterday's Amount) / Yesterday's Amount × 100%
   - Positive indicates increasing investor attention

3. Fund Flow (Estimated) = Volume × Average Price × 0.1
   - Positive indicates net inflow
```

### Step 5: Calculate Valuation Indicators

After getting stock basic info:

```
1. PE (P/E Ratio) = Stock Price / Earnings Per Share (EPS)
   - Lower PE indicates cheaper valuation (need industry comparison)

2. PB (P/B Ratio) = Stock Price / Book Value Per Share
   - PB < 1 indicates stock price below book value

3. Dividend Yield = Dividend Per Share / Stock Price × 100%
   - High dividend yield usually indicates stable cash returns
```

### Step 6: Comprehensive Analysis and Recommendations

#### Risk Score (0-100, lower score means higher risk)

| Indicator | Weight | Assessment |
|-----------|--------|------------|
| Volatility | 25% | > 50% high risk, < 20% low risk |
| Beta | 25% | > 1.5 high risk, < 0.8 low risk |
| VaR | 25% | < -5% high risk, > -2% low risk |
| Turnover Rate | 25% | > 10% high turnover (short-term risk), < 2% low liquidity |

#### Liquidity Score (0-100)

| Indicator | Weight | Assessment |
|-----------|--------|------------|
| Turnover Rate | 40% | Moderate (2%-8%) is optimal |
| Turnover Change | 30% | Positive indicates increased attention |
| Fund Flow | 30% | Positive indicates net inflow |

#### Valuation Score (0-100)

| Indicator | Weight | Assessment |
|-----------|--------|------------|
| PE | 40% | Below industry average PE gets higher score |
| PB | 30% | PB < 1 gets higher score |
| Dividend Yield | 30% | > 3% gets higher score |

#### Comprehensive Score and Recommendations

```
Comprehensive Score = Risk Score × 0.4 + Liquidity Score × 0.3 + Valuation Score × 0.3

Recommendation Logic:
- Score >= 75: Strong Buy
- Score >= 60: Buy
- Score >= 45: Hold/Wait
- Score >= 30: Reduce Position
- Score < 30: Sell
```

## Output Format

The skill will output a report in the following format:

```markdown
# Stock K-line Analysis Report

## Basic Information
- Stock Symbol: [Symbol]
- Analysis Date: [Current Date]
- Data Period: [Date Range]

## 1. Risk Indicator Analysis
| Indicator | Value | Assessment |
|-----------|-------|------------|
| Annualized Volatility | XX.XX% | High/Normal/Low |
| Beta | X.XX | High Volatility/Match/Low Volatility |
| VaR(95%) | -XX.XX% | High/Medium/Low Risk |
| Risk Score | XX/100 | [Assessment] |

## 2. Liquidity Analysis
| Indicator | Value | Assessment |
|-----------|-------|------------|
| Turnover Rate | XX.XX% | Active/Normal/Inactive |
| Turnover Change | ±XX.XX% | Rising/Fair/Declining |
| Fund Flow | ±XX Million | Net Inflow/Net Outflow |
| Liquidity Score | XX/100 | [Assessment] |

## 3. Valuation Analysis
| Indicator | Value | Comparison |
|-----------|-------|------------|
| P/E Ratio | XX.XX | High/Medium/Low |
| P/B Ratio | X.XX | High/Medium/Low |
| Dividend Yield | X.XX% | High/Medium/Low |
| Valuation Score | XX/100 | [Assessment] |

## 4. Comprehensive Score and Recommendation
| Item | Value |
|------|-------|
| Risk Score | XX/100 |
| Liquidity Score | XX/100 |
| Valuation Score | XX/100 |
| **Comprehensive Score** | **XX/100** |

## 5. Investment Recommendation
[Specific Buy/Sell/Hold recommendation with reasons]

## 6. Technical Supplementary
[Optional: MA, MACD and other technical indicator analysis]
```

## Important Notes

1. **Data Limitations**: API data may have delays; refer to real-time data for important decisions
2. **Industry Differences**: Different industries have very different PE, PB ranges; valuation analysis needs industry comparison
3. **Market Environment**: Indicators may be distorted in extreme market conditions
4. **Risk Warning**: This analysis is for reference only and does not constitute investment advice

## Tool Dependencies

- `stocks_price`: Get historical K-line data
- `stocks_info`: Get stock basic information
- `stocks_financial_data`: Get financial data (backup)
