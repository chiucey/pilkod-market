---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3044022052d5e6498b1988d76c91bc32f2aa54eabb66cbd15a5e8fb9baf223b840f72995022024e905e54306f8a6110c9d93b29a50ca8e46899ae5cbc651f2a58cca95dfa5e0
    ReservedCode2: 304402202063184a3a60f448f7fc2614bd9d2edfd46cb5be6f7e09d420ab53a8df3bf85102205b4432d3449883f9ba1f423f31858df23822f91f77225aee282273bf27410ae1
---

# 六大分析模块详细规格

## 模块① 商圈画像与可服务市场 (TAM/SAM/SOM)

### 计算公式

```
TAM (Total Addressable Market) = 区域总人口 × 人均年消费额
SAM (Serviceable Addressable Market) = 目标商圈覆盖人口 × 人均年消费额 × 品类渗透率
SOM (Serviceable Obtainable Market) = SAM × 预期市场份额
```

### Python实现

```python
def calculate_market_pyramid(population, avg_consumption, penetration_rate, target_share):
    """
    计算TAM/SAM/SOM金字塔模型

    Parameters:
    -----------
    population : int - 区域总人口
    avg_consumption : float - 人均年消费额（元）
    penetration_rate : float - 品类渗透率（0-1）
    target_share : float - 目标市场份额（0-1）

    Returns:
    --------
    dict: {'TAM': float, 'SAM': float, 'SOM': float}
    """
    tam = population * avg_consumption
    sam = tam * penetration_rate
    som = sam * target_share

    return {
        'TAM': tam,
        'SAM': sam,
        'SOM': som
    }

# 示例数据
market_data = calculate_market_pyramid(
    population=500000,      # 50万人口
    avg_consumption=25000,  # 人均年消费2.5万
    penetration_rate=0.15,  # 品类渗透率15%
    target_share=0.05      # 目标市场份额5%
)
```

### 输出图表规格
- 类型：垂直金字塔图
- 颜色梯度：TAM(蓝) → SAM(青) → SOM(绿)
- 标注：数值 + 百分比
- 字体：DejaVu Sans, 英文标签

---

## 模块② 竞争强度分析

### 核心指标

```python
import numpy as np
from scipy.spatial.distance import cdist

def calculate_competition_metrics(competitor_locations, candidate_location, total_area_km2):
    """
    计算竞争强度指标

    Parameters:
    -----------
    competitor_locations : np.array - 竞品坐标 [[lat, lon], ...]
    candidate_location : np.array - 候选点坐标 [lat, lon]
    total_area_km2 : float - 分析区域面积(km²)

    Returns:
    --------
    dict: {'poi_density': float, 'nearest_distance': float, 'hhi': float}
    """
    # POI密度 (竞品数/km²)
    poi_density = len(competitor_locations) / total_area_km2

    # 最近邻距离 (m)
    distances = cdist([candidate_location], competitor_locations, metric='euclidean')
    nearest_distance = np.min(distances) * 111000  # 度转km再转m

    # HHI指数（需要市场份额数据）
    # HHI = Σ(Market_Share_i)² × 10000
    # < 1500: 低集中, 1500-2500: 中集中, > 2500: 高集中

    return {
        'poi_density': round(poi_density, 2),
        'nearest_distance': round(nearest_distance, 0),
        'hhi': hhi_score
    }
```

### 距离衰减函数

```python
from scipy.optimize import curve_fit

def distance_decay(x, a, b):
    """幂函数衰减模型: y = a * x^(-b)"""
    return a * np.power(x, -b)

def fit_decay_function(competition_data):
    """
    拟合距离衰减函数

    competition_data: DataFrame with 'distance' and 'sales_impact' columns
    """
    x_data = competition_data['distance'].values
    y_data = competition_data['sales_impact'].values

    # 幂函数拟合
    popt, pcov = curve_fit(distance_decay, x_data, y_data, p0=[1, 0.5])

    return {'a': popt[0], 'b': popt[1]}
```

### HHI解读标准

| HHI值 | 集中度 | 市场特征 |
|-------|--------|----------|
| < 1500 | 低集中 | 充分竞争，进入机会较多 |
| 1500-2500 | 中集中 | 头部效应显现，需要差异化 |
| > 2500 | 高集中 | 寡头垄断，后进者风险高 |

---

## 模块③ 目标客群匹配度

### STP画像模型

```python
def calculate_customer_match(ideal_profile, actual_profile, weights):
    """
    计算客群匹配指数

    Parameters:
    -----------
    ideal_profile : dict - 理想客群画像
    actual_profile : dict - 实际客群数据
    weights : dict - 各维度权重

    Returns:
    --------
    float: 匹配度分数 (0-100)
    """
    scores = {}

    # 年龄匹配度 (余弦相似度)
    age_similarity = 1 - abs(ideal_profile['avg_age'] - actual_profile['avg_age']) / 30
    scores['age'] = max(0, min(100, age_similarity * 100))

    # 收入匹配度 (收入区间重叠率)
    income_overlap = calculate_income_overlap(
        ideal_profile['income_range'],
        actual_profile['income_distribution']
    )
    scores['income'] = income_overlap * 100

    # 消费偏好匹配
    preference_match = len(set(ideal_profile['preferences']) &
                           set(actual_profile['top_categories'])) / \
                       len(ideal_profile['preferences'])
    scores['preference'] = preference_match * 100

    # 综合得分
    total_score = sum(scores[k] * weights.get(k, 0) for k in scores)
    weight_sum = sum(weights.values())

    return round(total_score / weight_sum, 1)

def calculate_income_overlap(ideal_range, actual_distribution):
    """计算收入区间重叠率"""
    ideal_min, ideal_max = ideal_range
    overlap = max(0, min(ideal_max, actual_distribution['p75']) -
                  max(ideal_min, actual_distribution['p25']))
    ideal_span = ideal_max - ideal_min
    return min(1, overlap / ideal_span) if ideal_span > 0 else 0
```

### 雷达图绘制

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_radar_chart(match_scores, dimensions, output_path):
    """
    绘制客群匹配度雷达图

    Parameters:
    -----------
    match_scores : list - 各维度得分
    dimensions : list - 维度名称（英文）
    output_path : str - 输出路径
    """
    plt.figure(figsize=(8, 8))

    # 设置角度
    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
    angles += angles[:1]  # 闭合

    scores = match_scores + match_scores[:1]  # 闭合

    # 绘制
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, scores, 'o-', linewidth=2, color='#2196F3')
    ax.fill(angles, scores, alpha=0.25, color='#2196F3')

    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, fontsize=11)
    ax.set_ylim(0, 100)

    plt.title('Customer Profile Match Radar', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
```

---

## 模块④ 销量与营收预测

### 简化预测模型

```python
def simple_sales_forecast(footfall, conversion_rate, aov, seasonality=None):
    """
    简化销量预测: Sales = Footfall × Conversion × AOV × Seasonal

    Parameters:
    -----------
    footfall : int - 日均客流量
    conversion_rate : float - 转化率（0-1）
    aov : float - 平均客单价（元）
    seasonality : dict, optional - 季节因子

    Returns:
    --------
    dict: 月度预测数据
    """
    base_sales = footfall * conversion_rate * aov

    if seasonality:
        monthly_sales = {
            month: base_sales * 30 * factor
            for month, factor in seasonality.items()
        }
    else:
        monthly_sales = {month: base_sales * 30 for month in range(1, 13)}

    return monthly_sales
```

### 进阶回归模型

```python
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd

class SalesForecastModel:
    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()

    def build_model(self, historical_data):
        """
        构建多元回归预测模型

        Sales = β₀ + β₁×Footfall + β₂×Price + β₃×Promotion + β₄×Season

        Parameters:
        -----------
        historical_data : pd.DataFrame
            Columns: ['footfall', 'price', 'promotion', 'season', 'sales']
        """
        features = ['footfall', 'price', 'promotion', 'season']
        X = historical_data[features].values
        y = historical_data['sales'].values

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

        # 计算R²
        self.r_squared = self.model.score(X_scaled, y)

        return {
            'coefficients': dict(zip(features, self.model.coef_)),
            'intercept': self.model.intercept_,
            'r_squared': self.r_squared
        }

    def predict(self, forecast_data):
        """预测未来销量"""
        X = forecast_data[['footfall', 'price', 'promotion', 'season']].values
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def get_model_summary(self):
        """返回模型摘要"""
        return {
            'formula': 'log(Sales) = β₀ + β₁×log(Footfall) + β₂×Price + β₃×Promo',
            'r_squared': self.r_squared,
            'interpretation': '每增加1%客流，销量增加β₁%'
        }
```

### 时间序列模型 (ARIMA示例)

```python
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

def arima_forecast(sales_series, periods=12):
    """
    ARIMA时间序列预测

    Parameters:
    -----------
    sales_series : pd.Series - 历史月度销量
    periods : int - 预测月数

    Returns:
    --------
    dict: {'forecast': list, 'confidence_interval': tuple}
    """
    # ARIMA(1,1,1) 模型
    model = ARIMA(sales_series, order=(1, 1, 1))
    fitted = model.fit()

    # 预测
    forecast = fitted.get_forecast(steps=periods)
    mean_forecast = forecast.predicted_mean
    conf_int = forecast.conf_int()

    return {
        'forecast': mean_forecast.tolist(),
        'lower_ci': conf_int.iloc[:, 0].tolist(),
        'upper_ci': conf_int.iloc[:, 1].tolist()
    }
```

---

## 模块⑤ 成本结构与盈亏平衡

### 成本结构分析

```python
import pandas as pd

def calculate_cost_structure(rent_per_sqm, area, staff_count, avg_salary,
                             COGS_rate, marketing_budget):
    """
    计算成本结构

    Returns:
    --------
    pd.DataFrame: 成本明细表
    """
    # 固定成本
    monthly_rent = rent_per_sqm * area
    monthly_salary = staff_count * avg_salary
    fixed_costs = monthly_rent + monthly_salary + marketing_budget

    # 变动成本
    # COGS (Cost of Goods Sold) = 商品成本

    cost_breakdown = pd.DataFrame({
        'Item': ['Rent', 'Staff Salary', 'Marketing', 'COGS'],
        'Monthly Cost (CNY)': [monthly_rent, monthly_salary, marketing_budget, 0],
        'Percentage': [
            monthly_rent / (fixed_costs + 1),
            monthly_salary / (fixed_costs + 1),
            marketing_budget / (fixed_costs + 1),
            COGS_rate
        ]
    })

    return cost_breakdown

def calculate_bep(unit_price, unit_variable_cost, fixed_costs):
    """
    计算盈亏平衡点

    BEP = Fixed_Costs / (Unit_Price - Unit_Variable_Cost)

    Returns:
    --------
    dict: {'units': int, 'revenue': float, 'months_to_breakeven': float}
    """
    contribution_margin = unit_price - unit_variable_cost
    bep_units = fixed_costs / contribution_margin
    bep_revenue = bep_units * unit_price
    monthly_units = 30 * 50  # 假设日均50单
    months_to_breakeven = bep_units / (monthly_units * 30)

    return {
        'BEP_Units': int(bep_units),
        'BEP_Revenue': round(bep_revenue, 2),
        'Months_to_Breakeven': round(months_to_breakeven, 1)
    }

def calculate_payback(initial_investment, monthly_net_income):
    """
    计算投资回收期

    Payback = Initial_Investment / Monthly_Net_Income
    """
    return initial_investment / monthly_net_income
```

### 敏感性分析 (Tornado Plot)

```python
import numpy as np
import matplotlib.pyplot as plt

def sensitivity_analysis(base_npv, variables, ranges):
    """
    敏感性分析：各变量变化对NPV的影响

    Parameters:
    -----------
    base_npv : float - 基准NPV
    variables : list - 变量名称
    ranges : dict - {variable: (low_pct, high_pct)}

    Returns:
    --------
    dict: 各变量的NPV影响范围
    """
    results = {}

    for var in variables:
        low_pct, high_pct = ranges[var]

        # 计算低/高情景下的NPV
        # (简化版，实际需要代入完整模型)
        npv_low = base_npv * (1 + low_pct)
        npv_high = base_npv * (1 + high_pct)

        results[var] = {
            'low': npv_low,
            'high': npv_high,
            'range': npv_high - npv_low,
            'impact': (npv_high - npv_low) / base_npv * 100
        }

    return results

def plot_tornado_chart(sensitivity_results, output_path):
    """
    绘制龙卷风图
    """
    variables = list(sensitivity_results.keys())
    ranges = [sensitivity_results[v]['range'] for v in variables]
    impacts = [sensitivity_results[v]['impact'] for v in variables]

    # 排序
    sorted_idx = np.argsort(ranges)[::-1]
    variables = [variables[i] for i in sorted_idx]
    ranges = [ranges[i] for i in sorted_idx]
    impacts = [impacts[i] for i in sorted_idx]

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['#e74c3c' if i > 0 else '#3498db' for i in ranges]
    y_pos = np.arange(len(variables))

    ax.barh(y_pos, ranges, color=colors, height=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(variables)
    ax.set_xlabel('NPV Impact (CNY)', fontsize=11)
    ax.set_title('Sensitivity Analysis - NPV Tornado Chart', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
```

---

## 模块⑥ 选址评分体系

### 综合评分模型

```python
def calculate_location_score(candidate_data, weights):
    """
    候选点综合评分

    Parameters:
    -----------
    candidate_data : pd.DataFrame
        Columns: ['name', 'footfall', 'rent', 'match_score', 'competition', 'accessibility']
    weights : dict
        {'footfall': 0.30, 'rent': 0.20, 'match': 0.25, 'competition': 0.15, 'accessibility': 0.10}

    Returns:
    --------
    pd.DataFrame: 含综合评分的排名表
    """
    df = candidate_data.copy()

    # 标准化各指标 (0-100分)
    # 人流、匹配度、可达性：越高越好
    for col in ['footfall', 'match_score', 'accessibility']:
        col_min, col_max = df[col].min(), df[col].max()
        df[f'{col}_norm'] = (df[col] - col_min) / (col_max - col_min) * 100

    # 租金、竞争：越低越好 (反向标准化)
    for col in ['rent', 'competition']:
        col_min, col_max = df[col].min(), df[col].max()
        df[f'{col}_norm'] = (col_max - df[col]) / (col_max - col_min) * 100

    # 综合评分
    df['Total_Score'] = (
        df['footfall_norm'] * weights['footfall'] +
        df['rent_norm'] * weights['rent'] +
        df['match_score_norm'] * weights['match'] +
        df['competition_norm'] * weights['competition'] +
        df['accessibility_norm'] * weights['accessibility']
    )

    # 排名
    df['Rank'] = df['Total_Score'].rank(ascending=False).astype(int)

    return df.sort_values('Rank')[['name', 'Total_Score', 'Rank']]
```

### 权重建议

| 指标 | 权重 | 说明 |
|------|------|------|
| 人流 | 30% | 核心驱动因素 |
| 租金 | 20% | 成本控制 |
| 客群匹配 | 25% | 转化潜力 |
| 竞争 | 15% | 市场压力 |
| 可达性 | 10% | 便利程度 |

---

## 数据来源规范

所有数据必须标注：
```
来源: [来源名称]
URL: [链接]
更新时间: [YYYY-MM-DD]
数据置信度: [高/中/低]
数据缺口假设: [如有，列出假设]
```

---

*规格版本: 1.0.0 | 更新日期: 2026-04-25*
