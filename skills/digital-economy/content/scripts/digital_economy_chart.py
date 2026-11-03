#!/usr/bin/env python3
"""
数字经济数据可视化脚本
支持生成多种数字经济相关图表，输出为HTML或PNG格式

用法:
  python digital_economy_chart.py --type [chart_type] --data [data_file] --output [output_file]

支持图表类型:
  - scale_trend     : 数字经济规模趋势图（折线/柱状组合）
  - penetration     : 各行业数字化渗透率雷达图
  - comparison      : 区域数字经济对比柱状图
  - structure       : 数字经济结构占比饼图
  - growth_rate     : 增速对比图
  - indicator_radar : 综合指标雷达图
"""

import argparse
import json
import sys
import os

def check_dependencies():
    """检查并安装必要依赖"""
    missing = []
    try:
        import plotly
    except ImportError:
        missing.append("plotly")
    try:
        import pandas
    except ImportError:
        missing.append("pandas")

    if missing:
        print(f"正在安装缺少的依赖: {', '.join(missing)}")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing, 
                            stdout=subprocess.DEVNULL)
        print("依赖安装完成")

check_dependencies()

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


# ============================================================
# 图表生成函数
# ============================================================

def chart_scale_trend(data: dict, output_path: str):
    """
    生成数字经济规模趋势图（柱状+折线组合）
    
    data格式示例:
    {
      "title": "中国数字经济规模趋势",
      "years": [2019, 2020, 2021, 2022, 2023, 2024],
      "scale": [35.8, 39.2, 45.5, 50.2, 53.9, 56.1],
      "gdp_ratio": [36.2, 38.6, 39.8, 41.5, 44.7, 47.0],
      "unit": "万亿元"
    }
    """
    years = data.get("years", [])
    scale = data.get("scale", [])
    gdp_ratio = data.get("gdp_ratio", [])
    title = data.get("title", "数字经济规模趋势")
    unit = data.get("unit", "万亿元")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=years, y=scale,
            name=f"数字经济规模（{unit}）",
            marker_color="#1E90FF",
            opacity=0.85,
            text=[f"{v}{unit}" for v in scale],
            textposition="outside"
        ),
        secondary_y=False
    )

    if gdp_ratio:
        fig.add_trace(
            go.Scatter(
                x=years, y=gdp_ratio,
                name="占GDP比重（%）",
                mode="lines+markers+text",
                line=dict(color="#FF6B35", width=3),
                marker=dict(size=8),
                text=[f"{v}%" for v in gdp_ratio],
                textposition="top center"
            ),
            secondary_y=True
        )

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis=dict(title="年份", tickvals=years),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Microsoft YaHei, SimHei, Arial", size=13),
        height=500
    )
    fig.update_yaxes(title_text=f"规模（{unit}）", secondary_y=False)
    fig.update_yaxes(title_text="占GDP比重（%）", secondary_y=True)

    _save(fig, output_path)


def chart_penetration(data: dict, output_path: str):
    """
    生成行业数字化渗透率雷达图
    
    data格式示例:
    {
      "title": "各行业数字化渗透率",
      "industries": ["农业", "工业", "建筑业", "批零贸易", "金融业", "服务业"],
      "values": [10.8, 24.6, 18.3, 44.7, 60.5, 45.2],
      "benchmark": [8.0, 20.0, 15.0, 40.0, 55.0, 40.0]
    }
    """
    industries = data.get("industries", [])
    values = data.get("values", [])
    benchmark = data.get("benchmark", [])
    title = data.get("title", "行业数字化渗透率雷达图")

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=industries + [industries[0]],
        fill="toself",
        name="当前水平",
        line_color="#1E90FF",
        fillcolor="rgba(30,144,255,0.2)"
    ))

    if benchmark:
        fig.add_trace(go.Scatterpolar(
            r=benchmark + [benchmark[0]],
            theta=industries + [industries[0]],
            fill="toself",
            name="基准/目标",
            line_color="#FF6B35",
            fillcolor="rgba(255,107,53,0.1)",
            line_dash="dash"
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        showlegend=True,
        font=dict(family="Microsoft YaHei, SimHei, Arial", size=13),
        height=500
    )

    _save(fig, output_path)


def chart_comparison(data: dict, output_path: str):
    """
    生成区域/企业数字经济横向对比图
    
    data格式示例:
    {
      "title": "2024年主要城市数字经济规模对比",
      "categories": ["北京", "上海", "深圳", "杭州", "广州", "成都"],
      "values": [18500, 15000, 12000, 9800, 8500, 6200],
      "unit": "亿元",
      "highlight": "深圳"
    }
    """
    categories = data.get("categories", [])
    values = data.get("values", [])
    title = data.get("title", "数字经济对比")
    unit = data.get("unit", "亿元")
    highlight = data.get("highlight", "")

    colors = ["#FF6B35" if c == highlight else "#1E90FF" for c in categories]

    # 按值排序
    sorted_data = sorted(zip(categories, values, colors), key=lambda x: x[1])
    categories_sorted = [d[0] for d in sorted_data]
    values_sorted = [d[1] for d in sorted_data]
    colors_sorted = [d[2] for d in sorted_data]

    fig = go.Figure(go.Bar(
        y=categories_sorted,
        x=values_sorted,
        orientation="h",
        marker_color=colors_sorted,
        text=[f"{v}{unit}" for v in values_sorted],
        textposition="outside"
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis=dict(title=f"规模（{unit}）"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Microsoft YaHei, SimHei, Arial", size=13),
        height=max(400, len(categories) * 60)
    )

    _save(fig, output_path)


def chart_structure(data: dict, output_path: str):
    """
    生成数字经济结构占比图（环形图）
    
    data格式示例:
    {
      "title": "2024年中国数字经济结构",
      "labels": ["数字产业化", "产业数字化"],
      "values": [8.5, 47.6],
      "unit": "万亿元"
    }
    """
    labels = data.get("labels", [])
    values = data.get("values", [])
    title = data.get("title", "数字经济结构")
    unit = data.get("unit", "")

    colors = ["#1E90FF", "#FF6B35", "#32CD32", "#FFD700", "#9370DB", "#20B2AA"]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker_colors=colors[:len(labels)],
        textinfo="label+percent",
        textfont_size=14,
        hovertemplate="%{label}: %{value}" + unit + " (%{percent})<extra></extra>"
    ))

    fig.add_annotation(
        text=f"总计<br>{sum(values)}{unit}",
        x=0.5, y=0.5,
        font_size=14,
        showarrow=False
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        font=dict(family="Microsoft YaHei, SimHei, Arial", size=13),
        height=480,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5)
    )

    _save(fig, output_path)


def chart_indicator_radar(data: dict, output_path: str):
    """
    生成综合发展指标雷达图（适用于城市/地区对比）
    
    data格式示例:
    {
      "title": "城市数字经济综合竞争力评估",
      "indicators": ["基础设施", "产业规模", "创新能力", "人才供给", "营商环境", "应用水平"],
      "cities": [
        {"name": "北京", "scores": [92, 95, 98, 90, 88, 93]},
        {"name": "上海", "scores": [94, 90, 92, 88, 92, 91]},
        {"name": "深圳", "scores": [90, 88, 90, 85, 95, 88]}
      ]
    }
    """
    indicators = data.get("indicators", [])
    cities = data.get("cities", [])
    title = data.get("title", "综合指标雷达图")

    colors = ["#1E90FF", "#FF6B35", "#32CD32", "#FFD700", "#9370DB"]
    fig = go.Figure()

    for i, city in enumerate(cities):
        scores = city["scores"]
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=indicators + [indicators[0]],
            fill="toself",
            name=city["name"],
            line_color=color,
            fillcolor=color.replace("FF", "40").replace("#", "rgba(") + ",0.15)"
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        font=dict(family="Microsoft YaHei, SimHei, Arial", size=13),
        height=520
    )

    _save(fig, output_path)


def _save(fig, output_path: str):
    """保存图表为HTML或PNG"""
    ext = os.path.splitext(output_path)[-1].lower()
    if ext == ".png":
        try:
            fig.write_image(output_path)
            print(f"图表已保存为PNG: {output_path}")
        except Exception as e:
            html_path = output_path.replace(".png", ".html")
            fig.write_html(html_path)
            print(f"PNG导出失败（需要kaleido库），已改为HTML格式保存: {html_path}")
    else:
        fig.write_html(output_path, include_plotlyjs="cdn")
        print(f"图表已保存: {output_path}")


# ============================================================
# 快速演示模式（无需数据文件）
# ============================================================

DEMO_DATA = {
    "scale_trend": {
        "title": "中国数字经济规模趋势（2019-2024）",
        "years": [2019, 2020, 2021, 2022, 2023, 2024],
        "scale": [35.8, 39.2, 45.5, 50.2, 53.9, 56.1],
        "gdp_ratio": [36.2, 38.6, 39.8, 41.5, 44.7, 47.0],
        "unit": "万亿元"
    },
    "penetration": {
        "title": "2024年各行业数字化渗透率",
        "industries": ["农业", "工业", "建筑业", "批零贸易", "金融业", "现代服务业"],
        "values": [10.8, 24.6, 18.3, 44.7, 60.5, 45.2],
        "benchmark": [15.0, 30.0, 25.0, 50.0, 65.0, 50.0]
    },
    "comparison": {
        "title": "2024年主要城市数字经济规模对比",
        "categories": ["北京", "上海", "深圳", "杭州", "广州", "成都", "武汉"],
        "values": [18500, 15000, 12000, 9800, 8500, 6200, 5800],
        "unit": "亿元",
        "highlight": "深圳"
    },
    "structure": {
        "title": "2024年中国数字经济结构",
        "labels": ["数字产业化", "产业数字化"],
        "values": [8.5, 47.6],
        "unit": "万亿元"
    },
    "indicator_radar": {
        "title": "主要城市数字经济综合竞争力（2024）",
        "indicators": ["基础设施", "产业规模", "创新能力", "人才供给", "营商环境", "应用水平"],
        "cities": [
            {"name": "北京", "scores": [92, 95, 98, 90, 88, 93]},
            {"name": "上海", "scores": [94, 90, 92, 88, 92, 91]},
            {"name": "深圳", "scores": [90, 88, 90, 85, 95, 88]}
        ]
    }
}

CHART_FUNCS = {
    "scale_trend": chart_scale_trend,
    "penetration": chart_penetration,
    "comparison": chart_comparison,
    "structure": chart_structure,
    "indicator_radar": chart_indicator_radar
}


def main():
    parser = argparse.ArgumentParser(description="数字经济数据可视化工具")
    parser.add_argument("--type", choices=list(CHART_FUNCS.keys()), 
                        default="scale_trend", help="图表类型")
    parser.add_argument("--data", help="JSON数据文件路径（不提供则使用演示数据）")
    parser.add_argument("--output", default="digital_economy_chart.html", 
                        help="输出文件路径（支持.html或.png）")
    parser.add_argument("--demo", action="store_true", help="生成所有演示图表")

    args = parser.parse_args()

    if args.demo:
        print("生成所有演示图表...")
        for chart_type, func in CHART_FUNCS.items():
            out = f"demo_{chart_type}.html"
            func(DEMO_DATA[chart_type], out)
        print("所有演示图表生成完成！")
        return

    if args.data:
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        print(f"未指定数据文件，使用内置演示数据（图表类型: {args.type}）")
        data = DEMO_DATA[args.type]

    CHART_FUNCS[args.type](data, args.output)


if __name__ == "__main__":
    main()
