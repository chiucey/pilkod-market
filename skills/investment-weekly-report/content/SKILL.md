---
name: investment-weekly-report
description: Generate weekly investment reports, analyzing A-share/Hong Kong/US stock market trends. Used when users request weekly investment reports, market summaries, or weekly performance analysis.
---

# 投资周报生成技能

## 功能概述

本技能用于生成投资周报，定期更新和追踪以下主要指数的周度表现：
- **国证A指**（沪深A股市场整体表现）
- **恒生指数**（香港股票市场）
- **标普500指数**（美国股票市场）

## 工作流程

### 1. 数据获取

使用 `stocks_price` 工具获取各指数的历史价格数据：
- 设置 `interval: "1wk"` 获取周度数据
- 设置适当的时间范围以计算周度涨跌幅

### 2. 周度涨跌幅计算

对于每个指数，计算：
- 本周收盘价 vs 上周收盘价
- 周涨跌幅百分比 = (本周收盘价 - 上周收盘价) / 上周收盘价 × 100%
- 标记涨跌颜色（涨用红色，跌用绿色）

### 3. 市场走势分析

基于涨跌幅数据，撰写简要分析：
- 整体市场情绪（上涨/下跌/震荡）
- 主要驱动因素（如果有明显趋势）
- 跨市场比较（A股 vs 港股 vs 美股）

## 输出格式

生成结构化的周报内容：

```
## 本周市场回顾

| 指数 | 上周收盘 | 本周收盘 | 周涨跌幅 | 趋势 |
|------|----------|----------|----------|------|
| 国证A指 | XXX | XXX | ±X.XX% | ↑/↓/→ |
| 恒生指数 | XXX | XXX | ±X.XX% | ↑/↓/→ |
| 标普500 | XXX | XXX | ±X.XX% | ↑/↓/→ |

## 市场走势简评

[简要分析内容]
```

## 执行命令

1. **获取国证A指数据**：使用 `stocks_price` 查询 `000985.SZ` 或相关指数
2. **获取恒生指数数据**：使用 `stocks_price` 查询 `^HSI`
3. **获取标普500数据**：使用 `stocks_price` 查询 `^GSPC`

## 注意事项

- 股票代码根据实际数据源调整
- 如遇数据获取失败，记录错误并尝试备用数据源
- 分析保持客观简洁，避免过度解读短期波动
