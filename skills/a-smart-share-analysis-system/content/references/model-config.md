# 模型配置参考

## 技术指标计算公式

### 均线系统
```python
def calculate_ma(close_prices, period):
    """移动平均线"""
    return close_prices.rolling(window=period).mean()

def calculate_ema(close_prices, period):
    """指数移动平均"""
    return close_prices.ewm(span=period, adjust=False).mean()
```

### MACD
```python
def calculate_macd(close_prices, fast=12, slow=26, signal=9):
    """MACD指标"""
    ema_fast = close_prices.ewm(span=fast, adjust=False).mean()
    ema_slow = close_prices.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist
```

### KDJ
```python
def calculate_kdj(high, low, close, n=9, m1=3, m2=3):
    """KDJ随机指标"""
    lowest_low = low.rolling(window=n).min()
    highest_high = high.rolling(window=n).max()
    rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
    k = rsv.ewm(com=m1-1, adjust=False).mean()
    d = k.ewm(com=m2-1, adjust=False).mean()
    j = 3 * k - 2 * d
    return k, d, j
```

### RSI
```python
def calculate_rsi(close_prices, period=14):
    """RSI相对强弱指标"""
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

### 布林带
```python
def calculate_boll(close_prices, period=20, std_dev=2):
    """布林带指标"""
    middle = close_prices.rolling(window=period).mean()
    std = close_prices.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return upper, middle, lower
```

## 模型参数配置

### XGBoost参数
```python
XGBOOST_PARAMS = {
    "objective": "binary:logistic",
    "eval_metric": "auc",
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 1,
    "reg_alpha": 0.1,
    "reg_lambda": 1,
    "scale_pos_weight": 1
}
```

### LightGBM参数
```python
LIGHTGBM_PARAMS = {
    "objective": "binary",
    "metric": "auc",
    "boosting_type": "gbdt",
    "num_leaves": 31,
    "learning_rate": 0.05,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "min_child_samples": 20,
    "reg_alpha": 0.1,
    "reg_lambda": 1
}
```

### 深度学习模型
```python
DEEP_LEARNING_CONFIG = {
    "input_dim": 100,
    "hidden_dims": [128, 64, 32],
    "output_dim": 1,
    "dropout_rate": 0.3,
    "activation": "relu",
    "optimizer": "adam",
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 100,
    "early_stopping_patience": 10
}
```

## 回测配置

```python
BACKTEST_PARAMS = {
    "initial_capital": 1000000,
    "commission_rate": 0.0003,
    "stamp_tax_rate": 0.001,
    "slippage_rate": 0.001,

    "position": {
        "max_single_position": 0.3,
        "max_total_position": 0.95,
        "min_position": 0.05
    },

    "risk_management": {
        "stop_loss": 0.07,
        "take_profit": 0.15,
        "trailing_stop": 0.05
    },

    "rebalance": {
        "frequency": "weekly",
        "threshold": 0.1
    }
}
```

## 模型评估指标

```python
EVALUATION_METRICS = {
    "regression": [
        "MAE",      # 平均绝对误差
        "MSE",      # 均方误差
        "RMSE",     # 均方根误差
        "MAPE",     # 平均绝对百分比误差
        "R2"        # 决定系数
    ],
    "classification": [
        "Accuracy",     # 准确率
        "Precision",    # 精确率
        "Recall",       # 召回率
        "F1-Score",     # F1分数
        "AUC-ROC"       # AUC值
    ],
    "trading": [
        "Total Return",         # 总收益率
        "Annualized Return",   # 年化收益率
        "Sharpe Ratio",        # 夏普比率
        "Max Drawdown",        # 最大回撤
        "Win Rate",            # 胜率
        "Profit Loss Ratio",   # 盈亏比
        "Calmar Ratio",        # 卡玛比率
        "Sortino Ratio"       # 索提诺比率
    ]
}
```
