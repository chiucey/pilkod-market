# 数据源API参考文档

## 一、A股数据接口

### 1.1 东方财富API

#### 行业板块列表
```python
# 接口地址
URL = "http://push2.eastmoney.com/api/qt/clist/get"

# 请求参数
params = {
    "pn": 1,              # 页码
    "pz": 50,             # 每页数量
    "po": 1,              # 排序方向 1:降序 -1:升序
    "np": 1,              # 是否用新格式
    "ut": "bd1d9ddb04089700cf9c27f6f7426281",
    "fltt": 2,            # 行情类型 1:旧行情 2:新行情
    "invt": 2,            # 数据类型 2:新格式
    "fid": "f3",          # 排序字段 f3:涨幅 f62:主力净流入
    "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",  # 板块筛选
    "fields": "f1,f2,f3,f12,f14,f62,f184",  # 返回字段
}

# 字段说明
"""
f1: 股票代码
f2: 最新价
f3: 涨跌幅
f12: 代码
f14: 名称
f62: 主力净流入
f184: 主力净流入占比
"""
```

#### 概念板块列表
```python
# 概念板块接口
URL = "http://push2.eastmoney.com/api/qt/clist/get"
params = {
    "pn": 1,
    "pz": 100,
    "po": 1,
    "np": 1,
    "ut": "bd1d9ddb04089700cf9c27f6f7426281",
    "fltt": 2,
    "invt": 2,
    "fid": "f3",
    "fs": "m:0+t:80",  # 概念板块
    "fields": "f2,f3,f12,f14,f62,f184",
}
```

### 1.2 同花顺API

#### 板块资金流向
```python
# 接口地址
URL = "http://data.10jqka.com.cn/funds/ggzjl/"

# 请求参数
params = {
    "page": 1,
    "field": "199112,9001,9086,3322,9003,9087,3323,9088,3324",
    "order_field": 9001,
    "order_type": 0,
    "ajax": 1,
}
```

#### 行业板块数据
```python
URL = "http://data.10jqka.com.cn/industry/hy/"

params = {
    "page": 1,
    "field": "stockcode,name,price,change,change_pct,volume,amount",
    "order_field": "change_pct",
    "order_type": 0,
    "ajax": 1,
}
```

### 1.3 聚合数据/AKShare

```python
import akshare as ak

# 获取A股板块列表
ak.stock_board_industry_name_em()

# 获取行业板块实时行情
ak.stock_board_industry_cons_em(symbol="新能源")

# 获取概念板块列表
ak.stock_board_concept_name_em()

# 获取概念板块成分股
ak.stock_board_concept_cons_em(symbol="锂电池")
```

## 二、港股数据接口

### 2.1 港交所披露易API

#### 上市公司列表
```python
# 港交所上市公司列表
URL = "https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx"
```

#### 行业分类
```python
# 恒生行业分类 (HSICS)
# Level 1: 11个行业
# Level 2: 24个子行业
# Level 3: 69个行业组

industries = {
    "01": {"name_cn": "能源业", "name_en": "Energy"},
    "02": {"name_cn": "原材料业", "name_en": "Materials"},
    "03": {"name_cn": "工业", "name_en": "Industrials"},
    "08": {"name_cn": "电讯业", "name_en": "Telecommunications"},
    "09": {"name_cn": "公用事业", "name_en": "Utilities"},
    "10": {"name_cn": "金融业", "name_en": "Financials"},
    "11": {"name_cn": "地产建筑业", "name_en": "Real Estate"},
    "14": {"name_cn": "资讯科技业", "name_en": "Information Technology"},
    "15": {"name_cn": "非必需消费", "name_en": "Consumer Discretionary"},
    "16": {"name_cn": "必需消费", "name_en": "Consumer Staples"},
    "17": {"name_cn": "医疗保健业", "name_en": "Health Care"},
}
```

### 2.2 富途API

```python
# 富途港股数据
import futu as ft

# 连接行情服务
quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11111)

# 获取港股列表
stock_list = quote_ctx.get_plate_list(ft.PlateType.INDUSTRY)

# 获取板块成分股
stocks = quote_ctx.get_plate_stocks("HK.HSI")

# 断开连接
quote_ctx.close()
```

### 2.3 AKShare港股接口

```python
import akshare as ak

# 获取港股行业板块
ak.hk_sector_summary()

# 获取港股板块行情
ak.hk_sector_cons(symbol="科技")

# 获取恒生指数成分股
ak.hk_hs_const()
```

## 三、美股数据接口

### 3.1 Yahoo Finance API

```python
import yfinance as yf

# 获取板块ETF数据
xlk = yf.Ticker("XLK")  # Technology Sector
xlv = yf.Ticker("XLV")  # Health Care Sector

# 获取历史数据
hist = xlk.history(period="1mo")

# 获取基本信息
info = xlk.info
print(f"PE Ratio: {info['trailingPE']}")
print(f"Market Cap: {info['marketCap']}")
```

### 3.2 Finviz API

```python
import finviz

# 获取板块概览
for sector in finviz.util.get_sectors():
    print(sector)

# 获取行业列表
for industry in finviz.util.get_industries():
    print(industry)

# 筛选特定板块股票
stock_filter = {
    'sector': 'Technology',
    'market_cap': 'Large',
    'pe_ratio': '<20',
}
stocks = finviz Screener (filters=[stock_filter])
```

### 3.3 SEC EDGAR API

```python
# SEC EDGAR 公司查找
URL = "https://www.sec.gov/cgi-bin/browse-edgar"

params = {
    "action": "getcompany",
    "CIK": "0000320193",  # Apple
    "type": "10-K",
    "dateb": "",
    "owner": "include",
    "count": "40",
    "search_text": "",
}
```

### 3.4 AKShare美股接口

```python
import akshare as ak

# 获取美股板块ETF
ak.us_sector_etf()

# 获取美股行业ETF
ak.us_industry_etf()

# 获取主要指数成分股
ak.us_指数_sample()
```

## 四、通用数据接口

### 4.1 Tushare Pro API

```python
import tushare as ts

# 设置token
ts.set_token('your_token')
pro = ts.pro_api()

# 获取A股行业分类
df = pro.index_classify(level='L1', src='SW')

# 获取行业日行情
df = pro.daily_basic(
    ts_code='000001.SZ',
    trade_date='20240101',
    fields='ts_code,trade_date,close,turnover_rate,pe,pb'
)

# 获取资金流向
df = pro.moneyflow(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240131'
)
```

### 4.2 东方财富Choice接口

```python
# Choice数据接口（需要授权）
import efinance as ef

# 获取行业板块数据
df = ef.stock.get_sector_list()

# 获取板块成分股
df = ef.stock.get_sector_stocks('新能源汽车')

# 获取板块历史行情
df = ef.stock.get_sector_hist('新能源汽车', beg=20240101, end=20240401)
```

## 五、宏观数据接口

### 5.1 国家统计局API

```python
# 统计局数据
URL = "https://data.stats.gov.cn/easyquery.htm"

params = {
    "m": "QueryData",
    "dbcode": "hgyd",     # 宏观经济
    "rowcode": "zb",      # 指标
    "colcode": "sj",      # 时间
    "wds": "[]",
    "dfwds": '[{"wdcode":"zb","valuecode":"A010101"}]',
    "k1": "1234567890",
}
```

### 5.2 世界银行API

```python
import wbdata

# 设置数据源
wbdata.set_data_source(API.source)

# 获取GDP数据
indicator = wbdata.indicators.get('NY.GDP.MKTP.CD')
data = wbdata.get_dataframe(
    {indicator['id']: 'GDP'},
    country=['CN', 'US', 'HK'],
    date=range(2020, 2024)
)
```

## 六、数据获取模板

### 6.1 完整数据获取流程

```python
def fetch_sector_data(sector_name: str, market: str = "A") -> dict:
    """
    通用板块数据获取函数
    """
    import requests
    import pandas as pd

    data = {
        "sector_name": sector_name,
        "market": market,
        "timestamp": datetime.now().isoformat(),
        "basic_info": {},
        "valuation": {},
        "money_flow": {},
        "stocks": []
    }

    if market == "A":
        # 东方财富数据
        url = "http://push2.eastmoney.com/api/qt/clist/get"
        # ... 数据获取逻辑
        pass
    elif market == "HK":
        # 港股数据
        # ...
        pass
    elif market == "US":
        # 美股数据
        # ...
        pass

    return data
```

### 6.2 数据清洗模板

```python
def clean_sector_data(raw_data: dict) -> dict:
    """
    数据清洗函数
    """
    cleaned = {}

    # 处理空值
    for key, value in raw_data.items():
        if value is None or value == '':
            cleaned[key] = 0
        else:
            cleaned[key] = value

    # 格式化数字
    if 'pe' in cleaned:
        cleaned['pe'] = round(float(cleaned['pe']), 2)

    if 'market_cap' in cleaned:
        # 转换为亿元
        cleaned['market_cap_yi'] = round(cleaned['market_cap'] / 1e8, 2)

    return cleaned
```

## 七、数据更新频率

| 数据类型 | 更新频率 | 延迟 | 建议获取时间 |
|---------|---------|------|------------|
| 实时行情 | 实时 | <1秒 | 交易时段 |
| 资金流向 | 日频 | 收盘后15分钟 | 16:00-17:00 |
| 财务数据 | 季频 | 财报发布后 | 定期更新 |
| 估值数据 | 日频 | 收盘后 | 16:30后 |
| 宏观数据 | 月频 | 数据发布后 | 月初 |
