#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
笑傲牛熊分析器核心模块
用于MaxClaw技能执行
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# 尝试导入akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False


@dataclass
class StageResult:
    """阶段分析结果"""
    stage: int  # 1-4阶段
    stage_name: str
    stage_color: str
    confidence: float
    description: str


class WeinsteinAnalyzer:
    """笑傲牛熊方法论分析器"""

    STAGE_COLORS = {
        1: 'FFFFFF',      # 无色
        2: 'FF6464',     # 红色
        3: 'FFFF64',     # 黄色
        4: '64FF64',     # 绿色
    }

    def __init__(self):
        pass

    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """计算指数移动平均线"""
        return data.ewm(span=period, adjust=False).mean()

    def determine_stage(self, df: pd.DataFrame, price_col: str = 'close') -> StageResult:
        """判断股票所处阶段"""
        if df is None or df.empty or len(df) < 30:
            return StageResult(1, "阶段1-底部", "FFFFFF", 0.5, "数据不足")

        prices = df[price_col]
        ma30 = self.calculate_ema(prices, 30)

        current_price = prices.iloc[-1]
        current_ma = ma30.iloc[-1]

        # 计算均线斜率
        ma_slope = ma30.iloc[-1] - ma30.iloc[-5] if len(ma30) >= 5 else 0
        ma_direction = "上升" if ma_slope > 0 else "下降" if ma_slope < 0 else "走平"

        price_above_ma = current_price > current_ma

        # 计算高低点
        recent = df.tail(10)
        higher_highs = recent['high'].iloc[-1] > recent['high'].iloc[-5] if len(recent) >= 5 else False
        higher_lows = recent['low'].iloc[-1] > recent['low'].iloc[-5] if len(recent) >= 5 else False

        # 阶段判断
        if not price_above_ma and ma_direction == "下降":
            stage, stage_name, desc, conf = 4, "阶段4-下跌", "价格在均线下方，均线向下运行", 0.8
        elif price_above_ma and higher_highs and higher_lows and ma_direction == "上升":
            stage, stage_name, desc, conf = 2, "阶段2-拉升", "强势拉升，均线向上运行", 0.9
        elif not price_above_ma and ma_direction in ["走平", "上升"]:
            stage, stage_name, desc, conf = 3, "阶段3-顶部", "价格在均线下方反复穿越", 0.6
        elif price_above_ma and ma_direction == "走平":
            stage, stage_name, desc, conf = 3, "阶段3-顶部", "顶部震荡区", 0.6
        else:
            stage, stage_name, desc, conf = 1, "阶段1-底部", "底部吸筹区间", 0.5

        return StageResult(stage, stage_name, self.STAGE_COLORS.get(stage, "FFFFFF"), conf, desc)

    def calculate_relative_strength(self, stock_df: pd.DataFrame, market_df: pd.DataFrame) -> Tuple[str, float, str]:
        """计算相对强度"""
        if stock_df is None or market_df is None or stock_df.empty or market_df.empty:
            return "弱", 0, "64FF64"

        stock_price = stock_df['close'].iloc[-1]
        market_price = market_df['close'].iloc[-1]

        if len(stock_df) >= 30 and len(market_df) >= 30:
            base_stock = stock_df['close'].iloc[-30]
            base_market = market_df['close'].iloc[-30]
            current_ratio = (stock_price / market_price) * 100
            base_ratio = (base_stock / base_market) * 100
            rs_change = (current_ratio / base_ratio - 1) * 100
        else:
            rs_change = 0

        if rs_change > 20:
            return "强", rs_change, "FF6464"
        elif rs_change > 5:
            return "小强", rs_change, "FFFF64"
        elif rs_change > -5:
            return "小弱", rs_change, "FFFF64"
        else:
            return "弱", rs_change, "64FF64"

    def analyze_volume(self, df: pd.DataFrame, lookback: int = 20) -> Tuple[str, str, float]:
        """分析成交量"""
        if df is None or df.empty or 'volume' not in df.columns:
            return "不足", "FFFF64", 1.0

        recent = df.tail(lookback)
        current_volume = recent['volume'].iloc[-1]
        avg_volume = recent['volume'].mean()

        if avg_volume == 0:
            return "不足", "FFFF64", 1.0

        volume_ratio = current_volume / avg_volume

        vol_ma5 = df['volume'].rolling(5).mean().iloc[-1]
        vol_ma20 = df['volume'].rolling(20).mean().iloc[-1]

        if current_volume > vol_ma5:
            return "放量", "FF6464", volume_ratio
        elif current_volume > vol_ma20:
            return "温和", "FFFF64", volume_ratio
        else:
            return "缩量", "64FF64", volume_ratio

    def analyze_ma_position(self, df: pd.DataFrame) -> Tuple[bool, bool, bool, str]:
        """分析均线位置"""
        if df is None or df.empty:
            return False, False, False, "FFFF64"

        current_price = df['close'].iloc[-1]
        ma30 = df['close'].rolling(30).mean().iloc[-1] if len(df) >= 30 else current_price
        ma60 = df['close'].rolling(60).mean().iloc[-1] if len(df) >= 60 else ma30

        above_30 = current_price > ma30
        between_30_60 = ma30 < current_price < ma60
        below_60 = current_price < ma60

        if above_30:
            color = "FF6464"
        elif below_60:
            color = "64FF64"
        else:
            color = "FFFFFF"

        return above_30, between_30_60, below_60, color

    def analyze_resistance(self, df: pd.DataFrame) -> Tuple[float, int, float, int]:
        """分析阻力位"""
        if df is None or df.empty:
            return 0.0, 0, 0.0, 0

        highs = df['high'].rolling(window=20).max()
        resistance_level = highs.iloc[-2] if len(highs) >= 2 else df['high'].iloc[-1]

        weeks_ago = 0
        for i in range(2, min(len(df), 52)):
            if df['high'].iloc[-i] > resistance_level:
                weeks_ago = i // 5
                break

        return resistance_level, weeks_ago, resistance_level, weeks_ago

    def calculate_stop_loss(self, df: pd.DataFrame, buy_price: float = None) -> Tuple[float, float]:
        """计算止损位"""
        if df is None or df.empty:
            return 0.0, 0.0

        ma30 = self.calculate_ema(df['close'], 30).iloc[-1]
        support_low = df['low'].tail(20).min()
        daily_stop = max(support_low, ma30) - 0.125

        if buy_price:
            hard_stop = buy_price * 0.93
            daily_stop = min(daily_stop, hard_stop)

        return daily_stop, ma30


def get_stock_data(stock_code: str, days: int = 365) -> Optional[pd.DataFrame]:
    """获取股票数据"""
    if not AKSHARE_AVAILABLE:
        return None

    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - pd.Timedelta(days=days)).strftime('%Y%m%d')

        df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="weekly",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )

        if df is not None and not df.empty:
            df = df.rename(columns={
                '日期': 'trade_date', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume'
            })
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            return df.sort_values('trade_date').reset_index(drop=True)
    except Exception as e:
        print(f"获取 {stock_code} 数据失败: {e}")

    return None


def get_market_data(index_code: str = "000001", days: int = 365) -> Optional[pd.DataFrame]:
    """获取大盘数据"""
    if not AKSHARE_AVAILABLE:
        return None

    try:
        df = ak.stock_zh_index_daily(symbol=f"sh{index_code}")
        if df is not None and not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            start_date = datetime.now() - pd.Timedelta(days=days)
            df = df[df['date'] >= start_date]
            df = df.rename(columns={'date': 'trade_date', 'close': 'close'})
            return df.sort_values('trade_date').reset_index(drop=True)
    except Exception as e:
        print(f"获取大盘数据失败: {e}")

    return None


def analyze_single_stock(stock_code: str, stock_name: str = None) -> Dict:
    """分析单只股票"""
    analyzer = WeinsteinAnalyzer()

    # 获取数据
    stock_df = get_stock_data(stock_code)
    market_df = get_market_data()

    if stock_df is None or stock_df.empty:
        return {
            'stock_code': stock_code,
            'stock_name': stock_name or stock_code,
            'error': '无法获取数据',
            'recommendation': '数据获取失败'
        }

    # 基本信息
    current_price = stock_df['close'].iloc[-1]
    price_change = (stock_df['close'].iloc[-1] / stock_df['close'].iloc[-2] - 1) * 100 if len(stock_df) >= 2 else 0

    # 阶段分析
    stock_stage = analyzer.determine_stage(stock_df)
    market_stage = analyzer.determine_stage(market_df) if market_df is not None else StageResult(2, "阶段2-拉升", "FF6464", 0.5, "默认")

    # 相对强度
    rs_level, rs_value, rs_color = analyzer.calculate_relative_strength(stock_df, market_df)

    # 均线位置
    above_30, between_30_60, below_60, week_color = analyzer.analyze_ma_position(stock_df)

    # 成交量
    volume_level, volume_color, volume_ratio = analyzer.analyze_volume(stock_df)

    # 阻力与止损
    resistance, res_weeks, _, _ = analyzer.analyze_resistance(stock_df)
    daily_stop, weekly_stop = analyzer.calculate_stop_loss(stock_df, current_price)

    # 操作建议
    if market_stage.stage != 2:
        recommendation = "观望"
        detail = f"市场处于{market_stage.stage_name}，建议等待"
    elif stock_stage.stage == 4:
        recommendation = "卖出"
        detail = "股票处于第四阶段下跌"
    elif stock_stage.stage == 3:
        recommendation = "减仓"
        detail = f"股票处于{stock_stage.stage_name}"
    elif stock_stage.stage == 2:
        if rs_level in ["弱", "小弱"]:
            recommendation = "观望"
            detail = "股票在第二阶段但相对强度较弱"
        else:
            recommendation = "持有"
            detail = "股票在第二阶段强势运行"
    else:
        recommendation = "等待"
        detail = "等待突破第一阶段"

    return {
        'stock_code': stock_code,
        'stock_name': stock_name or stock_code,
        'current_price': round(current_price, 2),
        'price_change_pct': round(price_change, 2),
        'dividend_yield': 0.0,
        'high_dividend': False,
        'relative_strength': rs_level,
        'rs_value': round(rs_value, 2),
        'volume_level': volume_level,
        'volume_color': volume_color,
        'volume_ratio': round(volume_ratio, 2),
        'pullback_occurred': False,
        'pullback_volume_decreased': False,
        'volume_decrease_ratio': 0,
        'below_previous_low': False,
        'above_30_week': above_30,
        'between_30_60': between_30_60,
        'below_60_week': below_60,
        'above_250_5min': above_30,
        'market_stage': {'stage': market_stage.stage, 'stage_name': market_stage.stage_name},
        'industry_stage': {'stage': stock_stage.stage, 'stage_name': stock_stage.stage_name},
        'stock_stage': {'stage': stock_stage.stage, 'stage_name': stock_stage.stage_name},
        'second_breakout_resistance': round(resistance, 2),
        'second_breakout_weeks': res_weeks,
        'resistance_level': round(resistance, 2),
        'resistance_weeks': res_weeks,
        'stop_loss_daily': round(daily_stop, 2),
        'stop_loss_weekly': round(weekly_stop, 2),
        'recommendation': recommendation,
        'recommendation_detail': detail,
    }


# 导出供外部使用
__all__ = ['WeinsteinAnalyzer', 'analyze_single_stock', 'get_stock_data', 'get_market_data', 'StageResult']
