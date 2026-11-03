# -*- coding: utf-8 -*-
"""
量化回测可视化软件 - 主应用
支持多策略回测、可视化分析、数据导出
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
from pathlib import Path
import logging
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from backtest_engine import BacktestEngine
from performance import PerformanceAnalyzer
from strategies import list_strategies, get_strategy
from data_fetcher import StockDataFetcher

# 配置日志
logging.basicConfig(level=logging.WARNING)

# 页面配置
st.set_page_config(
    page_title="A股量化回测系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: bold;
        color: #1e3c72;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #6c757d;
        margin-top: 0.3rem;
    }
    .positive {
        color: #28a745;
    }
    .negative {
        color: #dc3545;
    }
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化Session State
if 'fetcher' not in st.session_state:
    st.session_state.fetcher = StockDataFetcher()
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = None


def load_stock_data(symbol, start_date, end_date):
    """加载股票数据"""
    try:
        with st.spinner(f"正在获取 {symbol} 的真实数据..."):
            df = st.session_state.fetcher.fetch_stock_data(
                symbol, start_date, end_date, use_cache=True
            )
            if df is not None and not df.empty:
                st.session_state.current_data = {symbol: df}
                return df
            else:
                st.error(f"无法获取 {symbol} 的数据，请检查股票代码")
                return None
    except Exception as e:
        st.error(f"数据获取失败: {e}")
        return None


def run_backtest(strategy_name, params):
    """运行回测"""
    if st.session_state.current_data is None:
        st.error("请先加载数据")
        return None
    
    data = st.session_state.current_data
    strategy = get_strategy(strategy_name)
    
    if strategy is None:
        st.error(f"未找到策略: {strategy_name}")
        return None
    
    # 创建回测引擎
    engine = BacktestEngine(initial_capital=params.get('initial_capital', 1000000))
    engine.load_data(data)
    engine.set_strategy(strategy, **params)
    
    # 运行回测
    with st.spinner("正在运行回测..."):
        equity_curve = engine.run()
        trades = engine.get_trades()
        summary = engine.get_summary()
    
    # 计算绩效指标
    analyzer = PerformanceAnalyzer(equity_curve, trades)
    metrics = analyzer.get_full_report()
    
    return {
        'equity_curve': equity_curve,
        'trades': trades,
        'metrics': metrics,
        'summary': summary,
        'engine': engine
    }


def plot_equity_curve(results):
    """绘制资金曲线"""
    equity = results['equity_curve']
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3]
    )
    
    # 资金曲线
    fig.add_trace(
        go.Scatter(
            x=equity.index, y=equity['total_value'],
            mode='lines',
            name='资产价值',
            line=dict(color='#2E86AB', width=2),
            fill='tozeroy',
            fillcolor='rgba(46, 134, 171, 0.2)'
        ),
        row=1, col=1
    )
    
    # 初始资金线
    fig.add_hline(
        y=results['summary']['initial_capital'],
        line_dash="dash",
        line_color="gray",
        annotation_text="初始资金",
        row=1, col=1
    )
    
    # 日收益率
    fig.add_trace(
        go.Bar(
            x=equity.index, y=equity['daily_return'] * 100,
            name='日收益率 (%)',
            marker_color=equity['daily_return'].apply(lambda x: '#28a745' if x > 0 else '#dc3545'),
            opacity=0.6
        ),
        row=2, col=1
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
    
    fig.update_layout(
        title="📈 资金曲线与日收益率",
        height=550,
        showlegend=True,
        hovermode='x unified'
    )
    fig.update_xaxes(title_text="日期", row=2, col=1)
    fig.update_yaxes(title_text="资产价值 (元)", row=1, col=1)
    fig.update_yaxes(title_text="收益率 (%)", row=2, col=1)
    
    return fig


def plot_drawdown(results):
    """绘制回撤图"""
    equity = results['equity_curve']
    cumulative = equity['total_value']
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max * 100
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=drawdown.index, y=drawdown,
            mode='lines',
            name='回撤',
            line=dict(color='#dc3545', width=1.5),
            fill='tozeroy',
            fillcolor='rgba(220, 53, 69, 0.3)'
        )
    )
    
    # 标注最大回撤
    max_dd = drawdown.min()
    max_dd_idx = drawdown.idxmin()
    fig.add_annotation(
        x=max_dd_idx, y=max_dd,
        text=f"最大回撤: {max_dd:.2f}%",
        showarrow=True,
        arrowhead=2,
        arrowcolor="red",
        bgcolor="white",
        bordercolor="red"
    )
    
    fig.update_layout(
        title="📉 回撤分析",
        xaxis_title="日期",
        yaxis_title="回撤 (%)",
        height=400,
        hovermode='x unified'
    )
    
    return fig


def plot_returns_distribution(results):
    """绘制收益分布"""
    equity = results['equity_curve']
    returns = equity['daily_return'].dropna() * 100
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=('日收益率分布', '月度收益'))
    
    # 日收益率直方图
    fig.add_trace(
        go.Histogram(
            x=returns,
            nbinsx=50,
            name='日收益率',
            marker_color='steelblue',
            opacity=0.7
        ),
        row=1, col=1
    )
    
    fig.add_vline(
        x=returns.mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"均值: {returns.mean():.3f}%",
        row=1, col=1
    )
    
    # 月度收益
    monthly = equity['total_value'].resample('ME').last().pct_change().dropna() * 100
    if not monthly.empty:
        colors = ['#28a745' if x > 0 else '#dc3545' for x in monthly]
        fig.add_trace(
            go.Bar(
                x=monthly.index.strftime('%Y-%m'),
                y=monthly,
                name='月度收益',
                marker_color=colors,
                opacity=0.8
            ),
            row=1, col=2
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=2)
    
    fig.update_layout(height=450, showlegend=False)
    fig.update_xaxes(title_text="收益率 (%)", row=1, col=1)
    fig.update_xaxes(title_text="月份", row=1, col=2)
    
    return fig


def plot_trades(results):
    """绘制交易记录"""
    trades = results['trades']
    equity = results['equity_curve']
    
    if trades.empty:
        return None
    
    fig = go.Figure()
    
    # 资金曲线
    fig.add_trace(
        go.Scatter(
            x=equity.index, y=equity['total_value'],
            mode='lines',
            name='资产曲线',
            line=dict(color='#2E86AB', width=2)
        )
    )
    
    # 买入点
    buy_trades = trades[trades['type'] == 'buy']
    if not buy_trades.empty:
        buy_points = [(idx, equity.loc[idx, 'total_value']) for idx in buy_trades.index if idx in equity.index]
        if buy_points:
            fig.add_trace(
                go.Scatter(
                    x=[p[0] for p in buy_points], y=[p[1] for p in buy_points],
                    mode='markers',
                    name='买入',
                    marker=dict(symbol='triangle-up', size=12, color='#28a745', line=dict(width=1, color='white'))
                )
            )
    
    # 卖出点
    sell_trades = trades[trades['type'] == 'sell']
    if not sell_trades.empty:
        sell_points = [(idx, equity.loc[idx, 'total_value']) for idx in sell_trades.index if idx in equity.index]
        if sell_points:
            fig.add_trace(
                go.Scatter(
                    x=[p[0] for p in sell_points], y=[p[1] for p in sell_points],
                    mode='markers',
                    name='卖出',
                    marker=dict(symbol='triangle-down', size=12, color='#dc3545', line=dict(width=1, color='white'))
                )
            )
    
    fig.update_layout(
        title="💰 交易记录",
        xaxis_title="日期",
        yaxis_title="资产价值 (元)",
        height=450,
        hovermode='x unified'
    )
    
    return fig


def display_metrics(metrics):
    """显示绩效指标卡片"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics.get('total_return', 0)*100:.2f}%</div>
            <div class="metric-label">总收益率</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics.get('annualized_return', 0)*100:.2f}%</div>
            <div class="metric-label">年化收益率</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics.get('sharpe_ratio', 0):.2f}</div>
            <div class="metric-label">夏普比率</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{abs(metrics.get('max_drawdown', 0))*100:.2f}%</div>
            <div class="metric-label">最大回撤</div>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics.get('win_rate', 0)*100:.1f}%</div>
            <div class="metric-label">胜率</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics.get('profit_ratio', 0):.2f}</div>
            <div class="metric-label">盈亏比</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics.get('total_trades', 0)}</div>
            <div class="metric-label">交易次数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metrics.get('profit_factor', 0):.2f}</div>
            <div class="metric-label">利润因子</div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """主函数"""
    # 标题
    st.markdown('<div class="main-header">📊 A股量化回测系统</div>', unsafe_allow_html=True)
    st.markdown("支持移动平均线、RSI、布林带、MACD、KDJ、KDJ+BBI等经典策略")
    st.markdown("---")
    
    # 侧边栏
    with st.sidebar:
        st.markdown("### 📈 回测配置")
        st.markdown("---")
        
        # 股票选择
        symbol = st.text_input("股票代码", value="000001", help="输入A股代码，如：000001、600519")
        
        # 日期选择
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("开始日期", value=datetime(2023, 1, 1))
        with col2:
            end_date = st.date_input("结束日期", value=datetime(2024, 1, 1))
        
        st.markdown("---")
        
        # ========== 全局仓位选择 ==========
        st.markdown("### 💰 仓位管理")
        
        # 仓位比例选项
        position_options = {
            "1/4 (25%)": 0.25,
            "1/3 (33.3%)": 0.333,
            "1/2 (50%)": 0.5,
            "全仓 (100%)": 1.0
        }
        
        selected_position = st.selectbox(
            "每次买入仓位",
            options=list(position_options.keys()),
            index=3,  # 默认全仓
            help="选择每次买入时使用的资金比例"
        )
        buy_ratio = position_options[selected_position]
        
        # 显示当前仓位比例
        st.info(f"📊 当前仓位: {selected_position} (买入时使用 {buy_ratio*100:.0f}% 可用资金)")
        
        st.markdown("---")
        
        # 策略选择
        st.markdown("### ⚙️ 策略配置")
        
        strategies = list_strategies()
        strategy_names = {
            'ma_cross': '📊 移动平均线交叉',
            'rsi': '📈 RSI相对强弱',
            'bollinger': '📉 布林带',
            'macd': '📊 MACD',
            'kdj': '📈 KDJ随机指标',
            'dual_ma_rsi': '🎯 双均线+RSI',
            'kdj_bbi': '🔥 KDJ+BBI组合策略',
        }
        
        strategy_name = st.selectbox(
            "选择策略",
            strategies,
            format_func=lambda x: strategy_names.get(x, x)
        )
        
        st.markdown("---")
        st.markdown("### 🔧 策略参数")
        
        # 基础参数（所有策略共享）
        params = {
            'initial_capital': st.number_input("初始资金 (元)", value=1000000, step=100000),
            'buy_ratio': buy_ratio,  # 添加仓位比例参数
        }
        
        # 各策略特有参数
        if strategy_name == 'ma_cross':
            params['short_window'] = st.slider("短期均线", 3, 30, 5)
            params['long_window'] = st.slider("长期均线", 10, 60, 20)
        elif strategy_name == 'rsi':
            params['period'] = st.slider("RSI周期", 5, 30, 14)
            params['oversold'] = st.slider("超卖阈值", 20, 40, 30)
            params['overbought'] = st.slider("超买阈值", 60, 90, 70)
        elif strategy_name == 'bollinger':
            params['period'] = st.slider("布林带周期", 10, 50, 20)
            params['std_dev'] = st.slider("标准差倍数", 1.5, 3.0, 2.0, 0.1)
        elif strategy_name == 'macd':
            params['fast_period'] = st.slider("快线周期", 6, 20, 12)
            params['slow_period'] = st.slider("慢线周期", 20, 40, 26)
            params['signal_period'] = st.slider("信号线周期", 5, 15, 9)
        elif strategy_name == 'kdj':
            params['n'] = st.slider("KDJ周期 N", 5, 20, 9)
            params['m1'] = st.slider("KDJ周期 M1", 2, 10, 3)
            params['m2'] = st.slider("KDJ周期 M2", 2, 10, 3)
        elif strategy_name == 'dual_ma_rsi':
            params['ma_short'] = st.slider("短期均线", 3, 15, 5)
            params['ma_long'] = st.slider("长期均线", 15, 40, 20)
            params['rsi_period'] = st.slider("RSI周期", 10, 20, 14)
            params['rsi_buy'] = st.slider("RSI买入阈值", 30, 50, 40)
            params['rsi_sell'] = st.slider("RSI卖出阈值", 50, 70, 60)
        elif strategy_name == 'kdj_bbi':
            params['kdj_n'] = st.slider("KDJ周期 N", 5, 20, 9)
            params['kdj_m1'] = st.slider("KDJ周期 M1", 2, 10, 3)
            params['kdj_m2'] = st.slider("KDJ周期 M2", 2, 10, 3)
            params['j_buy_threshold'] = st.slider("J值买入阈值", -20, 20, 0, help="J值低于此值时买入")
            params['j_sell_half_threshold'] = st.slider("J值卖出一半阈值", 80, 150, 107, help="J值高于此值时卖出一半")
        
        st.markdown("---")
        run_button = st.button("🚀 运行回测", type="primary", use_container_width=True)
    
    # 主区域
    if run_button:
        # 加载数据
        df = load_stock_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        if df is not None:
            # 显示数据概览
            with st.expander("📊 数据概览", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("数据条数", len(df))
                with col2:
                    st.metric("开始日期", df.index[0].strftime('%Y-%m-%d'))
                with col3:
                    st.metric("结束日期", df.index[-1].strftime('%Y-%m-%d'))
                st.dataframe(df.tail(10), use_container_width=True)
            
            # 运行回测
            results = run_backtest(strategy_name, params)
            
            if results:
                st.session_state.backtest_results = results
                
                # 绩效指标
                st.markdown("### 📈 绩效指标")
                display_metrics(results['metrics'])
                
                # 可视化图表
                st.markdown("---")
                st.markdown("### 📊 可视化分析")
                
                st.plotly_chart(plot_equity_curve(results), use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(plot_drawdown(results), use_container_width=True)
                with col2:
                    returns_fig = plot_returns_distribution(results)
                    if returns_fig:
                        st.plotly_chart(returns_fig, use_container_width=True)
                
                trades_fig = plot_trades(results)
                if trades_fig:
                    st.plotly_chart(trades_fig, use_container_width=True)
                
                # 交易明细
                with st.expander("📋 交易明细"):
                    if not results['trades'].empty:
                        st.dataframe(results['trades'], use_container_width=True)
                    else:
                        st.info("无交易记录")
                
                # 导出功能
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    csv_equity = results['equity_curve'].to_csv().encode('utf-8')
                    st.download_button("📥 导出资金曲线", csv_equity, f"{symbol}_equity.csv", "text/csv")
                with col2:
                    if not results['trades'].empty:
                        csv_trades = results['trades'].to_csv().encode('utf-8')
                        st.download_button("📥 导出交易记录", csv_trades, f"{symbol}_trades.csv", "text/csv")
                with col3:
                    metrics_df = pd.DataFrame([results['metrics']])
                    csv_metrics = metrics_df.to_csv().encode('utf-8')
                    st.download_button("📥 导出绩效指标", csv_metrics, f"{symbol}_metrics.csv", "text/csv")
    else:
        # 欢迎界面
        st.info("👈 请在左侧配置回测参数，然后点击「运行回测」按钮")
        
        with st.expander("📖 使用说明", expanded=True):
            st.markdown("""
            ### 🚀 快速开始
            1. **输入股票代码**：如 000001（平安银行）、600519（贵州茅台）
            2. **选择回测日期**：建议选择1年以上的数据
            3. **选择仓位比例**：1/4、1/3、1/2 或 全仓
            4. **选择交易策略**：7种经典策略可选
            5. **调整策略参数**：根据策略调整相应参数
            6. **点击运行回测**：等待几秒钟即可看到结果
            
            ### 💰 仓位管理
            - **1/4 (25%)**：每次买入使用25%可用资金
            - **1/3 (33.3%)**：每次买入使用33.3%可用资金
            - **1/2 (50%)**：每次买入使用50%可用资金
            - **全仓 (100%)**：每次买入使用全部可用资金
            
            ### 📊 支持的策略
            - **移动平均线交叉**：金叉买入，死叉卖出
            - **RSI相对强弱**：超卖买入，超买卖出
            - **布林带**：触及下轨买入，上轨卖出
            - **MACD**：DIF上穿DEA买入，下穿卖出
            - **KDJ随机指标**：K线上穿D线买入，下穿卖出
            - **双均线+RSI**：组合信号，更稳健
            - **KDJ+BBI组合**：J值<0买入 → J>107卖出一半 → 跌破BBI清仓
            
            ### 📈 绩效指标解读
            - **总收益率**：回测期间的总收益
            - **年化收益率**：折算成年度的收益率
            - **夏普比率**：风险调整后收益，>1较好
            - **最大回撤**：历史最大亏损幅度
            - **胜率**：盈利交易占比
            - **盈亏比**：平均盈利/平均亏损
            - **利润因子**：总盈利/总亏损，>1盈利
            """)
        
        # 策略预览
        st.markdown("---")
        st.markdown("### 🎯 可用策略")
        
        strategies = list_strategies()
        strategy_info = {
            'ma_cross': ('移动平均线交叉', '短期均线上穿长期均线买入，下穿卖出'),
            'rsi': ('RSI相对强弱指标', 'RSI低于30买入，高于70卖出'),
            'bollinger': ('布林带', '价格触及下轨买入，触及上轨卖出'),
            'macd': ('MACD指标', 'DIF上穿DEA买入，下穿卖出'),
            'kdj': ('KDJ随机指标', 'K线上穿D线买入，下穿卖出'),
            'dual_ma_rsi': ('双均线+RSI组合', '均线金叉+RSI确认买入'),
            'kdj_bbi': ('KDJ+BBI组合策略', 'J值<0买入 → J>107卖出一半 → 跌破BBI清仓'),
        }
        
        cols = st.columns(3)
        for i, strategy in enumerate(strategies):
            name, desc = strategy_info.get(strategy, (strategy, '经典量化策略'))
            with cols[i % 3]:
                st.markdown(f"""
                <div class="info-box">
                    <strong>{name}</strong><br>
                    <small>{desc}</small>
                </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
