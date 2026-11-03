#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术分析脚本 - 计算各种技术指标和交易信号

支持指标：
- 移动平均线 (MA)
- 指数移动平均线 (EMA)
- MACD
- RSI
- KDJ
- 布林带 (Bollinger Bands)
- 威廉指标 (Williams %R)
- OBV 能量潮

用法：
    from analysis import TechnicalAnalyzer
    analyzer = TechnicalAnalyzer()
    result = analyzer.analyze(price_data)
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class TechnicalAnalyzer:
    """技术分析器"""

    def __init__(self):
        self.default_periods = {
            "short": 5,
            "medium": 20,
            "long": 60,
            "extra_long": 250
        }

    def calculate_ma(self, prices: List[float], period: int) -> List[float]:
        """
        计算简单移动平均线 (SMA)

        Args:
            prices: 价格列表
            period: 周期

        Returns:
            List[float]: MA值列表
        """
        if len(prices) < period:
            return [None] * len(prices)

        ma = []
        for i in range(len(prices)):
            if i < period - 1:
                ma.append(None)
            else:
                ma.append(sum(prices[i - period + 1:i + 1]) / period)
        return ma

    def calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """
        计算指数移动平均线 (EMA)

        Args:
            prices: 价格列表
            period: 周期

        Returns:
            List[float]: EMA值列表
        """
        if len(prices) < period:
            return [None] * len(prices)

        multiplier = 2 / (period + 1)
        ema = [None] * (period - 1)
        ema.append(sum(prices[:period]) / period)

        for i in range(period, len(prices)):
            ema.append((prices[i] - ema[-1]) * multiplier + ema[-1])

        return ema

    def calculate_macd(self, prices: List[float], fast: int = 12,
                       slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
        """
        计算MACD指标

        Args:
            prices: 价格列表
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            Dict: 包含DIF, DEA, MACD柱的值
        """
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)

        # DIF = EMA_fast - EMA_slow
        dif = []
        for i in range(len(prices)):
            if ema_fast[i] is None or ema_slow[i] is None:
                dif.append(None)
            else:
                dif.append(ema_fast[i] - ema_slow[i])

        # DEA = EMA(DIF, signal)
        dea = self.calculate_ema([d if d else 0 for d in dif], signal)

        # MACD柱 = (DIF - DEA) * 2
        macd_hist = []
        for i in range(len(prices)):
            if dif[i] is None or dea[i] is None:
                macd_hist.append(None)
            else:
                macd_hist.append((dif[i] - dea[i]) * 2)

        return {
            "dif": dif,
            "dea": dea,
            "macd_hist": macd_hist
        }

    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """
        计算相对强弱指标 (RSI)

        Args:
            prices: 价格列表
            period: 周期

        Returns:
            List[float]: RSI值列表
        """
        if len(prices) < period + 1:
            return [None] * len(prices)

        rsi = [None] * period

        # 计算初始涨跌幅
        gains = []
        losses = []
        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))

        # 计算平均涨跌幅
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        # 计算RSI
        for i in range(period, len(gains)):
            if i == period:
                rs = avg_gain / avg_loss if avg_loss != 0 else 100
            else:
                rs = ((rsi[-1] / 100 * (period - 1) + gains[i]) / period) / \
                     ((100 - rsi[-1]) / 100 * (period - 1) + losses[i]) * period \
                     if losses[i] != 0 else 100

            rsi_value = 100 - (100 / (1 + rs)) if rs != 0 else 100
            rsi.append(rsi_value)

        rsi.append(None)  # 最后一个位置
        return rsi

    def calculate_kdj(self, prices_high: List[float], prices_low: List[float],
                       prices_close: List[float], period: int = 9) -> Dict[str, List[float]]:
        """
        计算KDJ随机指标

        Args:
            prices_high: 最高价列表
            prices_low: 最低价列表
            prices_close: 收盘价列表
            period: 周期

        Returns:
            Dict: 包含K, D, J的值
        """
        if len(prices_high) < period:
            return {"k": [None] * len(prices_high),
                    "d": [None] * len(prices_high),
                    "j": [None] * len(prices_high)}

        k = [50.0]  # 初始K值
        d = [50.0]  # 初始D值

        for i in range(1, len(prices_close)):
            if i < period - 1:
                k.append(50.0)
                d.append(50.0)
            else:
                # 计算RSV
                recent_high = max(prices_high[i - period + 1:i + 1])
                recent_low = min(prices_low[i - period + 1:i + 1])

                if recent_high == recent_low:
                    rsv = 50
                else:
                    rsv = (prices_close[i] - recent_low) / (recent_high - recent_low) * 100

                # 计算K和D
                k_value = 2 / 3 * k[-1] + 1 / 3 * rsv
                d_value = 2 / 3 * d[-1] + 1 / 3 * k_value

                k.append(k_value)
                d.append(d_value)

        # 计算J值: J = 3K - 2D
        j = []
        for i in range(len(k)):
            if k[i] is None or d[i] is None:
                j.append(None)
            else:
                j.append(3 * k[i] - 2 * d[i])

        return {
            "k": k,
            "d": d,
            "j": j
        }

    def calculate_bollinger_bands(self, prices: List[float],
                                  period: int = 20,
                                  std_dev: float = 2.0) -> Dict[str, List[float]]:
        """
        计算布林带

        Args:
            prices: 价格列表
            period: 周期
            std_dev: 标准差倍数

        Returns:
            Dict: 包含upper, middle, lower的值
        """
        middle = self.calculate_ma(prices, period)

        upper = []
        lower = []

        for i in range(len(prices)):
            if middle[i] is None:
                upper.append(None)
                lower.append(None)
            else:
                # 计算标准差
                slice_prices = prices[max(0, i - period + 1):i + 1]
                mean = middle[i]
                variance = sum((p - mean) ** 2 for p in slice_prices) / len(slice_prices)
                std = math.sqrt(variance)

                upper.append(middle[i] + std_dev * std)
                lower.append(middle[i] - std_dev * std)

        return {
            "upper": upper,
            "middle": middle,
            "lower": lower
        }

    def calculate_obv(self, prices_close: List[float],
                      volumes: List[int]) -> List[float]:
        """
        计算OBV能量潮

        Args:
            prices_close: 收盘价列表
            volumes: 成交量列表

        Returns:
            List[float]: OBV值列表
        """
        if len(prices_close) != len(volumes):
            raise ValueError("价格和成交量长度不匹配")

        obv = [0.0]

        for i in range(1, len(prices_close)):
            if prices_close[i] > prices_close[i - 1]:
                obv.append(obv[-1] + volumes[i])
            elif prices_close[i] < prices_close[i - 1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])

        return obv

    def analyze(self, price_data: Dict) -> Dict:
        """
        综合技术分析

        Args:
            price_data: 价格数据，格式为:
                {
                    "dates": [...],
                    "open": [...],
                    "high": [...],
                    "low": [...],
                    "close": [...],
                    "volume": [...]
                }

        Returns:
            Dict: 技术分析结果
        """
        if not price_data or not price_data.get("success"):
            return {"success": False, "error": "无有效价格数据"}

        data = price_data.get("data", {})
        if not data or "close" not in data:
            return {"success": False, "error": "缺少收盘价数据"}

        close = data["close"]
        high = data.get("high", close)
        low = data.get("low", close)
        volume = data.get("volume", [0] * len(close))

        result = {
            "success": True,
            "symbol": price_data.get("symbol", ""),
            "analysis_date": datetime.now().isoformat(),
            "period": price_data.get("period", "unknown"),
            "indicators": {},
            "signals": {},
            "trend": {},
            "summary": {}
        }

        # 计算各周期均线
        ma_periods = [5, 10, 20, 60, 120, 250]
        ma_values = {}

        for period in ma_periods:
            if len(close) >= period:
                ma_values[f"ma{period}"] = self.calculate_ma(close, period)

        result["indicators"]["ma"] = ma_values

        # 计算MACD
        macd = self.calculate_macd(close)
        result["indicators"]["macd"] = macd

        # 计算RSI
        rsi_6 = self.calculate_rsi(close, 6)
        rsi_12 = self.calculate_rsi(close, 12)
        rsi_24 = self.calculate_rsi(close, 24)
        result["indicators"]["rsi"] = {
            "rsi6": rsi_6,
            "rsi12": rsi_12,
            "rsi24": rsi_24
        }

        # 计算KDJ
        kdj = self.calculate_kdj(high, low, close)
        result["indicators"]["kdj"] = kdj

        # 计算布林带
        bb = self.calculate_bollinger_bands(close, 20, 2.0)
        result["indicators"]["bollinger"] = bb

        # 生成交易信号
        signals = self._generate_signals(result["indicators"], close, volume)
        result["signals"] = signals

        # 判断趋势
        trend = self._analyze_trend(ma_values, close)
        result["trend"] = trend

        # 生成分析摘要
        summary = self._generate_summary(result["indicators"], signals, trend)
        result["summary"] = summary

        return result

    def _generate_signals(self, indicators: Dict, close: List[float],
                         volume: List[int]) -> Dict:
        """生成交易信号"""
        signals = {}

        # MACD信号
        macd = indicators.get("macd", {})
        dif = macd.get("dif", [])
        dea = macd.get("dea", [])
        hist = macd.get("macd_hist", [])

        if len(dif) >= 2 and dif[-1] is not None and dea[-1] is not None:
            # 金叉/死叉
            if dif[-1] > dea[-1] and dif[-2] <= dea[-2]:
                signals["macd_cross"] = {"signal": "golden_cross", "type": "bullish"}
            elif dif[-1] < dea[-1] and dif[-2] >= dea[-2]:
                signals["macd_cross"] = {"signal": "death_cross", "type": "bearish"}
            else:
                signals["macd_cross"] = {"signal": "hold", "type": "neutral"}

            # MACD柱变化
            if hist[-1] and hist[-1] > 0:
                signals["macd_histogram"] = {"value": hist[-1], "type": "bullish"}
            else:
                signals["macd_histogram"] = {"value": hist[-1], "type": "bearish"}

        # RSI信号
        rsi = indicators.get("rsi", {})
        rsi_14 = rsi.get("rsi14", rsi.get("rsi12", [None] * len(close)))

        if rsi_14[-1] is not None:
            if rsi_14[-1] > 70:
                signals["rsi"] = {"value": rsi_14[-1], "signal": "overbought", "type": "bearish"}
            elif rsi_14[-1] < 30:
                signals["rsi"] = {"value": rsi_14[-1], "signal": "oversold", "type": "bullish"}
            else:
                signals["rsi"] = {"value": rsi_14[-1], "signal": "neutral", "type": "neutral"}

        # KDJ信号
        kdj = indicators.get("kdj", {})
        k = kdj.get("k", [])
        d = kdj.get("d", [])
        j = kdj.get("j", [])

        if len(k) >= 2 and k[-1] is not None:
            if k[-1] > d[-1] and k[-2] <= d[-2]:
                signals["kdj_cross"] = {"signal": "golden_cross", "type": "bullish"}
            elif k[-1] < d[-1] and k[-2] >= d[-2]:
                signals["kdj_cross"] = {"signal": "death_cross", "type": "bearish"}
            else:
                signals["kdj_cross"] = {"signal": "hold", "type": "neutral"}

            if j[-1] is not None:
                if j[-1] > 100:
                    signals["kdj"] = {"j": j[-1], "signal": "overbought", "type": "bearish"}
                elif j[-1] < 0:
                    signals["kdj"] = {"j": j[-1], "signal": "oversold", "type": "bullish"}
                else:
                    signals["kdj"] = {"j": j[-1], "signal": "neutral", "type": "neutral"}

        # 布林带信号
        bb = indicators.get("bollinger", {})
        upper = bb.get("upper", [])
        lower = bb.get("lower", [])

        if len(close) >= 2 and len(upper) > 0 and upper[-1] is not None:
            if close[-1] > upper[-1]:
                signals["bollinger"] = {"signal": "break_upper", "type": "bullish"}
            elif close[-1] < lower[-1]:
                signals["bollinger"] = {"signal": "break_lower", "type": "bearish"}
            else:
                signals["bollinger"] = {"signal": "within_bands", "type": "neutral"}

        # 成交量信号
        if len(volume) >= 5:
            avg_vol = sum(volume[-5:]) / 5
            if volume[-1] > avg_vol * 1.5:
                signals["volume"] = {"signal": "volume_surge", "type": "bullish"}
            elif volume[-1] < avg_vol * 0.5:
                signals["volume"] = {"signal": "volume_shrink", "type": "neutral"}
            else:
                signals["volume"] = {"signal": "normal", "type": "neutral"}

        # 综合评分
        bullish_count = sum(1 for s in signals.values()
                          if isinstance(s, dict) and s.get("type") == "bullish")
        bearish_count = sum(1 for s in signals.values()
                          if isinstance(s, dict) and s.get("type") == "bearish")

        if bullish_count > bearish_count + 2:
            signals["overall"] = {"score": "strong_bullish", "bullish": bullish_count,
                                 "bearish": bearish_count}
        elif bullish_count > bearish_count:
            signals["overall"] = {"score": "bullish", "bullish": bullish_count,
                                 "bearish": bearish_count}
        elif bearish_count > bullish_count + 2:
            signals["overall"] = {"score": "strong_bearish", "bullish": bullish_count,
                                 "bearish": bearish_count}
        elif bearish_count > bullish_count:
            signals["overall"] = {"score": "bearish", "bullish": bullish_count,
                                 "bearish": bearish_count}
        else:
            signals["overall"] = {"score": "neutral", "bullish": bullish_count,
                                 "bearish": bearish_count}

        return signals

    def _analyze_trend(self, ma_values: Dict, close: List[float]) -> Dict:
        """分析趋势"""
        if not ma_values or not close:
            return {"trend": "unknown", "strength": 0}

        ma5 = ma_values.get("ma5", [None] * len(close))
        ma10 = ma_values.get("ma10", [None] * len(close))
        ma20 = ma_values.get("ma20", [None] * len(close))
        ma60 = ma_values.get("ma60", [None] * len(close))
        ma120 = ma_values.get("ma120", [None] * len(close))

        current_price = close[-1] if close else None

        # 判断均线多头/空头排列
        if all(v[-1] is not None for v in [ma5, ma10, ma20, ma60, ma120]):
            if ma5[-1] > ma10[-1] > ma20[-1] > ma60[-1] > ma120[-1]:
                trend = "strong_uptrend"
            elif ma5[-1] > ma10[-1] > ma20[-1]:
                trend = "uptrend"
            elif ma5[-1] < ma10[-1] < ma20[-1] < ma60[-1] < ma120[-1]:
                trend = "strong_downtrend"
            elif ma5[-1] < ma10[-1] < ma20[-1]:
                trend = "downtrend"
            else:
                trend = "sideways"
        else:
            trend = "insufficient_data"

        # 计算趋势强度
        strength = 0
        if current_price and ma5[-1]:
            price_above_ma = sum(1 for ma in [ma5, ma10, ma20, ma60, ma120]
                              if ma[-1] and current_price > ma[-1])
            strength = price_above_ma / 5 * 100

        # 判断位置
        position = "above_ma" if current_price and ma20[-1] and current_price > ma20[-1] else "below_ma"

        return {
            "trend": trend,
            "strength": round(strength, 2),
            "current_price": current_price,
            "position": position
        }

    def _generate_summary(self, indicators: Dict, signals: Dict,
                         trend: Dict) -> Dict:
        """生成分析摘要"""
        summary = {
            "trend": trend.get("trend", "unknown"),
            "strength": trend.get("strength", 0),
            "overall_signal": signals.get("overall", {}).get("score", "neutral"),
            "key_signals": [],
            "recommendation": "持有"
        }

        # 收集关键信号
        if signals.get("macd_cross"):
            summary["key_signals"].append(f"MACD: {signals['macd_cross']['signal']}")
        if signals.get("rsi"):
            summary["key_signals"].append(f"RSI: {signals['rsi']['value']:.1f} ({signals['rsi']['signal']})")
        if signals.get("kdj"):
            summary["key_signals"].append(f"KDJ J: {signals['kdj']['j']:.1f}")

        # 生成建议
        overall = signals.get("overall", {}).get("score", "neutral")
        trend_val = trend.get("trend", "unknown")

        if overall in ["strong_bullish", "bullish"] and trend_val in ["uptrend", "strong_uptrend"]:
            summary["recommendation"] = "买入"
        elif overall in ["strong_bearish", "bearish"] and trend_val in ["downtrend", "strong_downtrend"]:
            summary["recommendation"] = "卖出"
        elif overall == "strong_bullish" or trend_val == "strong_uptrend":
            summary["recommendation"] = "买入"
        elif overall == "strong_bearish" or trend_val == "strong_downtrend":
            summary["recommendation"] = "卖出"
        else:
            summary["recommendation"] = "持有"

        return summary


def main():
    """测试脚本"""
    import yfinance as yf

    analyzer = TechnicalAnalyzer()

    # 获取测试数据
    stock = yf.Ticker("AAPL")
    history = stock.history(period="3mo")

    price_data = {
        "symbol": "AAPL",
        "success": True,
        "period": "3mo",
        "data": {
            "dates": history.index.strftime('%Y-%m-%d').tolist(),
            "open": history['Open'].tolist(),
            "high": history['High'].tolist(),
            "low": history['Low'].tolist(),
            "close": history['Close'].tolist(),
            "volume": history['Volume'].tolist()
        }
    }

    result = analyzer.analyze(price_data)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
