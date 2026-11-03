---
name: a-stock-realtime-price
description: 获取A股/ETF实时股价的技能。当用户询问持仓股实时价格、分析盈亏、查询当前股价时触发。支持腾讯行情（优先）和QVeris API两种方式查询。
---

# A股/ETF实时股价查询

## 方式一：腾讯行情（优先）

**URL格式**（用户浏览器直接访问）：
- 深圳ETF/股票：`https://gu.qq.com/sz{代码}/gp`
- 上海ETF/股票：`https://gu.qq.com/sh{代码}/gp`

示例：
- 芯片ETF：https://gu.qq.com/sz159995/gp
- 爱旭股份：https://gu.qq.com/sh600732/gp

> 此方式为动态页面，AI工具端无法读取，需告知用户直接在浏览器打开。

---

## 方式二：QVeris API（工具调用）

### 前置准备
- API Key：需要自己去注册，没有注册提示，并弹出注册地址
- 注册地址：https://qveris.ai/account?page=api-keys

### 查询步骤

**第一步：搜索工具**（获取 search_id）

POST https://qveris.ai/api/v1/search

Headers: Authorization: Bearer <API_KEY>

Body: {"query": "stock price real time China A share", "limit": 5}


**第二步：执行查询**

POST https://qveris.ai/api/v1/tools/execute?tool_id=ths_ifind.real_time_quotation.v1

Headers: Authorization: Bearer <API_KEY>

Body: {

"search_id": "<第一步返回的search_id>",

"parameters": {

"codes": "159995.SZ,600732.SH,603906.SH",

"indicators": "latest,change,changeRatio,open,high,low,volume"

},

"max_response_size": 20480

}


### codes格式规范
- 必须带 `.SZ` 或 `.SH` 后缀，代码前**不加** sz/sh 前缀
- 多只股票用逗号分隔：`159995.SZ,600732.SH,603906.SH`

### 常用股票代码（A股/ETF）

| 标的 | 代码 |
|---|---|
| 芯片ETF | 159995.SZ |
| 半导体设备ETF | 159516.SZ |
| 爱旭股份 | 600732.SH |
| 龙蟠科技 | 603906.SH |
| 朗姿股份 | 002612.SZ |
| 健康元 | 600380.SH |
| 红利ETF | 510880.SH |
| 恒生科技ETF | 513180.SH |
| 国电电力 | 600795.SH |
| 地产ETF | 159707.SZ |
| 医药ETF | 159929.SZ |
| 医疗ETF | 159828.SZ |

---

## 查询优先级

1. **优先**：用户发持仓截图 → images_understand OCR 读数（最准）
2. **其次**：腾讯行情 URL（用户浏览器直接开）
3. **最后**：QVeris API（工具调用，作为备选）

---

## 响应格式

查询成功后，将数据整理为以下格式：

标的 | 现价 | 今日涨跌 | 成本价 | 盈亏额 | 盈亏%


示例：
龙蟠科技 | 22.52 | +0.45%🟢 | 15.02 | +1,500 | +49.7%

爱旭股份 | 14.01 | -4.37%🔴 | 13.66 | +177 | +2.6%
