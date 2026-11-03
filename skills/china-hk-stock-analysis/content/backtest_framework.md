# 量化回测框架 v2.0

本框架用于验证股票分析评分体系的有效性，通过三层回测结构实现从逻辑到结果到策略的完整验证。

---

## 一、核心设计原则

1. **避免未来函数**: 评分仅使用当期可获得数据
2. **考虑交易成本**: 印花税0.1%, 佣金0.03%
3. **流动性约束**: 日均成交额<1亿不做大仓位
4. **存活者偏差**: 纳入退市股票
5. **稳健性优先**: 不是最大化历史收益，而是最大化策略的长期稳定性

---

## 二、三层回测结构

### 第一层：逻辑评估

**目的**: 判断分析是否符合价值投资原则，输出逻辑可信度评分

```python
class LogicEvaluator:
    """
    逻辑评估器 - 检验分析是否符合投资原理
    """

    def evaluate(self, analysis_result: dict) -> dict:
        """
        评估分析逻辑质量

        返回:
            logic_score: 0-100
            logic_explanation: 逻辑解释
            risk_flags: 风险标记列表
        """
        scores = {
            "pe_check": self._check_pe(analysis_result),      # PE合理性
            "peg_check": self._check_peg(analysis_result),    # PEG合理性
            "roic_check": self._check_roic(analysis_result),  # ROIC合理性
            "fcf_check": self._check_fcf(analysis_result),   # 自由现金流
            "div_check": self._check_dividend(analysis_result), # 股息合理性
            "growth_check": self._check_growth(analysis_result), # 成长性一致性
        }

        # 权重计算
        weights = {
            "pe_check": 0.20,
            "peg_check": 0.20,
            "roic_check": 0.25,
            "fcf_check": 0.15,
            "div_check": 0.10,
            "growth_check": 0.10,
        }

        logic_score = sum(scores[k] * weights[k] for k in scores)

        return {
            "logic_score": round(logic_score, 1),
            "component_scores": scores,
            "risk_flags": self._identify_risk_flags(scores),
            "logic_explanation": self._generate_explanation(scores),
            "is_valid": logic_score >= 60,
        }

    def _check_pe(self, result: dict) -> float:
        """PE合理性检查"""
        pe = result.get("pe", 0)
        roe = result.get("roe", 0)

        # PE与ROE应匹配 (PEG原则)
        if pe <= 0:
            return 0
        peg = pe / (roe * 100) if roe > 0 else 999

        if peg < 0:
            return 0
        elif peg <= 0.8:
            return 100  # 非常合理
        elif peg <= 1.2:
            return 80   # 合理
        elif peg <= 1.5:
            return 60   # 略贵
        elif peg <= 2.0:
            return 40   # 偏贵
        else:
            return 20   # 极贵

    def _check_peg(self, result: dict) -> float:
        """PEG合理性检查"""
        peg = result.get("peg", 999)

        if peg < 0:
            return 0
        elif peg <= 0.5:
            return 100  # 极度低估
        elif peg <= 0.8:
            return 90   # 严重低估
        elif peg <= 1.0:
            return 70   # 合理
        elif peg <= 1.5:
            return 50   # 略贵
        else:
            return 30   # 偏贵

    def _check_roic(self, result: dict) -> float:
        """ROIC合理性检查"""
        roic = result.get("roic", 0)

        if roic <= 0:
            return 0
        elif roic >= 20:
            return 100  # 优秀
        elif roic >= 15:
            return 85   # 良好
        elif roic >= 10:
            return 70   # 中等
        elif roic >= 5:
            return 50   # 一般
        else:
            return 30   # 较差

    def _check_fcf(self, result: dict) -> float:
        """自由现金流检查"""
        fcf = result.get("free_cash_flow", 0)
        net_income = result.get("net_income", 0)

        if fcf <= 0:
            return 20   # 负现金流风险高
        elif net_income <= 0:
            return 40   # 亏损
        else:
            ratio = fcf / net_income
            if ratio >= 1.0:
                return 100  # 现金流充沛
            elif ratio >= 0.7:
                return 80   # 良好
            elif ratio >= 0.4:
                return 60   # 中等
            else:
                return 40   # 现金流一般

    def _check_dividend(self, result: dict) -> float:
        """股息合理性检查"""
        div_yield = result.get("dividend_yield", 0)
        payout_ratio = result.get("payout_ratio", 0)

        if div_yield <= 0:
            return 30 if payout_ratio < 30 else 60  # 不分红看情况
        elif div_yield > 15:
            return 30   # 异常高，可能陷阱
        elif payout_ratio > 100:
            return 30   # 不可持续
        elif payout_ratio > 80:
            return 50   # 偏高
        elif payout_ratio > 50:
            return 80   # 合理
        else:
            return 100  # 偏低但安全

    def _check_growth(self, result: dict) -> float:
        """成长性与估值一致性检查"""
        revenue_growth = result.get("revenue_growth", 0)
        net_profit_growth = result.get("net_profit_growth", 0)
        pe = result.get("pe", 0)

        # 成长型股票应有合理PE
        avg_growth = (revenue_growth + net_profit_growth) / 2

        if avg_growth <= 0:
            return 50   # 无成长性
        elif pe <= 0:
            return 50

        expected_pe = avg_growth * 2  # 简化模型
        if expected_pe <= 0:
            return 50

        pe_ratio = pe / expected_pe

        if pe_ratio <= 0.8:
            return 100  # 成长被低估
        elif pe_ratio <= 1.2:
            return 80   # 合理
        elif pe_ratio <= 1.5:
            return 60   # 略贵
        else:
            return 40   # 成长被高估

    def _identify_risk_flags(self, scores: dict) -> list:
        """识别风险标记"""
        flags = []
        if scores["pe_check"] < 50:
            flags.append("⚠️ PE估值异常")
        if scores["peg_check"] < 50:
            flags.append("⚠️ PEG显示过高估值")
        if scores["roic_check"] < 50:
            flags.append("⚠️ ROIC偏低，资本效率差")
        if scores["fcf_check"] < 50:
            flags.append("⚠️ 自由现金流不足")
        if scores["div_check"] < 50:
            flags.append("⚠️ 股息政策存疑")
        if scores["growth_check"] < 50:
            flags.append("⚠️ 成长性与估值不匹配")
        return flags

    def _generate_explanation(self, scores: dict) -> str:
        """生成逻辑解释"""
        avg = sum(scores.values()) / len(scores)
        if avg >= 80:
            return "逻辑严谨，符合价值投资原则"
        elif avg >= 60:
            return "逻辑基本合理，存在小幅改进空间"
        elif avg >= 40:
            return "逻辑存在矛盾，需进一步验证"
        else:
            return "逻辑存在严重问题，建议重新审视分析"
```

**逻辑评分输出格式**:
```json
{
  "logic_score": 78.5,
  "component_scores": {
    "pe_check": 80,
    "peg_check": 70,
    "roic_check": 85,
    "fcf_check": 90,
    "div_check": 75,
    "growth_check": 70
  },
  "risk_flags": [],
  "logic_explanation": "逻辑基本合理，存在小幅改进空间",
  "is_valid": true
}
```

---

### 第二层：结果跟踪

**目的**: 记录分析时价格，自动跟踪未来收益，验证预测有效性

```python
class ResultTracker:
    """
    结果跟踪器 - 自动跟踪预测收益
    """

    def __init__(self):
        self.tracking_records = []

    def create_record(self, analysis_result: dict, current_price: float,
                      current_date: str, target_price: float = None) -> dict:
        """
        创建跟踪记录

        参数:
            analysis_result: 分析结果
            current_price: 当前价格
            current_date: 分析日期
            target_price: 目标价格(可选)
        """
        record = {
            "report_id": analysis_result.get("report_id"),
            "stock_code": analysis_result.get("stock_code"),
            "stock_name": analysis_result.get("stock_name"),
            "analysis_date": current_date,
            "analysis_price": current_price,
            "signal": analysis_result.get("signal"),
            "score": analysis_result.get("composite_score"),
            "target_price": target_price,
            "tracking": {
                "day_7": {"price": None, "return_pct": None, "valid": None},
                "day_30": {"price": None, "return_pct": None, "valid": None},
                "day_90": {"price": None, "return_pct": None, "valid": None},
            },
            "prediction_correct": None,
        }
        self.tracking_records.append(record)
        return record

    def update_tracking(self, record_id: str, price_data: dict):
        """
        更新跟踪价格

        price_data格式: {"date": "2024-01-08", "price": 185.5}
        """
        record = self._find_record(record_id)
        if not record:
            return

        analysis_price = record["analysis_price"]
        analysis_date = datetime.strptime(record["analysis_date"], "%Y-%m-%d")
        update_date = datetime.strptime(price_data["date"], "%Y-%m-%d")
        days_diff = (update_date - analysis_date).days

        price = price_data["price"]
        return_pct = (price - analysis_price) / analysis_price * 100

        if days_diff <= 10:
            record["tracking"]["day_7"] = {
                "price": price,
                "return_pct": round(return_pct, 2),
                "valid": True,
                "update_date": price_data["date"]
            }
        elif days_diff <= 35:
            record["tracking"]["day_30"] = {
                "price": price,
                "return_pct": round(return_pct, 2),
                "valid": True,
                "update_date": price_data["date"]
            }
        elif days_diff <= 95:
            record["tracking"]["day_90"] = {
                "price": price,
                "return_pct": round(return_pct, 2),
                "valid": True,
                "update_date": price_data["date"]
            }

        # 判断预测是否正确
        self._evaluate_prediction(record)

    def _evaluate_prediction(self, record: dict):
        """
        评估预测是否正确

        规则:
        - BUY信号: 价格上涨=正确
        - SELL信号: 价格下跌=正确
        - HOLD信号: 变化<5%=正确
        """
        signal = record["signal"]
        day_30 = record["tracking"]["day_30"]
        day_90 = record["tracking"]["day_90"]

        if not day_90["valid"]:
            return

        return_pct = day_90["return_pct"]

        if signal in ["STRONG_BUY", "BUY"]:
            record["prediction_correct"] = return_pct > 0
        elif signal in ["SELL", "STRONG_SELL"]:
            record["prediction_correct"] = return_pct < 0
        else:  # HOLD
            record["prediction_correct"] = abs(return_pct) < 5

        record["actual_return_pct"] = return_pct

    def get_tracking_summary(self) -> dict:
        """
        获取跟踪汇总

        返回:
            summary: 跟踪汇总数据
        """
        total = len(self.tracking_records)
        completed_90 = sum(
            1 for r in self.tracking_records
            if r["tracking"]["day_90"]["valid"]
        )
        correct = sum(
            1 for r in self.tracking_records
            if r.get("prediction_correct") == True
        )

        return {
            "total_records": total,
            "completed_90_days": completed_90,
            "prediction_accuracy": round(correct / completed_90 * 100, 1)
                if completed_90 > 0 else None,
            "records": self.tracking_records
        }
```

**结果跟踪输出格式**:
```json
{
  "report_id": "uuid-xxx",
  "stock_code": "000333.SZ",
  "stock_name": "美的集团",
  "analysis_date": "2024-01-01",
  "analysis_price": 180.50,
  "signal": "BUY",
  "composite_score": 82.5,
  "target_price": 216.60,
  "tracking": {
    "day_7": {
      "price": 183.20,
      "return_pct": 1.50,
      "valid": true,
      "update_date": "2024-01-08"
    },
    "day_30": {
      "price": 188.30,
      "return_pct": 4.32,
      "valid": true,
      "update_date": "2024-01-31"
    },
    "day_90": {
      "price": 195.00,
      "return_pct": 8.03,
      "valid": true,
      "update_date": "2024-03-31"
    }
  },
  "prediction_correct": true,
  "actual_return_pct": 8.03
}
```

---

### 第三层：策略评估

**目的**: 汇总多只股票分析结果，输出策略级指标

```python
class StrategyEvaluator:
    """
    策略评估器 - 聚合多只股票分析结果
    """

    def __init__(self, benchmark_code: str = "000300.SH"):
        self.benchmark_code = benchmark_code  # 沪深300作为基准
        self.strategy_returns = []
        self.benchmark_returns = []
        self.records = []

    def add_record(self, tracking_record: dict):
        """添加跟踪记录"""
        self.records.append(tracking_record)

    def evaluate(self) -> dict:
        """
        策略评估

        返回:
            strategy_metrics: 策略级指标
        """
        if not self.records:
            return {"error": "No records to evaluate"}

        # 过滤有效记录
        valid_records = [
            r for r in self.records
            if r.get("actual_return_pct") is not None
        ]

        if len(valid_records) < 5:
            return {"error": "Insufficient records for evaluation"}

        returns = [r["actual_return_pct"] for r in valid_records]
        signals = [r["signal"] for r in valid_records]

        # 计算基准收益(简化:用恒生/沪深300平均收益代替)
        benchmark_return = self._get_benchmark_return(valid_records)

        # 基础指标
        win_rate = sum(1 for r in returns if r > 0) / len(returns)
        avg_return = sum(returns) / len(returns)
        max_drawdown = self._calculate_max_drawdown(returns)
        max_return = max(returns)
        min_return = min(returns)

        # 相对基准(Alpha)
        alpha = avg_return - benchmark_return

        # 分信号统计
        signal_stats = self._calculate_signal_stats(valid_records)

        # 风险调整收益
        volatility = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
        sharpe_ratio = (avg_return - 0.03) / volatility if volatility > 0 else 0
        calmar_ratio = avg_return / abs(max_drawdown) if max_drawdown != 0 else 0

        return {
            "strategy_metrics": {
                "total_analysis": len(valid_records),
                "win_rate": round(win_rate * 100, 1),
                "avg_return": round(avg_return, 2),
                "max_drawdown": round(max_drawdown, 2),
                "max_return": round(max_return, 2),
                "min_return": round(min_return, 2),
                "alpha_vs_benchmark": round(alpha, 2),
                "volatility": round(volatility, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "calmar_ratio": round(calmar_ratio, 2),
                "benchmark_return": round(benchmark_return, 2),
            },
            "signal_breakdown": signal_stats,
            "records_summary": {
                "STRONG_BUY": sum(1 for s in signals if s == "STRONG_BUY"),
                "BUY": sum(1 for s in signals if s == "BUY"),
                "HOLD": sum(1 for s in signals if s == "HOLD"),
                "SELL": sum(1 for s in signals if s == "SELL"),
                "STRONG_SELL": sum(1 for s in signals if s == "STRONG_SELL"),
            }
        }

    def _calculate_signal_stats(self, records: list) -> dict:
        """分信号统计"""
        stats = {}
        for signal in ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]:
            signal_records = [r for r in records if r["signal"] == signal]
            if not signal_records:
                continue

            returns = [r["actual_return_pct"] for r in signal_records]
            win_rate = sum(1 for r in returns if r > 0) / len(returns)

            stats[signal] = {
                "count": len(signal_records),
                "win_rate": round(win_rate * 100, 1),
                "avg_return": round(sum(returns) / len(returns), 2),
                "max_return": round(max(returns), 2),
                "min_return": round(min(returns), 2),
            }
        return stats

    def _calculate_max_drawdown(self, returns: list) -> float:
        """计算最大回撤"""
        cumulative = [100]
        for r in returns:
            cumulative.append(cumulative[-1] * (1 + r / 100))

        max_dd = 0
        peak = cumulative[0]
        for val in cumulative:
            if val > peak:
                peak = val
            dd = (peak - val) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _get_benchmark_return(self, records: list) -> float:
        """
        获取基准收益(简化版)

        实际应用中应获取对应日期的沪深300/恒生指数收益
        """
        # 简化: 假设基准年化收益8%
        days = 90
        return 8 * days / 365
```

**策略评估输出格式**:
```json
{
  "strategy_metrics": {
    "total_analysis": 25,
    "win_rate": 68.0,
    "avg_return": 8.5,
    "max_drawdown": -12.3,
    "max_return": 25.6,
    "min_return": -8.2,
    "alpha_vs_benchmark": 4.2,
    "volatility": 15.3,
    "sharpe_ratio": 0.52,
    "calmar_ratio": 0.69,
    "benchmark_return": 4.3
  },
  "signal_breakdown": {
    "BUY": {
      "count": 12,
      "win_rate": 75.0,
      "avg_return": 10.2,
      "max_return": 25.6,
      "min_return": -5.3
    },
    "HOLD": {
      "count": 8,
      "win_rate": 62.5,
      "avg_return": 3.8,
      "max_return": 12.1,
      "min_return": -8.2
    }
  },
  "records_summary": {
    "STRONG_BUY": 5,
    "BUY": 12,
    "HOLD": 8,
    "SELL": 0,
    "STRONG_SELL": 0
  }
}
```

---

## 三、回测信号定义

### 3.1 评分信号

```python
SIGNAL_THRESHOLDS = {
    "STRONG_BUY": 85,   # 综合评分 >= 85
    "BUY": 75,          # 综合评分 >= 75
    "HOLD": 60,         # 综合评分 60-74
    "SELL": 45,         # 综合评分 45-59
    "STRONG_SELL": 0,   # 综合评分 < 45
}
```

### 3.2 持仓规则

| 信号 | 操作 | 仓位 |
|------|------|------|
| STRONG_BUY | 全仓买入 | 100% |
| BUY | 8成仓 | 80% |
| HOLD | 观望 | 0% |
| SELL | 清仓 | 0% |
| STRONG_SELL | 做空/空仓 | 0% |

### 3.3 止损止盈

```python
STOP_LOSS = 0.08      # 止损8%
TAKE_PROFIT = 0.25   # 止盈25%
REBALANCE_PERIOD = 20  # 再平衡周期(交易日)
```

---

## 四、评分有效性检验

### 4.1 分位数组合收益

将股票按综合评分分为10组,验证高分组是否收益更高:

| 分组 | 评分范围 | 期望收益 | 验证标准 |
|------|----------|----------|----------|
| Q1(最高) | 90-100 | >15% | 年化收益最高 |
| Q2 | 80-89 | >12% | 显著正alpha |
| Q3 | 70-79 | >8% | 正alpha |
| Q4 | 60-69 | >5% | 接近大盘 |
| Q5 | 50-59 | 0-5% | 接近大盘 |
| Q6 | 40-49 | 0% | 大盘或以下 |
| Q7 | 30-39 | <0% | 负alpha |
| Q8 | 20-29 | <-5% | 显著负alpha |
| Q9 | 10-19 | <-10% | 差于大盘 |
| Q10(最低) | 0-9 | <-15% | 年化收益最低 |

**验证公式**:
```
IC (Information Coefficient) = corr(评分, 未来收益)
```
> IC > 0.05: 评分有效
> IC > 0.10: 评分高度有效
> IC < 0.02: 评分无效

### 4.2 多空组合收益

```
Long Q1 (最高评分) + Short Q10 (最低评分)
期望: 年化 > 15%, 夏普比率 > 1.0
```

---

## 五、自动回测优化（稳健性优先）

### 5.1 核心原则

**不是最大化历史收益，而是最大化策略的长期稳定性（robustness）**

### 5.2 数据分离

```python
class TrainTestSplitter:
    """
    训练集/测试集分离器
    """

    def split(self, data: pd.DataFrame,
              train_ratio: float = 0.7,
              method: str = "time") -> tuple:
        """
        数据分离

        参数:
            data: 完整数据集
            train_ratio: 训练集比例
            method: 分离方法
                - "time": 时间序列分离
                - "random": 随机分离

        返回:
            (train_data, test_data)
        """
        if method == "time":
            split_idx = int(len(data) * train_ratio)
            train_data = data.iloc[:split_idx]
            test_data = data.iloc[split_idx:]
        elif method == "random":
            train_data = data.sample(frac=train_ratio, random_state=42)
            test_data = data.drop(train_data.index)
        else:
            raise ValueError(f"Unknown method: {method}")

        return train_data, test_data

    def walk_forward_split(self, data: pd.DataFrame,
                           train_window: int = 252,
                           test_window: int = 63) -> list:
        """
        滚动回测分离 (walk-forward)

        每年滚动训练和测试

        返回:
            [(train_1, test_1), (train_2, test_2), ...]
        """
        splits = []
        start = 0

        while start + train_window + test_window <= len(data):
            train_end = start + train_window
            test_end = train_end + test_window

            train_data = data.iloc[start:train_end]
            test_data = data.iloc[train_end:test_end]

            splits.append((train_data, test_data))

            start += test_window  # 滚动窗口

        return splits
```

### 5.3 滚动回测（Walk-Forward）

```python
class WalkForwardBacktest:
    """
    滚动回测引擎

    多时间窗口反复训练和测试，输出平均表现
    """

    def __init__(self, strategy_evaluator: StrategyEvaluator):
        self.strategy_evaluator = strategy_evaluator
        self.walk_forward_results = []

    def run(self, data: pd.DataFrame,
            train_window: int = 252,
            test_window: int = 63) -> dict:
        """
        执行滚动回测

        参数:
            data: 价格数据 (date x stock)
            train_window: 训练窗口 (交易日)
            test_window: 测试窗口 (交易日)
        """
        splitter = TrainTestSplitter()
        splits = splitter.walk_forward_split(
            data, train_window, test_window
        )

        all_metrics = []

        for i, (train_data, test_data) in enumerate(splits):
            # 1. 训练集优化参数
            optimized_params = self._optimize_on_train(train_data)

            # 2. 测试集验证
            test_metrics = self._evaluate_on_test(test_data, optimized_params)

            all_metrics.append({
                "window_id": i,
                "train_period": f"{train_data.index[0]} to {train_data.index[-1]}",
                "test_period": f"{test_data.index[0]} to {test_data.index[-1]}",
                "train_metrics": self._calculate_metrics(train_data),
                "test_metrics": test_metrics,
                "params": optimized_params,
            })

            self.walk_forward_results.append(all_metrics[-1])

        return self._aggregate_results(all_metrics)

    def _optimize_on_train(self, train_data: pd.DataFrame) -> dict:
        """在训练集上优化参数"""
        # 简化的参数网格搜索
        param_grid = {
            "pe_weight": [0.15, 0.20, 0.25],
            "roe_weight": [0.15, 0.18, 0.20],
            "momentum_weight": [0.10, 0.15, 0.20],
        }

        best_ic = -1
        best_params = {}

        # 网格搜索
        for pe_w in param_grid["pe_weight"]:
            for roe_w in param_grid["roe_weight"]:
                for mom_w in param_grid["momentum_weight"]:
                    # 验证权重和为1
                    if abs(pe_w + roe_w + mom_w - 1.0) > 0.01:
                        continue

                    # 计算IC
                    ic = self._calculate_ic(train_data, {
                        "pe_weight": pe_w,
                        "roe_weight": roe_w,
                        "momentum_weight": mom_w,
                    })

                    if ic > best_ic:
                        best_ic = ic
                        best_params = {
                            "pe_weight": pe_w,
                            "roe_weight": roe_w,
                            "momentum_weight": mom_w,
                            "ic": ic,
                        }

        return best_params

    def _evaluate_on_test(self, test_data: pd.DataFrame,
                          params: dict) -> dict:
        """在测试集上评估"""
        # 使用优化参数计算评分
        scores = self._calculate_scores(test_data, params)

        # 计算测试集指标
        returns = self._calculate_returns(test_data)
        ic = self._calculate_ic(test_data, params)

        return {
            "ic": ic,
            "avg_return": returns.mean(),
            "sharpe_ratio": self._calculate_sharpe(returns),
            "max_drawdown": self._calculate_max_drawdown(returns),
        }

    def _aggregate_results(self, all_metrics: list) -> dict:
        """聚合滚动回测结果"""
        n = len(all_metrics)

        train_ics = [m["train_metrics"]["ic"] for m in all_metrics]
        test_ics = [m["test_metrics"]["ic"] for m in all_metrics]
        train_returns = [m["train_metrics"]["avg_return"] for m in all_metrics]
        test_returns = [m["test_metrics"]["avg_return"] for m in all_metrics]

        # 统计参数稳定性
        param_values = {}
        for m in all_metrics:
            for k, v in m["params"].items():
                if k != "ic":
                    if k not in param_values:
                        param_values[k] = []
                    param_values[k].append(v)

        param_stability = {
            k: {
                "mean": sum(v) / len(v),
                "std": (sum((x - sum(v)/len(v))**2 for x in v) / len(v)) ** 0.5,
                "min": min(v),
                "max": max(v),
            }
            for k, v in param_values.items()
        }

        return {
            "walk_forward_summary": {
                "num_windows": n,
                "train_period": f"{all_metrics[0]['train_period']} to {all_metrics[-1]['train_period']}",
                "test_period": f"{all_metrics[0]['test_period']} to {all_metrics[-1]['test_period']}",
            },
            "train_vs_test": {
                "train_ic_mean": sum(train_ics) / n,
                "test_ic_mean": sum(test_ics) / n,
                "train_return_mean": sum(train_returns) / n,
                "test_return_mean": sum(test_returns) / n,
                "overfitting_risk": self._calculate_overfitting_risk(
                    train_ics, test_ics
                ),
            },
            "parameter_stability": param_stability,
            "individual_windows": all_metrics,
        }

    def _calculate_overfitting_risk(self, train_ics: list,
                                    test_ics: list) -> str:
        """计算过拟合风险"""
        train_mean = sum(train_ics) / len(train_ics)
        test_mean = sum(test_ics) / len(test_ics)

        degradation = (train_mean - test_mean) / train_mean

        if degradation < 0.1:
            return "LOW"
        elif degradation < 0.3:
            return "MEDIUM"
        else:
            return "HIGH"
```

### 5.4 参数稳定性分析

**不输出单一最优参数，输出"有效区间"**

```python
class ParameterStabilityAnalyzer:
    """
    参数稳定性分析器

    不输出单一最优参数，而是输出"有效区间"
    """

    def analyze(self, param_history: list, ic_history: list) -> dict:
        """
        分析参数稳定性

        参数:
            param_history: 参数历史记录列表
            ic_history: 对应的IC历史记录

        返回:
            stability_report: 稳定性报告
        """
        # 找出IC > 0.8 * max_ic的有效参数区间
        max_ic = max(ic_history)
        threshold = 0.8 * max_ic

        valid_params = [
            (p, ic) for p, ic in zip(param_history, ic_history)
            if ic >= threshold
        ]

        if not valid_params:
            return {"error": "No valid parameters found"}

        valid_params_only = [p for p, _ in valid_params]

        # 计算每个参数的有效区间
        param_ranges = {}
        for key in valid_params_only[0].keys():
            values = [p[key] for p in valid_params_only]
            param_ranges[key] = {
                "effective_range": [min(values), max(values)],
                "center": sum(values) / len(values),
                "width": max(values) - min(values),
                "robust_score": self._calculate_robust_score(
                    values, ic_history, valid_params
                ),
            }

        # 稳定性评分
        avg_width = sum(v["width"] for v in param_ranges.values()) / len(param_ranges)
        robust_score = max(0, 100 - avg_width * 10)

        return {
            "effective_ranges": param_ranges,
            "robust_score": round(robust_score, 1),
            "valid_param_count": len(valid_params),
            "total_param_count": len(param_history),
            "coverage_ratio": round(len(valid_params) / len(param_history), 2),
        }

    def _calculate_robust_score(self, values: list, ic_history: list,
                                 valid_params: list) -> float:
        """计算稳定性评分"""
        if not values:
            return 0

        # 参数方差越小越稳定
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = variance ** 0.5

        # IC均值
        valid_ics = [ic for _, ic in valid_params]
        mean_ic = sum(valid_ics) / len(valid_ics)

        # 稳定性 = IC均值 / (1 + 参数标准差)
        stability = mean_ic / (1 + std)

        return round(stability, 4)
```

**参数稳定性输出格式**:
```json
{
  "effective_ranges": {
    "pe_weight": {
      "effective_range": [0.15, 0.25],
      "center": 0.20,
      "width": 0.10,
      "robust_score": 0.82
    },
    "roe_weight": {
      "effective_range": [0.15, 0.20],
      "center": 0.175,
      "width": 0.05,
      "robust_score": 0.88
    }
  },
  "robust_score": 78.5,
  "valid_param_count": 12,
  "total_param_count": 27,
  "coverage_ratio": 0.44
}
```

### 5.5 复杂度惩罚

```python
class ComplexityPenalty:
    """
    复杂度惩罚计算器

    策略规则越多，惩罚越高
    """

    def calculate(self, rules: list, base_score: float) -> dict:
        """
        计算复杂度惩罚后的分数

        参数:
            rules: 策略规则列表
            base_score: 原始评分

        返回:
            adjusted_score: 调整后评分
            penalty: 惩罚值
        """
        num_rules = len(rules)

        # 复杂度惩罚曲线
        if num_rules <= 3:
            penalty = 0
        elif num_rules <= 5:
            penalty = (num_rules - 3) * 0.02  # 每增加1条规则扣2%
        elif num_rules <= 8:
            penalty = 0.04 + (num_rules - 5) * 0.03  # 每增加1条规则扣3%
        else:
            penalty = 0.13 + (num_rules - 8) * 0.05  # 每增加1条规则扣5%

        # 特殊规则惩罚
        special_penalties = {
            "technical_timing": 0.05,   # 技术择时
            "short Selling": 0.10,     # 做空规则
            "leverage": 0.08,           # 杠杆使用
            "options_hedging": 0.06,    # 期权对冲
        }

        for rule in rules:
            if rule in special_penalties:
                penalty += special_penalties[rule]

        adjusted_score = base_score * (1 - penalty)

        return {
            "original_score": base_score,
            "adjusted_score": round(adjusted_score, 2),
            "penalty_rate": round(penalty * 100, 1),
            "penalty_amount": round(base_score * penalty, 2),
            "num_rules": num_rules,
            "recommendation": "优先选择简单策略" if num_rules > 5 else "策略复杂度适中",
        }
```

---

## 六、压力测试

```python
class StressTest:
    """
    压力测试器

    在熊市或高波动市场测试策略
    """

    def run(self, historical_data: pd.DataFrame,
            strategy_func: callable) -> dict:
        """
        执行压力测试

        参数:
            historical_data: 历史数据
            strategy_func: 策略函数

        返回:
            stress_test_report: 压力测试报告
        """
        # 定义压力场景
        scenarios = {
            "bear_market_2022": self._define_bear_market_2022(historical_data),
            "high_volatility": self._define_high_volatility(historical_data),
            "liquidity_crisis": self._define_liquidity_crisis(historical_data),
            "rate_hike_env": self._define_rate_hike_env(historical_data),
        }

        results = {}
        for name, data in scenarios.items():
            metrics = self._test_scenario(data, strategy_func)
            results[name] = metrics

        # 汇总
        max_drawdowns = [r["max_drawdown"] for r in results.values()]
        returns = [r["avg_return"] for r in results.values()]

        return {
            "scenarios": results,
            "summary": {
                "worst_drawdown": min(max_drawdowns),
                "worst_return": min(returns),
                "avg_return_under_stress": sum(returns) / len(returns),
                "survival_score": self._calculate_survival_score(results),
            },
            "risk_assessment": self._assess_risk(results),
        }

    def _define_bear_market_2022(self, data: pd.DataFrame) -> pd.DataFrame:
        """2022年熊市场景"""
        # 筛选2022年数据
        return data["2022-01-01":"2022-12-31"]

    def _define_high_volatility(self, data: pd.DataFrame) -> pd.DataFrame:
        """高波动场景"""
        # VIX > 30 的时期
        return data  # 需要VIX数据

    def _calculate_survival_score(self, results: dict) -> float:
        """
        计算生存评分

        0-100分，越高表示抗风险能力越强
        """
        score = 100

        for scenario, metrics in results.items():
            dd = metrics["max_drawdown"]
            ret = metrics["avg_return"]

            # 回撤惩罚
            if dd < -30:
                score -= 30
            elif dd < -20:
                score -= 20
            elif dd < -15:
                score -= 10

            # 收益惩罚
            if ret < -20:
                score -= 20
            elif ret < -10:
                score -= 10
            elif ret < -5:
                score -= 5

        return max(0, score)
```

**压力测试输出格式**:
```json
{
  "scenarios": {
    "bear_market_2022": {
      "period": "2022-01 to 2022-12",
      "avg_return": -8.5,
      "max_drawdown": -18.2,
      "sharpe_ratio": -0.45,
      "survived": true
    },
    "high_volatility": {
      "period": "2020-03 to 2020-04",
      "avg_return": -5.2,
      "max_drawdown": -22.1,
      "sharpe_ratio": -0.62,
      "survived": true
    }
  },
  "summary": {
    "worst_drawdown": -22.1,
    "worst_return": -8.5,
    "avg_return_under_stress": -6.85,
    "survival_score": 65.0
  },
  "risk_assessment": "中等抗风险能力，熊市需降低仓位"
}
```

---

## 七、综合回测输出

### 7.1 最终输出结构

```json
{
  "backtest_result": {
    "三层回测": {
      "第一层_逻辑评估": {
        "total_analyzed": 25,
        "avg_logic_score": 76.5,
        "logic_distribution": {
          "excellent (80-100)": 8,
          "good (60-79)": 12,
          "fair (40-59)": 4,
          "poor (<40)": 1
        },
        "common_risk_flags": ["PE偏高", "ROIC偏低"]
      },
      "第二层_结果跟踪": {
        "total_tracked": 20,
        "completed_90_days": 18,
        "prediction_accuracy": 72.2,
        "avg_actual_return": 8.3
      },
      "第三层_策略评估": {
        "win_rate": 68.0,
        "avg_return": 8.5,
        "max_drawdown": -12.3,
        "alpha_vs_benchmark": 4.2,
        "sharpe_ratio": 0.52
      }
    },
    "自动优化": {
      "train_test_split": {
        "train_period": "2019-2021",
        "test_period": "2022-2023",
        "train_return": 15.2,
        "test_return": 11.8
      },
      "walk_forward": {
        "num_windows": 4,
        "avg_train_ic": 0.082,
        "avg_test_ic": 0.065,
        "overfitting_risk": "LOW"
      },
      "parameter_stability": {
        "pe_weight": {"range": [0.15, 0.25], "robust_score": 0.82},
        "roe_weight": {"range": [0.15, 0.20], "robust_score": 0.88},
        "robust_score": 78.5
      },
      "complexity_penalty": {
        "num_rules": 4,
        "penalty_rate": "2%",
        "recommendation": "策略复杂度适中"
      }
    },
    "压力测试": {
      "bear_market_2022": {"return": -8.5, "drawdown": -18.2},
      "high_volatility": {"return": -5.2, "drawdown": -22.1},
      "survival_score": 65.0
    },
    "最终结论": {
      "backtest_return_train": "15.2%",
      "backtest_return_test": "11.8%",
      "robust_score": 78.5,
      "parameter_intervals": {
        "pe_weight": "0.15-0.25",
        "roe_weight": "0.15-0.20"
      },
      "max_drawdown": "-22.1%",
      "overfitting_flag": false,
      "strategy_recommendation": "策略可用于实盘，但需在熊市降低仓位"
    }
  }
}
```

---

## 八、风控模型

### 8.1 仓位管理

```python
def calculate_position(signal_strength, volatility, max_position=1.0):
    """
    凯利公式仓位计算

    公式: f* = (bp - q) / b
    其中: b=赔率, p=胜率, q=败率
    """
    win_rate = 0.55  # 历史胜率
    avg_win = 0.15   # 平均盈利
    avg_loss = 0.08  # 平均亏损
    b = avg_win / avg_loss

    f_star = (b * win_rate - (1 - win_rate)) / b
    position = min(f_star * signal_strength / 3, max_position)

    # 波动率调整
    if volatility > 0.30:
        position *= 0.7
    elif volatility < 0.15:
        position *= 1.2

    return max(0.05, min(position, max_position))
```

### 8.2 风险限制

```python
RISK_LIMITS = {
    "max_drawdown": 0.15,      # 最大回撤限制15%
    "max_single_position": 0.20, # 单只股票最大仓位20%
    "max_sector_concentration": 0.40,  # 行业最大仓位40%
    "min_daily_volume": 100000000,  # 日均成交额>1亿
    "max_positions": 20,         # 最多持仓数
}
```

### 8.3 止损机制

```python
STOP_LOSS_RULES = {
    "hard_stop": 0.08,          # 硬止损8%
    "trailing_stop": 0.05,      # 追踪止损5%
    "time_stop": 60,            # 时间止损60日
    "rebalance_threshold": 0.15, # 评分变化15%再平衡
}
```

---

## 九、版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v2.0 | 2026-04-12 | 三层回测结构(逻辑/跟踪/策略);稳健性优先优化;滚动回测;参数区间;复杂度惩罚;压力测试 |
| v1.0 | 2026-04-12 | 初始版本 |
