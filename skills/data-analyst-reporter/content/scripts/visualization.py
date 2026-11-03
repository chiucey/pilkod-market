#!/usr/bin/env python3
"""
数据可视化脚本 — 生成专业级交互式图表与综合报告

用法:
    python visualization.py --input data.csv --type line --x date --y revenue --output charts/
    python visualization.py --input rfm.csv --type rfm_heatmap --output charts/
    python visualization.py --input funnel.csv --type funnel --output charts/

优先使用 Plotly 生成交互式图表，备选 Matplotlib/Seaborn 静态图表。
依赖: pandas, plotly, matplotlib, seaborn
"""

import pandas as pd
import numpy as np
import os
import argparse
import warnings
warnings.filterwarnings('ignore')

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False


# ============================================================
# Plotly 交互式图表
# ============================================================

def plot_trend_line(df: pd.DataFrame, x: str, y: str | list,
                    title: str = '趋势分析', output_path: str = None):
    """生成折线趋势图（支持多指标）。"""
    if not HAS_PLOTLY:
        return _plot_trend_line_mpl(df, x, y, title, output_path)

    y_cols = [y] if isinstance(y, str) else y
    fig = go.Figure()
    for col in y_cols:
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col], mode='lines+markers',
            name=col, line=dict(width=2), marker=dict(size=6)
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis_title=x, yaxis_title='值',
        hovermode='x unified',
        template='plotly_white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    _save_figure(fig, output_path, title)
    return fig


def plot_bar_comparison(df: pd.DataFrame, x: str, y: str,
                        color: str = None, title: str = '对比分析',
                        output_path: str = None):
    """生成条形对比图。"""
    if not HAS_PLOTLY:
        return _plot_bar_mpl(df, x, y, title, output_path)

    fig = px.bar(df, x=x, y=y, color=color, title=title,
                 template='plotly_white',
                 text_auto='.2s',
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_traces(textangle=0, textposition='outside')
    fig.update_layout(title=dict(font=dict(size=18)), showlegend=color is not None)
    _save_figure(fig, output_path, title)
    return fig


def plot_rfm_heatmap(rfm: pd.DataFrame, output_path: str = None):
    """生成 RFM 客户细分热力图（R vs F，颜色=M均值）。"""
    if not HAS_PLOTLY:
        return _plot_rfm_heatmap_mpl(rfm, output_path)

    pivot = rfm.pivot_table(
        values='monetary', index='r_score', columns='f_score',
        aggfunc='mean'
    ).astype(float)

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f'F={c}' for c in pivot.columns],
        y=[f'R={r}' for r in pivot.index],
        colorscale='Blues',
        text=np.round(pivot.values, 0),
        texttemplate='¥%{text:,.0f}',
        hovertemplate='%{y}, %{x}<br>平均消费: ¥%{z:,.0f}<extra></extra>'
    ))
    fig.update_layout(
        title='RFM 客户价值热力图（颜色深度=平均消费金额）',
        xaxis_title='购买频率评分', yaxis_title='最近购买评分',
        template='plotly_white'
    )
    _save_figure(fig, output_path, 'rfm_heatmap')
    return fig


def plot_funnel(stages: list, values: list,
                title: str = '转化漏斗', output_path: str = None):
    """生成漏斗转化图。"""
    if not HAS_PLOTLY:
        return _plot_funnel_mpl(stages, values, title, output_path)

    fig = go.Figure(go.Funnel(
        y=stages, x=values,
        textinfo='value+percent initial+percent previous',
        marker=dict(color=['#4C72B0', '#55A868', '#C44E52',
                            '#8172B2', '#CCB974'][:len(stages)])
    ))
    fig.update_layout(title=dict(text=title, font=dict(size=18)),
                      template='plotly_white')
    _save_figure(fig, output_path, title)
    return fig


def plot_segment_distribution(rfm: pd.DataFrame, output_path: str = None):
    """生成客户细分饼图 + 价值分布条形图（双图布局）。"""
    if not HAS_PLOTLY:
        return None  # 简化处理，仅 Plotly 版

    seg_count = rfm['segment'].value_counts()
    seg_value = rfm.groupby('segment')['monetary'].sum().sort_values(ascending=False)

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'domain'}, {'type': 'bar'}]],
        subplot_titles=['客户数量分布', '各细分收入贡献']
    )
    fig.add_trace(go.Pie(
        labels=seg_count.index, values=seg_count.values,
        name='客户数', hole=0.4,
        textinfo='label+percent'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=seg_value.index, y=seg_value.values,
        name='收入', marker_color='#4C72B0',
        text=[f'¥{v:,.0f}' for v in seg_value.values],
        textposition='outside'
    ), row=1, col=2)

    fig.update_layout(
        title='客户细分全貌',
        template='plotly_white', showlegend=False, height=450
    )
    _save_figure(fig, output_path, 'segment_distribution')
    return fig


def create_comprehensive_report(figures: list, titles: list,
                                 report_title: str = '数据分析综合报告',
                                 output_path: str = 'report.html'):
    """
    将多个 Plotly 图表整合成单一 HTML 综合报告。

    Args:
        figures: Plotly figure 对象列表
        titles:  对应标题列表
        report_title: 报告总标题
        output_path:  HTML 输出路径
    """
    if not HAS_PLOTLY:
        print("⚠️  需要安装 plotly 才能生成综合报告")
        return

    html_parts = [f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{report_title}</title>
<style>
  body {{ font-family: 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
          margin: 0; padding: 24px; background: #f8f9fa; color: #333; }}
  h1   {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 12px; }}
  h2   {{ color: #34495e; margin-top: 40px; }}
  .chart-container {{ background: white; border-radius: 8px; padding: 16px;
                       margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  .timestamp {{ color: #888; font-size: 13px; margin-top: 8px; }}
  .toc {{ background: white; border-radius: 8px; padding: 16px 24px;
          margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  .toc a {{ color: #3498db; text-decoration: none; line-height: 2; }}
  .toc a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>📊 {report_title}</h1>
<p class="timestamp">生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>
<div class="toc">
  <strong>目录</strong><br>
  {''.join(f'<a href="#chart{i}">▸ {t}</a><br>' for i, t in enumerate(titles))}
</div>
"""]

    for i, (fig, title) in enumerate(zip(figures, titles)):
        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn' if i == 0 else False)
        html_parts.append(f"""
<div class="chart-container" id="chart{i}">
  <h2>{title}</h2>
  {chart_html}
</div>
""")

    html_parts.append("</body></html>")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(html_parts))

    print(f"✅ 综合报告已生成: {output_path}")
    return output_path


# ============================================================
# Matplotlib 静态图表（Plotly 不可用时的备选）
# ============================================================

def _plot_trend_line_mpl(df, x, y, title, output_path):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12, 5))
    y_cols = [y] if isinstance(y, str) else y
    for col in y_cols:
        ax.plot(df[x], df[col], marker='o', linewidth=2, label=col)
    ax.set_title(title, fontsize=16)
    ax.set_xlabel(x); ax.set_ylabel('值')
    ax.legend(); ax.grid(alpha=0.3); plt.tight_layout()
    if output_path:
        path = os.path.join(output_path, f"{title}.png")
        plt.savefig(path, dpi=150, bbox_inches='tight')
    return fig


def _plot_bar_mpl(df, x, y, title, output_path):
    import matplotlib.pyplot as plt, seaborn as sns
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, x=x, y=y, ax=ax, palette='Set2')
    ax.set_title(title, fontsize=16); plt.xticks(rotation=30); plt.tight_layout()
    if output_path:
        plt.savefig(os.path.join(output_path, f"{title}.png"), dpi=150, bbox_inches='tight')
    return fig


def _plot_rfm_heatmap_mpl(rfm, output_path):
    import matplotlib.pyplot as plt, seaborn as sns
    pivot = rfm.pivot_table(values='monetary', index='r_score',
                             columns='f_score', aggfunc='mean')
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt='.0f', cmap='Blues', ax=ax)
    ax.set_title('RFM 客户价值热力图'); plt.tight_layout()
    if output_path:
        plt.savefig(os.path.join(output_path, 'rfm_heatmap.png'), dpi=150, bbox_inches='tight')
    return fig


def _plot_funnel_mpl(stages, values, title, output_path):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(stages)))
    bars = ax.barh(stages[::-1], values[::-1], color=colors[::-1])
    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width() * 0.5, bar.get_y() + bar.get_height()/2,
                f'{val:,}', ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    ax.set_title(title, fontsize=16); ax.set_xlabel('用户数')
    plt.tight_layout()
    if output_path:
        plt.savefig(os.path.join(output_path, f"{title}.png"), dpi=150, bbox_inches='tight')
    return fig


# ============================================================
# 辅助函数
# ============================================================

def _save_figure(fig, output_path: str, name: str):
    if output_path is None:
        return
    os.makedirs(output_path, exist_ok=True)
    safe_name = name.replace('/', '_').replace(' ', '_')
    path = os.path.join(output_path, f"{safe_name}.html")
    fig.write_html(path)
    print(f"  💾 图表已保存: {path}")


# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='数据可视化工具')
    parser.add_argument('--input',  required=True, help='输入 CSV 文件路径')
    parser.add_argument('--type',   required=True,
                        choices=['line', 'bar', 'rfm_heatmap', 'funnel', 'segment'],
                        help='图表类型')
    parser.add_argument('--x',      default='date', help='x 轴列名')
    parser.add_argument('--y',      default='value', help='y 轴列名（多列用逗号分隔）')
    parser.add_argument('--title',  default='', help='图表标题')
    parser.add_argument('--output', default='./charts', help='输出目录')
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    y_cols = [c.strip() for c in args.y.split(',')]
    title  = args.title or args.type

    if args.type == 'line':
        plot_trend_line(df, args.x, y_cols if len(y_cols) > 1 else y_cols[0],
                        title, args.output)
    elif args.type == 'bar':
        plot_bar_comparison(df, args.x, y_cols[0], title=title, output_path=args.output)
    elif args.type == 'rfm_heatmap':
        plot_rfm_heatmap(df, args.output)
    elif args.type == 'funnel':
        stages = df[args.x].tolist()
        values = df[y_cols[0]].tolist()
        plot_funnel(stages, values, title, args.output)
    elif args.type == 'segment':
        plot_segment_distribution(df, args.output)

    print(f"✅ 图表已输出至: {args.output}")


if __name__ == '__main__':
    main()
