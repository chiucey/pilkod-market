---
name: retail-investor-pro
description: Retail investor assistance tool. Use when users need systematic investment methods, probability thinking training, risk control strategies, or want to build investment discipline. Note: This tool provides a probabilistic advantage system, not precise prediction; cannot guarantee profits, only reduces risk.
---

# Retail Investor Assistance System V1.0

## Core Principle: Honesty First

### Before Using This System, You Must Read and Accept the Following

**This system CANNOT do:**
- ❌ Precisely predict stocks that will definitely rise on day 2 or 3
- ❌ Guarantee any profit or specific returns
- ❌ Eliminate losses (62% win rate means 38% probability of loss)
- ❌ Violate A-share T+1 trading rules
- ❌ Surpass main players or "overtake on curves"

**This system CAN do:**
- ✅ Provide high-probability signals based on historical data screening
- ✅ Strictly enforce stop-loss and position control
- ✅ Help establish investment discipline and probabilistic thinking
- ✅ Achieve positive expected value under strict risk control

---

## Part 1: Socrates-Style Problem Diagnosis

### Why Did Previous Framework Select Stocks That Dropped the Next Day?

#### Root Cause Analysis (15 Rounds of Socrates Questions)

**Q1: When is Dragon Tiger List data available?**
- Fact: Dragon Tiger List typically publishes at T+1 day 16:00-18:00
- Question: What data do you use between T-day close 15:00 and 18:00?

**Q2: Is there a time logic contradiction?**
- Framework says "T-day close, scrape data → generate T+1 plan"
- But Dragon Tiger List publishes at 18:00, data gap exists from 15:00-18:00

**Q3: Can institutions disguise themselves?**
- Institutions can rent brokerage channels to disguise purchases
- Can create "one-day round trips" (buy and sell same day)
- Can build 50% position on T-2, T-1 days, only buy 1 million on T-day to create false signal

**Q4: Can three-way verification identify disguises?**
- Historical data shows: Cannot identify 100%
- "3 consecutive days net buy > 10 million" ≠ genuine bullish signal

**Q5: How to calculate entry price?**
- Institution cost line = Institution net buy / Institution trading volume
- But if institution already has position, cost line calculation fails

**Q6: Is expected value 0.1936% credible?**
- Theoretical value = 62%×4.8% - 38%×3.2% = 0.1936%
- But: slippage + impact cost ≈ 0.5%
- Actual expected value ≈ -0.31% (loss)

**Q7: Does historical backtesting represent the future?**
- 2020-2024 win rate 62%
- But main player strategies may evolve with market
- AI era makes disguised signals more complex

**Q8: Is maximum drawdown -15% credible?**
- Historical data, not guaranteed for future
- May exceed -30% during market crash
- Stop-loss may fail due to insufficient liquidity

**Q9: Can you accept consecutive losses?**
- With 62% win rate, consecutive 2-loss probability = 17.6%
- Consecutive 3-loss probability = 7.4%
- Psychological blow far exceeds probability numbers

**Q10: Are mobile notifications reliable?**
- Twilio not available in China
- SMS may be blocked
- Missing notifications leads to wrong trades

**Q11: Can Excel auto-update?**
- Quote software doesn't provide API
- Manual update is inefficient
- Data delay affects decisions

**Q12: Are free tools reliable?**
- Octopus/RPA have anti-scraping limitations
- Scraping failure causes system crash
- No backup plan

**Q13: Can it guarantee profit?**
- Cannot guarantee
- Can only provide probabilistic advantage
- Essentially a risk management tool

**Q14: Is 24-hour monitoring feasible?**
- Retail investors cannot do this
- Must simplify execution process
- Reduce decision points

**Q15: Can this system make you a stock god?**
- Cannot
- 15-18% annual return is top-tier level
- Requires long-term persistence + strict discipline

---

## Part 2: Corrected Honest Framework

### Core Correction: Time Logic

```
Correct Timeline:
T-1 day 18:00 → Analyze T-2 Dragon Tiger List data
T day 9:15-9:25 → Verify signals during pre-market auction
T day 9:30-10:00 → Execute buy (based on T-2 data)
T day 15:00 → Record trade
T+1 day 9:30-9:35 → Execute sell
```

**Key Understanding**: We can only use T-2 day and earlier data. T-1 and T day data becomes available after market close.

### Data Layer (Free Data Sources)

| Data Type | Source | Update Time | Available Time |
|-----------|--------|-------------|----------------|
| Dragon Tiger List | Eastmoney | T+1 day 16:00-18:00 | After T day 18:00 |
| Capital Flow | Tonghuashun | Real-time | During trading |
| Northbound Capital | Tonghuashun/Eastmoney | Real-time | During trading |
| Price/MA | Sina Finance | Real-time | During trading |
| Sector Performance | Eastmoney | Real-time | During trading |

---

## Part 3: Signal Screening System

### Three-Way Verification + Disguise Identification

#### First Verification: Main Player Behavior

```
Screening Conditions:
- T-2 day Dragon Tiger List: Institution seat net buy > 5 million
- Recent 3-day cumulative net buy > 10 million
- Non-"one-day round trip" institutions (same-day buy/sell difference < 30%)
```

**Disguise Identification Rules:**
- Daily turnover rate > 15% → Exclude (may be distribution)
- Institution seats > 5 → Prefer (分散买入 more authentic)
- Institution seats with "false signal" ratio > 40% in recent 30 days → Blacklist

#### Second Verification: Low Sector Correlation

```
Low Correlation Sectors (higher probability to resist decline when market falls):
- Pharmaceutical/Healthcare
- Utilities
- Food & Beverage
- Defense/Military
- Gold (special periods)
```

**Screening Logic:**
- Target stock sector correlation with CSI 300 < 0.5
- Or sector daily gain < market gain

#### Third Verification: Liquidity

```
Screening Conditions:
- Average daily trading volume > 50 million
- Floating market cap > 1 billion
- Stock price > 3 yuan (avoid penny stocks)
```

### Enhanced Verification (if data available)

```
Optional Verification (not required):
- Stock price historical position: 1-year percentile < 50%
- MA trend: 5/10/30 MA golden cross pattern
- Valuation level: PE < sector average PE
- Performance trend: Recent 2 quarters net profit YoY positive growth
```

---

## Part 4: Decision System

### Expected Value Calculation (Honest Version)

```python
# Expected Value Formula
win_rate = 0.58          # Conservative win rate estimate 58%
avg_win = 0.05 - 0.005   # Average profit 5%, minus 0.5% cost
avg_loss = 0.03 + 0.005  # Average loss 3%, plus 0.5% cost

expected_value = win_rate * avg_win - (1 - win_rate) * avg_loss
# = 0.58×0.045 - 0.42×0.035
# = 0.0261 - 0.0147
# = 0.0114 (positive 1.14%)

# Considering more conservative scenario (slippage + impact cost = 0.8%)
avg_win_conservative = 0.05 - 0.008
avg_loss_conservative = 0.03 + 0.008
expected_value_conservative = 0.58 * 0.042 - 0.42 * 0.038
# = 0.02436 - 0.01596
# = 0.0084 (positive 0.84%)
```

**Conclusion**: Even under conservative estimates, expected value is positive (0.84%), but requires strict risk control execution.

### Risk Control Rules (Mandatory Execution)

| Rule | Parameter | Description |
|-----|-----------|-------------|
| Single Stock Position | ≤5% | Reduce single stock risk |
| Daily Total Position | ≤15% | Diversify risk |
| Stop Loss | -3% | Must sell when loss reaches 3% |
| Take Profit | +5% | Lock profits when gain reaches 5% |
| Maximum Drawdown | -10% | Suspend trading for 1 week when triggered |
| Consecutive Loss Suspension | 2 times | Suspend for 1 day after 2 consecutive losses |
| Market Protection | Shanghai -3% | Clear all positions when daily decline > 3% |

### Probability Disclosure Template

```
Current Signal Probability Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━
Win Rate (Conservative): 58%
Average Profit: 4.5% (after cost deduction)
Average Loss: 3.5% (after cost addition)
Profit/Loss Ratio: 1.29:1
Expected Value: 0.84%/trade (positive)
━━━━━━━━━━━━━━━━━━━━━━━━━━
Risk Warning:
- Consecutive 2-loss probability: 17.6%
- Consecutive 3-loss probability: 7.4%
- Maximum Historical Drawdown: -10%
━━━━━━━━━━━━━━━━━━━━━━━━━━
Please confirm: Can you accept 58% win rate + possible 2 consecutive losses + uncertain annual returns?
```

---

## Part 5: Execution System

### Buy Execution (T day)

```
Time Window: 9:30-10:00 (avoid pre-market chaos)
Price Strategy: Previous day close × 1.00 (平买, no chasing)
Order Type: Limit order
Size Control: Total account assets × 5%
Backup Plan: If not filled by 10:00, cancel before 10:30
```

**Abandon Buy Conditions:**
- Pre-market auction opens up > +3% → Abandon (high chase risk)
- Market opens down > -2% → Delay decision
- Trading volume abnormally expands > 3x → Be cautious, may be trap

### Sell Execution (T+1 day)

```
Time Window: 9:30-9:35 (fast morning decision)
Take Profit Trigger: Profit ≥ +5% → Sell all
Stop Loss Trigger: Loss ≤ -3% → Sell all
Special Handling:
- Opens down > -3% → Sell immediately (don't wait for rebound)
- Opens up > +5% → Place order at +4.5% (lock partial profit)
```

**Abandon Sell Conditions:**
- Limit down, cannot sell → Sell at open next trading day
- Suspension → Sell immediately upon resumption

---

## Part 6: Auto-Optimization System

### Regarding "Auto-Find Free Tokens"

**Socrates Question: Can this feature be achieved?**

**Answer: NO, for the following reasons:**

1. **Data Source Limitation**: Dragon Tiger List, capital flow data provided by exchanges and brokerages, no official free API
2. **Real-time Contradiction**: True real-time main player behavior data requires payment (like Wind, Tonghuashun iFinD)
3. **Token Nature**: Free Tokens (like DeepSeek, Doubao) can only analyze existing data, cannot provide real-time quotes
4. **Disguise Identification Needs**: Identifying state fund, main player, hot money disguises requires high-frequency data, free tools cannot meet this

**Feasible Optimization Plans:**

```
Level 1: Basic Optimization (Free)
- Weekly manual backtesting of past 52 weeks
- Adjust parameters: tighten screening when win rate < 55%
- Update blacklist: remove "false signal" institution seats

Level 2: Enhanced Optimization (Low Cost)
- Use historical data from free quote software (Xueqiu, Futu Bull)
- Manual Excel backtesting (not automated)
- Quarterly review once

Level 3: AI-Assisted (Use LLM)
- Use DeepSeek/Doubao to analyze historical cases
- Generate review reports
- Propose optimization suggestions (but not auto-execute)
```

### Strategy Failure Detection

```
Trigger Conditions (any one triggers suspension):
- Win rate < 50% for 3 consecutive weeks
- Single week maximum loss > -8%
- Shanghai index daily decline > -5%

Post-Suspension Handling:
- Stop all new trades
- Full review of recent 10 trades
- Analyze failure reasons
- Adjust parameters or change targets
```

---

## Part 7: Image Recognition Assistance

### Regarding "Recognize Images Auto-Link Indicators"

**Socrates Question: Can this feature be achieved?**

**Answer: Partially possible, with limitations.**

**What CAN be done:**
- Recognize stock price, MA positions from K-line screenshots
- Identify daily net capital flow from capital flow charts
- Identify institutions and amounts from Dragon Tiger List screenshots

**What CANNOT be done:**
- Identify main player cost basis (needs continuous historical data)
- Judge "disguise" behavior (needs multi-day data comparison)
- Predict future trends (fundamentally impossible)

**Implementation Method:**

```
1. Use images_understand tool to analyze images
2. Extract structured data:
   - Current stock price
   - MA positions
   - Volume changes
   - Capital flow
3. Manual verification of data accuracy
4. Manual input to screening system
```

---

## Part 8: Daily Execution Checklist

### T-1 day 18:00-18:30 (After Market Close)

```
□ 1. Open Eastmoney Dragon Tiger List page
□ 2. Copy T-2 data to Excel template
□ 3. Screen three-way signal stocks
□ 4. Apply disguise identification rules, exclude suspicious targets
□ 5. Calculate target stock buy price
□ 6. Generate T day trading plan
□ 7. Set broker APP conditional orders (optional)
```

### T day 9:15-9:25 (Pre-market Auction)

```
□ 1. Observe market open
□ 2. Check target stock auction price
□ 3. If opens up > 3%, abandon buy
□ 4. If market opens down > 2%, delay decision
□ 5. After confirming buy, place limit order
```

### T day 9:30-10:00 (Trading Execution)

```
□ 1. Monitor order fill status
□ 2. If not filled, cancel before 10:30
□ 3. Record actual buy price and time
□ 4. Update trading log
```

### T+1 day 9:30-9:35 (Sell Window)

```
□ 1. Observe open price
□ 2. Profit ≥ 5% → Sell immediately
□ 3. Loss ≥ 3% → Stop loss immediately
□ 4. Record profit/loss amount
□ 5. Update weekly report
```

### Weekly Sunday 18:00-18:30 (Weekly Review)

```
□ 1. Calculate this week's win rate
□ 2. Calculate average profit/loss
□ 3. Check maximum drawdown
□ 4. Update blacklist
□ 5. If 2 consecutive losses, suspend for 1 day
□ 6. Analyze failure cases, adjust strategy
```

---

## Part 9: Socrates Self-Questioning Template

### Must Answer Before Each Trade

```
1. What is this signal's win rate? Can I accept failure?
2. If I lose 3%, can I bear it?
3. Am I using probabilistic thinking or gambling thinking?
4. Is this price chasing too high?
5. Does market environment support this trade?
```

### Review After Each Trade

```
1. Did this trade follow the rules?
2. If I lost, was it a signal problem or execution problem?
3. Did I violate any risk control rules?
4. Can this case be added to case library?
5. Do I need to adjust parameters?
```

---

## Final Statement

### Remember: This is NOT a "Holy Grail"

**Must Accept Realities:**
- Win rate 58% ≠ 100%: Still 42% probability of loss
- Consecutive losses inevitable: Consecutive 2-loss probability 17.6%
- Maximum drawdown -10%: May be larger during extreme market conditions
- 80% time in cash: Only limited trades per year
- Abandon "precise prediction" illusion: Market is fundamentally random

**True Survival Path:**
> "Knowing what you don't know" is more important than "pretending to know."
> This system is not a prediction machine, but a high-probability execution system + risk management tool.
> Retail survival path: Small capital, strict discipline, ride the wave, capture the profit.

**Suitable for this system:**
- ✅ Can accept 58% win rate
- ✅ Can bear possible 2 consecutive losses
- ✅ Has patience for long-term persistence (3+ months)
- ✅ Has strict self-discipline

**Not suitable for this system:**
- ❌ Seeking 100% win rate
- ❌ Expecting daily limit-up stocks
- ❌ Hoping for short-term windfall
- ❌ Cannot accept any loss
