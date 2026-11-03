"""
缠论图表生成器
输入股票代码，自动生成包含笔、线段、中枢的交互式缠论图表
"""

import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class ChanTheoryAnalyzer:
    """缠论分析器"""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.fens = []  # 分型列表
        self.bi_list = []  # 笔列表
        self.segments = []  # 线段列表
        self.zhongshu_list = []  # 中枢列表
        self.divergences = []  # 背离列表

    def find_fens(self) -> List[Dict]:
        """
        识别顶底分型
        顶分型：第二根K线高点最高，且收盘最低
        底分型：第二根K线低点最低，且收盘最高
        """
        df = self.df
        fens = []

        for i in range(1, len(df) - 1):
            # 检查顶分型
            if (df['High'].iloc[i-1] < df['High'].iloc[i] > df['High'].iloc[i+1] and
                df['Close'].iloc[i-1] > df['Close'].iloc[i] < df['Close'].iloc[i+1]):
                fens.append({
                    'index': i,
                    'date': df.index[i],
                    'type': 'top',
                    'price': df['High'].iloc[i]
                })
            # 检查底分型
            elif (df['Low'].iloc[i-1] > df['Low'].iloc[i] < df['Low'].iloc[i+1] and
                  df['Close'].iloc[i-1] < df['Close'].iloc[i] > df['Close'].iloc[i+1]):
                fens.append({
                    'index': i,
                    'date': df.index[i],
                    'type': 'bottom',
                    'price': df['Low'].iloc[i]
                })

        self.fens = fens
        return fens

    def find_bi(self, min_bars: int = 3) -> List[Dict]:
        """
        识别笔
        笔 = 顶分型 + 中间K线 + 底分型（或反向）
        中间至少有一根K线
        """
        if not self.fens:
            self.find_fens()

        bi_list = []
        current_direction = None  # 'up' or 'down'

        for i, fen in enumerate(self.fens):
            if current_direction is None:
                current_direction = 'up' if fen['type'] == 'top' else 'down'
                bi_start = fen
                continue

            # 检查方向变化
            if (current_direction == 'up' and fen['type'] == 'bottom') or \
               (current_direction == 'down' and fen['type'] == 'top'):

                # 计算中间K线数量
                mid_bars = fen['index'] - bi_start['index']

                if mid_bars >= min_bars:
                    bi_list.append({
                        'start': bi_start,
                        'end': fen,
                        'direction': current_direction,
                        'mid_bars': mid_bars
                    })
                    current_direction = 'up' if fen['type'] == 'top' else 'down'
                    bi_start = fen

        self.bi_list = bi_list
        return bi_list

    def find_segments(self, min_bi_count: int = 3) -> List[Dict]:
        """
        识别线段
        线段由至少3笔构成，且方向一致
        """
        if not self.bi_list:
            self.find_bi()

        segments = []
        current_direction = None
        bi_group = []

        for bi in self.bi_list:
            if current_direction is None:
                current_direction = bi['direction']
                bi_group.append(bi)
                continue

            if bi['direction'] == current_direction:
                bi_group.append(bi)
            else:
                # 方向变化，检查是否可以形成线段
                if len(bi_group) >= min_bi_count:
                    segments.append({
                        'start': bi_group[0]['start'],
                        'end': bi_group[-1]['end'],
                        'direction': current_direction,
                        'bi_list': bi_group.copy()
                    })
                bi_group = [bi]
                current_direction = bi['direction']

        # 最后一个线段
        if len(bi_group) >= min_bi_count:
            segments.append({
                'start': bi_group[0]['start'],
                'end': bi_group[-1]['end'],
                'direction': current_direction,
                'bi_list': bi_group.copy()
            })

        self.segments = segments
        return segments

    def find_zhongshu(self, min_segment_count: int = 3) -> List[Dict]:
        """
        识别中枢
        中枢 = 连续三段的重叠区域
        """
        if not self.segments:
            self.find_segments()

        zhongshu_list = []

        for i in range(len(self.segments) - min_segment_count + 1):
            seg1 = self.segments[i]
            seg2 = self.segments[i + 1]
            seg3 = self.segments[i + 2]

            # 获取线段的价格范围
            ranges = [
                (seg1['start']['price'], seg1['end']['price']),
                (seg2['start']['price'], seg2['end']['price']),
                (seg3['start']['price'], seg3['end']['price'])
            ]

            # 计算重叠区域
            max_low = max(r[0] for r in ranges)
            min_high = min(r[1] for r in ranges)

            if max_low < min_high:
                zhongshu_list.append({
                    'start_date': seg1['start']['date'],
                    'end_date': seg3['end']['date'],
                    'high': min_high,
                    'low': max_low,
                    'segments': [seg1, seg2, seg3]
                })

        self.zhongshu_list = zhongshu_list
        return zhongshu_list

    def find_divergence(self) -> List[Dict]:
        """
        检测背离
        基于MACD和价格的背离
        """
        df = self.df

        # 计算MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal

        divergences = []

        # 简化背离检测：寻找价格与MACD方向不一致的区域
        window = 20
        for i in range(window, len(df) - window):
            # 检查区间内的高低点
            price_window = df['Close'].iloc[i-window:i+window]
            macd_window = histogram.iloc[i-window:i+window]

            price_high_idx = price_window.idxmax()
            price_low_idx = price_window.idxmin()
            macd_high_idx = macd_window.idxmax()
            macd_low_idx = macd_window.idxmin()

            # 顶背离：价格创新高，MACD没创新高
            if (price_high_idx > df.index[i] and
                macd_high_idx < df.index[i]):
                divergences.append({
                    'type': 'top',
                    'date': price_high_idx,
                    'price': df['High'].loc[price_high_idx],
                    'description': '顶背离：价格创新高但MACD未创新高'
                })

            # 底背离：价格创新低，MACD没创新低
            if (price_low_idx > df.index[i] and
                macd_low_idx < df.index[i]):
                divergences.append({
                    'type': 'bottom',
                    'date': price_low_idx,
                    'price': df['Low'].loc[price_low_idx],
                    'description': '底背离：价格创新低但MACD未创新低'
                })

        # 去重
        seen = set()
        unique_divs = []
        for div in divergences:
            key = (div['type'], div['date'])
            if key not in seen:
                seen.add(key)
                unique_divs.append(div)

        self.divergences = unique_divs[:20]  # 限制数量
        return self.divergences

    def analyze(self):
        """执行完整分析"""
        self.find_fens()
        self.find_bi()
        self.find_segments()
        self.find_zhongshu()
        self.find_divergence()
        return self


def generate_chan_theory_chart(symbol: str, period: str = "2y", output_path: str = None) -> str:
    """
    生成缠论图表

    Args:
        symbol: 股票代码 (如 'AAPL', '600519.SS')
        period: 数据周期 (如 '1y', '2y', '5y')
        output_path: 输出HTML文件路径

    Returns:
        HTML文件路径
    """
    # 获取数据
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)

    if df.empty or len(df) < 100:
        raise ValueError(f"股票 {symbol} 数据不足，无法完成缠论分析")

    # 执行分析
    analyzer = ChanTheoryAnalyzer(df)
    analyzer.analyze()

    # 创建图表
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{symbol} 缠论分析图', 'MACD')
    )

    # K线图
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='K线',
            increasing_line_color='#FF4136',
            decreasing_line_color='#3D9970'
        ),
        row=1, col=1
    )

    # 笔
    for bi in analyzer.bi_list:
        color = '#FF6600' if bi['direction'] == 'up' else '#00AAFF'
        fig.add_trace(
            go.Scatter(
                x=[bi['start']['date'], bi['end']['date']],
                y=[bi['start']['price'], bi['end']['price']],
                mode='lines',
                line=dict(color=color, width=2),
                name=f"笔({'上' if bi['direction'] == 'up' else '下'})",
                showlegend=False
            ),
            row=1, col=1
        )

        # 标记笔的端点
        fig.add_trace(
            go.Scatter(
                x=[bi['start']['date'], bi['end']['date']],
                y=[bi['start']['price'], bi['end']['price']],
                mode='markers',
                marker=dict(
                    size=8,
                    color=color,
                    symbol='circle'
                ),
                showlegend=False
            ),
            row=1, col=1
        )

    # 中枢
    for i, z in enumerate(analyzer.zhongshu_list):
        fig.add_shape(
            type="rect",
            x0=z['start_date'], x1=z['end_date'],
            y0=z['low'], y1=z['high'],
            fillcolor="rgba(255,165,0,0.2)",
            line=dict(color="orange", width=2),
            name=f"中枢{i+1}"
        )

    # 背离标记
    for div in analyzer.divergences:
        color = '#FF0000' if div['type'] == 'top' else '#00FF00'
        fig.add_annotation(
            x=div['date'],
            y=div['price'],
            text=f"{'顶' if div['type'] == 'top' else '底'}背离",
            showarrow=True,
            arrowhead=1,
            arrowsize=2,
            arrowcolor=color,
            font=dict(color=color, size=10)
        )

    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal

    colors = ['#3D9970' if val >= 0 else '#FF4136' for val in histogram]

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=histogram,
            name='MACD柱',
            marker_color=colors,
            showlegend=False
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=macd,
            mode='lines',
            line=dict(color='#FF6600', width=1),
            name='DIF',
            showlegend=False
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=signal,
            mode='lines',
            line=dict(color='#00AAFF', width=1),
            name='DEA',
            showlegend=False
        ),
        row=2, col=1
    )

    # 更新布局
    fig.update_layout(
        title=dict(
            text=f'<b>{symbol}</b> 缠论技术分析',
            font=dict(size=20)
        ),
        height=800,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified",
        xaxis_rangeslider_visible=False
    )

    fig.update_xaxes(title_text="", row=2, col=1)
    fig.update_yaxes(title_text="价格", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)

    # 生成HTML
    if output_path is None:
        output_path = f"chan_theory_{symbol.replace('.', '_')}.html"

    fig.write_html(output_path, include_plotlyjs=True, full_html=True)

    return output_path


def main():
    """测试函数"""
    import sys

    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    else:
        symbol = "AAPL"

    print(f"正在分析股票: {symbol}")

    try:
        output_path = generate_chan_theory_chart(symbol)
        print(f"缠论图已生成: {output_path}")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
