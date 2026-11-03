# A股分析预测系统 - 模型参考文档

## 模型概览

### 机器学习模型

#### 1. XGBoost

**适用场景**: 表格数据预测、分类问题

**优势**:
- 精度高
- 处理缺失值
- 内置正则化
- 支持并行

**配置**:
```python
from xgboost import XGBClassifier

model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42
)
```

#### 2. LightGBM

**适用场景**: 大规模数据、实时预测

**优势**:
- 训练速度快
- 内存效率高
- 支持类别特征
- 准确率高

**配置**:
```python
from lightgbm import LGBMClassifier

model = LGBMClassifier(
    n_estimators=200,
    max_depth=8,
    learning_rate=0.05,
    num_leaves=31,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbose=-1
)
```

### 深度学习模型

#### 1. LSTM（长短期记忆网络）

**适用场景**: 时序数据预测、捕捉长期依赖

**优势**:
- 擅长处理时序关系
- 记忆长期信息
- 预测连续值

**配置**:
```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(timesteps, features)),
    Dropout(0.2),
    LSTM(32),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')  # 二分类
])
```

#### 2. Transformer

**适用场景**: 复杂时序模式、多特征融合

**优势**:
- 注意力机制
- 并行计算
- 长距离依赖

**配置**:
```python
from tensorflow.keras.layers import MultiHeadAttention

# 使用Keras Transformer层
model = Sequential([
    # ... 编码层
    MultiHeadAttention(num_heads=4, key_dim=features),
    Dense(1, activation='sigmoid')
])
```

### 集成模型

#### 1. Stacking Ensemble

**原理**: 多模型预测作为次级模型输入

```python
from sklearn.ensemble import StackingClassifier

estimators = [
    ('xgb', XGBClassifier()),
    ('lgb', LGBMClassifier()),
    ('rf', RandomForestClassifier())
]

stacking_model = StackingClassifier(
    estimators=estimators,
    final_estimator=LogisticRegression(),
    cv=5
)
```

#### 2. Voting Ensemble

**原理**: 多模型投票决策

```python
from sklearn.ensemble import VotingClassifier

voting_model = VotingClassifier(
    estimators=estimators,
    voting='soft'  # 概率加权
)
```

## 模型训练流程

```
1. 数据准备
   ├── 数据清洗
   ├── 特征工程
   └── 数据分割 (train/val/test)

2. 模型选择
   ├── 基准模型
   └── 集成模型

3. 超参数优化
   ├── GridSearchCV
   ├── RandomSearchCV
   └── BayesianOptimization

4. 模型训练
   ├── 交叉验证
   └── 早停策略

5. 模型评估
   ├── 准确率
   ├── 召回率
   ├── F1分数
   └── AUC-ROC

6. 回测验证
   ├── 历史数据回测
   ├── 模拟交易
   └── 收益分析
```

## 回测指标

```python
BACKTEST_METRICS = {
    "return_metrics": {
        "total_return": "总收益率",
        "annual_return": "年化收益率",
        "sharpe_ratio": "夏普比率",
        "sortino_ratio": "索提诺比率"
    },
    "risk_metrics": {
        "max_drawdown": "最大回撤",
        "volatility": "波动率",
        "var_95": "95%VaR"
    },
    "trade_metrics": {
        "win_rate": "胜率",
        "profit_loss_ratio": "盈亏比",
        "trade_count": "交易次数",
        "avg_trade_duration": "平均持仓时间"
    }
}
```

## 模型优化建议

### 当前模型存在的问题
1. 需要更多市场情绪特征
2. 行业轮动特征缺失
3. 极端行情预测能力不足

### 下一步优化方向
1. 引入更多基本面因子
2. 添加新闻情绪分析
3. 优化极端行情处理
