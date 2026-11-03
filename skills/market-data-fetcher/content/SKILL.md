---
name: market-data-fetcher
description: 【行情数据获取】获取A股/港股股票行情和基本面数据。当用户要求获取股票数据、查询股价、下载K线、拉取财务报告、查询指数行情、实时报价等任务时使用。支持日线、周线、月线、分钟线（前复权）和实时数据。
---

# 行情数据获取技能

## 数据源（已验证可用）

| 数据源 | 用途 | 状态 | 备注 |
|-------|------|:----:|------|
| **新浪财经** | 实时行情 | ✅ | `hq.sinajs.cn` GBK编码 |
| **腾讯财经** | K线（前复权） | ✅ | `web.ifzq.gtimg.cn` 已修复URL格式 |
| **东方财富** | K线备用 | ⚠️ | `push2his.eastmoney.com` 可能断开 |
| **163财经** | K线备用 | ⚠️ | `quotes.money.163.com` HTTP 502 |

> ⚠️ **重要修复（2026-04-28）**：腾讯财经K线接口URL格式已修正，原格式返回 `bad params`。
> 正确格式：`?_var=kline_dayqfq&param={market}{code},day,{start},{end},{count},qfq`

---

## 核心函数

### get_kline_data（已修复）

获取单只股票K线（前复权）。

```python
from market_data import get_kline_data

data = get_kline_data(
    symbol="600519",      # 必填：股票代码
    period="daily",        # 可选：daily/weekly/monthly/1min~60min（默认: daily）
    start_date="20250101", # 可选：开始日期 YYYYMMDD（默认: 365天前）
    end_date="20260428",  # 可选：结束日期 YYYYMMDD（默认: 今天）
    adjust="qfq"          # 可选：qfq前复权/hfq后复权/none不复权（默认: qfq）
)
# 返回: {"code":0, "data":{"dates":[...], "open":[...], "close":[...], "high":[...], "low":[...], "volume":[...]}, "source": "Tencent Finance"}
```

**返回值示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "symbol": "600519",
    "period": "daily",
    "dates": ["2026-04-01", "2026-04-02"],
    "open": [1459.44, 1459.88],
    "close": [1459.88, 1468.00],
    "high": [1469.99, 1479.93],
    "low": [1452.88, 1450.00],
    "volume": [29125, 61691],
    "turnover": [],
    "count": 60
  },
  "source": "Tencent Finance",
  "timestamp": "2026-04-28T10:30:00"
}
```

---

### get_realtime_quotes

获取实时行情（新浪财经，失败时自动切换腾讯备用）。

```python
from market_data import get_realtime_quotes

data = get_realtime_quotes(
    symbols=["600519", "000001", "688041"]  # 必填：股票代码列表
)
# 返回: {"code":0, "data":{"600519": {"name":"贵州茅台", "close":1405.0, "change_pct":0.13, ...}}}
```

**返回值示例：**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "600519": {
      "symbol": "600519",
      "name": "贵州茅台",
      "close": 1405.0,
      "prev_close": 1403.2,
      "open": 1400.0,
      "high": 1415.0,
      "low": 1398.5,
      "volume": 126500,
      "change": 1.8,
      "change_pct": 0.13,
      "timestamp": "2026-04-28 10:30:00"
    }
  },
  "source": "Sina Finance"
}
```

---

### get_market_data

批量获取K线数据。

```python
from market_data import get_market_data

data = get_market_data(
    symbols=["600519", "000001"],  # 必填
    interval="daily",               # 可选：1m/5m/15m/30m/60m/1d/1w/1mo（默认: 1d）
    start_date="2026-01-01",       # 可选：YYYY-MM-DD
    end_date="2026-04-28",         # 可选：YYYY-MM-DD
    adjust="qfq"                   # 可选：qfq/hfq/none（默认: qfq）
)
```

---

### get_fundamentals

获取基本面数据（财务报表+估值）。

```python
from market_data import get_fundamentals

data = get_fundamentals(symbol="600519")
# 返回财务报表和估值数据
```

---

## 快速使用示例

```python
# 1. 获取K线（前复权日K，修复后的腾讯接口）
from market_data import get_kline_data

kl = get_kline_data("600519", period="daily",
                     start_date="20250101", end_date="20260428")
print(f"K线条数: {kl['data']['count']}, 来源: {kl['source']}")
# → K线条数: 60, 来源: Tencent Finance

# 2. 批量获取实时行情（新浪，失败切腾讯）
from market_data import get_realtime_quotes

qt = get_realtime_quotes(["600519", "300750", "688041"])
for code, info in qt['data'].items():
    print(f"{code}: {info['name']} {info['close']} ({info['change_pct']:+.2f}%)")

# 3. 完整选股流程：实时价格 → K线 → 技术分析
from market_data import get_realtime_quotes, get_kline_data
from technical_analysis import TechnicalIndicators

# Step 1: 获取所有≤15元的股票实时价格
quotes = get_realtime_quotes(["600519", "000001", ...])
under15 = {k:v for k,v in quotes['data'].items() if v.get('close', 999) <= 15.0}

# Step 2: 获取K线数据
for code in under15:
    kl = get_kline_data(code, period="daily")
    closes = kl['data']['close']
    # → 调用 technical_analysis 模块计算RSI/MACD等
```

---

## 缓存策略

| 数据类型 | TTL | 说明 |
|---------|-----|------|
| 实时行情 | 10秒 | 防止频繁请求 |
| 日K数据 | 5分钟 | 盘中/盘后缓存 |
| 分钟K | 1分钟 | 高频数据 |

---

## 故障排除

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| `bad params` | 腾讯K线URL格式错误 | 已修复，使用正确格式 `,day,{dates},...` |
| `Remote end closed` | 东方财富/163被封 | 自动切换到腾讯财经 |
| `GBK decode error` | 编码问题 | 新浪API已设置GBK自动解码 |
| 返回空数组 `[]` | 股票代码/市场错误 | 检查 `normalize_symbol` 格式 |
| 403 Forbidden | 请求频率过快 | 增加 `time.sleep(0.15)` 间隔 |

---

## 合规声明

> 本技能提供数据获取接口，数据的解读和投资决策由用户自行负责。
