#!/usr/bin/env python3
"""
门店选址分析脚本
Store Location Analysis Runner

此脚本提供可复现的完整分析流程

Requirements:
    pip install pandas numpy matplotlib seaborn scipy scikit-learn statsmodels

Usage:
    python analysis_runner.py --city "上海" --district "陆家嘴" --store-type "咖啡店"
"""

import argparse
import json
import warnings
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.spatial.distance import cdist
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings('ignore')

# 全局字体设置
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 输出目录
OUTPUT_DIR = Path('output')
OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================================
# 模块1: 市场容量分析 (TAM/SAM/SOM)
# =============================================================================

def calculate_market_pyramid(population, avg_consumption, penetration_rate, target_share):
    """计算TAM/SAM/SOM金字塔模型"""
    tam = population * avg_consumption
    sam = tam * penetration_rate
    som = sam * target_share
    return {'TAM': tam, 'SAM': sam, 'SOM': som}


def plot_market_pyramid(market_data, output_path):
    """绘制市场金字塔图"""
    levels = ['TAM', 'SAM', 'SOM']
    values = [market_data[k] / 1e8 for k in levels]  # 转换为亿元

    fig, ax = plt.subplots(figsize=(10, 8))

    colors = ['#1976D2', '#42A5F5', '#81C784']
    widths = [0.8, 0.6, 0.4]
    heights = [0.3, 0.25, 0.2]

    for i, (level, val, color, w, h) in enumerate(zip(levels, values, colors, widths, heights)):
        ax.bar(0.5, h, bottom=i * 0.35, width=w, color=color, alpha=0.9)
        ax.text(0.5, i * 0.35 + h / 2, f'{level}: ¥{val:.1f}B',
                ha='center', va='center', fontsize=12, fontweight='bold',
                color='white')

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('Market Size Pyramid (TAM/SAM/SOM)', fontsize=14, fontweight='bold', pad=20)
    ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    return str(output_path)


# =============================================================================
# 模块2: 竞争强度分析
# =============================================================================

def calculate_competition_metrics(competitor_locations, candidate_location, total_area_km2):
    """计算竞争强度指标"""
    poi_density = len(competitor_locations) / total_area_km2
    distances = cdist([candidate_location], competitor_locations, 'euclidean')
    nearest_distance = np.min(distances) * 111000  # 度转km转m
    return {
        'poi_density': round(poi_density, 2),
        'nearest_distance': round(float(nearest_distance), 0),
        'competitor_count': len(competitor_locations)
    }


def distance_decay(x, a, b):
    """距离衰减函数: y = a * x^(-b)"""
    return a * np.power(x, -b)


def fit_decay_function(competition_data):
    """拟合距离衰减函数"""
    x_data = competition_data['distance'].values
    y_data = competition_data['sales_impact'].values
    popt, _ = curve_fit(distance_decay, x_data, y_data, p0=[1, 0.5], maxfev=5000)
    return {'a': popt[0], 'b': popt[1]}


# =============================================================================
# 模块3: 客群匹配度
# =============================================================================

def calculate_customer_match(ideal_profile, actual_profile, weights):
    """计算客群匹配指数"""
    scores = {}

    # 年龄匹配度
    age_diff = abs(ideal_profile['avg_age'] - actual_profile['avg_age'])
    scores['age'] = max(0, min(100, (1 - age_diff / 30) * 100))

    # 收入匹配度
    ideal_min, ideal_max = ideal_profile['income_range']
    actual_p25 = actual_profile['income_p25']
    actual_p75 = actual_profile['income_p75']
    overlap = max(0, min(ideal_max, actual_p75) - max(ideal_min, actual_p25))
    ideal_span = ideal_max - ideal_min
    scores['income'] = (min(1, overlap / ideal_span) * 100) if ideal_span > 0 else 0

    # 偏好匹配
    overlap_count = len(set(ideal_profile['preferences']) &
                       set(actual_profile['top_categories']))
    scores['preference'] = (overlap_count / len(ideal_profile['preferences'])) * 100

    # 综合得分
    total = sum(scores[k] * weights.get(k, 0) for k in scores)
    weight_sum = sum(weights.values())

    return {
        'age_match': round(scores['age'], 1),
        'income_match': round(scores['income'], 1),
        'preference_match': round(scores['preference'], 1),
        'overall_score': round(total / weight_sum, 1)
    }


def plot_radar_chart(match_scores, output_path):
    """绘制客群匹配雷达图"""
    dimensions = ['Age Match', 'Income Match', 'Preference Match']
    values = [match_scores['age_match'], match_scores['income_match'], match_scores['preference_match']]
    values += values[:1]

    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    ax.plot(angles, values, 'o-', linewidth=2, color='#1976D2')
    ax.fill(angles, values, alpha=0.25, color='#1976D2')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_title('Customer Profile Match', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    return str(output_path)


# =============================================================================
# 模块4: 销量预测
# =============================================================================

class SalesForecastModel:
    """销量预测模型"""

    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()

    def build_model(self, historical_data):
        """构建多元回归模型"""
        features = ['footfall', 'price', 'promotion', 'season']
        X = historical_data[features].values
        y = historical_data['sales'].values

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

        return {
            'coefficients': dict(zip(features, self.model.coef_)),
            'intercept': self.model.intercept_,
            'r_squared': self.model.score(X_scaled, y)
        }

    def predict(self, forecast_data):
        """预测销量"""
        X = forecast_data[['footfall', 'price', 'promotion', 'season']].values
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)


def plot_sales_forecast(forecast_data, output_path):
    """绘制销售预测图"""
    months = range(1, len(forecast_data) + 1)

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(months, forecast_data, 'b-', linewidth=2, marker='o', label='Forecast')
    ax.fill_between(months,
                   [f * 0.85 for f in forecast_data],
                   [f * 1.15 for f in forecast_data],
                   alpha=0.2, color='blue', label='Confidence Interval')

    ax.set_xlabel('Month', fontsize=11)
    ax.set_ylabel('Sales (CNY)', fontsize=11)
    ax.set_title('12-Month Sales Forecast', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xticks(months)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    return str(output_path)


# =============================================================================
# 模块5: 成本与盈亏分析
# =============================================================================

def calculate_cost_structure(rent_per_sqm, area, staff_count, avg_salary, marketing_budget):
    """计算成本结构"""
    monthly_rent = rent_per_sqm * area
    monthly_salary = staff_count * avg_salary
    fixed_costs = monthly_rent + monthly_salary + marketing_budget

    return {
        'rent': monthly_rent,
        'salary': monthly_salary,
        'marketing': marketing_budget,
        'fixed_total': fixed_costs
    }


def calculate_bep(unit_price, unit_variable_cost, fixed_costs):
    """计算盈亏平衡点"""
    contribution = unit_price - unit_variable_cost
    bep_units = fixed_costs / contribution
    return {
        'bep_units': int(bep_units),
        'bep_revenue': round(bep_units * unit_price, 2),
        'contribution_margin': contribution
    }


def calculate_payback(initial_investment, monthly_net_income):
    """计算投资回收期"""
    return initial_investment / monthly_net_income


# =============================================================================
# 模块6: 选址评分
# =============================================================================

def calculate_location_score(candidate_data, weights):
    """计算候选点综合评分"""
    df = candidate_data.copy()

    # 标准化: 人流、匹配度、可达性（越高越好）
    for col in ['footfall', 'match_score', 'accessibility']:
        col_min, col_max = df[col].min(), df[col].max()
        df[f'{col}_norm'] = (df[col] - col_min) / (col_max - col_min) * 100

    # 标准化: 租金、竞争（越低越好）
    for col in ['rent', 'competition_index']:
        col_min, col_max = df[col].min(), df[col].max()
        df[f'{col}_norm'] = (col_max - df[col]) / (col_max - col_min) * 100

    # 综合评分
    df['Total_Score'] = (
        df['footfall_norm'] * weights['footfall'] +
        df['rent_norm'] * weights['rent'] +
        df['match_score_norm'] * weights['match'] +
        df['competition_index_norm'] * weights['competition'] +
        df['accessibility_norm'] * weights['accessibility']
    )

    df['Rank'] = df['Total_Score'].rank(ascending=False).astype(int)

    return df.sort_values('Rank')[['name', 'Total_Score', 'Rank']]


def plot_ranking_chart(ranking_data, output_path):
    """绘制排名条形图"""
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['#388E3C' if i == 1 else '#1976D2' for i in ranking_data['Rank']]
    bars = ax.barh(ranking_data['name'], ranking_data['Total_Score'], color=colors)

    for bar, score in zip(bars, ranking_data['Total_Score']):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
               f'{score:.1f}', va='center', fontsize=10)

    ax.set_xlabel('Total Score', fontsize=11)
    ax.set_title('Location Ranking', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 110)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    return str(output_path)


# =============================================================================
# MBA战略分析
# =============================================================================

def generate_pest_analysis():
    """生成PEST分析（需要根据具体城市/行业填充）"""
    return {
        'political': '政策环境评估...',
        'economic': '经济环境评估...',
        'social': '社会文化评估...',
        'technological': '技术环境评估...'
    }


def generate_porters_five_forces():
    """生成波特五力分析"""
    return {
        'competitive_rivalry': {'score': 7, 'assessment': '行业竞争激烈'},
        'threat_of_new_entrants': {'score': 5, 'assessment': '进入壁垒中等'},
        'threat_of_substitutes': {'score': 6, 'assessment': '替代品威胁较大'},
        'buyer_power': {'score': 6, 'assessment': '买家议价能力较强'},
        'supplier_power': {'score': 4, 'assessment': '供应商议价能力较弱'}
    }


def generate_swot_analysis(strengths, weaknesses, opportunities, threats):
    """生成SWOT分析"""
    return {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'opportunities': opportunities,
        'threats': threats
    }


# =============================================================================
# HTML报告生成
# =============================================================================

def generate_html_report(analysis_results, output_path):
    """生成完整的HTML分析报告"""

    # 决策判定
    decision = 'RECOMMENDED' if analysis_results['final_score'] >= 60 else 'NOT RECOMMENDED'
    decision_cn = '推荐进入' if decision == 'RECOMMENDED' else '建议不进入'

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>门店选址分析报告 - {analysis_results['city']}{analysis_results['district']}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        {open(OUTPUT_DIR / 'styles.css').read() if (OUTPUT_DIR / 'styles.css').exists() else ''}
    </style>
</head>
<body>
    <div class="container">
        <!-- 封面 -->
        <div class="cover">
            <h1>Store Location Analysis Report</h1>
            <p class="subtitle">门店选址分析报告</p>
            <div class="location-tag">{analysis_results['city']} · {analysis_results['district']}</div>
            <div class="decision-badge {'decision-enter' if decision == 'RECOMMENDED' else 'decision-reject'}">
                {'✅ ' + decision_cn}
            </div>
            <p class="confidence">Confidence Level: {analysis_results['confidence']}%</p>
        </div>

        <!-- 目录 -->
        <div class="toc">
            <div class="toc-title">Table of Contents</div>
            <ul class="toc-list">
                <li><a href="#market">Market Analysis | 市场分析</a></li>
                <li><a href="#competition">Competition | 竞争分析</a></li>
                <li><a href="#customer">Customer Match | 客群匹配</a></li>
                <li><a href="#forecast">Sales Forecast | 销量预测</a></li>
                <li><a href="#cost">Cost Analysis | 成本分析</a></li>
                <li><a href="#ranking">Ranking | 综合评分</a></li>
                <li><a href="#strategy">Strategy | 战略分析</a></li>
                <li><a href="#assumptions">Assumptions | 假设条件</a></li>
            </ul>
        </div>

        <!-- 市场分析 -->
        <div class="section active" id="market">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <span class="section-icon">1</span>
                    Market Size Analysis | 市场容量分析
                </div>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <div class="card-grid">
                    <div class="card">
                        <div class="card-title">TAM (Total Addressable Market)</div>
                        <div class="card-value">¥{analysis_results['market']['TAM']/1e8:.2f}B</div>
                    </div>
                    <div class="card">
                        <div class="card-title">SAM (Serviceable)</div>
                        <div class="card-value">¥{analysis_results['market']['SAM']/1e8:.2f}B</div>
                    </div>
                    <div class="card">
                        <div class="card-title">SOM (Obtainable)</div>
                        <div class="card-value">¥{analysis_results['market']['SOM']/1e8:.2f}B</div>
                    </div>
                </div>
                <div class="chart-container">
                    <img src="market_pyramid.png" alt="Market Pyramid" style="width:100%;max-width:600px;">
                </div>
            </div>
        </div>

        <!-- 竞争分析 -->
        <div class="section" id="competition">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <span class="section-icon">2</span>
                    Competition Analysis | 竞争强度分析
                </div>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <div class="card-grid">
                    <div class="card">
                        <div class="card-title">POI Density | 竞品密度</div>
                        <div class="card-value">{analysis_results['competition']['poi_density']}</div>
                        <div class="card-unit">per km²</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Nearest Competitor | 最近竞品</div>
                        <div class="card-value">{analysis_results['competition']['nearest_distance']:.0f}</div>
                        <div class="card-unit">meters</div>
                    </div>
                    <div class="card">
                        <div class="card-title">HHI Index</div>
                        <div class="card-value">{analysis_results['competition'].get('hhi', 'N/A')}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 客群匹配 -->
        <div class="section" id="customer">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <span class="section-icon">3</span>
                    Customer Match | 客群匹配度
                </div>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <div class="card-grid">
                    <div class="card">
                        <div class="card-title">Overall Score | 综合得分</div>
                        <div class="card-value">{analysis_results['customer_match']['overall_score']}</div>
                    </div>
                </div>
                <div class="chart-container">
                    <img src="radar_chart.png" alt="Radar Chart" style="width:100%;max-width:400px;">
                </div>
            </div>
        </div>

        <!-- 销售预测 -->
        <div class="section" id="forecast">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <span class="section-icon">4</span>
                    Sales Forecast | 销量预测
                </div>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <div class="chart-container">
                    <img src="sales_forecast.png" alt="Sales Forecast" style="width:100%;">
                </div>
            </div>
        </div>

        <!-- 成本分析 -->
        <div class="section" id="cost">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <span class="section-icon">5</span>
                    Cost & Breakeven | 成本与盈亏
                </div>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <div class="card-grid">
                    <div class="card">
                        <div class="card-title">Breakeven Point | 盈亏平衡</div>
                        <div class="card-value">{analysis_results['breakeven']['bep_units']:,}</div>
                        <div class="card-unit">units/month</div>
                    </div>
                    <div class="card">
                        <div class="card-title">Monthly Fixed Cost</div>
                        <div class="card-value">¥{analysis_results['cost']['fixed_total']:,.0f}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 综合评分 -->
        <div class="section" id="ranking">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <span class="section-icon">6</span>
                    Final Ranking | 综合评分
                </div>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <div class="chart-container">
                    <img src="ranking.png" alt="Ranking" style="width:100%;">
                </div>
            </div>
        </div>

        <!-- 战略分析 -->
        <div class="section" id="strategy">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <span class="section-icon">S</span>
                    MBA Strategy Analysis | MBA战略分析
                </div>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <!-- SWOT -->
                <div class="swot-grid">
                    <div class="swot-item swot-strengths">
                        <div class="swot-label">Strengths | 优势</div>
                        <p>{analysis_results['swot'].get('strengths', 'N/A')}</p>
                    </div>
                    <div class="swot-item swot-weaknesses">
                        <div class="swot-label">Weaknesses | 劣势</div>
                        <p>{analysis_results['swot'].get('weaknesses', 'N/A')}</p>
                    </div>
                    <div class="swot-item swot-opportunities">
                        <div class="swot-label">Opportunities | 机会</div>
                        <p>{analysis_results['swot'].get('opportunities', 'N/A')}</p>
                    </div>
                    <div class="swot-item swot-threats">
                        <div class="swot-label">Threats | 威胁</div>
                        <p>{analysis_results['swot'].get('threats', 'N/A')}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- 假设条件 -->
        <div class="section" id="assumptions">
            <div class="section-header" onclick="toggleSection(this)">
                <div class="section-title">
                    <span class="section-icon">A</span>
                    Data Assumptions | 数据假设
                </div>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="section-content">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Assumption | 假设项</th>
                            <th>Value | 假设值</th>
                            <th>Impact | 影响程度</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f"<tr><td>{a['item']}</td><td>{a['value']}</td><td class='assumption-{a['impact']}'>{a['impact'].upper()}</td></tr>" for a in analysis_results.get('assumptions', [])])}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 页脚 -->
        <div class="footer">
            <div class="footer-title">Data Sources | 数据来源</div>
            <ul class="source-list">
                {''.join([f"<li>{s['name']}: <a href='{s['url']}'>{s['url']}</a> (Updated: {s['update_date']})</li>" for s in analysis_results.get('sources', [])])}
            </ul>
            <p style="margin-top:20px;font-size:0.85rem;">
                Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                Tool Version: Python 3.x, Pandas {pd.__version__}, Matplotlib {plt.matplotlib.__version__}
            </p>
        </div>
    </div>

    <script>
        function toggleSection(header) {{
            header.parentElement.classList.toggle('active');
        }}
    </script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return str(output_path)


# =============================================================================
# 主函数
# =============================================================================

def main(city, district, store_type, **kwargs):
    """主分析流程"""

    print(f"Starting analysis for {city} {district} {store_type}...")

    # 模拟数据获取（实际使用时替换为真实数据源）
    # 此处使用示例数据，实际应用中应接入真实数据API
    population = kwargs.get('population', 500000)
    avg_consumption = kwargs.get('avg_consumption', 25000)
    penetration_rate = kwargs.get('penetration_rate', 0.15)
    target_share = kwargs.get('target_share', 0.05)

    # 模块1: 市场容量
    market_data = calculate_market_pyramid(
        population, avg_consumption, penetration_rate, target_share
    )
    plot_market_pyramid(market_data, OUTPUT_DIR / 'market_pyramid.png')

    # 模块3: 客群匹配
    ideal_profile = {'avg_age': 30, 'income_range': (15000, 30000), 'preferences': ['coffee', 'pastry']}
    actual_profile = {'avg_age': 28, 'income_p25': 12000, 'income_p75': 28000, 'top_categories': ['coffee', 'dessert']}
    weights = {'age': 0.4, 'income': 0.3, 'preference': 0.3}
    match_scores = calculate_customer_match(ideal_profile, actual_profile, weights)
    plot_radar_chart(match_scores, OUTPUT_DIR / 'radar_chart.png')

    # 模块4: 销量预测
    forecast_data = [50000 + i*2000 + np.random.randint(-5000, 5000) for i in range(12)]
    plot_sales_forecast(forecast_data, OUTPUT_DIR / 'sales_forecast.png')

    # 模块5: 成本
    cost_data = calculate_cost_structure(
        rent_per_sqm=200, area=100, staff_count=5, avg_salary=8000, marketing_budget=10000
    )
    breakeven_data = calculate_bep(unit_price=50, unit_variable_cost=20, fixed_costs=cost_data['fixed_total'])

    # 模块6: 评分
    candidates = pd.DataFrame({
        'name': ['Location A', 'Location B', 'Location C'],
        'footfall': [5000, 3500, 4200],
        'rent': [25000, 18000, 22000],
        'match_score': [85, 70, 78],
        'competition_index': [0.4, 0.3, 0.35],
        'accessibility': [90, 75, 85]
    })
    weights = {'footfall': 0.30, 'rent': 0.20, 'match': 0.25, 'competition': 0.15, 'accessibility': 0.10}
    ranking = calculate_location_score(candidates, weights)
    plot_ranking_chart(ranking, OUTPUT_DIR / 'ranking.png')

    # 组装结果
    results = {
        'city': city,
        'district': district,
        'store_type': store_type,
        'market': market_data,
        'customer_match': match_scores,
        'competition': {'poi_density': 12.5, 'nearest_distance': 350},
        'breakeven': breakeven_data,
        'cost': cost_data,
        'final_score': ranking.iloc[0]['Total_Score'],
        'confidence': 85,
        'swot': {
            'strengths': 'High footfall location with good demographics',
            'weaknesses': 'Premium rent costs',
            'opportunities': 'Growing coffee culture in area',
            'threats': 'Intense competition from established brands'
        },
        'assumptions': [
            {'item': 'Conversion Rate', 'value': '5%', 'impact': 'high'},
            {'item': 'AOV', 'value': '¥45', 'impact': 'medium'},
            {'item': 'Rent Growth', 'value': '3%/year', 'impact': 'low'}
        ],
        'sources': [
            {'name': 'City Statistics Bureau', 'url': 'https://example.com', 'update_date': '2026-01-15'}
        ]
    }

    # 生成HTML报告
    report_path = generate_html_report(results, OUTPUT_DIR / 'report.html')

    print(f"Analysis complete. Report saved to: {report_path}")

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Store Location Analysis')
    parser.add_argument('--city', required=True, help='City name')
    parser.add_argument('--district', required=True, help='District/商圈 name')
    parser.add_argument('--store-type', required=True, help='Store type')
    args = parser.parse_args()

    main(args.city, args.district, args.store_type)
