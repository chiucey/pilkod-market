---
name: market-valuation-report
description: Generate investment market valuation reports including S&P 500 forward P/E ratio and Shiller PE (CAPE) ratio analysis. Use when users ask for market valuation queries, valuation reports, bubble risk analysis, or P/E ratio data.
---

# 投资市场估值报告技能

## 工作流程

### 步骤 1：数据获取

使用 `extract_content_from_websites` 工具从以下来源获取数据：

1. **S&P 500 Forward P/E**:
   - 主源: https://en.macromicro.me/series/20052/sp500-forward-pe-ratio
   - 备源: 搜索 "S&P 500 forward P/E ratio current" 或访问 ycharts.com

2. **Shiller PE Ratio (CAPE)**:
   - https://multpl.com/shiller-pe

### 步骤 2：数据提取

从页面内容中提取：
- 当前 Forward P/E 数值
- 当前 Shiller PE 数值
- 历史均值数据（如有）
- 最新更新日期

### 步骤 3：评估分析

**Forward P/E 评估标准**:
- < 15: 偏低
- 15-20: 适中
- > 20: 偏高
- > 25: 显著偏高

**Shiller PE 评估标准**:
- < 15: 偏低
- 15-20: 适中
- > 20: 偏高
- > 30: 泡沫预警

### 步骤 4：生成报告

按以下格式输出报告：

```
📊 **投资市场估值周报** | {日期}

**S&P 500 前瞻市盈率**
- 当前值: {数值}
- 评估: {偏高/适中/偏低}

**Shiller PE Ratio (CAPE)**
- 当前值: {数值}
- 历史均值: ~17.35
- 当前/均值比率: {百分比}
- 评估: {偏高/适中/偏低}

**综合评估**: {泡沫风险分析}
```

### 步骤 5：风险提示

根据估值水平提供：
1. 核心风险等级（低/中/高/泡沫）
2. 与历史高点的比较
3. 投资建议（防御/中性/积极）
4. 需关注的风险因素

## 数据来源说明

- **Macromicro**: 亚洲领先的数据分析平台，提供实时市场指标
- **Multpl.com**: Robert Shiller 授权的CAPE数据源
- **ycharts**: 金融数据聚合平台

## 注意事项

- 数据可能因时区差异略有不同
- Forward P/E 通常基于未来12个月盈利预期
- Shiller PE 使用10年平均通胀调整盈利，波动较小
- 建议结合VIX波动率指数一起分析
