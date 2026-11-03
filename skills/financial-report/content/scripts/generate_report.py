#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成脚本 - 生成专业的HTML金融分析报告

功能：
- 整合基本面、技术面、消息面分析结果
- 生成交互式图表
- 输出专业的HTML报告
- 支持一键部署

用法：
    from generate_report import ReportGenerator
    generator = ReportGenerator()
    report_path = generator.generate(report_data)
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ReportGenerator:
    """金融分析报告生成器"""

    def __init__(self, template_path: str = None):
        """
        初始化报告生成器

        Args:
            template_path: HTML模板路径，默认使用assets目录下的模板
        """
        if template_path is None:
            # 默认模板路径
            base_dir = Path(__file__).parent.parent
            template_path = base_dir / "assets" / "report_template.html"

        self.template_path = template_path
        self.template = self._load_template()

    def _load_template(self) -> str:
        """加载HTML模板"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"警告: 模板文件 {self.template_path} 未找到，使用默认模板")
            return self._get_default_template()

    def _get_default_template(self) -> str:
        """获取默认HTML模板"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}} - 金融分析报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        :root {
            --bg-primary: #0a0a0a;
            --bg-secondary: #141414;
            --bg-card: #1a1a1a;
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --text-muted: #666666;
            --accent-green: #00d26a;
            --accent-red: #ff4757;
            --accent-blue: #3b82f6;
            --accent-yellow: #f59e0b;
            --border-color: #2a2a2a;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }

        .header-left h1 {
            font-size: 32px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .header-left .subtitle {
            color: var(--text-secondary);
            font-size: 14px;
        }

        .header-right {
            text-align: right;
        }

        .rating-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .rating-buy { background: var(--accent-green); color: #000; }
        .rating-hold { background: var(--accent-yellow); color: #000; }
        .rating-sell { background: var(--accent-red); color: #fff; }

        .meta-info {
            color: var(--text-muted);
            font-size: 12px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid var(--border-color);
        }

        .card-title {
            font-size: 14px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 16px;
        }

        .metric {
            margin-bottom: 16px;
        }

        .metric-label {
            color: var(--text-muted);
            font-size: 12px;
            margin-bottom: 4px;
        }

        .metric-value {
            font-size: 24px;
            font-weight: 600;
        }

        .metric-change {
            font-size: 14px;
            margin-left: 8px;
        }

        .change-positive { color: var(--accent-green); }
        .change-negative { color: var(--accent-red); }

        .table {
            width: 100%;
            border-collapse: collapse;
        }

        .table th, .table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }

        .table th {
            color: var(--text-secondary);
            font-weight: 500;
            font-size: 12px;
            text-transform: uppercase;
        }

        .table td {
            font-size: 14px;
        }

        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 16px;
        }

        .summary-text {
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.8;
        }

        .tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .tag {
            background: var(--bg-secondary);
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 12px;
            color: var(--text-secondary);
        }

        .risk-high { border-left: 3px solid var(--accent-red); }
        .risk-medium { border-left: 3px solid var(--accent-yellow); }
        .risk-low { border-left: 3px solid var(--accent-green); }

        .disclaimer {
            margin-top: 40px;
            padding: 20px;
            background: var(--bg-secondary);
            border-radius: 8px;
            font-size: 12px;
            color: var(--text-muted);
        }

        .disclaimer strong {
            color: var(--text-secondary);
        }
    </style>
</head>
<body>
    <div class="container">
        {{CONTENT}}
    </div>
</body>
</html>
"""

    def generate(self, data: Dict, output_path: str = None) -> str:
        """
        生成HTML报告

        Args:
            data: 分析数据，包含以下字段：
                - symbol: 股票代码
                - name: 公司名称
                - info: 基本信息
                - financial: 财务数据
                - technical: 技术分析
                - news: 消息面
                - macro: 宏观分析
                - rating: 评级
                - target_price: 目标价
                - upside: 上升空间
                - risks: 风险因素
            output_path: 输出文件路径

        Returns:
            str: 生成的HTML内容
        """
        content = self._build_content(data)
        html = self.template.replace("{{CONTENT}}", content)
        html = html.replace("{{TITLE}}", f"{data.get('name', 'N/A')} ({data.get('symbol', '')})")

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

        return html

    def _build_content(self, data: Dict) -> str:
        """构建报告内容"""
        sections = []

        # 头部信息
        sections.append(self._build_header(data))

        # 关键指标卡片
        sections.append(self._build_metrics_section(data))

        # 财务分析
        sections.append(self._build_financial_section(data))

        # 估值分析
        sections.append(self._build_valuation_section(data))

        # 技术分析
        sections.append(self._build_technical_section(data))

        # 消息面分析
        sections.append(self._build_news_section(data))

        # 投资建议
        sections.append(self._build_recommendation_section(data))

        # 风险因素
        sections.append(self._build_risks_section(data))

        # 免责声明
        sections.append(self._build_disclaimer())

        return '\n'.join(sections)

    def _build_header(self, data: Dict) -> str:
        """构建头部区域"""
        rating = data.get("rating", "hold")
        rating_text = {"buy": "买入", "hold": "持有", "sell": "卖出"}.get(rating.lower(), "持有")
        rating_class = f"rating-{rating.lower()}"

        return f'''
        <div class="header">
            <div class="header-left">
                <h1>{data.get("name", "N/A")} ({data.get("symbol", "")})</h1>
                <div class="subtitle">
                    {data.get("industry", "")} | {data.get("exchange", "")}
                </div>
            </div>
            <div class="header-right">
                <div class="rating-badge {rating_class}">{rating_text}</div>
                <div class="meta-info">
                    <div>报告日期: {datetime.now().strftime("%Y-%m-%d")}</div>
                    <div>目标价: ¥{data.get("target_price", "N/A")}</div>
                    <div>上升空间: {data.get("upside", "N/A")}%</div>
                </div>
            </div>
        </div>
        '''

    def _build_metrics_section(self, data: Dict) -> str:
        """构建关键指标卡片"""
        metrics = data.get("key_metrics", {})

        price = metrics.get("price", "N/A")
        change = metrics.get("change", 0)
        change_class = "change-positive" if change >= 0 else "change-negative"
        change_sign = "+" if change >= 0 else ""

        market_cap = metrics.get("market_cap", 0)
        if market_cap:
            if market_cap >= 1e12:
                market_cap_str = f"¥{market_cap/1e12:.2f}万亿"
            elif market_cap >= 1e8:
                market_cap_str = f"¥{market_cap/1e8:.2f}亿"
            else:
                market_cap_str = f"¥{market_cap:.0f}"

        return f'''
        <div class="grid">
            <div class="card">
                <div class="card-title">当前价格</div>
                <div class="metric-value">
                    ¥{price}
                    <span class="metric-change {change_class}">{change_sign}{change}%</span>
                </div>
            </div>
            <div class="card">
                <div class="card-title">总市值</div>
                <div class="metric-value">{market_cap_str}</div>
            </div>
            <div class="card">
                <div class="card-title">市盈率 (PE)</div>
                <div class="metric-value">{metrics.get("pe", "N/A")}</div>
            </div>
            <div class="card">
                <div class="card-title">市净率 (PB)</div>
                <div class="metric-value">{metrics.get("pb", "N/A")}</div>
            </div>
        </div>
        '''

    def _build_financial_section(self, data: Dict) -> str:
        """构建财务分析区域"""
        financials = data.get("financial", {})

        rows = []
        for item in financials.get("items", []):
            name = item.get("name", "")
            value = item.get("value", "N/A")
            change = item.get("change", 0)
            change_class = "change-positive" if change >= 0 else "change-negative"
            change_sign = "+" if change >= 0 else ""

            rows.append(f'''
            <tr>
                <td>{name}</td>
                <td>{value}</td>
                <td class="{change_class}">{change_sign}{change}%</td>
                <td>{item.get("comparison", "N/A")}</td>
            </tr>
            ''')

        return f'''
        <div class="card" style="margin-bottom: 20px;">
            <div class="card-title">财务分析</div>
            <table class="table">
                <thead>
                    <tr>
                        <th>指标</th>
                        <th>最新值</th>
                        <th>同比变化</th>
                        <th>行业对比</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
        '''

    def _build_valuation_section(self, data: Dict) -> str:
        """构建估值分析区域"""
        valuation = data.get("valuation", {})

        rows = []
        for item in valuation.get("items", []):
            name = item.get("name", "")
            value = item.get("value", "N/A")
            percentile = item.get("percentile", "N/A")
            industry = item.get("industry_avg", "N/A")

            rows.append(f'''
            <tr>
                <td>{name}</td>
                <td>{value}</td>
                <td>{percentile}%</td>
                <td>{industry}</td>
            </tr>
            ''')

        return f'''
        <div class="card" style="margin-bottom: 20px;">
            <div class="card-title">估值分析</div>
            <table class="table">
                <thead>
                    <tr>
                        <th>估值指标</th>
                        <th>当前值</th>
                        <th>历史分位</th>
                        <th>行业均值</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
        '''

    def _build_technical_section(self, data: Dict) -> str:
        """构建技术分析区域"""
        technical = data.get("technical", {})
        signals = technical.get("signals", {})

        ma_trend = signals.get("ma_trend", "缠绕")
        macd_signal = signals.get("macd", "中性")
        rsi_value = signals.get("rsi", 50)
        bb_position = signals.get("bollinger", "中性")

        return f'''
        <div class="card" style="margin-bottom: 20px;">
            <div class="card-title">技术分析</div>
            <div class="grid">
                <div>
                    <div class="metric-label">均线系统</div>
                    <div class="metric">{ma_trend}</div>
                </div>
                <div>
                    <div class="metric-label">MACD</div>
                    <div class="metric">{macd_signal}</div>
                </div>
                <div>
                    <div class="metric-label">RSI</div>
                    <div class="metric">{rsi_value:.1f}</div>
                </div>
                <div>
                    <div class="metric-label">布林带</div>
                    <div class="metric">{bb_position}</div>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="priceChart"></canvas>
            </div>
        </div>
        '''

    def _build_news_section(self, data: Dict) -> str:
        """构建消息面分析区域"""
        news = data.get("news", {})

        items = news.get("items", [])
        if not items:
            return '''
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-title">消息面分析</div>
                <p class="summary-text">暂无重要消息</p>
            </div>
            '''

        rows = []
        for item in items[:5]:
            date = item.get("date", "")
            title = item.get("title", "")
            sentiment = item.get("sentiment", "中性")
            sentiment_class = {
                "利好": "change-positive",
                "利空": "change-negative",
                "中性": ""
            }.get(sentiment, "")

            rows.append(f'''
            <tr>
                <td>{date}</td>
                <td>{title}</td>
                <td class="{sentiment_class}">{sentiment}</td>
            </tr>
            ''')

        return f'''
        <div class="card" style="margin-bottom: 20px;">
            <div class="card-title">消息面分析</div>
            <table class="table">
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>标题</th>
                        <th>情绪</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
        '''

    def _build_recommendation_section(self, data: Dict) -> str:
        """构建投资建议区域"""
        recommendation = data.get("recommendation", {})

        return f'''
        <div class="card" style="margin-bottom: 20px;">
            <div class="card-title">投资建议</div>
            <div class="grid">
                <div>
                    <div class="metric-label">目标价</div>
                    <div class="metric">¥{recommendation.get("target_price", "N/A")}</div>
                </div>
                <div>
                    <div class="metric-label">上升空间</div>
                    <div class="metric change-positive">+{recommendation.get("upside", "N/A")}%</div>
                </div>
                <div>
                    <div class="metric-label">止损价</div>
                    <div class="metric change-negative">¥{recommendation.get("stop_loss", "N/A")}</div>
                </div>
                <div>
                    <div class="metric-label">核心逻辑</div>
                    <div class="metric">{recommendation.get("logic", "N/A")}</div>
                </div>
            </div>
        </div>
        '''

    def _build_risks_section(self, data: Dict) -> str:
        """构建风险因素区域"""
        risks = data.get("risks", [])

        if not risks:
            return ''

        risk_items = []
        for risk in risks:
            level = risk.get("level", "medium")
            level_text = {"high": "高风险", "medium": "中风险", "low": "低风险"}.get(level, "中风险")

            risk_items.append(f'''
            <li style="margin-bottom: 12px;">
                <strong>[{level_text}]</strong> {risk.get("description", "")}
            </li>
            ''')

        return f'''
        <div class="card risk-medium" style="margin-bottom: 20px;">
            <div class="card-title">风险因素</div>
            <ul style="list-style: none; padding: 0;">
                {''.join(risk_items)}
            </ul>
        </div>
        '''

    def _build_disclaimer(self) -> str:
        """构建免责声明"""
        return '''
        <div class="disclaimer">
            <strong>免责声明</strong><br><br>
            本报告由AI系统自动生成，仅供研究参考和学习交流使用。<br>
            本报告不构成任何投资建议，投资者应自主做出投资决策，并承担投资风险。<br>
            报告中的信息、数据和观点可能存在延迟或错误，不对准确性做任何保证。<br>
            过往业绩不代表未来表现，投资有风险，入市需谨慎。
        </div>
        '''

    def generate_with_price_chart(self, data: Dict, price_data: Dict, output_path: str = None) -> str:
        """
        生成包含价格走势图的HTML报告

        Args:
            data: 分析数据
            price_data: 价格数据（用于绑定图表）
            output_path: 输出文件路径

        Returns:
            str: 生成的HTML内容
        """
        html = self.generate(data, output_path)

        # 添加图表数据
        if price_data and price_data.get("success"):
            chart_script = f'''
            <script>
                const priceData = {json.dumps(price_data.get('data', {}), default=str)};
                const ctx = document.getElementById('priceChart').getContext('2d');

                new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: priceData.dates,
                        datasets: [{{
                            label: '收盘价',
                            data: priceData.close,
                            borderColor: '#00d26a',
                            backgroundColor: 'rgba(0, 210, 106, 0.1)',
                            fill: true,
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                display: true,
                                labels: {{ color: '#a0a0a0' }}
                            }}
                        }},
                        scales: {{
                            x: {{
                                type: 'time',
                                time: {{
                                    unit: 'month'
                                }},
                                grid: {{
                                    color: '#2a2a2a'
                                }},
                                ticks: {{
                                    color: '#666666'
                                }}
                            }},
                            y: {{
                                grid: {{
                                    color: '#2a2a2a'
                                }},
                                ticks: {{
                                    color: '#666666'
                                }}
                            }}
                        }}
                    }}
                }});
            </script>
            '''

            # 在</body>前插入图表脚本
            html = html.replace('</body>', chart_script + '</body>')

        return html


def generate_sample_report(symbol: str = "600519.SS", output_path: str = None) -> str:
    """
    生成示例报告（用于测试）

    Args:
        symbol: 股票代码
        output_path: 输出路径

    Returns:
        str: HTML报告内容
    """
    generator = ReportGenerator()

    # 示例数据
    sample_data = {
        "symbol": symbol,
        "name": "贵州茅台",
        "industry": "白酒",
        "exchange": "上交所",
        "rating": "buy",
        "target_price": 2200,
        "upside": 25,
        "key_metrics": {
            "price": 1760.00,
            "change": 2.5,
            "market_cap": 2.21e12,
            "pe": 35.2,
            "pb": 12.5,
            "dividend_yield": 1.2
        },
        "financial": {
            "items": [
                {"name": "营业收入", "value": "1275.56亿", "change": 16.5, "comparison": "优"},
                {"name": "净利润", "value": "651.87亿", "change": 19.1, "comparison": "优"},
                {"name": "毛利率", "value": "91.97%", "change": 0.3, "comparison": "优"},
                {"name": "ROE", "value": "30.26%", "change": 2.5, "comparison": "优"},
            ]
        },
        "valuation": {
            "items": [
                {"name": "市盈率(PE)", "value": "35.2", "percentile": "45", "industry_avg": "32.5"},
                {"name": "市净率(PB)", "value": "12.5", "percentile": "52", "industry_avg": "10.2"},
                {"name": "市销率(PS)", "value": "17.3", "percentile": "48", "industry_avg": "15.8"},
            ]
        },
        "technical": {
            "signals": {
                "ma_trend": "多头排列",
                "macd": "金叉",
                "rsi": 62.5,
                "bollinger": "中轨上方"
            }
        },
        "news": {
            "items": [
                {"date": "2024-04-10", "title": "Q1业绩超预期", "sentiment": "利好"},
                {"date": "2024-04-05", "title": "提价公告", "sentiment": "利好"},
                {"date": "2024-03-28", "title": "行业政策变化", "sentiment": "中性"},
            ]
        },
        "recommendation": {
            "target_price": 2200,
            "upside": 25,
            "stop_loss": 1580,
            "logic": "业绩稳健增长，酱香龙头地位稳固，估值合理"
        },
        "risks": [
            {"level": "medium", "description": "消费复苏不及预期"},
            {"level": "low", "description": "食品安全风险"},
        ]
    }

    return generator.generate(sample_data, output_path)


def main():
    """测试脚本"""
    print("生成示例报告...")

    output_path = "/workspace/financial-report/sample_report.html"
    html = generate_sample_report("600519.SS", output_path)

    print(f"报告已生成: {output_path}")
    print(f"文件大小: {len(html)} bytes")


if __name__ == "__main__":
    main()
