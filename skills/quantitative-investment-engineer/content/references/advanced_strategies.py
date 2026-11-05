# ===== 高级策略模板：多因子量化选股 =====

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FactorConfig:
    """因子配置"""
    name: str
    weight: float
    direction: int  # 1: 值越大越好, -1: 值越小越好
    quantile: float = 0.2  # 取前20%的股票


class MultiFactorSelector:
    """
    多因子量化选股模型
    核心思想：通过多个维度筛选优质股票，构建投资组合
    """

    def __init__(self, factors: List[FactorConfig]):
        self.factors = factors
        self.factor_values: Dict[str, pd.Series] = {}

    def add_factor(self, factor: FactorConfig, values: pd.Series):
        """添加因子"""
        self.factor_values[factor.name] = values

    def calculate_factor_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算因子得分"""
        result = df.copy()

        # 计算每个因子得分
        for factor in self.factors:
            if factor.name not in result.columns:
                continue

            values = result[factor.name]

            # 处理无穷值和NaN
            values = values.replace([np.inf, -np.inf], np.nan)

            # 标准化
            z_score = (values - values.mean()) / values.std()

            # 根据方向调整
            if factor.direction == -1:
                z_score = -z_score

            result[f'{factor.name}_score'] = z_score

        # 计算综合得分
        score_cols = [f'{f.name}_score' for f in self.factors if f.name in result.columns]
        if score_cols:
            weights = [f.weight for f in self.factors if f.name in result.columns]
            total_weight = sum(weights)

            result['composite_score'] = sum(
                result[col] * (w / total_weight)
                for col, w in zip(score_cols, weights)
            )

        return result

    def select_stocks(self, df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
        """选股"""
        scored = self.calculate_factor_scores(df)

        if 'composite_score' not in scored.columns:
            return pd.DataFrame()

        # 按综合得分排序
        selected = scored.nlargest(top_n, 'composite_score')

        return selected[['symbol', 'name', 'composite_score']] + [
            scored.loc[selected.index, f'{f.name}_score']
            for f in self.factors
        ]


# ===== 配对交易策略 =====
class PairsTradingStrategy:
    """
    配对交易策略
    原理：当两只高度相关的股票价格偏离均值时，
    做多被低估的股票，做空被高估的股票，等待价格回归
    """

    def __init__(self, lookback: int = 60, entry_threshold: float = 2.0, exit_threshold: float = 0.5):
        self.lookback = lookback
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.hedge_ratio = 0.0
        self.spread_mean = 0.0
        self.spread_std = 0.0

    def calculate_spread(self, stock1: pd.Series, stock2: pd.Series) -> pd.Series:
        """计算价差"""
        # 使用OLS计算对冲比率
        self.hedge_ratio = np.polyfit(stock2, stock1, 1)[0]

        # 计算价差
        spread = stock1 - self.hedge_ratio * stock2

        # 计算均值和标准差
        self.spread_mean = spread.rolling(self.lookback).mean().iloc[-1]
        self.spread_std = spread.rolling(self.lookback).std().iloc[-1]

        return spread

    def generate_signals(self, spread: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """生成交易信号"""
        z_score = (spread - self.spread_mean) / self.spread_std

        # 标准化价差
        signals = pd.Series(0, index=spread.index)

        # 入场信号
        signals[z_score > self.entry_threshold] = -1  # 做空spread (做多stock2，做空stock1)
        signals[z_score < -self.entry_threshold] = 1   # 做多spread (做多stock1，做空stock2)

        # 平仓信号
        signals[(z_score < self.exit_threshold) & (signals != 0)] = 0
        signals[(z_score > -self.exit_threshold) & (signals != 0)] = 0

        return signals, z_score

    def backtest(self,
                 stock1_prices: pd.Series,
                 stock2_prices: pd.Series,
                 initial_capital: float = 1000000) -> Dict:
        """回测配对交易"""
        spread = self.calculate_spread(stock1_prices, stock2_prices)
        signals, z_score = self.generate_signals(spread)

        capital = initial_capital
        position = 0  # 1: long spread, -1: short spread, 0: flat
        pnl_list = []

        for i in range(self.lookback, len(spread)):
            # 计算收益
            ret1 = (stock1_prices.iloc[i] - stock1_prices.iloc[i-1]) / stock1_prices.iloc[i-1]
            ret2 = (stock2_prices.iloc[i] - stock2_prices.iloc[i-1]) / stock2_prices.iloc[i-1]

            if position == 1:
                pnl = ret1 - self.hedge_ratio * ret2
            elif position == -1:
                pnl = -ret1 + self.hedge_ratio * ret2
            else:
                pnl = 0

            # 更新信号
            new_signal = signals.iloc[i]

            # 执行交易
            if new_signal != 0 and position == 0:
                position = new_signal
            elif new_signal == 0 and position != 0:
                position = 0
                capital *= (1 + pnl)
            else:
                capital *= (1 + pnl)

            pnl_list.append(capital)

        return {
            'final_capital': capital,
            'total_return': (capital - initial_capital) / initial_capital,
            'equity_curve': pnl_list,
            'z_score': z_score,
            'hedge_ratio': self.hedge_ratio
        }


# ===== 统计套利策略模板 =====
class StatArbStrategy:
    """
    统计套利策略
    核心：利用资产的均值回复特性，在价差偏离时建仓，等待回归
    """

    def __init__(self,
                 window: int = 20,
                 entry_z: float = 2.0,
                 exit_z: float = 0.5,
                 holding_period: int = 10):
        self.window = window
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.holding_period = holding_period

    def calculate_zscore(self, prices: pd.Series) -> pd.Series:
        """计算Z分数"""
        ma = prices.rolling(self.window).mean()
        std = prices.rolling(self.window).std()
        return (prices - ma) / std

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """生成信号"""
        result = df.copy()

        # 计算Z分数
        result['zscore'] = self.calculate_zscore(result['spread'])

        # 入场信号
        result['signal'] = 0
        result.loc[result['zscore'] > self.entry_z, 'signal'] = -1
        result.loc[result['zscore'] < -self.entry_z, 'signal'] = 1

        # 平仓信号
        result.loc[abs(result['zscore']) < self.exit_z, 'signal'] = 0

        return result

    def run(self, df: pd.DataFrame, capital: float = 1000000) -> Dict:
        """运行策略"""
        signals = self.generate_signals(df)

        trades = []
        current_position = 0
        entry_price = 0
        entry_idx = 0

        for i in range(len(signals)):
            signal = signals.iloc[i]['signal']

            if current_position == 0:
                if signal != 0:
                    current_position = signal
                    entry_price = signals.iloc[i]['spread']
                    entry_idx = i
            else:
                # 检查止损/止盈
                price_change = (signals.iloc[i]['spread'] - entry_price) / entry_price

                if current_position == 1 and price_change < -0.05:  # 5%止损
                    current_position = 0
                    trades.append({'entry': entry_idx, 'exit': i, 'pnl': price_change, 'type': 'LONG'})
                elif current_position == -1 and price_change > 0.05:
                    current_position = 0
                    trades.append({'entry': entry_idx, 'exit': i, 'pnl': -price_change, 'type': 'SHORT'})
                # 检查到期强制平仓
                elif i - entry_idx >= self.holding_period:
                    current_position = 0
                    pnl = price_change if current_position == 1 else -price_change
                    trades.append({'entry': entry_idx, 'exit': i, 'pnl': pnl, 'type': 'HOLDING_EXPIRE'})

        return {'trades': trades, 'zscore': signals['zscore']}
