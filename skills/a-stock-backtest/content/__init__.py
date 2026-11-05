# -*- coding: utf-8 -*-
"""
A股量化回测系统
A-share Quantitative Backtesting System

提供完整的数据获取、回测引擎、策略分析和可视化功能
"""

__version__ = "1.0.0"
__author__ = "MiniMax Agent"

from data_fetcher import StockDataFetcher, fetch_stock
from portfolio import Portfolio, Position, Trade
from backtest_engine import BacktestEngine, BacktestRunner, Signal, Order
from strategies import (
    ma_cross_strategy,
    rsi_strategy,
    bollinger_strategy,
    macd_strategy,
    kdj_strategy,
    dual_ma_rsi_strategy,
    list_strategies,
    get_strategy,
)
from performance import PerformanceAnalyzer, generate_performance_report
from visualization import BacktestVisualizer, create_backtest_report
from main import QuantBacktestSystem

__all__ = [
    # 数据获取
    "StockDataFetcher",
    "fetch_stock",
    # 投资组合
    "Portfolio",
    "Position",
    "Trade",
    # 回测引擎
    "BacktestEngine",
    "BacktestRunner",
    "Signal",
    "Order",
    # 策略
    "ma_cross_strategy",
    "rsi_strategy",
    "bollinger_strategy",
    "macd_strategy",
    "kdj_strategy",
    "dual_ma_rsi_strategy",
    "list_strategies",
    "get_strategy",
    # 绩效评估
    "PerformanceAnalyzer",
    "generate_performance_report",
    # 可视化
    "BacktestVisualizer",
    "create_backtest_report",
    # 主系统
    "QuantBacktestSystem",
]
