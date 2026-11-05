---
name: spx-0dte-gex-analyzer
description: 分析SPX 0DTE期权的Gamma Exposure，为期权交易提供建议。当用户询问SPX gamma exposure、GEX分析、0DTE gamma风险、SPX铁鹰策略建议时使用。
---

# SPX 0DTE Gamma Exposure 分析器

## 概述

此技能实时计算SPX 0DTE期权的Gamma Exposure (GEX)，并根据GEX情况提供期权策略建议。

## 工作流程

### 步骤 1：获取SPX当前数据

获取以下信息：
- SPX当前价格
- SPX期权的Gamma数据（通过0DTE期权链）

### 步骤 2：计算GEX

GEX公式：
```
GEX = Σ (Gamma × OpenInterest × ContractSize × Price)
```

- 正GEX：期权卖家对冲压力推高市场
- 负GEX：期权买家对冲压力跟随市场

### 步骤 3：分析GEX信号

| GEX状态 | 市场影响 | 隐含波动率 |
|---------|----------|------------|
| 高正GEX | 支撑位提供买盘 | IV较低 |
| 高负GEX | 阻力位提供卖盘 | IV较高 |
| 中性 | 盘整格局 | 正常 |

### 步骤 4：提供Iron Condor建议

根据GEX情况调整Iron Condor参数：

**高正GEX（Gamma压制）**：
- 宽wing增加盈利概率
- 缩短delta中性对冲周期
- 关注short gamma风险

**高负GEX（Gamma支撑）**：
- 收窄wing提高收益
- 扩大delta对冲范围
- 把握高IV环境

**中性GEX**：
- 标准IC参数
- 维持常规风险管理

### 步骤 5：计算关键价位

输出：
- 零Gamma点（Gamma flip）
- 最大Gamma压力点
- 支撑/阻力区域
- 建议建仓价位

## 输出格式

```
=== SPX 0DTE GEX 分析 ===

📊 当前GEX: [数值]
📈 市场状态: [支撑/阻力/中性]
🎯 建议Iron Condor参数:
   - 卖出Put: [行权价]
   - 卖出Call: [行权价]
   - 保护Put: [行权价]
   - 保护Call: [行权价]
   - 预期收益: [金额]
   - 最大风险: [金额]

⚠️ 风险提示: [风险说明]
```