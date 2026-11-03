---
name: stock-intel
description: 股票信息综合查询 Skill — 融合 Baostock（涓流历史数据）+ AKShare（实时扫描）+ QVERIS（专业API工具发现）。当用户需要查询股票数据、分析行情、研究基本面时触发。
---

# Stock Intel Skill — 三合一股票信息引擎

## 数据源三角定位

```
  Baostock          AKShare            QVERIS
  ─────────         ─────────          ─────────
  历史K线           实时行情            专业API工具发现
  涓流API           市场扫描            财报/研报/事件
  财务数据          宏观指标            舆情分析
  分红送转          期货外汇            深度财务指标
```

## 核心原则

1. **涓流优先**：历史数据用 Baostock（稳定，不限流）
2. **实时扫描**：当日行情、市场概貌用 AKShare
3. **深度挖掘**：财报、研报、事件舆情用 QVERIS 发现工具后再调用
4. **三者互补**：单一数据源不足时启用下一层

## 执行流程

### 第一步：解析需求，确定数据层

用户请求分析股票时，判断需要哪层数据：

| 需求 | 数据层 |
|------|--------|
| 历史K线、技术指标 | Baostock |
| 当日股价、涨跌幅、成交量 | AKShare |
| 市场概貌、板块涨跌、情绪 | AKShare |
| 财报、利润表、资产负债表 | QVERIS |
| 研报摘要、目标价、评级 | QVERIS |
| 事件舆情、重大公告 | QVERIS |
| 实时预警、量化筛选 | Baostock + AKShare |

### 第二步：调用数据

#### Baostock（Python，直接调用）

```python
import baostock as bs
bs.login()
# 历史K线
rs = bs.query_history_k_data_plus('sz.000001',
    'date,code,open,high,low,close,volume,turn',
    start_date='2025-01-01', end_date='2026-03-28', frequency='d')
# 财务摘要
rs = bs.query财务摘要(start_date='2025-12-31')
bs.logout()
```

#### AKShare（Python，直接调用）

```python
import akshare as ak
# 实时行情
df = ak.stock_zh_a_spot_em()
# 指数实时
df = ak.stock_zh_index_spot_em()
# 资金流向
df = ak.stock_individual_fund_flow(stock="000001")
# 龙虎榜
df = ak.stock_lhb_detail_em(date="20260328")
```

#### QVERIS（发现→调用，两步走）

```bash
# Step 1: 发现工具
node ~/.openclaw/skills/qveris-official/scripts/qveris_tool.mjs discover "Chinese stock financial report API"

# Step 2: 调用工具（用discover返回的tool_id）
node ~/.openclaw/skills/qveris-official/scripts/qveris_tool.mjs call <tool_id> \
  --discovery-id <search_id> \
  --params '{"symbol": "600519"}'
```

### 第三步：聚合输出

三源数据到位后，按统一格式输出：

```json
{
  "stock": "600519",
  "company": "贵州茅台",
  "layers": {
    "baostock": { "data": {...} },
    "akshare":  { "data": {...} },
    "qveris":   { "data": {...} }
  }
}
```

## 注意事项

- Baostock 有频率限制，K线请求间隔 > 1秒
- AKShare 为爬虫数据，建议缓存当天数据
- QVERIS 需 `QVERIS_API_KEY` 环境变量
- 三源数据可能有微小差异，以 Baostock 历史数据为准
