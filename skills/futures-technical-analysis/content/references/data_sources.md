# 期货数据源参考指南

## 推荐数据源（按优先级）

### 1. Tushare Pro API
**网址**: https://tushare.pro
**特点**: 免费额度充足，API友好，Python生态完善

#### 安装与配置
```bash
pip install tushare
```

#### 核心接口

```python
import tushare as ts

# 初始化
pro = ts.pro_api('YOUR_TOKEN')

# 期货持仓数据
df = pro.fut_holding(date='20240301', exchange='DCE', fut_type='1')

# 仓单数据
df = pro.ed置yield(date='20240301', commodity='Y')

# 现货价格
df = pro.spot(dates='20240301', symbol='豆粕')

# 商品供需数据
df = pro.commodity_supply_demand(year='2024', commodity='豆粕')
```

### 2. 东方财富Choice
**网址**: https://choice.eastmoney.com
**特点**: 机构级数据，全品类覆盖

### 3. 同花顺iFinD
**网址**: https://www.10jqka.com.cn
**特点**: 期货产业链数据完整

### 4. 交易所官方数据
- 大连商品交易所: https://www.dce.com.cn
- 上海期货交易所: https://www.shfe.com.cn
- 郑州商品交易所: https://www.czce.com.cn
- 上海国际能源交易中心: https://www.ine.cn

### 5. Wind万德
**网址**: https://www.wind.com.cn
**特点**: 机构级全品类数据

## 技术指标计算参考

### MA（移动平均线）
```python
import pandas as pd

def calc_ma(prices, periods=[5, 10, 20, 60]):
    result = {}
    for p in periods:
        result[f'MA{p}'] = prices.rolling(p).mean()
    return result
```

### MACD
```python
def calc_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal).mean()
    macd_bar = (dif - dea) * 2
    return {'dif': dif, 'dea': dea, 'macd_bar': macd_bar}
```

### RSI
```python
def calc_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

### BOLL
```python
def calc_boll(prices, period=20, std_dev=2):
    mid = prices.rolling(period).mean()
    std = prices.rolling(period).std()
    upper = mid + std_dev * std
    lower = mid - std_dev * std
    return {'upper': upper, 'mid': mid, 'lower': lower}
```

### ATR
```python
def calc_atr(high, low, close, period=14):
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr
```

## 持仓结构分析方法

### 会员持仓集中度
```python
def calc_concentration(holdings_df):
    """
    holdings_df: 包含会员持仓的DataFrame
    返回: 多头/空头集中度
    """
    top10_long = holdings_df.nlargest(10, 'long_vol')['long_vol'].sum()
    top10_short = holdings_df.nlargest(10, 'short_vol')['short_vol'].sum()
    total_vol = holdings_df['vol'].sum()

    long_concentration = top10_long / total_vol * 100
    short_concentration = top10_short / total_vol * 100

    return {
        'long_concentration': long_concentration,
        'short_concentration': short_concentration
    }
```

### 净持仓变化
```python
def calc_net_position_change(current, previous):
    """
    计算净持仓变化
    """
    net_change = current['net_position'] - previous['net_position']
    return {
        'net_change': net_change,
        'direction': 'long' if net_change > 0 else 'short'
    }
```

## 库存周期判断

| 库存阶段 | 价格上涨 | 价格下跌 |
|---------|---------|---------|
| 主动增库存 | 被动增库存 | 主动去库存 |
| 被动增库存 | 主动增库存 | 被动去库存 |

## 产业链利润计算

### 上游利润
```
利润 = 现货价格 - 成本 - 运费 - 加工费
```

### 盘面利润
```
利润 = 期货价格 × 转换系数 - 现货价格 - 升贴水 - 运费
```

## 数据质量检查清单

- [ ] 数据时间戳是否最新
- [ ] 数据来源是否可靠
- [ ] 数据完整性（无缺失）
- [ ] 数据异常值检测
- [ ] 数据口径一致性
