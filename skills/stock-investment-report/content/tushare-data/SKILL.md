---
name: tushare-data
description: Tushare金融数据接口技能。当需要获取A股市场数据、进行股票分析、获取财务数据、行情数据、资金流向、指数数据时使用此技能。触发关键词：Tushare、股票数据、财务数据、行情数据、资金流向、A股分析、上市公司数据。
---

# Tushare数据接口技能

## 概述

Tushare是一个免费、开源的Python金融数据接口包，本技能提供完整的Tushare数据调用能力，用于获取A股市场的各类数据进行分析。

## 前置准备

### 安装Tushare

```python
pip install tushare
```

### 初始化API

```python
import tushare as ts

# 使用个人token初始化
pro = ts.pro_api('YOUR_TOKEN')

# 或使用默认方式（部分功能受限）
ts.set_token('YOUR_TOKEN')
pro = ts.pro_api()
```

### 获取Token

1. 访问 [Tushare官网](https://tushare.pro/)
2. 注册账号并登录
3. 进入个人中心 → API接口
4. 复制您的Token

## 核心API调用

### 1. 股票基础信息

```python
# 查询股票列表
df = pro.stock_basic(
    ts_code='',      # 股票代码
    name='',         # 股票名称
    exchange='',     # 交易所: SSE(上交所), SZSE(深交所)
    list_status='L', # 上市状态: L(上市), D(退市), P(暂停)
    fields='ts_code,name,industry,market,list_date'
)

# 获取上市公司信息
df = pro.company_info(ts_code='000001.SZ')
```

### 2. 行情数据

```python
# 日线行情
df = pro.daily(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240301'
)

# 日线行情(含估值指标)
df = pro.daily_basic(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240301',
    fields='ts_code,trade_date,close,pe,pb,ps,total_mv,circ_mv'
)

# 周线/月线行情
df = pro.weekly(ts_code='000001.SZ', start_date='20240101')
df = pro.monthly(ts_code='000001.SZ', start_date='20240101')

# 实时行情
df = ts.realtime_quote(ts_code='000001.SZ')

# 历史分时(需要Pro会员)
df = pro.tick_data(
    ts_code='000001.SZ',
    trade_date='20240101'
)
```

### 3. 财务数据

```python
# 财务指标数据
df = pro.fina_indicator(
    ts_code='000001.SZ',
    start_date='20230101',
    end_date='20240301'
)

# 利润表
df = pro.income(
    ts_code='000001.SZ',
    start_date='20230101',
    end_date='20240301',
    fields='ts_code,ann_date,f_ann_date,report_type,n_income'
)

# 资产负债表
df = pro.balancesheet(
    ts_code='000001.SZ',
    start_date='20230101'
)

# 现金流量表
df = pro.cashflow(
    ts_code='000001.SZ',
    start_date='20230101'
)

# 主营业务构成
df = pro.fina_mainbz(
    ts_code='000001.SZ',
    start_date='20230101'
)
```

### 4. 资金流向

```python
# 个股资金流向
df = pro.moneyflow(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240301'
)

# 个股资金流向(详细)
df = pro.moneyflow_hsgt(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240301'
)

# 北向/南向资金
df = pro.hk_hold(ts_code='000001.SZ', start_date='20240101')
df = pro.ggt_top10(ts_code='000001.SZ', trade_date='20240101')
```

### 5. 股东数据

```python
# 股东人数变化
df = pro.stk_holdernumber(
    ts_code='000001.SZ',
    start_date='20230101',
    end_date='20240301'
)

# 前十大股东
df = pro.top10_holders(ts_code='000001.SZ')

# 股东增减持
df = pro.stk_holdertrade(
    ts_code='000001.SZ',
    start_date='20230101'
)
```

### 6. 指数数据

```python
# 指数日线
df = pro.index_daily(
    ts_code='000300.SH',  # 沪深300
    start_date='20240101',
    end_date='20240301'
)

# 获取指数成分股
df = pro.index_weight(index_code='000300.SH', trade_date='20240301')
```

### 7. 估值数据

```python
# 股票历史PE/PB
df = pro.daily_basic(
    ts_code='000001.SZ',
    start_date='20200101',
    end_date='20240301',
    fields='ts_code,trade_date,close,pe,pb'
)

# 计算历史分位
# 使用pandas计算当前PE在历史数据中的分位数
import numpy as np
percentile = (df['pe'] < current_pe).mean() * 100
```

## 常用数据组合

### 完整基本面分析数据

```python
import tushare as ts

pro = ts.pro_api('YOUR_TOKEN')

def get_fundamental_data(ts_code):
    """获取完整基本面数据"""
    results = {}

    # 1. 股票基本信息
    basic = pro.stock_basic(ts_code=ts_code, fields='name,industry,market,list_date')
    results['basic'] = basic

    # 2. 最新财务指标
    fina = pro.fina_indicator(
        ts_code=ts_code,
        start_date='20230101',
        fields='ts_code,roe,gross_profit_margin,net_profit_margin,debt_to_assets,op_qfq_y,net_profit_yoy'
    )
    results['fina'] = fina

    # 3. 最新估值数据
    valuation = pro.daily_basic(
        ts_code=ts_code,
        trade_date='',
        fields='ts_code,trade_date,close,pe,pb,ps,total_mv,circ_mv'
    )
    results['valuation'] = valuation

    # 4. 最新资金流向
    moneyflow = pro.moneyflow(
        ts_code=ts_code,
        start_date='',
        end_date='',
        fields='ts_code,trade_date,buy_sm_amount,sell_sm_amount,buy_md_amount,sell_md_amount,buy_lg_amount,sell_lg_amount'
    )
    results['moneyflow'] = moneyflow

    return results
```

## 注意事项

1. **积分限制**: Tushare对不同数据接口有积分要求，普通用户可能无法访问部分高级数据
2. **调用频率**: 注意API调用频率限制，避免被限制
3. **数据更新**: 部分数据有延迟，财务数据通常在报告期后1-2个月更新
4. **数据验证**: 获取数据后应进行必要的校验，确保数据完整性
5. **错误处理**: 添加异常处理机制，处理网络错误和API限流

## 错误处理示例

```python
import tushare as ts
import time

def retry_api_call(func, max_retries=3, delay=1):
    """API调用重试机制"""
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i < max_retries - 1:
                print(f"API调用失败，{delay}秒后重试... ({i+1}/{max_retries})")
                time.sleep(delay)
            else:
                print(f"API调用失败: {e}")
                return None

# 使用示例
df = retry_api_call(lambda: pro.daily(ts_code='000001.SZ'))
```
