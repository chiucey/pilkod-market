---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 04d00af95ceaa7a1bc1cd5f1ef30b894
    PropagateID: 04d00af95ceaa7a1bc1cd5f1ef30b894
    ReservedCode1: 3046022100e2cb53424b2f80ddcd029911ce3fa7eefe7289931764b8de48022d971000dc00022100cab9ef99a6bc91c6b5e42409881408d46393940adf37fa01cbc46d14f5dc1dee
    ReservedCode2: 304502202f6efab0d76e292b8a8e62e1725d48f3dd771e3c0b6f12086ec27146fc5e075e022100e761a96acb0f1c328618e8b2b74ba0ebd0eefe4d44539d3a354947b9d53e5f53
description: 实时获取外汇汇率和贵金属价格。当用户询问汇率、黄金价格、白银价格、贵金属行情、外汇报价、货币兑换等问题时使用。支持主流货币对（USD/CNY、EUR/CNY、GBP/CNY、JPY/CNY等）和贵金属（黄金、白银、铂金）。
name: realtime-finance-quotes
---

# 实时金融行情技能

## 首次使用配置

**重要提示**：使用贵金属功能前，用户需要配置以下API密钥（至少一个）。

### 获取API密钥

**API 1: Metal Price API**
1. 访问 [api.metalpriceapi.com](https://api.metalpriceapi.com) 注册账户
2. 在个人账户中获取API密钥
3. 环境变量名：`METAL_PRICE_API_KEY`

**API 2: Metals.dev**
1. 访问 [metals.dev](https://metals.dev) 注册账户
2. 在个人账户中获取API密钥
3. 环境变量名：`METALS_DEV_API_KEY`

### 配置方式

**用户需要提供自己的贵金属API密钥**。在首次使用贵金属功能时，系统会提示用户输入API密钥进行配置。

**推荐配置**：同时配置两个API密钥，当一个接口额度不足时自动切换到另一个。

---

## 触发条件

当用户询问以下类型问题时触发：
- 汇率查询（"今天美元兑人民币汇率多少"、"USD/CNY报价"）
- 黄金价格（"现在黄金多少钱"、"金价走势"）
- 白银/铂金价格（"白银价格"、"铂金报价"）
- 贵金属行情（"贵金属价格"）
- 货币兑换计算（"100美元换多少人民币"）
- 综合行情查询（"今日金融行情"）

## 执行流程

### 步骤1：检查API配置

**外汇汇率**：使用公开API，无需配置
```
https://api.exchangerate-api.com/v4/latest/{base_currency}
```

**贵金属API（按优先级排序）**：
1. **Primary**: Metal Price API - 检查 `METAL_PRICE_API_KEY`
2. **Fallback**: Metals.dev - 检查 `METALS_DEV_API_KEY`

### 步骤2：识别查询类型

根据用户输入判断查询类型：

| 查询类型 | 识别关键词 | 优先级 |
|----------|-----------|--------|
| 外汇汇率 | 汇率、兑换、货币、美元、欧元、英镑、日元 | 高 |
| 黄金价格 | 黄金、金价、金子、XAU、gold | 高 |
| 白银价格 | 白银、银价、silver、XAG | 中 |
| 铂金价格 | 铂金、铂金价格、platinum、XPT | 中 |
| 综合行情 | 行情、报价、实时 | 中 |

### 步骤3：调用数据源

**外汇汇率 API**（无需配置）：
```
https://api.exchangerate-api.com/v4/latest/{base_currency}
```
示例：获取USD为基础的所有汇率 `https://api.exchangerate-api.com/v4/latest/USD`

**贵金属 API 1 - Metal Price API**：
```
https://api.metalpriceapi.com/v1/latest?api_key={METAL_PRICE_API_KEY}&base=USD&currencies=XAU,XAG,XPT,CNY
```

**贵金属 API 2 - Metals.dev**：
```
https://api.metals.dev/v1/latest?api_key={METALS_DEV_API_KEY}&currency=USD&unit=toz
```

### 步骤4：自动切换逻辑

```
尝试 Metal Price API
    ↓ 成功
返回数据
    ↓ 失败（配额不足/错误）
切换到 Metals.dev
    ↓ 成功
返回数据
    ↓ 失败
返回错误信息，提示检查API配置
```

### 步骤5：数据处理与格式化

提取并格式化响应数据：

**外汇汇率格式**：
```
💱 外汇汇率 (更新时间: {时间})
━━━━━━━━━━━━━━━━━━
USD/CNY  : {汇率} ({涨跌}%)
EUR/CNY  : {汇率} ({涨跌}%)
GBP/CNY  : {汇率} ({涨跌}%)
JPY/CNY  : {汇率} ({涨跌}%)
EUR/USD  : {汇率}
GBP/USD  : {汇率}
USD/JPY  : {汇率}
━━━━━━━━━━━━━━━━━━
```

**贵金属格式**：
```
🥇 贵金属行情 (更新时间: {时间})
━━━━━━━━━━━━━━━━━━
黄金 (XAU/USD) : ${价格} ({涨跌}%)
白银 (XAG/USD) : ${价格} ({涨跌}%)
铂金 (XPT/USD) : ${价格} ({涨跌}%)
━━━━━━━━━━━━━━━━━━
```

### 步骤6：货币转换计算（可选）

如用户请求货币转换，使用公式：
```
目标金额 = 源金额 × 目标汇率
```

## 数据源说明

| 数据类型 | 数据源 | 是否需要配置 |
|----------|--------|--------------|
| 外汇汇率 | exchangerate-api.com | 否（公开API） |
| 贵金属 | Metal Price API / Metals.dev | **是（需API密钥）** |

### API配额说明

| API | 套餐 | 每月请求次数 | 更新频率 |
|-----|------|-------------|----------|
| Metal Price API | 免费版 | 500次/月 | 实时 |
| Metals.dev | 免费版 | 100次/月 | 实时 |

## 错误处理

1. **缺少API密钥**：提示用户先配置至少一个贵金属API密钥
2. **Primary API失败**：自动切换到Fallback API
3. **所有API失败**：返回友好错误信息，提示检查API配置或配额
4. **不支持的货币对**：提示用户选择支持的货币

## 输出规范

- 所有价格保留2位小数
- 涨跌用颜色标注：涨↑(绿色)、跌↓(红色)、平➖(灰色)
- 必须显示数据更新时间
- 标注数据来源

## 快速响应模板

**汇率查询响应**：
> 💱 **实时汇率** (更新: {时间})
>
> | 货币对 | 汇率 | 涨跌 |
> |--------|------|------|
> | USD/CNY | {rate} | {change}% |
> | EUR/CNY | {rate} | {change}% |
> | ... |
>
> 数据来源: exchangerate-api

**贵金属响应**：
> 🥇 **贵金属行情** (更新: {时间})
>
> | 品种 | 价格 (USD) | 涨跌 |
> |------|------------|------|
> | 黄金 | ${price} | {change}% |
> | 白银 | ${price} | {change}% |
>
> 数据来源: Metal Price API / Metals.dev
