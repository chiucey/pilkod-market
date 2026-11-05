---
name: cost-growth-analyzer
description: Tool for analyzing cloud bill cost growth reasons. Use when users ask to analyze cost growth ratio, growth magnitude, calculate growth contribution, or perform YoY/MoM analysis. Suitable for financial analysis, cost control, and budget management.
---

# Cost Growth Analyzer

## Overview

Analyze cloud bill data from two periods, calculate cost growth ratio, magnitude, and contribution, and identify main reasons for cost changes.

## Input Requirements

- Two cloud bill Excel files (.xlsx format)
- File structure must contain these columns:
  - `账单出账月份` or `账单出账日期` (billing month/date)
  - `资源一级分类` (resource level 1 category)
  - `资源二级分类` (resource level 2 category)
  - `PSA` (optional)
  - `成本（元）` (cost)

## Analysis Dimensions

### 1. Growth Ratio Analysis
- **Overall Growth Rate**: (End Cost - Start Cost) / Start Cost x 100%
- **Category Growth Rate**: Calculate by resource level 1, level 2, and PSA
- **MoM/YoY**: Support multi-period comparison

### 2. Growth Magnitude Analysis
- **Absolute Growth**: End Cost - Start Cost
- **Dimension Breakdown**: Breakdown by resource category, PSA, etc.
- **TOP N Contributors**: Identify resources/services with highest growth contribution

### 3. Contribution Calculation
- **Contribution Formula**: Item Contribution = Item Growth / Total Growth x 100%
- **Cumulative Contribution**: Sort by contribution descending, calculate cumulative percentage
- **Marginal Contribution**: Identify services with highest marginal growth contribution

## Output Format

Generate Excel analysis report with these sheets:

1. **Overview**: Overall growth metrics summary
2. **Level 1 Growth Analysis**: Growth rate comparison by primary category
3. **Level 2 Growth Analysis**: Growth rate comparison by secondary category
4. **Contribution Analysis**: Contribution and cumulative contribution by dimension
5. **TOP Growth Resources**: Top contributors ranked by growth magnitude
6. **Anomaly Alert**: Flag resources with abnormal growth

## Usage Example

```
User: Analyze cost growth between January and March 2026 cloud bills
-> Execute cost growth analysis, output growth ratio, magnitude, and contribution report
```

## Notes

- Handle negative or zero cost data specially
- Mark new resources (no start period data) separately
- Calculate with 2 decimal places, round when displaying
