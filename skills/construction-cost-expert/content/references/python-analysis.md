# Python 成本数据分析模板

> 以下为可直接使用的 Python 脚本模板，基于 pandas + matplotlib，适用于施工单位日常成本数据分析场景。

---

## 环境准备

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']  # 中文显示
plt.rcParams['axes.unicode_minus'] = False

# Excel 文件读取
# df = pd.read_excel('成本台账.xlsx', sheet_name='Sheet1')
```

---

## 模板一：月度成本归集与对比

```python
"""
场景：读取项目月度成本数据，进行实际vs目标对比分析
输入：cost_data.xlsx（含列：项目/月份/成本类型/目标金额/实际金额）
"""

import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
df = pd.read_excel('cost_data.xlsx')

# 计算超支情况
df['超支金额'] = df['实际金额'] - df['目标金额']
df['超支率'] = df['超支金额'] / df['目标金额']

# 按月汇总
monthly = df.groupby('月份').agg({
    '目标金额': 'sum',
    '实际金额': 'sum',
    '超支金额': 'sum'
}).reset_index()

# 可视化：月度目标 vs 实际
fig, ax = plt.subplots(figsize=(12, 5))
x = range(len(monthly))
width = 0.35
ax.bar([i - width/2 for i in x], monthly['目标金额'], width, label='目标成本', color='#4C78A8')
ax.bar([i + width/2 for i in x], monthly['实际金额'], width, label='实际成本', color='#F58518')
ax.set_xticks(x)
ax.set_xticklabels(monthly['月份'])
ax.set_ylabel('金额（元）')
ax.set_title('月度成本对比分析')
ax.legend()
plt.tight_layout()
plt.savefig('monthly_cost_comparison.png', dpi=150)
plt.show()
print("图表已保存：monthly_cost_comparison.png")

# 超支预警
warning = df[df['超支率'] > 0.1].sort_values('超支率', ascending=False)
print(f"\n⚠️ 超支预警（超支率>10%）：\n{warning[['项目','成本类型','超支率']]}")
```

---

## 模板二：清单报价不平衡分析

```python
"""
场景：分析清单报价中单价偏高的项目，辅助调价决策
输入：boq.xlsx（含列：清单编号/清单名称/投标单价/市场单价/工程量）
"""

import pandas as pd

df = pd.read_excel('boq.xlsx')

# 计算单价偏差率
df['偏差率'] = (df['投标单价'] - df['市场单价']) / df['市场单价']

# 标记偏高价（可以报高价的变更机会项）
df['报价策略'] = df['偏差率'].apply(
    lambda x: '🔴 偏高（可调高）' if x > 0.1 else
              ('🟡 略高' if 0 < x <= 0.1 else
               ('🟢 正常' if -0.1 <= x <= 0 else '🔵 偏低（避免报低）'))
)

# 按偏差率排序输出
result = df[['清单编号', '清单名称', '投标单价', '市场单价', '偏差率', '报价策略']].sort_values('偏差率', ascending=False)
print("不平衡报价分析结果：")
print(result.to_string(index=False))

# 汇总偏高价项目（变更概率大的项目）
high_price = result[result['偏差率'] > 0.1]
total_potential = (high_price['投标单价'] - high_price['市场单价']) * high_price['工程量']
print(f"\n偏高报价项目潜在收益合计：{total_potential.sum():,.2f} 元")
```

---

## 模板三：多项目对标分析

```python
"""
场景：多个项目同类型工程的单方指标横向对标
输入：projects.xlsx（含列：项目名称/建筑面积/总成本/地上成本/地下室成本）
"""

import pandas as pd
import numpy as np

df = pd.read_excel('projects.xlsx')

# 计算各单方指标
df['建安单方'] = df['总成本'] / df['建筑面积']
df['地上单方'] = df['地上成本'] / df['建筑面积']
df['地下单方'] = df['地下室成本'] / df['地下室面积']

# 计算行业均值
industry_avg = {
    '建安单方': 2200,  # 参考值，根据地区调整
    '地上单方': 1800,
    '地下单方': 3000
}

# 对标分析
for col in ['建安单方', '地上单方', '地下单方']:
    df[f'{col}_偏差率'] = (df[col] - industry_avg[col]) / industry_avg[col]

# 排名
df['建安单方排名'] = df['建安单方'].rank().astype(int)

# 可视化
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 5))
colors = ['#E45756' if x > 0.1 else '#54A24B' if x < -0.1 else '#8796C0' 
          for x in df['建安单方_偏差率']]
bars = ax.barh(df['项目名称'], df['建安单方'], color=colors)
ax.axvline(x=industry_avg['建安单方'], color='red', linestyle='--', label=f'行业均值 {industry_avg["建安单方"]}')
ax.set_xlabel('建安单方（元/㎡）')
ax.set_title('多项目建安单方对标')
ax.legend()
plt.tight_layout()
plt.savefig('project_benchmark.png', dpi=150)
plt.show()

print(df[['项目名称', '建筑面积', '建安单方', '建安单方_偏差率', '建安单方排名']].to_string(index=False))
```

---

## 模板四：结算审减分析

```python
"""
场景：分析结算审核结果，识别审减规律
输入：settlement.xlsx（含列：变更编号/类型/报送金额/审定金额/审减原因）
"""

import pandas as pd

df = pd.read_excel('settlement.xlsx')

# 基本统计
total_submitted = df['报送金额'].sum()
total_approved = df['审定金额'].sum()
total_reduction = total_submitted - total_approved
overall_reduction_rate = total_reduction / total_submitted

print(f"报送总额：{total_submitted:,.2f} 元")
print(f"审定总额：{total_approved:,.2f} 元")
print(f"总审减额：{total_reduction:,.2f} 元")
print(f"总审减率：{overall_reduction_rate:.2%}")

# 按类型统计审减率
type_analysis = df.groupby('类型').agg({
    '报送金额': 'sum',
    '审定金额': 'sum'
}).reset_index()
type_analysis['审减率'] = (type_analysis['报送金额'] - type_analysis['审定金额']) / type_analysis['报送金额']
type_analysis = type_analysis.sort_values('审减率', ascending=False)

print("\n按类型审减分析：")
print(type_analysis.to_string(index=False))

# 审减原因词频分析
print("\n审减高频原因：")
reasons = df['审减原因'].value_counts().head(10)
print(reasons)
```

---

## 模板五：变更台账管理

```python
"""
场景：批量处理变更台账，输出统计摘要
输入：change_orders.xlsx
"""

import pandas as pd

df = pd.read_excel('change_orders.xlsx')

# 基础筛选
pending = df[df['状态'].isin(['待报送', '待审定'])]
approved = df[df['状态'] == '已结算']

# 关键指标
metrics = {
    '变更总数': len(df),
    '已结算数量': len(approved),
    '待处理数量': len(pending),
    '报送总额': df['报送金额'].sum(),
    '审定总额': approved['审定金额'].sum() if len(approved) > 0 else 0,
    '平均审减率': (1 - approved['审定金额'].sum() / approved['报送金额'].sum()) if len(approved) > 0 and approved['报送金额'].sum() > 0 else 0
}

for key, val in metrics.items():
    print(f"{key}：{val:,.2f}" if isinstance(val, float) else f"{key}：{val}")

# 输出待处理清单（按金额排序）
print("\n待处理变更（按金额降序）：")
print(pending[['编号', '类型', '报送金额', '日期']].sort_values('报送金额', ascending=False).head(10).to_string(index=False))
```

---

## 常用数据读取

```python
# 读取 Excel 指定 sheet
df = pd.read_excel('file.xlsx', sheet_name='成本台账')

# 读取 CSV
df = pd.read_csv('file.csv', encoding='utf-8-sig')

# 读取有合并单元格的 Excel（跳过表头行）
df = pd.read_excel('file.xlsx', header=1)

# 导出结果
df.to_excel('output.xlsx', index=False)
df.to_csv('output.csv', index=False, encoding='utf-8-sig')
```

---

> **使用建议**：将以上模板保存为 `.py` 文件，放在 `scripts/` 目录下，每次分析时复制改写。可配合 Jupyter Notebook 使用，提升交互效率。
