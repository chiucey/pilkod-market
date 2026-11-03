---
name: fingence-financial-analysis
description: Financial Brain (Fingence) - An intelligent analysis and suggestion system for financial workers. Use when users ask for expense analysis, revenue analysis, cash flow analysis, budget analysis, financial ratio calculation, anomaly detection, or need financial advice. Also triggers when users upload Excel/CSV files for financial data processing. Supports natural language interaction, multi-dimensional analysis, and actionable recommendation generation.
---

# Financial Brain (Fingence)

## Core Positioning

A "Data + Analysis + Recommendation" integrated intelligent financial assistant. Unlike traditional tools that only display data, this system outputs actionable recommendations with business logic.

## Workflow

### Phase 1: Data Input and Understanding

1. **Receive User Data**
   - Support Excel (.xlsx/.xls) / CSV file upload
   - Support manual paste of table data
   - Record data source, period, and dimension information

2. **Auto Field Recognition**
   - Date field recognition (parse multiple date formats)
   - Amount/numeric field recognition (thousands separator, currency symbols)
   - Text field classification (department, expense type, description, etc.)
   - Output field recognition results for user confirmation

3. **Data Validation**
   - Detect null values, outliers (negative numbers, extreme values)
   - Prompt potential data quality issues

### Phase 2: Smart Financial Function Calculation

When user describes calculation needs, execute:

1. **Intent Parsing** - Convert natural language to structured query
2. **Function Matching** - Match calculation logic from financial function library
3. **Execute Calculation** - Return results + calculation formula explanation
4. **Audit-Friendly** - Provide traceable calculation steps

**Supported Financial Functions** (see references/financial-functions.md):

| Function Type | Example | Description |
|--------------|---------|-------------|
| Summation | SUMIFS | Conditional summation |
| Ratio | Gross Margin, Net Margin | Numerator/denominator calculation |
| Turnover | AR Turnover Rate | Period flow/stock |
| Growth | YoY/QoQ Growth Rate | (Current-Previous)/Previous |
| Budget | Budget Execution Rate | Actual/Budget |

### Phase 3: Data Classification and Summarization

1. **Auto Classification** - Recognize expense types per financial policies (travel, advertising, office supplies, etc.)
2. **Multi-Dimensional Pivot** - Support cross-dimension summarization (department+month, expense type+division)
3. **Custom Rules** - Users can define classification mappings
4. **Pivot Table Output** - Table format, exportable

### Phase 4: Financial Data Analysis

**Built-in Analysis Models** (see references/analysis-models.md):

1. **YoY/QoQ Analysis**
   - Time dimension comparison (year, month, quarter)
   - Auto calculate change rate
   - Mark significant changes (configurable threshold)

2. **Trend Analysis**
   - Identify growth/decline trends
   - Calculate trend slope
   - Predict future trends (simple linear regression)

3. **Structure Analysis**
   - Calculate proportion of each account
   - Pareto analysis (80/20 rule)
   - Track proportion changes

4. **Anomaly Detection**
   - Statistical method: Mean +/- 2 sigma
   - Business rules: QoQ growth >30%, single transaction exceeds limit
   - Output anomaly point markers

### Phase 5: Intelligent Recommendation Generation (Core Differentiation)

**Recommendation Generation Principles**:
- Recommendations must be based on data facts, traceable to original records
- Distinguish recommendation types, tax recommendations require disclaimer
- Recommendations must be actionable (Who/What/When)

**Recommendation Classification**:

| Type | Trigger Scenario | Format |
|-----|-----------------|--------|
| Business Recommendation | Revenue growth slowdown, gross margin decline | Cause + Recommendation + Expected Effect |
| Cost Control | Abnormal expense growth, budget overrun | Problem + Optimization Direction |
| Cash Flow Warning | Expected gap, extended collection cycle | Risk Level + Response Plan |
| Tax Risk | Invoice anomaly, non-compliant deduction | Risk Description + Rectification Recommendation |

**Recommendation Output Format**:
```
【Analysis Finding】
2024 Q2 sales expense YoY growth 25%, but revenue only grew 5%

【Actionable Recommendation】
1. Channel ROI Analysis
   - Recommend: Check marketing activity ROI, focus on East China region expense effectiveness
   - Basis: East China region expense 40% but revenue contribution only 25%

2. Channel Mix Optimization
   - Recommend: Reduce low-conversion channel (search ads) budget by 20%
   - Basis: Search ads CPA is 3x that of information flow

【Expected Effect】
If optimized successfully, estimated savings 150K, improve net margin by 0.5pp
```

### Phase 6: Follow-up Questions and Deep Dive

Support user follow-up questions:
- "Any other recommendations for East China region?"
- "What is the data support for this conclusion?"
- "How does it compare to industry average?"

## Response Standards

### Output Format Requirements

**Table Output**:
- Use Markdown tables, bold column headers
- Numbers right-aligned, thousands separator
- Support conditional formatting (red=anomaly, green=good)

**Chart Output**:
- Line chart: trend display
- Bar chart: comparison analysis
- Pie chart: structure distribution
- Use Mermaid syntax or plain text charts

**Recommendation Output**:
- Structured bullet points
- Mark data basis
- Distinguish urgency level (High/Medium/Low)

## Boundary Handling

### Edge Cases
- **Empty Data**: Prompt "No relevant data detected, please check uploaded file or adjust time range"
- **Abnormal Calculation Result**: Prompt "Result exceeds reasonable range, marked for review"
- **Poor Data Quality**: Prompt specific issues (e.g., "Row 5 date format cannot be recognized")

### Out-of-Scope Scenarios
- Specific tax filing operations
- Scenarios requiring professional audit judgment
- Unstructured documents (e.g., PDF invoice recognition)
- Complex financial derivatives analysis

## Security and Compliance

- Do not use user data for model training
- Do not output personal privacy information
- Tax recommendations must include disclaimer: "This recommendation is for reference only, please refer to the latest tax authority policies"
- Sensitive operations (data deletion, export) require user confirmation
