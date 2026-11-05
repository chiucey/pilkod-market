---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 737427582109498add63b3b1303183ad
    PropagateID: 737427582109498add63b3b1303183ad
    ReservedCode1: 3044022071f954de3ca5506242928091063ce979c62388c2e31e5850f01f07cf65162c7e022038b7095f3f10a67a96b33420276cc7626411c8c89b0607927b07450fca8a91ae
    ReservedCode2: 3045022100c1d64552881e059085cabb5410a2d95dc667ac97ee706c98184f2daaad1c847902203827e67e1542e97874a28d7d29e439e5f141ef736aff6285d5b097fbe30b9081
dependency:
    python:
        - akshare>=1.10.0
        - openpyxl>=3.0.0
        - pandas>=2.0.0
description: A股上市公司财务报表查询与导出；支持资产负债表、利润表、现金流量表、财务摘要，按报告期/年度/单季度查询，可导出Excel
name: a-stock-financial
---

# A股财务报表查询

基于 AkShare（同花顺数据源）查询A股上市公司财务报表，支持导出 Excel。

## 查询报表

```bash
# 查所有报表（默认最近4期）
python scripts/fetch_reports.py <股票代码>

# 指定报表类型
python scripts/fetch_reports.py <股票代码> --type income --indicator 按年度 --last 5

# 指定报告期
python scripts/fetch_reports.py <股票代码> --type balance --period 2025-12-31
```

| 参数 | 选项 |
|------|------|
| `--type` | balance / income / cashflow / abstract / all |
| `--indicator` | 按报告期 / 按年度 / 按单季度 |
| `--period` | 指定报告期，如 2025-12-31 |
| `--last` | 最近N期（默认4） |

## 导出 Excel

```bash
python scripts/export_excel.py <股票代码> <公司名称>

# 指定报告期或导出数量
python scripts/export_excel.py 600326 西藏天路 --period 2025-12-31 --last 5
```

导出文件含4个 Sheet：资产负债表、利润表、现金流量表、财务摘要。

## 注意事项

- 股票代码为6位数字（如 600326），不含交易所后缀
- 用户提供公司名时，用 WebSearch 搜索股票代码
- 不要用 `stock_zh_a_spot_em()` 拉全市场行情（极慢）
- 数据源为同花顺，免费无需 token
