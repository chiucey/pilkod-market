# Financial Function Library Reference

This document defines financial functions supported by Fingence and their calculation logic.

## 1. Summation Functions

### SUMIFS - Conditional Summation

**Syntax**: `SUMIFS(sum_range, criteria_range1, criteria1, [criteria_range2, criteria2, ...])`

**Financial Scenarios**:
- Sum sales expenses by department: `SUMIFS(expense_col, dept_col, "Sales", expense_type_col, "Sales Expense")`
- Sum by month: `SUMIFS(amount_col, month_col, "2024-01")`

### SUMPRODUCT - Complex Conditional Summation

**Syntax**: `SUMPRODUCT((condition1)*(condition2)*numeric_col)`

**Financial Scenarios**:
- Multi-condition product summation: Calculate weighted amount for specific period and department

---

## 2. Ratio Functions

### Gross Margin Ratio

```
Gross Margin = (Revenue - COGS) / Revenue × 100%
```

**Interpretation**:
- > 40%: Excellent
- 20%-40%: Good
- < 20%: Need attention

### Net Profit Margin

```
Net Margin = Net Profit / Revenue × 100%
```

**Interpretation**:
- > 15%: Excellent
- 5%-15%: Good
- < 5%: Need attention

### Expense Ratio

```
Expense Ratio = Expense Amount / Revenue × 100%
```

**Breakdown Expense Ratios**:
- Sales Expense Ratio = Sales Expense / Revenue
- Admin Expense Ratio = Admin Expense / Revenue

---

## 3. Turnover Functions

### Accounts Receivable Turnover

```
AR Turnover = Net Credit Sales / Average AR Balance
Average AR = (Beginning Balance + Ending Balance) / 2
```

**Days Sales Outstanding**:
```
DSO = 365 / Turnover Rate
```

**Interpretation**:
- < 30 days: Excellent, fast collection
- 30-60 days: Normal
- > 60 days: Higher risk

### Inventory Turnover

```
Inventory Turnover = COGS / Average Inventory
Days Inventory Outstanding = 365 / Inventory Turnover
```

### Total Asset Turnover

```
Total Asset Turnover = Revenue / Average Total Assets
```

---

## 4. Growth Functions

### Year-over-Year (YoY) Growth Rate

```
YoY Growth = (Current Period - Same Period Last Year) / Same Period Last Year × 100%
```

### Quarter-over-Quarter (QoQ) Growth Rate

```
QoQ Growth = (Current Period - Previous Period) / Previous Period × 100%
```

### Compound Annual Growth Rate (CAGR)

```
CAGR = (Ending Value / Beginning Value)^(1/Years) - 1
```

---

## 5. Budget Functions

### Budget Execution Rate

```
Budget Execution Rate = Actual Amount / Budget Amount × 100%
```

**Interpretation**:
- 90%-110%: Good execution
- < 90%: Insufficient execution
- > 110%: Overrun

### Budget Variance Rate

```
Budget Variance Rate = (Actual - Budget) / Budget × 100%
```

---

## 6. DuPont Analysis Functions

### ROE Decomposition

```
ROE = Net Margin × Asset Turnover × Equity Multiplier
    = (Net Profit/Revenue) × (Revenue/Total Assets) × (Total Assets/Equity)
```

### Factor Interpretation

| Factor | Optimization Direction |
|--------|------------------------|
| Net Margin | Improve gross margin, control expenses |
| Asset Turnover | Accelerate asset turnover, reduce idle assets |
| Equity Multiplier | Use financial leverage appropriately |

---

## 7. Cash Flow Analysis Functions

### Operating Cash Flow / Net Income Ratio

```
Operating Cash Ratio = Operating Cash Flow / Net Income
```

**Interpretation**:
- > 1: High-quality earnings
- < 1: Possible earnings inflation
- < 0: Requires close attention

### Cash to Debt Ratio

```
Cash to Debt Ratio = Operating Cash Flow / Maturing Debt
```

---

## 8. Anomaly Detection Thresholds

| Metric | Anomaly Threshold | Note |
|--------|------------------|------|
| Gross Margin Change | +/- 10% | Explanation needed if exceeded |
| Expense Growth Rate | > 30% | YoY/QoQ |
| Single Transaction | > Average 3σ | Suspicious large amount |
| AR Aging | > 90 days | Collection risk |
| Budget Execution Deviation | > 15% | Approval required |

---

## 9. Calculation Step Display Format

When user needs audit review, display calculation process in the following format:

```
【Calculation Steps】Calculate 2024 Q1 Sales Department 1 Gross Margin

Step 1: Identify Data
  - Revenue (Sales Dept 1): 5,000,000
  - COGS (Sales Dept 1): 3,000,000

Step 2: Apply Formula
  Gross Margin = (Revenue - COGS) / Revenue × 100%
              = (5,000,000 - 3,000,000) / 5,000,000 × 100%

Step 3: Calculate Result
  = 40%

【Data Traceability】
  - Revenue Detail: sheet "Sales Data", rows 15-45
  - Cost Detail: sheet "Cost Data", rows 10-38
```
