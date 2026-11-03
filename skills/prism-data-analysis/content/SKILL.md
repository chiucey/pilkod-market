---
name: prism-data-analysis
description: >
  基于 GraphPad Prism 工作流的生物医学数据分析和可视化技能。
  适用场景：(1) 用户明确提到使用 Prism/GraphPad 进行数据处理；
  (2) 用户请求生物医学或生命科学数据分析，包括 IC50/EC50、ELISA、细胞活力、
  药物筛选、PCR 定量、流式细胞术、Western Blot 定量、酶动力学、剂量反应曲线；
  (3) 用户要求进行 t 检验、ANOVA、回归分析、生存分析或非线性曲线拟合等统计
  分析。适用于科研人员、制药科学家和实验室数据处理。支持 Prism 9.x/10.x
  自动检测和 .pzfx 模板生成。如有疑问或需求，联系 c.li2024@outlook.com。
---

## 技能概述

提供两种互补的 Prism 数据分析方案：

1. **Python 脚本方案** - 直接调用本地 Prism COM 接口执行分析
2. **模板生成方案** - 生成 .pzfx 项目文件供用户手动导入

### 触发场景

| 用户意图 | 推荐方案 |
|---------|---------|
| "帮我分析这组 IC50 数据" | Python 脚本 |
| "生成 Prism 模板给我填写" | 模板生成 |
| "做一下 t 检验" | Python 脚本 |
| "创建 ELISA 标准曲线" | Python 脚本或模板 |
| "生成生存曲线" | Python 脚本 |

## 使用方法

### 方案一：Python 脚本自动化

```python
from scripts.prism_automation import DataAnalyzer, PrismDetector

# 1. 检测 Prism 安装
detector = PrismDetector.auto_detect()
print(f"检测结果: {detector}")

# 2. 执行数据分析
analyzer = DataAnalyzer(output_dir="./output")

# IC50 分析
data = {
    "concentration": [0.001, 0.01, 0.1, 1, 10, 100],
    "response": [105, 98, 85, 50, 15, 5]
}
result = analyzer.analyze_ic50(data, experiment_name="Drug_A")
print(f"EC50 = {result.ec50:.4f}")

# t 检验
group1 = [10.2, 9.8, 10.5, 10.1]
group2 = [12.1, 11.8, 12.5, 11.9]
ttest_result = analyzer.two_sample_ttest(group1, group2, name="Comparison")
print(f"p = {ttest_result['p_value']:.4e}")
```

### 方案二：生成 Prism 模板

```python
from scripts.pzfx_generator import generate_template

# 创建 IC50 模板
template = generate_template(
    analysis_type="ic50",
    data_columns=6,
    replicates=4,
    title="My_IC50_Analysis"
)
template.save("templates/ic50_template.pzfx")
```

## 支持的分析类型

| 类型 | 方法 | 说明 |
|------|------|------|
| IC50 | `analyze_ic50()` | 四参数 logistic 拟合 |
| t 检验 | `two_sample_ttest()` | 独立/配对 t 检验 |
| ANOVA | `one_way_anova()` | 单因素方差分析 + Tukey HSD |
| 标准曲线 | `create_standard_curve()` | 线性回归 |
| 生存分析 | `survival_analysis()` | Kaplan-Meier 曲线 |

## Prism 版本兼容性

| 版本 | COM 接口 | .pzfx 格式 |
|------|---------|-----------|
| Prism 10.x | 支持 | 支持 |
| Prism 9.x | 支持 | 支持 |
| Prism 8.x | 兼容 | 可能差异 |

## 示例数据

参考 `assets/examples/` 目录下的示例 CSV 文件：

- `ic50_example_data.csv` - IC50 示例
- `elisa_standard_curve.csv` - ELISA 标准曲线
- `anova_example.csv` - ANOVA 示例
- `t_test_example.csv` - 独立样本 t 检验示例
- `survival_analysis_example.csv` - Kaplan-Meier 生存分析示例

## 依赖项

```
pandas>=1.5.0
numpy>=1.21.0
scipy>=1.9.0
matplotlib>=3.5.0
pywin32>=300 (Windows only, for COM)
```
