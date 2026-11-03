# 数据分析方法参考

## 1. 预测分析方法

### 1.1 时间序列预测

**适用场景**：具有时间顺序的历史数据，如月度销售额、日活用户数等

**常用方法**：
- **简单移动平均**：适合趋势平稳的数据
  - 计算公式：`F(t+1) = (1/n) * Σ(D(t-i))`, i=0 to n-1
- **指数平滑法**：权重递减，适合短期预测
  - 一次指数平滑：适合无趋势数据
  - 二次指数平滑：适合线性趋势
  - 三次指数平滑：适合季节性数据
- **ARIMA**：自回归差分移动平均模型
  - 参数：(p, d, q) - 自回归阶数、差分阶数、移动平均阶数

**Python实现示例**：
```python
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def predict_with_holt_winters(data, periods=12, trend='add', seasonal='add', seasonal_periods=12):
    """Holt-Winters指数平滑预测"""
    model = ExponentialSmoothing(
        data,
        trend=trend,
        seasonal=seasonal,
        seasonal_periods=seasonal_periods
    )
    fitted = model.fit()
    forecast = fitted.forecast(periods)
    return forecast
```

### 1.2 回归预测

**适用场景**：有明确自变量和因变量关系的数据

**方法选择**：
- 线性回归：变量关系近似线性
- 多项式回归：非线性关系
- 梯度提升树：复杂非线性关系（如XGBoost、LightGBM）

## 2. 归因分析方法

### 2.1 多因素归因模型

**适用场景**：分析多个因素对结果的影响程度

**方法**：
- **线性回归系数**：标准化后比较
  ```python
  from sklearn.preprocessing import StandardScaler
  from sklearn.linear_model import LinearRegression

  def attribution_analysis(X, y):
      scaler = StandardScaler()
      X_scaled = scaler.fit_transform(X)
      model = LinearRegression()
      model.fit(X_scaled, y)
      # 标准化系数即为归因贡献度
      return pd.Series(model.coef_, index=X.columns).sort_values(ascending=False)
  ```
- **Shapley值**：博弈论方法，公平分配贡献
- **增量贡献分析**：每次添加一个变量观察增量

### 2.2 A/B测试归因

**适用场景**：对比实验组和对照组的差异

**分析方法**：
- t检验：比较两组均值差异
- 卡方检验：比较两组比例差异
- 置信区间：计算差异的置信区间

## 3. 总结归纳方法

### 3.1 描述性统计

```python
def summarize_data(data):
    summary = {
        'count': data.count(),
        'mean': data.mean(),
        'std': data.std(),
        'min': data.min(),
        '25%': data.quantile(0.25),
        '50%': data.median(),
        '75%': data.quantile(0.75),
        'max': data.max()
    }
    return pd.DataFrame(summary)
```

### 3.2 分组聚合分析

```python
def group_summary(df, group_col, agg_col, agg_funcs=['mean', 'sum', 'count']):
    return df.groupby(group_col)[agg_col].agg(agg_funcs).round(2)
```

### 3.3 帕累托分析

识别主要因素（80/20法则）

```python
def pareto_analysis(data, value_col):
    sorted_data = data.sort_values(value_col, ascending=False)
    sorted_data['cumulative_pct'] = (sorted_data[value_col].cumsum() /
                                       sorted_data[value_col].sum() * 100)
    return sorted_data
```

## 4. 对比分析方法

### 4.1 时间维度对比

- **同比**：与去年同期对比
- **环比**：与上一周期对比

```python
def temporal_comparison(df, date_col, value_col, period='M'):
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)

    monthly = df[value_col].resample(period).sum()

    result = pd.DataFrame({
        'current': monthly,
        'previous': monthly.shift(1),
        'yoy': monthly.pct_change(12) if period == 'M' else monthly.pct_change(4) if period == 'W' else monthly.pct_change(),
        'mom': monthly.pct_change()
    })
    return result
```

### 4.2 组间对比

- 独立样本t检验
- Mann-Whitney U检验（非参数）
- ANOVA方差分析（多组比较）

```python
from scipy import stats

def compare_groups(group1, group2):
    t_stat, p_value = stats.ttest_ind(group1, group2)
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'mean_diff': group1.mean() - group2.mean()
    }
```

## 5. 波动分析方法

### 5.1 波动指标

```python
def fluctuation_metrics(data):
    return {
        'variance': data.var(),
        'std_dev': data.std(),
        'cv': data.std() / data.mean() * 100,  # 变异系数
        'range': data.max() - data.min(),
        'iqr': data.quantile(0.75) - data.quantile(0.25)
    }
```

### 5.2 异常值检测

- **Z-score方法**：|z| > 3 为异常
- **IQR方法**：< Q1-1.5*IQR 或 > Q3+1.5*IQR 为异常

```python
def detect_outliers_iqr(data):
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    return data[(data < lower) | (data > upper)], lower, upper
```

### 5.3 移动标准差

识别趋势变化点

```python
def rolling_volatility(data, window=7):
    return data.rolling(window=window).std()
```

## 分析类型判断示例

### 示例1：预测分析识别
**输入**："预测下个月的销售趋势"
- 关键词匹配：预测、未来趋势
- 识别为：预测分析
- 建议方法：时间序列预测

### 示例2：归因分析识别
**输入**："分析用户流失的主要原因"
- 关键词匹配：原因、归因、分析
- 识别为：归因分析
- 建议方法：多因素回归/Shapley值

### 示例3：对比分析识别
**输入**："对比华东区和华南区的销售表现"
- 关键词匹配：对比、比较
- 识别为：对比分析
- 建议方法：组间统计检验

### 示例4：波动分析识别
**输入**："检测本周股价的异常波动"
- 关键词匹配：波动、异常
- 识别为：波动分析
- 建议方法：异常值检测

### 示例5：多类型组合
**输入**："分析上季度销售下降的原因，并预测下季度走势"
- 关键词：下降的原因 → 归因分析
- 关键词：预测走势 → 预测分析
- 识别为：归因分析 + 预测分析组合
