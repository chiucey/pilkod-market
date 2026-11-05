# PEG Valuation Calculation Reference Guide

## PEG Indicator Definition

**PEG = Price-to-Earnings Ratio (PE) / Profit Growth Rate (G)**

- PEG < 1: Stock may be undervalued
- PEG = 1: Stock is fairly priced
- PEG > 1: Stock may be overvalued

## Core Calculation Formulas

### 1. P/E Ratio (PE) Calculation
```
PE = Current Price / Earnings Per Share (TTM)
```

### 2. Profit Growth Rate (G) Calculation
```
G = (Current Year Profit - Last Year Profit) / |Last Year Profit| × 100%
```

### 3. PEG Calculation
```
PEG = PE / G
```

## Profit Growth Rate Selection Rules (Danbin Method)

**Key Principle**: Use the minimum 3-year non-GAAP net profit growth rate

```
G = min(This Year Non-GAAP Growth, Last Year Non-GAAP Growth, Year Before Last Non-GAAP Growth)
```

### Example Calculation

Assuming company data:
| Year | Non-GAAP Net Profit | Growth Rate |
|------|---------------------|-------------|
| 2024 | 10 Bn | 25% |
| 2023 | 8 Bn | 15% |
| 2022 | 6 Bn | 40% |

**Use 3-year minimum growth rate**: G = min(25%, 15%, 40%) = 15%

**PEG Calculation**:
- Current PE = 30x
- PEG = 30 / 15 = 2.0

**Judgment**: PEG = 2.0 > 1, valuation is expensive

## Valuation Judgment Standards

| PEG Range | Valuation Judgment | Investment Recommendation | Action |
|-----------|-------------------|--------------------------|--------|
| PEG < 0.5 | Extremely Undervalued | Strongly Recommend | Can heavy position |
| 0.5 <= PEG < 1 | Relatively Undervalued | Recommend Buy | Can build position |
| 1 <= PEG < 1.5 | Basically Fair | Observe | Light position |
| 1.5 <= PEG < 2 | Slightly Overvalued | Cautious | Not recommended to chase |
| PEG >= 2 | Overvalued | Not Recommended | Clear position/Avoid |

## Special Case Handling

### 1. Negative Growth Rate
- If minimum growth rate is negative, PEG is negative
- Handling: Use absolute value for calculation, but need additional analysis of profit decline reasons
- Recommendation: Be cautious with companies having negative growth

### 2. Zero Growth Rate
- If growth rate is 0, PEG calculation is meaningless
- Handling: Mark as "Unable to value", need other indicators for comprehensive assessment

### 3. Negative PE
- If company is losing money, PE is negative
- Handling: Cannot use PEG, need to use PB, PS and other indicators

### 4. Cyclical Industries
- Cyclical industries have volatile profits
- Recommendation: Use cycle-adjusted PE or industry-specific indicators

## Data Sources

### Financial Data
1. **Official Reports**: Company annual reports, quarterly reports
2. **Exchange Websites**: Shanghai Stock Exchange, Shenzhen Stock Exchange disclosure platforms
3. **Data Platforms**: Eastmoney, Tonghuashun, iFinD

### Non-GAAP Net Profit
- Non-GAAP Net Profit = Net Profit - Non-recurring Gains and Losses
- Non-recurring items include: Government subsidies, Asset disposal gains, Investment income, etc.
- Non-GAAP Net Profit better reflects company's real operating capability

## Precautions

1. **Single Indicator Limitation**: PEG is just one valuation method, need comprehensive judgment with other indicators
2. **Industry Differences**: Different industries have different reasonable PEG levels
3. **Growth Assessment**: Need to analyze whether growth is sustainable
4. **Data Quality**: Ensure data used is accurate and reliable
