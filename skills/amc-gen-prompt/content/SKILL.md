---
name: amc-gen-prompt
description: Generate English prompts for Amazon AMC AI. Use when users want to analyze advertising performance, create AMC queries, generate SQL, or need help writing prompts for Amazon AMC. Trigger phrases: "AMC提示词", "生成AMC查询", "广告分析提示词", "analyze Amazon AMC", "generate AMC query", "amc-gen-prompt", "AMC相关", "生成提示词", "写提示词", "需要提示词"
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502207861a1b907d037bceb949ef40b989973f135f277cac8b8d1e4afebeb7270b1b302210098cf3c0f90598b0c6b11aae9aa75b00bc196a39d02ac78008d1b41efbe800866
    ReservedCode2: 3044022056906a0bfeba4f1d481b4f3ab5c62d7b3fc457c1038bc31c9715718908d3476e02206a49f546a63662ef194bbe472246c7d44938b002b166bae957c079185b4d3872
---

# Amazon AMC AI Prompt Generator

Generate optimized English prompts for Amazon AMC AI based on user requirements.

## ⚠️ 语言要求（重要）

- **回复用户**：永远使用**中文**
- **生成的提示词**：必须是**英文**（供 AMC AI 使用）
- **预览/示例**：可以是英文

## Workflow

### Step 1: Understand User Requirements

Extract the following from user input:
- **Time Range**: Date range (e.g., last 7 days, last month, Q1 2024)
- **Grouping**: How to segment data (campaign, ad group, keyword, etc.)
- **Metrics**: Required metrics (impressions, clicks, CTR, CPC, spend, conversions, ROAS, etc.)
- **Sorting**: Order of results (spend DESC, CTR ASC, etc.)
- **Filters**: Any specific conditions or filters

### Step 2: Generate English Prompt

Create a clear, structured English prompt following AMC AI best practices:

```english
Analyze [time_range] advertising performance on Amazon.
- Group by: [grouping_dimension]
- Metrics: [list_metrics]
- Sort: [sorting_requirement]
- Filters: [any_conditions]
```

### Step 3: Provide Output

Present to user:
1. **Generated Prompt** (copyable, ready for AMC AI)
2. **Considerations** (any notes about the prompt)
3. **Expected Output** (brief description of what AMC AI will return)

## Prompt Templates

### Template 1: Basic Performance Analysis

```
Analyze the [time_range] advertising performance on Amazon.
- Group by: [campaign_name/ad_group_name/keyword/etc.]
- Include metrics: impressions, clicks, click-through rate (CTR), cost per click (CPC), spend, conversions, cost per acquisition (CPA), return on ad spend (ROAS)
- Sort by: [metric] [ASC/DESC]
- Limit results to: [number] rows
```

### Template 2: Trend Analysis

```
Analyze [time_range] advertising trends on Amazon.
- Group by: [time_period] (daily/weekly/monthly)
- Compare metrics: impressions, clicks, spend, conversions
- Calculate period-over-period changes
- Show trends for: [specific campaigns or all]
```

### Template 3: Conversion Funnel

```
Analyze the [time_range] conversion funnel on Amazon.
- Track stages: impressions → clicks → detail page views → add to cart → purchase
- Group by: [campaign or ad group]
- Calculate conversion rates between each stage
- Identify drop-off points
```

## Common Metrics Reference

| Metric | Description | Formula |
|--------|-------------|---------|
| Impressions | Number of ad views | - |
| Clicks | Number of ad clicks | - |
| CTR | Click-through rate | clicks/impressions × 100 |
| CPC | Cost per click | spend/clicks |
| Spend | Total advertising cost | - |
| Conversions | Number of purchases | - |
| CPA | Cost per acquisition | spend/conversions |
| ROAS | Return on ad spend | revenue/spend |

## Examples

### Example 1: Campaign Performance

**User Request**: "Analyze last 7 days campaign performance, show impressions, clicks, CTR, CPC, spend, sort by spend descending"

**Generated Prompt**:
```
Analyze the last 7 days of advertising performance on Amazon.
- Group by: campaign_name
- Include metrics: impressions, clicks, click-through rate (CTR), cost per click (CPC), spend
- Sort by: spend DESC
- Show top 50 campaigns
```

### Example 2: Keyword Analysis

**User Request**: "Analyze keyword performance for last month, calculate CTR and conversion rate by keyword"

**Generated Prompt**:
```
Analyze the last 30 days of keyword advertising performance on Amazon.
- Group by: keyword_id or keyword_text
- Include metrics: impressions, clicks, click-through rate (CTR), conversions, conversion rate (purchases/clicks × 100)
- Filter to: search term campaigns only
- Sort by: conversions DESC
```

## Best Practices

1. **Be Specific**: Include exact time ranges, metric names, and grouping dimensions
2. **Use AMC Terminology**: Match Amazon's naming conventions (campaign_name, spend, impressions, etc.)
3. **Set Expectations**: Mention sorting, limits, and any special requirements
4. **Iterate**: If user provides feedback, adjust prompt accordingly

## Notes

- Always use English prompts for AMC AI
- Keep prompts concise but complete
- Include specific date ranges rather than vague terms like "recent"
- List metrics explicitly rather than "all metrics"
