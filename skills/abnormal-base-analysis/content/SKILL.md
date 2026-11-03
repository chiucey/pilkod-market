---
name: abnormal-base-analysis
description: Analyze A-share stocks with daily gain >= 10%, trace back their abnormal base position (异动底仓) accumulation on daily chart, and identify the date range where the main capital built positions. This skill should be used when the user wants to find stocks that surged 10%+ today, and understand which daily timeframe the smart money accumulated positions before the breakout.
---

# A-Share Abnormal Base Position Analysis

## Overview
Analyze A-share stocks with daily gain >= 10%, trace back their abnormal base position (异动底仓) - the period when main capital built positions on the daily chart.

Typical pattern: **Base Building (volume spike) → Volume Contraction (washout) → Breakout (another volume spike limit up)**

Example: Yibo Technology (301366) on June 3, 2026 - base position concentrated during May 22-27, 2026, followed by volume contraction, then restarted on June 2.

## Trigger Conditions
Use this skill when user expresses:
- "Analyze today's limit-up stocks' base positions"
- "Help me find stocks that rose 10%+ today, what time did the base position concentrate"
- "Analyze XX stock's abnormal base position"
- "When did the main capital build positions for limit-up stocks"
- A-share abnormal base position related queries

## Analysis Workflow

### 1. Run Analysis Script
Execute analysis using `scripts/analyze.py`:
```bash
python scripts/analyze.py [options]
```

**Options**:
| Option | Description | Example |
|--------|-------------|---------|
| `--output`, `-o` | Output format: text/json/html (default: text) | `--output html` |
| `--threshold`, `-t` | Gain threshold (default: 9.9%) | `--threshold 10.0` |
| `--max-stocks`, `-m` | Max stocks to analyze (0=all, default: 0) | `--max-stocks 20` |

**Common Commands**:
```bash
# Analyze all stocks with gain >= 10% today (text output)
python scripts/analyze.py
# Output HTML report and preview
python scripts/analyze.py --output html
# Analyze top 20 only, JSON output
python scripts/analyze.py --max-stocks 20 --output json
# Lower threshold (e.g., >= 5%)
python scripts/analyze.py --threshold 5.0 --max-stocks 10
```

**Note**: Script requires network access to external APIs. In sandbox environment, use `dangerouslyDisableSandbox` to run.

### 2. Interpret Analysis Results
Script output contains:
- **Base Position Range**: Date range of main capital position building
- **Volume Ratio**: Base period volume relative to 60-day average (1.3x+ = significant volume)
- **Volume Contraction**: Volume contraction period after base building
- **Confidence Score**: 0-100, comprehensive evaluation of base position signal quality

### 3. Summarize for User
After generating HTML report, use `preview_url` to display. Provide text summary:
- Total number of stocks with gain >= 10%
- How many detected base positions
- Top 5 by confidence with brief description
- For typical stocks (confidence > 70), briefly describe complete path: base building → contraction → breakout

## Analysis Algorithm

### Base Position Cluster Detection
Look backward from breakout day (gain >= 10% day), find continuous trading day clusters with abnormal volume:
1. Calculate 60-day moving average of volume as baseline
2. Mark day as "volume spike day" when volume >= 1.3x baseline
3. Continuous volume spike days (allowing 1 day of slight contraction) form a base position cluster
4. Cluster must contain at least 2 trading days to be included

### Volume Contraction Detection
Period between end of base cluster and breakout day:
- Calculate average volume ratio to baseline for this period
- Ratio <= 0.7 = "typical volume contraction", indicating thorough washout

### Multi-Cluster Scoring
A stock may detect multiple base clusters. Score each cluster across multiple dimensions and select the best as "main base position".

### Three Yangs Control Three Yins Analysis (Source: "股是股非")
Within base cluster, analyze relationship between yang volume (total volume on up days) and yin volume (total volume on down days):
- Yang volume > 1.5x Yin volume → Three yangs control three yins qualified
- Yang volume < Yin volume → Weak volume pattern, insufficient main capital control

### Ice Volume Detection (Source: "股是股非")
Detect volume shrinkage to extremely low levels at end of contraction period:
- **Ice Volume**: During contraction period, daily volume shrinks to below 30% of MA60, indicating selling pressure exhausted
- **Sudden Extreme Ice**: First down day after base cluster ends, volume drops to below 30% of base cluster average, indicating main capital locked in

### Good Position Evaluation (Source: "股是股非")
Evaluate whether base position is in favorable position:
- **MA Alignment**: Closing price on base start day within MA60 ± 5%, indicating solid price center
- **Above Support**: Base start price above 20-day low, with support protection
- **MA90 Trend**: 90-day moving average up/flat/down, determine medium-long term trend direction

### Washout Pattern Classification (Source: "股是股非")
Classify washout patterns for contraction period:
- **Not Broken Then Risen**: Contraction period low not broken below base cluster low, mild washout
- **Broken Then Risen**: Contraction period broke below base cluster low then rebounded, thorough washout
- **Big Wash**: Contraction > 10 days
- **Small Wash**: Contraction 3~10 days
- **Micro Wash**: Contraction < 3 days

## Confidence Scoring System
Full score 100 points, 9 dimensions comprehensive scoring:

| Dimension | Max Score | Description |
|-----------|-----------|-------------|
| Volume Spike Intensity | 15 | Higher volume ratio better, >=3x = full score |
| Cluster Days | 10 | 3-8 days optimal building period |
| Days to Breakout | 15 | 1-5 days optimal, farther = deduction |
| Contraction Quality | 10 | Lower volume ratio better, <=0.5x = full score |
| Price Mildness | 5 | Smaller gain/loss in base period better |
| Three Yangs Control Three Yins | 10 | Yang/yin >=2.0 full score, >=1.5 gets 7 points |
| Ice Volume Detection | 15 | Ice volume +8, sudden extreme ice +7 |
| Good Position Evaluation | 10 | MA alignment +5, above support +5 |
| Washout Pattern | 10 | Not broken then risen +6, big wash +4 |

## Data Source
- East Money (东方财富) quotes interface (unofficial, free public)
- Covers all A-shares on Shanghai, Shenzhen, Beijing exchanges
- Daily K-line data (adjusted forward)

### Volume-Price Analysis Theory Source
New dimensions (Three Yangs Control Three Yins, Ice Volume/Sudden Extreme Ice, MA Alignment, Washout Pattern Classification) sourced from "股是股非" series volume-price analysis system.

Reference documents:
- "股是股非" e-book series (1, 2, 3, 猎取暴涨股)
- "主力洗震逼路径及图表模式"
- "三阳控三阴（系列新编版2026年）"
- "在好位置异动或异动形成好位置"

## Notes
- Requires network connection, 500ms interval to avoid rate limiting
- Analyzing large number of stocks takes time (~0.5-1 second per stock)
- 60-day average volume requires at least 60 trading days of historical data
- Recent IPO stocks (less than 60 days) may have inaccurate analysis
- This analysis is for research reference only, not investment advice