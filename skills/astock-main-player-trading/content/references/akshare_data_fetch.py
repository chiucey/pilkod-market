# A股数据获取脚本 (akshare)

本目录包含使用 akshare 库获取A股数据的参考脚本。

## 安装

```bash
pip install akshare
```

## 常用数据获取函数

### 1. 股票历史行情数据

```python
import akshare as ak

# 获取单只股票历史行情
df = ak.stock_zh_a_hist(symbol="000001", period="daily",
                         start_date="20240101", end_date="20240509")
print(df)
```

### 2. 实时行情数据

```python
import akshare as ak

# 获取实时行情
df = ak.stock_zh_a_spot_em()
# 包含股票代码、名称、现价、涨跌幅、成交量等信息
```

### 3. 分时数据（分时博弈分析用）

```python
import akshare as ak

# 获取分时数据（用于攻击波分析）
df = ak.stock_zh_a_minute(symbol="000001", period="1")
```

### 4. 资金流向

```python
import akshare as ak

# 获取主力资金流向
df = ak.stock_individual_fund_flow(stock="000001")
```

### 5. 龙虎榜数据

```python
import akshare as ak

# 获取龙虎榜数据
df = ak.stock_lhb_detail_em(symbol="20240509")
```

### 6. 融资融券数据

```python
import akshare as ak

# 获取融资融券数据
df = ak.stock_margin_detail(symbol="000001", start_date="20240101",
                            end_date="20240509")
```

### 7. 大宗交易数据

```python
import akshare as ak

# 获取大宗交易数据
df = ak.stock_block_trade_em()
```

## 量化分析常用指标计算

```python
import akshare as ak
import pandas as pd

def calculate_indicators(stock_code: str, days: int = 5) -> dict:
    """计算主力行为分析常用指标"""
    # 获取历史数据
    df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                            start_date="20230101", end_date="20240509")

    # 计算成交量移动平均
    df['vol_ma5'] = df['成交量'].rolling(5).mean()
    df['vol_ma10'] = df['成交量'].rolling(10).mean()

    # 计算放量倍率
    current_vol = df['成交量'].iloc[-1]
    avg_vol_5d = df['vol_ma5'].iloc[-2]  # 前5日均值
    volume_ratio = current_vol / avg_vol_5d if avg_vol_5d > 0 else 0

    # 当日涨跌幅
    change_pct = df['涨跌幅'].iloc[-1]

    # 量价齐升/齐跌判断
    price_change = df['收盘'].iloc[-1] - df['收盘'].iloc[-2]
    vol_change = df['成交量'].iloc[-1] - df['成交量'].iloc[-2]

    return {
        'stock_code': stock_code,
        'volume_ratio': volume_ratio,
        'change_pct': change_pct,
        'price_change': price_change,
        'vol_change': vol_change,
        'is_bear_trap': volume_ratio < 0.3 and change_pct < 0  # 诱空判断
    }
```

## 注意事项

1. **数据延迟**：akshare数据可能有15-30分钟延迟
2. **频率限制**：避免高频请求，每次分析间隔建议≥30秒
3. **交易日判断**：非交易时段使用最近交易日数据
4. **错误处理**：添加异常捕获，防止网络问题导致分析中断
