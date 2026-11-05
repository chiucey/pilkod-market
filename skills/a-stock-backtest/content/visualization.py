# -*- coding: utf-8 -*-
"""
可视化模块 - 回测结果可视化
使用Matplotlib生成回测分析图表
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import seaborn as sns

from config import VISUALIZATION_CONFIG

logger = logging.getLogger(__name__)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
plt.style.use('seaborn-v0_8-whitegrid')


class BacktestVisualizer:
    """
    回测可视化类
    生成各种回测分析图表
    """

    def __init__(self, figsize: Tuple[int, int] = None, dpi: int = None):
        """
        初始化可视化器

        Args:
            figsize: 图表尺寸
            dpi: 分辨率
        """
        self.figsize = figsize or VISUALIZATION_CONFIG.get('figsize', (14, 8))
        self.dpi = dpi or VISUALIZATION_CONFIG.get('dpi', 100)

    def plot_equity_curve(
        self,
        equity_curve: pd.DataFrame,
        title: str = "Equity Curve",
        show_cumulative_return: bool = True,
    ) -> Figure:
        """
        绘制资金曲线

        Args:
            equity_curve: 资金曲线DataFrame
            title: 图表标题

        Returns:
            matplotlib Figure对象
        """
        fig, axes = plt.subplots(2, 1, figsize=self.figsize, dpi=self.dpi, sharex=True)

        # 上图：资产价值
        ax1 = axes[0]
        ax1.plot(equity_curve.index, equity_curve['total_value'], linewidth=2, label='Total Value')
        ax1.fill_between(
            equity_curve.index,
            equity_curve['total_value'],
            alpha=0.3
        )
        ax1.set_ylabel('Total Value (CNY)', fontsize=12)
        ax1.set_title(title, fontsize=14, fontweight='bold')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        # 标注初始资金
        initial_value = equity_curve['total_value'].iloc[0]
        ax1.axhline(y=initial_value, color='gray', linestyle='--', alpha=0.7, label='Initial')

        # 下图：日收益率
        ax2 = axes[1]
        if 'daily_return' in equity_curve.columns:
            colors = ['green' if x >= 0 else 'red' for x in equity_curve['daily_return'].fillna(0)]
            ax2.bar(equity_curve.index, equity_curve['daily_return'] * 100, color=colors, alpha=0.7)
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax2.set_ylabel('Daily Return (%)', fontsize=12)
            ax2.set_xlabel('Date', fontsize=12)
            ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def plot_drawdown(
        self,
        equity_curve: pd.DataFrame,
        title: str = "Drawdown Analysis",
    ) -> Figure:
        """
        绘制回撤分析图

        Args:
            equity_curve: 资金曲线DataFrame
            title: 图表标题

        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # 计算回撤
        cumulative = equity_curve['total_value']
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max * 100

        # 绘制回撤曲线
        ax.fill_between(drawdown.index, drawdown, 0, alpha=0.5, color='red')
        ax.plot(drawdown.index, drawdown, color='darkred', linewidth=1)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # 标注最大回撤
        max_dd = drawdown.min()
        max_dd_date = drawdown.idxmin()
        ax.annotate(
            f'Max Drawdown: {max_dd:.2f}%',
            xy=(max_dd_date, max_dd),
            xytext=(max_dd_date, max_dd - 5),
            fontsize=10,
            arrowprops=dict(arrowstyle='->', color='black'),
        )

        plt.tight_layout()
        return fig

    def plot_returns_distribution(
        self,
        equity_curve: pd.DataFrame,
        title: str = "Returns Distribution",
    ) -> Figure:
        """
        绘制收益分布图

        Args:
            equity_curve: 资金曲线DataFrame
            title: 图表标题

        Returns:
            matplotlib Figure对象
        """
        fig, axes = plt.subplots(1, 2, figsize=self.figsize, dpi=self.dpi)

        # 日收益率直方图
        ax1 = axes[0]
        if 'daily_return' in equity_curve.columns:
            returns = equity_curve['daily_return'].dropna() * 100
            ax1.hist(returns, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
            ax1.axvline(x=returns.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {returns.mean():.3f}%')
            ax1.set_xlabel('Daily Return (%)', fontsize=12)
            ax1.set_ylabel('Frequency', fontsize=12)
            ax1.set_title('Daily Returns Distribution', fontsize=12)
            ax1.legend()
            ax1.grid(True, alpha=0.3)

        # 月度收益柱状图
        ax2 = axes[1]
        monthly = equity_curve['total_value'].resample('ME').last().pct_change().dropna() * 100
        if not monthly.empty:
            colors = ['green' if x >= 0 else 'red' for x in monthly]
            ax2.bar(
                range(len(monthly)),
                monthly,
                color=colors,
                alpha=0.7
            )
            ax2.set_xticks(range(len(monthly)))
            ax2.set_xticklabels([d.strftime('%Y-%m') for d in monthly.index], rotation=45, ha='right')
            ax2.set_xlabel('Month', fontsize=12)
            ax2.set_ylabel('Monthly Return (%)', fontsize=12)
            ax2.set_title('Monthly Returns', fontsize=12)
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax2.grid(True, alpha=0.3)

        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig

    def plot_trades(
        self,
        equity_curve: pd.DataFrame,
        trades: pd.DataFrame,
        title: str = "Trading Activity",
    ) -> Figure:
        """
        绘制交易记录图

        Args:
            equity_curve: 资金曲线DataFrame
            trades: 交易记录DataFrame
            title: 图表标题

        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # 资金曲线
        ax.plot(equity_curve.index, equity_curve['total_value'], linewidth=2, label='Equity', color='blue')

        if not trades.empty:
            # 买入点
            buy_trades = trades[trades['type'] == 'buy']
            if not buy_trades.empty:
                buy_dates = buy_trades.index
                buy_values = [equity_curve.loc[d, 'total_value'] for d in buy_dates if d in equity_curve.index]
                ax.scatter(buy_dates[:len(buy_values)], buy_values, color='green', marker='^', s=100, label='Buy', zorder=5)

            # 卖出点
            sell_trades = trades[trades['type'] == 'sell']
            if not sell_trades.empty:
                sell_dates = sell_trades.index
                sell_values = [equity_curve.loc[d, 'total_value'] for d in sell_dates if d in equity_curve.index]
                ax.scatter(sell_dates[:len(sell_values)], sell_values, color='red', marker='v', s=100, label='Sell', zorder=5)

        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Total Value (CNY)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def plot_monthly_returns_heatmap(
        self,
        equity_curve: pd.DataFrame,
        title: str = "Monthly Returns Heatmap",
    ) -> Figure:
        """
        绘制月度收益热力图

        Args:
            equity_curve: 资金曲线DataFrame
            title: 图表标题

        Returns:
            matplotlib Figure对象
        """
        # 计算月度收益率
        monthly = equity_curve['total_value'].resample('ME').last().pct_change().dropna() * 100
        monthly.index = monthly.index.to_period('M')

        if monthly.empty:
            return plt.figure()

        # 转换为年-月矩阵
        monthly_df = monthly.to_frame('return')
        monthly_df['year'] = monthly_df.index.year
        monthly_df['month'] = monthly_df.index.month
        pivot = monthly_df.pivot(index='year', columns='month', values='return')

        # 绘制热力图
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        sns.heatmap(
            pivot,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            center=0,
            ax=ax,
            cbar_kws={'label': 'Return (%)'},
        )
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Year', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')

        # 设置月份标签
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ax.set_xticklabels(month_labels[:len(pivot.columns)])

        plt.tight_layout()
        return fig

    def plot_performance_summary(
        self,
        metrics: Dict,
        title: str = "Performance Summary",
    ) -> Figure:
        """
        绘制绩效指标汇总

        Args:
            metrics: 绩效指标字典
            title: 图表标题

        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=(10, 6), dpi=self.dpi)

        # 绩效指标
        performance_data = {
            'Total Return': metrics.get('total_return', 0) * 100,
            'Annualized Return': metrics.get('annualized_return', 0) * 100,
            'Sharpe Ratio': metrics.get('sharpe_ratio', 0),
            'Max Drawdown': metrics.get('max_drawdown', 0) * 100,
            'Win Rate': metrics.get('win_rate', 0) * 100,
        }

        # 横向柱状图
        y_pos = np.arange(len(performance_data))
        colors = ['steelblue' if 'Return' in k or 'Rate' in k else 'coral' for k in performance_data.keys()]

        bars = ax.barh(y_pos, list(performance_data.values()), color=colors, alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(list(performance_data.keys()))
        ax.set_xlabel('Value', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')

        # 添加数值标签
        for i, (bar, value) in enumerate(zip(bars, performance_data.values())):
            if 'Ratio' in list(performance_data.keys())[i]:
                label = f'{value:.2f}'
            else:
                label = f'{value:.2f}%'
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, label, va='center')

        ax.grid(True, axis='x', alpha=0.3)
        plt.tight_layout()
        return fig


def create_backtest_report(
    equity_curve: pd.DataFrame,
    trades: pd.DataFrame,
    metrics: Dict,
    output_dir: str,
    show_plots: bool = False,
) -> List[str]:
    """
    创建完整回测报告

    Args:
        equity_curve: 资金曲线DataFrame
        trades: 交易记录DataFrame
        metrics: 绩效指标字典
        output_dir: 输出目录
        show_plots: 是否显示图表

    Returns:
        保存的文件路径列表
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    saved_files = []

    # 创建可视化器
    visualizer = BacktestVisualizer()

    # 1. 资金曲线
    try:
        fig = visualizer.plot_equity_curve(equity_curve, "Backtest Equity Curve")
        filepath = output_path / "equity_curve.png"
        fig.savefig(filepath, dpi=100, bbox_inches='tight')
        saved_files.append(str(filepath))
        logger.info(f"Saved: {filepath}")
        if not show_plots:
            plt.close(fig)
    except Exception as e:
        logger.warning(f"Failed to save equity curve: {e}")

    # 2. 回撤分析
    try:
        fig = visualizer.plot_drawdown(equity_curve, "Drawdown Analysis")
        filepath = output_path / "drawdown.png"
        fig.savefig(filepath, dpi=100, bbox_inches='tight')
        saved_files.append(str(filepath))
        logger.info(f"Saved: {filepath}")
        if not show_plots:
            plt.close(fig)
    except Exception as e:
        logger.warning(f"Failed to save drawdown: {e}")

    # 3. 收益分布
    try:
        fig = visualizer.plot_returns_distribution(equity_curve, "Returns Distribution")
        filepath = output_path / "returns_distribution.png"
        fig.savefig(filepath, dpi=100, bbox_inches='tight')
        saved_files.append(str(filepath))
        logger.info(f"Saved: {filepath}")
        if not show_plots:
            plt.close(fig)
    except Exception as e:
        logger.warning(f"Failed to save returns distribution: {e}")

    # 4. 交易记录
    if not trades.empty:
        try:
            fig = visualizer.plot_trades(equity_curve, trades, "Trading Activity")
            filepath = output_path / "trades.png"
            fig.savefig(filepath, dpi=100, bbox_inches='tight')
            saved_files.append(str(filepath))
            logger.info(f"Saved: {filepath}")
            if not show_plots:
                plt.close(fig)
        except Exception as e:
            logger.warning(f"Failed to save trades: {e}")

    # 5. 月度收益热力图
    try:
        fig = visualizer.plot_monthly_returns_heatmap(equity_curve, "Monthly Returns Heatmap")
        filepath = output_path / "monthly_heatmap.png"
        fig.savefig(filepath, dpi=100, bbox_inches='tight')
        saved_files.append(str(filepath))
        logger.info(f"Saved: {filepath}")
        if not show_plots:
            plt.close(fig)
    except Exception as e:
        logger.warning(f"Failed to save monthly heatmap: {e}")

    # 6. 绩效汇总
    try:
        fig = visualizer.plot_performance_summary(metrics, "Performance Summary")
        filepath = output_path / "performance_summary.png"
        fig.savefig(filepath, dpi=100, bbox_inches='tight')
        saved_files.append(str(filepath))
        logger.info(f"Saved: {filepath}")
        if not show_plots:
            plt.close(fig)
    except Exception as e:
        logger.warning(f"Failed to save performance summary: {e}")

    if show_plots:
        plt.show()

    return saved_files


if __name__ == "__main__":
    # 测试可视化
    print("=" * 60)
    print("可视化模块测试")
    print("=" * 60)

    # 生成模拟数据
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='B')
    np.random.seed(42)

    equity = pd.DataFrame({
        'date': dates,
        'total_value': 1000000 * (1 + np.random.randn(len(dates)) * 0.01).cumprod(),
    })
    equity['daily_return'] = equity['total_value'].pct_change()
    equity.set_index('date', inplace=True)

    # 创建可视化器
    visualizer = BacktestVisualizer()

    # 绘制图表
    print("\n1. 资金曲线...")
    fig = visualizer.plot_equity_curve(equity)
    plt.savefig('/tmp/equity_curve.png')
    print("   Saved: /tmp/equity_curve.png")

    print("\n2. 回撤分析...")
    fig = visualizer.plot_drawdown(equity)
    plt.savefig('/tmp/drawdown.png')
    print("   Saved: /tmp/drawdown.png")

    print("\n3. 收益分布...")
    fig = visualizer.plot_returns_distribution(equity)
    plt.savefig('/tmp/returns_distribution.png')
    print("   Saved: /tmp/returns_distribution.png")

    print("\n可视化测试完成!")
