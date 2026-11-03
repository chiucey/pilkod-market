---
name: multi-paradigm-investment-analysis
description: Multi-paradigm investment decision analysis. Used when users request stock analysis from different investment masters' perspectives, simulating independent decisions from 11 top investors, comparing value/quantitative/macro/allocation methodologies. Triggers include: "analyze this stock", "multi-investor decision", "investment master perspective", "different style analysis".
---

# Multi-Paradigm Investment Decision System

Simulate independent investment decisions from 11 top investors on the same investment target.

## Input

User provides investment target (company name, stock ticker, or asset type).

## Execution Flow

### Step 1: Data Acquisition

Use the following tools to gather investment target data:

- `stocks_info` - Get company basics (PE, ROE, dividend yield, etc.)
- `stocks_financial_data` - Get financials (revenue, profit, cash flow, debt)
- `stocks_news` - Get latest news and catalysts
- `stocks_statistics` - Get valuation metrics and market data

### Step 2: Independent Decision Analysis

Analyze each investor in the following order. **Each analysis must be independent and MUST NOT borrow logic from other investors.**

#### Analysis Framework (by Investor)

| Investor | Analysis Dimensions | Participation Criteria |
|----------|---------------------|------------------------|
| Warren Buffett | Moat/Management/ROIC/Cash Flow/Valuation | Understandable stable business + economic moat |
| 段永平 (Duan Yongping) | Simplicity/Sustained Profit/Management/Conviction | Simple business + long-term profitability |
| Jim Simons | Signal Strength/Stability/Cost/Capacity | Quantifiable signals exist |
| George Soros | Expectation Gap/Liquidity/Policy/Catalyst | Macro mismatch + reflexivity |
| Stanley Druckenmiller | Liquidity/Cycle/Expectation Gap/Position | Clear trend + catalyst |
| Ray Dalio | Growth/Inflation/Policy/Portfolio | Can fit into macro framework |
| David Swensen | Asset Role/Premium/Correlation | Has allocation value |
| Howard Marks | Cycle/Sentiment/Risk Premium | Cycle mismatch |
| John Bogle | Cost/Diversification/Long-term | Index investing |
| Peter Lynch | Growth/PEG/Industry/Cognition | Understandable growth stock |
| Joel Greenblatt | EY/ROIC/Catalyst | Valuation mismatch/special situation |

### Step 3: Output Format

Each investor analysis must include:

```
=== [Investor Name] ===

Decision Variables: [List key variables this investor focuses on]

Participation: [✅ Participate / ⚠️ Conditional / ❌ Do Not Participate]

Analysis: [300-500 words independent analysis based on data and investment philosophy]

Conclusion: [Clear actionable recommendation]

Confidence: [★ 1-5 stars + percentage]
```

### Step 4: Divergence Summary

After all analyses, output:

1. **Core Divergence 1**: Is valuation reasonable?
2. **Core Divergence 2**: Impact of AI/innovation strategy
3. **Core Divergence 3**: Impact of macro environment

Finally, output a **Decision Matrix Table** (Investor | Decision | Confidence | Core Rationale)

## Key Constraints

1. **Independence**: Each investor analysis must be independent, no cross-referencing
2. **Method Diversity**: Must reflect different methodologies (quant/macro/value/allocation)
3. **Non-Participation Rule**: If criteria not met, output "明确不参与 + reason" (clearly do not participate + reason)
4. **No Fabrication**: Do not fabricate specific historical quotes, only analysis based on data
5. **No Summary**: Do not output aggregated conclusions, maintain independence

## Notes

- If user does not provide investment target, ask for input
- Use real market data, no simulated data
- Confidence reflects analysis certainty, not recommendation strength
