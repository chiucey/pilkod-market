# AKShare 期货分析技能

## 技能信息
- **名称**: akshare-skill
- **来源**: ppsteven/trade-skills (https://skills.sh/ppsteven/trade-skills/akshare-skill)
- **安装命令**: `npx skills add https://github.com/ppsteven/trade-skills --skill akshare-skill`

## 简介

AKShare 是 Python 开源金融数据库，专注中国金融市场数据，涵盖期货、股票、债券、宏观等。本技能提供完整的 API 调用文档和分析工作流。

## 核心能力

### 期货数据（ Derivatives & Futures ）
- 期货合约行情（主力合约、指数合约）
- 期货持仓数据（仓单、仓差）
- 期货交割数据
- 商品期权合约、希腊值、隐含波动率

### 其他数据类别
| 类别 | 内容 |
|------|------|
| 股票 | A/B 股历史行情、实时行情、行业板块 |
| 债券 | 国债、企业债、城投债 |
| 宏观 | GDP、CPI、工业产值、消费数据 |
| 外汇 | 人民币中间价、汇率、离岸 USD/CNH |
| 大宗商品 | 原油、天然气、煤炭、贵金属 |
| 数字货币 | 主流币种行情 |

## 使用方式

### CLI 方式（推荐）

```bash
# 期货历史行情
python3 scripts/akshare_cli.py futures_zh_hist --symbol "CU" --start_date 20240101 --end_date 20241231

# 期货持仓排行
python3 scripts/akshare_cli.py futures_spot_stock --symbol "CU"

# 商品期权
python3 scripts/akshare_cli.py options_opt_detail --symbol "CU"

# 主力合约行情
python3 scripts/akshare_cli.py futures_zh_daily_sina
```

### Python 库方式

```python
import akshare as ak

# 期货历史行情
df = ak.futures_zh_hist(symbol="CU", start_date="20240101", end_date="20241231")

# 期货仓单
df = ak.futures_spot_stock(symbol="CU")

# 商品期权详情
df = ak.options_opt_detail(symbol="CU")
```

## 期货常用数据接口速查

| 数据需求 | 函数 |
|---------|------|
| 期货日线行情 | `futures_zh_hist` |
| 期货持仓数据 | `futures_spot_stock` |
| 期货仓单详情 | `futures_spot_goods` |
| 期货成交持仓排名 | `futures_rank_search` |
| 期货主力/指数合约 | `futures_zh_daily_sina` |
| 商品期权希腊值 | `options_opt_greeks` |
| 期货夜盘数据 | `futures_zh_nh` |
| 原油期货 | `futures_oil_price` |

## 安装依赖

```bash
pip install akshare
```

> AKShare 需要联网运行，数据来源包括新浪财经、搜狐财经、东方财富等。
