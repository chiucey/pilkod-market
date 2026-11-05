# 数据分析与处理详细指南

## 一、核心指标计算

### 1.1 完成量指标

```python
def calculate_completion(df):
    """
    完成量 = 实际完成数 / 目标数 × 100%
    """
    df['completion_rate'] = df['actual_count'] / df['target_count'] * 100
    df['completion_status'] = df['completion_rate'].apply(
        lambda x: '达标' if x >= 100 else '预警' if x >= 80 else '落后'
    )
    return df

# 示例数据结构
# | 产品系 | 平台 | 目标数 | 实际完成 | 完成率 | 状态 |
# |--------|------|--------|---------|--------|------|
# | A7     | 京东 | 1000   | 850     | 85%    | 预警 |
```

### 1.2 控比指标

```python
def calculate_cost_control(df):
    """
    控比 = 实际花费 / 预算 × 100%
    - 控比 < 100%：预算未用完
    - 控比 = 100%：刚好用完
    - 控比 > 100%：超预算
    """
    df['cost_control_ratio'] = df['actual_spend'] / df['budget'] * 100

    df['control_status'] = df['cost_control_ratio'].apply(
        lambda x: '超支' if x > 105 else
                  '预警' if x > 100 else
                  '正常'
    )
    return df
```

### 1.3 同比增长（YoY）

```python
def calculate_yoy_growth(df):
    """
    同比增长 = (本期值 - 上期值) / |上期值| × 100%
    """
    df = df.sort_values(['product_line', 'platform', 'date'])

    df['yoy_growth'] = df.groupby(['product_line', 'platform'])['value'].pct_change(periods=7) * 100

    return df

# 环比增长（CAGR）
def calculate_mom_growth(df):
    """
    环比增长 = (本期 - 上期) / 上期 × 100%
    """
    df = df.sort_values(['product_line', 'platform', 'date'])
    df['mom_growth'] = df.groupby(['product_line', 'platform'])['value'].pct_change() * 100
    return df
```

---

## 二、Excel/Google Sheets 高级函数

### 2.1 完成量公式

```excel
=SUMIF(B:B,"京东",D:D)/SUMIF(B:B,"京东",C:C)*100
```

### 2.2 控比公式

```excel
=D2/C2  // 实际花费 / 预算
```

### 2.3 同比增长公式

```excel
=(B2-B3)/ABS(B3)*100  // (本期-上期)/|上期|
```

### 2.4 条件格式

- 完成率 >= 100%：绿色
- 完成率 80-99%：黄色
- 完成率 < 80%：红色

---

## 三、SQL 数据提取

### 3.1 基础销售数据查询

```sql
-- 各平台每日销售汇总
SELECT
    DATE(sale_date) as date,
    product_line,
    platform,
    SUM(sales_amount) as total_sales,
    SUM(quantity) as total_quantity,
    COUNT(DISTINCT order_id) as order_count
FROM sales_fact
WHERE sale_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
GROUP BY DATE(sale_date), product_line, platform
ORDER BY date DESC, product_line, platform;
```

### 3.2 人群资产查询

```sql
-- 人群资产变化趋势
SELECT
    stat_date,
    product_line,
    platform,
    audience_size,
    interaction_count,
    conversion_count,
    ROUND(conversion_count * 100.0 / audience_size, 2) as conversion_rate
FROM audience_fact
WHERE stat_date >= DATE_SUB(CURRENT_DATE, INTERVAL 7 DAY)
ORDER BY stat_date, product_line, platform;
```

### 3.3 预算执行查询

```sql
-- 预算执行情况
SELECT
    product_line,
    platform,
    SUM(budget) as total_budget,
    SUM(actual_spend) as total_spend,
    ROUND(SUM(actual_spend) * 100.0 / SUM(budget), 2) as spend_ratio,
    CASE
        WHEN SUM(actual_spend) > SUM(budget) * 1.05 THEN '超支'
        WHEN SUM(actual_spend) > SUM(budget) THEN '预警'
        ELSE '正常'
    END as status
FROM budget_fact
WHERE period = '2024-Q1'
GROUP BY product_line, platform;
```

---

## 四、Python Pandas 数据处理

### 4.1 读取多平台数据

```python
import pandas as pd
from pathlib import Path

def load_multi_platform_data(data_dir: str, date: str):
    """加载多平台数据"""
    platforms = ['jd', 'tmall', 'douyin', 'xiaohongshu', 'bilibili']

    dfs = {}
    for platform in platforms:
        file_path = Path(data_dir) / f"{platform}_{date}.csv"
        if file_path.exists():
            dfs[platform] = pd.read_csv(file_path)
        else:
            print(f"Warning: {file_path} not found")

    return dfs
```

### 4.2 合并计算指标

```python
def merge_and_calculate(dfs: dict):
    """合并多平台数据并计算指标"""
    all_data = []

    for platform, df in dfs.items():
        df['platform'] = platform
        all_data.append(df)

    combined_df = pd.concat(all_data, ignore_index=True)

    # 计算核心指标
    combined_df['completion_rate'] = (
        combined_df['actual'] / combined_df['target'] * 100
    ).round(2)

    combined_df['cost_ratio'] = (
        combined_df['actual_spend'] / combined_df['budget'] * 100
    ).round(2)

    return combined_df
```

### 4.3 生成汇总报表

```python
def generate_summary(combined_df: pd.DataFrame):
    """按产品系生成汇总报表"""
    summary = combined_df.groupby(['product_line', 'platform']).agg({
        'actual': 'sum',
        'target': 'sum',
        'actual_spend': 'sum',
        'budget': 'sum'
    }).reset_index()

    summary['completion_rate'] = (
        summary['actual'] / summary['target'] * 100
    ).round(2)

    summary['cost_ratio'] = (
        summary['actual_spend'] / summary['budget'] * 100
    ).round(2)

    return summary
```

---

## 五、数据质量检查

```python
def validate_data(df: pd.DataFrame) -> list:
    """数据质量检查"""
    issues = []

    # 检查空值
    null_counts = df.isnull().sum()
    if null_counts.any():
        issues.append(f"存在空值: {null_counts[null_counts > 0].to_dict()}")

    # 检查负数
    numeric_cols = ['actual', 'target', 'actual_spend', 'budget']
    for col in numeric_cols:
        if col in df.columns and (df[col] < 0).any():
            issues.append(f"{col} 存在负值")

    # 检查完成率异常
    if 'completion_rate' in df.columns:
        abnormal = df[(df['completion_rate'] < 0) | (df['completion_rate'] > 200)]
        if not abnormal.empty:
            issues.append(f"完成率异常(0-200%之外): {len(abnormal)} 条")

    return issues
```
