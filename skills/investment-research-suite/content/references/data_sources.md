# 数据源参考

## A股/港股数据

### akshare（推荐）

```python
import akshare as ak

# === 股票行情 ===
stock_zh_a_spot_em()      # A股实时行情
stock_zh_index_spot_em() # 沪深指数实时行情
stock_hk_spot_em()        # 港股实时行情

# === 历史数据 ===
stock_zh_a_hist(symbol="600519", period="daily", adjust="qfq")
stock_hk_hist(symbol="00700", period="daily", adjust="qfq")

# === 财务数据 ===
stock_individual_info_em(symbol="600519")
stock_balance_sheet_by_report_em(symbol="600519")
stock_profit_sheet_by_report_em(symbol="600519")
stock_cash_flow_sheet_by_report_em(symbol="600519")
stock_financial_analysis_indicator(symbol="600519")
stock_financial_analysis_dupont(symbol="600519")

# === 板块数据 ===
stock_sector_spot(indicator="实时")
stock_board_concept_spot_em()

# === 资金流向 ===
stock_market_day_zj_EM()

# === 龙虎榜 ===
stock_lhb_detail_em()

# === 涨跌停 ===
stock_zt_pool_em(date=current_date)
```

## 美股数据

### yfinance

```python
import yfinance as yf

# 主要指数
sp500 = yf.Ticker("^GSPC")    # 标普500
nasdaq = yf.Ticker("^IXIC")   # 纳斯达克
dow = yf.Ticker("^DJI")      # 道琼斯

# 个股数据
stock = yf.Ticker("AAPL")
info = stock.info              # 估值指标
financials = stock.financials  # 利润表
balance_sheet = stock.balance_sheet  # 资产负债表
stock.history(period="1y")    # OHLCV价格历史
stock.recommendations          # 分析师建议
```

## 网络数据源

### 券商研报
- 搜索：`[股票名称] 研报`
- 搜索：`[股票名称] 目标价`
- 搜索：`[股票名称] 盈利预测`

### 新闻数据
- 东方财富、同花顺
- 主流财经媒体
- 公司公告

## 数据时效性

| 数据类型 | 更新频率 | 建议时间范围 |
|----------|----------|--------------|
| 实时行情 | 盘中实时 | 当日 |
| 日K线 | 日终更新 | 最近1年 |
| 财务数据 | 季报/年报 | 最近4期财报 |
| 资金流向 | 日终更新 | 最近5日 |
| 龙虎榜 | 日终更新 | 最近5日 |
