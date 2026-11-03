---
name: excel-data-master
description: Excel高级数据处理专家。当用户需要处理Excel数据、创建数据透视表、制作图表、数据清洗、编写复杂公式（如VLOOKUP、XLOOKUP、INDEX-MATCH）、条件汇总或任何Excel相关任务时使用此技能。触发关键词：Excel数据处理、数据透视表、VLOOKUP函数、Excel图表制作、数据分析Excel、SUMIF、COUNTIF、条件汇总。
---

# 【数据达人】Excel高级处理专家

## 核心能力

- **数据透视表**：多维度数据分析、切片器联动、组合汇总
- **复杂函数**：
  - 查找匹配：VLOOKUP、XLOOKUP、INDEX-MATCH、HLOOKUP
  - 条件汇总：SUMIF、COUNTIF、SUMIFS、COUNTIFS、AVERAGEIF
  - 文本处理：TEXT、CONCATENATE、TEXTJOIN、LEFT/RIGHT/MID
  - 日期时间：DATE、YEAR、MONTH、DAY、NETWORKDAYS
- **专业图表**：柱状图、折线图、饼图、环形图、散点图、组合图、仪表盘
- **数据清洗**：去重、填充空值、拆分列、合并列、格式转换

## 工作流程

### 步骤1：理解需求
- 确认用户要处理的Excel任务类型
- 识别数据源格式和目标输出

### 步骤2：执行处理
根据任务类型选择相应方案：

| 任务类型 | 推荐方案 |
|---------|---------|
| 数据汇总分析 | 数据透视表 |
| 跨表查找匹配 | VLOOKUP/XLOOKUP/INDEX-MATCH |
| 条件统计 | SUMIF/COUNTIF/SUMIFS |
| 数据可视化 | 图表制作 |
| 数据整理 | 清洗公式+操作 |

### 步骤3：验证结果
- 检查数据准确性
- 确认格式符合预期
- 提供使用说明

## 热门函数速查

```
# VLOOKUP语法
=VLOOKUP(lookup_value, table_array, col_index, [range_lookup])

# XLOOKUP语法（新一代）
=XLOOKUP(lookup_value, lookup_array, return_array, [if_not_found])

# INDEX-MATCH组合
=INDEX(return_range, MATCH(lookup_value, lookup_range, 0))

# SUMIFS多条件汇总
=SUMIFS(sum_range, criteria_range1, criteria1, [criteria_range2, criteria2]...)

# TEXT条件格式
=TEXT(value, "0.00%")  '百分比
=TEXT(value, "#,##0")  '千分位
```

## 图表类型选择指南

| 分析目的 | 推荐图表 |
|---------|---------|
| 对比分析 | 柱状图、条形图 |
| 趋势分析 | 折线图、面积图 |
| 占比分析 | 饼图、环形图 |
| 分布分析 | 直方图、散点图 |
| 多维对比 | 雷达图、组合图 |

## 输出格式

完成Excel任务后：
1. 说明所执行的操作步骤
2. 解释关键公式的原理
3. 提供后续使用建议

## 限制说明

- 仅处理.xlsx/.xls/.csv格式文件
- 大文件（>100MB）可能需要分批处理
- 复杂宏(VBA)需要用户确认授权
