# Quantitative LOF Fund Reference Data

## Monitored Fund List

| Code | Name | Strategy | Benchmark | Sharpe | MaxDD(%) | Size | Notes |
|------|------|----------|-----------|--------|----------|------|-------|
| 166107 | 信澳量化多因子LOF-A | Multi-factor | CSI 500 | 2.48 | 48.9 | Small | High turnover 881%, extreme risk/reward |
| 166108 | 信澳量化多因子LOF-C | Multi-factor | CSI 500 | 2.48 | 48.9 | Small | C-class, 7-day free redemption |
| 166109 | 信澳量化先锋LOF-A | Stat arbitrage | CSI 500 | 2.20 | 45.0 | Small | Pairs trading strategy |
| 161039 | 富国中证1000增强LOF-A | Index enhance | CSI 1000 | 1.80 | 35.0 | Large | Best liquidity, preferred choice |
| 161035 | 富国中证500增强LOF | Index enhance | CSI 500 | 1.60 | 32.0 | Medium | Balanced risk/reward |
| 501059 | 西部利得国企红利增强LOF | Dividend enhance | CSI SOE Div | 1.40 | 25.0 | Medium | Lowest risk, defensive |
| 160644 | 鹏华港美互联LOF | Cross-border | HST+NDX | 0.81 | 33.9 | Small | QDII-LOF, forex quota risk |

## Buy Condition Matrix

### Premium/Discount Rules
- Premium > +5%: PROHIBIT (overpriced)
- +2% to +5%: AVOID (expensive)
- -1% to +2%: FAIR (acceptable)
- -3% to -1%: GOOD (discount buy)
- <-3%: EXCELLENT (deep discount rare opportunity)

### Score Interpretation
- 80-100: Strong buy - multiple positive factors aligned
- 65-79: Buy - favorable conditions
- 50-64: Cautious buy - some positives but watch risks
- 35-49: Watch - not ideal, wait
- 0-34: Avoid - poor conditions or high risk

### Drawdown-Based Entry
- Drawdown > -15% from recent high: Strong accumulation zone
- Drawdown -8% to -15%: Moderate entry zone
- Drawdown -3% to -8%: Light试探 entry
- Drawdown < -3%: Wait for better entry

## Risk Warnings

1. 信澳 funds (166107/166109): Size < 50M, liquidation risk exists
2. 160644: QDII forex quota may suspend申购
3. All quant funds: Model失效 risk when market风格 converges
4. High turnover funds: 交易成本侵蚀收益
5. C-class funds: 持有<6月优选C, >1年优选A
