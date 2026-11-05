---
name: stock-valuation-analyst
description: Professional stock valuation analysis skill for comprehensive financial analysis. Use when users request stock valuation, chip distribution analysis, buy/sell signal generation, SSE Index chip analysis, fundamental analysis, financial statement analysis, valuation metrics interpretation, intrinsic value calculation, or investment recommendations.
---

# Stock Valuation Analyst

## Skill Overview

Professional stock valuation analysis toolkit providing systematic and scientific valuation methodologies. Integrates absolute valuation, relative valuation, chip distribution analysis, and technical analysis across multiple dimensions.

## Core Analysis Framework

### 1. Valuation Method System

#### 1.1 Absolute Valuation (Intrinsic Value)

**DCF (Discounted Cash Flow) Model**

```
Intrinsic Value = Σ [FCFt / (1+WACC)^t] + TV / (1+WACC)^n

Where:
- FCFt = Free Cash Flow in year t
- WACC = Weighted Average Cost of Capital
- TV = Terminal Value
- n = Forecast period
```

**Dividend Discount Model (DDM)**

```
V = Σ [DPSt / (1+r)^t]

Applicable: Stable dividend-paying blue-chip stocks
```

**Residual Income Model (RI)**

```
V = BV0 + Σ [ROEt × BVt-1 - r × BVt-1] / (1+r)^t
```

#### 1.2 Relative Valuation

| Metric | Formula | Use Case | Reference |
|--------|---------|----------|-----------|
| PE (P/E Ratio) | Price / EPS | Growth companies | Industry average, historical percentile |
| PB (P/B Ratio) | Price / Book Value | Financials, cyclical | Asset revaluation value |
| PS (P/S Ratio) | Price / Revenue | Loss or high-growth | Industry standard |
| EV/EBITDA | Enterprise Value / EBITDA | Capital-intensive | Cross-border comparison |
| PEG | PE / Earnings Growth | Growth stocks | <1 undervalued |
| PCF | Price / Cash Flow | Stable cash flow | Industry average |

#### 1.3 Special Valuation Methods

**Liquidation Value Method**

```
Liquidation Value = Σ (Asset Liquidation Value × Liquidation Ratio) - Liabilities
Per Share Liquidation = Liquidation Value / Total Shares
```

**Historical Valuation Method**

```
Current Valuation Percentile = (Current - Historical Low) / (Historical High - Historical Low) × 100%
```

---

### 2. Valuation Analysis Process

#### 2.1 Fundamental Analysis Phase

1. **Industry Positioning Analysis**
   - Industry lifecycle stage assessment
   - Industry competitive landscape
   - Industry cyclicality evaluation

2. **Company Competitive Position**
   - Market share analysis
   - Moat analysis (brand, patents, switching costs, network effects, cost advantages)
   - Management capability assessment

3. **Business Model Evaluation**
   - Revenue structure analysis
   - Cost structure analysis
   - Cash flow characteristics

#### 2.2 Financial Analysis Phase

**Profitability Analysis**

| Metric | Calculation | Quality Standard |
|--------|-------------|------------------|
| Gross Margin | (Revenue - COGS) / Revenue | >30% (consumer), >40% (pharma) |
| Net Margin | Net Income / Revenue | >10% |
| ROE | Net Income / Equity | >15% |
| ROIC | EBIT(1-Tax Rate) / Invested Capital | >10% |

**Growth Analysis**

- Revenue growth (YoY, QoQ)
- Net income growth
- Cash flow growth comparison
- Quarterly trend analysis

**Financial Health**

```
Current Ratio = Current Assets / Current Liabilities (>1.5)
Quick Ratio = (Current Assets - Inventory) / Current Liabilities (>1.0)
Debt-to-Asset = Total Debt / Total Assets (<50%)
Interest Coverage = EBIT / Interest Expense (>3)
```

#### 2.3 Valuation Calculation Phase

**Multi-Scenario Valuation**

| Scenario | Optimistic | Base | Conservative |
|----------|------------|------|--------------|
| Revenue Growth | Industry +10% | Industry | Industry -5% |
| Net Margin | Historical high | Average | Historical low |
| Valuation Multiple | Industry high | Industry median | Industry low |

**Valuation Range Determination**

```
Undervalued: Current Price < Conservative Value × 0.8
Fair Value: Conservative × 0.8 ≤ Current ≤ Optimistic × 1.2
Overvalued: Current Price > Optimistic × 1.2
```

---

### 3. Chip Distribution Analysis

#### 3.1 Cost Distribution Analysis

**Chip Concentration Indicator**

```
Chip Concentration = (Cost 90% - Cost 10%) / Cost 50% × 100%

- <10%: Highly concentrated, major player control
- 10%-30%: Relatively concentrated
- >30%: Dispersed, loose chips
```

**COST (Cost MA)**

- 15/30/60/120/250-day cost moving averages
- Relationship between price and cost MA indicates holding cost

#### 3.2 Major Player Behavior Identification

**Accumulation Characteristics**

- Low-position sustained low-volume consolidation
- Breakthrough on increasing volume
- Shareholder count continuously decreasing
- Block trades at discount

**Distribution Characteristics**

- High-position price stagnation with volume
- Multiple failures to break new highs
- Shareholder count significantly increasing
- Block trades at premium or par

**Washout Characteristics**

- Pullback to key support on low volume
- Quick drop followed by quick recovery
- Increased volatility but stable center

#### 3.3 Support and Resistance Analysis

**Support Level Identification**

```
Support Priority:
1. Historical trading congestion area
2. Previous lows
3. Round numbers
4. Trendline support
5. Moving average support (20/60/120-day)
```

**Resistance Level Identification**

```
Resistance Priority:
1. Historical trading congestion area
2. Previous highs
3. Trendline resistance
4. Moving average resistance
5. Fibonacci retracement levels
```

---

### 4. Buy/Sell Signal System

#### 4.1 Value Investment Signals

**Buy Signals**

```
✅ PE/PB at historical low percentile (<20%)
✅ Price below liquidation value
✅ Industry leader with valuation discount
✅ Turning point in performance
✅ Major shareholders/institutions continuously buying
```

**Sell Signals**

```
❌ PE/PB at historical high percentile (>80%)
❌ Industry at cyclical peak
✅ Core competitive advantage eroded
✅ Management significantly reducing holdings
✅ Valuation bubble
```

#### 4.2 Technical Signals

**Trend Confirmation Signals**

| Signal Type | Buy Condition | Sell Condition |
|-------------|---------------|----------------|
| MA | Price above MA with MA trending up | Price below MA with MA trending down |
| MACD | DIF crosses above DEA, red bar expanding | DIF crosses below DEA, green bar expanding |
| RSI | RSI<30 oversold golden cross | RSI>70 overbought death cross |
| KDJ | J value<20 golden cross | J value>80 death cross |

#### 4.3 Combined Signal Judgment

```
Strong Buy = Undervalued + Technical bottom + Fund inflow + Improving earnings
Strong Sell = Overvalued + Technical top + Fund outflow + Declining earnings
```

---

### 5. SSE Index Chip Analysis

#### 5.1 Index Cost Structure

**Average Cost Calculation**

```
SSE Average Cost = Σ(Close × Volume) / ΣVolume
```

**Cost Range Distribution**

- Below 3000: Historical low-cost area
- 3000-3500: Medium cost area
- 3500-4000: Higher cost area
- Above 4000: High cost area

#### 5.2 Index Trend Judgment

**Bull/Bear Force Comparison**

```
Bull Force = Breakthroughs + Upside volume days
Bear Force = Breakdowns + Downside volume days
Trend Signal = Bull Force / (Bull + Bear Force)
```

---

### 6. Financial Report Interpretation

#### 6.1 Annual Report Key Points

**Balance Sheet**

- Asset quality (receivables, inventory, goodwill)
- Liability structure (interest-bearing debt ratio)
- Cash reserves (cash/interest-bearing debt)

**Income Statement**

- Revenue growth quality (non-seasonal)
- Gross margin trend
- Expense ratio control
- Net income cash quality

**Cash Flow Statement**

- Operating CF / Net Income > 1
- Investment CF reasonableness
- Financing CF changes

#### 6.2 Quarterly Report Tracking

- Revenue QoQ changes
- Single-quarter gross margin
- Expense trend
- Order/advance receivable changes

#### 6.3 Financial Anomaly Detection

```
Warning Signals:
⚠️ Receivables growth > Revenue growth
⚠️ Inventory growth > Revenue growth
⚠️ Operating cash flow continuously negative
⚠️ Gross margin abnormal fluctuation
⚠️ Large goodwill impairment
⚠️ Abnormal related-party transactions
```

---

### 7. Analysis Output Standards

#### 7.1 Valuation Report Template

```markdown
## [Company Name] Valuation Analysis Report

### 1. Company Overview
- Main business description
- Industry position
- Core competitive advantages

### 2. Financial Analysis
- Profitability metrics
- Growth metrics
- Financial health

### 3. Valuation Analysis
- Absolute valuation (DCF assumptions)
- Relative valuation (industry comparison)
- Valuation range

### 4. Chip Analysis
- Cost distribution
- Major player activity
- Support and resistance

### 5. Investment Recommendation
- Current valuation status
- Reasonable buy range
- Stop-loss/take-profit recommendations
```

#### 7.2 Risk Disclosures

- Valuation assumption risks
- Industry cyclicality risks
- Market systemic risks
- Stock-specific risks

---

### 8. Usage Guidelines

1. **Multi-Dimensional Verification**: Single valuation method has limitations, recommend comprehensive approaches
2. **Dynamic Adjustment**: Adjust timely based on macro environment, industry changes, company fundamentals
3. **Risk Control**: Even if undervalued, consider systemic risk and position management
4. **Information Sources**: Prioritize official disclosures, cross-verify data accuracy
5. **Independent Judgment**: Valuation analysis for reference only, not investment advice

---

## References

Detailed valuation models, calculation formulas, and case studies available in the `references/` directory.
