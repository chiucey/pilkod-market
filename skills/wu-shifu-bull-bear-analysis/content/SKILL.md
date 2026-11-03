---
name: wu-shifu-bull-bear-analysis
description: >
  吴师傅牛熊分析：量化框架，通过多维度技术指标识别和确认牛熊市状态。
  Use this skill whenever the user asks to assess market conditions, identify the
  current market phase, determine whether a market is bullish or bearish, score a
  market's trend strength, evaluate regime change signals, or build/apply any scoring
  system for trend confirmation. Trigger this skill when the user mentions phrases like
  "分析牛熊", "判断市场状态", "现在是牛市还是熊市", "is this a bull/bear market",
  "what's the market regime", or asks to evaluate any index, stock, or asset for trend
  status. Always use this skill in combination with any multi-timeframe technical
  analysis workflow.
---

# 吴师傅牛熊分析 (Wu Shifu Bull & Bear Market Analysis)

A rigorous, multi-dimensional technical scoring system for objectively classifying
market regimes. Inspired by Stan Weinstein's Stage Analysis, IBD Market School,
and USIC champion methodologies (Oliver Kell, Marios Stamatoudis, et al.).

---

## Core Philosophy

> No single indicator defines a market regime. Professional traders use **layered
> confirmation** across structure, trend, momentum, volume, and breadth.
> The goal is to reduce subjectivity and act on evidence, not narrative.

---

## Dimension 1 — Price Structure (Most Fundamental)

**Logic**: Raw price action defines trend before any indicator can.

```
Bull Market Structure:
  → Higher Highs (HH) + Higher Lows (HL) in sequence
  → Each swing high exceeds the prior swing high
  → Each pullback low holds above the prior pullback low
  → Quantification: Require ≥3 consecutive HH + HL to confirm uptrend

Bear Market Structure:
  → Lower Highs (LH) + Lower Lows (LL) in sequence
  → Each rally fails below the prior swing high
  → Each decline breaks below the prior swing low
  → Quantification: Require ≥3 consecutive LH + LL to confirm downtrend

Transition / Neutral:
  → Mixed signals (e.g. HH but LL, or LH but HL)
  → Treat as range-bound until structure resolves
```

**Scoring**: +1 (bull structure) / 0 (neutral) / -1 (bear structure)

---

## Dimension 2 — Moving Average System (Trend Core)

**Recommended MAs**: 10, 21, 50, 150, 200-day EMA/SMA

### 2a. Price vs. 200-Day MA

| Condition                              | Score |
|----------------------------------------|-------|
| Price clearly above 200-day MA         | +1    |
| Price near / choppy around 200-day MA  |  0    |
| Price clearly below 200-day MA         | -1    |

### 2b. 200-Day MA Slope

| Condition                   | Score |
|-----------------------------|-------|
| 200-day MA sloping upward   | +1    |
| 200-day MA flat             |  0    |
| 200-day MA sloping downward | -1    |

### 2c. MA Alignment (Stack Order)

| Condition                                          | Score |
|----------------------------------------------------|-------|
| Bullish stack: 10 > 21 > 50 > 150 > 200            | +1    |
| Partial alignment or mixed                         |  0    |
| Bearish stack: 10 < 21 < 50 < 150 < 200           | -1    |

### Stan Weinstein Stage Filter (Weekly Chart)

```
Use 30-week MA (≈150-day MA) on weekly chart as the primary stage filter:

  Stage 2 (Mark-Up / Bull):   Price > rising 30-week MA     → Confirm long bias
  Stage 3 (Top / Transition):  Price near flat 30-week MA    → Reduce exposure
  Stage 4 (Mark-Down / Bear):   Price < declining 30-week MA → No new longs

This is the single most powerful weekly filter before any lower-timeframe analysis.
```

---

## Dimension 3 — Momentum Indicators

### 3a. RSI (14-period) — Bull/Bear Zone Theory

> Based on Constance Brown's RSI Range Shift model. More useful than
> traditional overbought/oversold interpretation.

```
Bull Market RSI Behavior:
  → RSI oscillates in the 40–80 zone
  → Pullbacks hold above 40 (demand zone)
  → Readings above 70 are sustainable, not automatic sell signals
  → Score: +1 if RSI midpoint (average over last 20 bars) > 50

Bear Market RSI Behavior:
  → RSI oscillates in the 20–60 zone
  → Rallies fail below 60 (supply zone)
  → Readings below 30 are sustainable, not automatic buy signals
  → Score: -1 if RSI midpoint < 50

Regime Change Signal:
  → RSI center of gravity shifting from above-50 to below-50 = early bear warning
  → RSI center of gravity shifting from below-50 to above-50 = early bull recovery
```

### 3b. MACD (12/26/9) — Zero-Line Context

| Condition                                              | Score |
|--------------------------------------------------------|-------|
| MACD line + signal line both above zero, histogram +  | +1    |
| Mixed (one above, one below zero)                     |  0    |
| MACD line + signal line both below zero, histogram -  | -1    |

**Critical distinction**:
- Bullish crossover **above zero** = strong bull signal
- Bullish crossover **below zero** = weak relief rally only, not trend change

---

## Dimension 4 — Volume Structure

**Logic**: Volume is the fuel. Trend without volume confirmation is fragile.

```
Bull Market Volume Profile:
  ✅ Up-volume days > Down-volume days (track weekly ratio)
  ✅ Breakouts to new highs accompanied by above-average volume
  ✅ Pullbacks occur on declining volume (healthy consolidation)
  ✅ Accumulation Days > Distribution Days over any 4-week window

Bear Market Volume Profile:
  ❌ Down-volume days > Up-volume days
  ❌ Breakdowns below support on high volume (selling conviction)
  ❌ Counter-trend rallies on low volume (no real demand)
  ❌ IBD Distribution Count: ≥5 distribution days in 4 weeks = market under pressure
```

**Scoring**: +1 (bullish volume profile) / 0 (neutral) / -1 (bearish volume profile)

**Distribution Day Definition (IBD)**:
> A distribution day = index falls ≥0.2% on volume higher than the prior session.
> Cluster of 4–5 distribution days within a few weeks = institutional selling = bear warning.

---

## Dimension 5 — Market Breadth (Leading / Institutional-Grade)

**Logic**: Breadth leads price. Divergences warn of regime change before it happens.

| Indicator                        | Bull Condition                              | Bear Condition                              |
|----------------------------------|---------------------------------------------|---------------------------------------------|
| Advance/Decline Line             | A/D Line making new highs with price        | A/D Line diverging (lagging) from price     |
| 52-Week New Highs vs. New Lows   | New Highs >> New Lows (ratio > 3:1)         | New Lows >> New Highs (ratio > 3:1)        |
| % of Stocks Above 200-day MA     | > 60% of constituents above 200-day MA      | < 40% of constituents above 200-day MA       |
| % of Stocks Above 50-day MA      | > 60% above 50-day MA                       | < 40% above 50-day MA                       |
| McClellan Oscillator             | Persistently positive                       | Persistently negative                       |

**Breadth Divergence Warning**:
```
If index makes new ATH but A/D Line does NOT confirm → Distribution likely
If index makes new low but A/D Line holds higher → Potential exhaustion of selling
```

**Scoring per breadth indicator**: +1 / 0 / -1 (average the sub-scores for Dimension 5)

---

## Master Scoring System

Apply each dimension and sum the scores.

```
┌────────────────────────────────────────────┬───────────────┬───────┐
│ Dimension                                  │ Weight        │ Score │
├────────────────────────────────────────────┼───────────────┼───────┤
│ 1. Price Structure (HH/HL vs LH/LL)       │ Core (×1)     │ ±1    │
│ 2a. Price vs 200-day MA                   │ Core (×1)     │ ±1    │
│ 2b. 200-day MA Slope                      │ Core (×1)     │ ±1    │
│ 2c. MA Stack Alignment                    │ Secondary (×1)│ ±1    │
│ 3a. RSI Zone (center of gravity vs 50)    │ Secondary (×1)│ ±1    │
│ 3b. MACD vs Zero Line                     │ Secondary (×1)│ ±1    │
│ 4. Volume Structure                       │ Secondary (×1)│ ±1    │
│ 5. Market Breadth (avg of sub-indicators) │ Leading (×1) │ ±1    │
├────────────────────────────────────────────┼───────────────┼───────┤
│ TOTAL                                      │               │ ±8    │
└────────────────────────────────────────────┴───────────────┴───────┘
```

### Score Interpretation Table

| Score | Regime Label         | Tactical Stance                                          |
|-------|----------------------|----------------------------------------------------------|
| +7/+8 | **Strong Bull**      | Full long exposure. Offense mode. Ride leaders.          |
| +5/+6 | **Bull**             | Active long bias. Be selective. Manage stops.            |
| +3/+4 | **Mild Bull / Chop** | Reduced size. Favor only highest-quality setups.         |
| +1/+2 | **Neutral / Caution**| Minimal exposure. No new longs. Preserve capital.         |
| -1/0  | **Transition**       | Defensive. Hedge or raise cash. Watch for break.         |
| -3/-2 | **Mild Bear**        | No new longs. Short setups or cash only.                 |
| -5/-4 | **Bear**             | Short bias appropriate. Tight risk management.           |
| -7/-6 | **Strong Bear**      | Fully defensive. Max cash. Only short the weakest names. |

---

## Timeframe Application Matrix

```
┌──────────────────┬──────────────────────────────────────────┬────────────────────┐
│ Trader Type      │ Primary Indicators to Score             │ Review Cadence     │
├──────────────────┼──────────────────────────────────────────┼────────────────────┤
│ Long-term Invest │ 200-day MA + 30-week MA + A/D Line      │ Weekly             │
│ Swing Trader     │ 50/200 MA + RSI zone + MACD zero + Breadth│ Daily             │
│ Day Trader       │ EMA(9/21/50) + VWAP + Intraday structure │ Hourly (with daily│
│                  │                                           │ as filter)         │
└──────────────────┴──────────────────────────────────────────┴────────────────────┘

Rule: Always score the HIGHER timeframe first.
      Lower timeframe signals are only valid when aligned with higher timeframe regime.
```

---

## Usage Instructions

When this skill is triggered:

1. **Identify the asset and timeframe** the user is asking about.
2. **Collect or request relevant data points**: current price, MA values, RSI, MACD,
   volume trend, and breadth data if available (for indices).
3. **Score each of the 8 dimensions** explicitly. Show your working.
4. **Sum the scores** and map to the interpretation table.
5. **State the regime** clearly: "Based on this scoring, [ASSET] is currently in a
   [REGIME LABEL] condition with a score of [X/8]."
6. **Identify the 1–2 weakest dimensions** that could flip the score — these are the
   key risk factors to watch.
7. **If the user requests a chart**, generate Python code using `mplfinance` and
   `matplotlib` to visualize the MA stack, RSI zone, and MACD on a multi-panel chart.
   Annotate key support/resistance and the scoring rationale.

### Output Format Template

```
## Market Regime Assessment: [ASSET] ([TIMEFRAME])

**Overall Score: [X] / 8 → [REGIME LABEL]**

| Dimension                  | Reading                        | Score |
|----------------------------|--------------------------------|-------|
| 1. Price Structure         | [HH/HL or LH/LL description] | ±1    |
| 2a. Price vs 200 MA        | [Above/Below/Near]            | ±1    |
| 2b. 200 MA Slope           | [Rising/Flat/Declining]       | ±1    |
| 2c. MA Stack               | [Bull/Neutral/Bear stack]    | ±1    |
| 3a. RSI Zone               | [Center of gravity vs 50]    | ±1    |
| 3b. MACD vs Zero           | [Above/Straddling/Below]      | ±1    |
| 4. Volume Structure        | [Accum/Neutral/Distribution] | ±1    |
| 5. Breadth                 | [A/D, NH/NL, % above MA]      | ±1    |

**Tactical Stance**: [1–2 sentence action implication]

**Key Risk to Watch**: [The 1–2 dimensions closest to flipping]
```

---

## Important Limitations

- This framework is **educational and analytical**. It is not a mechanical trading
  system and does not generate buy/sell signals automatically.
- Scores can lag during sharp regime transitions (flash crashes, sudden macro shocks).
- Breadth data (A/D Line, NH/NL) is most relevant for broad **market indices**
  (S&P 500, Nasdaq, etc.). For individual stocks, focus on Dimensions 1–4.
- Always cross-reference with **fundamental context** (earnings cycle, macro regime,
  sector rotation) before acting on the technical score.

> ⚠️ **Disclaimer**: All analysis produced using this framework is for educational
> and reference purposes only. This is not financial advice. Trading involves risk.
> You are solely responsible for your own trading decisions.
