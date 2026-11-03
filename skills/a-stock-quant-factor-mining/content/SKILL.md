---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: fa5996ffb680d750ca16bbcc503a6fd3
    PropagateID: fa5996ffb680d750ca16bbcc503a6fd3
    ReservedCode1: 3045022100d47d3c28f981e9ff25d4aeef278f6004fc0159251d76161ceae068ea2e31899802204015174bb80e81dc9d5297130cebcbaaef12dd0264f1edb9832b51cf8ce06eaa
    ReservedCode2: 3045022100d6ef53238d247b138387ef65630911e1e45ac32b56a7f55211f30d9ef082c24402205903c928366cb435c3c700989fdf53cc41d4305ba3a72ac9236708b4acbdc46d
description: A股量化因子挖掘與10年回測優化專家。當用戶要求構建量化交易策略、因子選股、多因子組合、回測優化、追求年化20%收益時使用。支援 Qlib、AKShare、Baostock 數據源，涵蓋價值、質量、成長、動量、技術因子。
name: a-stock-quant-factor-mining
---

# A股量化因子挖掘與回測優化系統

## 系統概述

本技能為專業量化交易工程師，提供從因子發掘到策略優化的完整 pipeline，目標是在 2016-2026 年回測中達到年化 20% 收益（夏普 >1.0，最大回撤 <25%）。

## 核心工作流程

### 步驟 1：環境初始化

```python
# 安裝必要套件
pip install akshare baostock pandas numpy scikit-learn lightgbm xgboost qlib
```

### 步驟 2：數據獲取

支援數據源優先順序：
1. **AKShare** - 免費主力
2. **Baostock** - 基本面數據
3. **Qlib DataLoader** - 整合數據

```python
import akshare as ak
import baostock as bs
import pandas as pd

# 登入 Baostock
bs.login()

# 獲取滬深300成分股
hs300 = ak.stock_info_sh_name_code(symbol="滬深300")

# 獲取日線數據（示例）
df = ak.stock_zh_a_hist(symbol="000001", period="daily",
                        start_date="20150101", end_date="20260418")

# 獲取財務數據
profit_data = bs.query_profit_sheet_data(code="sz.000001", year=2024, quarter=4)
```

### 步驟 3：因子構建

```python
# 核心因子定義
FACTORS = {
    "value": {
        "pe_ttm": "市盈率(TTM)",
        "pb": "市淨率",
        "ps_ttm": "市銷率(TTM)",
        "dividend_yield": "股息率"
    },
    "quality": {
        "roe_ttm": "ROE(TTM)",
        "gross_margin": "毛利率",
        "net_margin": "淨利率",
        "current_ratio": "流動比率",
        "quick_ratio": "速動比率"
    },
    "growth": {
        "revenue_growth": "營收增長率",
        "profit_growth": "利潤增長率",
        "equity_growth": "淨資產增長率"
    },
    "momentum": {
        "mom_1m": "1月動量",
        "mom_3m": "3月動量",
        "mom_6m": "6月動量",
        "mom_12m": "12月動量",
        "mom_20d": "20日動量"
    },
    "technical": {
        "turnover_rate": "換手率",
        "volatility_20d": "20日波動率",
        "volatility_60d": "60日波動率",
        "volume_ratio": "量價相關性"
    }
}
```

### 步驟 4：因子有效性檢驗

```python
def factor_validation(factor_data, index_returns):
    """單因子IC/IR檢驗"""
    # IC (Information Coefficient)
    ic = factor_data.corrwith(index_returns)

    # IR (Information Ratio)
    ic_mean = ic.mean()
    ic_std = ic.std()
    ir = ic_mean / ic_std if ic_std != 0 else 0

    # 分層回測
    quantile_returns = {}
    for q in [0.2, 0.4, 0.6, 0.8, 1.0]:
        quantile_returns[f"Q{int(q*100)}"] = ...

    return {"IC": ic, "IC_mean": ic_mean, "IR": ir, "quantile_returns": quantile_returns}
```

### 步驟 5：多因子組合

```python
from sklearn.linear_model import Ridge
from sklearn.ensemble import GradientBoostingRegressor

def multi_factor_model(factors_df, target_returns):
    """多因子組合模型"""
    # 去除NaN和極值
    factors_clean = winsorize(factors_df, limits=[0.01, 0.99])

    # 標準化
    factors_scaled = StandardScaler().fit_transform(factors_clean)

    # 訓練 LightGBM 模型
    model = lgb.LGBMRanker(
        objective="lambdarank",
        n_estimators=100,
        learning_rate=0.05
    )

    model.fit(factors_scaled, target_returns)

    return model
```

### 步驟 6：回測框架

使用 Qlib 進行回測：

```python
# Qlib 配置
import qlib
from qlib.data.dataset import DatasetH
from qlib.strategy import TopkDropoutStrategy

qlib.init(provider_uri="./data")

# 策略定義
strategy = TopkDropoutStrategy(
    model=model,
    dataset=dataset,
    topk=50,
    n_dropout=5
)

# 回測執行
backtest_config = {
    "strategy": strategy,
    "backtest": {
        "start_time": "2016-01-01",
        "end_time": "2026-04-18",
        "account": 10000000,  # 1000萬
        "benchmark": "000300.SH"
    }
}
```

### 步驟 7：績效評估

```python
def evaluate_performance(portfolio_returns, benchmark_returns):
    """完整績效評估"""
    results = {
        "年化收益率": calculate_annual_return(portfolio_returns),
        "年化波動率": calculate_annual_volatility(portfolio_returns),
        "夏普比率": calculate_sharpe_ratio(portfolio_returns),
        "最大回撤": calculate_max_drawdown(portfolio_returns),
        "卡瑪比率": results["年化收益率"] / abs(results["最大回撤"]),
        "勝率": calculate_win_rate(portfolio_returns),
        "盈虧比": calculate_profit_loss_ratio(portfolio_returns)
    }
    return results
```

## A股特殊約束處理

```python
# T+1 交易約束
NO_TRADE_IF_UP_LIMIT = True  # 漲停不買入
NO_TRADE_IF_DOWN_LIMIT = True  # 跌停不賣出

# 交易成本
COMMISSION_RATE = 0.0003  # 萬三
STAMP_TAX_RATE = 0.001    # 千分之一（賣出時）

# 滑點
SLIPPAGE_RATE = 0.0005  # 萬五

# 停牌處理
EXCLUDE_SUSPENDED = True  # 排除停牌股票
```

## 輸出格式標準

每次迭代後輸出：

```
【當前階段】因子組合 vX.X
【數據獲取狀態】股票池: XXX 支, 時間範圍: XXXX-XX ~ XXXX-XX
【因子列表與有效性】
  - 動量因子 IC: X.XX, IR: X.XX
  - 價值因子 IC: X.XX, IR: X.XX
  ...
【回測結果】
  | 指標 | 策略 | 基準(000300) |
  | 年化收益率 | XX.XX% | XX.XX% |
  | 夏普比率 | X.XX | X.XX |
  | 最大回撤 | XX.XX% | XX.XX% |
【淨值曲線】[描述曲線特徵]
【下一步計劃】建議添加XX因子 / 調整倉位優化 / 風控增強
```

## 迭代策略

1. **第一階段**：單因子 baseline（12月動量）
2. **第二階段**：加入價值/質量因子
3. **第三階段**：機器學習多因子模型
4. **第四階段**：倉位優化（風險平價）
5. **第五階段**：風控增強（行業中性、止損）
6. **第六階段**：參數搜索與最終優化

## 安全聲明

⚠️ **重要提醒**：
- 所有回測均為歷史模擬，不構成實盤建議
- 實盤前必須經過人工驗證和風控審核
- 過去業績不代表未來表現
- A股市場存在黑天鵝事件風險

## 觸發條件

當用戶提供以下關鍵詞時觸發：
- 量化交易、因子選股、多因子策略
- 回測優化、策略評估
- Qlib、AKShare、Baostock
- 年化收益、夏普比率
- A股、滬深300、中證500
