#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行为金融分析脚本 - 精准分析投资人群行为
识别市场情绪偏差、群体行为模式，提供行为金融视角的投资建议
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import sys


class BehaviorAnalyzer:
    """行为金融分析师 - 精准分析投资人群行为"""
    
    def __init__(self):
        """初始化"""
        self.bias_types = {
            'overconfidence': '过度自信',
            'herding': '羊群效应',
            'loss_aversion': '损失厌恶',
            'disposition': '处置效应',
            'anchoring': '锚定效应',
            'gamblers_fallacy': '赌徒谬误',
            'recency': '近因效应',
            'framing': '框架效应'
        }
    
    def get_market_sentiment(self, symbol: str, period: str = "3mo") -> Dict:
        """
        获取市场情绪综合指标
        
        参数:
            symbol: 股票代码
            period: 分析周期
        
        返回:
            市场情绪分析结果
        """
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period, interval="1d")
            
            if hist.empty:
                return {'error': '无法获取数据', 'symbol': symbol}
            
            # 计算基础指标
            sentiment_indicators = self._calculate_sentiment_indicators(hist)
            
            # 识别行为偏差
            behavior_biases = self._detect_behavior_biases(hist)
            
            # 计算情绪周期位置
            cycle_position = self._identify_sentiment_cycle(hist)
            
            # 生成行为金融建议
            behavior_suggestion = self._generate_behavior_suggestion(
                sentiment_indicators, behavior_biases, cycle_position
            )
            
            result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'sentiment_indicators': sentiment_indicators,
                'behavior_biases': behavior_biases,
                'sentiment_cycle': cycle_position,
                'behavior_suggestion': behavior_suggestion
            }
            
            return result
            
        except Exception as e:
            return {'error': f'分析失败: {str(e)}', 'symbol': symbol}
    
    def _calculate_sentiment_indicators(self, hist: pd.DataFrame) -> Dict:
        """计算情绪指标"""
        if hist.empty:
            return {}
        
        latest = hist.iloc[-1]
        recent = hist.tail(20)
        
        # 1. 涨跌情绪
        price_change = (latest['Close'] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100
        if price_change > 20:
            sentiment_level = '极度乐观'
            sentiment_score = 90
        elif price_change > 10:
            sentiment_level = '乐观'
            sentiment_score = 70
        elif price_change > 0:
            sentiment_level = '偏乐观'
            sentiment_score = 55
        elif price_change > -10:
            sentiment_level = '偏悲观'
            sentiment_score = 45
        elif price_change > -20:
            sentiment_level = '悲观'
            sentiment_score = 30
        else:
            sentiment_level = '极度悲观'
            sentiment_score = 10
        
        # 2. 成交量情绪
        avg_volume = hist['Volume'].mean()
        current_volume = latest['Volume']
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 2:
            volume_sentiment = '异常活跃'
        elif volume_ratio > 1.5:
            volume_sentiment = '活跃'
        elif volume_ratio > 0.8:
            volume_sentiment = '正常'
        else:
            volume_sentiment = '清淡'
        
        # 3. 波动率情绪
        volatility = hist['Close'].pct_change().std() * 100
        if volatility > 5:
            volatility_sentiment = '高波动'
        elif volatility > 2:
            volatility_sentiment = '适中'
        else:
            volatility_sentiment = '低波动'
        
        # 4. 动量情绪
        returns = recent['Close'].pct_change().dropna()
        positive_ratio = (returns > 0).sum() / len(returns) if len(returns) > 0 else 0.5
        
        if positive_ratio > 0.7:
            momentum_sentiment = '强势动量'
        elif positive_ratio > 0.55:
            momentum_sentiment = '偏强'
        elif positive_ratio > 0.45:
            momentum_sentiment = '中性'
        elif positive_ratio > 0.3:
            momentum_sentiment = '偏弱'
        else:
            momentum_sentiment = '弱势动量'
        
        # 5. 综合情绪评分
        # 基于价格变化、成交量、波动率的综合评分
        price_component = min(max(sentiment_score, 0), 100)
        volume_component = min(max(volume_ratio * 30, 0), 100)
        volatility_component = 100 - min(max(volatility * 10, 0), 100)
        
        composite_score = (price_component * 0.5 + volume_component * 0.2 + volatility_component * 0.3)
        
        return {
            'price_change_percent': round(price_change, 2),
            'sentiment_level': sentiment_level,
            'sentiment_score': round(composite_score, 1),
            'volume_ratio': round(volume_ratio, 2),
            'volume_sentiment': volume_sentiment,
            'volatility': round(volatility, 2),
            'volatility_sentiment': volatility_sentiment,
            'momentum_positive_ratio': round(positive_ratio * 100, 1),
            'momentum_sentiment': momentum_sentiment
        }
    
    def _detect_behavior_biases(self, hist: pd.DataFrame) -> List[Dict]:
        """检测行为偏差"""
        biases = []
        
        if hist.empty or len(hist) < 60:
            return [{'type': '数据不足', 'description': '需要更多历史数据进行分析'}]
        
        recent = hist.tail(60)
        
        # 1. 检测羊群效应（成交量突增但价格无趋势）
        avg_volume = hist['Volume'].mean()
        recent_volume = recent['Volume'].mean()
        price_std = recent['Close'].std()
        
        if recent_volume > avg_volume * 1.5 and price_std < hist['Close'].std() * 0.5:
            biases.append({
                'type': '羊群效应',
                'english': 'Herding Effect',
                'description': '成交量放大但价格波动收窄，可能存在散户跟风行为',
                'severity': '中',
                'investment_impact': '警惕短期波动加剧，考虑逆向操作或等待趋势明确'
            })
        
        # 2. 检测处置效应（上涨时卖出，下跌时死守）
        recent_returns = recent['Close'].pct_change().dropna()
        positive_returns = recent_returns[recent_returns > 0]
        negative_returns = recent_returns[recent_returns < 0]
        
        if len(positive_returns) > len(negative_returns) * 1.5:
            biases.append({
                'type': '处置效应',
                'english': 'Disposition Effect',
                'description': '近期上涨交易日多于下跌，可能存在投资者急于兑现盈利的心理',
                'severity': '中',
                'investment_impact': '市场可能尚未充分上涨，可考虑持仓观察'
            })
        elif len(negative_returns) > len(positive_returns) * 1.5:
            biases.append({
                'type': '损失厌恶',
                'english': 'Loss Aversion',
                'description': '近期下跌交易日多于上涨，投资者可能因恐惧而过度抛售',
                'severity': '中',
                'investment_impact': '可能出现超卖，考虑逆向买入机会'
            })
        
        # 3. 检测近因效应（过度关注近期走势）
        short_return = (recent['Close'].iloc[-1] - recent['Close'].iloc[-10]) / recent['Close'].iloc[-10] * 100
        long_return = (recent['Close'].iloc[-1] - recent['Close'].iloc[0]) / recent['Close'].iloc[0] * 100
        
        if abs(short_return) > abs(long_return) * 2:
            if short_return > 0:
                biases.append({
                    'type': '近因效应-乐观',
                    'english': 'Recency Bias (Optimistic)',
                    'description': '短期涨幅显著高于长期，投资者可能过度乐观',
                    'severity': '中',
                    'investment_impact': '警惕回调风险，不要被短期上涨迷惑'
                })
            else:
                biases.append({
                    'type': '近因效应-悲观',
                    'english': 'Recency Bias (Pessimistic)',
                    'description': '短期跌幅显著高于长期，投资者可能过度悲观',
                    'severity': '中',
                    'investment_impact': '可能是买入机会，关注基本面是否支撑'
                })
        
        # 4. 检测过度波动
        volatility = recent_returns.std() * 100
        if volatility > 4:
            biases.append({
                'type': '过度波动',
                'english': 'Excessive Volatility',
                'description': '价格波动剧烈，可能反映投资者情绪极度不稳定',
                'severity': '高',
                'investment_impact': '降低仓位或等待波动率下降'
            })
        
        # 5. 检测趋势追随过度
        trend_strength = self._calculate_trend_strength(recent)
        if trend_strength > 0.8 and recent_returns.std() > 0.03:
            biases.append({
                'type': '趋势狂热',
                'english': 'Trend Mania',
                'description': '趋势强劲且波动大，可能存在追涨杀跌行为',
                'severity': '高',
                'investment_impact': '趋势可能接近尾声，谨慎追高'
            })
        
        # 6. 检测均值回归倾向
        current_price = recent['Close'].iloc[-1]
        mean_price = recent['Close'].mean()
        deviation_percent = abs(current_price - mean_price) / mean_price * 100
        
        if deviation_percent > 15:
            biases.append({
                'type': '偏离均值',
                'english': 'Deviation from Mean',
                'description': f'价格偏离均值{deviation_percent:.1f}%，存在均值回归可能',
                'severity': '中',
                'investment_impact': '关注均值回归机会'
            })
        
        return biases
    
    def _calculate_trend_strength(self, hist: pd.DataFrame) -> float:
        """计算趋势强度"""
        if hist.empty:
            return 0.0
        
        returns = hist['Close'].pct_change().dropna()
        
        # 使用R-squared计算趋势强度
        x = np.arange(len(returns))
        y = returns.values
        
        if len(x) < 2:
            return 0.0
        
        # 简单线性回归
        coeffs = np.polyfit(x, y, 1)
        y_pred = np.polyval(coeffs, x)
        
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return abs(r_squared)
    
    def _identify_sentiment_cycle(self, hist: pd.DataFrame) -> Dict:
        """识别情绪周期位置"""
        if hist.empty or len(hist) < 30:
            return {'position': '数据不足'}
        
        recent = hist.tail(30)
        
        # 计算30日涨跌
        price_change = (recent['Close'].iloc[-1] - recent['Close'].iloc[0]) / recent['Close'].iloc[0] * 100
        
        # 计算成交量变化
        volume_change = (recent['Volume'].iloc[-1] - recent['Volume'].iloc[0]) / recent['Volume'].iloc[0] * 100 if recent['Volume'].iloc[0] > 0 else 0
        
        # 计算波动率变化
        recent_volatility = recent['Close'].pct_change().std()
        earlier_volatility = hist.iloc[:-30]['Close'].pct_change().std() if len(hist) > 30 else recent_volatility
        
        # 判断周期位置
        if price_change > 10 and volume_change > 30:
            position = '情绪高潮'
            description = '市场极度乐观，警惕盛极而衰'
        elif price_change > 5:
            position = '情绪高涨'
            description = '市场乐观，但需关注反转风险'
        elif price_change > 0:
            position = '情绪回暖'
            description = '市场情绪改善，趋势向好'
        elif price_change > -5:
            position = '情绪谨慎'
            description = '市场情绪谨慎，可能震荡'
        elif price_change > -10:
            position = '情绪低迷'
            description = '市场情绪低迷，可能孕育机会'
        else:
            position = '情绪绝望'
            description = '市场极度悲观，可能物极必反'
        
        return {
            'position': position,
            'description': description,
            'price_change_30d': round(price_change, 2),
            'volume_change_30d': round(volume_change, 2),
            'volatility_trend': '上升' if recent_volatility > earlier_volatility else '下降'
        }
    
    def _generate_behavior_suggestion(self, sentiment: Dict, biases: List[Dict], cycle: Dict) -> Dict:
        """生成行为金融建议"""
        suggestions = []
        risk_level = '低'
        action = '正常操作'
        
        # 基于情绪周期的建议
        cycle_position = cycle.get('position', '未知')
        
        if cycle_position in ['情绪高潮', '情绪高涨']:
            suggestions.append('市场情绪过于乐观，应保持谨慎，减少追高')
            suggestions.append('考虑逐步减仓，锁定利润')
            risk_level = '高'
            action = '减仓观望'
        elif cycle_position in ['情绪绝望', '情绪低迷']:
            suggestions.append('市场情绪过度悲观，可能存在超卖机会')
            suggestions.append('关注基本面优质标的的买入机会')
            risk_level = '中'
            action = '关注机会'
        elif cycle_position == '情绪回暖':
            suggestions.append('市场情绪改善，可适度加仓')
            action = '适度加仓'
        
        # 基于行为偏差的建议
        high_severity_biases = [b for b in biases if b.get('severity') == '高']
        if high_severity_biases:
            for bias in high_severity_biases:
                if bias.get('investment_impact'):
                    suggestions.append(f"【{bias['type']}】{bias['investment_impact']}")
        
        # 综合建议
        sentiment_score = sentiment.get('sentiment_score', 50)
        if sentiment_score > 80:
            suggestions.append('情绪极度亢奋，逆向思维，考虑减仓')
            risk_level = '高'
        elif sentiment_score < 20:
            suggestions.append('情绪极度悲观，关注价值投资机会')
        
        return {
            'action': action,
            'risk_level': risk_level,
            'suggestions': suggestions,
            'contrarian_opportunity': cycle_position in ['情绪高潮', '情绪绝望'],
            'sentiment_score': sentiment_score
        }
    
    def analyze_investor_behavior(self, symbol: str, period: str = "6mo") -> Dict:
        """
        深度分析投资者行为
        
        参数:
            symbol: 股票代码
            period: 分析周期
        
        返回:
            投资者行为分析报告
        """
        sentiment = self.get_market_sentiment(symbol, period)
        
        if 'error' in sentiment:
            return sentiment
        
        # 额外分析
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'executive_summary': self._generate_executive_summary(sentiment),
            'sentiment_analysis': sentiment,
            'behavior_insights': self._generate_behavior_insights(sentiment),
            'investment_strategy': self._generate_investment_strategy(sentiment)
        }
        
        return result
    
    def _generate_executive_summary(self, sentiment: Dict) -> str:
        """生成执行摘要"""
        cycle = sentiment.get('sentiment_cycle', {})
        behavior = sentiment.get('behavior_suggestion', {})
        
        summary = f"当前市场处于【{cycle.get('position', '未知')}】阶段，"
        summary += f"情绪评分{behavior.get('sentiment_score', 'N/A')}分，"
        summary += f"建议{behavior.get('action', '观望')}。"
        
        if behavior.get('contrarian_opportunity'):
            summary += "出现逆向投资机会信号。"
        
        return summary
    
    def _generate_behavior_insights(self, sentiment: Dict) -> List[str]:
        """生成行为洞察"""
        insights = []
        
        # 偏差洞察
        biases = sentiment.get('behavior_biases', [])
        for bias in biases:
            if bias.get('type') != '数据不足':
                insights.append(f"检测到{bias.get('type')}：{bias.get('description')}")
        
        # 情绪洞察
        cycle = sentiment.get('sentiment_cycle', {})
        if cycle.get('volatility_trend') == '上升':
            insights.append("波动率上升，市场不确定性增加，需谨慎操作")
        
        return insights
    
    def _generate_investment_strategy(self, sentiment: Dict) -> Dict:
        """生成投资策略"""
        behavior = sentiment.get('behavior_suggestion', {})
        cycle = sentiment.get('sentiment_cycle', {})
        
        action = behavior.get('action', '观望')
        risk_level = behavior.get('risk_level', '中')
        
        if action == '减仓观望':
            strategy = {
                'position': '建议降低仓位至30%以下',
                'entry_strategy': '等待情绪回落至正常水平再考虑加仓',
                'exit_strategy': '设置止盈止损，纪律执行',
                'key_focus': '风险控制第一'
            }
        elif action == '关注机会':
            strategy = {
                'position': '可考虑逐步建仓至50%',
                'entry_strategy': '分批买入，关注估值合理性',
                'exit_strategy': '设定目标价和止损位',
                'key_focus': '逆向布局优质标的'
            }
        elif action == '适度加仓':
            strategy = {
                'position': '可维持或适度增加仓位至60%',
                'entry_strategy': '回调即是买入机会',
                'exit_strategy': '趋势破坏则减仓',
                'key_focus': '顺势而为'
            }
        else:
            strategy = {
                'position': '维持现有仓位或观望',
                'entry_strategy': '等待更明确信号',
                'exit_strategy': '严格执行止损',
                'key_focus': '耐心等待'
            }
        
        return strategy


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='行为金融分析工具 - 精准分析投资人群行为')
    parser.add_argument('symbol', help='股票代码 (如: AAPL, 600519.SS, 0700.HK)')
    parser.add_argument('--type', choices=['sentiment', 'behavior', 'full'], 
                       default='full', help='分析类型')
    parser.add_argument('--period', default='3mo', help='数据周期')
    
    args = parser.parse_args()
    
    analyzer = BehaviorAnalyzer()
    
    if args.type == 'sentiment':
        result = analyzer.get_market_sentiment(args.symbol, period=args.period)
    elif args.type == 'behavior':
        result = analyzer.analyze_investor_behavior(args.symbol, period=args.period)
    else:
        result = analyzer.analyze_investor_behavior(args.symbol, period=args.period)
    
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
