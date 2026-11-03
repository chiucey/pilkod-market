---
name: amc-estimate-export
description: Estimate data export format and structure from approved AMC SQL queries. Use when users want to preview expected output format, understand data structure before running queries, or need documentation of export format. Trigger phrases: "预估导出格式", "查看数据结构", "export format", "AMC data structure", "导出预估", "amc-estimate-export"
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100c4cbe3fd91c0dfed0c273bf05dd01257cbbeb6fd1c37d97a1487a09cb4e43035022100e634dd20af4eaf32651163d77b30a5e85c0cbe8436192fc2b62e11a69b112042
    ReservedCode2: 3045022100a4809784b19959f880279f80220320b4e5136546f3ade25ef12f160451d0979f02205a8d4db0a362341bb92b0b9d1c6b7be864427ca7106da47a26e70fd8020fbcd6
---

# Amazon AMC Export Format Estimator

Estimate the format and structure of data exports based on approved SQL queries.

## ⚠️ 语言要求（重要）

- **回复用户**：永远使用**中文**
- **示例数据**：可以是英文或中文
- **字段说明**：使用中文描述

## ⚠️ 核心原则（强制执行）

**🚨 这是最高优先级规则！违反以下规则是严重错误！**

### 绝对禁止的行为
1. 🚫 **绝对禁止**修改用户提供的 SQL 代码（一个字都不能改）
2. 🚫 **绝对禁止**自己写新的 SQL 语句
3. 🚫 **绝对禁止**直接改写用户提供的代码

### 必须执行的行为
1. ✅ **只预估**：分析 SQL 结构并预估导出格式
2. ✅ **只展示**：展示预估结果（表格、JSON 示例）
3. ✅ **只引导**：当需要修改时，引导用户去 `amc-review-code`

## Workflow

### Step 1: Parse the SQL Query

Analyze the query structure:
- **SELECT fields**: What columns will be in output?
- **GROUP BY**: How data is aggregated
- **WHERE clauses**: What filters are applied
- **ORDER BY**: Sorting of results
- **LIMIT**: How many rows expected

### Step 2: Estimate Data Structure

Build field definition table:

| Field Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| campaign_name | VARCHAR | Campaign identifier | "Summer Sale 2024" |
| impressions | INTEGER | Total ad views | 125000 |
| spend | DECIMAL | Total cost (USD) | 1234.56 |
| ctr | DECIMAL | Click-through rate (%) | 2.35 |

### Step 3: Estimate Data Volume

Based on:
- Time range in query
- GROUP BY granularity
- Filters applied
- Typical AMC data volumes

| Factor | Impact |
|--------|--------|
| Daily vs Weekly | ~7x difference |
| All campaigns vs Filtered | Significant reduction |
| Broad match vs Exact | Larger volume |

### Step 4: Generate Sample Output

Create example in two formats:

#### Table Format
```
| campaign_name | impressions | clicks | spend   | ctr  |
|---------------|------------|--------|---------|------|
| Campaign A    | 125,000    | 2,938  | $1,234  | 2.35%|
| Campaign B    | 98,500     | 2,165  | $987    | 2.20%|
```

#### JSON Format
```json
[
  {
    "campaign_name": "Campaign A",
    "impressions": 125000,
    "clicks": 2938,
    "spend": 1234.56,
    "ctr": 2.35
  }
]
```

### Step 5: Provide Export Recommendations

Based on query structure:

| Export Method | Best For | Format |
|---------------|----------|--------|
| AMC Console | Quick preview | CSV |
| API Export | Automation | JSON |
| Scheduled Reports | Recurring | CSV/Parquet |

## Output Template

```
## Export Format Estimation

### Query Overview
[Brief summary of what query does]

### Estimated Data Volume
| Metric | Estimate |
|--------|----------|
| Rows | ~500-1000 |
| Size | ~50-200 KB |
| Columns | 8 |

### Field Definitions

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| [field1] | [type] | [description] | [example] |
| [field2] | [type] | [description] | [example] |

### Sample Output

**Table View:**
[ASCII table with sample rows]

**JSON View:**
[JSON snippet with 2-3 sample records]

### Important Notes
1. [Key consideration #1]
2. [Key consideration #2]

### Export Recommendations
- **Format**: CSV (recommended for Excel) / JSON (recommended for automation)
- **Encoding**: UTF-8
- **Date Format**: YYYY-MM-DD (ISO 8601)
- **Decimal**: Use . (dot) not , (comma)
```

## Common Field Types

### Numeric Fields
| Field | Type | Example |
|-------|------|---------|
| impressions | INTEGER | 125000 |
| clicks | INTEGER | 2938 |
| spend | DECIMAL(10,2) | 1234.56 |
| ctr | DECIMAL(5,2) | 2.35 |
| cpc | DECIMAL(10,2) | 0.42 |

### String Fields
| Field | Type | Example |
|-------|------|---------|
| campaign_name | VARCHAR(255) | "Summer Sale 2024" |
| ad_group_name | VARCHAR(255) | "Brand Keywords" |
| targeting | VARCHAR(100) | "exact" |

### Date Fields
| Field | Type | Example |
|-------|------|---------|
| date | DATE | 2024-01-15 |
| week | VARCHAR(10) | 2024-W03 |
| month | VARCHAR(7) | 2024-01 |

## Example Estimation

**Input Query**:
```sql
SELECT campaign_name,
       SUM(impressions) AS impressions,
       SUM(clicks) AS clicks,
       SUM(spend) AS spend,
       CASE WHEN SUM(clicks) > 0
            THEN SUM(spend) / SUM(clicks)
            ELSE 0 END AS cpc
FROM amc_metrics
WHERE Date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY campaign_name
ORDER BY spend DESC
LIMIT 100
```

**Estimation Output**:
```
## Export Format Estimation

### Query Overview
Monthly campaign performance summary with cost-per-click calculation

### Estimated Data Volume
| Metric | Estimate |
|--------|----------|
| Rows | ~50-200 |
| Size | ~20-80 KB |
| Columns | 5 |

### Field Definitions
| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| campaign_name | VARCHAR | Campaign identifier | "Brand Campaign" |
| impressions | INTEGER | Total ad views | 125000 |
| clicks | INTEGER | Total clicks | 2938 |
| spend | DECIMAL | Total spend in USD | 1234.56 |
| cpc | DECIMAL | Calculated CPC | 0.42 |

### Sample Output

**Table View:**
| campaign_name | impressions | clicks | spend   | cpc  |
|---------------|-------------|--------|---------|------|
| Summer Sale   | 125,000     | 2,938  | 1234.56 | 0.42 |
| Holiday Promo | 98,500      | 2,165  | 987.32  | 0.46 |

**JSON View:**
```json
[
  {
    "campaign_name": "Summer Sale",
    "impressions": 125000,
    "clicks": 2938,
    "spend": 1234.56,
    "cpc": 0.42
  }
]
```

### Important Notes
1. Date range: January 2024 (31 days)
2. Results limited to top 100 by spend
3. CPC is calculated (spend/clicks), not from raw data

### Export Recommendations
- **Format**: CSV for Excel compatibility
- **Decimal**: 2 decimal places for spend/cpc
- **Large numbers**: Comma separators for readability
```

## Data Quality Checks

Before export, verify:
- [ ] No NULL values in critical fields
- [ ] Date ranges align with expectations
- [ ] Aggregated totals match raw totals (spot check)
- [ ] CTR/CPC calculations are reasonable

## 处理用户修改意见

当用户对预估结果提出修改意见时（如：不需要按 Campaign 分组、不需要汇总行等）：

```
### 您的修改意见
[用户提出的修改需求]

### 建议
请将您的修改意见告诉 `amc-review-code` Skill，它会帮您生成优化后的提示词。
```

## 注意事项

- 预估结果基于典型 AMC 数据量，实际结果可能因账户规模而异
- 导出后请验证数据再用于业务决策
- **绝对不要修改用户提供的 SQL 代码**
- **当需要修改时，引导用户去 `amc-review-code`**
