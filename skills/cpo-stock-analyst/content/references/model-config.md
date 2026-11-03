# 模型配置参考 v3.5

## Alpha因子库概览

| 因子类别 | 数量 | v3.5新增 |
|---------|------|---------|
| 技术面因子 | 15+ | - |
| 均线特征 | 7+ | - |
| 技术指标 | 15+ | - |
| 基本面因子 | 9+ | - |
| 市场资金因子 | 10+ | +5 |
| 外盘联动因子 | 10+ | - |
| 热点板块因子 | 5+ | - |
| **CPO产业链因子** | **NEW** | **+8** |
| **缩量市场因子** | **NEW** | **+5** |
| **板块轮动因子** | **NEW** | **+5** |
| **龙头新高因子** | **NEW** | **+5** |
| **资金结构因子** | **NEW** | **+5** |
| 政策情绪因子 | 3+ | - |
| 多指标共振 | 3+ | - |
| 市场风格因子 | 5+ | - |
| 深度学习因子 | 4+ | - |
| 另类数据因子 | 3+ | - |
| **合计** | **110+** | **+33** |

## 新增Alpha因子详解

### CPO产业链因子 ⭐

```python
CPO_CHAIN_FEATURES = {
    "cpo_module_sentiment": "CPO光模块情绪因子",
    "cpo_device_sentiment": "CPO设备情绪因子",
    "optical_chip_sentiment": "光芯片情绪因子",
    "optical_fiber_sentiment": "光纤情绪因子",
    "liquid_cooling_sentiment": "液冷服务器情绪因子",
    "cpo_leader_new_high": "CPO龙头创新高动量",
    "cpo_volume_price_ratio": "CPO量价配合因子",
    "optical_module_export_ratio": "光模块出口比例"
}
```

### 缩量市场情绪因子 ⭐

```python
VOLUME_CONTRACTION_FEATURES = {
    "volume_shrink_ratio": "成交量萎缩比例",
    "volume_shrink_speed": "缩量速度",
    "market_sentiment_cooling": "情绪降温指数",
    "breakout_threshold": "突破缩量阈值",
    "dry_powder_ratio": "资金观望度(干粉比例)"
}
```

### 板块轮动加速度因子 ⭐

```python
SECTOR_ROTATION_FEATURES = {
    "sector_rotation_acceleration": "板块轮动加速度",
    "sector_lead_lag_spread": "领涨滞涨板块价差",
    "theme_density_index": "主题密度指数",
    "sector_concentration_ratio": "资金集中度",
    "leader_continuity_score": "龙头连续性"
}
```

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

### XGBoost参数 v3.5
```python
XGBOOST_PARAMS_V35 = {
    "objective": "binary:logistic",
    "eval_metric": "auc",
    "max_depth": 6,
    "learning_rate": 0.03,        # v3.5优化：降低学习率提升稳定性
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 1,
    "reg_alpha": 0.1,
    "reg_lambda": 1,
    "scale_pos_weight": 1,
    # v3.5新增：CPO相关因子权重
    "feature_weights": {
        "cpo_chain": 1.3,
        "volume_contraction": 1.2,
        "sector_rotation": 1.15
    }
}
```

### LightGBM参数 v3.5
```python
LIGHTGBM_PARAMS_V35 = {
    "objective": "binary",
    "metric": "auc",
    "boosting_type": "gbdt",
    "num_leaves": 31,
    "learning_rate": 0.03,        # v3.5优化
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "min_child_samples": 20,
    "reg_alpha": 0.1,
    "reg_lambda": 1,
    # v3.5新增
    "feature_weights": {
        "new_high_momentum": 1.25,
        "capital_structure": 1.1
    }
}
```

### 集成模型v3.5参数
```python
ENSEMBLE_PARAMS_V35 = {
    "models": ["xgboost", "lightgbm", "lstm", "transformer"],
    "weights": [0.35, 0.25, 0.2, 0.2],
    "hot_sectors": ["CPO", "光模块", "半导体设备", "液冷服务器"],
    "feature_weights": {
        "cpo_chain": 1.3,           # CPO因子30%权重提升
        "volume_contraction": 1.2,   # 缩量因子20%权重提升
        "sector_rotation": 1.15,     # 轮动因子15%权重提升
        "new_high_momentum": 1.25,    # 新高因子25%权重提升
        "capital_structure": 1.1      # 资金结构10%权重提升
    }
}
```

## 回测配置 v3.5

```python
BACKTEST_PARAMS_V35 = {
    "initial_capital": 1000000,
    "commission_rate": 0.0003,
    "stamp_tax_rate": 0.001,
    "slippage_rate": 0.001,

    "position": {
        "max_single_position": 0.25,  # v3.5优化：降低单票上限
        "max_total_position": 0.85,   # v3.5优化：降低总仓位
        "min_position": 0.05
    },

    "risk_management": {
        "stop_loss": 0.07,           # 7%硬性止损
        "take_profit": 0.15,         # 15%止盈
        "trailing_stop": 0.05,        # 5%移动止损
        # v3.5新增：缩量市场止损
        "volume_contraction_stop": 0.04  # 缩量市场更严格止损
    },

    "rebalance": {
        "frequency": "weekly",
        "threshold": 0.15,           # v3.5优化：调整再平衡阈值
        "shrink_warning": 0.2        # v3.5新增：缩量预警阈值
    },

    # v3.5新增：CPO主线策略
    "cpo_strategy": {
        "enabled": True,
        "weight_boost": 1.2,         # CPO主线权重提升
        "leader_follow": True,        # 跟随龙头
        "new_high_filter": True       # 新高过滤
    }
}
```
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
EVALUATION_METRICS_V35 = {
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
        "Sortino Ratio",       # 索提诺比率
        # v3.5新增
        "CPO_Return",          # CPO主线收益率
        "Leader_Return",       # 龙头股收益率
        "Shrink_Adjusted_Return"  # 缩量调整收益率
    ],
    # v3.5新增评估指标
    "cpo_metrics": [
        "CPO_Signal_Accuracy",    # CPO信号准确率
        "CPO_Lead_Lag_Ratio",     # CPO领先/滞后比率
        "New_High_Success_Rate"   # 新高策略成功率
    ]
}
```

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
