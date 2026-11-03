---
name: data-analysis-skill
description: Analyze CSV, Excel, JSON data files and generate structured reports. Use for 数据分析, 数据概览, 字段质量, 数值统计, 类别统计, 分组聚合, 相关性分析, 数据清洗, 异常值检测, 数据可视化建议, 报表生成. Supports .csv, .xlsx, .xls, .json formats with automatic encoding detection and missing value handling.
---

# Data Analysis Skill

## Intake

1. Identify the data source type (CSV, Excel, JSON), file path, and analysis objectives.
2. Determine if specific columns, grouping fields, or analysis types are needed.
3. Clarify output format requirements (JSON report, summary statistics, or visual recommendations).

## Resource Routing

Read `references/data-analysis-playbook.md` when producing any data profile, statistical summary, correlation analysis, group aggregation, outlier detection, or data quality assessment.

Use targeted sections in the playbook:

- Data profiling: File Structure, Column Types, Missing Values
- Statistical analysis: Numeric Summary, Categorical Summary, DateTime Summary
- Correlation work: Correlation Matrix, Top Pairs, Feature Relationships
- Group analysis: Group Aggregation, Segment Statistics, Trend Comparison
- Data quality: Duplicate Detection, Outlier Bounds, Data Validation
- Reporting: JSON Output Format, Visualization Recommendations

## Core Workflow

1. Start from file format detection and encoding resolution before analysis.
2. Load data with automatic type inference and missing value handling.
3. Generate column profiles with dtype, missing rate, and unique counts.
4. Calculate statistical summaries for numeric, categorical, and datetime columns.
5. Compute correlations between numeric columns when applicable.
6. Perform group-based aggregation if grouping field is specified.
7. Detect outliers using IQR method for numeric columns.
8. Output structured JSON report with all findings.

## Output Defaults

When the user asks for a complete data analysis, produce:

- **File Overview**: rows, columns, selected columns, duplicate rows, memory usage
- **Column Profile**: dtype, missing count, missing rate, unique count per column
- **Numeric Summary**: count, mean, median, std, min, max, Q1, Q3, outlier count, outlier bounds
- **Categorical Summary**: count, missing, unique, mode, top values frequency
- **DateTime Summary**: count, missing, min, max date range
- **Correlation Summary**: top correlated column pairs sorted by absolute correlation
- **Group Summary**: group sizes and aggregated statistics for specified grouping column

When the user asks for data profiling or quality assessment, produce:

- Data type validation and conversion notes
- Missing value analysis with imputation recommendations
- Duplicate row detection and removal suggestions
- Outlier detection with IQR bounds and affected rows count

When the user asks for statistical summaries or reports, produce:

- Descriptive statistics for requested columns
- Segment-based aggregations with mean/sum/count
- Cross-column correlation coefficients

## Analysis Capabilities

- **File Formats**: CSV (auto encoding detection), Excel (.xlsx/.xls with sheet selection), JSON
- **Column Types**: Numeric, Categorical, DateTime with automatic detection
- **Statistical Methods**: Mean, median, mode, std, quartiles, IQR, correlation
- **Grouping**: Group by any column with numeric aggregations
- **Outliers**: IQR-based detection with configurable bounds
- **Encoding**: Automatic UTF-8-sig, UTF-8, GB18030 detection for CSV

## Guardrails

- Do not attempt to analyze files larger than available memory without warning.
- Handle encoding errors gracefully with fallback options.
- Mark correlation calculations as unavailable when fewer than 2 numeric columns exist.
- Report errors clearly with file path and specific error message.
- Preserve original data types; do not convert without explicit reason.
- Handle datetime columns with timezone awareness separately from numeric/categorical.