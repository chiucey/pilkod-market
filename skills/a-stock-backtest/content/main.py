# -*- coding: utf-8 -*-
"""
A股量化回测系统 - 主程序
提供完整的使用示例和命令行接口
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import pandas as pd
import numpy as np

# 导入项目模块
from config import BACKTEST_CONFIG, RESULTS_DIR, DATA_CONFIG
from data_fetcher import StockDataFetcher
from portfolio import Portfolio
from backtest_engine import BacktestEngine
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
from visualization import create_backtest_report

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuantBacktestSystem:
    """
    量化回测系统主类
    整合数据获取、回测、绩效评估和可视化
    """

    def __init__(self, data_dir: Optional[str] = None, results_dir: Optional[str] = None):
        """
        初始化量化回测系统

        Args:
            data_dir: 数据目录
            results_dir: 结果输出目录
        """
        self.data_fetcher = StockDataFetcher(
            cache_dir=data_dir or DATA_CONFIG.get("cache_dir")
        )
        self.results_dir = Path(results_dir or RESULTS_DIR)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.current_results: Dict = {}

    def run_backtest(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        strategy_name: str,
        initial_capital: float = 1000000,
        strategy_params: Optional[Dict] = None,
        use_cache: bool = True,
    ) -> Dict:
        """
        运行回测

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            strategy_name: 策略名称
            initial_capital: 初始资金
            strategy_params: 策略参数
            use_cache: 是否使用数据缓存

        Returns:
            回测结果字典
        """
        logger.info("=" * 60)
        logger.info("开始量化回测")
        logger.info("=" * 60)
        logger.info(f"回测标的: {symbols}")
        logger.info(f"回测区间: {start_date} 至 {end_date}")
        logger.info(f"策略名称: {strategy_name}")
        logger.info(f"初始资金: ¥{initial_capital:,.2f}")

        # 获取策略函数
        strategy = get_strategy(strategy_name)
        if strategy is None:
            raise ValueError(f"未找到策略: {strategy_name}")

        strategy_params = strategy_params or {}

        # 获取数据
        logger.info("\n[1/5] 获取市场数据...")
        data = self.data_fetcher.fetch_multiple_stocks(
            symbols, start_date, end_date, use_cache=use_cache
        )
        logger.info(f"成功加载 {len(data)} 只股票数据")

        # 创建回测引擎
        logger.info("\n[2/5] 初始化回测引擎...")
        engine = BacktestEngine(initial_capital=initial_capital)
        engine.load_data(data)
        engine.set_strategy(strategy, **strategy_params)

        # 执行回测
        logger.info("\n[3/5] 执行回测...")
        equity_curve = engine.run()

        # 获取交易记录
        trades = engine.get_trades()
        summary = engine.get_summary()

        # 计算绩效指标
        logger.info("\n[4/5] 计算绩效指标...")
        analyzer = PerformanceAnalyzer(equity_curve, trades)
        metrics = analyzer.get_full_report()

        # 保存结果
        logger.info("\n[5/5] 保存结果...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.results_dir / f"backtest_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        saved_files = create_backtest_report(
            equity_curve,
            trades,
            metrics,
            str(output_dir),
            show_plots=False
        )

        # 保存回测配置
        config_info = {
            "symbols": symbols,
            "start_date": start_date,
            "end_date": end_date,
            "strategy": strategy_name,
            "strategy_params": strategy_params,
            "initial_capital": initial_capital,
        }
        pd.DataFrame([config_info]).to_csv(output_dir / "config.csv", index=False)

        # 保存交易记录
        if not trades.empty:
            trades.to_csv(output_dir / "trades.csv")

        self.current_results = {
            "equity_curve": equity_curve,
            "trades": trades,
            "metrics": metrics,
            "summary": summary,
            "output_dir": str(output_dir),
            "saved_files": saved_files,
        }

        logger.info("\n" + "=" * 60)
        logger.info("回测完成!")
        logger.info("=" * 60)

        return self.current_results

    def print_results(self, results: Optional[Dict] = None) -> None:
        """
        打印回测结果

        Args:
            results: 回测结果字典
        """
        if results is None:
            results = self.current_results

        if not results:
            print("无回测结果可显示")
            return

        metrics = results.get("metrics", {})

        print("\n" + "=" * 60)
        print("回测绩效报告")
        print("=" * 60)

        print("\n【收益指标】")
        print(f"  总收益率:        {metrics.get('total_return', 0)*100:>10.2f}%")
        print(f"  年化收益率:      {metrics.get('annualized_return', 0)*100:>10.2f}%")
        print(f"  交易天数:        {metrics.get('total_days', 0):>10d}天")
        print(f"  日均收益率:      {metrics.get('avg_daily_return', 0)*100:>10.4f}%")

        print("\n【风险指标】")
        print(f"  年化波动率:      {metrics.get('annualized_volatility', 0)*100:>10.2f}%")
        print(f"  最大回撤:        {metrics.get('max_drawdown', 0)*100:>10.2f}%")
        print(f"  最大回撤天数:    {metrics.get('max_drawdown_duration', 0):>10d}天")
        print(f"  95% VaR:        {metrics.get('var_95', 0)*100:>10.2f}%")

        print("\n【风险调整收益】")
        print(f"  夏普比率:        {metrics.get('sharpe_ratio', 0):>10.4f}")
        print(f"  卡玛比率:        {metrics.get('calmar_ratio', 0):>10.4f}")
        print(f"  索提诺比率:      {metrics.get('sortino_ratio', 0):>10.4f}")

        print("\n【交易统计】")
        print(f"  总交易次数:      {metrics.get('total_trades', 0):>10d}")
        print(f"  胜率:            {metrics.get('win_rate', 0)*100:>10.2f}%")
        print(f"  平均盈亏:        ¥{metrics.get('avg_profit_per_trade', 0):>10.2f}")
        print(f"  盈亏比:          {metrics.get('profit_ratio', 0):>10.2f}")
        print(f"  利润因子:        {metrics.get('profit_factor', 0):>10.2f}")

        print("\n【结果文件】")
        output_dir = results.get("output_dir", "")
        print(f"  输出目录: {output_dir}")

        print("\n" + "=" * 60)


def run_demo():
    """运行演示"""
    print("\n" + "=" * 60)
    print("A股量化回测系统 - 演示")
    print("=" * 60)

    # 创建系统实例
    system = QuantBacktestSystem()

    # 示例1：移动平均线策略
    print("\n\n" + "-" * 40)
    print("示例1: MA均线交叉策略")
    print("-" * 40)

    results = system.run_backtest(
        symbols=["000001"],  # 平安银行
        start_date="2023-01-01",
        end_date="2024-01-01",
        strategy_name="ma_cross",
        initial_capital=1000000,
        strategy_params={"short_window": 5, "long_window": 20},
    )
    system.print_results(results)

    # 示例2：RSI策略
    print("\n\n" + "-" * 40)
    print("示例2: RSI超买超卖策略")
    print("-" * 40)

    results = system.run_backtest(
        symbols=["600519"],  # 贵州茅台
        start_date="2023-01-01",
        end_date="2024-01-01",
        strategy_name="rsi",
        initial_capital=1000000,
        strategy_params={"period": 14, "oversold": 30, "overbought": 70},
    )
    system.print_results(results)

    print("\n演示完成!")


def run_custom_backtest():
    """运行自定义回测"""
    print("\n" + "=" * 60)
    print("自定义回测")
    print("=" * 60)

    system = QuantBacktestSystem()

    # 获取用户输入
    symbol = input("\n请输入股票代码（如 000001）: ").strip()
    start_date = input("请输入开始日期（如 2023-01-01）: ").strip()
    end_date = input("请输入结束日期（如 2024-01-01）: ").strip()

    # 显示可用策略
    print("\n可用策略:")
    for i, name in enumerate(list_strategies(), 1):
        print(f"  {i}. {name}")

    strategy_idx = input("\n请选择策略编号: ").strip()
    strategies = list_strategies()
    if strategy_idx.isdigit() and 1 <= int(strategy_idx) <= len(strategies):
        strategy_name = strategies[int(strategy_idx) - 1]
    else:
        strategy_name = "ma_cross"

    initial_capital = float(input("请输入初始资金（默认1000000）: ").strip() or "1000000")

    # 运行回测
    results = system.run_backtest(
        symbols=[symbol],
        start_date=start_date,
        end_date=end_date,
        strategy_name=strategy_name,
        initial_capital=initial_capital,
    )

    system.print_results(results)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="A股量化回测系统")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["demo", "custom", "batch"],
        default="demo",
        help="运行模式"
    )
    parser.add_argument(
        "--symbol",
        type=str,
        help="股票代码"
    )
    parser.add_argument(
        "--start",
        type=str,
        default="2023-01-01",
        help="开始日期"
    )
    parser.add_argument(
        "--end",
        type=str,
        default="2024-01-01",
        help="结束日期"
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="ma_cross",
        help="策略名称"
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=1000000,
        help="初始资金"
    )
    parser.add_argument(
        "--params",
        type=str,
        help="策略参数（JSON格式）"
    )

    args = parser.parse_args()

    if args.mode == "demo":
        run_demo()
    elif args.mode == "custom":
        run_custom_backtest()
    elif args.mode == "batch":
        # 批量回测模式
        if not args.symbol:
            print("批量模式需要指定股票代码")
            return

        import json
        params = json.loads(args.params) if args.params else {}

        system = QuantBacktestSystem()
        results = system.run_backtest(
            symbols=[args.symbol],
            start_date=args.start,
            end_date=args.end,
            strategy_name=args.strategy,
            initial_capital=args.capital,
            strategy_params=params,
        )
        system.print_results(results)


if __name__ == "__main__":
    main()
