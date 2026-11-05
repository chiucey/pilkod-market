# ===== 完整策略示例：布林带均值回归策略 =====

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class BollingerBandReversionStrategy:
    """
    布林带均值回归策略
    原理：当价格触及布林带下轨时买入，触及上轨时卖出
    适用于震荡市场，趋势市场需配合止损
    """

    def __init__(self,
                 bb_period: int = 20,
                 bb_std: float = 2.0,
                 rsi_period: int = 14,
                 rsi_oversold: float = 30,
                 rsi_overbought: float = 70,
                 position_size: float = 0.1):
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.position_size = position_size

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        result = df.copy()

        # 布林带
        result['bb_middle'] = result['close'].rolling(self.bb_period).mean()
        result['bb_std'] = result['close'].rolling(self.bb_period).std()
        result['bb_upper'] = result['bb_middle'] + (result['bb_std'] * self.bb_std)
        result['bb_lower'] = result['bb_middle'] - (result['bb_std'] * self.bb_std)
        result['bb_position'] = (result['close'] - result['bb_lower']) / (result['bb_upper'] - result['bb_lower'])

        # RSI
        delta = result['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_period).mean()
        rs = gain / loss
        result['rsi'] = 100 - (100 / (1 + rs))

        # ATR (用于止损)
        tr1 = result['high'] - result['low']
        tr2 = abs(result['high'] - result['close'].shift())
        tr3 = abs(result['low'] - result['close'].shift())
        result['atr'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1).rolling(14).mean()

        # 成交量均线
        result['volume_ma'] = result['volume'].rolling(20).mean()
        result['volume_ratio'] = result['volume'] / result['volume_ma']

        return result.dropna()

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        result = self.calculate_indicators(df)

        result['signal'] = 0  # 0: 持有, 1: 买入, -1: 卖出

        # 买入信号：价格触及下轨 + RSI超卖 + 成交量放大
        buy_condition = (
            (result['close'] <= result['bb_lower'] * 1.01) &
            (result['rsi'] < self.rsi_oversold) &
            (result['volume_ratio'] > 1.2)
        )
        result.loc[buy_condition, 'signal'] = 1

        # 卖出信号：价格触及上轨 + RSI超买
        sell_condition = (
            (result['close'] >= result['bb_upper'] * 0.99) &
            (result['rsi'] > self.rsi_overbought)
        )
        result.loc[sell_condition, 'signal'] = -1

        # 止损信号：价格反向运行超过2倍ATR
        # (在实际回测中通过BacktestEngine的风控模块实现)

        return result

    def run_backtest(self, df: pd.DataFrame, initial_capital: float = 1000000) -> dict:
        """运行回测"""
        result = self.generate_signals(df)
        capital = initial_capital
        position = 0
        trades = []
        equity_curve = [initial_capital]

        for i in range(len(result)):
            row = result.iloc[i]

            # 买入
            if row['signal'] == 1 and position == 0:
                shares = int(capital * self.position_size / row['close'])
                if shares > 0:
                    cost = shares * row['close']
                    commission = cost * 0.0003
                    capital -= (cost + commission)
                    position = shares
                    trades.append({
                        'date': row['date'],
                        'type': 'BUY',
                        'price': row['close'],
                        'shares': shares,
                        'commission': commission
                    })

            # 卖出
            elif row['signal'] == -1 and position > 0:
                proceeds = position * row['close']
                commission = proceeds * 0.0003
                capital += (proceeds - commission)
                trades.append({
                    'date': row['date'],
                    'type': 'SELL',
                    'price': row['close'],
                    'shares': position,
                    'commission': commission
                })
                position = 0

            # 更新权益
            if position > 0:
                current_value = capital + position * row['close']
            else:
                current_value = capital
            equity_curve.append(current_value)

        # 计算绩效指标
        equity = np.array(equity_curve)
        returns = np.diff(equity) / equity[:-1]

        total_return = (equity[-1] - initial_capital) / initial_capital
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if returns.std() > 0 else 0
        max_drawdown = np.max(np.maximum.accumulate(equity) - equity) / initial_capital

        winning_trades = [t for t in trades if t['type'] == 'SELL']
        if winning_trades:
            avg_win = np.mean([t['price'] - t['shares'] for t in trades if t['type'] == 'SELL'])

        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'final_capital': equity[-1],
            'equity_curve': equity
        }


# ===== 使用示例 =====
if __name__ == '__main__':
    # 模拟数据
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    close_prices = 100 * np.cumprod(1 + np.random.randn(len(dates)) * 0.02)
    high_prices = close_prices * (1 + np.random.rand(len(dates)) * 0.02)
    low_prices = close_prices * (1 - np.random.rand(len(dates)) * 0.02)
    open_prices = close_prices * (1 + np.random.randn(len(dates)) * 0.01)
    volumes = np.random.randint(1000000, 10000000, len(dates))

    df = pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    })

    # 运行策略
    strategy = BollingerBandReversionStrategy()
    results = strategy.run_backtest(df)

    print("=" * 50)
    print("回测结果")
    print("=" * 50)
    print(f"总收益率: {results['total_return']*100:.2f}%")
    print(f"夏普比率: {results['sharpe_ratio']:.2f}")
    print(f"最大回撤: {results['max_drawdown']*100:.2f}%")
    print(f"总交易次数: {results['total_trades']}")
    print(f"最终资金: {results['final_capital']:.2f}")
