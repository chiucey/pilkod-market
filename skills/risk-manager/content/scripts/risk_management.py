#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险管理模块 - 风险评估、策略回测、组合优化、价格预测
"""

import json
import math
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Union
from collections import defaultdict

# 导入数据获取模块
import sys
import os

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, os.path.join(SKILLS_ROOT, 'market-data-fetcher', 'scripts'))
sys.path.insert(0, os.path.join(SKILLS_ROOT, 'stock-analyzer', 'scripts'))

from market_data import get_kline_data, get_realtime_quotes
from technical_analysis import TechnicalIndicators


class RiskAssessor:
    """风险评估器"""

    @staticmethod
    def calculate_returns(prices: List[float]) -> List[float]:
        """计算收益率序列"""
        returns = []
        for i in range(1, len(prices)):
            if prices[i - 1] > 0:
                ret = (prices[i] - prices[i - 1]) / prices[i - 1]
                returns.append(ret)
        return returns

    @staticmethod
    def calculate_volatility(returns: List[float], annualize: bool = True) -> float:
        """计算波动率"""
        if len(returns) < 2:
            return 0

        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)

        vol = math.sqrt(variance)

        if annualize:
            vol *= math.sqrt(252)  # 年化

        return round(vol, 4)

    @staticmethod
    def calculate_var(returns: List[float], confidence: float = 0.95) -> float:
        """计算风险价值 (VaR)"""
        if not returns:
            return 0

        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        index = min(index, len(sorted_returns) - 1)

        return round(sorted_returns[index], 4)

    @staticmethod
    def calculate_cvar(returns: List[float], confidence: float = 0.95) -> float:
        """计算条件风险价值 (CVaR)"""
        if not returns:
            return 0

        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        index = min(index, len(sorted_returns) - 1)

        # CVaR是VaR及更差情况下的平均损失
        tail_returns = sorted_returns[:index + 1]
        cvar = sum(tail_returns) / len(tail_returns) if tail_returns else 0

        return round(cvar, 4)

    @staticmethod
    @staticmethod
    def calculate_max_drawdown(prices_or_returns: List[float],
                                is_prices: bool = True) -> float:
        """
        计算最大回撤

        Args:
            prices_or_returns: 价格列表(is_prices=True)或收益率列表(is_prices=False)
            is_prices: True=输入为价格序列，False=输入为收益率序列

        Returns:
            最大回撤值（负数），如 -0.15 表示回撤15%
        """
        if not prices_or_returns:
            return 0.0

        if is_prices:
            # 输入为价格序列（标准用法）
            prices = prices_or_returns
            peak = prices[0]
            max_dd = 0.0
            for price in prices:
                if price > peak:
                    peak = price
                dd = (price - peak) / peak if peak > 0 else 0
                if dd < max_dd:
                    max_dd = dd
            return round(max_dd, 4)
        else:
            # 输入为收益率序列 → 转换为价格后计算
            cumulative = [1.0]
            for r in prices_or_returns:
                cumulative.append(cumulative[-1] * (1 + r))
            prices = cumulative[1:]  # 去掉初始的1.0
            peak = prices[0]
            max_dd = 0.0
            for price in prices:
                if price > peak:
                    peak = price
                dd = (price - peak) / peak if peak > 0 else 0
                if dd < max_dd:
                    max_dd = dd
            return round(max_dd, 4)

    @staticmethod
    def calculate_returns_drawdown(returns: List[float]) -> float:
        """
        从收益率序列计算最大回撤（便捷方法）

        Args:
            returns: 每日收益率列表，如 [0.01, -0.02, 0.015]

        Returns:
            最大回撤值（负数）
        """
        return RiskAssessor.calculate_max_drawdown(returns, is_prices=False)

    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.03) -> float:
        """计算夏普比率"""
        if len(returns) < 2:
            return 0

        mean_return = sum(returns) / len(returns)
        volatility = RiskAssessor.calculate_volatility(returns, annualize=True)

        if volatility == 0:
            return 0

        # 年化夏普比率
        sharpe = (mean_return * 252 - risk_free_rate) / (volatility)

        return round(sharpe, 2)

    @staticmethod
    def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.03,
                                target_return: float = 0) -> float:
        """计算索提诺比率"""
        if len(returns) < 2:
            return 0

        mean_return = sum(returns) / len(returns)

        # 下行波动率
        downside_returns = [r for r in returns if r < target_return]
        if not downside_returns:
            return 0

        downside_std = math.sqrt(sum(r ** 2 for r in downside_returns) / len(downside_returns))
        downside_std *= math.sqrt(252)  # 年化

        if downside_std == 0:
            return 0

        sortino = (mean_return * 252 - risk_free_rate) / downside_std

        return round(sortino, 2)

    @staticmethod
    def calculate_beta(stock_returns: List[float], market_returns: List[float]) -> float:
        """计算Beta"""
        if len(stock_returns) != len(market_returns) or len(stock_returns) < 2:
            return 1.0

        # 计算协方差和市场方差
        mean_stock = sum(stock_returns) / len(stock_returns)
        mean_market = sum(market_returns) / len(market_returns)

        covariance = sum((s - mean_stock) * (m - mean_market)
                        for s, m in zip(stock_returns, market_returns)) / (len(stock_returns) - 1)

        market_variance = sum((m - mean_market) ** 2 for m in market_returns) / (len(market_returns) - 1)

        if market_variance == 0:
            return 1.0

        beta = covariance / market_variance

        return round(beta, 2)


class PortfolioOptimizer:
    """组合优化器"""

    @staticmethod
    def equal_weight(symbols: List[str], prices: Dict[str, float]) -> Dict[str, float]:
        """等权重分配"""
        if not symbols:
            return {}

        weight = 1.0 / len(symbols)

        return {symbol: round(weight, 4) for symbol in symbols}

    @staticmethod
    def risk_parity(symbols: List[str], volatilities: Dict[str, float]) -> Dict[str, float]:
        """风险平价组合"""
        if not symbols:
            return {}

        # 计算波动率倒数
        inv_vols = {}
        total_inv_vol = 0

        for symbol in symbols:
            vol = volatilities.get(symbol, 0.2)
            if vol > 0:
                inv_vols[symbol] = 1.0 / vol
                total_inv_vol += inv_vols[symbol]

        if total_inv_vol == 0:
            return PortfolioOptimizer.equal_weight(symbols, {})

        # 归一化
        weights = {}
        for symbol in symbols:
            weights[symbol] = round(inv_vols[symbol] / total_inv_vol, 4)

        return weights

    @staticmethod
    def mean_variance_optimize(
        symbols: List[str],
        expected_returns: Dict[str, float],
        volatilities: Dict[str, float],
        correlations: Dict[Tuple[str, str], float],
        risk_aversion: float = 1.0
    ) -> Dict[str, float]:
        """均值-方差优化 (简化版)"""
        if not symbols:
            return {}

        n = len(symbols)

        # 如果只有一只股票
        if n == 1:
            return {symbols[0]: 1.0}

        # 简化：使用波动率倒数和预期收益加权
        scores = {}
        total_score = 0

        for symbol in symbols:
            vol = volatilities.get(symbol, 0.2)
            ret = expected_returns.get(symbol, 0.1)

            if vol > 0:
                # 综合评分：预期收益高、波动率低的股票权重高
                score = ret / vol
                scores[symbol] = score
                total_score += score

        if total_score == 0:
            return PortfolioOptimizer.equal_weight(symbols, {})

        weights = {}
        for symbol in symbols:
            weights[symbol] = round(scores[symbol] / total_score, 4)

        return weights


class StrategyBacktester:
    """策略回测器"""

    def __init__(self, initial_capital: float = 1000000, commission: float = 0.0003):
        self.initial_capital = initial_capital
        self.commission = commission
        self.trades = []
        self.equity_curve = []

    def backtest_ma_cross(self, prices: List[float], dates: List[str],
                          fast_period: int = 5, slow_period: int = 20) -> Dict:
        """
        均线交叉策略回测

        Args:
            prices: 价格列表
            dates: 日期列表
            fast_period: 快线周期
            slow_period: 慢线周期

        Returns:
            回测结果
        """
        if len(prices) < slow_period:
            return {"error": "数据不足"}

        # 计算均线
        ma_fast = TechnicalIndicators.calculate_ma(prices, fast_period)
        ma_slow = TechnicalIndicators.calculate_ma(prices, slow_period)

        capital = self.initial_capital
        position = 0  # 持仓数量
        cash = capital
        equity = capital
        trades = []
        equity_history = []

        prev_fast_above = None

        for i in range(slow_period, len(prices)):
            current_price = prices[i]
            fast = ma_fast[i]
            slow = ma_slow[i]

            if fast is None or slow is None:
                continue

            # 金叉买入
            if prev_fast_above == False and fast > slow:
                # 买入
                shares = int(cash / (current_price * (1 + self.commission)))
                if shares > 0:
                    cost = shares * current_price * (1 + self.commission)
                    trades.append({
                        "type": "buy",
                        "date": dates[i] if i < len(dates) else None,
                        "price": current_price,
                        "shares": shares,
                        "cost": cost
                    })
                    cash -= cost
                    position += shares

            # 死叉卖出
            elif prev_fast_above == True and fast < slow:
                # 卖出
                if position > 0:
                    revenue = position * current_price * (1 - self.commission)
                    trades.append({
                        "type": "sell",
                        "date": dates[i] if i < len(dates) else None,
                        "price": current_price,
                        "shares": position,
                        "revenue": revenue
                    })
                    cash += revenue
                    position = 0

            prev_fast_above = fast > slow

            # 更新权益
            equity = cash + position * current_price
            equity_history.append({
                "date": dates[i] if i < len(dates) else None,
                "equity": round(equity, 2)
            })

        # 平仓
        if position > 0:
            final_price = prices[-1]
            revenue = position * final_price * (1 - self.commission)
            trades.append({
                "type": "sell",
                "date": dates[-1] if dates else None,
                "price": final_price,
                "shares": position,
                "revenue": revenue
            })
            cash += revenue
            position = 0
            equity = cash

        # 计算绩效
        total_return = (equity - self.initial_capital) / self.initial_capital

        # 计算收益率序列
        returns = []
        for i in range(1, len(equity_history)):
            ret = (equity_history[i]["equity"] - equity_history[i-1]["equity"]) / equity_history[i-1]["equity"]
            returns.append(ret)

        sharpe = RiskAssessor.calculate_sharpe_ratio(returns) if returns else 0
        max_dd, _, _ = RiskAssessor.calculate_max_drawdown([e["equity"] for e in equity_history])

        # 统计交易
        buy_trades = [t for t in trades if t["type"] == "buy"]
        sell_trades = [t for t in trades if t["type"] == "sell"]

        win_trades = 0
        total_profit = 0
        for i, buy in enumerate(buy_trades):
            if i < len(sell_trades):
                profit = sell_trades[i]["revenue"] - buy["cost"]
                total_profit += profit
                if profit > 0:
                    win_trades += 1

        win_rate = win_trades / len(buy_trades) if buy_trades else 0

        return {
            "total_return": round(total_return * 100, 2),
            "final_equity": round(equity, 2),
            "sharpe_ratio": sharpe,
            "max_drawdown": round(max_dd * 100, 2),
            "total_trades": len(trades),
            "win_rate": round(win_rate * 100, 2),
            "trades": trades,
            "equity_curve": equity_history
        }


class PriceForecaster:
    """价格预测器"""

    @staticmethod
    def simple_moving_average_forecast(prices: List[float], horizon: int = 5) -> List[float]:
        """简单移动平均预测"""
        if not prices:
            return []

        ma = sum(prices[-20:]) / min(20, len(prices))  # 20日均线

        # 预测未来N天
        last_price = prices[-1]
        trend = (prices[-1] - prices[-20]) / 19 if len(prices) >= 20 else 0

        forecasts = []
        for i in range(1, horizon + 1):
            # 假设价格逐渐向均线回归
            forecast = last_price + trend * i * 0.5 + (ma - last_price) * (i / horizon) * 0.3
            forecasts.append(round(forecast, 2))

        return forecasts

    @staticmethod
    def linear_trend_forecast(prices: List[float], horizon: int = 5) -> Dict:
        """线性趋势预测"""
        if len(prices) < 10:
            return {"error": "数据不足"}

        n = len(prices)
        x = list(range(n))
        y = prices

        # 线性回归: y = a * x + b
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n

        # 预测
        forecasts = []
        for i in range(n, n + horizon):
            forecast = slope * i + intercept
            forecasts.append(round(forecast, 2))

        # 趋势判断
        direction = "up" if slope > 0 else "down"
        confidence = min(abs(slope) / prices[-1] * 100, 100) if prices[-1] > 0 else 50

        return {
            "forecasts": forecasts,
            "direction": direction,
            "confidence": round(confidence, 2),
            "trend_slope": round(slope, 4)
        }

    @staticmethod
    def momentum_forecast(prices: List[float], horizon: int = 5) -> Dict:
        """动量预测"""
        if len(prices) < 20:
            return {"error": "数据不足"}

        # 计算近期动量
        recent_return = (prices[-1] - prices[-20]) / prices[-20] if prices[-20] > 0 else 0

        # 假设动量持续但衰减
        decay = 0.9  # 每月衰减90%

        forecasts = []
        for i in range(1, horizon + 1):
            # 预测价格
            forecast = prices[-1] * (1 + recent_return * (decay ** i))
            forecasts.append(round(forecast, 2))

        direction = "up" if recent_return > 0 else "down"
        confidence = min(abs(recent_return) * 10 * 100, 95)

        return {
            "forecasts": forecasts,
            "direction": direction,
            "confidence": round(confidence, 2),
            "momentum": round(recent_return * 100, 2)
        }


# ========== 对外API函数 ==========

def assess_risk(symbols: List[str], metrics: List[str] = None,
               confidence: float = 0.95, lookback_days: int = 252) -> Dict:
    """
    风险评估

    Args:
        symbols: 股票代码列表
        metrics: 风险指标列表
        confidence: 置信度
        lookback_days: 回溯天数

    Returns:
        风险评估结果
    """
    if metrics is None:
        metrics = ["var", "cvar", "beta", "volatility", "sharpe", "max_drawdown"]

    result = {
        "code": 0,
        "message": "success",
        "data": {
            "individual": {},
            "portfolio": {}
        },
        "timestamp": datetime.now().isoformat()
    }

    all_returns = []

    # 计算回溯的开始日期
    start_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    for symbol in symbols:
        # 获取K线数据
        kline = get_kline_data(symbol, "daily", start_date=start_date)
        if kline["code"] != 0 or not kline["data"].get("close"):
            result["data"]["individual"][symbol] = {"error": "数据获取失败"}
            continue

        closes = kline["data"]["close"]
        returns = RiskAssessor.calculate_returns(closes)

        if len(returns) < 10:
            result["data"]["individual"][symbol] = {"error": "数据不足"}
            continue

        all_returns.extend(returns)

        # 计算各项指标
        metrics_data = {}

        if "volatility" in metrics:
            metrics_data["volatility"] = RiskAssessor.calculate_volatility(returns)

        if "var" in metrics:
            metrics_data["var_95"] = RiskAssessor.calculate_var(returns, confidence)

        if "cvar" in metrics:
            metrics_data["cvar_95"] = RiskAssessor.calculate_cvar(returns, confidence)

        if "max_drawdown" in metrics:
            max_dd, _, _ = RiskAssessor.calculate_max_drawdown(closes)
            metrics_data["max_drawdown"] = max_dd

        if "sharpe" in metrics:
            metrics_data["sharpe_ratio"] = RiskAssessor.calculate_sharpe_ratio(returns)

        result["data"]["individual"][symbol] = metrics_data

    # 计算组合风险
    if all_returns and len(symbols) > 1:
        portfolio_returns = []
        for i in range(len(all_returns) // len(symbols)):
            period_returns = all_returns[i::len(symbols)]
            avg_return = sum(period_returns) / len(period_returns)
            portfolio_returns.append(avg_return)

        portfolio_metrics = {}

        if "volatility" in metrics:
            portfolio_metrics["volatility"] = RiskAssessor.calculate_volatility(portfolio_returns)

        if "var" in metrics:
            portfolio_metrics["var_95"] = RiskAssessor.calculate_var(portfolio_returns, confidence)

        if "sharpe" in metrics:
            portfolio_metrics["sharpe_ratio"] = RiskAssessor.calculate_sharpe_ratio(portfolio_returns)

        result["data"]["portfolio"] = portfolio_metrics

    return result


def backtest_strategy(symbol: str, strategy: Dict, start_date: str = None,
                     end_date: str = None, initial_capital: float = 1000000) -> Dict:
    """
    策略回测

    Args:
        symbol: 股票代码
        strategy: 策略规则
        start_date: 开始日期
        end_date: 结束日期
        initial_capital: 初始资金

    Returns:
        回测结果
    """
    result = {
        "code": 0,
        "message": "success",
        "data": {},
        "timestamp": datetime.now().isoformat()
    }

    # 获取数据
    kline = get_kline_data(symbol, "daily", start_date, end_date)
    if kline["code"] != 0:
        result["code"] = kline["code"]
        result["message"] = kline["message"]
        return result

    prices = kline["data"].get("close", [])
    dates = kline["data"].get("dates", [])

    if len(prices) < 30:
        result["code"] = 1001
        result["message"] = "数据不足"
        return result

    # 回测
    tester = StrategyBacktester(initial_capital=initial_capital)

    strategy_type = strategy.get("entry", {}).get("type", "ma_cross")

    if strategy_type == "ma_cross":
        fast = strategy.get("entry", {}).get("fast_ma", 5)
        slow = strategy.get("entry", {}).get("slow_ma", 20)
        backtest_result = tester.backtest_ma_cross(prices, dates, fast, slow)
    else:
        backtest_result = {"error": "不支持的策略类型"}

    result["data"] = backtest_result

    return result


def optimize_portfolio(symbols: List[str], objective: str = "max_sharpe",
                      constraints: Dict = None) -> Dict:
    """
    组合优化

    Args:
        symbols: 股票代码列表
        objective: 优化目标
        constraints: 约束条件

    Returns:
        优化结果
    """
    result = {
        "code": 0,
        "message": "success",
        "data": {
            "optimal_weights": {},
            "expected_return": None,
            "expected_volatility": None,
            "sharpe_ratio": None
        },
        "timestamp": datetime.now().isoformat()
    }

    if not symbols:
        result["code"] = 1001
        result["message"] = "股票列表为空"
        return result

    # 获取各股票收益和波动率
    expected_returns = {}
    volatilities = {}

    for symbol in symbols:
        start_date = (datetime.now() - timedelta(days=252)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        kline = get_kline_data(symbol, "daily", start_date=start_date, end_date=end_date)
        if kline["code"] != 0:
            continue

        closes = kline["data"].get("close", [])
        if len(closes) < 20:
            continue

        returns = RiskAssessor.calculate_returns(closes)
        if returns:
            expected_returns[symbol] = sum(returns) / len(returns) * 252  # 年化
            volatilities[symbol] = RiskAssessor.calculate_volatility(returns)

    if not expected_returns:
        result["code"] = 1002
        result["message"] = "无法获取数据"
        return result

    # 优化
    if objective == "max_sharpe":
        weights = PortfolioOptimizer.mean_variance_optimize(
            symbols, expected_returns, volatilities, {}, risk_aversion=2.0
        )
    elif objective == "min_vol":
        weights = PortfolioOptimizer.risk_parity(symbols, volatilities)
    else:
        weights = PortfolioOptimizer.equal_weight(symbols, {})

    # 应用约束
    if constraints:
        max_weight = constraints.get("max_weight", 1.0)
        min_weight = constraints.get("min_weight", 0.0)

        for symbol in weights:
            weights[symbol] = min(max(weights[symbol], min_weight), max_weight)

        # 归一化
        total = sum(weights.values())
        if total > 0:
            weights = {s: round(w / total, 4) for s, w in weights.items()}

    result["data"]["optimal_weights"] = weights

    # 计算组合预期收益和波动率
    if weights:
        portfolio_return = sum(expected_returns.get(s, 0) * w for s, w in weights.items())
        portfolio_vol = sum(volatilities.get(s, 0.2) * w for s, w in weights.items())

        result["data"]["expected_return"] = round(portfolio_return, 4)
        result["data"]["expected_volatility"] = round(portfolio_vol, 4)

        if portfolio_vol > 0:
            sharpe = (portfolio_return - 0.03) / portfolio_vol
            result["data"]["sharpe_ratio"] = round(sharpe, 2)

    return result


def forecast_price(symbol: str, horizon: int = 5,
                  model: str = "auto") -> Dict:
    """
    价格预测

    Args:
        symbol: 股票代码
        horizon: 预测周期天数
        model: 模型类型

    Returns:
        预测结果
    """
    result = {
        "code": 0,
        "message": "success",
        "data": {
            "symbol": symbol,
            "model": model,
            "predictions": []
        },
        "timestamp": datetime.now().isoformat()
    }

    # 获取数据 - 回溯100天
    start_date = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    kline = get_kline_data(symbol, "daily", start_date=start_date, end_date=end_date)
    if kline["code"] != 0:
        result["code"] = kline["code"]
        result["message"] = kline["message"]
        return result

    prices = kline["data"].get("close", [])

    if len(prices) < 20:
        result["code"] = 1001
        result["message"] = "数据不足"
        return result

    # 预测
    if model == "sma" or model == "auto":
        forecasts = PriceForecaster.simple_moving_average_forecast(prices, horizon)
        model_used = "sma"
    elif model == "linear":
        forecast_result = PriceForecaster.linear_trend_forecast(prices, horizon)
        forecasts = forecast_result.get("forecasts", [])
        model_used = "linear"
    elif model == "momentum":
        forecast_result = PriceForecaster.momentum_forecast(prices, horizon)
        forecasts = forecast_result.get("forecasts", [])
        model_used = "momentum"
    else:
        forecasts = PriceForecaster.simple_moving_average_forecast(prices, horizon)
        model_used = "sma"

    result["data"]["model"] = model_used

    # 构建预测结果
    dates = kline["data"].get("dates", [])
    last_date = dates[-1] if dates else None

    for i, forecast in enumerate(forecasts):
        # 计算置信区间 (±3%)
        lower = round(forecast * 0.97, 2)
        upper = round(forecast * 1.03, 2)

        result["data"]["predictions"].append({
            "day": i + 1,
            "price": forecast,
            "lower": lower,
            "upper": upper
        })

    # 趋势判断
    if len(forecasts) >= 2:
        trend = forecasts[-1] - prices[-1]
        result["data"]["direction"] = "up" if trend > 0 else "down"
        result["data"]["expected_change_pct"] = round((trend / prices[-1]) * 100, 2)
        result["data"]["confidence"] = 70  # 简化置信度

    return result


# ========== CLI测试 ==========

if __name__ == "__main__":
    print("=" * 60)
    print("风险管理模块 - 测试")
    print("=" * 60)

    # 测试1: 风险评估
    print("\n【测试1】风险评估")
    result = assess_risk(
        symbols=["600519", "000858"],
        metrics=["var", "beta", "sharpe", "max_drawdown", "volatility"],
        lookback_days=60
    )
    print(f"股票风险评估:")
    for symbol, data in result['data']['individual'].items():
        print(f"\n  {symbol}:")
        for metric, value in data.items():
            print(f"    {metric}: {value}")

    # 测试2: 策略回测
    print("\n" + "=" * 60)
    print("\n【测试2】均线交叉策略回测")
    result = backtest_strategy(
        symbol="600519",
        strategy={
            "entry": {"type": "ma_cross", "fast_ma": 5, "slow_ma": 20}
        },
        initial_capital=1000000
    )
    print(f"总收益率: {result['data'].get('total_return')}%")
    print(f"夏普比率: {result['data'].get('sharpe_ratio')}")
    print(f"最大回撤: {result['data'].get('max_drawdown')}%")
    print(f"胜率: {result['data'].get('win_rate')}%")
    print(f"交易次数: {result['data'].get('total_trades')}")

    # 测试3: 组合优化
    print("\n" + "=" * 60)
    print("\n【测试3】组合优化")
    result = optimize_portfolio(
        symbols=["600519", "000858", "601318"],
        objective="max_sharpe"
    )
    print(f"最优权重:")
    for symbol, weight in result['data']['optimal_weights'].items():
        print(f"  {symbol}: {weight * 100:.1f}%")
    print(f"预期收益率: {result['data']['expected_return'] * 100:.2f}%")
    print(f"预期波动率: {result['data']['expected_volatility'] * 100:.2f}%")
    print(f"夏普比率: {result['data']['sharpe_ratio']}")

    # 测试4: 价格预测
    print("\n" + "=" * 60)
    print("\n【测试4】价格预测")
    result = forecast_price("600519", horizon=5)
    print(f"模型: {result['data']['model']}")
    print(f"方向: {result['data']['direction']}")
    print(f"预期变动: {result['data']['expected_change_pct']}%")
    print(f"预测:")
    for pred in result['data']['predictions']:
        print(f"  第{pred['day']}天: {pred['price']} (区间: {pred['lower']}-{pred['upper']})")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)