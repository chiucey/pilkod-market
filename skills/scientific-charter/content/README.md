# Scientific Charter

科研图表绘制技能包，支持生成出版质量的数据可视化图表。

## ✨ 功能特性

- ✅ **多库支持**: Matplotlib、Seaborn、Plotly
- ✅ **出版质量**: PDF、SVG、PNG、EPS 格式输出
- ✅ **LaTeX 支持**: 公式和标签渲染
- ✅ **色盲友好**: 使用感知均匀的配色方案
- ✅ **多面板布局**: GridSpec 复杂图形排版
- ✅ **内置模板**: 多种可复用图表模板

## 📊 支持的图表类型

### 基础图表
- 线图 (Line Chart)
- 散点图 (Scatter Plot)
- 条形图 (Bar Chart)
- 直方图 (Histogram)
- 箱线图 (Box Plot)

### 高级图表
- 热图 (Heatmap)
- 小提琴图 (Violin Plot)
- 3D 表面图 (3D Surface)
- 轮廓图 (Contour Plot)
- 矢量场 (Vector Field)

### 统计图表
- 回归图 (Regression Plot)
- 残差图 (Residual Plot)
- 配对图 (Pair Plot)
- 分面网格 (Faceted Grid)

## 🚀 安装

### 方法 1: 使用 npx skills (推荐)

```bash
npx skills add <this-repo-url>
```

### 方法 2: 手动安装

1. 下载 `scientific-charter.skill` 文件
2. 运行安装命令：

```bash
npx skills add ./scientific-charter.skill
```

### 方法 3: 从源文件安装

```bash
git clone https://github.com/<your-username>/scientific-charter.git
cd scientific-charter
npx skills add .
```

## 📖 使用方法

安装后，直接描述您的图表需求，技能会自动触发：

```
请帮我创建一个出版质量的线图，展示温度变化趋势
```

```
用 Seaborn 创建一个统计可视化图表
```

```
生成一个 3D 散点图，展示三个变量之间的关系
```

## 💡 快速示例

### Matplotlib - 出版质量线图

```python
import matplotlib.pyplot as plt
import numpy as np

# 数据
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# 创建出版质量图表
plt.figure(figsize=(8, 6))
plt.plot(x, y1, label=r'$\sin(x)$', linewidth=2, color='#2E86AB')
plt.plot(x, y2, label=r'$\cos(x)$', linewidth=2, color='#A23B72', linestyle='--')

# 自定义样式
plt.xlabel('时间 (s)', fontsize=12)
plt.ylabel('振幅', fontsize=12)
plt.title('三角函数', fontsize=14, fontweight='bold')
plt.legend(frameon=True, fancybox=True, shadow=True)
plt.grid(True, alpha=0.3, linestyle=':')

# 保存矢量格式
plt.savefig('figure_1.pdf', dpi=300, bbox_inches='tight')
plt.close()
```

### Seaborn - 统计可视化

```python
import seaborn as sns
import matplotlib.pyplot as plt

# 设置样式
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.2)

# 加载示例数据
tips = sns.load_dataset("tips")

# 创建统计图表
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('餐厅小费分析', fontsize=16, fontweight='bold')

# 箱线图
sns.boxplot(data=tips, x='day', y='total_bill', ax=axes[0, 0])
axes[0, 0].set_title('每日账单分布')

# 小提琴图
sns.violinplot(data=tips, x='day', y='total_bill', ax=axes[0, 1])
axes[0, 1].set_title('账单分布（小提琴图）')

# 带回归的散点图
sns.regplot(data=tips, x='total_bill', y='tip', ax=axes[1, 0])
axes[1, 0].set_title('账单 vs 小费（带回归线）')

# 分类散点图
sns.swarmplot(data=tips, x='day', y='tip', ax=axes[1, 1])
axes[1, 1].set_title('每日小费（蜂群图）')

plt.tight_layout()
plt.savefig('statistical_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
```

### Plotly - 交互式 3D 散点图

```python
import plotly.express as px

# 创建示例数据
df = px.data.iris()

# 创建交互式 3D 散点图
fig = px.scatter_3d(
    df,
    x='sepal_length',
    y='sepal_width',
    z='petal_width',
    color='species',
    size='petal_length',
    hover_data=['petal_length', 'petal_width'],
    title='鸢尾花数据集 - 3D 可视化'
)

# 自定义布局
fig.update_layout(
    scene=dict(
        xaxis_title='萼片长度 (cm)',
        yaxis_title='萼片宽度 (cm)',
        zaxis_title='花瓣宽度 (cm)',
    ),
    font=dict(size=12),
    showlegend=True,
    width=900,
    height=700
)

# 保存为交互式 HTML
fig.write_html('iris_3d_interactive.html')
fig.show()
```

## 🎨 图表模板

技能包含以下可复用模板（`references/chart_templates.py`）：

- `create_line_chart()` - 线图模板
- `create_scatter_plot()` - 散点图模板
- `create_heatmap()` - 热图模板
- `create_bar_chart()` - 条形图模板
- `create_boxplot()` - 箱线图模板
- `create_3d_scatter()` - 3D 散点图模板

## 📐 LaTeX 集成

### 在 Matplotlib 中启用 LaTeX

```python
import matplotlib.pyplot as plt

# 启用 LaTeX 渲染
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman", "Times New Roman"],
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})

# 在标签中使用 LaTeX
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_xlabel(r'时间, $t$ (s)')
ax.set_ylabel(r'振幅, $A$ (mV)')
ax.set_title(r'信号 with $\alpha = 0.05$ 显著性')
ax.text(0.5, 0.5, r'$f(x) = \frac{1}{\sqrt{2\pi}} e^{-\frac{x^2}{2}}$',
        transform=ax.transAxes, fontsize=14)
```

## 🎨 科学配色方案

### 感知均匀色彩图（推荐）

```python
# 好的色彩图（感知均匀）
good_cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
```

### 色盲友好调色板

```python
import seaborn as sns

# 色盲友好调色板
colorblind_palette = sns.color_palette("colorblind", 10)

# 或使用自定义调色板
custom_palette = ['#0173b2', '#de8f05', '#029e73', '#cc78bc', 
                   '#ca9161', '#fbafe4', '#949494', '#ece133']
```

## 📤 导出格式指南

| 格式 | 使用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **PDF** | 论文、演示 | 矢量、可缩放、文件小 | 需要 PDF 阅读器 |
| **SVG** | 网页、编辑 | 矢量、可用 Illustrator 编辑 | 文件较大 |
| **PNG** | 网页、预览 | 通用支持 | 栅格化、固定分辨率 |
| **EPS** | LaTeX 文档 | 矢量、兼容 LaTeX | 过时格式 |
| **TIFF** | 印刷出版 | 高质量、无损 | 文件非常大 |

### 高分辨率导出

```python
fig, ax = plt.subplots()

# 绘制数据
ax.plot(x, y)

# 多格式保存
formats = {
    'pdf': dict(format='pdf', bbox_inches='tight'),
    'svg': dict(format='svg', bbox_inches='tight'),
    'png': dict(format='png', dpi=300, bbox_inches='tight'),
    'tiff': dict(format='tiff', dpi=600, bbox_inches='tight', compression='lzw')
}

for fmt, params in formats.items():
    fig.savefig(f'figure_1.{fmt}', **params)

plt.close()
```

## ✅ 最佳实践

### 应该做的 ✅

1. **出版使用矢量格式** (PDF, EPS, SVG)
2. **设置合适的 DPI** - 印刷 300+，屏幕 72-150
3. **始终标注坐标轴** 和单位
4. **保存时使用 `bbox_inches='tight'`** 防止裁剪
5. **在循环中关闭图表** 防止内存泄漏
6. **使用色盲友好调色板** (viridis, colorblind)
7. **包含误差条** 当展示实验数据时
8. **使用一致的样式** 多面板图形
9. **在目标尺寸下测试** - 打印时是否清晰可读？
10. **使用 LaTeX 表示数学符号**

### 不应该做的 ❌

1. **避免使用彩虹色彩图** (jet) - 使用感知均匀色彩图
2. **2D 足够时不要使用 3D** - 更难准确读取
3. **不要过度平滑数据** - 保留重要特征
4. **不要使用饼图进行精确比较** - 条形图更好
5. **不要仅依赖颜色** - 使用标记/形状区分
6. **不要忘记引用数据来源**
7. **不要使用误导性坐标轴** (条形图始终从 0 开始)
8. **不要使图表过于拥挤** - 让数据说话
9. **不要对出版物使用默认样式** - 始终自定义
10. **不要忽视可访问性** - 考虑色盲观众

## 🔧 故障排除

### 字体渲染问题

```python
# 如果 LaTeX 失败，使用 mathtext 替代
plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "cm"  # Computer Modern
})
```

### 大数据集的内存问题

```python
# 对大数据集使用下采样
import matplotlib
matplotlib.use('Agg')  # 非交互式后端

# 绘图前下采样
if len(x) > 10000:
    indices = np.linspace(0, len(x)-1, 10000, dtype=int)
    x = x[indices]
    y = y[indices]

# 保存后关闭所有图表
plt.close('all')
```

### 颜色条对齐

```python
from mpl_toolkits.axes_grid1 import make_axes_locatable

fig, ax = plt.subplots()
im = ax.imshow(data, cmap='viridis')

# 正确的颜色条对齐
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
plt.colorbar(im, cax=cax)
```

## 📋 要求

- Python 3.8+
- Matplotlib 3.5+
- Seaborn 0.12+ (可选)
- Plotly 5.0+ (可选)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 👤 作者

Created by WorkBuddy User

## 📝 更新日志

### v1.0.0 (2026-05-05)
- 初始版本
- 支持基础图表类型
- 添加出版质量输出
- 内置图表模板

## 🔗 相关链接

- [Matplotlib 图库](https://matplotlib.org/stable/gallery/index.html)
- [Seaborn 教程](https://seaborn.pydata.org/tutorial.html)
- [Plotly 文档](https://plotly.com/python/)
- [ColorBrewer 配色方案](https://colorbrewer2.org/)
- [Nature 期刊指南](https://www.nature.com/nature/for-authors/formatting-guide)
