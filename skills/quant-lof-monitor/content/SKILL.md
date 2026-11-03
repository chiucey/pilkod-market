---
name: quant-lof-monitor
description: >
  量化LOF基金实时监控与买入信号分析系统。当用户询问以下内容时使用：
  (1) 量化LOF基金每日监控或基金巡检请求,
  (2) 特定量化LOF基金是否可买入（支持代码: 166107/166108/166109/161039/161035/501059/160644）,
  (3) LOF基金折溢价套利机会分析,
  (4) 量化基金实时行情分析,
  (5) 量化多因子/指数增强/红利策略基金的买入时机判断,
  (6) 基金评分系统（综合折溢价率、流动性、规模、夏普比率等维度）。
  触发关键词：量化LOF, LOF监控, 折溢价, 量化多因子, 量化先锋, 1000增强, 500增强, 港美互联, 基金买入信号, fund monitor, LOF arbitrage, 信澳, 富国, 西部利得, 鹏华港美
---

# Quant LOF Monitor Skill

## Purpose

Monitor quantitative strategy LOF funds in real-time, calculate composite buy scores (0-100),
and generate actionable buy/sell/hold recommendations with risk analysis.

## Workflow

### 1. Data Collection

Run the monitor script to fetch live data from Jisilu:

```bash
python scripts/monitor.py
```

This outputs JSON with real-time prices, NAVs, premium/discount rates,
composite scores (0-100), and buy signals for all tracked funds.

If the script fails, manually fetch from:
- Jisilu: https://www.jisilu.cn/data/lof/stock_lof_list/
- Eastmoney: https://quote.eastmoney.com/center/gridlist.html#fs_lof

### 2. Analysis & Reporting

After obtaining data, produce analysis using the template in `references/funds_data.md`.
Key report structure:

```
## 量化LOF基金监控报告 {date}

### 一、市场整体状态
- 监控数量: X只 | 交易状态: 盘中/收盘
- 积极买入: X只 | 谨慎买入: X只 | 观望: X只 | 回避: X只

### 二、基金逐一分析
[Per-fund analysis with price, NAV, premium, score, signals]

### 三、今日买入优先级
[Ranked list with fund name, code, score, and core reasons]
```

### 3. Rating Rules

Apply these rating badges based on score and premium:

| Score | Premium <2% | Premium >=2% | Badge |
|-------|-------------|--------------|-------|
| >=80 | Any | N/A | A-强烈买入 |
| 65-79 | Yes | N/A | B-积极买入 |
| 50-64 | Yes | N/A | C-谨慎买入 |
| 50-64 | No | Yes | C-谨慎(溢价偏高) |
| 35-49 | Any | Any | D-观望 |
| <35 | Any | Any | E-回避 |

Special override: If premium > +5%, force "E-回避" regardless of score.

## Tracked Funds (7)

| Code | Name | Strategy | Key Metrics |
|------|------|----------|-------------|
| 166107 | 信澳量化多因子LOF-A | Multi-factor | Sharpe 2.48, MaxDD 48.9% |
| 166108 | 信澳量化多因子LOF-C | Multi-factor | C类，7日免赎回 |
| 166109 | 信澳量化先锋LOF-A | Stat arbitrage | Sharpe 2.20, MaxDD 45.0% |
| 161039 | 富国中证1000增强LOF-A | CSI1000 enhance | Best liquidity, preferred |
| 161035 | 富国中证500增强LOF | CSI500 enhance | Balanced option |
| 501059 | 西部利得国企红利增强LOF | Dividend enhance | Lowest risk, defensive |
| 160644 | 鹏华港美互联LOF | Cross-border QDII | Forex quota limit |

## Risk Warnings

1. 信澳 funds (166107/166109/166108): Scale <50M, liquidation risk exists
2. 160644: QDII forex quota may suspend 申购
3. All quant funds: Model失效 risk when market风格 converges to single direction
4. Premium/discount is estimated intraday; actual NAV updates T+1
5. This is data analysis only, not investment advice

## References

- `references/funds_data.md` - Detailed fund parameters, risk metrics, and buy condition matrices
- `scripts/monitor.py` - Data fetching and scoring automation script
- `scripts/config.py` - Alert configuration for push notifications
- `assets/quant_lof_analysis.png` - Fund analysis chart visualization
