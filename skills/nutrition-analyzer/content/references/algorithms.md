# 算法参考

## 1. RDA达成率计算

```python
def calculate_rda_achievement(actual_intake, rda_value, ul_value=None):
    """
    计算RDA达成率和状态

    参数：
    - actual_intake: 实际摄入量
    - rda_value: 推荐膳食供给量
    - ul_value: 可耐受最高摄入量（可选）

    返回：
    - achievement_rate: 达成率百分比
    - status: 状态标签
    """
    achievement_rate = (actual_intake / rda_value) * 100

    if ul_value and actual_intake > ul_value:
        status = "exceeds_ul"
        category = "过量（危险）"
    elif achievement_rate < 50:
        status = "severe_deficiency"
        category = "严重缺乏"
    elif achievement_rate < 75:
        status = "insufficient"
        category = "不足"
    elif achievement_rate < 100:
        status = "approaching_target"
        category = "接近目标"
    elif achievement_rate <= 150:
        status = "adequate"
        category = "充足"
    else:
        status = "high_intake"
        category = "较高"

    return {
        'achievement_rate': round(achievement_rate, 1),
        'status': status,
        'category': category
    }
```

## 2. 营养密度评分

```python
def calculate_nutrient_density_score(meal_data):
    """
    计算食物营养密度评分（0-10分）

    因素权重：
    - 维生素达成率：40%
    - 矿物质达成率：30%
    - 膳食纤维：20%
    - 限制性营养素（饱和脂肪、钠、添加糖）：10%
    """
    score = 0

    # 维生素评分
    vitamin_achievements = [
        meal_data['micronutrients'][v] / RDA[v]
        for v in ['vitamin_a', 'vitamin_c', 'vitamin_d', 'vitamin_e', 'vitamin_k']
    ]
    vitamin_score = min(sum(vitamin_achievements) / len(vitamin_achievements), 1.5) * 10
    score += min(vitamin_score, 10) * 0.40

    # 矿物质评分
    mineral_achievements = [
        meal_data['micronutrients'][m] / RDA[m]
        for m in ['calcium', 'iron', 'magnesium', 'zinc']
    ]
    mineral_score = min(sum(mineral_achievements) / len(mineral_achievements), 1.5) * 10
    score += min(mineral_score, 10) * 0.30

    # 膳食纤维评分
    fiber_score = min(meal_data['macronutrients']['fiber_g'] / 5, 2) * 10
    score += min(fiber_score, 10) * 0.20

    # 限制性营养素扣分
    penalty = 0
    if meal_data['macronutrients']['saturated_fat_g'] > 10:
        penalty += 2
    if meal_data['micronutrients']['sodium_mg'] > 600:
        penalty += 2
    if meal_data.get('added_sugars_g', 0) > 10:
        penalty += 2

    score = max(0, score - penalty * 0.10)

    return round(score, 1)
```

## 3. 健康饮食指数评分 (HEI-2015改编)

```python
def calculate_healthy_eating_index(daily_data):
    """
    计算健康饮食指数（HEI-2015改编）

    评分范围：0-100分
    """
    score = 0

    # 充足性成分（满分50分）
    # 1. 水果（5分）
    fruit_servings = daily_data['fruit_servings']
    score += min(fruit_servings, 2.5) * 2

    # 2. 蔬菜（5分）
    veg_servings = daily_data['vegetable_servings']
    score += min(veg_servings, 3) * 1.67

    # 3. 全谷物（10分）
    whole_grains_oz = daily_data['whole_grains_oz']
    score += min(whole_grains_oz, 3) * 3.33

    # 4. 乳制品（10分）
    dairy_servings = daily_data['dairy_servings']
    score += min(dairy_servings, 3) * 3.33

    # 5. 蛋白质（5分）
    protein_oz = daily_data['protein_oz']
    score += min(protein_oz, 5) * 1

    # 6. 海鲜/植物蛋白（5分）
    plant_protein_oz = daily_data['plant_protein_oz']
    score += min(plant_protein_oz, 2) * 2.5

    # 7. 脂肪酸比例（10分）
    fat_ratio = daily_data['unsaturated_fat_g'] / max(daily_data['saturated_fat_g'], 1)
    score += min(fat_ratio, 2.5) * 4

    # 适度性成分（满分40分，反向计分）
    # 8. 精制谷物（10分）
    refined_grains_oz = daily_data['refined_grains_oz']
    score += max(10 - refined_grains_oz * 2, 0)

    # 9. 钠（10分）
    sodium_g = daily_data['sodium_mg'] / 1000
    score += max(10 - sodium_g * 2, 0)

    # 10. 添加糖（10分）
    added_sugars_pct = daily_data['added_sugars_g'] / (daily_data['total_calories'] / 100)
    score += max(10 - added_sugars_pct * 10, 0)

    # 11. 饱和脂肪（10分）
    saturated_fat_pct = daily_data['saturated_fat_g'] / (daily_data['total_calories'] / 100)
    score += max(10 - saturated_fat_pct * 10, 0)

    return round(score, 1)
```

## 4. 趋势分析

```python
import numpy as np
from scipy import stats

def analyze_trend(data_series, time_points=None):
    """
    分析营养素趋势

    返回：
    - direction: 趋势方向 (increasing/decreasing/stable)
    - slope: 回归斜率
    - significance: p值（统计显著性）
    - change_pct: 变化百分比
    """
    if len(data_series) < 2:
        return {'direction': 'stable', 'slope': 0, 'significance': 1, 'change_pct': 0}

    y = np.array(data_series)
    x = np.arange(len(y))

    # 线性回归
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # 趋势方向判断
    if p_value > 0.05:
        direction = 'stable'
    elif slope > 0.01 * np.mean(y):
        direction = 'increasing'
    elif slope < -0.01 * np.mean(y):
        direction = 'decreasing'
    else:
        direction = 'stable'

    # 变化百分比
    if y[0] != 0:
        change_pct = ((y[-1] - y[0]) / y[0]) * 100
    else:
        change_pct = 0

    return {
        'direction': direction,
        'slope': round(slope, 4),
        'significance': round(p_value, 4),
        'change_pct': round(change_pct, 1),
        'r_squared': round(r_value**2, 4)
    }
```

## 5. 相关性分析

```python
from scipy.stats import pearsonr

def analyze_correlation(x_data, y_data, lag=0):
    """
    分析两个变量间的相关性

    参数：
    - x_data: 自变量列表
    - y_data: 因变量列表
    - lag: 时间滞后（天）

    返回：
    - correlation: Pearson相关系数
    - p_value: 显著性水平
    - strength: 相关强度描述
    """
    if lag > 0:
        x_data = x_data[:-lag]
        y_data = y_data[lag:]

    correlation, p_value = pearsonr(x_data, y_data)

    # 相关强度分类
    abs_corr = abs(correlation)
    if abs_corr < 0.3:
        strength = '弱'
    elif abs_corr < 0.7:
        strength = '中'
    else:
        strength = '强'

    return {
        'correlation': round(correlation, 3),
        'p_value': round(p_value, 4),
        'strength': strength,
        'significant': p_value < 0.05,
        'direction': '正相关' if correlation > 0 else '负相关'
    }
```
