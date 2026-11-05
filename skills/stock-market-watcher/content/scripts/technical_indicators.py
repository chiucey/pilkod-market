"""
股票技术指标计算模块
实现布林线、CCI、MACD、EXPMA等常用技术指标
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class TechnicalIndicators:
    """技术指标计算类"""

    def __init__(self, prices: List[float], highs: List[float] = None,
                 lows: List[float] = None, volumes: List[float] = None):
        """
        初始化技术指标计算器

        Args:
            prices: 收盘价列表
            highs: 最高价列表（可选）
            lows: 最低价列表（可选）
            volumes: 成交量列表（可选）
        """
        self.prices = np.array(prices)
        self.highs = np.array(highs) if highs else None
        self.lows = np.array(lows) if lows else None
        self.volumes = np.array(volumes) if volumes else None

    def sma(self, period: int = 20) -> np.ndarray:
        """
        简单移动平均线 (SMA)

        Args:
            period: 计算周期

        Returns:
            SMA数组
        """
        if len(self.prices) < period:
            return np.full(len(self.prices), np.nan)

        return np.array([
            np.mean(self.prices[i:i+period])
            for i in range(len(self.prices) - period + 1)
        ])

    def ema(self, period: int = 12) -> np.ndarray:
        """
        指数加权移动平均线 (EMA)

        Args:
            period: 计算周期

        Returns:
            EMA数组
        """
        if len(self.prices) < period:
            return np.full(len(self.prices), np.nan)

        alpha = 2 / (period + 1)
        ema_values = [self.prices[0]]

        for i in range(1, len(self.prices)):
            ema_values.append(alpha * self.prices[i] + (1 - alpha) * ema_values[-1])

        return np.array(ema_values)

    def bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> Dict[str, np.ndarray]:
        """
        布林线指标

        Args:
            period: 移动平均周期
            std_dev: 标准差倍数

        Returns:
            包含中轨、上轨、下轨的字典
        """
        if len(self.prices) < period:
            return {
                'middle': np.array([]),
                'upper': np.array([]),
                'lower': np.array([]),
                'bandwidth': np.array([]),
                'position': []
            }

        middle = self.sma(period)

        # 计算滚动标准差
        rolling_std = np.array([
            np.std(self.prices[i:i+period])
            for i in range(len(self.prices) - period + 1)
        ])

        upper = middle + std_dev * rolling_std
        lower = middle - std_dev * rolling_std

        # 布林带宽度
        bandwidth = (upper - lower) / middle * 100

        # 当前价格在布林带的位置
        current_price = self.prices[-1]
        current_upper = upper[-1] if len(upper) > 0 else None
        current_lower = lower[-1] if len(lower) > 0 else None
        current_middle = middle[-1] if len(middle) > 0 else None

        if current_upper and current_lower and current_middle:
            if current_price > current_upper:
                position = "突破上轨"
            elif current_price < current_lower:
                position = "跌破下轨"
            elif current_price > current_middle:
                position = "中轨上方"
            else:
                position = "中轨下方"
        else:
            position = "数据不足"

        return {
            'middle': middle,
            'upper': upper,
            'lower': lower,
            'bandwidth': bandwidth,
            'position': position,
            'current': {
                'upper': current_upper,
                'middle': current_middle,
                'lower': current_lower
            }
        }

    def cci(self, period: int = 14) -> Dict[str, any]:
        """
        顺势指标 (CCI)

        Args:
            period: 计算周期

        Returns:
            CCI值及相关信号
        """
        if self.highs is None or self.lows is None or len(self.prices) < period:
            return {
                'cci': np.array([]),
                'signal': "数据不足",
                'current': None
            }

        typical_prices = (self.highs + self.lows + self.prices) / 3

        if len(typical_prices) < period:
            return {
                'cci': np.array([]),
                'signal': "数据不足",
                'current': None
            }

        # 计算典型价格的SMA
        tp_sma = np.array([
            np.mean(typical_prices[i:i+period])
            for i in range(len(typical_prices) - period + 1)
        ])

        # 计算平均绝对偏差
        mean_deviation = np.array([
            np.mean(np.abs(typical_prices[i:i+period] - tp_sma[i]))
            for i in range(len(typical_prices) - period + 1)
        ])

        # 计算CCI
        cci = np.zeros(len(tp_sma))
        for i in range(len(tp_sma)):
            if mean_deviation[i] != 0:
                cci[i] = (typical_prices[period-1+i] - tp_sma[i]) / (0.015 * mean_deviation[i])

        current_cci = cci[-1] if len(cci) > 0 else None

        # CCI信号判断
        if current_cci is not None:
            if current_cci > 100:
                signal = "超买区"
            elif current_cci < -100:
                signal = "超卖区"
            else:
                signal = "正常区间"
        else:
            signal = "数据不足"

        return {
            'cci': cci,
            'signal': signal,
            'current': current_cci,
            'overbought': 100,
            'oversold': -100
        }

    def macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, np.ndarray]:
        """
        MACD指标

        Args:
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            包含DIF、DEA、MACD柱及信号
        """
        if len(self.prices) < slow:
            return {
                'dif': np.array([]),
                'dea': np.array([]),
                'histogram': np.array([]),
                'signal': "数据不足",
                'crossover': None,
                'current': {}
            }

        # 计算EMA
        ema_fast = self.ema(fast)
        ema_slow = self.ema(slow)

        # 计算DIF
        min_len = min(len(ema_fast), len(ema_slow))
        dif = ema_fast[:min_len] - ema_slow[:min_len]

        # 计算DEA（信号线）
        if len(dif) < signal:
            return {
                'dif': np.array([]),
                'dea': np.array([]),
                'histogram': np.array([]),
                'signal': "数据不足",
                'crossover': None,
                'current': {}
            }

        dea = np.array(dif[:signal].tolist())
        for i in range(signal, len(dif)):
            dea = np.append(dea, dea[-1] * (2/10) + dif[i] * (8/10))

        # 计算MACD柱
        histogram = (dif[:len(dea)] - dea) * 2

        # 判断金叉/死叉
        current_dif = dif[-1] if len(dif) > 0 else None
        current_dea = dea[-1] if len(dea) > 0 else None

        if len(dif) >= 2:
            if dif[-1] > dea[-1] and dif[-2] <= dea[-2]:
                crossover = "金叉"
            elif dif[-1] < dea[-1] and dif[-2] >= dea[-2]:
                crossover = "死叉"
            elif dif[-1] > dea[-1]:
                crossover = "多头排列"
            else:
                crossover = "空头排列"
        else:
            crossover = "数据不足"

        return {
            'dif': dif,
            'dea': dea,
            'histogram': histogram,
            'signal': crossover,
            'crossover': crossover,
            'current': {
                'dif': current_dif,
                'dea': current_dea,
                'histogram': histogram[-1] if len(histogram) > 0 else None
            }
        }

    def expma(self, short: int = 12, long: int = 50) -> Dict[str, np.ndarray]:
        """
        EXPMA指数加权移动平均

        Args:
            short: 短期周期
            long: 长期周期

        Returns:
            短期EXPMA、长期EXPMA及排列信号
        """
        if len(self.prices) < long:
            return {
                'expma_short': np.array([]),
                'expma_long': np.array([]),
                'signal': "数据不足",
                'crossover': None,
                'current': {}
            }

        expma_short = self.ema(short)
        expma_long = self.ema(long)

        min_len = min(len(expma_short), len(expma_long))
        short_trimmed = expma_short[:min_len]
        long_trimmed = expma_long[:min_len]

        # 判断多空排列
        if len(short_trimmed) >= 2:
            if short_trimmed[-1] > long_trimmed[-1] and short_trimmed[-2] <= long_trimmed[-2]:
                crossover = "短期线上穿长期线"
            elif short_trimmed[-1] < long_trimmed[-1] and short_trimmed[-2] >= long_trimmed[-2]:
                crossover = "短期线下穿长期线"
            elif short_trimmed[-1] > long_trimmed[-1]:
                crossover = "多头排列"
            else:
                crossover = "空头排列"
        else:
            crossover = "数据不足"

        return {
            'expma_short': short_trimmed,
            'expma_long': long_trimmed,
            'signal': crossover,
            'crossover': crossover,
            'current': {
                'short': short_trimmed[-1] if len(short_trimmed) > 0 else None,
                'long': long_trimmed[-1] if len(long_trimmed) > 0 else None
            }
        }

    def get_all_indicators(self) -> Dict[str, Dict]:
        """
        获取所有技术指标

        Returns:
            包含所有指标的字典
        """
        return {
            'bollinger_bands': self.bollinger_bands(),
            'cci': self.cci(),
            'macd': self.macd(),
            'expma': self.expma()
        }


def calculate_all_for_stock(historical_data: List[Dict]) -> Dict:
    """
    计算股票的所有技术指标

    Args:
        historical_data: 历史行情数据列表，每项包含 high, low, close, volume

    Returns:
        所有指标计算结果
    """
    if not historical_data or len(historical_data) < 50:
        return {
            'error': '数据不足，至少需要50个交易日数据',
            'required': 50,
            'provided': len(historical_data) if historical_data else 0
        }

    closes = [d['close'] for d in historical_data]
    highs = [d['high'] for d in historical_data]
    lows = [d['low'] for d in historical_data]
    volumes = [d.get('volume', 0) for d in historical_data]

    ti = TechnicalIndicators(closes, highs, lows, volumes)
    indicators = ti.get_all_indicators()

    return {
        'indicators': indicators,
        'current_price': closes[-1],
        'data_count': len(historical_data),
        'timestamp': historical_data[-1].get('date', 'unknown')
    }


if __name__ == "__main__":
    # 测试代码
    import random

    # 模拟50天数据
    test_data = []
    price = 100
    for i in range(60):
        price = price * (1 + random.uniform(-0.02, 0.025))
        test_data.append({
            'date': f'2024-01-{i+1:02d}',
            'open': price * 0.99,
            'high': price * 1.02,
            'low': price * 0.98,
            'close': price,
            'volume': random.randint(1000000, 5000000)
        })

    result = calculate_all_for_stock(test_data)
    print("技术指标计算结果：")
    print(f"当前价格: {result['current_price']:.2f}")
    print(f"数据量: {result['data_count']}")
    print(f"\n布林线: {result['indicators']['bollinger_bands']['position']}")
    print(f"CCI: {result['indicators']['cci']['current']:.2f} ({result['indicators']['cci']['signal']})")
    print(f"MACD: {result['indicators']['macd']['crossover']}")
    print(f"EXPMA: {result['indicators']['expma']['crossover']}")
