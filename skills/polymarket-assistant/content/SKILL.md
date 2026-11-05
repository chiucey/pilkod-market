---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e10dd8e461850cde803f8db5762a8950
    PropagateID: e10dd8e461850cde803f8db5762a8950
    ReservedCode1: 30450220576d0b3890abdf6d0ca293791c8aebacd01bfddb8ac432ef56725448590a4223022100bff3a9707e117063b3c921078537baf73ade0021ab9ecd37e0ef45c577e030d7
    ReservedCode2: 3046022100f74bac09051207c492a3524ab2f1075023381a8f0e2debba009c13ef2d16300b022100a1b32709895d2ff781fe22eb56420efed1ea7e310fe3dc91ff0646162a9c52b1
description: |-
    当用户需要以下场景时使用：
    - 查询 Polymarket 预测市场的热门话题和趋势
    - 根据关键词（如"美国大选"、"美联储利率"）搜索相关市场
    - 查看特定市场的赔率和概率数据
    - 查询用户在 Polymarket 上的资产余额和持仓情况
    - 尝试在 Polymarket 上进行买入或卖出交易操作
    - 了解某个预测市场话题的历史数据和成交量
name: polymarket-assistant
---

# Polymarket Assistant

Polymarket 是一个基于区块链的预测市场平台。本技能帮助用户查询市场数据、账户信息和进行交易操作。

## 核心功能

### 1. 市场数据查询

- **热门市场**：获取当前最热门的预测市场话题
- **关键词搜索**：根据用户输入的关键词搜索相关市场
- **市场详情**：查看特定市场的当前赔率、概率、成交量等信息

### 2. 账户信息查询

- **资产余额**：查看用户在 Polymarket 上的 USDC 余额
- **持仓情况**：查看用户当前正在进行的投注和潜在收益
- **历史记录**：查询用户的交易历史

### 3. 交易操作（可选）

- **买入**：对某个市场的结果进行投注
- **卖出**：平仓或出售持有的头寸

## 使用方法

### 查询热门市场

```
搜索 Polymarket 的热门预测市场
```

### 搜索特定话题

```
搜索 Polymarket 关于"美国大选"的市场
查询"美联储利率"的预测市场
```

### 查看市场详情

```
查看 [市场ID] 的详细赔率
查询这个市场的当前价格
```

### 账户操作

```
查看我的 Polymarket 余额
显示我的持仓情况
```

### 交易操作

```
我想买入 [市场] 的 [结果] 选项
卖出我在 [市场] 的持仓
```

## 配置要求

本技能需要以下配置：

- **API Key**：Polymarket API 密钥（可选，用于账户操作）
- **钱包地址**：用户的 Web3 钱包地址

## 注意事项

- 所有交易操作涉及真实资金，请用户确认后再执行
- 市场赔率会实时变化，显示的数据仅供参考
- 部分高级功能可能需要 API Key 才能使用
