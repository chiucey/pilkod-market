# Excel深度分析 - 参考方法文档

## 1. 统计分析方法

### 1.1 描述性统计

```python
# 数值型字段统计
numerical_stats = {
    'count': 计数,
    'mean': 均值,
    'std': 标准差,
    'min': 最小值,
    '25%': Q1,
    '50%': 中位数,
    '75%': Q3,
    'max': 最大值,
    'skewness': 偏度,
    'kurtosis': 峰度,
    'missing_rate': 缺失率
}

# 分类型字段统计
categorical_stats = {
    'unique_count': 唯一值数量,
    'mode': 众数,
    'mode_frequency': 众数频率,
    'missing_count': 缺失数量,
    'missing_rate': 缺失率,
    'top_values': 频率最高的5个值
}
```

### 1.2 相关性分析

```python
# Pearson相关系数 - 适用于线性关系
pearson_corr = df.corr(method='pearson')

# Spearman秩相关 - 适用于非线性单调关系
spearman_corr = df.corr(method='spearman')

# 相关系数解释
correlation_interpretation = {
    '|r| >= 0.8': '强相关',
    '0.5 <= |r| < 0.8': '中等相关',
    '0.3 <= |r| < 0.5': '弱相关',
    '|r| < 0.3': '几乎无相关'
}
```

### 1.3 正态性检验

```python
# Shapiro-Wilk检验（样本量<5000）
from scipy import stats
stat, p_value = stats.shapiro(data)

# K-S检验
stat, p_value = stats.kstest(data, 'norm')

# 判断标准
is_normal = p_value > 0.05
```

## 2. 异常检测方法

### 2.1 Z-Score方法

```python
def z_score_anomaly(data, threshold=3):
    """检测偏离均值超过threshold个标准差的值"""
    z_scores = np.abs((data - data.mean()) / data.std())
    return z_scores > threshold

# 优点：简单直观
# 缺点：对异常值敏感（异常值会影响均值和标准差）
# 适用：近似正态分布的数据
```

### 2.2 IQR方法

```python
def iqr_anomaly(data, k=1.5):
    """检测超出k倍四分位距的值"""
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - k * IQR
    upper_bound = Q3 + k * IQR
    return (data < lower_bound) | (data > upper_bound)

# k=1.5：标准异常检测
# k=3：极端异常检测
# 优点：鲁棒性强，不受极端值影响
# 适用：任意分布的数据
```

### 2.3 孤立森林

```python
from sklearn.ensemble import IsolationForest

def isolation_forest_anomaly(df, contamination=0.1):
    """基于树的异常检测算法"""
    model = IsolationForest(contamination=contamination, random_state=42)
    predictions = model.fit_predict(df)
    scores = model.decision_function(df)
    return predictions == -1, scores

# 优点：高维数据效果好，计算效率高
# 缺点：需要调优contamination参数
# 适用：多维度联合异常检测
```

### 2.4 基于业务规则的异常检测

```python
# 示例业务规则
business_rules = [
    {
        'name': '负值检测',
        'condition': lambda x: x < 0,
        'applicable_to': ['金额', '数量', '价格'],
        'severity': 'high'
    },
    {
        'name': '日期逻辑错误',
        'condition': lambda row: row['结束日期'] < row['开始日期'],
        'applicable_to': ['日期字段组合'],
        'severity': 'high'
    },
    {
        'name': '超出合理范围',
        'condition': lambda x: x > 1000000,
        'applicable_to': ['单价'],
        'severity': 'medium'
    }
]
```

## 3. 根因分析方法

### 3.1 帕累托分析

```python
def pareto_analysis(issues_df, value_col='count', label_col='issue'):
    """识别最重要的少数问题"""
    df = issues_df.sort_values(value_col, ascending=False)
    df['cumulative_pct'] = (df[value_col].cumsum() / df[value_col].sum() * 100).round(2)

    # 识别80/20分界点
    pareto_issues = df[df['cumulative_pct'] <= 80]
    return pareto_issues

# 应用场景：
# - 问题优先级排序
# - 资源优化配置
# - 识别关键少数问题
```

### 3.2 对比分析

```python
def comparative_analysis(df, group_col, metric_col, value_col):
    """对比不同组别的指标差异"""
    grouped = df.groupby(group_col)[value_col].agg(['mean', 'std', 'count'])
    overall = df[value_col].mean()

    # 计算各组与整体的偏差
    grouped['deviation_from_overall'] = ((grouped['mean'] - overall) / overall * 100).round(2)

    return grouped.sort_values('mean', ascending=False)

# 分析维度示例：
# - 时间维度：同比、环比
# - 空间维度：地区、部门
# - 属性维度：产品类别、客户类型
```

### 3.3 关联规则挖掘

```python
from mlxtend.frequent_patterns import apriori, association_rules

def association_analysis(df, itemsets_col, min_support=0.1):
    """发现数据中的关联模式"""
    # 将数据转换为交易格式
    onehot = pd.get_dummies(df[itemsets_col])

    # 频繁项集挖掘
    frequent_itemsets = apriori(onehot, min_support=min_support, use_colnames=True)

    # 生成关联规则
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

    return rules.sort_values('lift', ascending=False)

# 应用场景：
# - 客户行为关联分析
# - 业务问题关联分析
# - 影响因素组合分析
```

### 3.4 归因分析

```python
def attribution_analysis(df, outcome_col, factor_cols):
    """分解各因素对结果的影响程度"""
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler

    # 标准化处理
    scaler = StandardScaler()
    X = scaler.fit_transform(df[factor_cols])
    y = df[outcome_col]

    # 回归分析
    model = LinearRegression()
    model.fit(X, y)

    # 计算相对重要性（标准化系数绝对值）
    importance = pd.DataFrame({
        'factor': factor_cols,
        'coefficient': model.coef_,
        'abs_importance': np.abs(model.coef_)
    }).sort_values('abs_importance', ascending=False)

    return importance
```

## 4. 数据质量评估框架

### 4.1 质量维度与评分

```python
quality_dimensions = {
    'completeness': {
        'weight': 0.25,
        'metrics': ['缺失率', '空值率'],
        'score_method': 'inverse_missing_rate'
    },
    'consistency': {
        'weight': 0.25,
        'metrics': ['格式一致率', '跨字段校验通过率'],
        'score_method': 'consistency_ratio'
    },
    'accuracy': {
        'weight': 0.20,
        'metrics': ['业务规则通过率', '异常值比例'],
        'score_method': 'accuracy_ratio'
    },
    'timeliness': {
        'weight': 0.15,
        'metrics': ['数据时效性', '更新时间间隔'],
        'score_method': 'time_decay'
    },
    'uniqueness': {
        'weight': 0.15,
        'metrics': ['重复率', '主键唯一性'],
        'score_method': 'inverse_duplicate_rate'
    }
}

def calculate_quality_score(df, dimensions):
    """计算综合数据质量分数"""
    scores = {}
    for dim, config in dimensions.items():
        dim_score = calculate_dimension_score(df, config)
        scores[dim] = dim_score

    total_score = sum(scores[dim] * dimensions[dim]['weight']
                      for dim in dimensions)

    return round(total_score, 2)
```

### 4.2 问题严重程度分级

```python
severity_levels = {
    'critical': {
        'range': '直接影响业务',
        'color': 'red',
        'action': '立即处理',
        'examples': ['数据完全缺失', '主键重复', '负值金额']
    },
    'high': {
        'range': '影响较大',
        'color': 'orange',
        'action': '尽快处理',
        'examples': ['关键字段缺失>10%', '格式严重不一致']
    },
    'medium': {
        'range': '有一定影响',
        'color': 'yellow',
        'action': '计划处理',
        'examples': ['非关键字段缺失', '少量异常值']
    },
    'low': {
        'range': '影响较小',
        'color': 'blue',
        'action': '可选处理',
        'examples': ['格式轻微不一致', '数据精度问题']
    }
}
```

## 5. 分析报告模板

### 5.1 问题清单模板

```markdown
| 问题编号 | 问题类型 | 涉及字段 | 问题描述 | 记录数 | 占比 | 严重程度 | 建议措施 |
|---------|---------|---------|---------|--------|------|---------|---------|
| P001 | 缺失值 | 客户名称 | 客户名称字段为空 | 125 | 2.5% | High | 补充或标记为"未知客户" |
| P002 | 异常值 | 订单金额 | 金额为负数 | 3 | 0.06% | Critical | 检查数据录入错误 |
| ... | ... | ... | ... | ... | ... | ... | ... |
```

### 5.2 根因分析模板

```markdown
## 根因分析报告

### 问题：订单金额异常偏高

**问题表现**：
- 5%的订单金额超过平均值的5倍
- 最大单笔订单金额为平均值的20倍

**可能原因**：
1. 录入错误（单位错误，如万元当元）
2. 批量订单未拆分
3. 数据合并错误

**证据支持**：
- 异常订单的时间分布：无明显规律
- 异常订单的客户分布：集中在3个客户
- 异常订单的产品分布：均为定制类产品

**根本原因**（高置信度）：
> 定制类产品的订单金额录入使用了含税价格，但系统配置为不含税，导致金额偏高约13%

**修复建议**：
1. 短期：回溯修正历史数据
2. 中期：统一价格录入标准
3. 长期：配置价格自动含税计算
```

## 6. 可视化建议

| 分析目的 | 推荐图表 | 适用场景 |
|---------|---------|---------|
| 数据分布 | 直方图、箱线图 | 查看数值分布、识别异常 |
| 时间趋势 | 折线图 | 趋势分析、季节性检测 |
| 相关性 | 热力图 | 多变量相关性展示 |
| 构成分析 | 饼图、堆叠柱状图 | 占比分析 |
| 对比分析 | 柱状图 | 不同类别数值对比 |
| 异常标注 | 散点图+标注 | 异常点可视化 |
| 问题分布 | 树状图 | 问题分类占比展示 |

## 7. 执行示例

### 7.1 完整分析流程

```python
import pandas as pd
import numpy as np
from analyzer import DataAnalyzer

# 初始化分析器
analyzer = DataAnalyzer(file_path='sales_data.xlsx')

# 执行完整分析
report = analyzer.full_analysis()

# 输出报告
print(report)

# 保存详细结果
analyzer.save_results(output_dir='./analysis_output')
```

### 7.2 自定义分析

```python
# 只做异常检测
anomalies = analyzer.detect_anomalies(
    columns=['金额', '数量'],
    method=['iqr', 'zscore'],
    sensitivity='high'
)

# 只做根因分析
root_cause = analyzer.root_cause_analysis(
    target='流失率',
    potential_factors=['活跃度', '购买频次', '客单价', '产品种类'],
    method='regression'
)

# 分组对比分析
comparison = analyzer.compare_groups(
    group_by='地区',
    metrics=['销售额', '利润率', '客户数']
)
```
