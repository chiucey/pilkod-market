# Qlib 配置與使用指南

## 環境安裝

```bash
pip install numpy pandas scikit-learn lightgbm xgboost
git clone https://github.com/microsoft/qlib.git
cd qlib && pip install -e .
python -m qlib.init
```

## 數據獲取

### 1. 使用 Qlib DataLoader

```python
from qlib.data.dataset import DatasetH
from qlib.data.ops import Operators

# 定義因子
factor_config = {
    "Resi_12": Operators.Div(
        Operators.Rolling(Operators.Ref("close", -12), "mean"),
        Operators.Rolling(Operators.Ref("close", -1), "mean")
    ),
    "PE": Operators.Div("close", "eps_basic"),
    "ROE": "roe"
}
```

### 2. 使用 Alpha158

```python
from qlib.contrib.data.handler import Alpha158

handler = Alpha158(
    instruments="cn",
    start_time="2015-01-01",
    end_time="2026-04-18",
    fit_start_time="2015-01-01",
    fit_end_time="2015-12-31"
)
```

## 策略配置

### TopkDropoutStrategy

```python
from qlib.strategy import TopkDropoutStrategy
from qlib.contrib.strategy import LongOnlyStrategy

strategy = TopkDropoutStrategy(
    model=model,              # 訓練好的模型
    dataset=dataset,          # 數據集
    topk=50,                  # 持有Top50股票
    n_dropout=10,             # 每次換倉替換10支
    risk_config={"value": 0}
)
```

### 自訂策略

```python
class CustomStrategy:
    def __init__(self, model, dataset, topk, n_dropout):
        self.model = model
        self.dataset = dataset
        self.topk = topk
        self.n_dropout = n_dropout

    def generate_positions(self, current_date):
        # 預測
        pred = self.model.predict(self.dataset)

        # 排序並選擇 Topk
        top_stocks = pred.nlargest(self.topk).index

        # 計算權重（等權或風險平價）
        weights = {stock: 1/self.topk for stock in top_stocks}

        return weights
```

## 回測配置

```python
from qlib.workflow import R
from qlib.utils import init_instance_by_config

# 回測任務配置
backtest_config = {
    "strategy": {
        "class": "TopkDropoutStrategy",
        "module_path": "qlib.contrib.strategy",
        "kwargs": {
            "model": model,
            "dataset": dataset,
            "topk": 50,
            "n_dropout": 10
        }
    },
    "backtest": {
        "start_time": "2016-01-01",
        "end_time": "2026-04-18",
        "account": 10000000,
        "benchmark": "000300.SH",
        "exchange_kwargs": {
            "freq": "day",
            "limit_threshold": 0.099,  # 漲停閾值
            "deal_price": "close",
            "open_cost": 0.0003,
            "close_cost": 0.0013,
            "min_cost": 5
        }
    }
}

# 執行回測
init_instance_by_config(backtest_config)
```

## 常用 Benchmark

| 代碼 | 名稱 |
|------|------|
| 000300.SH | 滬深300 |
| 000905.SH | 中證500 |
| 000001.SH | 上證指數 |
| 399001.SZ | 深證成指 |

## 指標計算

```python
from qlib.contrib.report import analysis_position

# 生成回測報告
report = analysis_position(
    report_df=backtest_result["report"],
    portfolio_details=backtest_result["portfolio_details"]
)

# 輸出關鍵指標
print(f"年化收益率: {report['annualized_return']}")
print(f"夏普比率: {report['sharpe']}")
print(f"最大回撤: {report['max_drawdown']}")
```
