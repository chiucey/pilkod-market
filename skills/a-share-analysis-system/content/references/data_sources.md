# A股分析预测系统 - 数据源参考文档

## 免费数据源

### 1. AKShare

**官网**: https://akshare.akfamily.xyz/

**安装**: `pip install akshare`

**常用API**:

```python
import akshare as ak

# 实时行情
ak.stock_zh_a_spot()  # 个股实时行情
ak.stock_zh_index_spot()  # 指数实时行情

# 历史数据
ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20230101", end_date="20231231")

# 指数数据
ak.stock_zh_index_daily(symbol="sh000001")  # 上证指数历史
```

**数据质量**: 高，覆盖全面，免费使用

### 2. Tushare

**官网**: https://tushare.pro/

**安装**: `pip install tushare`

**常用API**:

```python
import tushare as ts

# 初始化
ts.set_token('your_token')
pro = ts.pro_api()

# 日线数据
df = pro.daily(ts_code='000001.SZ', start_date='20230101', end_date='20231231')

# 指数日线
df = pro.index_daily(ts_code='000001.SH')
```

**数据质量**: 高，专业级，需注册获取token

### 3. Baostock

**官网**: http://baostock.com/

**安装**: `pip install baostock`

**常用API**:

```python
import baostock as bs

# 登录
bs.login()

# 日线数据
rs = bs.query_history_k_data_plus("sh.600000",
    "date,code,open,high,low,close,volume",
    start_date='2023-01-01', end_date='2023-12-31',
    frequency="d", adjustflag="3")

# 登出
bs.logout()
```

**数据质量**: 中等，覆盖时间跨度长

## 数据优先级配置

```python
DATA_SOURCE_PRIORITY = [
    {
        "name": "AKShare",
        "priority": 1,
        "apis": {
            "realtime": "stock_zh_a_spot",
            "history": "stock_zh_a_hist",
            "index": "stock_zh_index_daily"
        },
        "fallback": ["Tushare", "Baostock"]
    },
    {
        "name": "Tushare",
        "priority": 2,
        "apis": {
            "realtime": "quote_api",
            "history": "daily",
            "index": "index_daily"
        },
        "fallback": ["Baostock"]
    },
    {
        "name": "Baostock",
        "priority": 3,
        "apis": {
            "history": "query_history_k_data_plus"
        }
    }
]
```

## 数据检核规则

### 横向一致性检查
- 同一日期的多字段数据一致性
- 价格与成交量的合理性关系
- 涨跌幅与价格变化的匹配

### 纵向一致性检查
- 相邻日期数据的连续性
- 极端值检测
- 缺失值检测

### 智能判别规则
```python
VALIDATION_RULES = {
    "price_range": {
        "min": 0.01,
        "max": 10000,
        "description": "单股价格合理范围"
    },
    "volume_ratio": {
        "max": 100,
        "description": "量比合理性"
    },
    "change_pct_range": {
        "min": -20,
        "max": 20,
        "description": "单日涨跌幅限制"
    }
}
```

## 数据缓存策略

```python
CACHE_CONFIG = {
    "realtime_data": {
        "ttl": 60,  # 60秒
        "refresh": "always"
    },
    "daily_data": {
        "ttl": 86400,  # 收盘后不更新
        "refresh": "after_close"
    },
    "history_data": {
        "ttl": 604800,  # 7天
        "refresh": "weekly"
    }
}
```
