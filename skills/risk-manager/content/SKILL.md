---
name: risk-manager
description: 【风险管理者】风险管理、组合优化、策略回测和价格预测技能。当用户要求评估股票风险、计算VaR、组合优化、策略回测、收益预测、风险控制、资产配置等任务时使用。
---

# 风险管理技能

## 模块一：风险评估

### assess_risk

计算单只股票或投资组合的风险指标。

**支持的指标：**

| 类型 | 指标名 | 说明 |
|-----|--------|------|
| 市场风险 | VaR | 风险价值 |
| 市场风险 | CVaR | 条件风险价值 |
| 市场风险 | Beta | 系统性风险 |
| 市场风险 | MaxDrawdown | 最大回撤 |
| 收益风险 | Volatility | 波动率 |
| 收益风险 | Sharpe | 夏普比率 |

## 模块二：策略回测

### backtest_strategy

根据定义的买卖规则，在历史数据上模拟交易。

**策略规则示例：**

```python
{
  "entry": {
    "type": "ma_cross",
    "fast_ma": 5,
    "slow_ma": 20,
    "direction": "long"
  },
  "exit": {
    "type": "ma_cross",
    "fast_ma": 5,
    "slow_ma": 20,
    "direction": "short"
  },
  "position": {
    "max_position": 0.3,
    "stop_loss": 0.05,
    "take_profit": 0.15
  }
}
```

**输出指标：**

| 指标 | 说明 |
|-----|------|
| total_return | 总收益率 |
| annual_return | 年化收益率 |
| sharpe_ratio | 夏普比率 |
| max_drawdown | 最大回撤 |
| win_rate | 胜率 |

## 模块三：组合优化

### optimize_portfolio

根据给定标的池，生成有效前沿并推荐最优权重。

**约束条件示例：**

```python
{
  "max_weight": 0.3,
  "min_weight": 0.05,
  "sector_limits": {
    "consumer": 0.5,
    "finance": 0.4
  }
}
```

## 模块四：价格预测

### forecast_price

利用模型预测未来股价走势。

**输入参数：**

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| symbol | str | 是 | 股票代码 |
| horizon | int | 否 | 预测周期天数 (默认: 5) |
| model | str | 否 | 模型类型：arima/lstm/prophet (默认: auto) |

## 风险管理规则

1. **仓位控制**：单只股票最大仓位不超过组合的30%
2. **止损规则**：单笔交易最大亏损不超过入场价的5%
3. **分散化**：组合至少包含5只不同行业股票
4. **VaR限制**：95%置信度下日VaR不超过组合值的2.5%

## 合规声明

> ⚠️ 基于历史数据的量化分析结果仅供参考，不构成投资建议。市场有风险，投资需谨慎。