# 笑傲牛熊分析器代码实现

## 核心算法说明

### 1. 四阶段判断算法

```python
def determine_stage(df, price_col='close'):
    """
    基于30周EMA判断股票所处阶段
    """
    # 计算30周EMA
    ma30 = calculate_ema(prices, 30)

    # 获取最近20个数据点
    recent = df.tail(20)

    # 判断条件
    price_above_ma = current_price > current_ma
    ma_direction = "上升" if ma_slope > 0 else "下降" if ma_slope < 0 else "走平"

    # 阶段判断逻辑
    if not price_above_ma and ma_direction == "下降":
        return 4  # 阶段4-下跌
    elif price_above_ma and higher_highs and higher_lows:
        return 2  # 阶段2-拉升
    elif not price_above_ma:
        return 3  # 阶段3-顶部
    else:
        return 1  # 阶段1-底部
```

### 2. 相对强度计算

```python
def calculate_relative_strength(stock_df, market_df):
    """
    计算个股与大盘的相对强度
    """
    # 当前RS
    current_ratio = (stock_price / market_price) * 100

    # 基准RS（30天前）
    base_ratio = (base_stock / base_market) * 100

    # RS变化率
    rs_change = (current_ratio / base_ratio - 1) * 100

    # 分类判断
    if rs_change > 20:
        return "强", "red"
    elif rs_change > 5:
        return "小强", "yellow"
    elif rs_change > -5:
        return "小弱", "yellow"
    else:
        return "弱", "green"
```

### 3. 止损位计算

```python
def calculate_stop_loss(df, buy_price=None):
    """
    计算止损位
    """
    # 30周均线
    ma30 = calculate_ema(df['close'], 30).iloc[-1]

    # 前期支撑低点
    support_low = df['low'].tail(20).min()

    # 日线止损
    daily_stop = max(support_low, ma30) - 0.125

    # 应用硬止损
    if buy_price:
        hard_stop = buy_price * 0.93  # 7%止损
        daily_stop = min(daily_stop, hard_stop)

    return daily_stop, ma30  # 日线止损, 周线止损
```

---

## Excel报告生成

### 颜色映射

| 指标 | 好信号 | 中性信号 | 坏信号 |
|------|--------|----------|--------|
| 阶段2 | 红色 | - | - |
| 阶段3 | - | 黄色 | - |
| 阶段4 | - | - | 绿色 |
| 相对强度-强 | 红色 | - | - |
| 相对强度-弱 | - | - | 绿色 |
| 相对强度-小强/小弱 | - | 黄色 | - |
| 高于30周 | 红色 | - | - |
| 低于60周 | - | - | 绿色 |
| 放量 | 红色 | - | - |
| 缩量 | - | - | 绿色 |
| 回抽缩量 | 红色 | - | - |
| 股息率高(>4.5%) | 红色 | - | - |

---

## 数据获取流程

### akshare接口使用

```python
import akshare as ak

# 获取股票历史数据
stock_df = ak.stock_zh_a_hist(
    symbol="600519",
    period="weekly",
    start_date="20240101",
    end_date="20260404",
    adjust="qfq"  # 前复权
)

# 获取大盘指数数据
index_df = ak.stock_zh_index_daily(symbol="sh000001")

# 获取行业板块数据
industry_df = ak.stock_board_industry_hist_em(
    symbol="半导体",
    period="weekly",
    start_date="20240101",
    end_date="20260404"
)
```

### 数据存储策略

1. 首次获取：下载完整历史数据
2. 后续更新：增量获取，只获取新数据
3. 检测事件：自动检测股息、拆股等事件
4. 本地缓存：SQLite数据库存储

---

## 常见股票代码

### 白酒板块
| 名称 | 代码 |
|------|------|
| 贵州茅台 | 600519 |
| 五粮液 | 000858 |
| 泸州老窖 | 000568 |
| 山西汾酒 | 600809 |

### 金融板块
| 名称 | 代码 |
|------|------|
| 中国平安 | 601318 |
| 招商银行 | 600036 |
| 东方财富 | 300059 |

### 新能源板块
| 名称 | 代码 |
|------|------|
| 宁德时代 | 300750 |
| 比亚迪 | 002594 |
| 隆基绿能 | 601012 |

### ETF基金
| 名称 | 代码 |
|------|------|
| 沪深300ETF | 510300 |
| 半导体ETF | 512760 |
| 酒ETF | 512690 |
| 光伏ETF | 515790 |
| 医疗ETF | 512010 |
| 军工ETF | 512660 |

### 大盘指数
| 名称 | 代码 |
|------|------|
| 上证综指 | 000001 |
| 深证成指 | 399001 |
| 创业板指 | 399006 |
| 沪深300 | 000300 |
