---
name: tonghuashun-wencai-stock
description: A股市场综合数据skill（新浪+东方财富免费接口）。无需API key，无需安装任何包。
  - 强势板块TOP5（东方财富证监会行业）
  - 涨停/跌停全览（新浪涨幅榜）
  - 大资金活跃TOP30（成交额/市值比排序）
  - 实时行情（新浪hq.sinajs.cn）
---

# 同花顺+新浪财经数据 Skill

## 数据源（全部免费无限）

| 接口 | 数据源 | 用途 |
|------|--------|------|
| `hq.sinajs.cn` | 新浪财经 | 实时行情（单只/批量） |
| `vip.stock.finance.sina.com.cn` | 新浪涨幅榜 | 涨停/跌停/全市场 |
| `push2.eastmoney.com` | 东方财富 | 证监会行业板块涨跌 |

## 文件

- `scripts/stock_query.py` — 核心查询库（含 `THSWenCaiQuerier` 类）
- `scripts/market_query_final.py` — 市场综合监控脚本（完整三件套）

## 使用方法

### 方法一：直接运行（推荐）

```bash
# 市场综合三件套（板块+涨停跌停+资金）
python3 /workspace/skills/tonghuashun-wencai-stock/scripts/market_query_final.py

# 查询涨停
python3 /workspace/skills/tonghuashun-wencai-stock/scripts/stock_query.py 涨停

# 查询实时行情（多只）
python3 /workspace/skills/tonghuashun-wencai-stock/scripts/stock_query.py sh600036 sz300001 sh688628
```

### 方法二：Python模块调用

```python
import sys
sys.path.insert(0, '/workspace/skills/tonghuashun-wencai-stock/scripts')
from stock_query import (
    get_limit_up, get_limit_down, get_main_flow,
    get_realtime_quote, get_sector_top5,
    THSWenCaiQuerier, fmt_amount
)

# 涨停
stocks = get_limit_up()

# 跌停
stocks = get_limit_down()

# 主力/资金活跃度TOP30
stocks = get_main_flow(30)

# 实时行情
q = get_realtime_quote(['sh600036', 'sz300001'])

# 板块TOP5
sectors = get_sector_top5()

# 成交额格式化
fmt_amount(1350000000)  # → "13.50亿"
```

## 返回字段

### get_limit_up() / get_limit_down()
```python
{'name': '招商银行', 'code': 'sh600036', 'price': 39.58, 'pct': 2.34, 'amount': 1234567890.0}
```

### get_main_flow() — 资金/市值比TOP30
```python
{'name': '神剑股份', 'code': 'sz002361', 'price': 8.88, 'pct': -3.79,
 'amount': 5188000000.0, 'ratio': 0.2936}
# ratio = 成交额(元) / (市值(万元)*10000) = 资金/市值倍数
```

### get_sector_top5() — 强势板块
```python
{'rank': 1, 'name': '半导体', 'pct': 3.45}
```

## 数据限制

| 数据 | 来源 | 限制 |
|------|------|------|
| 涨停/跌停/全市场 | 新浪涨幅榜 | **无限** ✅ |
| 实时行情 | 新浪hq | **无限** ✅ |
| 强势板块 | 东方财富 | **无限** ✅ |
| 主力资金(DDX/DDX) | — | 需要L2付费数据 |

## 股票代码格式

- 沪市：`sh600036`（6开头）
- 深市：`sz300001`（0/3开头）
- 科创板：`sh688xxx`
- 北交所：`bj9xxxxx`
