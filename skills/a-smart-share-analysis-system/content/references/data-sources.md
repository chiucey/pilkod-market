# 数据源配置参考

## 免费数据源

### 1. AKShare
```python
import akshare as ak

# 实时行情
ak.stock_zh_a_spot_em()

# 历史K线
ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20230101", end_date="20231231")

# 指数行情
ak.stock_zh_index_spot_em()

# 行业板块
ak.stock_board_industry_name_em()
```

### 2. Tushare (需要token)
```python
import tushare as ts

# 初始化
ts.set_token('your_token')
pro = ts.pro_api()

# 指数日线
pro.index_daily(ts_code='000001.SH', start_date='20230101', end_date='20231231')

# 股票日线
pro.daily(ts_code='000001.SZ', start_date='20230101', end_date='20231231')
```

### 3. 东方财富API
```python
# 实时行情
# http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery&pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152

# 北向资金
# http://push2.eastmoney.com/api/qt/kamt.rtmin/get?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55,f56
```

### 4. 新浪财经
```python
# 实时行情
# https://hq.sinajs.cn/list=sh000001,sz399001,sz399006

# 实时成交
# https://hq.stock.sohu.com/hq/block/bk_2801.html
```

## 数据源优先级配置

```python
DATA_SOURCE_PRIORITY = {
    "realtime": {
        1: {"name": "东方财富", "api": "eastmoney", "reliability": 0.95},
        2: {"name": "新浪财经", "api": "sina", "reliability": 0.90},
        3: {"name": "腾讯财经", "api": "tencent", "reliability": 0.85}
    },
    "historical": {
        1: {"name": "AKShare", "api": "akshare", "reliability": 0.90},
        2: {"name": "Tushare", "api": "tushare", "reliability": 0.95}
    },
    "fundamentals": {
        1: {"name": "东方财富", "api": "eastmoney", "reliability": 0.90},
        2: {"name": "巨潮资讯", "api": "cninfo", "reliability": 0.95}
    }
}
```

## 数据更新策略

```python
UPDATE_STRATEGY = {
    "realtime_data": {
        "frequency": "每分钟",
        "during_trading": True,
        "after_hours": False
    },
    "daily_data": {
        "frequency": "每日收盘后",
        "time": "16:00",
        "retry": 3
    },
    "fundamental_data": {
        "frequency": "每周",
        "time": "周日02:00"
    }
}
```
