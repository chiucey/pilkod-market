---
name: akshare-data
description: 获取 A 股、港股、基金、期货、宏观经济等金融数据。当用户询问股价、行情、财务数据、资金流向、板块涨跌、基金净值、宏观经济指标时激活。支持「贵州茅台最新价」「宁德时代实时行情」「北向资金今日流向」「贵州茅台 ROE」「新能源板块成分股」等查询。
---

# AKShare + Tushare 金融数据

## 环境要求

- Python 3.8+：`/opt/pylib/bin/python3`
- 库：akshare、tushare、requests、beautifulsoup4、lxml

## ts_code 格式（Tushare 专用）

| 交易所 | 代码 | 后缀 | 示例 |
|--------|------|------|------|
| 上海证券交易所 | SSE | `.SH` | 600519.SH、000001.SH |
| 深圳证券交易所 | SZSE | `.SZ` | 000001.SZ、399005.SZ |
| 北京证券交易所 | BSE | `.BJ` | 830942.BJ |
| 香港证券交易所 | HKEX | `.HK` | 00700.HK、00001.HK |

## 脚本

### stock_quote.py — AKShare 行情（无需 Token）

```bash
/opt/pylib/bin/python3 scripts/stock_quote.py "贵州茅台"        # 实时行情
/opt/pylib/bin/python3 scripts/stock_quote.py "贵州茅台" --hist  # 日K线
/opt/pylib/bin/python3 scripts/stock_quote.py "贵州茅台" --fund  # 资金流向
```

### sector.py — AKShare 板块

```bash
/opt/pylib/bin/python3 scripts/sector.py "新能源"               # 行业板块
/opt/pylib/bin/python3 scripts/sector.py "AI" --concept         # 概念板块
```

### tushare_stock.py — Tushare 数据（需 Token）

```bash
/opt/pylib/bin/python3 scripts/tushare_stock.py --basic           # 股票列表
/opt/pylib/bin/python3 scripts/tushare_stock.py --flow           # 沪深港通资金流向
/opt/pylib/bin/python3 scripts/tushare_stock.py --daily --symbol 600519.SH   # 日K线
/opt/pylib/bin/python3 scripts/tushare_stock.py --fin   --symbol 600519.SH   # 财务指标
/opt/pylib/bin/python3 scripts/tushare_stock.py --daily --symbol 00700.HK   # 港股K线
/opt/pylib/bin/python3 scripts/tushare_stock.py --hk-hold          # 港股通持股明细
```

Token 已配置：`84ce99cb1834d03ce83ae4ffc192cd4feab1e838cdb89b8b5e731734`

## 常用接口速查

### AKShare（免费）
- `ak.stock_zh_a_spot_em()` — A 股实时行情
- `ak.stock_zh_a_hist(symbol="000001")` — 历史K线
- `ak.stock_individual_fund_flow(stock="贵州茅台")` — 主力资金
- `ak.stock_board_industry_name_em()` — 行业板块
- `ak.macro_china_gdp_yearly()` — GDP

### Tushare（需 Token）
- `pro.daily(ts_code="600519.SH")` — 日K线
- `pro.fina_indicator_pd(ts_code="600519.SH")` — 财务指标
- `pro.moneyflow_hsgt(start_date, end_date)` — 北向资金
- `pro.hk_hold_top(ths_code="SH")` — 港股通持股

## 注意事项

- 使用 `/opt/pylib/bin/python3` 执行脚本
- 请求间隔建议 > 1 秒