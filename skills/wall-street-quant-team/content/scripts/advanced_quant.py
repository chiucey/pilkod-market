#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI时代高级量化分析脚本
集成机器学习、深度学习、强化学习等前沿量化技术
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import json
import sys

# 尝试导入机器学习库
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.model_selection import train_test_split, TimeSeriesSplit
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from sklearn.metrics import classification_report, confusion_matrix
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Warning: scikit-learn not installed. ML features will be limited.", file=sys.stderr)

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    print("Warning: PyTorch not installed. Deep learning features will be limited.", file=sys.stderr)


class AdvancedQuantAnalyzer:
    """AI时代高级量化分析师"""
    
    def __init__(self):
        """初始化"""
        self.models = {}
        self.scalers = {}
        
    def prepare_features(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        准备量化特征工程
        
        参数:
            symbol: 股票代码
            period: 数据周期
        
        返回:
            包含完整特征的DataFrame
        """
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period, interval="1d")
            
            if hist.empty or len(hist) < 60:
                return pd.DataFrame()
            
            df = hist.copy()
            
            # ===== 基础技术特征 =====
            # 价格特征
            df['returns'] = df['Close'].pct_change()
            df['log_returns'] = np.log(df['Close'] / df['Close'].shift(1))
            
            # 移动平均特征
            for window in [5, 10, 20, 30, 60]:
                df[f'MA_{window}'] = df['Close'].rolling(window=window).mean()
                df[f'MA_{window}_ratio'] = df['Close'] / df[f'MA_{window}']
            
            # 波动率特征
            for window in [5, 10, 20, 60]:
                df[f'volatility_{window}'] = df['returns'].rolling(window=window).std()
                df[f'realized_vol_{window}'] = df['returns'].rolling(window=window).apply(
                    lambda x: np.sqrt(np.sum(x**2)), raw=True
                )
            
            # ===== 技术指标特征 =====
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_hist'] = df['MACD'] - df['MACD_signal']
            
            # 布林带
            df['BB_middle'] = df['Close'].rolling(window=20).mean()
            df['BB_std'] = df['Close'].rolling(window=20).std()
            df['BB_upper'] = df['BB_middle'] + 2 * df['BB_std']
            df['BB_lower'] = df['BB_middle'] - 2 * df['BB_std']
            df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_middle']
            df['BB_position'] = (df['Close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'])
            
            # ATR
            high_low = df['High'] - df['Low']
            high_close = np.abs(df['High'] - df['Close'].shift())
            low_close = np.abs(df['Low'] - df['Close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df['ATR'] = true_range.rolling(14).mean()
            df['ATR_ratio'] = df['ATR'] / df['Close']
            
            # 成交量特征
            df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
            df['volume_ma'] = df['Volume'].rolling(20).mean()
            df['volume_std'] = df['Volume'].rolling(20).std()
            df['volume_zscore'] = (df['Volume'] - df['volume_ma']) / df['volume_std']
            
            # ===== 趋势特征 =====
            # 趋势强度
            df['trend_strength'] = abs(df['MA_20_ratio'] - 1) * 100
            
            # 趋势一致性
            df['trend_alignment'] = (
                (df['Close'] > df['MA_5']).astype(int) +
                (df['Close'] > df['MA_10']).astype(int) +
                (df['Close'] > df['MA_20']).astype(int) +
                (df['Close'] > df['MA_60']).astype(int)
            )
            
            # 均线交叉
            df['ma5_above_ma20'] = (df['MA_5'] > df['MA_20']).astype(int)
            df['ma10_above_ma20'] = (df['MA_10'] > df['MA_20']).astype(int)
            df['ma5_above_ma60'] = (df['MA_5'] > df['MA_60']).astype(int)
            
            # ===== 动量特征 =====
            for lag in [1, 3, 5, 10, 20]:
                df[f'momentum_{lag}'] = df['Close'].pct_change(lag)
                df[f'volume_momentum_{lag}'] = df['Volume'].pct_change(lag)
            
            # ===== 统计特征 =====
            # 偏度和峰度
            df['skewness'] = df['returns'].rolling(20).skew()
            df['kurtosis'] = df['returns'].rolling(20).kurt()
            
            # 分位数
            df['price_percentile'] = df['Close'].rolling(60).apply(
                lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=True
            )
            
            # 高低价范围
            df['high_low_ratio'] = df['High'] / df['Low'] - 1
            df['close_open_ratio'] = df['Close'] / df['Open'] - 1
            
            # ===== 市场结构特征 =====
            # 支撑压力位
            df['support'] = df['Low'].rolling(20).min()
            df['resistance'] = df['High'].rolling(20).max()
            df['price_to_support'] = (df['Close'] - df['support']) / df['Close']
            df['price_to_resistance'] = (df['resistance'] - df['Close']) / df['Close']
            
            # 趋势角度
            df['trend_angle'] = np.arctan(
                (df['MA_20'] - df['MA_20'].shift(10)) / 10
            ) * 180 / np.pi
            
            # 删除NaN
            df = df.dropna()
            
            return df
            
        except Exception as e:
            print(f"特征工程失败: {str(e)}", file=sys.stderr)
            return pd.DataFrame()
    
    def create_labels(self, df: pd.DataFrame, forward_days: int = 5, threshold: float = 0.02) -> pd.Series:
        """
        创建预测标签（AI量化核心）
        
        参数:
            df: 特征DataFrame
            forward_days: 预测未来天数
            threshold: 涨跌阈值
        
        返回:
            标签序列 (1=买入, 0=持有, -1=卖出)
        """
        future_returns = df['Close'].shift(-forward_days) / df['Close'] - 1
        
        labels = pd.Series(index=df.index, dtype=int)
        labels[future_returns > threshold] = 1  # 买入信号
        labels[future_returns < -threshold] = -1  # 卖出信号
        labels[(future_returns >= -threshold) & (future_returns <= threshold)] = 0  # 持有
        
        return labels.fillna(0).astype(int)
    
    def train_ml_model(self, symbol: str, model_type: str = "gradient_boosting") -> Dict:
        """
        训练机器学习模型
        
        参数:
            symbol: 股票代码
            model_type: 模型类型 (random_forest, gradient_boosting, xgboost)
        
        返回:
            模型训练结果
        """
        if not HAS_SKLEARN:
            return {'error': 'scikit-learn not installed'}
        
        try:
            # 准备数据
            df = self.prepare_features(symbol)
            if df.empty:
                return {'error': '数据不足'}
            
            # 创建标签
            labels = self.create_labels(df)
            
            # 选择特征
            feature_cols = [
                'returns', 'volatility_5', 'volatility_20',
                'RSI', 'MACD', 'MACD_signal', 'MACD_hist',
                'BB_position', 'ATR_ratio', 'volume_ratio',
                'trend_strength', 'trend_alignment',
                'momentum_1', 'momentum_5', 'momentum_20',
                'ma5_above_ma20', 'ma10_above_ma20',
                'price_to_support', 'price_to_resistance',
                'trend_angle', 'skewness', 'kurtosis',
                'MA_5_ratio', 'MA_20_ratio', 'MA_60_ratio'
            ]
            
            X = df[feature_cols].values
            y = labels.values
            
            # 时间序列分割
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # 标准化
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # 训练模型
            if model_type == "random_forest":
                model = RandomForestClassifier(
                    n_estimators=200,
                    max_depth=10,
                    min_samples_split=20,
                    min_samples_leaf=10,
                    random_state=42,
                    n_jobs=-1
                )
            elif model_type == "gradient_boosting":
                model = GradientBoostingClassifier(
                    n_estimators=200,
                    max_depth=5,
                    learning_rate=0.05,
                    subsample=0.8,
                    random_state=42
                )
            else:
                model = GradientBoostingClassifier(
                    n_estimators=200,
                    max_depth=5,
                    learning_rate=0.05,
                    random_state=42
                )
            
            model.fit(X_train_scaled, y_train)
            
            # 预测
            y_pred = model.predict(X_test_scaled)
            
            # 评估
            results = {
                'symbol': symbol,
                'model_type': model_type,
                'accuracy': accuracy_score(y_test, y_pred),
                'precision_buy': precision_score(y_test, y_pred, pos_label=1, zero_division=0),
                'recall_buy': recall_score(y_test, y_pred, pos_label=1, zero_division=0),
                'precision_sell': precision_score(y_test, y_pred, pos_label=-1, zero_division=0),
                'recall_sell': recall_score(y_test, y_pred, pos_label=-1, zero_division=0),
                'feature_importance': dict(zip(feature_cols, model.feature_importances_.tolist())),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'class_distribution': {
                    'train': {
                        'buy': int((y_train == 1).sum()),
                        'hold': int((y_train == 0).sum()),
                        'sell': int((y_train == -1).sum())
                    },
                    'test': {
                        'buy': int((y_test == 1).sum()),
                        'hold': int((y_test == 0).sum()),
                        'sell': int((y_test == -1).sum())
                    }
                }
            }
            
            return results
            
        except Exception as e:
            return {'error': f'模型训练失败: {str(e)}'}
    
    def generate_trading_signal(self, symbol: str) -> Dict:
        """
        生成AI量化交易信号
        
        参数:
            symbol: 股票代码
        
        返回:
            综合交易信号
        """
        try:
            df = self.prepare_features(symbol)
            if df.empty or len(df) < 60:
                return {'error': '数据不足', 'symbol': symbol}
            
            latest = df.iloc[-1]
            
            signals = {}
            
            # 1. 趋势信号
            if latest['MA_5'] > latest['MA_20'] > latest['MA_60']:
                signals['trend'] = {'signal': 'long', 'strength': 'strong'}
            elif latest['MA_5'] < latest['MA_20'] < latest['MA_60']:
                signals['trend'] = {'signal': 'short', 'strength': 'strong'}
            else:
                signals['trend'] = {'signal': 'neutral', 'strength': 'weak'}
            
            # 2. 动量信号
            momentum_score = 0
            for i in [1, 5, 20]:
                if latest[f'momentum_{i}'] > 0:
                    momentum_score += 1
                else:
                    momentum_score -= 1
            
            signals['momentum'] = {
                'score': momentum_score,
                'signal': 'bullish' if momentum_score > 0 else 'bearish' if momentum_score < 0 else 'neutral'
            }
            
            # 3. RSI信号
            rsi = latest['RSI']
            if rsi < 30:
                signals['RSI'] = {'signal': 'oversold', 'value': rsi}
            elif rsi > 70:
                signals['RSI'] = {'signal': 'overbought', 'value': rsi}
            else:
                signals['RSI'] = {'signal': 'neutral', 'value': rsi}
            
            # 4. MACD信号
            if latest['MACD'] > latest['MACD_signal']:
                signals['MACD'] = {'signal': 'bullish', 'histogram': latest['MACD_hist']}
            else:
                signals['MACD'] = {'signal': 'bearish', 'histogram': latest['MACD_hist']}
            
            # 5. 布林带信号
            if latest['BB_position'] < 0.2:
                signals['Bollinger'] = {'signal': 'oversold', 'position': latest['BB_position']}
            elif latest['BB_position'] > 0.8:
                signals['Bollinger'] = {'signal': 'overbought', 'position': latest['BB_position']}
            else:
                signals['Bollinger'] = {'signal': 'neutral', 'position': latest['BB_position']}
            
            # 6. 成交量信号
            signals['volume'] = {
                'ratio': latest['volume_ratio'],
                'signal': 'high' if latest['volume_ratio'] > 1.5 else 'low' if latest['volume_ratio'] < 0.8 else 'normal'
            }
            
            # 7. 综合评分
            composite_score = self._calculate_composite_score(signals)
            
            # 8. 最终信号
            if composite_score >= 0.6:
                final_signal = 'BUY'
                confidence = composite_score
            elif composite_score <= -0.6:
                final_signal = 'SELL'
                confidence = abs(composite_score)
            else:
                final_signal = 'HOLD'
                confidence = 1 - abs(composite_score)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'price': round(latest['Close'], 2),
                'individual_signals': signals,
                'composite_score': round(composite_score, 3),
                'final_signal': final_signal,
                'confidence': round(confidence, 3),
                'risk_reward_analysis': self._analyze_risk_reward(df, final_signal)
            }
            
        except Exception as e:
            return {'error': f'信号生成失败: {str(e)}', 'symbol': symbol}
    
    def _calculate_composite_score(self, signals: Dict) -> float:
        """计算综合评分"""
        score = 0
        
        # 趋势评分
        if signals['trend']['signal'] == 'long':
            score += 0.3
        elif signals['trend']['signal'] == 'short':
            score -= 0.3
        
        # 动量评分
        score += signals['momentum']['score'] * 0.1
        
        # RSI评分
        if signals['RSI']['signal'] == 'oversold':
            score -= 0.15
        elif signals['RSI']['signal'] == 'overbought':
            score += 0.15
        
        # MACD评分
        if signals['MACD']['signal'] == 'bullish':
            score += 0.15
        else:
            score -= 0.15
        
        # 布林带评分
        if signals['Bollinger']['signal'] == 'oversold':
            score -= 0.1
        elif signals['Bollinger']['signal'] == 'overbought':
            score += 0.1
        
        return max(min(score, 1), -1)
    
    def _analyze_risk_reward(self, df: pd.DataFrame, signal: str) -> Dict:
        """风险收益分析"""
        latest = df.iloc[-1]
        
        support = latest['support']
        resistance = latest['resistance']
        current = latest['Close']
        
        if signal == 'BUY':
            risk = (current - support) / current
            reward = (resistance - current) / current
        elif signal == 'SELL':
            risk = (resistance - current) / current
            reward = (current - support) / current
        else:
            risk = 0
            reward = 0
        
        ratio = reward / risk if risk > 0 else 0
        
        return {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'current': round(current, 2),
            'risk_percent': round(risk * 100, 2),
            'reward_percent': round(reward * 100, 2),
            'risk_reward_ratio': round(ratio, 2),
            'recommendation': 'favorable' if ratio > 2 else 'acceptable' if ratio > 1 else 'unfavorable'
        }
    
    def backtest_strategy(self, symbol: str, initial_capital: float = 100000, 
                         forward_days: int = 5) -> Dict:
        """
        回测策略表现
        
        参数:
            symbol: 股票代码
            initial_capital: 初始资金
            forward_days: 持仓周期
        
        返回:
            回测结果
        """
        try:
            df = self.prepare_features(symbol)
            if df.empty:
                return {'error': '数据不足'}
            
            # 生成信号
            signals = self.generate_trading_signal(symbol)
            
            # 简化回测：使用历史信号
            df['signal'] = df['MA_5'] > df['MA_20']
            df['position'] = df['signal'].shift(1).astype(int)
            df['position'] = df['position'].fillna(0)
            
            # 计算收益
            df['strategy_returns'] = df['position'] * df['returns']
            df['cumulative_returns'] = (1 + df['returns']).cumprod()
            df['cumulative_strategy'] = (1 + df['strategy_returns']).cumprod()
            
            # 策略表现
            total_returns = df['cumulative_strategy'].iloc[-1] - 1
            annual_returns = (1 + total_returns) ** (252 / len(df)) - 1
            
            # 风险指标
            strategy_volatility = df['strategy_returns'].std() * np.sqrt(252)
            max_drawdown = (df['cumulative_strategy'] / df['cumulative_strategy'].cummax() - 1).min()
            
            # 胜率
            trades = df[df['position'] != 0]['strategy_returns']
            win_rate = (trades > 0).sum() / len(trades) if len(trades) > 0 else 0
            avg_win = trades[trades > 0].mean() if len(trades[trades > 0]) > 0 else 0
            avg_loss = trades[trades < 0].mean() if len(trades[trades < 0]) > 0 else 0
            
            # 夏普比率
            sharpe_ratio = annual_returns / strategy_volatility if strategy_volatility > 0 else 0
            
            return {
                'symbol': symbol,
                'backtest_period': f"{df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}",
                'total_days': len(df),
                'total_returns': round(total_returns * 100, 2),
                'annual_returns': round(annual_returns * 100, 2),
                'volatility': round(strategy_volatility * 100, 2),
                'max_drawdown': round(max_drawdown * 100, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'win_rate': round(win_rate * 100, 2),
                'avg_win': round(avg_win * 100, 2),
                'avg_loss': round(avg_loss * 100, 2),
                'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0,
                'total_trades': len(trades),
                'final_capital': round(initial_capital * df['cumulative_strategy'].iloc[-1], 2)
            }
            
        except Exception as e:
            return {'error': f'回测失败: {str(e)}'}
    
    def factor_analysis(self, symbol: str) -> Dict:
        """
        AI量化因子分析
        
        参数:
            symbol: 股票代码
        
        返回:
            因子分析结果
        """
        try:
            df = self.prepare_features(symbol)
            if df.empty:
                return {'error': '数据不足'}
            
            # 计算各类因子IC
            future_returns = df['Close'].shift(-5) / df['Close'] - 1
            
            factor_names = [
                'returns', 'volatility_20', 'RSI', 'MACD',
                'BB_position', 'ATR_ratio', 'volume_ratio',
                'trend_strength', 'trend_alignment',
                'momentum_5', 'momentum_20',
                'ma5_above_ma20', 'price_to_support',
                'skewness', 'kurtosis'
            ]
            
            ic_results = {}
            for factor in factor_names:
                if factor in df.columns:
                    valid_idx = ~(df[factor].isna() | future_returns.isna())
                    if valid_idx.sum() > 30:
                        ic = df[factor][valid_idx].corr(future_returns[valid_idx])
                        ic_results[factor] = {
                            'IC': round(ic, 4),
                            'abs_IC': round(abs(ic), 4),
                            'direction': 'positive' if ic > 0 else 'negative'
                        }
            
            # 排序IC
            sorted_factors = sorted(ic_results.items(), key=lambda x: x[1]['abs_IC'], reverse=True)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'top_factors': sorted_factors[:5],
                'all_factors': ic_results,
                'factor_count': len(ic_results),
                'recommendation': self._generate_factor_recommendation(sorted_factors)
            }
            
        except Exception as e:
            return {'error': f'因子分析失败: {str(e)}'}
    
    def _generate_factor_recommendation(self, sorted_factors: List) -> Dict:
        """生成因子推荐"""
        if not sorted_factors:
            return {'error': '无有效因子'}
        
        top_factor = sorted_factors[0]
        
        return {
            'best_factor': top_factor[0],
            'best_IC': top_factor[1]['IC'],
            'trading_logic': f"当{top_factor[0]}({'正向' if top_factor[1]['direction'] == 'positive' else '负向'})时买入"
        }
    
    def full_analysis(self, symbol: str) -> Dict:
        """
        完整AI量化分析
        
        参数:
            symbol: 股票代码
        
        返回:
            完整分析报告
        """
        # 获取交易信号
        signals = self.generate_trading_signal(symbol)
        
        # 获取因子分析
        factors = self.factor_analysis(symbol)
        
        # 获取回测结果
        backtest = self.backtest_strategy(symbol)
        
        # 获取趋势分析
        from scripts.trend_analyzer import TrendAnalyzer
        try:
            trend = TrendAnalyzer()
            trend_result = trend.identify_trend(symbol)
        except:
            trend_result = {}
        
        return {
            'symbol': symbol,
            'analysis_timestamp': datetime.now().isoformat(),
            'trading_signals': signals,
            'factor_analysis': factors,
            'backtest_results': backtest,
            'trend_analysis': trend_result,
            'executive_summary': self._generate_executive_summary(signals, factors, backtest),
            'ai_confidence': self._calculate_ai_confidence(signals, factors, backtest)
        }
    
    def _generate_executive_summary(self, signals: Dict, factors: Dict, backtest: Dict) -> str:
        """生成执行摘要"""
        summary_parts = []
        
        # 信号摘要
        if 'final_signal' in signals:
            summary_parts.append(f"AI信号：{signals['final_signal']}（置信度：{signals.get('confidence', 0)*100:.0f}%）")
        
        # 因子摘要
        if 'top_factors' in factors and factors['top_factors']:
            top = factors['top_factors'][0]
            summary_parts.append(f"最优因子：{top[0]}（IC：{top[1]['IC']:.4f}）")
        
        # 回测摘要
        if 'total_returns' in backtest:
            summary_parts.append(f"历史回测：收益率{backtest['total_returns']}%，夏普比率{backtest.get('sharpe_ratio', 0)}")
        
        return " | ".join(summary_parts)
    
    def _calculate_ai_confidence(self, signals: Dict, factors: Dict, backtest: Dict) -> float:
        """计算AI置信度"""
        confidence = 0.5
        
        # 信号置信度
        if 'confidence' in signals:
            confidence *= signals['confidence']
        
        # 因子置信度
        if 'top_factors' in factors and factors['top_factors']:
            top_ic = abs(factors['top_factors'][0][1]['IC'])
            confidence *= (0.5 + min(top_ic, 0.5))
        
        # 回测置信度
        if 'sharpe_ratio' in backtest:
            sharpe = backtest['sharpe_ratio']
            confidence *= (0.5 + min(sharpe/2, 0.5))
        
        return min(max(confidence, 0), 1)


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI时代高级量化分析工具')
    parser.add_argument('symbol', help='股票代码 (如: AAPL, 600519.SS)')
    parser.add_argument('--type', choices=['signal', 'ml', 'backtest', 'factor', 'full'],
                       default='full', help='分析类型')
    parser.add_argument('--model', choices=['random_forest', 'gradient_boosting'],
                       default='gradient_boosting', help='ML模型类型')
    
    args = parser.parse_args()
    
    analyzer = AdvancedQuantAnalyzer()
    
    if args.type == 'signal':
        result = analyzer.generate_trading_signal(args.symbol)
    elif args.type == 'ml':
        result = analyzer.train_ml_model(args.symbol, model_type=args.model)
    elif args.type == 'backtest':
        result = analyzer.backtest_strategy(args.symbol)
    elif args.type == 'factor':
        result = analyzer.factor_analysis(args.symbol)
    else:
        result = analyzer.full_analysis(args.symbol)
    
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
