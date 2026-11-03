# SPX 0DTE GEX 参考文档

## 什么是 Gamma Exposure (GEX)？

GEX衡量期权市场对标的资产价格波动的潜在影响。

### 计算公式

```
GEX = Σ (Gamma × OpenInterest × ContractMultiplier × SpotPrice)
```

- **正GEX**: 期权卖方需要在下跌时卖出/上涨时买入 → 市场缓冲
- **负GEX**: 期权买方需要在下跌时卖出/上涨时买入 → 市场加速

## GEX解读指南

### GEX值分类

| GEX范围 | 市场信号 | 建议策略 |
|---------|----------|----------|
| > +500M | 强支撑 | 下跌时可买入 |
| +100M ~ +500M | 中性支撑 | 标准IC |
| -100M ~ +100M | 平衡 | 观望 |
| -100M ~ -500M | 中性阻力 | 收窄IC |
| < -500M | 强阻力 | 谨慎做空 |

## Iron Condor 调整逻辑

### 高正GEX (支撑市场)
- 扩大Put wing宽度至120-150点
- 降低short delta暴露
- 等待回调至支撑位买入

### 高负GEX (阻力市场)
- 扩大Call wing宽度至120-150点
- 考虑买入虚值Put对冲
- 把握高IV环境卖出更多IC

### 中性GEX
- 使用标准100点wing
- 维持delta中性对冲
- 关注零gamma点突破

## 数据来源

### 推荐数据源
1. **Polygon.io** - 实时期权数据
2. **Tradier** - 经纪商API
3. **Interactive Brokers** - 全市场数据
4. **Alpaca** - 免费Tier可用

### 数据要求
- SPX 0DTE期权链 (当日到期)
- 每个行权价的OI和Gamma值
- 实时成交价和买卖价差

## 风险提示

⚠️ 0DTE期权具有极高时间价值衰减
⚠️ GEX仅为辅助指标，不构成投资建议
⚠️ 请根据个人风险承受能力调整仓位