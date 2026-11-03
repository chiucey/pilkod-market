# Financial Analysis Models Reference

This document defines built-in analysis models in Fingence and their application scenarios.

## 1. YoY/QoQ Analysis Model

### Model Description
Compare financial data across different periods, identifying trend changes and abnormal fluctuations.

### Analysis Dimensions

| Dimension | Description | Applicable Scenario |
|-----------|-------------|---------------------|
| Time YoY | This year vs same period last year | Remove seasonal factors |
| Time QoQ | Current period vs previous period | Short-term trend tracking |
| Department Comparison | Horizontal comparison across departments | Performance evaluation |
| Account Comparison | Expense type proportion changes | Cost structure analysis |

### Output Format

```
【YoY Analysis】2024 Q2 vs 2023 Q2

┌─────────────┬──────────┬──────────┬───────────┬──────────┐
│ Account     │ 2024Q2   │ 2023Q2   │ Change    │ Growth   │
├─────────────┼──────────┼──────────┼───────────┼──────────┤
│ Revenue     │ 12M      │ 10M      │ +2M       │ +20% 📈 │
│ COGS        │ 7.2M     │ 5.8M     │ +1.4M     │ +24% 📈 │
│ Sales Exp   │ 1.5M     │ 1.2M     │ +0.3M     │ +25% 📈 │
│ Admin Exp   │ 0.8M     │ 0.75M    │ +0.05M    │ +7%      │
└─────────────┴──────────┴──────────┴───────────┴──────────┘

【Anomaly Annotation】
⚠️ Sales expense growth 25% exceeds revenue growth 20%, recommend monitoring cost-effectiveness
```

### Threshold Configuration
- Revenue change: +/- 5% annotation
- Cost change: +/- 10% annotation
- Expense change: +/- 15% annotation
- Profit margin change: +/- 2% annotation

---

## 2. Trend Analysis Model

### Model Description
Analyze how financial metrics change over time, identifying trends, periodicity, and predicting future values.

### Analysis Types

#### 1. Moving Average Analysis
```
n-period Moving Average = (Xₜ + Xₜ₋₁ + ... + Xₜ₋ₙ₊₁) / n
```

#### 2. Trend Strength Judgment
| Trend Type | R² Value | Description |
|------------|----------|-------------|
| Strong uptrend | > 0.8 | Sustained growth |
| Weak uptrend | 0.5-0.8 | Volatile growth |
| No clear trend | < 0.5 | High volatility |
| Downtrend | < 0 | Sustained decline |

#### 3. Seasonal Analysis
- Calculate seasonal indices for each month/quarter
- Trend analysis after removing seasonal factors
- Applicable to accounts with significant seasonality (revenue, expenses, etc.)

### Output Format

```
【Trend Analysis】Last 12 months revenue trend

📊 Trend Judgment: Uptrend (R²=0.85)
📈 Monthly Average Growth Rate: 3.2%
🔮 Predicted Next Month Revenue: 12.8M

Month      Actual      Trend Line    Forecast
───────────────────────────────────────────────
2024-01    9.5M        9.28M        -
2024-02    9.8M        9.58M        -
...
2024-12    -           12.5M        12.8M

【Inflection Point Annotation】
⚠️ 2024-06 shows abnormal peak, QoQ +15%, reasons need confirmation
```

---

## 3. Structure Analysis Model

### Model Description
Analyze the composition structure of financial data, identifying key contributors and proportion changes.

### Analysis Types

#### 1. Composition Analysis
```
Proportion = Specific Account Amount / Total Amount × 100%
```

#### 2. Pareto Analysis (80/20 Rule)
- Identify the key 20% of factors contributing 80% of value
- Prioritize attention to key accounts

#### 3. Waterfall Analysis
Display decomposition of each factor's contribution to overall change

### Output Format

```
【Structure Analysis】2024 Expense Composition

┌─────────────┬──────────┬────────┐
│ Expense Type│ Amount   │ Share  │
├─────────────┼──────────┼────────┤
│ Personnel   │ 4.5M     │ 45%    │ ███████████████
│ Marketing   │ 2.0M     │ 20%    │ ██████
│ Travel      │ 1.2M     │ 12%    │ ████
│ Office      │ 1.0M     │ 10%    │ ███
│ Other       │ 1.3M     │ 13%    │ ████
└─────────────┴──────────┴────────┘

【Pareto Analysis】
✅ Top 3 expenses account for 77% of total, key control targets
🎯 Recommendation: Personnel cost highest (45%), prioritize optimization
```

---

## 4. Anomaly Detection Model

### Model Description
Automatically identify abnormal points in financial data, assisting risk warning and audit focus.

### Detection Methods

#### 1. Statistical Methods

**Z-Score Method**:
```
Z = (X - μ) / σ
```
- |Z| > 2: Mild anomaly
- |Z| > 3: Significant anomaly

**IQR Method**:
```
IQR = Q3 - Q1
Anomaly = X < Q1 - 1.5×IQR or X > Q3 + 1.5×IQR
```

#### 2. Business Rule Methods

| Rule | Condition | Annotation Level |
|------|----------|------------------|
| Large Transaction | Single > 500K | ⚠️ Medium |
| Expense Surge | QoQ > 30% | 🔴 High |
| Persistent Overrun | 3 consecutive months over budget | ⚠️ Medium |
| Extended Aging | AR > 90 days | 🔴 High |
| Negative Amount | Negative AR | ⚠️ Medium |

#### 3. Combined Detection
Combine statistical methods and business rules to improve detection accuracy

### Output Format

```
【Anomaly Detection Report】2024 Expense Details

🔴 High Risk Anomalies (2 items)
  1. Sales Dept 2 - Travel Expense
     Issue: Single reimbursement 85K, 2.6x department average 32K
     Date: 2024-06-15
     Recommend: Review reimbursement documents

  2. Marketing Dept - Advertising
     Issue: QoQ growth 45%, exceeds threshold 30%
     Period: 2024-Q2
     Recommend: Check delivery effectiveness

⚠️ Medium Risk Anomalies (5 items)
  [List omitted]

✅ Normal (93 items)
```

---

## 5. DuPont Analysis Model

### Model Description
Decompose ROE into multiple drivers, identifying contributions from profitability, asset efficiency, and financial leverage.

### Decomposition Formula
```
ROE = Net Margin × Asset Turnover × Equity Multiplier
    = (Net Profit/Revenue) × (Revenue/Total Assets) × (Total Assets/Equity)
```

### Analysis Dimensions

#### 1. Net Margin Analysis
- Gross margin analysis
- Expense ratio analysis
- Pre-tax/post-tax profit margin

#### 2. Asset Turnover Analysis
- Total asset turnover
- Various asset category turnovers (AR, Inventory, Fixed Assets)

#### 3. Financial Leverage Analysis
- Asset-liability ratio
- Debt-to-equity ratio

### Output Format

```
【DuPont Analysis】2024 Annual

                    ROE = 15.2%
                    ┌─────────────┐
                    │             │
        ┌───────────┤             ├───────────┐
        │ Net Margin│ Asset Turn │ Equity    │
        │ 8.5%      │ 1.2        │ Multiplier│
        │  ↑+1.2%   │  ↓-0.1    │ 1.49      │
        └───────────┴───────────┴───────────┘

【YoY Change】
  ROE Change: +1.8% (Last year 13.4%)

  Contribution Decomposition:
  ├─ Net margin improvement contribution: +2.0%
  ├─ Asset turnover decline contribution: -0.5%
  └─ Financial leverage decline contribution: +0.3%

【Key Findings】
  ✅ Net margin improvement is main driver of ROE growth
  ⚠️ Asset turnover decline needs attention
  ℹ️ Financial leverage decline indicates debt reduction
```

---

## 6. Cash Flow Analysis Model

### Model Description
Analyze cash flow status, identifying liquidity risks and fund usage efficiency.

### Analysis Dimensions

#### 1. Cash Inflow Structure
- Operating cash flow proportion
- Investing cash flow proportion
- Financing cash flow proportion

#### 2. Cash Outflow Structure
- Cost expenditure proportion
- Expense expenditure proportion
- Investment expenditure proportion

#### 3. Liquidity Metrics
```
Current Ratio = Current Assets / Current Liabilities
Quick Ratio = (Current Assets - Inventory) / Current Liabilities
Cash Ratio = Cash / Current Liabilities
```

### Output Format

```
【Cash Flow Analysis】2024 Jan-Jun

┌─────────────────────────────────────────┐
│ Ending Cash Balance: 8.5M              │
│ Expected Next Month Outflow: 3.2M       │
│ Expected Next Month Inflow: 2.8M        │
├─────────────────────────────────────────┤
│ Expected 30-Day Balance: 8.1M           │
│ ⚠️ Expected Gap: 0.4M                  │
└─────────────────────────────────────────┘

【Liquidity Metrics】
  Current Ratio: 1.8 (Good > 1.5)
  Quick Ratio: 1.2 (Normal > 1.0)
  Cash Ratio: 0.6 (Low < 1.0)

【Warning Level】🟡 Medium Risk

【Recommended Actions】
  1. Collect AR from Customer A 800K (30 days overdue)
  2. Postpone non-urgent procurement payments 15 days
  3. Consider activating bank credit line
```

---

## 7. Budget Analysis Model

### Model Description
Compare budget vs actual, identifying budget execution deviations and reasons.

### Analysis Metrics
- Budget execution rate
- Budget variance rate
- Zero-based analysis (necessity of each expenditure)

### Output Format

```
【Budget Analysis】2024 Q2 Sales Expense

┌─────────────┬────────┬────────┬────────┬────────┐
│ Account     │ Budget │ Actual │ Var    │ Exec % │
├─────────────┼────────┼────────┼────────┼────────┤
│ Advertising │ 1M     │ 1.25M  │ +0.25M │ 125% 🔴│
│ Exhibition  │ 0.5M   │ 0.48M  │ -0.02M │ 96%    │
│ Travel      │ 0.3M   │ 0.42M  │ +0.12M │ 140% 🔴│
│ Entertainment│ 0.2M  │ 0.15M  │ -0.05M │ 75%    │
└─────────────┴────────┴────────┴────────┴────────┘

【Overall Execution Rate】117% ⚠️ Over budget 170K

【Overrun Reason Analysis】
  1. Advertising: Temporary 618 promotion added
  2. Travel: Sales team expansion
```
