# Detailed Valuation Methods Guide

## DCF (Discounted Cash Flow) Model Deep Dive

### Free Cash Flow Calculation

```
Free Cash Flow (FCF) = Net Income + D&A - CapEx - Working Capital Change

Or:

FCF = EBIT × (1-Tax Rate) + D&A - CapEx - Working Capital Change
```

### WACC Calculation

```
WACC = Re × E/(E+D) + Rd × (1-T) × D/(E+D)

Where:
- Re = Cost of Equity = Rf + β × (Rm - Rf)
- Rf = Risk-free rate (Treasury yield)
- β = Beta coefficient
- Rm = Expected market return
- Rd = Cost of debt
- T = Tax rate
- E = Equity market value
- D = Debt market value
```

### Terminal Value Calculation

**Perpetual Growth Model:**
```
TV = FCFn × (1+g) / (WACC - g)
```

**Exit Multiple Model:**
```
TV = EBITDn × Exit Multiple
TV = FCFn × Exit Multiple
```

### Sensitivity Analysis Example

| WACC \ Perpetual Growth | 2% | 3% | 4% | 5% |
|------------------------|-----|-----|-----|-----|
| 8% | $45.2 | $52.8 | $63.5 | $80.2 |
| 9% | $38.1 | $43.5 | $51.2 | $62.8 |
| 10% | $32.8 | $36.9 | $42.5 | $51.0 |
| 11% | $28.5 | $31.6 | $35.8 | $42.2 |

---

## Relative Valuation Deep Dive

### PE Valuation Method

**Applicable Scenarios:**
- Companies with stable profitability
- Low-cyclicality businesses
- Comparable with industry peers

**Calculation:**

```
Fair PE = Historical Average PE × (Expected Growth / Historical Growth) × (1+Risk Premium)

Or Industry Comparison:
Fair Price = Industry Average PE × Expected EPS
```

**PE Reference by Industry:**

| Industry | Fair PE Range | Notes |
|----------|---------------|-------|
| Banking | 5-10x | Stable earnings but affected by macro |
| Consumer | 20-35x | Brand premium, stable growth |
| Healthcare | 25-45x | High R&D barrier, strong growth |
| Technology | 30-60x | High growth, valuation premium |
| Cyclical | 8-15x | High earnings volatility |

### PB Valuation Method

**Applicable Scenarios:**
- Financial industry (banking, insurance, securities)
- Asset-heavy industries
- Cyclical industries
- Loss-making companies

**Calculation:**

```
Fair PB = Industry Average PB × ROE Adjustment × Growth Adjustment

Where:
ROE Adjustment = Company ROE / Industry Average ROE
Growth Adjustment = (1+Expected Growth) / (1+Industry Growth)
```

### EV/EBITDA Valuation

**Formula:**

```
EV = Equity Market Cap + Net Debt + Minority Interest + Preferred Stock

EBITDA = EBIT + Depreciation + Amortization

EV/EBITDA = Enterprise Value Multiple
```

**Applicable Scenarios:**
- Capital-intensive businesses
- Cross-border comparisons
- M&A valuation reference

---

## Chip Distribution Analysis Deep Dive

### Cost Distribution Calculation

**Volume-Weighted Average Cost:**

```
Average Cost = Σ(Close Price × Volume) / ΣVolume

90% Cost Range = [Cost 10th percentile, Cost 90th percentile]
50% Cost Range = [Cost 25th percentile, Cost 75th percentile]
```

### Major Player Behavior Quantification

**Control Degree Indicator:**

```
Control Degree = (60-Day High Count - 60-Day Low Count) / Total Trading Days × 100%

Interpretation:
- >30%: Highly controlled
- 10%-30%: Lightly controlled
- <10%: No significant control
```

**Accumulation Signal Quantification:**

```
Accumulation Signal = Volume > 1.5x Average + Price Stable + Narrow Range
```

---

## Financial Metrics Quick Reference

### Profitability Metrics

| Metric | Formula | Excellent | Good | Poor |
|--------|---------|-----------|------|------|
| Gross Margin | (Revenue-COGS)/Revenue | >40% | 20-40% | <20% |
| Net Margin | Net Income/Revenue | >15% | 5-15% | <5% |
| ROE | Net Income/Equity | >20% | 10-20% | <10% |
| ROA | Net Income/Total Assets | >10% | 5-10% | <5% |
| ROIC | EBIT(1-T)/Invested Capital | >15% | 8-15% | <8% |

### Growth Metrics

| Metric | Excellent Standard | Good Standard |
|--------|-------------------|--------------|
| Revenue Growth | >20% | 10-20% |
| Net Income Growth | >25% | 10-25% |
| 3-Year CAGR | >20% | 10-20% |

### Financial Health Metrics

| Metric | Safe | Warning | Danger |
|--------|------|---------|--------|
| Current Ratio | >2.0 | 1.5-2.0 | <1.5 |
| Debt-to-Asset | <50% | 50-70% | >70% |
| Interest Coverage | >5x | 3-5x | <3x |
| Op CF/Net Income | >1.2 | 0.8-1.2 | <0.8 |

---

## Valuation Report Example

### Example: Kweichow Moutai Valuation Analysis (For Reference Only)

**Company Overview:**
- Main Business: Premium baijiu production and sales
- Industry Position: Leading baijiu company
- Core Competence: Brand moat, pricing power

**Financial Data (Assumed):**
- 2023 Revenue: 1,400 billion RMB
- 2023 Net Income: 750 billion RMB
- 5-Year Net Income CAGR: 15%
- Current PE: 35x
- Current Price: 1,800 RMB

**Valuation Analysis:**

1. **PE Relative Valuation:**
   - Industry Average PE: 30x
   - Brand Premium Adjustment: +20%
   - Fair PE: 36x
   - Fair Price: 36 × (750/Current Shares) ≈ 1,850 RMB

2. **DCF Valuation (Simplified):**
   - Perpetual Growth Assumption: 5%
   - WACC: 9%
   - Intrinsic Value Range: 1,600-2,200 RMB

3. **Valuation Conclusion:**
   - Current price near fair value upper limit
   - Historical PE at above-median level
   - Recommendation: Hold, wait for pullback to below 1,500 to add

---

## Risk Adjustments and Discounts

### Growth Discount

```
Market Cap Discount = 1 / (1 + Growth Uncertainty) × 100%

Higher uncertainty = Larger discount
```

### Liquidity Discount

```
Non-listed company liquidity discount: 20-30%
Restricted stock discount: 10-25% (depending on lock-up period)
```

### Control Premium

```
Listed company control premium: 20-40%
Minority shareholder discount: 10-20%
```
