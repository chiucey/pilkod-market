# 数据源 API 参考

## A股数据 (akshare)

### 实时行情

```python
import akshare as ak

# A股实时行情（全部）
stock_zh_a_spot = ak.stock_zh_a_spot_em()

# 个股信息
stock_info = ak.stock_individual_info_em(symbol="600519")

# 实时涨跌排行
stock_zh_a_change_ratio = ak.stock_zh_a_change_ratio_em()
```

### 历史数据

```python
# A股历史K线
stock_hist = ak.stock_zh_a_hist(
    symbol="600519",
    period="daily",  # 日线
    start_date="20240101",
    end_date="20240131",
    adjust="qfq"  # 前复权
)

# 返回字段：日期、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅、涨跌额、换手率
```

### 指数数据

```python
# 沪深指数实时行情
index_spot = ak.stock_zh_index_spot_em()

# 上证系列指数
index_sh = ak.stock_zh_index_spot_sina(symbol="上证系列指数")

# 深证系列指数
index_sz = ak.stock_zh_index_spot_sina(symbol="深证系列指数")
```

### 板块数据

```python
# 行业板块实时行情
sector_spot = ak.stock_sector_spot(indicator="实时")

# 概念板块实时行情
concept_spot = ak.stock_board_concept_spot_em()

# 行业板块历史涨跌统计
sector_detail = ak.stock_sector_detail(symbol="半导体")
```

### 资金流向

```python
# 市场资金流向
money_flow = ak.stock_market_day_zj_EM()

# 个股资金流向
stock_money_flow = ak.stock_individual_fund_flow(stock="600519")
```

### 龙虎榜

```python
# 龙虎榜详情
lhb_detail = ak.stock_lhb_detail_em()

# 龙虎榜统计
lhb_statistic = ak.stock_lhb_statistic_em()

# 个股龙虎榜
stock_lhb = ak.stock_lhb_detail_em(symbol="000001")
```

### 涨跌停

```python
from datetime import datetime

# 当前日期
current_date = datetime.now().strftime("%Y%m%d")

# 涨停股池
limit_up = ak.stock_zt_pool_em(date=current_date)

# 跌停股池
limit_down = ak.stock_zt_pool_em(date=current_date, zt_limit="down")
```

---

## 港股数据

### 实时行情

```python
# 港股实时行情
hk_spot = ak.stock_hk_spot_em()

# 港股个股实时行情
hk_stock_spot = ak.stock_hk_stock_spot_em(symbol="00700")
```

### 历史数据

```python
# 港股历史K线
hk_hist = ak.stock_hk_hist(
    symbol="00700",
    period="daily",
    start_date="20240101",
    end_date="20240131",
    adjust="qfq"
)
```

### 南向资金

```python
# 港股通南向资金
hk_south = ak.stock_hk_south_trade统计(date=current_date)
```

---

## 美股数据 (yfinance)

### 主要指数

```python
import yfinance as yf

# 标普500
sp500 = yf.Ticker("^GSPC")

# 纳斯达克
nasdaq = yf.Ticker("^IXIC")

# 道琼斯
dow = yf.Ticker("^DJI")
```

### 历史数据

```python
# 获取历史数据
sp500_hist = sp500.history(period="5d")  # 最近5个交易日

# 获取指定日期范围
sp500_range = sp500.history(start="2024-01-01", end="2024-01-31")
```

### 个股数据

```python
# 苹果公司
aapl = yf.Ticker("AAPL")

# 基本信息
info = aapl.info

# 财务数据
financials = aapl.financials
balance_sheet = aapl.balance_sheet
cash_flow = aapl.cashflow

# 历史价格
history = aapl.history(period="1mo")
```

---

## 数据时间说明

| 市场 | 交易时间 | 数据更新 |
|------|----------|----------|
| A股 | 9:30-11:30, 13:00-15:00 | 盘中实时，收盘后15:30更新 |
| 港股 | 9:30-12:00, 13:00-16:00 | 盘中实时，收盘后16:30更新 |
| 美股 | 21:30-04:00 (北京时间) | 盘中实时，收盘后05:00更新 |
