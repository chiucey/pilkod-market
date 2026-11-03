# API Reference

## prism_automation 模块

### PrismDetector

Prism 安装检测器。

#### Methods

##### `detect_all_installations() -> List[PrismVersion]`
检测系统上所有 Prism 安装。

##### `auto_detect() -> Optional[PrismVersion]`
自动检测第一个可用的 Prism 安装。

### PrismVersion

Prism 版本信息数据类。

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_prism_10` | bool | 是否为 Prism 10.x |
| `is_prism_9` | bool | 是否为 Prism 9.x |

### DataAnalyzer

数据分析核心类。

#### Methods

##### `analyze_ic50(data, experiment_name) -> IC50Result`
IC50 分析（4 参数 logistic 拟合）。

**参数：**
- `data`: dict，含 `concentration` 和 `response` 列表
- `experiment_name`: 实验名称

**返回：**
`IC50Result` 对象，含 EC50、Hill Slope、R² 等

##### `two_sample_ttest(group1, group2, paired=False, name="t_test") -> Dict`
t 检验分析。

**参数：**
- `group1`: 第一组数据列表
- `group2`: 第二组数据列表
- `paired`: 是否为配对 t 检验
- `name`: 分析名称

**返回：**
dict，含 t 统计量、p 值、Cohen's d 等

##### `one_way_anova(groups, name="one_way_anova") -> Dict`
单因素方差分析。

**参数：**
- `groups`: dict，键为组名，值为数据列表
- `name`: 分析名称

**返回：**
dict，含 ANOVA 表和 Tukey HSD 结果

##### `create_standard_curve(data, title="Standard Curve") -> StandardCurveResult`
标准曲线分析（线性回归）。

**参数：**
- `data`: dict，含 `concentration` 和 `response` 列表
- `title`: 曲线标题

**返回：**
`StandardCurveResult` 对象

##### `survival_analysis(time, event, group=None, name="survival") -> Dict`
Kaplan-Meier 生存分析。

**参数：**
- `time`: 生存时间列表
- `event`: 事件指示器（1=事件，0=删失）
- `group`: 可选的分组标签
- `name`: 分析名称

**返回：**
dict，含生存概率和 log-rank 检验结果

### IC50Result

IC50 分析结果容器。

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `ec50` | float | EC50 值 |
| `hill_slope` | float | Hill 斜率 |
| `bottom` | float | 底部渐近线 |
| `top` | float | 顶部渐近线 |
| `r_squared` | float | R² 值 |
| `plot_path` | str | 图表路径 |

#### Methods

##### `save(filepath)`
保存结果到文本文件。

### StandardCurveResult

标准曲线结果容器。

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `slope` | float | 斜率 |
| `intercept` | float | 截距 |
| `r_squared` | float | R² 值 |
| `equation` | str | 方程字符串 |
| `plot_path` | str | 图表路径 |

#### Methods

##### `export_equation(filepath)`
导出方程到文本文件。

---

## pzfx_generator 模块

### generate_template(analysis_type, data_columns=6, replicates=4, groups=2, title="Prism Template") -> PrismTemplate

生成 Prism 项目模板。

**analysis_type 选项：**
- `"ic50"` - IC50 分析模板
- `"standard_curve"` - 标准曲线模板
- `"paired_ttest"` - 配对 t 检验模板
- `"two_group_ttest"` - 独立 t 检验模板
- `"one_way_anova"` - 单因素 ANOVA 模板
- `"survival"` - 生存分析模板

### create_ic50_template(concentrations=None, replicates=4, title="IC50 Template") -> PrismTemplate

创建 IC50 模板。

### create_standard_curve_template(standard_points=7, replicates=3, title="Standard Curve") -> PrismTemplate

创建标准曲线模板。

### create_anova_template(groups, samples_per_group, title="One-way ANOVA") -> PrismTemplate

创建 ANOVA 模板。

### create_ttest_template(n_pairs, paired=True, title="t-test") -> PrismTemplate

创建 t 检验模板。

### create_survival_template(n_subjects, n_groups=2, title="Survival Analysis") -> PrismTemplate

创建生存分析模板。

### PrismTemplate.save(filepath)

保存模板为 .pzfx 文件。
