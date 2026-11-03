# -*- coding: utf-8 -*-
"""
投资组合管理模块
负责交易执行、资金管理、持仓记录等核心功能
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np

from config import BACKTEST_CONFIG

logger = logging.getLogger(__name__)


class OrderType(Enum):
    """订单类型枚举"""
    BUY = "buy"
    SELL = "sell"


class Position:
    """
    持仓记录类
    记录单个股票的持仓信息
    """

    def __init__(
        self,
        symbol: str,
        quantity: int,
        avg_cost: float,
        entry_date: datetime,
    ):
        """
        初始化持仓

        Args:
            symbol: 股票代码
            quantity: 持股数量（股数）
            avg_cost: 平均成本价
            entry_date: 入场日期
        """
        self.symbol = symbol
        self.quantity = quantity
        self.avg_cost = avg_cost
        self.entry_date = entry_date
        self.trades: List[Dict] = []  # 交易记录列表

    @property
    def market_value(self) -> float:
        """当前市值"""
        return self.quantity * self.avg_cost

    def add_trade(self, trade: Dict) -> None:
        """添加交易记录"""
        self.trades.append(trade)

    def update(self, quantity: int, price: float, trade_type: str, date: datetime) -> None:
        """
        更新持仓

        Args:
            quantity: 交易数量（正数买入，负数卖出）
            price: 成交价格
            trade_type: 交易类型
            date: 交易日期
        """
        if trade_type == OrderType.BUY.value:
            # 买入：更新平均成本
            total_cost = self.quantity * self.avg_cost + quantity * price
            self.quantity += quantity
            if self.quantity > 0:
                self.avg_cost = total_cost / self.quantity
        elif trade_type == OrderType.SELL.value:
            # 卖出：减少持仓
            self.quantity += quantity  # quantity为负数

        # 记录交易
        trade_record = {
            "date": date,
            "type": trade_type,
            "quantity": quantity,
            "price": price,
            "symbol": self.symbol,
        }
        self.add_trade(trade_record)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "avg_cost": self.avg_cost,
            "market_value": self.market_value,
            "entry_date": self.entry_date,
        }


@dataclass
class Trade:
    """
    交易记录数据类
    """
    date: datetime
    symbol: str
    order_type: OrderType
    quantity: int
    price: float
    commission: float = 0.0
    stamp_tax: float = 0.0
    slippage: float = 0.0

    @property
    def total_cost(self) -> float:
        """总成本（含手续费、印花税、滑点）"""
        return self.quantity * self.price + self.commission + self.slippage

    @property
    def total_proceeds(self) -> float:
        """总收入（含手续费、印花税、滑点）"""
        return self.quantity * self.price - self.commission - self.stamp_tax - self.slippage


@dataclass
class PortfolioState:
    """
    投资组合状态快照
    """
    date: datetime
    cash: float
    positions: Dict[str, Position]
    total_value: float
    daily_return: float = 0.0
    cumulative_return: float = 0.0


class Portfolio:
    """
    投资组合管理类
    管理现金、持仓、执行交易、计算盈亏
    """

    def __init__(self, initial_capital: Optional[float] = None):
        """
        初始化投资组合

        Args:
            initial_capital: 初始资金，默认从配置文件读取
        """
        self.initial_capital = initial_capital or BACKTEST_CONFIG["initial_capital"]
        self.cash = self.initial_capital
        self.positions: Dict[str, Position] = {}  # symbol -> Position
        self.trades: List[Trade] = []  # 所有交易记录
        self.history: List[PortfolioState] = []  # 历史状态记录

        # 交易成本参数
        self.commission_rate = BACKTEST_CONFIG["commission_rate"]
        self.stamp_tax_rate = BACKTEST_CONFIG["stamp_tax_rate"]
        self.slippage_rate = BACKTEST_CONFIG["slippage_rate"]
        self.min_trade_unit = BACKTEST_CONFIG["min_trade_unit"]

        # 统计指标
        self.total_commission = 0.0
        self.total_stamp_tax = 0.0

        logger.info(f"投资组合初始化完成，初始资金: ¥{self.initial_capital:,.2f}")

    def _calculate_commission(self, amount: float) -> float:
        """
        计算手续费

        Args:
            amount: 交易金额

        Returns:
            手续费
        """
        commission = amount * self.commission_rate
        return max(commission, 5.0)  # 最低5元

    def _calculate_stamp_tax(self, amount: float) -> float:
        """
        计算印花税（仅卖出时收取）

        Args:
            amount: 交易金额

        Returns:
            印花税
        """
        return amount * self.stamp_tax_rate

    def _calculate_slippage(self, amount: float) -> float:
        """
        计算滑点成本

        Args:
            amount: 交易金额

        Returns:
            滑点成本
        """
        return amount * self.slippage_rate

    def _adjust_quantity(self, quantity: int) -> int:
        """
        调整交易数量为最小单位的整数倍

        Args:
            quantity: 原始数量

        Returns:
            调整后的数量
        """
        return (quantity // self.min_trade_unit) * self.min_trade_unit

    def get_position(self, symbol: str) -> Optional[Position]:
        """
        获取持仓

        Args:
            symbol: 股票代码

        Returns:
            持仓对象或None
        """
        return self.positions.get(symbol)

    def get_position_value(self, symbol: str, current_price: float) -> float:
        """
        获取持仓市值

        Args:
            symbol: 股票代码
            current_price: 当前价格

        Returns:
            持仓市值
        """
        position = self.get_position(symbol)
        if position:
            return position.quantity * current_price
        return 0.0

    def get_total_value(self, prices: Dict[str, float]) -> float:
        """
        计算投资组合总市值

        Args:
            prices: 当前各股票价格字典 {symbol: price}

        Returns:
            总市值
        """
        position_value = sum(
            self.get_position_value(symbol, prices.get(symbol, 0))
            for symbol in self.positions
        )
        return self.cash + position_value

    def buy(
        self,
        symbol: str,
        quantity: int,
        price: float,
        date: datetime,
    ) -> bool:
        """
        买入股票

        Args:
            symbol: 股票代码
            quantity: 买入数量（股数）
            price: 买入价格
            date: 交易日期

        Returns:
            是否成功
        """
        # 调整数量为最小单位倍数
        quantity = self._adjust_quantity(quantity)
        if quantity <= 0:
            logger.warning(f"无效买入数量: {quantity}")
            return False

        # 计算成本
        amount = quantity * price
        commission = self._calculate_commission(amount)
        slippage = self._calculate_slippage(amount)
        total_cost = amount + commission + slippage

        # 检查资金是否充足
        if total_cost > self.cash:
            # 尝试用全部资金买入
            max_quantity = int((self.cash * 0.99) / (price * (1 + self.commission_rate + self.slippage_rate)))
            max_quantity = self._adjust_quantity(max_quantity)
            if max_quantity < self.min_trade_unit:
                logger.warning(f"资金不足，无法买入 {symbol}")
                return False
            quantity = max_quantity
            amount = quantity * price
            commission = self._calculate_commission(amount)
            slippage = self._calculate_slippage(amount)
            total_cost = amount + commission + slippage

        # 执行买入
        self.cash -= total_cost

        if symbol in self.positions:
            self.positions[symbol].update(quantity, price, OrderType.BUY.value, date)
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                avg_cost=price,  # 简化处理
                entry_date=date,
            )
            self.positions[symbol].update(0, price, OrderType.BUY.value, date)
            self.positions[symbol].quantity = quantity
            self.positions[symbol].avg_cost = price

        # 记录交易
        trade = Trade(
            date=date,
            symbol=symbol,
            order_type=OrderType.BUY,
            quantity=quantity,
            price=price,
            commission=commission,
            slippage=slippage,
        )
        self.trades.append(trade)
        self.total_commission += commission

        logger.info(
            f"买入 {symbol}: 数量={quantity}, 价格=¥{price:.2f}, "
            f"金额=¥{amount:.2f}, 手续费=¥{commission:.2f}"
        )
        return True

    def sell(
        self,
        symbol: str,
        quantity: int,
        price: float,
        date: datetime,
    ) -> bool:
        """
        卖出股票

        Args:
            symbol: 股票代码
            quantity: 卖出数量（股数）
            price: 卖出价格
            date: 交易日期

        Returns:
            是否成功
        """
        # 检查持仓
        position = self.get_position(symbol)
        if not position or position.quantity < quantity:
            # 尝试卖出全部持仓
            if not position or position.quantity == 0:
                logger.warning(f"无持仓或持仓不足，无法卖出 {symbol}")
                return False
            quantity = position.quantity

        # 调整数量
        quantity = self._adjust_quantity(quantity)
        if quantity <= 0:
            return False

        # 计算收入
        amount = quantity * price
        commission = self._calculate_commission(amount)
        stamp_tax = self._calculate_stamp_tax(amount)
        slippage = self._calculate_slippage(amount)
        total_proceeds = amount - commission - stamp_tax - slippage

        # 执行卖出
        self.cash += total_proceeds
        position.update(-quantity, price, OrderType.SELL.value, date)

        # 移除空仓
        if position.quantity <= 0:
            del self.positions[symbol]

        # 记录交易
        trade = Trade(
            date=date,
            symbol=symbol,
            order_type=OrderType.SELL,
            quantity=quantity,
            price=price,
            commission=commission,
            stamp_tax=stamp_tax,
            slippage=slippage,
        )
        self.trades.append(trade)
        self.total_commission += commission
        self.total_stamp_tax += stamp_tax

        logger.info(
            f"卖出 {symbol}: 数量={quantity}, 价格=¥{price:.2f}, "
            f"金额=¥{amount:.2f}, 手续费=¥{commission:.2f}, 印花税=¥{stamp_tax:.2f}"
        )
        return True

    def sell_all(self, symbol: str, price: float, date: datetime) -> bool:
        """
        卖出全部持仓

        Args:
            symbol: 股票代码
            price: 卖出价格
            date: 交易日期

        Returns:
            是否成功
        """
        position = self.get_position(symbol)
        if not position:
            return False
        return self.sell(symbol, position.quantity, price, date)

    def record_state(self, date: datetime, prices: Dict[str, float]) -> None:
        """
        记录当前状态到历史

        Args:
            date: 当前日期
            prices: 各股票当前价格
        """
        total_value = self.get_total_value(prices)

        state = PortfolioState(
            date=date,
            cash=self.cash,
            positions={k: v for k, v in self.positions.items()},
            total_value=total_value,
        )

        if self.history:
            prev_value = self.history[-1].total_value
            state.daily_return = (total_value - prev_value) / prev_value if prev_value > 0 else 0
            state.cumulative_return = (total_value - self.initial_capital) / self.initial_capital

        self.history.append(state)

    def get_equity_curve(self) -> pd.DataFrame:
        """
        获取资金曲线

        Returns:
            包含每日资产数据的DataFrame
        """
        if not self.history:
            return pd.DataFrame()

        data = {
            "date": [state.date for state in self.history],
            "cash": [state.cash for state in self.history],
            "total_value": [state.total_value for state in self.history],
            "daily_return": [state.daily_return for state in self.history],
            "cumulative_return": [state.cumulative_return for state in self.history],
        }

        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)
        return df

    def get_trade_history(self) -> pd.DataFrame:
        """
        获取交易历史

        Returns:
            交易记录DataFrame
        """
        if not self.trades:
            return pd.DataFrame()

        data = {
            "date": [t.date for t in self.trades],
            "symbol": [t.symbol for t in self.trades],
            "type": [t.order_type.value for t in self.trades],
            "quantity": [t.quantity for t in self.trades],
            "price": [t.price for t in self.trades],
            "commission": [t.commission for t in self.trades],
            "stamp_tax": [t.stamp_tax for t in self.trades],
        }

        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)
        return df

    def get_summary(self) -> Dict:
        """
        获取投资组合摘要

        Returns:
            摘要信息字典
        """
        total_trades = len(self.trades)
        buy_trades = len([t for t in self.trades if t.order_type == OrderType.BUY])
        sell_trades = len([t for t in self.trades if t.order_type == OrderType.SELL])

        return {
            "initial_capital": self.initial_capital,
            "final_value": self.history[-1].total_value if self.history else self.initial_capital,
            "total_return": self.history[-1].cumulative_return if self.history else 0,
            "cash": self.cash,
            "positions_count": len(self.positions),
            "total_trades": total_trades,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "total_commission": self.total_commission,
            "total_stamp_tax": self.total_stamp_tax,
        }


if __name__ == "__main__":
    # 测试投资组合功能
    logging.basicConfig(level=logging.INFO)

    portfolio = Portfolio(initial_capital=100000)

    print("=" * 60)
    print("测试投资组合功能")
    print("=" * 60)

    # 测试买入
    portfolio.buy("000001", 1000, 10.5, datetime(2023, 1, 1))
    print(f"\n买入后现金: ¥{portfolio.cash:,.2f}")
    print(f"000001 持仓: {portfolio.get_position('000001').to_dict()}")

    # 测试卖出
    portfolio.sell("000001", 500, 11.0, datetime(2023, 1, 15))
    print(f"\n卖出后现金: ¥{portfolio.cash:,.2f}")
    print(f"000001 持仓: {portfolio.get_position('000001').to_dict()}")

    # 测试资金曲线
    portfolio.record_state(datetime(2023, 1, 1), {"000001": 10.5})
    portfolio.record_state(datetime(2023, 1, 15), {"000001": 11.0})

    equity = portfolio.get_equity_curve()
    print("\n资金曲线:")
    print(equity)

    trades = portfolio.get_trade_history()
    print("\n交易记录:")
    print(trades)
