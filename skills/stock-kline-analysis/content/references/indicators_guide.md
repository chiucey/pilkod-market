# Stock Technical Indicators Reference Guide

## 1. Risk Indicators

### 1.1 Annualized Volatility

**Formula**: `Volatility = STD(Daily Returns) × √252`

**Calculation Steps**:
1. Calculate daily returns: `Daily Return = (Today's Close - Yesterday's Close) / Yesterday's Close`
2. Calculate standard deviation (STD) of daily returns
3. Multiply by √252 (number of trading days per year) to get annualized volatility

**Interpretation**:
- Volatility < 20%: Low volatility, relatively controllable risk
- Volatility 20%-35%: Normal volatility
- Volatility 35%-50%: Moderately high volatility
- Volatility > 50%: High volatility, significant risk

**Use Cases**: Compare risk levels of different stocks, guide position sizing

---

### 1.2 Beta Coefficient

**Formula**: `Beta = COV(Stock Returns, Market Returns) / VAR(Market Returns)`

**Calculation Steps**:
1. Get stock daily return series
2. Get market benchmark daily return series (e.g., CSI 300 Index)
3. Calculate covariance between the two and market variance
4. Divide covariance by market variance to get Beta

**Interpretation**:
- Beta = 1: Stock volatility matches market
- Beta > 1: Stock volatility exceeds market (e.g., Beta=1.5 means if market rises 1%, stock may rise 1.5%)
- Beta < 1: Stock volatility less than market
- Beta < 0: Negatively correlated with market (rare)

**Use Cases**:
- Portfolio risk adjustment
- Hedge strategy design
- Systematic risk assessment

---

### 1.3 VaR (Value at Risk)

**Formula**: `VaR(95%) = Mean(Daily Returns) - 1.65 × STD(Daily Returns)`

**Interpretation**:
- Meaning: Maximum possible single-day loss at 95% confidence level
- VaR = -3%: 95% confident that single-day loss will not exceed 3%

**Use Cases**:
- Risk limit management
- Stop-loss strategy setting
- Capital adequacy assessment

---

## 2. Liquidity Indicators

### 2.1 Turnover Rate

**Formula**: `Turnover Rate = Trading Volume / Circulating Shares × 100%`

**Interpretation**:
- Turnover Rate < 2%: Trading is inactive, insufficient liquidity
- Turnover Rate 2%-5%: Normal level
- Turnover Rate 5%-10%: Relatively active
- Turnover Rate > 10%: Highly active, watch for speculation risk

**Use Cases**:
- Evaluate stock liquidity
- Identify highly speculative stocks
- Determine buy/sell timing

---

### 2.2 Turnover Amount Change Rate

**Formula**: `Turnover Change = (Today's Amount - Yesterday's Amount) / Yesterday's Amount × 100%`

**Interpretation**:
- Positive and continuously increasing: Rising investor attention, potential momentum
- Negative and continuously decreasing: Capital withdrawal, be cautious
- Sharp fluctuations: May be affected by significant events

---

### 2.3 Fund Flow

**Formula**: `Fund Flow = Active Buy Amount - Active Sell Amount`

**Simplified Estimate**: `Fund Flow ≈ Volume × Average Price × (Buy Ratio - 0.5)`

**Interpretation**:
- Sustained net inflow: Institutional/large capital accumulation signal
- Sustained net outflow: Institutional/large capital reduction signal
- Short-term fluctuations: May be affected by short-term factors, need trend confirmation

---

## 3. Valuation Indicators

### 3.1 P/E Ratio (PE)

**Formula**: `PE = Stock Price / Earnings Per Share (EPS)`

**Types**:
- Static PE: Using previous year's EPS
- Trailing PE (TTM): Using last 12 months EPS
- Forward PE: Using expected EPS

**Interpretation**:
- PE < 0: Loss-making company
- PE < 10: Possibly undervalued (need industry comparison)
- PE 10-25: Reasonable range
- PE 25-40: Moderately high
- PE > 40: High valuation

**Note**: Different industries have very different PE levels; compare with industry average

---

### 3.2 P/B Ratio (PB)

**Formula**: `PB = Stock Price / Book Value Per Share`

**Interpretation**:
- PB < 1: Stock price below book value, usually seen as undervalued
- PB = 1: Stock price equals book value
- PB > 3: Usually high valuation

**Best For**:
- Banks, insurance and other asset-heavy industries
- Bankruptcy liquidation valuation
- Value investing screening

---

### 3.3 Dividend Yield

**Formula**: `Dividend Yield = Dividend Per Share / Stock Price × 100%`

**Interpretation**:
- Dividend Yield > 5%: High dividend, strong defensive characteristics
- Dividend Yield 3%-5%: Good
- Dividend Yield 1%-3%: Normal
- Dividend Yield < 1%: Low dividend or no dividend

**Use Cases**:
- Value investing stock selection
- Retirement portfolio
- Investors needing cash flow

---

## 4. Comprehensive Scoring System

### Recommended Weights

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Risk Control | 40% | Volatility, Beta, VaR comprehensive assessment |
| Liquidity | 30% | Turnover rate, trading changes, fund flow |
| Valuation | 30% | PE, PB, dividend yield comprehensive assessment |

### Scoring Standards

| Comprehensive Score | Recommendation |
|---------------------|----------------|
| 75-100 | Strong Buy |
| 60-74 | Buy |
| 45-59 | Hold/Wait |
| 30-44 | Reduce Position |
| 0-29 | Sell |

---

## 5. Important Notes

1. **Data Timeliness**: Recommend using data from the past 3+ months for calculation
2. **Industry Differences**: Different industries have very different reasonable indicator ranges
3. **Market Environment**: Indicators may perform differently in bull/bear markets
4. **Single Indicator Limitations**: Should use multiple indicators for comprehensive judgment
5. **Combine with Fundamentals**: Technical analysis should be combined with fundamental analysis
