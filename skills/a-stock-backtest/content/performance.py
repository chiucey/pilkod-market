# -*- coding: utf-8 -*-
"""
性能评估模块 - 回测绩效指标计算
提供全面的策略绩效评估指标
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """
    绩效分析器
    计算各种风险收益指标
    """

    def __init__(self, equity_curve: pd.DataFrame, trades: pd.DataFrame, benchmark: Optional[pd.Series] = None):
        """
        初始化绩效分析器

        Args:
            equity_curve: 资金曲线DataFrame，需包含total_value和daily_return列
            trades: 交易记录DataFrame
            benchmark: 基准收益率序列（可选）
        """
        self.equity_curve = equity_curve.copy()
        self.trades = trades.copy() if not trades.empty else pd.DataFrame()
        self.benchmark = benchmark

        # 计算收益率序列
        if 'daily_return' in self.equity_curve.columns:
            self.daily_returns = self.equity_curve['daily_return'].dropna()
        else:
            self.daily_returns = self.equity_curve['total_value'].pct_change().dropna()

    def calculate_returns_metrics(self) -> Dict:
        """
        计算收益类指标

        Returns:
            收益指标字典
        """
        total_value = self.equity_curve['total_value']
        initial_value = total_value.iloc[0]

        # 总收益率
        total_return = (total_value.iloc[-1] - initial_value) / initial_value

        # 年化收益率
        trading_days = len(self.equity_curve)
        years = trading_days / 252
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

        # 策略收益
        strategy_returns = self.daily_returns

        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'total_days': trading_days,
            'avg_daily_return': strategy_returns.mean(),
            'cumulative_return': total_return,
        }

    def calculate_risk_metrics(self) -> Dict:
        """
        计算风险类指标

        Returns:
            风险指标字典
        """
        strategy_returns = self.daily_returns

        # 日波动率
        daily_volatility = strategy_returns.std()

        # 年化波动率
        annualized_volatility = daily_volatility * np.sqrt(252)

        # 最大回撤
        cumulative = (1 + strategy_returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # 最大回撤持续期
        drawdown_start = None
        max_duration = 0
        current_duration = 0
        for i, d in enumerate(drawdown):
            if d < 0:
                if drawdown_start is None:
                    drawdown_start = i
                current_duration += 1
                if current_duration > max_duration:
                    max_duration = current_duration
            else:
                drawdown_start = None
                current_duration = 0

        return {
            'daily_volatility': daily_volatility,
            'annualized_volatility': annualized_volatility,
            'max_drawdown': max_drawdown,
            'max_drawdown_duration': max_duration,
            'var_95': np.percentile(strategy_returns, 5),  # 95% VaR
        }

    def calculate_risk_adjusted_metrics(self) -> Dict:
        """
        计算风险调整收益指标

        Returns:
            风险调整收益指标字典
        """
        returns_metrics = self.calculate_returns_metrics()
        risk_metrics = self.calculate_risk_metrics()

        annualized_return = returns_metrics['annualized_return']
        annualized_volatility = risk_metrics['annualized_volatility']
        max_drawdown = abs(risk_metrics['max_drawdown'])

        # 夏普比率
        risk_free_rate = 0.03  # 假设无风险利率3%
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility if annualized_volatility > 0 else 0

        # 卡玛比率
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0

        # 索提诺比率（只考虑下行波动）
        downside_returns = self.daily_returns[self.daily_returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = (annualized_return - risk_free_rate) / downside_volatility if downside_volatility > 0 else 0

        return {
            'sharpe_ratio': sharpe_ratio,
            'calmar_ratio': calmar_ratio,
            'sortino_ratio': sortino_ratio,
            'info_ratio': self._calculate_info_ratio(),
        }

    def _calculate_info_ratio(self) -> float:
        """
        计算信息比率（相对基准）

        Returns:
            信息比率
        """
        if self.benchmark is None:
            return 0.0

        # 对齐日期
        returns = self.daily_returns.reindex(self.benchmark.index).dropna()
        benchmark = self.benchmark.reindex(returns.index).dropna()

        if len(returns) == 0 or len(benchmark) == 0:
            return 0.0

        excess_returns = returns - benchmark
        tracking_error = excess_returns.std() * np.sqrt(252)

        return (excess_returns.mean() * 252) / tracking_error if tracking_error > 0 else 0

    def calculate_trading_metrics(self) -> Dict:
        """
        计算交易类指标

        Returns:
            交易指标字典
        """
        if self.trades.empty:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_profit_per_trade': 0,
                'profit_factor': 0,
            }

        # 简化计算：按交易对计算盈亏
        trades_list = []
        current_position = None
        entry_price = 0
        entry_date = None

        for idx, trade in self.trades.iterrows():
            if trade['type'] == 'buy':
                if current_position is None:
                    current_position = {'shares': 0, 'cost': 0}
                current_position['shares'] += trade['quantity']
                current_position['cost'] += trade['quantity'] * trade['price']
                entry_date = idx
            elif trade['type'] == 'sell' and current_position:
                sell_value = trade['quantity'] * trade['price']
                avg_cost = current_position['cost'] / current_position['shares']
                profit = (trade['price'] - avg_cost) * trade['quantity']

                trades_list.append({
                    'entry_date': entry_date,
                    'exit_date': idx,
                    'profit': profit,
                    'return': profit / (avg_cost * trade['quantity']),
                    'duration': (idx - entry_date).days if entry_date else 0
                })

                current_position['shares'] -= trade['quantity']
                current_position['cost'] = current_position['shares'] * avg_cost

                if current_position['shares'] <= 0:
                    current_position = None

        if not trades_list:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_profit_per_trade': 0,
                'profit_factor': 0,
            }

        trades_df = pd.DataFrame(trades_list)

        # 统计指标
        total_trades = len(trades_df)
        wins = trades_df[trades_df['profit'] > 0]
        losses = trades_df[trades_df['profit'] <= 0]

        win_rate = len(wins) / total_trades if total_trades > 0 else 0
        avg_profit = trades_df['profit'].mean()
        avg_win = wins['profit'].mean() if len(wins) > 0 else 0
        avg_loss = abs(losses['profit'].mean()) if len(losses) > 0 else 0

        # 盈亏比
        profit_ratio = avg_win / avg_loss if avg_loss > 0 else 0

        # 利润因子
        total_profit = wins['profit'].sum() if len(wins) > 0 else 0
        total_loss = abs(losses['profit'].sum()) if len(losses) > 0 else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else 0

        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_profit_per_trade': avg_profit,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_ratio': profit_ratio,
            'profit_factor': profit_factor,
            'max_consecutive_wins': self._max_consecutive(trades_df['profit'] > 0),
            'max_consecutive_losses': self._max_consecutive(trades_df['profit'] <= 0),
        }

    def _max_consecutive(self, conditions: pd.Series) -> int:
        """计算最大连续次数"""
        max_count = 0
        current_count = 0
        for cond in conditions:
            if cond:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        return max_count

    def calculate_monthly_returns(self) -> pd.DataFrame:
        """
        计算月度收益率

        Returns:
            月度收益率DataFrame
        """
        if 'total_value' not in self.equity_curve.columns:
            return pd.DataFrame()

        df = self.equity_curve.copy()
        df['month'] = df.index.to_period('M')
        df['return'] = df['total_value'].pct_change()

        monthly = df.groupby('month').apply(
            lambda x: (x['total_value'].iloc[-1] / x['total_value'].iloc[0]) - 1
        )

        return monthly

    def get_full_report(self) -> Dict:
        """
        获取完整绩效报告

        Returns:
            完整绩效指标字典
        """
        report = {}

        report.update(self.calculate_returns_metrics())
        report.update(self.calculate_risk_metrics())
        report.update(self.calculate_risk_adjusted_metrics())
        report.update(self.calculate_trading_metrics())

        return report

    def print_report(self) -> None:
        """打印绩效报告"""
        report = self.get_full_report()

        print("=" * 60)
        print("量化策略绩效报告")
        print("=" * 60)

        print("\n【收益指标】")
        print(f"  总收益率:        {report['total_return']*100:.2f}%")
        print(f"  年化收益率:      {report['annualized_return']*100:.2f}%")
        print(f"  交易天数:        {report['total_days']}天")
        print(f"  日均收益率:      {report['avg_daily_return']*100:.4f}%")

        print("\n【风险指标】")
        print(f"  日波动率:        {report['daily_volatility']*100:.4f}%")
        print(f"  年化波动率:      {report['annualized_volatility']*100:.2f}%")
        print(f"  最大回撤:        {report['max_drawdown']*100:.2f}%")
        print(f"  最大回撤天数:    {report['max_drawdown_duration']}天")
        print(f"  95% VaR:        {report['var_95']*100:.2f}%")

        print("\n【风险调整收益】")
        print(f"  夏普比率:        {report['sharpe_ratio']:.4f}")
        print(f"  卡玛比率:        {report['calmar_ratio']:.4f}")
        print(f"  索提诺比率:      {report['sortino_ratio']:.4f}")

        print("\n【交易统计】")
        print(f"  总交易次数:      {report['total_trades']}")
        print(f"  胜率:            {report['win_rate']*100:.2f}%")
        print(f"  平均盈亏:        ¥{report['avg_profit_per_trade']:.2f}")
        print(f"  平均盈利:        ¥{report['avg_win']:.2f}")
        print(f"  平均亏损:        ¥{report['avg_loss']:.2f}")
        print(f"  盈亏比:          {report['profit_ratio']:.2f}")
        print(f"  利润因子:        {report['profit_factor']:.2f}")
        print(f"  最大连续盈利:    {report['max_consecutive_wins']}次")
        print(f"  最大连续亏损:    {report['max_consecutive_losses']}次")

        print("\n" + "=" * 60)


def generate_performance_report(
    equity_curve: pd.DataFrame,
    trades: pd.DataFrame,
    output_path: Optional[str] = None
) -> Dict:
    """
    生成完整绩效报告

    Args:
        equity_curve: 资金曲线
        trades: 交易记录
        output_path: 输出文件路径（可选）

    Returns:
        绩效指标字典
    """
    analyzer = PerformanceAnalyzer(equity_curve, trades)
    report = analyzer.get_full_report()

    if output_path:
        # 保存为CSV
        report_df = pd.DataFrame([report])
        report_df.to_csv(output_path, index=False)
        logger.info(f"绩效报告已保存: {output_path}")

    return report


if __name__ == "__main__":
    # 测试绩效分析
    print("=" * 60)
    print("绩效分析测试")
    print("=" * 60)

    # 模拟数据
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='B')
    np.random.seed(42)

    equity = pd.DataFrame({
        'date': dates,
        'total_value': 1000000 * (1 + np.random.randn(len(dates)) * 0.01).cumprod(),
    })
    equity['daily_return'] = equity['total_value'].pct_change()
    equity.set_index('date', inplace=True)

    # 计算绩效
    analyzer = PerformanceAnalyzer(equity, pd.DataFrame())
    analyzer.print_report()
