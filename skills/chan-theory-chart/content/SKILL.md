---
name: chan-theory-chart
description: 输入股票代码，自动生成缠论技术分析图表。当用户要求分析股票、查看缠论图、绘制笔线段中枢时使用。触发短语如："分析贵州茅台"、"缠论图"、"笔中枢分析"、"查看线段"、"[股票代码]"。
---

# 缠论技术分析图 Skill

输入股票代码，自动生成包含K线、笔、线段、中枢、背离的交互式缠论图表。

## 核心功能

- **K线图**：标准OHLC蜡烛图
- **笔(Bi)**：缠论基础构件，连接相邻顶底分型
- **线段(Segment)**：由至少3笔组成
- **中枢(Zhongshu)**：至少3笔段重叠区域
- **背离分析**：价格与MACD/RSI背离检测

## 数据获取

使用 Yahoo Finance API 获取股票数据，无需API Key：

```python
import yfinance as yf

def get_stock_data(symbol: str, period: str = "2y") -> pd.DataFrame:
    """获取股票历史数据"""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    return df
```

## 缠论算法

### 笔的定义

笔 = 顶分型 + 底分型（或反向），中间至少有一根K线：

```
顶分型：第二根K线高点最高，且收盘最低
底分型：第二根K线低点最低，且收盘最高
```

### 线段定义

线段由至少3笔构成，且笔之间没有重叠：

```
笔1 → 笔2 → 笔3（方向一致，无包含关系）
```

### 中枢定义

中枢 = 连续三段的重叠区域：

```
线段A → 线段B → 线段C（重叠部分 = 中枢）
```

## 触发指令

| 用户输入 | 执行动作 |
|---------|---------|
| "分析 AAPL" | 获取苹果数据，生成缠论图 |
| "贵州茅台 600519" | 获取茅台K线，绘制笔中枢 |
| "TSLA缠论图" | 生成特斯拉完整分析 |
| "查看线段背离" | 高亮线段和背离信号 |

## 执行流程

1. **接收股票代码** → 解析股票代码（支持美股、A股）
2. **获取数据** → yfinance获取2年历史数据
3. **计算缠论元素** → 笔 → 线段 → 中枢 → 背离
4. **生成图表** → HTML交互式图表
5. **输出结果** → 返回HTML文件路径

## 缠论元素渲染

使用Plotly生成交互式HTML：

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 创建图表
fig = make_subplots(rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    row_heights=[0.7, 0.3])

# K线图
fig.add_trace(go.Candlestick(x=df.index,
                            open=df['Open'],
                            high=df['High'],
                            low=df['Low'],
                            close=df['Close'],
                            name='K线'),
             row=1, col=1)

# 笔标记
fig.add_trace(go.Scatter(x=bi_tops.index, y=bi_tops['price'],
                         mode='markers', marker=dict(size=10, color='red'),
                         name='笔顶'),
             row=1, col=1)

# 中枢区域
for zhongshu in zhongshu_list:
    fig.add_shape(type="rect",
                  x0=zhongshu['start'], x1=zhongshu['end'],
                  y0=zhongshu['low'], y1=zhongshu['high'],
                  fillcolor="rgba(255,165,0,0.3)",
                  line=dict(color="orange"))
```

## 输出格式

生成单个HTML文件，包含：
- 交互式K线图（可缩放、平移）
- 笔/线段/中枢叠加层
- MACD副图（背离检测）
- 股票信息头部（代码、名称、价格）

## 示例调用

```python
# 完整分析流程
symbol = "AAPL"  # 或 "600519.SS" for A股
period = "2y"
output_path = generate_chan_theory_chart(symbol, period)
```

## 错误处理

- **无效代码**：提示"股票代码不存在，请检查格式"
- **数据不足**：提示"数据不足，无法完成缠论分析（需要至少100根K线）"
- **网络错误**：提示"获取数据失败，请检查网络连接"

## 技术依赖

- `yfinance`：股票数据获取
- `pandas`：数据处理
- `plotly`：交互式图表生成
- `numpy`：数值计算
