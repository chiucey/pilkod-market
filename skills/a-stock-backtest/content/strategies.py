# -*- coding: utf-8 -*-
"""
交易策略模块 - 经典量化策略实现
提供多种技术指标策略用于回测
"""

import logging
from typing import Dict, List, Callable
import pandas as pd
import numpy as np

from backtest_engine import Signal
from config import STRATEGY_CONFIG

logger = logging.getLogger(__name__)


def ma_cross_strategy(
    date, data: Dict[str, pd.DataFrame], portfolio,
    short_window: int = 5, long_window: int = 20, **kwargs
) -> List[Signal]:
    """
    移动平均线交叉策略
    当短期均线上穿长期均线时买入，下穿时卖出

    Args:
        short_window: 短期均线周期
        long_window: 长期均线周期

    Returns:
        Signal列表
    """
    signals = []
    buy_ratio = kwargs.get('buy_ratio', 1.0)  # 获取仓位比例

    for symbol, df in data.items():
        if len(df) < long_window:
            continue

        # 计算移动平均线
        ma_short = df['close'].rolling(window=short_window).mean()
        ma_long = df['close'].rolling(window=long_window).mean()

        # 获取最新值
        current_ma_short = ma_short.iloc[-1]
        current_ma_long = ma_long.iloc[-1]
        prev_ma_short = ma_short.iloc[-2]
        prev_ma_long = ma_long.iloc[-2]
        current_price = df['close'].iloc[-1]

        # 金叉：短期均线上穿长期均线
        if prev_ma_short <= prev_ma_long and current_ma_short > current_ma_long:
            # 检查是否已持仓
            position = portfolio.get_position(symbol)
            if position is None or position.quantity == 0:
                # 使用仓位比例计算买入数量
                available_cash = portfolio.cash * buy_ratio
                quantity = int(available_cash * 0.99 / (current_price * (1 + 0.0003 + 0.0001)))
                quantity = (quantity // 100) * 100  # 整手
                if quantity >= 100:
                    signals.append(Signal(
                        date=date,
                        symbol=symbol,
                        action='buy',
                        quantity=quantity,
                        price=current_price,
                        reason=f'MA金叉: short={short_window}, long={long_window}'
                    ))

        # 死叉：短期均线下穿长期均线
        elif prev_ma_short >= prev_ma_long and current_ma_short < current_ma_long:
            position = portfolio.get_position(symbol)
            if position and position.quantity > 0:
                signals.append(Signal(
                    date=date,
                    symbol=symbol,
                    action='sell',
                    quantity=position.quantity,
                    price=current_price,
                    reason=f'MA死叉: short={short_window}, long={long_window}'
                ))

    return signals


def rsi_strategy(
    date, data: Dict[str, pd.DataFrame], portfolio,
    period: int = 14, oversold: int = 30, overbought: int = 70, **kwargs
) -> List[Signal]:
    """
    RSI相对强弱指标策略
    RSI低于超卖阈值时买入，高于超买阈值时卖出

    Args:
        period: RSI计算周期
        oversold: 超卖阈值
        overbought: 超买阈值

    Returns:
        Signal列表
    """
    signals = []
    buy_ratio = kwargs.get('buy_ratio', 1.0)

    for symbol, df in data.items():
        if len(df) < period + 1:
            continue

        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2]
        current_price = df['close'].iloc[-1]

        # RSI从超卖区域上穿
        if prev_rsi < oversold and current_rsi >= oversold:
            position = portfolio.get_position(symbol)
            if position is None or position.quantity == 0:
                available_cash = portfolio.cash * buy_ratio
                quantity = int(available_cash * 0.99 / (current_price * (1 + 0.0003 + 0.0001)))
                quantity = (quantity // 100) * 100
                if quantity >= 100:
                    signals.append(Signal(
                        date=date,
                        symbol=symbol,
                        action='buy',
                        quantity=quantity,
                        price=current_price,
                        reason=f'RSI超卖: {current_rsi:.2f}'
                    ))

        # RSI从超买区域下穿
        elif prev_rsi > overbought and current_rsi <= overbought:
            position = portfolio.get_position(symbol)
            if position and position.quantity > 0:
                signals.append(Signal(
                    date=date,
                    symbol=symbol,
                    action='sell',
                    quantity=position.quantity,
                    price=current_price,
                    reason=f'RSI超买: {current_rsi:.2f}'
                ))

    return signals


def bollinger_strategy(
    date, data: Dict[str, pd.DataFrame], portfolio,
    period: int = 20, std_dev: float = 2.0, **kwargs
) -> List[Signal]:
    """
    布林带策略
    价格触及下轨时买入，触及上轨时卖出

    Args:
        period: 布林带周期
        std_dev: 标准差倍数

    Returns:
        Signal列表
    """
    signals = []
    buy_ratio = kwargs.get('buy_ratio', 1.0)

    for symbol, df in data.items():
        if len(df) < period:
            continue

        # 计算布林带
        middle = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper = middle + std_dev * std
        lower = middle - std_dev * std

        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        current_lower = lower.iloc[-1]
        current_upper = upper.iloc[-1]
        prev_lower = lower.iloc[-2]
        prev_upper = upper.iloc[-2]

        # 价格从下轨下方上穿下轨
        if prev_price <= prev_lower and current_price > current_lower:
            position = portfolio.get_position(symbol)
            if position is None or position.quantity == 0:
                available_cash = portfolio.cash * buy_ratio
                quantity = int(available_cash * 0.99 / (current_price * (1 + 0.0003 + 0.0001)))
                quantity = (quantity // 100) * 100
                if quantity >= 100:
                    signals.append(Signal(
                        date=date,
                        symbol=symbol,
                        action='buy',
                        quantity=quantity,
                        price=current_price,
                        reason=f'布林带下轨突破'
                    ))

        # 价格从上轨上方下穿上轨
        elif prev_price >= prev_upper and current_price < current_upper:
            position = portfolio.get_position(symbol)
            if position and position.quantity > 0:
                signals.append(Signal(
                    date=date,
                    symbol=symbol,
                    action='sell',
                    quantity=position.quantity,
                    price=current_price,
                    reason=f'布林带上轨突破'
                ))

    return signals


def macd_strategy(
    date, data: Dict[str, pd.DataFrame], portfolio,
    fast_period: int = 12, slow_period: int = 26, signal_period: int = 9, **kwargs
) -> List[Signal]:
    """
    MACD策略
    DIF上穿DEA时买入，下穿时卖出

    Args:
        fast_period: 快线周期
        slow_period: 慢线周期
        signal_period: 信号线周期

    Returns:
        Signal列表
    """
    signals = []
    buy_ratio = kwargs.get('buy_ratio', 1.0)

    for symbol, df in data.items():
        if len(df) < slow_period + signal_period:
            continue

        # 计算MACD
        ema_fast = df['close'].ewm(span=fast_period, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow_period, adjust=False).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal_period, adjust=False).mean()
        macd = (dif - dea) * 2

        current_dif = dif.iloc[-1]
        current_dea = dea.iloc[-1]
        prev_dif = dif.iloc[-2]
        prev_dea = dea.iloc[-2]
        current_price = df['close'].iloc[-1]

        # DIF上穿DEA（金叉）
        if prev_dif <= prev_dea and current_dif > current_dea:
            position = portfolio.get_position(symbol)
            if position is None or position.quantity == 0:
                available_cash = portfolio.cash * buy_ratio
                quantity = int(available_cash * 0.99 / (current_price * (1 + 0.0003 + 0.0001)))
                quantity = (quantity // 100) * 100
                if quantity >= 100:
                    signals.append(Signal(
                        date=date,
                        symbol=symbol,
                        action='buy',
                        quantity=quantity,
                        price=current_price,
                        reason=f'MACD金叉'
                    ))

        # DIF下穿DEA（死叉）
        elif prev_dif >= prev_dea and current_dif < current_dea:
            position = portfolio.get_position(symbol)
            if position and position.quantity > 0:
                signals.append(Signal(
                    date=date,
                    symbol=symbol,
                    action='sell',
                    quantity=position.quantity,
                    price=current_price,
                    reason=f'MACD死叉'
                ))

    return signals


def kdj_strategy(
    date, data: Dict[str, pd.DataFrame], portfolio,
    n: int = 9, m1: int = 3, m2: int = 3, **kwargs
) -> List[Signal]:
    """
    KDJ随机指标策略
    K线上穿D线时买入，下穿时卖出

    Args:
        n: RSV周期
        m1: K线周期
        m2: D线周期

    Returns:
        Signal列表
    """
    signals = []
    buy_ratio = kwargs.get('buy_ratio', 1.0)

    for symbol, df in data.items():
        if len(df) < n + m1 + m2:
            continue

        # 计算KDJ
        low_n = df['low'].rolling(window=n).min()
        high_n = df['high'].rolling(window=n).max()
        rsv = (df['close'] - low_n) / (high_n - low_n) * 100
        rsv = rsv.fillna(50)

        k = pd.Series(index=df.index, dtype=float)
        d = pd.Series(index=df.index, dtype=float)
        j = pd.Series(index=df.index, dtype=float)

        for i in range(len(df)):
            if i == 0:
                k.iloc[i] = 50
                d.iloc[i] = 50
            else:
                k.iloc[i] = (m1 - 1) / m1 * k.iloc[i-1] + 1 / m1 * rsv.iloc[i]
                d.iloc[i] = (m2 - 1) / m2 * d.iloc[i-1] + 1 / m2 * k.iloc[i]
            j.iloc[i] = 3 * k.iloc[i] - 2 * d.iloc[i]

        current_k = k.iloc[-1]
        current_d = d.iloc[-1]
        prev_k = k.iloc[-2]
        prev_d = d.iloc[-2]
        current_price = df['close'].iloc[-1]

        # K线上穿D线（金叉）
        if prev_k <= prev_d and current_k > current_d:
            position = portfolio.get_position(symbol)
            if position is None or position.quantity == 0:
                available_cash = portfolio.cash * buy_ratio
                quantity = int(available_cash * 0.99 / (current_price * (1 + 0.0003 + 0.0001)))
                quantity = (quantity // 100) * 100
                if quantity >= 100:
                    signals.append(Signal(
                        date=date,
                        symbol=symbol,
                        action='buy',
                        quantity=quantity,
                        price=current_price,
                        reason=f'KDJ金叉'
                    ))

        # K线下穿D线（死叉）
        elif prev_k >= prev_d and current_k < current_d:
            position = portfolio.get_position(symbol)
            if position and position.quantity > 0:
                signals.append(Signal(
                    date=date,
                    symbol=symbol,
                    action='sell',
                    quantity=position.quantity,
                    price=current_price,
                    reason=f'KDJ死叉'
                ))

    return signals


def dual_ma_rsi_strategy(
    date, data: Dict[str, pd.DataFrame], portfolio,
    ma_short: int = 5, ma_long: int = 20, rsi_period: int = 14,
    rsi_buy: int = 40, rsi_sell: int = 60, **kwargs
) -> List[Signal]:
    """
    双均线+RSI组合策略
    均线金叉且RSI确认时买入，死叉时卖出

    Args:
        ma_short: 短期均线周期
        ma_long: 长期均线周期
        rsi_period: RSI周期
        rsi_buy: RSI买入阈值
        rsi_sell: RSI卖出阈值

    Returns:
        Signal列表
    """
    signals = []
    buy_ratio = kwargs.get('buy_ratio', 1.0)

    for symbol, df in data.items():
        if len(df) < max(ma_long, rsi_period + 1):
            continue

        # 计算均线
        ma_s = df['close'].rolling(window=ma_short).mean()
        ma_l = df['close'].rolling(window=ma_long).mean()

        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        current_ma_s = ma_s.iloc[-1]
        current_ma_l = ma_l.iloc[-1]
        prev_ma_s = ma_s.iloc[-2]
        prev_ma_l = ma_l.iloc[-2]
        current_rsi = rsi.iloc[-1]
        current_price = df['close'].iloc[-1]

        # 金叉 + RSI确认
        if prev_ma_s <= prev_ma_l and current_ma_s > current_ma_l:
            position = portfolio.get_position(symbol)
            if position is None or position.quantity == 0:
                # RSI确认
                if current_rsi > rsi_buy:
                    available_cash = portfolio.cash * buy_ratio
                    quantity = int(available_cash * 0.99 / (current_price * (1 + 0.0003 + 0.0001)))
                    quantity = (quantity // 100) * 100
                    if quantity >= 100:
                        signals.append(Signal(
                            date=date,
                            symbol=symbol,
                            action='buy',
                            quantity=quantity,
                            price=current_price,
                            reason=f'双均线金叉+RSI确认: {current_rsi:.2f}'
                        ))

        # 死叉
        elif prev_ma_s >= prev_ma_l and current_ma_s < current_ma_l:
            position = portfolio.get_position(symbol)
            if position and position.quantity > 0:
                signals.append(Signal(
                    date=date,
                    symbol=symbol,
                    action='sell',
                    quantity=position.quantity,
                    price=current_price,
                    reason=f'双均线死叉'
                ))

    return signals


def kdj_bbi_strategy(
    date, data: Dict[str, pd.DataFrame], portfolio,
    kdj_n: int = 9, kdj_m1: int = 3, kdj_m2: int = 3,
    j_buy_threshold: float = 0, j_sell_half_threshold: float = 107, **kwargs
) -> List[Signal]:
    """
    KDJ+BBI组合策略
    J值<0时买入，J值>107时卖出一半，跌破BBI时清仓

    Args:
        kdj_n: KDJ周期N
        kdj_m1: KDJ周期M1
        kdj_m2: KDJ周期M2
        j_buy_threshold: J值买入阈值
        j_sell_half_threshold: J值卖出一半阈值

    Returns:
        Signal列表
    """
    signals = []

    for symbol, df in data.items():
        if len(df) < max(kdj_n + kdj_m1 + kdj_m2, 20):
            continue

        # 计算KDJ
        low_n = df['low'].rolling(window=kdj_n).min()
        high_n = df['high'].rolling(window=kdj_n).max()
        rsv = (df['close'] - low_n) / (high_n - low_n) * 100
        rsv = rsv.fillna(50)

        k = pd.Series(index=df.index, dtype=float)
        d = pd.Series(index=df.index, dtype=float)
        j = pd.Series(index=df.index, dtype=float)

        for i in range(len(df)):
            if i == 0:
                k.iloc[i] = 50
                d.iloc[i] = 50
            else:
                k.iloc[i] = (kdj_m1 - 1) / kdj_m1 * k.iloc[i-1] + 1 / kdj_m1 * rsv.iloc[i]
                d.iloc[i] = (kdj_m2 - 1) / kdj_m2 * d.iloc[i-1] + 1 / kdj_m2 * k.iloc[i]
            j.iloc[i] = 3 * k.iloc[i] - 2 * d.iloc[i]

        # 计算BBI
        bbi = (df['close'].rolling(window=3).mean() +
               df['close'].rolling(window=6).mean() +
               df['close'].rolling(window=12).mean() +
               df['close'].rolling(window=24).mean()) / 4

        current_j = j.iloc[-1]
        prev_j = j.iloc[-2]
        current_price = df['close'].iloc[-1]
        current_bbi = bbi.iloc[-1]
        prev_price = df['close'].iloc[-2]
        position = portfolio.get_position(symbol)

        # J值<0买入
        if current_j < j_buy_threshold and (position is None or position.quantity == 0):
            buy_ratio = kwargs.get('buy_ratio', 1.0)
            available_cash = portfolio.cash * buy_ratio
            quantity = int(available_cash * 0.99 / (current_price * (1 + 0.0003 + 0.0001)))
            quantity = (quantity // 100) * 100
            if quantity >= 100:
                signals.append(Signal(
                    date=date,
                    symbol=symbol,
                    action='buy',
                    quantity=quantity,
                    price=current_price,
                    reason=f'KDJ J值低于{j_buy_threshold}: {current_j:.2f}'
                ))

        # J值>107卖出一半
        elif current_j > j_sell_half_threshold and position and position.quantity > 0:
            half_quantity = position.quantity // 2
            if half_quantity >= 100:
                signals.append(Signal(
                    date=date,
                    symbol=symbol,
                    action='sell',
                    quantity=half_quantity,
                    price=current_price,
                    reason=f'KDJ J值高于{j_sell_half_threshold}: {current_j:.2f}'
                ))

        # 跌破BBI清仓
        elif prev_price > prev(bbi, 2) and current_price < current_bbi:
            if position and position.quantity > 0:
                signals.append(Signal(
                    date=date,
                    symbol=symbol,
                    action='sell',
                    quantity=position.quantity,
                    price=current_price,
                    reason='跌破BBI清仓'
                ))

    return signals


def prev(series: pd.Series, n: int = 1) -> float:
    """获取n天前的值"""
    return series.iloc[-n-1] if len(series) > n else series.iloc[0]


# 策略注册表
_STRATEGIES: Dict[str, Callable] = {
    'ma_cross': ma_cross_strategy,
    'rsi': rsi_strategy,
    'bollinger': bollinger_strategy,
    'macd': macd_strategy,
    'kdj': kdj_strategy,
    'dual_ma_rsi': dual_ma_rsi_strategy,
    'kdj_bbi': kdj_bbi_strategy,
}


def list_strategies() -> List[str]:
    """
    获取所有可用策略名称

    Returns:
        策略名称列表
    """
    return list(_STRATEGIES.keys())


def get_strategy(name: str) -> Callable:
    """
    获取指定名称的策略函数

    Args:
        name: 策略名称

    Returns:
        策略函数，不存在则返回None
    """
    return _STRATEGIES.get(name)


if __name__ == "__main__":
    # 测试策略
    print("=" * 60)
    print("可用策略列表")
    print("=" * 60)

    for name in list_strategies():
        print(f"  - {name}")

    print("\n策略总数:", len(list_strategies()))
