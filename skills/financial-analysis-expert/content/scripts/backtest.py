#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化策略回测框架
Financial Analysis Expert - Backtest Module
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import warnings

warnings.filterwarnings('ignore')


class Position(Enum):
    """持仓状态"""
    LONG = 1      # 多头
    SHORT = -1    # 空头
    FLAT = 0     # 空仓


@dataclass
class Trade:
    """交易记录"""
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_price: float
    exit_price: float
    position: Position
    size: float
    pnl: float
    pnl_pct: float
    holding_days: int


@dataclass
class PerformanceMetrics:
    """绩效指标"""
    total_return: float = 0.0
    annualized_return: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_duration: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    avg_holding_days: float = 0.0
    calmar_ratio: float = 0.0


class BacktestEngine:
    """
    回测引擎

    使用示例:
    --------
    >>> engine = BacktestEngine(initial_capital=1000000, commission=0.001)
    >>> engine.load_data(df)
    >>> engine.set_signal_generator(my_strategy)
    >>> results = engine.run()
    >>> print(results['metrics'])
    """

    def __init__(
        self,
        initial_capital: float = 1000000.0,
        commission: float = 0.001,
        slippage: float = 0.0,
        risk_free_rate: float = 0.03
    ):
        """
        初始化回测引擎

        Args:
            initial_capital: 初始资金
            commission: 交易佣金比例
            slippage: 滑点比例
            risk_free_rate: 无风险利率
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.risk_free_rate = risk_free_rate

        self.data: Optional[pd.DataFrame] = None
        self.signals: Optional[pd.Series] = None
        self.equity_curve: Optional[pd.Series] = None
        self.trades: List[Trade] = []
        self.metrics: Optional[PerformanceMetrics] = None

    def load_data(self, data: pd.DataFrame, price_col: str = 'close'):
        """
        加载市场数据

        Args:
            data: 包含OHLCV数据的DataFrame
            price_col: 价格列名
        """
        self.data = data.copy()
        self.price_col = price_col

    def set_signals(self, signals: pd.Series):
        """
        设置交易信号

        Args:
            signals: 信号序列，1=买入，-1=卖出，0=持有
        """
        self.signals = signals

    def create_signals(self, strategy_func: Callable, **kwargs):
        """
        使用策略函数生成信号

        Args:
            strategy_func: 策略函数，接收(data)返回signals
        """
        self.signals = strategy_func(self.data, **kwargs)

    def run(self) -> Dict:
        """
        执行回测

        Returns:
            包含回测结果的字典
        """
        if self.data is None or self.signals is None:
            raise ValueError("请先加载数据和设置信号")

        # 初始化
        capital = self.initial_capital
        position = Position.FLAT
        entry_price = 0.0
        entry_date = None
        position_size = 0.0

        equity = [self.initial_capital]
        dates = []

        self.trades = []

        prices = self.data[self.price_col].values
        signals = self.signals.values

        # 逐日回测
        for i in range(1, len(self.data)):
            date = self.data.index[i]
            price = prices[i]

            # 执行交易逻辑
            if signals[i] == 1 and position == Position.FLAT:
                # 买入开仓
                entry_price = price * (1 + self.slippage)
                entry_price *= (1 + self.commission)
                position_size = capital / entry_price
                capital = 0
                position = Position.LONG
                entry_date = date

            elif signals[i] == -1 and position == Position.LONG:
                # 卖出平仓
                exit_price = price * (1 - self.slippage)
                exit_price *= (1 - self.commission)
                capital = position_size * exit_price
                pnl = capital - self.initial_capital if len(self.trades) == 0 else capital - self._get_initial_capital()
                pnl_pct = pnl / self._get_initial_capital() * 100

                trade = Trade(
                    entry_date=entry_date,
                    exit_date=date,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    position=position,
                    size=position_size,
                    pnl=pnl,
                    pnl_pct=pnl_pct,
                    holding_days=(date - entry_date).days
                )
                self.trades.append(trade)

                position = Position.FLAT
                position_size = 0.0
                entry_price = 0.0

            # 更新权益
            if position == Position.LONG:
                current_value = position_size * price
            else:
                current_value = capital

            equity.append(current_value)
            dates.append(date)

        # 平仓未平仓位
        if position == Position.LONG:
            price = prices[-1]
            exit_price = price * (1 - self.slippage) * (1 - self.commission)
            capital = position_size * exit_price

            trade = Trade(
                entry_date=entry_date,
                exit_date=self.data.index[-1],
                entry_price=entry_price,
                exit_price=exit_price,
                position=Position.LONG,
                size=position_size,
                pnl=capital - self._get_initial_capital(),
                pnl_pct=(capital - self._get_initial_capital()) / self._get_initial_capital() * 100,
                holding_days=(self.data.index[-1] - entry_date).days
            )
            self.trades.append(trade)

        # 计算绩效指标
        self.equity_curve = pd.Series(equity, index=[self.data.index[0]] + dates)
        self.metrics = self._calculate_metrics()

        return {
            'equity_curve': self.equity_curve,
            'trades': self.trades,
            'metrics': self.metrics
        }

    def _get_initial_capital(self) -> float:
        """获取初始资金（考虑再投资）"""
        return self.initial_capital

    def _calculate_metrics(self) -> PerformanceMetrics:
        """计算绩效指标"""
        equity = self.equity_curve.values

        # 收益率序列
        returns = np.diff(equity) / equity[:-1]
        returns = np.insert(returns, 0, 0)

        # 总收益率
        total_return = (equity[-1] - equity[0]) / equity[0]

        # 年化收益率
        days = len(equity)
        years = days / 252
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

        # 波动率
        volatility = np.std(returns) * np.sqrt(252)

        # 夏普比率
        excess_return = annualized_return - self.risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility > 0 else 0

        # 最大回撤
        peak = equity[0]
        max_drawdown = 0
        max_dd_duration = 0
        current_dd_duration = 0

        for value in equity:
            if value > peak:
                peak = value
                current_dd_duration = 0
            else:
                drawdown = (peak - value) / peak
                current_dd_duration += 1
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                    max_dd_duration = current_dd_duration

        # 交易统计
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl <= 0]

        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0

        total_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0
        total_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 1
        profit_factor = total_profit / total_loss if total_loss > 0 else 0

        avg_holding = np.mean([t.holding_days for t in self.trades]) if self.trades else 0

        # 卡玛比率
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0

        return PerformanceMetrics(
            total_return=total_return * 100,
            annualized_return=annualized_return * 100,
            volatility=volatility * 100,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown * 100,
            max_drawdown_duration=max_dd_duration,
            win_rate=win_rate * 100,
            profit_factor=profit_factor,
            total_trades=len(self.trades),
            avg_holding_days=avg_holding,
            calmar_ratio=calmar_ratio
        )

    def get_metrics_dict(self) -> Dict:
        """获取绩效指标字典"""
        if self.metrics is None:
            return {}
        return {
            '总收益率': f"{self.metrics.total_return:.2f}%",
            '年化收益率': f"{self.metrics.annualized_return:.2f}%",
            '波动率': f"{self.metrics.volatility:.2f}%",
            '夏普比率': f"{self.metrics.sharpe_ratio:.2f}",
            '最大回撤': f"{self.metrics.max_drawdown:.2f}%",
            '卡玛比率': f"{self.metrics.calmar_ratio:.2f}",
            '胜率': f"{self.metrics.win_rate:.2f}%",
            '盈亏比': f"{self.metrics.profit_factor:.2f}",
            '交易次数': self.metrics.total_trades,
            '平均持仓天数': f"{self.metrics.avg_holding_days:.1f}"
        }


class StrategyLibrary:
    """策略库"""

    @staticmethod
    def ma_cross_strategy(
        data: pd.DataFrame,
        fast_period: int = 5,
        slow_period: int = 20
    ) -> pd.Series:
        """
        均线交叉策略

        Args:
            data: OHLC数据
            fast_period: 快速均线周期
            slow_period: 慢速均线周期

        Returns:
            信号序列
        """
        close = data['close']
        ma_fast = close.rolling(window=fast_period).mean()
        ma_slow = close.rolling(window=slow_period).mean()

        signals = pd.Series(0, index=data.index)
        signals[ma_fast > ma_slow] = 1
        signals[ma_fast <= ma_slow] = -1

        # 只在状态变化时产生信号
        signals = signals.diff().fillna(0)
        signals[signals == -2] = -1  # 从1变-1
        signals[signals == 2] = 1    # 从-1变1

        return signals.replace(0, np.nan).fillna(0)

    @staticmethod
    def macd_strategy(
        data: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> pd.Series:
        """
        MACD策略

        Args:
            data: OHLC数据
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期

        Returns:
            信号序列
        """
        close = data['close']
        ema_fast = close.ewm(span=fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=slow_period, adjust=False).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal_period, adjust=False).mean()
        macd = dif - dea

        signals = pd.Series(0, index=data.index)
        signals[(dif > dea) & (dif.shift(1) <= dea.shift(1))] = 1
        signals[(dif < dea) & (dif.shift(1) >= dea.shift(1))] = -1

        return signals

    @staticmethod
    def bollinger_band_strategy(
        data: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> pd.Series:
        """
        布林带均值回归策略

        Args:
            data: OHLC数据
            period: 周期
            std_dev: 标准差倍数

        Returns:
            信号序列
        """
        close = data['close']
        ma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        upper = ma + std_dev * std
        lower = ma - std_dev * std

        signals = pd.Series(0, index=data.index)
        signals[close < lower] = 1   # 触及下轨买入
        signals[close > upper] = -1  # 触及上轨卖出

        return signals


# 使用示例
if __name__ == "__main__":
    # 生成示例数据
    np.random.seed(42)
    n = 500
    dates = pd.date_range("2023-01-01", periods=n)

    close = pd.Series(100 + np.cumsum(np.random.randn(n) * 2), index=dates)
    high = close + np.abs(np.random.randn(n) * 3)
    low = close - np.abs(np.random.randn(n) * 3)

    data = pd.DataFrame({
        'open': close - np.random.randn(n),
        'high': high,
        'low': low,
        'close': close,
        'volume': np.random.randint(1000000, 10000000, n)
    })

    # 创建回测引擎
    engine = BacktestEngine(
        initial_capital=1000000,
        commission=0.001,
        slippage=0.0005
    )

    # 加载数据
    engine.load_data(data)

    # 使用策略库生成信号
    signals = StrategyLibrary.macd_strategy(data)
    engine.set_signals(signals)

    # 运行回测
    results = engine.run()

    # 输出结果
    print("=" * 50)
    print("回测结果")
    print("=" * 50)
    for key, value in engine.get_metrics_dict().items():
        print(f"{key}: {value}")
    print("=" * 50)
    print(f"交易记录数: {len(results['trades'])}")
