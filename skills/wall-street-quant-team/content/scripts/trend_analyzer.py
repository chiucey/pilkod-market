#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
趋势分析脚本 - 顺势而为，趋势是第一准则
识别和跟踪市场趋势，提供趋势判断和预测
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import json
import sys


class TrendAnalyzer:
    """趋势分析器 - 顺势而为"""
    
    def __init__(self):
        """初始化"""
        self.trend_periods = {
            'short': 20,      # 短期趋势
            'medium': 60,     # 中期趋势
            'long': 120       # 长期趋势
        }
    
    def get_trend_data(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """
        获取趋势分析所需数据
        
        参数:
            symbol: 股票代码
            period: 数据周期
        
        返回:
            包含趋势数据的DataFrame
        """
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period, interval="1d")
            
            if hist.empty:
                return pd.DataFrame()
            
            # 计算各类均线
            hist['MA5'] = hist['Close'].rolling(window=5).mean()
            hist['MA10'] = hist['Close'].rolling(window=10).mean()
            hist['MA20'] = hist['Close'].rolling(window=20).mean()
            hist['MA60'] = hist['Close'].rolling(window=60).mean()
            hist['MA120'] = hist['Close'].rolling(window=120).mean()
            
            # 计算移动平均线角度（趋势强度）
            hist['MA20_angle'] = np.arctan((hist['MA20'] - hist['MA20'].shift(10)) / 10) * 180 / np.pi
            
            # 计算价格与均线的偏离度
            hist['price_deviation'] = ((hist['Close'] - hist['MA20']) / hist['MA20']) * 100
            
            # 计算趋势线（线性回归）
            hist['trend_line'] = self._calculate_trend_line(hist['Close'])
            
            return hist
            
        except Exception as e:
            print(f"获取趋势数据失败: {str(e)}", file=sys.stderr)
            return pd.DataFrame()
    
    def _calculate_trend_line(self, prices: pd.Series, window: int = 20) -> pd.Series:
        """计算趋势线"""
        trend = pd.Series(index=prices.index, dtype=float)
        for i in range(window, len(prices)):
            y = prices.iloc[i-window:i].values
            x = np.arange(len(y))
            z = np.polyfit(x, y, 1)
            trend.iloc[i] = z[0]
        return trend
    
    def identify_trend(self, symbol: str, period: str = "6mo") -> Dict:
        """
        识别趋势方向和强度
        
        参数:
            symbol: 股票代码
            period: 分析周期
        
        返回:
            趋势分析结果
        """
        hist = self.get_trend_data(symbol, period)
        
        if hist.empty:
            return {'error': '无法获取数据', 'symbol': symbol}
        
        latest = hist.iloc[-1]
        
        # 短期趋势判断
        short_trend = self._judge_single_trend(
            latest['MA5'], latest['MA10'], latest['MA20']
        )
        
        # 中期趋势判断
        medium_trend = self._judge_single_trend(
            latest['MA10'], latest['MA20'], latest['MA60']
        )
        
        # 长期趋势判断
        long_trend = self._judge_single_trend(
            latest['MA20'], latest['MA60'], latest['MA120']
        )
        
        # 综合趋势判断
        trend_score = self._calculate_trend_score(short_trend, medium_trend, long_trend)
        
        # 趋势强度
        trend_strength = self._judge_trend_strength(hist)
        
        # 趋势角度
        trend_angle = latest['MA20_angle'] if not pd.isna(latest['MA20_angle']) else 0
        
        result = {
            'symbol': symbol,
            'price': round(latest['Close'], 2),
            'timestamp': datetime.now().isoformat(),
            'short_trend': {
                'direction': short_trend,
                'period': '短期'
            },
            'medium_trend': {
                'direction': medium_trend,
                'period': '中期'
            },
            'long_trend': {
                'direction': long_trend,
                'period': '长期'
            },
            'comprehensive': {
                'score': trend_score,
                'direction': '上升趋势' if trend_score > 0 else '下降趋势' if trend_score < 0 else '震荡整理',
                'strength': trend_strength
            },
            'trend_angle': round(trend_angle, 2),
            'ma_levels': {
                'ma5': round(latest['MA5'], 2) if not pd.isna(latest['MA5']) else None,
                'ma10': round(latest['MA10'], 2) if not pd.isna(latest['MA10']) else None,
                'ma20': round(latest['MA20'], 2) if not pd.isna(latest['MA20']) else None,
                'ma60': round(latest['MA60'], 2) if not pd.isna(latest['MA60']) else None,
                'ma120': round(latest['MA120'], 2) if not pd.isna(latest['MA120']) else None
            },
            'price_deviation': round(latest['price_deviation'], 2) if not pd.isna(latest['price_deviation']) else 0,
            'investment_suggestion': self._generate_trend_suggestion(trend_score, trend_strength, trend_angle)
        }
        
        return result
    
    def _judge_single_trend(self, ma_fast: float, ma_mid: float, ma_slow: float) -> str:
        """判断单周期趋势"""
        if pd.isna(ma_fast) or pd.isna(ma_mid) or pd.isna(ma_slow):
            return '数据不足'
        
        # 多头排列 = 上升趋势
        if ma_fast > ma_mid > ma_slow:
            return '上升趋势'
        # 空头排列 = 下降趋势
        elif ma_fast < ma_mid < ma_slow:
            return '下降趋势'
        # 混乱排列 = 震荡
        else:
            return '震荡整理'
    
    def _calculate_trend_score(self, short: str, medium: str, long: str) -> int:
        """计算趋势得分"""
        score = 0
        
        # 短期趋势得分
        if short == '上升趋势':
            score += 2
        elif short == '下降趋势':
            score -= 2
        
        # 中期趋势得分
        if medium == '上升趋势':
            score += 3
        elif medium == '下降趋势':
            score -= 3
        
        # 长期趋势得分（权重最高）
        if long == '上升趋势':
            score += 5
        elif long == '下降趋势':
            score -= 5
        
        return score
    
    def _judge_trend_strength(self, hist: pd.DataFrame, window: int = 20) -> str:
        """判断趋势强度"""
        if len(hist) < window:
            return '数据不足'
        
        recent = hist.tail(window)
        
        # 计算收益率
        returns = recent['Close'].pct_change().dropna()
        
        # 计算趋势一致性（上涨日占比）
        up_days = (returns > 0).sum()
        up_ratio = up_days / len(returns) if len(returns) > 0 else 0
        
        # 计算波动率
        volatility = returns.std() * 100
        
        # 综合判断
        if up_ratio > 0.65 and volatility < 3:
            return '强势'
        elif up_ratio > 0.55:
            return '较强'
        elif up_ratio > 0.45:
            return '中性'
        elif up_ratio < 0.35:
            return '弱势'
        else:
            return '较弱'
    
    def _generate_trend_suggestion(self, trend_score: int, trend_strength: str, trend_angle: float) -> Dict:
        """生成顺势投资建议"""
        # 基础建议
        if trend_score >= 5 and trend_strength in ['强势', '较强']:
            base_suggestion = '强烈买入'
            action = '上升趋势确立，顺势做多'
            risk_level = '低'
        elif trend_score >= 3:
            base_suggestion = '买入'
            action = '趋势向上，可以考虑买入'
            risk_level = '中低'
        elif trend_score <= -5 and trend_strength in ['弱势', '较弱']:
            base_suggestion = '强烈卖出'
            action = '下降趋势确立，顺势做空或空仓'
            risk_level = '低'
        elif trend_score <= -3:
            base_suggestion = '卖出'
            action = '趋势向下，建议减仓或离场'
            risk_level = '中低'
        elif abs(trend_score) <= 2:
            base_suggestion = '观望'
            action = '趋势不明，保持观望'
            risk_level = '中'
        else:
            base_suggestion = '谨慎'
            action = '趋势不明确，谨慎操作'
            risk_level = '中'
        
        # 趋势角度修正
        if abs(trend_angle) > 30:
            action += f'，趋势角度{abs(trend_angle):.1f}度，趋势强劲'
        elif abs(trend_angle) < 10:
            action += '，趋势角度平缓，动能不足'
        
        return {
            'suggestion': base_suggestion,
            'action': action,
            'risk_level': risk_level,
            'trend_following': True  # 顺势而为标志
        }
    
    def detect_trend_reversal(self, symbol: str, period: str = "3mo") -> Dict:
        """
        检测趋势反转信号
        
        参数:
            symbol: 股票代码
            period: 分析周期
        
        返回:
            趋势反转分析结果
        """
        hist = self.get_trend_data(symbol, period)
        
        if hist.empty or len(hist) < 60:
            return {'error': '数据不足', 'symbol': symbol}
        
        signals = []
        
        # 1. 均线死叉/金叉检测
        ma_cross = self._detect_ma_cross(hist)
        signals.extend(ma_cross)
        
        # 2. 价格与均线偏离检测
        deviation_signals = self._detect_deviation(hist)
        signals.extend(deviation_signals)
        
        # 3. 趋势角度变化检测
        angle_signals = self._detect_angle_change(hist)
        signals.extend(angle_signals)
        
        # 4. 成交量异常检测
        volume_signals = self._detect_volume_anomaly(hist)
        signals.extend(volume_signals)
        
        # 综合判断
        reversal_probability = self._calculate_reversal_probability(signals)
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'signals': signals,
            'reversal_probability': reversal_probability,
            'reversal_direction': self._judge_reversal_direction(signals),
            'warning_level': '高' if reversal_probability > 0.7 else '中' if reversal_probability > 0.4 else '低'
        }
    
    def _detect_ma_cross(self, hist: pd.DataFrame) -> List[Dict]:
        """检测均线交叉"""
        signals = []
        
        if len(hist) < 3:
            return signals
        
        # 金叉（短期上穿中期）
        if hist['MA5'].iloc[-2] < hist['MA20'].iloc[-2] and hist['MA5'].iloc[-1] > hist['MA20'].iloc[-1]:
            signals.append({
                'type': '金叉',
                'description': '短期均线上穿长期均线，看涨信号',
                'strength': '强',
                'trend_change': '可能反转向上'
            })
        
        # 死叉（短期下穿中期）
        if hist['MA5'].iloc[-2] > hist['MA20'].iloc[-2] and hist['MA5'].iloc[-1] < hist['MA20'].iloc[-1]:
            signals.append({
                'type': '死叉',
                'description': '短期均线下穿长期均线，看跌信号',
                'strength': '强',
                'trend_change': '可能反转向下'
            })
        
        return signals
    
    def _detect_deviation(self, hist: pd.DataFrame) -> List[Dict]:
        """检测价格偏离"""
        signals = []
        
        if len(hist) < 30:
            return signals
        
        # 计算30日价格变化
        price_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-30]) / hist['Close'].iloc[-30] * 100
        
        # 计算同期均线变化
        ma_change = (hist['MA20'].iloc[-1] - hist['MA20'].iloc[-30]) / hist['MA20'].iloc[-30] * 100
        
        # 顶背离：价格上涨但均线下降
        if price_change > 5 and ma_change < -2:
            signals.append({
                'type': '顶背离',
                'description': '价格创新高但均线未跟随，警惕反转',
                'strength': '中',
                'trend_change': '可能反转向下'
            })
        
        # 底背离：价格下跌但均线上行
        if price_change < -5 and ma_change > 2:
            signals.append({
                'type': '底背离',
                'description': '价格创新低但均线未跟随，可能企稳',
                'strength': '中',
                'trend_change': '可能反转向上'
            })
        
        return signals
    
    def _detect_angle_change(self, hist: pd.DataFrame) -> List[Dict]:
        """检测趋势角度变化"""
        signals = []
        
        if len(hist) < 20 or hist['MA20_angle'].isna().all():
            return signals
        
        # 计算角度变化
        angle_change = hist['MA20_angle'].iloc[-1] - hist['MA20_angle'].iloc[-10]
        
        # 角度急剧下降
        if angle_change < -15:
            signals.append({
                'type': '角度骤降',
                'description': f'趋势角度下降{abs(angle_change):.1f}度，动能减弱',
                'strength': '中',
                'trend_change': '上升动能减弱'
            })
        
        # 角度急剧上升
        if angle_change > 15:
            signals.append({
                'type': '角度骤升',
                'description': f'趋势角度上升{abs(angle_change):.1f}度，动能增强',
                'strength': '中',
                'trend_change': '下跌动能减弱'
            })
        
        return signals
    
    def _detect_volume_anomaly(self, hist: pd.DataFrame) -> List[Dict]:
        """检测成交量异常"""
        signals = []
        
        if len(hist) < 20:
            return signals
        
        # 计算平均成交量
        avg_volume = hist['Volume'].tail(20).mean()
        current_volume = hist['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # 放量上涨
        if volume_ratio > 1.5 and hist['Close'].iloc[-1] > hist['Close'].iloc[-2]:
            signals.append({
                'type': '放量上涨',
                'description': f'成交量放大{volume_ratio:.1f}倍且价格上涨，确认上升趋势',
                'strength': '强',
                'trend_change': '上升趋势确认'
            })
        
        # 放量下跌
        if volume_ratio > 1.5 and hist['Close'].iloc[-1] < hist['Close'].iloc[-2]:
            signals.append({
                'type': '放量下跌',
                'description': f'成交量放大{volume_ratio:.1f}倍且价格下跌，确认下降趋势',
                'strength': '强',
                'trend_change': '下降趋势确认'
            })
        
        return signals
    
    def _calculate_reversal_probability(self, signals: List[Dict]) -> float:
        """计算反转概率"""
        if not signals:
            return 0.0
        
        strength_weights = {'强': 0.4, '中': 0.25, '弱': 0.1}
        
        total_prob = 0.0
        for signal in signals:
            prob = strength_weights.get(signal.get('strength', '弱'), 0.1)
            total_prob += prob
        
        return min(total_prob, 1.0)
    
    def _judge_reversal_direction(self, signals: List[Dict]) -> str:
        """判断反转方向"""
        up_signals = sum(1 for s in signals if '向上' in s.get('trend_change', ''))
        down_signals = sum(1 for s in signals if '向下' in s.get('trend_change', ''))
        
        if up_signals > down_signals:
            return '可能向上反转'
        elif down_signals > up_signals:
            return '可能向下反转'
        else:
            return '方向不明'
    
    def get_trend_support_resistance(self, symbol: str, period: str = "6mo") -> Dict:
        """
        获取趋势支撑位和压力位
        
        参数:
            symbol: 股票代码
            period: 分析周期
        
        返回:
            支撑位和压力位
        """
        hist = self.get_trend_data(symbol, period)
        
        if hist.empty:
            return {'error': '无法获取数据', 'symbol': symbol}
        
        current_price = hist['Close'].iloc[-1]
        
        # 支撑位：使用均线和前期低点
        support_levels = []
        
        # 均线支撑
        for ma in ['MA5', 'MA10', 'MA20', 'MA60']:
            if not pd.isna(hist[ma].iloc[-1]):
                ma_value = hist[ma].iloc[-1]
                if ma_value < current_price:
                    support_levels.append({
                        'level': round(ma_value, 2),
                        'source': f'{ma}均线支撑'
                    })
        
        # 前期低点支撑
        recent_lows = hist['Low'].tail(60).nsmallest(5)
        for low in recent_lows:
            if low < current_price:
                support_levels.append({
                    'level': round(low, 2),
                    'source': '前期低点'
                })
                break
        
        # 压力位：使用均线和前期高点
        resistance_levels = []
        
        # 均线压力
        for ma in ['MA5', 'MA10', 'MA20', 'MA60']:
            if not pd.isna(hist[ma].iloc[-1]):
                ma_value = hist[ma].iloc[-1]
                if ma_value > current_price:
                    resistance_levels.append({
                        'level': round(ma_value, 2),
                        'source': f'{ma}均线压力'
                    })
        
        # 前期高点压力
        recent_highs = hist['High'].tail(60).nlargest(5)
        for high in recent_highs:
            if high > current_price:
                resistance_levels.append({
                    'level': round(high, 2),
                    'source': '前期高点'
                })
                break
        
        # 按价格排序
        support_levels.sort(key=lambda x: x['level'], reverse=True)
        resistance_levels.sort(key=lambda x: x['level'])
        
        return {
            'symbol': symbol,
            'current_price': round(current_price, 2),
            'support_levels': support_levels[:3],  # 最近3个支撑位
            'resistance_levels': resistance_levels[:3],  # 最近3个压力位
            'timestamp': datetime.now().isoformat()
        }


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='趋势分析工具 - 顺势而为，趋势是第一准则')
    parser.add_argument('symbol', help='股票代码 (如: AAPL, 600519.SS, 0700.HK)')
    parser.add_argument('--type', choices=['trend', 'reversal', 'levels', 'all'], 
                       default='trend', help='分析类型')
    parser.add_argument('--period', default='6mo', help='数据周期')
    
    args = parser.parse_args()
    
    analyzer = TrendAnalyzer()
    
    if args.type == 'trend':
        result = analyzer.identify_trend(args.symbol, period=args.period)
    elif args.type == 'reversal':
        result = analyzer.detect_trend_reversal(args.symbol, period=args.period)
    elif args.type == 'levels':
        result = analyzer.get_trend_support_resistance(args.symbol, period=args.period)
    elif args.type == 'all':
        result = {
            'trend': analyzer.identify_trend(args.symbol, period=args.period),
            'reversal': analyzer.detect_trend_reversal(args.symbol, period=args.period),
            'levels': analyzer.get_trend_support_resistance(args.symbol, period=args.period)
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
