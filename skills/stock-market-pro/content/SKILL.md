---
name: stock-market-pro
version: 1.4.0
description: 多源股票分析工具。当用户要求查询股票报价、分析股票基本面、生成技术图表(RSI/MACD/BB/VWAP/ATR)、获取综合报告，或需要A股、港股、美股及全球市场分析时使用。支持Yahoo Finance、东方财富、富途牛牛、新浪财经、Wind、Tushare、AkShare等数据源。
author: kys42
license: MIT-0
permissions:
  - read:file
  - write:file
  - network:true
triggers:
  - stock
  - 股票
  - quote
  - 报价
  - chart
  - 图表
  - fundamentals
  - 基本面
  - market
  - 市场
  - A股
  - 港股
  - 美股
  - 东方财富
  - 富途
  - 新浪
  - Wind
  - Tushare
  - yfinance
  - akshare
dependencies:
  python:
    - yfinance
    - akshare
    - efinance
    - pandas
    - numpy
    - matplotlib
  optional:
    tushare: ">=1.2.0"
    futu-api: ">=6.0.0"
    windpy: ">=1.0.0"
environment_variables:
  - TUSHARE_TOKEN
  - WIND_USERNAME
  - WIND_PASSWORD
---

# Stock Market Pro - 多源股票分析技能

## 概述

Stock Market Pro 是一个专业的多源股票分析工具，支持 **Yahoo Finance、东方财富、富途牛牛、新浪财经、Wind、Tushare、AkShare** 七大主流数据源。提供实时报价、基本面数据、技术图表及综合报告，覆盖 **A股、港股、美股及全球市场**。

## 支持的操作

| 操作 | 说明 | 支持数据源 |
|------|------|------------|
| `price` | 获取实时报价 | 所有数据源 |
| `fundamentals` | 获取基本面数据 | dfcf (东方财富) |
| `history` | 获取历史数据 | 所有数据源 |
| `pro` | 生成专业图表(带技术指标) | 所有数据源 |
| `report` | 生成综合分析报告 | 所有数据源 |
| `news` | 搜索相关新闻 | DuckDuckGo |
| `options` | 获取期权链接(美股) | Yahoo Finance |

## 技术指标

- **RSI** - 相对强弱指数 (默认14日)
- **MACD** - 指数平滑异同移动平均线 (12/26/9)
- **BB** - 布林带 (20日，2倍标准差)
- **VWAP** - 成交量加权平均价
- **ATR** - 平均真实波幅 (14日)

## 数据源选择指南

| 用户类型 | 推荐数据源 | 说明 |
|---------|-----------|------|
| A股个人投资者 | 东方财富 (dfcf) | 数据最全，免费，无门槛 |
| 港股/美股跨境 | 富途牛牛 (futu) | 需运行 OpenD，行情分析强 |
| 全球资讯覆盖 | 新浪财经 (sina) | 40+市场，资讯快 |
| 量化入门/个人开发 | Tushare | 需 token，免费版够用 |
| 机构专业需求 | Wind | 需 Wind 终端及账号 |
| 免费开源首选 | AkShare | 无需配置，覆盖广 |
| 国际股票/加密/外汇 | Yahoo Finance (yfinance) | 全球市场通用 |

## 使用方法

### 基础查询

```
action: "price"
ticker: "AAPL" 或 "600519" 或 "00700.HK"
data_source: "auto" | "dfcf" | "futu" | "sina" | "tushare" | "wind" | "akshare" | "yfinance"
```

### 示例调用

```python
# 获取实时报价
run({"action": "price", "ticker": "AAPL", "data_source": "yfinance"})

# 获取A股基本面 (东方财富)
run({"action": "fundamentals", "ticker": "600519", "data_source": "dfcf"})

# 生成技术图表
run({
    "action": "pro",
    "ticker": "000001",
    "data_source": "dfcf",
    "period": "6mo",
    "indicators": ["rsi", "macd", "bb"]
})

# 生成综合报告
run({"action": "report", "ticker": "00700.HK", "data_source": "futu", "period": "1y"})
```

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| action | string | "price" | 操作类型 |
| ticker | string | 必需 | 股票代码 |
| data_source | string | "auto" | 数据源选择 |
| period | string | "6mo" | 历史数据周期 (1mo/3mo/6mo/1y) |
| chart_type | string | "candlestick" | 图表类型 |
| indicators | array | ["rsi", "macd", "bb"] | 技术指标列表 |
| max_results | int | 8 | 新闻搜索最大条数 |

## 股票代码格式

- **美股**: 直接使用代码，如 `AAPL`, `TSLA`, `MSFT`
- **A股**: 6位数字，如 `600519` (上海), `000001` (深圳)
- **港股**: 4-5位数字或带.HK后缀，如 `00700`, `00700.HK`

## 环境配置

### 必需依赖
```bash
pip install yfinance akshare efinance pandas numpy matplotlib
```

### 可选依赖
```bash
pip install tushare                    # Tushare 数据源
pip install futu-api                   # 富途牛牛 (需运行 OpenD)
# Wind 需安装 WindPy (来自 Wind 终端)
```

### 环境变量 (可选)
```bash
export TUSHARE_TOKEN="your_token"
export WIND_USERNAME="username"
export WIND_PASSWORD="password"
```

## 注意事项

- 富途牛牛需提前运行 OpenD 网关 (默认端口 11111)
- Tushare 免费版有 API 调用频率限制
- Wind 数据源需要购买 Wind 终端
- 图表文件保存在 `/tmp` 目录
- 本工具仅供参考，不构成投资建议
- 请遵守各数据平台的使用条款

## 数据源智能路由

当 `data_source` 设置为 `"auto"` 时，系统会根据股票代码自动选择最优数据源：

- **美股代码** (如 `AAPL`) → Yahoo Finance
- **A股代码** (6位数字) → 东方财富
- **港股代码** (4-5位数字) → 富途牛牛
- **其他** → AkShare
