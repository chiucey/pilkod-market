---
name: gold-nasdaq-etf-analyzer
description: Professional analysis assistant for Gold ETF and Nasdaq ETF trading. Use when users ask to analyze Gold ETF or Nasdaq ETF market trends, buy/sell timing, news impact assessment, risk evaluation, or questions like "Is today good for Gold ETF?", "Should I hold Nasdaq ETF?", "Why is Gold rising?", "What affects Nasdaq ETF?". Supports daily market monitoring and trading signal generation.
---

# Gold ETF & Nasdaq ETF Analysis Assistant

## Core Capabilities

This skill combines real-time news, market data, and professional analysis frameworks to provide investors with trading decision support for Gold ETFs and Nasdaq ETFs.

## Analysis Dimensions

### 1. Gold ETF Analysis Framework

**Price Drivers:**

- **Real Interest Rates**: Gold price negatively correlates with real US interest rates; rate cuts benefit gold
- **Central Bank Purchases**: Gold buying by global central banks is a key price support, especially amid de-dollarization
- **Geopolitical Risk**: Regional conflicts and war threats increase safe-haven demand
- **Inflation Levels**: Gold's hedging value increases during high inflation periods
- **Risk Sentiment**: Capital flows to gold during market volatility

**Technical Signal Recognition:**

- Gold price breaking key resistance levels (e.g., $2640/oz)
- Gold ETF NAV hitting record highs
- Gold stocks ETFs outperforming

### 2. Nasdaq ETF Analysis Framework

**Price Drivers:**

- **Fed Policy**: Rate hikes are bearish for tech stocks; rate cuts benefit growth stocks
- **Tech Earnings**: Performance of weighted stocks like Apple, Microsoft, Google affects index
- **Macro Economy**: GDP, employment data, CPI influence market expectations
- **Valuation Levels**: Nasdaq 100 adjustment risk when at historical high valuations
- **Market Sentiment**: Fear & Greed Index, VIX volatility

**Technical Signal Recognition:**

- Nasdaq futures dropping significantly (e.g., Nasdaq 100 futures down >1%)
- Tech sector rotation signals
- US-China stock market correlation effects

## Execution Workflow

### Step 1: Collect Real-Time News

Use `batch_web_search` tool with queries:

```json
{
  "queries": [
    {"query": "Gold ETF Gold price today", "data_range": "d"},
    {"query": "Nasdaq ETF Nasdaq market", "data_range": "d"},
    {"query": "Federal Reserve interest rate gold", "data_range": "d"},
    {"query": "Tech stocks earnings Nasdaq", "data_range": "d"}
  ]
}
```

### Step 2: Analyze News Impact

**Gold ETF News Analysis:**

1. Extract gold-related macro news (USD, rates, inflation)
2. Identify geopolitical events (Middle East conflicts, Russia-Ukraine situation)
3. Track central bank buying dynamics and institutional forecasts
4. Assess safe-haven sentiment changes

**Nasdaq ETF News Analysis:**

1. Monitor Fed officials' speeches and monetary policy signals
2. Analyze mega-cap tech earnings releases
3. Evaluate macro data impact on tech stocks
4. Track pre-market US stock futures

### Step 3: Generate Trading Signals

**Signal Levels:**

- **Strong Buy**: Multiple positive factors converging, technical breakout
- **Cautious Buy**: Improving fundamentals but elevated valuations
- **Hold**: No clear direction, waiting for signals
- **Cautious Sell**: Overvaluation or bearish factors emerging
- **Strong Sell**: Clear trend reversal signals

**Output Format:**

```
## [ETF Name] Analysis Report

### Fundamental Summary
[Key news highlights]

### Price Action
[Current price, key support/resistance levels]

### Signal Rating
| Dimension | Score | Commentary |
|-----------|-------|------------|
| Fundamentals | XX/10 | [Assessment] |
| Technicals | XX/10 | [Assessment] |
| Sentiment | XX/10 | [Assessment] |

### Overall Recommendation
**[Buy/Hold/Sell]** - [Core rationale summary]

### Risk Reminders
[Key risk factors to note]
```

### Step 4: Risk Disclosures

Must include the following disclaimer:

> WARNING: This analysis is for reference only and does not constitute investment advice. ETF prices are affected by multiple factors and involve risk of loss. Please make investment decisions based on your own risk tolerance.

## Trigger Scenarios

**Valid Triggers:**

- "Analyze my Gold ETF holdings"
- "Is Nasdaq ETF suitable for buying today"
- "Why has Gold been rising recently"
- "Help me assess Nasdaq ETF risks"
- "How does Fed rate hike affect Gold ETF"

**Non-Trigger Scenarios:**

- Analyzing A-share ETFs (use other skills)
- Simple news search without analysis needs
- Individual stock recommendation requests

## Quality Standards

1. **Timeliness**: Prioritize using today's or recent news data
2. **Accuracy**: Cite news sources with `<citation>{{index}}</citation>` tags
3. **Completeness**: Cover fundamentals, technicals, and sentiment dimensions
4. **Actionability**: Provide clear trading recommendations and risk warnings

## References

For detailed methodology, see `references/analysis_framework.md`
