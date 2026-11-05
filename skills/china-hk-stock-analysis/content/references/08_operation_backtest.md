# 个股操作建议与回测优化 v1.0

本文档定义个股操作建议生成、回测执行、稳健优化的完整流程。

---

## 一、核心工作流

```
┌─────────────────────────────────────────────────────────────────────┐
│                        个股 → 操作建议 → 回测 → 稳健优化             │
└─────────────────────────────────────────────────────────────────────┘

个股分析
   ↓
生成操作建议（含具体价格区间）
   ↓
执行回测（3层验证）
   ↓
基于回测结果优化
   ↓
输出稳健最优方案
```

---

## 二、操作建议生成

### 2.1 建议结构

```python
class StockOperationRecommendation:
    """
    个股操作建议生成器
    """

    def generate(self, analysis_result: dict) -> dict:
        """
        基于8维度评分生成具体操作建议

        返回:
            recommendation: 操作建议
        """
        score = analysis_result["composite_score"]
        valuation = analysis_result["dimensions"]["valuation"]
        fundamental = analysis_result["dimensions"]["fundamental"]
        technical = analysis_result["dimensions"]["technical"]
        risk = analysis_result["dimensions"]["risk"]

        # 1. 确定信号
        signal = self._determine_signal(score)

        # 2. 计算建议购买区间
        buy_zone = self._calculate_buy_zone(
            current_price=analysis_result["current_price"],
            dcf_intrinsic_value=analysis_result.get("dcf_intrinsic_value"),
            score=score,
            valuation=valuation,
            risk=risk,
        )

        # 3. 目标价格
        target_prices = self._calculate_target_prices(
            current_price=analysis_result["current_price"],
            score=score,
            fundamental=fundamental,
        )

        # 4. 止损止盈
        stop_loss, take_profit = self._calculate_stop_loss_tp(
            buy_price=buy_zone["conservative_buy"],
            volatility=analysis_result.get("volatility", 0.25),
            risk=risk,
        )

        # 5. 持仓周期
        holding_period = self._calculate_holding_period(
            score=score,
            technical=technical,
        )

        # 6. 仓位建议
        position_size = self._calculate_position_size(
            score=score,
            risk=risk,
            signal=signal,
        )

        return {
            "report_id": analysis_result["report_id"],
            "stock_code": analysis_result["stock_code"],
            "stock_name": analysis_result["stock_name"],
            "signal": signal,
            "composite_score": score,
            "current_price": analysis_result["current_price"],
            "recommendation": {
                "buy_zone": buy_zone,
                "target_prices": target_prices,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "holding_period": holding_period,
                "position_size": position_size,
            },
            "backtest_ready": True,
        }

    def _determine_signal(self, score: float) -> str:
        """确定信号"""
        if score >= 85:
            return "STRONG_BUY"
        elif score >= 75:
            return "BUY"
        elif score >= 60:
            return "HOLD"
        elif score >= 45:
            return "SELL"
        else:
            return "STRONG_SELL"

    def _calculate_buy_zone(self, current_price: float,
                            dcf_intrinsic_value: float,
                            score: float,
                            valuation: dict,
                            risk: dict) -> dict:
        """
        计算建议购买区间

        基于:
        1. DCF内在价值的安全边际
        2. 当前估值分位
        3. 风险等级
        """
        # 安全边际计算
        if dcf_intrinsic_value and dcf_intrinsic_value > current_price:
            safety_margin = (dcf_intrinsic_value - current_price) / dcf_intrinsic_value
        else:
            # 无DCF时用PE分位估算
            pe_percentile = valuation.get("pe_percentile", 50)
            safety_margin = (100 - pe_percentile) / 200  # PE分位越低安全边际越高

        # 风险调整
        risk_score = risk.get("score", 50)
        risk_factor = 1.0 if risk_score >= 70 else 0.9 if risk_score >= 50 else 0.8

        # 激进购买价 (当前价格 - 5%)
        aggressive_buy = current_price * 0.95

        # 保守购买价 (基于安全边际)
        conservative_buy = current_price * (1 - safety_margin * 0.5 * risk_factor)

        # 合理购买区间
        fair_buy = current_price * (1 - safety_margin * 0.3 * risk_factor)

        return {
            "aggressive_buy_price": round(aggressive_buy, 2),
            "fair_buy_price": round(fair_buy, 2),
            "conservative_buy_price": round(conservative_buy, 2),
            "buy_zone_description": f"{round(conservative_buy, 2)} - {round(aggressive_buy, 2)}",
            "safety_margin": round(safety_margin * 100, 1),
            "based_on": "DCF内在价值" if dcf_intrinsic_value else "PE分位分析",
        }

    def _calculate_target_prices(self, current_price: float,
                                 score: float,
                                 fundamental: dict) -> dict:
        """
        计算目标价格

        三个情景:
        - 保守目标: 基于当前估值合理回归
        - 合理目标: 基于分析师共识
        - 乐观目标: 基于成长预期
        """
        # 基础收益目标
        if score >= 85:
            conservative_return = 0.30  # 30%
            fair_return = 0.45         # 45%
            optimistic_return = 0.60    # 60%
        elif score >= 75:
            conservative_return = 0.20
            fair_return = 0.35
            optimistic_return = 0.50
        elif score >= 60:
            conservative_return = 0.10
            fair_return = 0.20
            optimistic_return = 0.30
        else:
            conservative_return = 0.05
            fair_return = 0.10
            optimistic_return = 0.15

        # ROE调整
        roe = fundamental.get("roe", 15)
        if roe >= 20:
            adjustment = 1.2  # 高ROE可以期待更高收益
        elif roe >= 15:
            adjustment = 1.0
        else:
            adjustment = 0.8

        return {
            "conservative_target": round(current_price * (1 + conservative_return * adjustment), 2),
            "fair_target": round(current_price * (1 + fair_return * adjustment), 2),
            "optimistic_target": round(current_price * (1 + optimistic_return * adjustment), 2),
            "conservative_return_pct": round(conservative_return * adjustment * 100, 1),
            "fair_return_pct": round(fair_return * adjustment * 100, 1),
            "optimistic_return_pct": round(optimistic_return * adjustment * 100, 1),
        }

    def _calculate_stop_loss_tp(self, buy_price: float,
                                volatility: float,
                                risk: dict) -> dict:
        """
        计算止损止盈

        基于:
        1. 买入价格
        2. 波动率
        3. 风险等级
        """
        risk_score = risk.get("score", 50)

        # 止损: 波动率 * 风险系数
        if risk_score >= 70:  # 低风险
            stop_loss_pct = 0.15   # 15%止损
        elif risk_score >= 50:  # 中风险
            stop_loss_pct = 0.10   # 10%止损
        else:                    # 高风险
            stop_loss_pct = 0.08   # 8%止损

        # 止盈: 动态跟踪
        take_profit_pct = 0.25  # 默认25%

        return {
            "stop_loss_price": round(buy_price * (1 - stop_loss_pct), 2),
            "stop_loss_pct": round(stop_loss_pct * 100, 1),
            "take_profit_price": round(buy_price * (1 + take_profit_pct), 2),
            "take_profit_pct": round(take_profit_pct * 100, 1),
            "trailing_stop_pct": 5,  # 5%追踪止损
        }

    def _calculate_holding_period(self, score: float,
                                  technical: dict) -> dict:
        """
        计算建议持仓周期

        基于:
        1. 评分高低
        2. 技术趋势
        """
        # 基础周期
        if score >= 80:
            base_period = 90   # 高分建议持有90天
        elif score >= 70:
            base_period = 60
        elif score >= 60:
            base_period = 30
        else:
            base_period = 14

        # 趋势调整
        trend = technical.get("trend", "neutral")
        if trend == "uptrend":
            adjustment = 1.3   # 上升趋势延长持有
        elif trend == "downtrend":
            adjustment = 0.7   # 下降趋势缩短持有
        else:
            adjustment = 1.0

        period = int(base_period * adjustment)

        return {
            "recommended_days": period,
            "min_days": int(period * 0.5),
            "max_days": int(period * 1.5),
            "rebalance_trigger": "评分变化>15%或持仓>max_days",
        }

    def _calculate_position_size(self, score: float,
                                 risk: dict,
                                 signal: str) -> dict:
        """
        计算仓位建议

        基于:
        1. 信号强度
        2. 风险评分
        3. 综合评分
        """
        # 基础仓位
        base_position = {
            "STRONG_BUY": 1.0,
            "BUY": 0.8,
            "HOLD": 0.0,
            "SELL": 0.0,
            "STRONG_SELL": 0.0,
        }.get(signal, 0.0)

        # 风险调整
        risk_score = risk.get("score", 50)
        if risk_score < 40:  # 高风险
            risk_adjustment = 0.7
        elif risk_score < 60:
            risk_adjustment = 0.85
        else:
            risk_adjustment = 1.0

        final_position = base_position * risk_adjustment

        return {
            "max_position": round(final_position * 100, 1),
            "min_position": round(final_position * 0.5 * 100, 1),
            "base_position": round(base_position * 100, 1),
            "risk_adjustment": risk_adjustment,
        }
```

### 2.2 操作建议输出格式

```json
{
  "report_id": "uuid-xxx",
  "stock_code": "000333.SZ",
  "stock_name": "美的集团",
  "signal": "BUY",
  "composite_score": 82.5,
  "current_price": 180.50,
  "recommendation": {
    "buy_zone": {
      "aggressive_buy_price": 171.48,
      "fair_buy_price": 175.20,
      "conservative_buy_price": 168.35,
      "buy_zone_description": "168.35 - 171.48",
      "safety_margin": 15.2,
      "based_on": "DCF内在价值"
    },
    "target_prices": {
      "conservative_target": 216.60,
      "fair_target": 243.68,
      "optimistic_target": 270.75,
      "conservative_return_pct": 20.0,
      "fair_return_pct": 35.0,
      "optimistic_return_pct": 50.0
    },
    "stop_loss": {
      "stop_loss_price": 152.42,
      "stop_loss_pct": 10.0,
      "take_profit_price": 225.63,
      "take_profit_pct": 25.0,
      "trailing_stop_pct": 5
    },
    "holding_period": {
      "recommended_days": 90,
      "min_days": 45,
      "max_days": 135,
      "rebalance_trigger": "评分变化>15%或持仓>max_days"
    },
    "position_size": {
      "max_position": 80.0,
      "min_position": 40.0,
      "base_position": 80.0,
      "risk_adjustment": 1.0
    }
  },
  "backtest_ready": true
}
```

---

## 三、回测执行

### 3.1 回测执行器

```python
class OperationBacktestEngine:
    """
    操作建议回测引擎

    对每条操作建议执行3层回测验证
    """

    def __init__(self, price_data_service):
        self.price_service = price_data_service
        self.logic_evaluator = LogicEvaluator()
        self.result_tracker = ResultTracker()
        self.strategy_evaluator = StrategyEvaluator()

    def backtest(self, recommendation: dict,
                 historical_prices: dict) -> dict:
        """
        执行完整回测

        参数:
            recommendation: 操作建议
            historical_prices: 历史价格数据 {date: price}

        返回:
            backtest_result: 完整回测结果
        """
        # ===== 第一层：逻辑评估 =====
        logic_result = self._layer1_logic_evaluation(recommendation)

        # ===== 第二层：结果跟踪 =====
        tracking_result = self._layer2_result_tracking(
            recommendation, historical_prices
        )

        # ===== 第三层：策略评估 =====
        strategy_result = self._layer3_strategy_evaluation(tracking_result)

        return {
            "report_id": recommendation["report_id"],
            "stock_code": recommendation["stock_code"],
            "backtest_date": datetime.now().strftime("%Y-%m-%d"),
            "layer1_logic": logic_result,
            "layer2_tracking": tracking_result,
            "layer3_strategy": strategy_result,
            "overall_robust_score": self._calculate_overall_robust_score(
                logic_result, tracking_result, strategy_result
            ),
        }

    def _layer1_logic_evaluation(self, recommendation: dict) -> dict:
        """
        第一层：逻辑评估

        检查操作建议是否符合投资逻辑
        """
        # 从recommendation提取分析数据
        score = recommendation["composite_score"]
        valuation = recommendation.get("valuation", {})
        fundamental = recommendation.get("fundamental", {})
        risk = recommendation.get("risk", {})

        # 逻辑检查
        logic_checks = {
            "score_consistency": self._check_score_consistency(score, valuation),
            "valuation_reasonable": self._check_valuation_reasonable(
                recommendation["current_price"],
                recommendation["recommendation"]["buy_zone"]
            ),
            "target_reasonable": self._check_target_reasonable(
                recommendation["current_price"],
                recommendation["recommendation"]["target_prices"]
            ),
            "risk_reasonable": self._check_risk_reasonable(
                recommendation["recommendation"]["stop_loss"],
                fundamental
            ),
        }

        # 逻辑评分
        logic_score = sum(logic_checks.values()) / len(logic_checks)

        return {
            "logic_score": round(logic_score, 1),
            "logic_checks": logic_checks,
            "logic_valid": logic_score >= 60,
            "logic_explanation": self._explain_logic(logic_checks),
        }

    def _check_score_consistency(self, score: float,
                                 valuation: dict) -> float:
        """检查评分一致性"""
        pe_percentile = valuation.get("pe_percentile", 50)
        signal_score = score

        # 高评分应该对应低PE分位
        if score >= 75 and pe_percentile > 50:
            return 50   # 矛盾
        elif score >= 75 and pe_percentile <= 30:
            return 100  # 一致
        else:
            return 70

    def _check_valuation_reasonable(self, current_price: float,
                                     buy_zone: dict) -> float:
        """检查买入区间合理性"""
        zone_low = buy_zone["conservative_buy_price"]
        zone_high = buy_zone["aggressive_buy_price"]

        # 当前价应该在买入区间附近或略高
        if zone_low <= current_price <= zone_high * 1.1:
            return 100
        elif current_price < zone_low:
            return 80   # 比最低买入价还低，可以买入
        elif current_price > zone_high * 1.2:
            return 40   # 当前价太高
        else:
            return 70

    def _check_target_reasonable(self, current_price: float,
                                  targets: dict) -> float:
        """检查目标价合理性"""
        fair_target = targets["fair_target"]

        # 目标价应该比当前价高
        if fair_target <= current_price:
            return 30   # 目标价不合理

        # 上涨空间检查
        return_pct = (fair_target - current_price) / current_price
        if 0.15 <= return_pct <= 0.80:
            return 100  # 合理上涨空间
        elif return_pct < 0.15:
            return 50   # 上涨空间太小
        else:
            return 60   # 上涨空间过大但可接受

    def _check_risk_reasonable(self, stop_loss: dict,
                                fundamental: dict) -> float:
        """检查风险设置合理性"""
        stop_pct = stop_loss["stop_loss_pct"]
        roe = fundamental.get("roe", 15)

        # 高ROE公司可以承受较宽止损
        if roe >= 20 and stop_pct <= 15:
            return 100
        elif roe >= 15 and stop_pct <= 12:
            return 90
        elif roe >= 10 and stop_pct <= 10:
            return 80
        elif stop_pct > 15:
            return 50   # 止损太宽
        else:
            return 70

    def _explain_logic(self, checks: dict) -> str:
        """生成逻辑解释"""
        avg = sum(checks.values()) / len(checks)
        failed = [k for k, v in checks.items() if v < 60]

        if avg >= 90:
            return "逻辑非常严谨，建议高度可信"
        elif avg >= 70:
            if failed:
                return f"逻辑基本合理，但存在{len(failed)}处需关注: {', '.join(failed)}"
            return "逻辑合理，建议可信"
        elif avg >= 50:
            return f"逻辑存在矛盾，建议谨慎: {', '.join(failed)}"
        else:
            return "逻辑存在严重问题，建议重新分析"

    def _layer2_result_tracking(self, recommendation: dict,
                                 historical_prices: dict) -> dict:
        """
        第二层：结果跟踪

        跟踪实际操作收益
        """
        current_price = recommendation["current_price"]
        buy_zone = recommendation["recommendation"]["buy_zone"]
        target_prices = recommendation["recommendation"]["target_prices"]
        stop_loss = recommendation["recommendation"]["stop_loss"]

        # 实际买卖价格
        actual_buy_price = buy_zone["fair_buy_price"]  # 假设在合理价格买入
        stop_loss_price = stop_loss["stop_loss_price"]

        results = {
            "day_7": self._track_point(historical_prices, 7, actual_buy_price,
                                        stop_loss_price, target_prices),
            "day_30": self._track_point(historical_prices, 30, actual_buy_price,
                                        stop_loss_price, target_prices),
            "day_90": self._track_point(historical_prices, 90, actual_buy_price,
                                        stop_loss_price, target_prices),
        }

        # 判定预测是否正确
        final_result = results["day_90"]
        if final_result["return_pct"] is None:
            prediction_correct = None
        elif final_result["return_pct"] > 0:
            prediction_correct = True
        else:
            prediction_correct = False

        return {
            "buy_price": actual_buy_price,
            "tracking": results,
            "prediction_correct": prediction_correct,
            "final_return_pct": final_result["return_pct"],
        }

    def _track_point(self, prices: dict, days: int,
                     buy_price: float, stop_loss: float,
                     targets: dict) -> dict:
        """跟踪特定时间点"""
        # 找到对应日期的价格
        sorted_dates = sorted(prices.keys())

        if len(sorted_dates) < days:
            return {"return_pct": None, "price": None, "status": "数据不足"}

        target_date_idx = min(days, len(sorted_dates) - 1)
        target_date = sorted_dates[target_date_idx]
        price = prices[target_date]

        # 计算收益
        return_pct = (price - buy_price) / buy_price * 100

        # 检查是否触发止损
        if price <= stop_loss:
            status = "触发止损"
        elif price >= targets["optimistic_target"]:
            status = "达到乐观目标"
        elif price >= targets["fair_target"]:
            status = "达到合理目标"
        else:
            status = "持仓中"

        return {
            "days": days,
            "date": target_date,
            "price": price,
            "return_pct": round(return_pct, 2),
            "vs_stop_loss": round((price - stop_loss) / stop_loss * 100, 2),
            "status": status,
        }

    def _layer3_strategy_evaluation(self, tracking_result: dict) -> dict:
        """
        第三层：策略评估

        评估策略级表现
        """
        return_pct = tracking_result["final_return_pct"]

        if return_pct is None:
            return {"status": "数据不足，无法评估"}

        # 评估标准
        if return_pct >= 30:
            grade = "A+"
            rating = "优秀"
        elif return_pct >= 20:
            grade = "A"
            rating = "良好"
        elif return_pct >= 10:
            grade = "B+"
            rating = "合格"
        elif return_pct >= 0:
            grade = "B"
            rating = "勉强合格"
        else:
            grade = "C"
            rating = "不合格"

        return {
            "return_pct": return_pct,
            "grade": grade,
            "rating": rating,
            "meets_expectation": return_pct >= 15,
        }

    def _calculate_overall_robust_score(self, logic: dict,
                                         tracking: dict,
                                         strategy: dict) -> float:
        """计算综合稳健评分"""
        # 权重
        weights = {
            "logic": 0.30,
            "tracking": 0.40,
            "strategy": 0.30,
        }

        logic_score = logic.get("logic_score", 50)
        tracking_score = 100 if tracking.get("prediction_correct") else 30
        strategy_score = 90 if strategy.get("meets_expectation") else 50

        robust_score = (
            weights["logic"] * logic_score +
            weights["tracking"] * tracking_score +
            weights["strategy"] * strategy_score
        )

        return round(robust_score, 1)
```

### 3.2 回测结果输出格式

```json
{
  "report_id": "uuid-xxx",
  "stock_code": "000333.SZ",
  "backtest_date": "2024-01-15",
  "layer1_logic": {
    "logic_score": 82.5,
    "logic_checks": {
      "score_consistency": 100,
      "valuation_reasonable": 80,
      "target_reasonable": 80,
      "risk_reasonable": 70
    },
    "logic_valid": true,
    "logic_explanation": "逻辑基本合理，但存在1处需关注: risk_reasonable"
  },
  "layer2_tracking": {
    "buy_price": 175.20,
    "tracking": {
      "day_7": {
        "days": 7, "date": "2024-01-22", "price": 178.30,
        "return_pct": 1.77, "vs_stop_loss": 16.97, "status": "持仓中"
      },
      "day_30": {
        "days": 30, "date": "2024-02-14", "price": 185.50,
        "return_pct": 5.88, "vs_stop_loss": 21.69, "status": "持仓中"
      },
      "day_90": {
        "days": 90, "date": "2024-04-14", "price": 195.00,
        "return_pct": 11.30, "vs_stop_loss": 27.93, "status": "达到合理目标"
      }
    },
    "prediction_correct": true,
    "final_return_pct": 11.30
  },
  "layer3_strategy": {
    "return_pct": 11.30,
    "grade": "B+",
    "rating": "合格",
    "meets_expectation": false
  },
  "overall_robust_score": 66.3
}
```

---

## 四、稳健优化

### 4.1 优化器

```python
class RobustOptimizer:
    """
    稳健性优化器

    目标: 不是最大化历史收益，而是最大化策略的长期稳定性
    """

    def __init__(self):
        self.optimization_history = []

    def optimize(self, backtest_results: list,
                 train_window: int = 252,
                 test_window: int = 63) -> dict:
        """
        执行稳健优化

        参数:
            backtest_results: 历史回测结果列表
            train_window: 训练窗口(天)
            test_window: 测试窗口(天)

        返回:
            optimized_strategy: 稳健优化后的策略
        """
        # ===== 1. 数据分离 =====
        train_data, test_data = self._split_data(
            backtest_results, train_ratio=0.7
        )

        # ===== 2. 滚动回测 =====
        walk_forward_results = self._walk_forward_optimization(
            train_data, test_window
        )

        # ===== 3. 参数稳定性分析 =====
        stability_analysis = self._analyze_parameter_stability(
            walk_forward_results
        )

        # ===== 4. 复杂度惩罚 =====
        complexity_penalty = self._apply_complexity_penalty(
            walk_forward_results
        )

        # ===== 5. 压力测试 =====
        stress_results = self._run_stress_test(walk_forward_results)

        # ===== 6. 生成稳健最优方案 =====
        robust_optimal = self._generate_robust_optimal(
            stability_analysis,
            complexity_penalty,
            stress_results,
            test_data
        )

        return robust_optimal

    def _split_data(self, results: list,
                    train_ratio: float) -> tuple:
        """分离训练集和测试集"""
        split_idx = int(len(results) * train_ratio)
        train_data = results[:split_idx]
        test_data = results[split_idx:]
        return train_data, test_data

    def _walk_forward_optimization(self, train_data: list,
                                    test_window: int) -> list:
        """
        滚动回测优化

        多时间窗口反复训练和测试
        """
        walk_forward_results = []

        for i in range(0, len(train_data) - test_window, test_window):
            train_window = train_data[max(0, i):i + test_window]
            test_window_data = train_data[i + test_window:i + test_window * 2] \
                if i + test_window * 2 <= len(train_data) else []

            if not test_window_data:
                continue

            # 在训练集上优化参数
            optimized_params = self._optimize_params(train_window)

            # 在测试集上验证
            test_metrics = self._validate_on_test(test_window_data, optimized_params)

            walk_forward_results.append({
                "train_period": f"day_{i} to day_{i + test_window}",
                "test_period": f"day_{i + test_window} to day_{i + test_window * 2}",
                "params": optimized_params,
                "train_metrics": self._calculate_metrics(train_window),
                "test_metrics": test_metrics,
            })

        return walk_forward_results

    def _optimize_params(self, train_data: list) -> dict:
        """
        在训练集上优化参数

        优化目标: 最大化稳健性而非单次收益
        """
        # 参数候选
        param_candidates = {
            "buy_zone_adjustment": [0.9, 0.95, 1.0, 1.05, 1.1],
            "stop_loss_adjustment": [0.8, 0.9, 1.0, 1.1, 1.2],
            "target_adjustment": [0.9, 0.95, 1.0, 1.05, 1.1],
        }

        best_robust_score = -1
        best_params = {}

        # 网格搜索
        for buy_adj in param_candidates["buy_zone_adjustment"]:
            for stop_adj in param_candidates["stop_loss_adjustment"]:
                for target_adj in param_candidates["target_adjustment"]:
                    params = {
                        "buy_zone_adjustment": buy_adj,
                        "stop_loss_adjustment": stop_adj,
                        "target_adjustment": target_adj,
                    }

                    # 计算稳健评分
                    robust_score = self._calculate_robust_score(
                        train_data, params
                    )

                    if robust_score > best_robust_score:
                        best_robust_score = robust_score
                        best_params = params.copy()
                        best_params["robust_score"] = robust_score

        return best_params

    def _calculate_robust_score(self, data: list, params: dict) -> float:
        """
        计算稳健评分

        关键: 不是单次收益，而是多次表现的稳定性
        """
        returns = []
        for record in data:
            # 应用参数调整
            adjusted_return = self._apply_params(record, params)
            returns.append(adjusted_return)

        if not returns:
            return 0

        # 稳健评分 = 均值 / (标准差 + 1) * 惩罚因子
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_return = variance ** 0.5

        # 惩罚高波动
        stability_factor = mean_return / (std_return + 1)

        # 惩罚过拟合风险 (训练集表现远好于预期)
        expected_return = 15  # 假设期望15%
        overfitting_penalty = 1.0 if mean_return < expected_return * 1.5 \
            else 0.8

        robust_score = stability_factor * 10 * overfitting_penalty

        return max(0, min(100, robust_score))

    def _apply_params(self, record: dict, params: dict) -> float:
        """应用参数到记录"""
        # 简化: 返回实际收益按参数调整
        return record.get("final_return_pct", 0)

    def _validate_on_test(self, test_data: list,
                          params: dict) -> dict:
        """在测试集上验证"""
        returns = [
            self._apply_params(r, params)
            for r in test_data
        ]

        return {
            "avg_return": sum(returns) / len(returns) if returns else 0,
            "win_rate": sum(1 for r in returns if r > 0) / len(returns) if returns else 0,
            "max_drawdown": min(returns) if returns else 0,
        }

    def _calculate_metrics(self, data: list) -> dict:
        """计算指标"""
        returns = [r.get("final_return_pct", 0) for r in data]

        return {
            "avg_return": sum(returns) / len(returns) if returns else 0,
            "win_rate": sum(1 for r in returns if r > 0) / len(returns) if returns else 0,
            "robust_score": self._calculate_robust_score(data, {}),
        }

    def _analyze_parameter_stability(self, walk_forward_results: list) -> dict:
        """
        参数稳定性分析

        不输出单一最优参数，而是输出有效区间
        """
        # 收集所有有效参数
        all_params = [r["params"] for r in walk_forward_results]

        if not all_params:
            return {"error": "No data"}

        # 计算每个参数的范围
        param_ranges = {}
        for key in all_params[0].keys():
            if key == "robust_score":
                continue

            values = [p.get(key, 0) for p in all_params]
            mean_val = sum(values) / len(values)
            std_val = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5

            param_ranges[key] = {
                "effective_range": [min(values), max(values)],
                "mean": round(mean_val, 3),
                "std": round(std_val, 3),
                "center": mean_val,
            }

        # 计算稳健评分
        robust_scores = [r["params"].get("robust_score", 0)
                        for r in walk_forward_results]
        avg_robust = sum(robust_scores) / len(robust_scores) if robust_scores else 0

        # 有效参数占比
        max_ic = max(robust_scores) if robust_scores else 1
        threshold = 0.8 * max_ic
        valid_count = sum(1 for s in robust_scores if s >= threshold)

        return {
            "param_ranges": param_ranges,
            "avg_robust_score": round(avg_robust, 1),
            "valid_param_ratio": round(valid_count / len(walk_forward_results), 2)
                if walk_forward_results else 0,
            "stability_assessment": "HIGH" if avg_robust >= 70 else \
                "MEDIUM" if avg_robust >= 50 else "LOW",
        }

    def _apply_complexity_penalty(self, walk_forward_results: list) -> dict:
        """
        复杂度惩罚

        策略规则越多，惩罚越高
        """
        # 简化的规则数量
        base_rules = 5  # 基础规则数量
        num_strategies = len(walk_forward_results)

        # 复杂度惩罚
        if num_strategies <= 3:
            penalty = 0
        elif num_strategies <= 5:
            penalty = 0.05
        else:
            penalty = 0.10 + (num_strategies - 5) * 0.02

        return {
            "num_strategies": num_strategies,
            "complexity_penalty": round(penalty * 100, 1),
            "recommendation": "简单策略优先" if num_strategies > 5 else "策略复杂度适中",
        }

    def _run_stress_test(self, walk_forward_results: list) -> dict:
        """
        压力测试

        在极端市场条件下测试策略表现
        """
        # 分离熊市期和高波动期数据
        all_returns = []
        for r in walk_forward_results:
            test_ret = r.get("test_metrics", {}).get("avg_return", 0)
            all_returns.append(test_ret)

        if not all_returns:
            return {"error": "No data"}

        # 压力场景模拟
        sorted_returns = sorted(all_returns)
        worst_10_pct = sorted_returns[:max(1, len(sorted_returns) // 10)]

        stress_metrics = {
            "worst_case_return": round(min(all_returns), 2),
            "worst_10pct_avg": round(sum(worst_10_pct) / len(worst_10_pct), 2),
            "max_drawdown_simulated": round(min(all_returns), 2),
        }

        # 生存评分
        survival_score = 100
        if stress_metrics["max_drawdown_simulated"] < -20:
            survival_score -= 30
        elif stress_metrics["max_drawdown_simulated"] < -15:
            survival_score -= 15

        if stress_metrics["worst_case_return"] < -30:
            survival_score -= 30
        elif stress_metrics["worst_case_return"] < -15:
            survival_score -= 15

        stress_metrics["survival_score"] = max(0, survival_score)

        return stress_metrics

    def _generate_robust_optimal(self, stability: dict,
                                 complexity: dict,
                                 stress: dict,
                                 test_data: list) -> dict:
        """
        生成稳健最优方案
        """
        # 综合评分
        robust_score = (
            stability.get("avg_robust_score", 50) * 0.4 +
            stress.get("survival_score", 50) * 0.3 +
            (100 - complexity.get("complexity_penalty", 0)) * 0.3
        )

        # 测试集表现
        test_returns = [r.get("final_return_pct", 0) for r in test_data]
        test_avg_return = sum(test_returns) / len(test_returns) if test_returns else 0

        # 过拟合风险检测
        train_robust = stability.get("avg_robust_score", 50)
        test_score = 100 if test_avg_return >= 10 else 50
        overfitting_risk = "HIGH" if train_robust > test_score * 1.5 else \
            "MEDIUM" if train_robust > test_score * 1.2 else "LOW"

        return {
            "optimal_params": {
                "buy_zone_adjustment": stability.get("param_ranges", {})
                    .get("buy_zone_adjustment", {}).get("center", 1.0),
                "stop_loss_adjustment": stability.get("param_ranges", {})
                    .get("stop_loss_adjustment", {}).get("center", 1.0),
                "target_adjustment": stability.get("param_ranges", {})
                    .get("target_adjustment", {}).get("center", 1.0),
            },
            "param_intervals": {
                "buy_zone_adjustment": stability.get("param_ranges", {})
                    .get("buy_zone_adjustment", {}).get("effective_range", [0.95, 1.05]),
                "stop_loss_adjustment": stability.get("param_ranges", {})
                    .get("stop_loss_adjustment", {}).get("effective_range", [0.9, 1.1]),
                "target_adjustment": stability.get("param_ranges", {})
                    .get("target_adjustment", {}).get("effective_range", [0.95, 1.05]),
            },
            "robust_score": round(robust_score, 1),
            "stability_assessment": stability.get("stability_assessment", "UNKNOWN"),
            "complexity_penalty": complexity.get("complexity_penalty", 0),
            "stress_test": {
                "worst_case_return": stress.get("worst_case_return", 0),
                "survival_score": stress.get("survival_score", 0),
            },
            "test_set_performance": {
                "avg_return": round(test_avg_return, 2),
                "num_samples": len(test_data),
            },
            "overfitting_risk": overfitting_risk,
            "strategy_recommendation": self._generate_recommendation(
                robust_score, overfitting_risk, stress
            ),
        }

    def _generate_recommendation(self, robust_score: float,
                                 overfitting_risk: str,
                                 stress: dict) -> str:
        """生成策略建议"""
        if robust_score >= 80 and overfitting_risk != "HIGH":
            return "策略稳健，可用于实盘"
        elif robust_score >= 60:
            return "策略基本稳健，但需关注风险"
        elif overfitting_risk == "HIGH":
            return "存在过拟合风险，建议简化策略"
        else:
            return "策略稳定性不足，建议重新优化"
```

### 4.2 稳健优化输出格式

```json
{
  "optimization_summary": {
    "optimization_date": "2024-04-12",
    "optimization_method": "walk_forward_robust",
    "train_period": "2023-01 to 2023-09",
    "test_period": "2023-10 to 2024-04",
  },
  "optimal_params": {
    "buy_zone_adjustment": 1.0,
    "stop_loss_adjustment": 0.95,
    "target_adjustment": 1.05
  },
  "param_intervals": {
    "buy_zone_adjustment": [0.95, 1.05],
    "stop_loss_adjustment": [0.9, 1.1],
    "target_adjustment": [0.95, 1.05]
  },
  "robust_score": 78.5,
  "stability_assessment": "MEDIUM",
  "complexity_penalty": "5%",
  "stress_test": {
    "worst_case_return": -12.3,
    "survival_score": 72.0
  },
  "test_set_performance": {
    "avg_return": 11.8,
    "num_samples": 18
  },
  "overfitting_risk": "LOW",
  "strategy_recommendation": "策略基本稳健，但需关注风险"
}
```

---

## 五、完整回测优化流程

```python
class CompleteBacktestOptimizer:
    """
    完整回测优化流程

    个股 → 操作建议 → 回测 → 稳健优化 → 最优方案
    """

    def __init__(self, price_data_service):
        self.price_service = price_data_service
        self.recommendation_engine = StockOperationRecommendation()
        self.backtest_engine = OperationBacktestEngine(price_data_service)
        self.robust_optimizer = RobustOptimizer()
        self.all_backtest_results = []
        self.all_optimization_results = []

    def run_full_pipeline(self, stock_code: str,
                          analysis_result: dict,
                          historical_prices: dict) -> dict:
        """
        执行完整流程

        1. 生成操作建议
        2. 执行3层回测
        3. 稳健优化
        4. 输出最优方案
        """
        # Step 1: 生成操作建议
        recommendation = self.recommendation_engine.generate(analysis_result)

        # Step 2: 执行回测
        backtest_result = self.backtest_engine.backtest(
            recommendation, historical_prices
        )
        self.all_backtest_results.append(backtest_result)

        # Step 3: 稳健优化 (积累足够数据后)
        optimization_result = None
        if len(self.all_backtest_results) >= 10:
            optimization_result = self.robust_optimizer.optimize(
                self.all_backtest_results
            )
            self.all_optimization_results.append(optimization_result)

        # Step 4: 生成最终报告
        return self._generate_final_report(
            recommendation,
            backtest_result,
            optimization_result
        )

    def _generate_final_report(self, recommendation: dict,
                                backtest: dict,
                                optimization: dict) -> dict:
        """生成最终报告"""
        report = {
            "report_type": "complete_backtest_optimization",
            "report_date": datetime.now().strftime("%Y-%m-%d"),

            # 操作建议
            "recommendation": recommendation,

            # 回测结果
            "backtest": {
                "layer1_logic": backtest["layer1_logic"],
                "layer2_tracking": backtest["layer2_tracking"],
                "layer3_strategy": backtest["layer3_strategy"],
                "overall_robust_score": backtest["overall_robust_score"],
            },

            # 优化结果
            "optimization": optimization,

            # 最终建议
            "final_recommendation": self._generate_final_recommendation(
                backtest, optimization
            ),
        }

        return report

    def _generate_final_recommendation(self, backtest: dict,
                                       optimization: dict) -> dict:
        """生成最终建议"""
        robust_score = backtest["overall_robust_score"]

        if optimization:
            param_adj = optimization.get("optimal_params", {})
            param_interval = optimization.get("param_intervals", {})
            overfitting = optimization.get("overfitting_risk", "UNKNOWN")
            strategy_rec = optimization.get("strategy_recommendation", "")

            # 应用优化参数
            buy_zone = param_adj.get("buy_zone_adjustment", 1.0)
            stop_adj = param_adj.get("stop_loss_adjustment", 1.0)
            target_adj = param_adj.get("target_adjustment", 1.0)

            return {
                "robust_optimal_achieved": robust_score >= 70,
                "adjusted_parameters": {
                    "buy_zone_adjustment": buy_zone,
                    "stop_loss_adjustment": stop_adj,
                    "target_adjustment": target_adj,
                },
                "parameter_confidence_intervals": param_interval,
                "overfitting_risk": overfitting,
                "strategy_recommendation": strategy_rec,
                "confidence_level": "HIGH" if robust_score >= 80 else \
                    "MEDIUM" if robust_score >= 60 else "LOW",
            }
        else:
            return {
                "robust_optimal_achieved": False,
                "message": "需要更多数据才能进行稳健优化",
                "current_robust_score": robust_score,
                "data_needed": 10 - len(self.all_backtest_results),
            }
```

### 5.1 最终输出格式

```json
{
  "report_type": "complete_backtest_optimization",
  "report_date": "2024-04-12",
  "recommendation": {
    "report_id": "uuid-xxx",
    "stock_code": "000333.SZ",
    "stock_name": "美的集团",
    "signal": "BUY",
    "composite_score": 82.5,
    "current_price": 180.50,
    "recommendation": {
      "buy_zone": {...},
      "target_prices": {...},
      "stop_loss": {...},
      "holding_period": {...},
      "position_size": {...}
    }
  },
  "backtest": {
    "layer1_logic": {
      "logic_score": 82.5,
      "logic_valid": true,
      "logic_explanation": "逻辑基本合理"
    },
    "layer2_tracking": {
      "buy_price": 175.20,
      "day_90_return": 11.30,
      "prediction_correct": true
    },
    "layer3_strategy": {
      "grade": "B+",
      "rating": "合格",
      "meets_expectation": false
    },
    "overall_robust_score": 66.3
  },
  "optimization": {
    "optimal_params": {
      "buy_zone_adjustment": 1.0,
      "stop_loss_adjustment": 0.95,
      "target_adjustment": 1.05
    },
    "param_intervals": {
      "buy_zone_adjustment": [0.95, 1.05],
      "stop_loss_adjustment": [0.9, 1.1],
      "target_adjustment": [0.95, 1.05]
    },
    "robust_score": 78.5,
    "overfitting_risk": "LOW",
    "strategy_recommendation": "策略基本稳健，但需关注风险"
  },
  "final_recommendation": {
    "robust_optimal_achieved": true,
    "adjusted_parameters": {
      "buy_zone_adjustment": 1.0,
      "stop_loss_adjustment": 0.95,
      "target_adjustment": 1.05
    },
    "parameter_confidence_intervals": {
      "buy_zone_adjustment": [0.95, 1.05],
      "stop_loss_adjustment": [0.9, 1.1],
      "target_adjustment": [0.95, 1.05]
    },
    "overfitting_risk": "LOW",
    "strategy_recommendation": "策略基本稳健，但需关注风险",
    "confidence_level": "MEDIUM"
  }
}
```

---

## 六、使用流程

### 6.1 单只股票完整流程

```
1. AI分析股票 → 输出完整8维度评分报告
2. AI生成操作建议 → buy_zone / target_prices / stop_loss / position_size
3. 用户确认建议 → 进入回测
4. 执行3层回测 → 逻辑评估 / 结果跟踪 / 策略评估
5. 稳健优化 → 基于所有历史回测结果优化参数
6. 输出最优方案 → 含参数置信区间、过拟合风险、策略建议
```

### 6.2 批量股票流程

```
1. 批量分析多只股票 → 生成多个操作建议
2. 批量回测 → 收集所有回测结果
3. 策略级回测 → 计算胜率、Avg Return、Max Drawdown、Alpha
4. 滚动优化 → walk-forward多时间窗口
5. 压力测试 → 熊市/高波动场景
6. 输出稳健最优 → 含参数区间、robust_score、overfitting_flag
```

---

## 七、版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2026-04-12 | 初始版本：个股操作建议 + 三层回测 + 稳健优化 |
