#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标计算工具库
Financial Analysis Expert - Technical Indicators Module
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple, List


class TechnicalIndicators:
    """技术指标计算类"""

    @staticmethod
    def sma(series: pd.Series, period: int) -> pd.Series:
        """简单移动平均线 (SMA)"""
        return series.rolling(window=period).mean()

    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        """指数移动平均线 (EMA)"""
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def macd(
        series: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD指标
        返回: (DIF, DEA, MACD柱)
        """
        ema_fast = series.ewm(span=fast_period, adjust=False).mean()
        ema_slow = series.ewm(span=slow_period, adjust=False).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal_period, adjust=False).mean()
        bar = 2 * (dif - dea)
        return dif, dea, bar

    @staticmethod
    def kdj(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 9,
        k_period: int = 3,
        d_period: int = 3
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        KDJ随机指标
        返回: (K, D, J)
        """
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()

        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        rsv = rsv.fillna(50)

        k = rsv.ewm(com=k_period - 1, adjust=False).mean()
        d = k.ewm(com=d_period - 1, adjust=False).mean()
        j = 3 * k - 2 * d

        return k, d, j

    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """
        RSI相对强弱指标
        """
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        # 使用指数移动平均进行平滑
        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.fillna(50)

        return rsi

    @staticmethod
    def bollinger_bands(
        series: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        布林带指标
        返回: (上轨, 中轨, 下轨)
        """
        middle = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower

    @staticmethod
    def atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        ATR平均真实波幅
        """
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr

    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        OBV能量潮
        """
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]

        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i - 1]

        return obv

    @staticmethod
    def cci(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        CCI商品通道指数
        """
        tp = (high + low + close) / 3
        sma_tp = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(
            lambda x: np.abs(x - x.mean()).mean()
        )
        cci = (tp - sma_tp) / (mad * 0.015)
        return cci

    @staticmethod
    def williams_r(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        威廉指标
        """
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()

        wr = -100 * (highest_high - close) / (highest_high - lowest_low)
        return wr

    @staticmethod
    def adx(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        ADX平均趋向指数
        返回: (ADX, +DI, -DI)
        """
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        tr = pd.concat([
            high - low,
            abs(high - close.shift(1)),
            abs(low - close.shift(1))
        ], axis=1).max(axis=1)

        plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx, plus_di, minus_di


class TradingSignals:
    """交易信号生成类"""

    @staticmethod
    def ma_cross(
        short_ma: pd.Series,
        long_ma: pd.Series
    ) -> pd.DataFrame:
        """
        均线交叉信号
        """
        signals = pd.DataFrame(index=short_ma.index)
        signals['position'] = 0
        signals.loc[short_ma > long_ma, 'position'] = 1
        signals.loc[short_ma <= long_ma, 'position'] = -1

        signals['signal'] = signals['position'].diff()
        # signal = 1: 金叉买入
        # signal = -1: 死叉卖出

        return signals

    @staticmethod
    def macd_signals(
        dif: pd.Series,
        dea: pd.Series,
        macd_bar: pd.Series
    ) -> pd.DataFrame:
        """
        MACD交易信号
        """
        signals = pd.DataFrame(index=dif.index)

        # 金叉死叉
        signals['cross'] = 0
        signals.loc[(dif > dea) & (dif.shift(1) <= dea.shift(1)), 'cross'] = 1
        signals.loc[(dif < dea) & (dif.shift(1) >= dea.shift(1)), 'cross'] = -1

        # 零轴交叉
        signals['zero_cross'] = 0
        signals.loc[(dif > 0) & (dif.shift(1) <= 0), 'zero_cross'] = 1
        signals.loc[(dif < 0) & (dif.shift(1) >= 0), 'zero_cross'] = -1

        # 柱状图转势
        signals['bar_change'] = 0
        signals.loc[(macd_bar > 0) & (macd_bar.shift(1) <= 0), 'bar_change'] = 1
        signals.loc[(macd_bar < 0) & (macd_bar.shift(1) >= 0), 'bar_change'] = -1

        return signals

    @staticmethod
    def kdj_signals(
        k: pd.Series,
        d: pd.Series,
        j: pd.Series
    ) -> pd.DataFrame:
        """
        KDJ交易信号
        """
        signals = pd.DataFrame(index=k.index)

        # 金叉死叉
        signals['cross'] = 0
        signals.loc[(k > d) & (k.shift(1) <= d.shift(1)), 'cross'] = 1
        signals.loc[(k < d) & (k.shift(1) >= d.shift(1)), 'cross'] = -1

        # 超买超卖
        signals['level'] = 'neutral'
        signals.loc[(k < 20) & (d < 20), 'level'] = 'oversold'
        signals.loc[(k > 80) & (d > 80), 'level'] = 'overbought'

        # J值极端
        signals['j_extreme'] = 0
        signals.loc[j < -20, 'j_extreme'] = 1  # 超卖极端
        signals.loc[j > 100, 'j_extreme'] = -1  # 超买极端

        return signals

    @staticmethod
    def rsi_signals(rsi: pd.Series) -> pd.DataFrame:
        """
        RSI交易信号
        """
        signals = pd.DataFrame(index=rsi.index)

        signals['rsi'] = rsi
        signals['level'] = 'neutral'

        signals.loc[rsi < 30, 'level'] = 'oversold'
        signals.loc[rsi > 70, 'level'] = 'overbought'

        # RSI反转信号
        signals['reversal'] = 0
        signals.loc[(rsi < 30) & (rsi > rsi.shift(1)), 'reversal'] = 1
        signals.loc[(rsi > 70) & (rsi < rsi.shift(1)), 'reversal'] = -1

        return signals


def calculate_all_indicators(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series = None
) -> pd.DataFrame:
    """
    计算所有常用技术指标
    """
    indicators = TechnicalIndicators()

    result = pd.DataFrame(index=close.index)

    # 均线
    result['ma5'] = indicators.sma(close, 5)
    result['ma10'] = indicators.sma(close, 10)
    result['ma20'] = indicators.sma(close, 20)
    result['ma60'] = indicators.sma(close, 60)

    # EMA
    result['ema12'] = indicators.ema(close, 12)
    result['ema26'] = indicators.ema(close, 26)

    # MACD
    dif, dea, bar = indicators.macd(close)
    result['macd_dif'] = dif
    result['macd_dea'] = dea
    result['macd_bar'] = bar

    # KDJ
    if volume is not None:
        k, d, j = indicators.kdj(high, low, close)
        result['kdj_k'] = k
        result['kdj_d'] = d
        result['kdj_j'] = j

    # RSI
    result['rsi'] = indicators.rsi(close, 14)

    # 布林带
    upper, middle, lower = indicators.bollinger_bands(close)
    result['bb_upper'] = upper
    result['bb_middle'] = middle
    result['bb_lower'] = lower

    # ATR
    result['atr'] = indicators.atr(high, low, close)

    # CCI
    result['cci'] = indicators.cci(high, low, close)

    # 威廉指标
    result['wr'] = indicators.williams_r(high, low, close)

    return result


# 使用示例
if __name__ == "__main__":
    # 示例数据
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2024-01-01", periods=n)

    close = pd.Series(100 + np.cumsum(np.random.randn(n) * 2), index=dates)
    high = close + np.random.rand(n) * 5
    low = close - np.random.rand(n) * 5
    volume = pd.Series(np.random.randint(1000000, 10000000, n), index=dates)

    # 计算所有指标
    df = calculate_all_indicators(high, low, close, volume)
    print("技术指标计算完成")
    print(df.tail(10))
