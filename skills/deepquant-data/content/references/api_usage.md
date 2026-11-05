# 启睿策略中心数据接口文档

## Tushare Pro API 接口参考

### 1. 股票行情接口

#### 日线行情 (daily)
```python
pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20240327')
```

返回字段：
- ts_code: 股票代码
- trade_date: 交易日期
- open: 开盘价
- high: 最高价
- low: 最低价
- close: 收盘价
- vol: 成交量（手）
- amount: 成交额（千元）

#### 周线行情 (weekly)
```python
pro.weekly(ts_code='000001.SZ', start_date='20230101', end_date='20240327')
```

#### 月线行情 (monthly)
```python
pro.monthly(ts_code='000001.SZ', start_date='20230101', end_date='20240327')
```

### 2. 指数数据接口

#### 指数日线 (index_daily)
```python
pro.index_daily(ts_code='000001.SH', start_date='20240101', end_date='20240327')
```

#### 指数成分股 (index_weight)
```python
pro.index_weight(index_code='000300.SH', trade_date='20240301')
```

### 3. 基金数据接口

#### 基金基本信息 (fund_basic)
```python
pro.fund_basic(market='E')  # E=场内基金, O=场外基金
```

#### 基金净值 (nav)
```python
pro.nav(ts_code='510300.SH')  # 基金代码
```

### 4. 可转债接口

#### 可转债基本信息 (cb_basic)
```python
pro.cb_basic()
```

#### 可转债行情 (cb_daily)
```python
pro.cb_daily(trade_date='20240327')
```

### 5. 上市公司信息

#### 股票基本信息 (stock_basic)
```python
pro.stock_basic(ts_code='000001.SZ', list_status='L')
```

#### 公司高管 (stk_executives)
```python
pro.stk_executives(ts_code='000001.SZ')
```

### 6. 财务数据接口

#### 财务指标 (fina_indicator)
```python
pro.fina_indicator(ts_code='000001.SZ', start_date='20230101')
```

#### 利润表 (income)
```python
pro.income(ts_code='000001.SZ', start_date='20230101', report_type='1')
```

#### 资产负债表 (balancesheet)
```python
pro.balancesheet(ts_code='000001.SZ', start_date='20230101')
```

#### 现金流量表 (cashflow)
```python
pro.cashflow(ts_code='000001.SZ', start_date='20230101')
```

### 7. 一致性预期接口

#### 一致性预期 (consensus_pre)
```python
pro.consensus_pre(ts_code='000001.SZ', ann_date='20240101')
```

#### 业绩预告 (forecast)
```python
pro.forecast(ts_code='000001.SZ', start_date='20230101')
```

#### 业绩快报 (express)
```python
pro.express(ts_code='000001.SZ', start_date='20230101')
```

#### 分析师预期统计 (consensus_stat)
```python
pro.consensus_stat(ts_code='000001.SZ')
```

### 8. 股本数据接口

#### 流通股本 (float_share_d)
```python
pro.float_share_d(ts_code='000001.SZ', start_date='20230101')
```

#### 限售股解禁 (share_float)
```python
pro.share_float(ts_code='000001.SZ', start_date='20230101')
```

### 常见错误代码

| 错误码 | 说明 |
|-------|------|
| 40001 | 权限不足 |
| 40002 | 积分不足 |
| 40003 | 请求过于频繁 |
| 40004 | 无权访问 |
| 40007 | 参数错误 |
| 40008 | 无数据 |

### 数据延迟说明

| 数据类型 | 延迟时间 |
|---------|---------|
| 日线行情 | T日收盘后15-30分钟 |
| 财务数据 | T+1交易日 |
| 一致性预期 | T日盘中更新 |
| 基金净值 | T日估值，晚间确认 |
