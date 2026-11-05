---
name: a-stock-backtest
description: A股量化回测系统技能。提供完整的数据获取、回测引擎、策略分析和可视化功能。当用户要求进行A股量化回测、策略回测、绩效分析、股票数据分析、或使用命令行/Web界面运行交易策略回测时使用。
---

# A股量化回测系统

专业的A股量化回测系统，支持多种经典技术指标策略、数据获取、绩效评估和可视化分析。

## 核心功能

### 1. 数据获取 (StockDataFetcher)
从TuShare Pro API获取A股真实历史行情数据：
- 支持单只股票和多只股票批量获取
- 自动数据缓存，避免重复请求
- 返回标准OHLCV格式数据

```python
from data_fetcher import StockDataFetcher

fetcher = StockDataFetcher()
# 获取单只股票数据
df = fetcher.fetch_stock_data("000001", "2023-01-01", "2024-01-01")
# 批量获取多只股票
data = fetcher.fetch_multiple_stocks(["000001", "600519"], "2023-01-01", "2024-01-01")
```

### 2. 回测引擎 (BacktestEngine)
核心回测逻辑，模拟真实交易环境：
- 支持自定义初始资金、手续费率、滑点
- 逐日执行策略信号
- 生成交易记录和资金曲线

```python
from backtest_engine import BacktestEngine
from strategies import ma_cross_strategy

engine = BacktestEngine(initial_capital=1000000)
engine.load_data(data)
engine.set_strategy(ma_cross_strategy, short_window=5, long_window=20)
results = engine.run()
```

### 3. 投资组合管理 (Portfolio)
完整的交易执行和资金管理：
- 支持买入、卖出交易
- 手续费、印花税、滑点计算
- 持仓管理和盈亏跟踪

```python
from portfolio import Portfolio

portfolio = Portfolio(initial_capital=1000000)
portfolio.buy("000001", 1000, 10.5, datetime.now())
```

### 4. 绩效分析 (PerformanceAnalyzer)
全面的策略绩效评估指标：
- **收益指标**：总收益率、年化收益率、日均收益率
- **风险指标**：波动率、最大回撤、VaR
- **风险调整收益**：夏普比率、卡玛比率、索提诺比率
- **交易统计**：胜率、盈亏比、利润因子

```python
from performance import PerformanceAnalyzer

analyzer = PerformanceAnalyzer(equity_curve, trades)
report = analyzer.get_full_report()
analyzer.print_report()
```

## 支持的交易策略

| 策略名称 | 描述 | 关键参数 |
|---------|------|---------|
| ma_cross | 移动平均线交叉 | short_window, long_window |
| rsi | RSI超买超卖 | period, oversold, overbought |
| bollinger | 布林带策略 | period, std_dev |
| macd | MACD指标 | fast_period, slow_period, signal_period |
| kdj | KDJ随机指标 | n, m1, m2 |
| dual_ma_rsi | 双均线+RSI组合 | ma_short, ma_long, rsi_period |
| kdj_bbi | KDJ+BBI组合 | kdj_n, j_buy_threshold |

### 使用策略示例

```python
from strategies import get_strategy, list_strategies

# 列出所有可用策略
print(list_strategies())

# 获取策略函数
strategy = get_strategy('ma_cross')
```

## 使用方式

### 方式1: Python脚本

```python
from main import QuantBacktestSystem

system = QuantBacktestSystem()
results = system.run_backtest(
    symbols=["000001"],
    start_date="2023-01-01",
    end_date="2024-01-01",
    strategy_name="ma_cross",
    initial_capital=1000000,
    strategy_params={"short_window": 5, "long_window": 20}
)
system.print_results(results)
```

### 方式2: 命令行

```bash
# 演示模式
python main.py --mode demo

# 自定义回测
python main.py --mode custom

# 批量模式
python main.py --mode batch \
    --symbol 000001 \
    --start 2023-01-01 \
    --end 2024-01-01 \
    --strategy ma_cross \
    --capital 1000000
```

### 方式3: Web界面 (Streamlit)

```bash
pip install streamlit plotly
streamlit run app.py
```

## 绩效指标解读

- **总收益率**：回测期间的总收益百分比
- **年化收益率**：折算成年度的收益率，便于横向比较
- **夏普比率**：风险调整后收益，>1表示较好
- **最大回撤**：历史最大亏损幅度，控制风险
- **胜率**：盈利交易占总交易次数的比例
- **盈亏比**：平均盈利金额/平均亏损金额
- **利润因子**：总盈利/总亏损，>1表示盈利

## 依赖安装

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple \
    tushare pandas numpy matplotlib seaborn streamlit plotly
```

## 文件结构

```
a-stock-backtest/
├── __init__.py          # 包初始化
├── config.py            # 配置文件
├── data_fetcher.py      # 数据获取模块
├── backtest_engine.py   # 回测引擎
├── portfolio.py         # 投资组合管理
├── performance.py       # 绩效分析
├── strategies.py        # 交易策略
├── visualization.py     # 可视化模块
├── main.py              # 主程序入口
├── app.py               # Streamlit Web应用
└── requirements.txt     # 依赖列表
```

## 注意事项

1. **数据真实性**：系统使用TuShare Pro API获取真实A股数据，禁止使用模拟数据
2. **策略参数**：不同策略需要适当调整参数以适应市场特性
3. **回测局限**：历史表现不代表未来收益，实盘需谨慎
4. **交易成本**：已考虑手续费、印花税、滑点等真实交易成本
