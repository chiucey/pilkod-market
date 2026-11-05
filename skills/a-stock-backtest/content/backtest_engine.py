# -*- coding: utf-8 -*-
"""
回测引擎 - 核心回测逻辑
负责策略执行、信号生成、订单执行和回测控制
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Callable
from dataclasses import dataclass
import pandas as pd
import numpy as np

from portfolio import Portfolio
from config import BACKTEST_CONFIG

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    """交易信号数据类"""
    date: datetime
    symbol: str
    action: str  # 'buy', 'sell', 'hold'
    quantity: int = 0
    price: float = 0.0
    reason: str = ""


@dataclass
class Order:
    """订单数据类"""
    date: datetime
    symbol: str
    order_type: str  # 'buy', 'sell'
    quantity: int
    price: float


class BacktestEngine:
    """
    回测引擎类
    执行策略回测，模拟真实交易环境
    """

    def __init__(
        self,
        initial_capital: Optional[float] = None,
        commission_rate: Optional[float] = None,
        slippage_rate: Optional[float] = None,
    ):
        """
        初始化回测引擎

        Args:
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage_rate: 滑点率
        """
        self.initial_capital = initial_capital or BACKTEST_CONFIG["initial_capital"]
        self.commission_rate = commission_rate or BACKTEST_CONFIG["commission_rate"]
        self.slippage_rate = slippage_rate or BACKTEST_CONFIG["slippage_rate"]

        # 初始化投资组合
        self.portfolio = Portfolio(initial_capital=self.initial_capital)

        # 数据存储
        self.data: Dict[str, pd.DataFrame] = {}  # symbol -> DataFrame
        self.signals: List[Signal] = []
        self.orders: List[Order] = []

        # 回测状态
        self.current_date: Optional[datetime] = None
        self.current_prices: Dict[str, float] = {}
        self.is_running = False

        # 策略
        self.strategy: Optional[Callable] = None
        self.strategy_params: Dict = {}

        logger.info(f"回测引擎初始化完成，初始资金: ¥{self.initial_capital:,.2f}")

    def load_data(self, data: Union[pd.DataFrame, Dict[str, pd.DataFrame]]) -> None:
        """
        加载市场数据

        Args:
            data: 单只股票DataFrame或{股票代码: DataFrame}字典
        """
        if isinstance(data, pd.DataFrame):
            # 假设是单只股票，使用默认symbol
            self.data['default'] = data.copy()
        else:
            self.data = {k: v.copy() for k, v in data.items()}

        # 合并数据索引
        self.trading_dates = self._get_common_trading_dates()

        logger.info(f"数据加载完成，共 {len(self.trading_dates)} 个交易日，"
                   f"{len(self.data)} 只股票")

    def _get_common_trading_dates(self) -> pd.DatetimeIndex:
        """获取所有股票的共同交易日"""
        if not self.data:
            return pd.DatetimeIndex([])

        date_sets = [set(df.index) for df in self.data.values()]
        common_dates = set.intersection(*date_sets)
        return pd.DatetimeIndex(sorted(common_dates))

    def set_strategy(self, strategy: Callable, **params) -> None:
        """
        设置交易策略

        Args:
            strategy: 策略函数，接收(date, data, portfolio)参数
            **params: 策略参数
        """
        self.strategy = strategy
        self.strategy_params = params
        logger.info(f"策略已设置: {strategy.__name__}, 参数: {params}")

    def generate_signals(self, date: datetime, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """
        生成交易信号

        Args:
            date: 当前日期
            data: 当日市场数据

        Returns:
            信号列表
        """
        if self.strategy is None:
            return []

        try:
            return self.strategy(date, data, self.portfolio, **self.strategy_params)
        except Exception as e:
            logger.error(f"策略执行错误: {e}")
            return []

    def execute_order(self, order: Order) -> bool:
        """
        执行订单

        Args:
            order: 订单对象

        Returns:
            是否成功
        """
        if order.order_type == 'buy':
            return self.portfolio.buy(
                order.symbol,
                order.quantity,
                order.price,
                order.date
            )
        elif order.order_type == 'sell':
            return self.portfolio.sell(
                order.symbol,
                order.quantity,
                order.price,
                order.date
            )
        return False

    def _get_current_prices(self, date: datetime) -> Dict[str, float]:
        """
        获取指定日期的收盘价

        Args:
            date: 日期

        Returns:
            {symbol: price}字典
        """
        prices = {}
        for symbol, df in self.data.items():
            if date in df.index:
                prices[symbol] = df.loc[date, 'close']
            else:
                # 寻找最近交易日
                available_dates = df.index[df.index <= date]
                if len(available_dates) > 0:
                    prices[symbol] = df.loc[available_dates[-1], 'close']
        return prices

    def _get_data_until_date(self, date: datetime) -> Dict[str, pd.DataFrame]:
        """
        获取截至指定日期的历史数据

        Args:
            date: 日期

        Returns:
            {symbol: DataFrame}字典，每只股票包含截至该日期的数据
        """
        result = {}
        for symbol, df in self.data.items():
            result[symbol] = df[df.index <= date]
        return result

    def run(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        执行回测

        Args:
            start_date: 回测开始日期
            end_date: 回测结束日期

        Returns:
            回测结果DataFrame
        """
        if not self.data:
            raise ValueError("请先加载市场数据")

        # 确定回测区间
        if start_date is None:
            start_date = self.trading_dates[0]
        if end_date is None:
            end_date = self.trading_dates[-1]

        # 过滤交易日
        dates = self.trading_dates[
            (self.trading_dates >= start_date) &
            (self.trading_dates <= end_date)
        ]

        logger.info(f"开始回测: {start_date.date()} 至 {end_date.date()}，共 {len(dates)} 个交易日")
        self.is_running = True

        # 逐日执行回测
        for i, date in enumerate(dates):
            self.current_date = date

            # 获取当前价格
            self.current_prices = self._get_current_prices(date)

            # 获取历史数据（用于计算指标）
            historical_data = self._get_data_until_date(date)

            # 生成信号
            signals = self.generate_signals(date, historical_data)

            # 执行信号
            for signal in signals:
                self._process_signal(signal)

            # 记录当日状态
            self.portfolio.record_state(date, self.current_prices)

            # 进度日志
            if (i + 1) % 50 == 0:
                logger.info(f"回测进度: {i + 1}/{len(dates)} ({100*(i+1)/len(dates):.1f}%)")

        self.is_running = False
        logger.info("回测完成")

        return self.get_results()

    def _process_signal(self, signal: Signal) -> None:
        """
        处理交易信号

        Args:
            signal: 信号对象
        """
        if signal.action == 'hold':
            return

        price = signal.price
        if price <= 0:
            price = self.current_prices.get(signal.symbol, 0)
            if price <= 0:
                return

        # 创建订单
        order = Order(
            date=signal.date,
            symbol=signal.symbol,
            order_type=signal.action,
            quantity=signal.quantity,
            price=price
        )

        # 执行订单
        success = self.execute_order(order)
        if success:
            self.orders.append(order)
            self.signals.append(signal)

    def get_results(self) -> pd.DataFrame:
        """
        获取回测结果

        Returns:
            回测结果DataFrame
        """
        return self.portfolio.get_equity_curve()

    def get_trades(self) -> pd.DataFrame:
        """
        获取交易记录

        Returns:
            交易记录DataFrame
        """
        return self.portfolio.get_trade_history()

    def get_summary(self) -> Dict:
        """
        获取回测摘要

        Returns:
            摘要信息字典
        """
        return self.portfolio.get_summary()

    def get_positions_at_date(self, date: datetime) -> Dict:
        """
        获取指定日期的持仓情况

        Args:
            date: 日期

        Returns:
            持仓字典
        """
        positions = {}
        for symbol, position in self.portfolio.positions.items():
            positions[symbol] = {
                'quantity': position.quantity,
                'avg_cost': position.avg_cost,
                'market_value': position.quantity * self.current_prices.get(symbol, 0)
            }
        return positions


class BacktestRunner:
    """
    回测运行器
    便捷地运行回测并获取结果
    """

    def __init__(self, data_fetcher=None):
        """
        初始化回测运行器

        Args:
            data_fetcher: 数据获取器实例
        """
        self.data_fetcher = data_fetcher
        self.results = None

    def run(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        strategy: Callable,
        initial_capital: float = 1000000,
        **strategy_params
    ) -> Dict:
        """
        运行回测

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            strategy: 策略函数
            initial_capital: 初始资金
            **strategy_params: 策略参数

        Returns:
            回测结果字典
        """
        from data_fetcher import StockDataFetcher

        # 获取数据
        if self.data_fetcher is None:
            self.data_fetcher = StockDataFetcher()

        logger.info(f"获取 {len(symbols)} 只股票数据...")
        data = self.data_fetcher.fetch_multiple_stocks(symbols, start_date, end_date)

        # 创建回测引擎
        engine = BacktestEngine(initial_capital=initial_capital)
        engine.load_data(data)
        engine.set_strategy(strategy, **strategy_params)

        # 执行回测
        logger.info("开始回测...")
        equity_curve = engine.run()

        # 获取结果
        self.results = {
            'equity_curve': equity_curve,
            'trades': engine.get_trades(),
            'summary': engine.get_summary(),
        }

        return self.results


if __name__ == "__main__":
    # 简单测试
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("回测引擎测试")
    print("=" * 60)

    # 导入测试
    from data_fetcher import StockDataFetcher

    fetcher = StockDataFetcher()
    data = fetcher.fetch_stock_data("000001", "2023-01-01", "2024-01-01")

    # 创建回测引擎
    engine = BacktestEngine(initial_capital=100000)
    engine.load_data(data)

    # 设置简单策略：每日买入100股
    def simple_strategy(date, data, portfolio, **params):
        signals = []
        for symbol, df in data.items():
            if len(df) > 0:
                signals.append(Signal(
                    date=date,
                    symbol=symbol,
                    action='buy',
                    quantity=100,
                    price=df.iloc[-1]['close'],
                    reason='test'
                ))
        return signals

    engine.set_strategy(simple_strategy)

    # 运行回测
    results = engine.run()

    print("\n回测摘要:")
    for key, value in engine.get_summary().items():
        print(f"  {key}: {value}")

    print("\n资金曲线预览:")
    print(results.tail())
