---
name: scientific-charter
description: Generate publication-quality scientific charts and visualizations using Matplotlib, Seaborn, and Plotly. Supports line plots, scatter plots, bar charts, heatmaps, 3D plots, statistical visualizations, and more. Includes LaTeX formatting, custom styling, and multiple export formats for academic papers and presentations.
license: MIT
---

# Scientific Charter - Research-Grade Data Visualization

Professional scientific charting skill for creating publication-quality visualizations. Combines the power of Matplotlib, Seaborn, and Plotly with best practices for academic and research applications.

## When to Use

- Creating charts for scientific papers and publications
- Visualizing research data with statistical analysis
- Generating presentation-ready figures with LaTeX labels
- Building interactive visualizations for data exploration
- Producing multi-panel figures with precise control
- Exporting high-resolution charts in multiple formats (PDF, SVG, PNG, HTML)

## Supported Libraries

| Library | Best For | Output Format |
|---------|-----------|---------------|
| **Matplotlib** | Precise control, publication figures, LaTeX | Static (PDF, PNG, SVG) |
| **Seaborn** | Statistical plots, quick exploration | Static (PNG, PDF) |
| **Plotly** | Interactive charts, web display | Interactive (HTML) |

## Core Workflow

### 1. Data Analysis and Chart Selection

When invoked:
1. **Analyze data structure** - Understand variables, types, and relationships
2. **Select appropriate chart type** - Based on data and visualization goals
3. **Choose library** - Matplotlib for publication, Seaborn for statistics, Plotly for interaction
4. **Design visualization** - Colors, layouts, annotations, and formatting

### 2. Chart Types Reference

#### Basic Charts
- **Line Chart** - Trends over time or continuous variables
- **Scatter Plot** - Relationships between two variables
- **Bar Chart** - Categorical comparisons
- **Histogram** - Distribution of single variable
- **Box Plot** - Statistical distribution with quartiles

#### Advanced Charts
- **Heatmap** - Matrix data, correlations, 2D distributions
- **Violin Plot** - Distribution shape with probability density
- **3D Surface/Scatter** - Three-dimensional data
- **Contour Plot** - Topographic-style 2D projections
- **Vector Field** - Direction and magnitude data

#### Statistical Charts
- **Regression Plot** - Linear/curve fitting with confidence intervals
- **Residual Plot** - Model diagnostic visualizations
- **Pair Plot** - Multi-variable relationships matrix
- **Faceted Grid** - Small multiples by category

## Quick Start Examples

### Matplotlib - Publication-Quality Line Chart

```python
import matplotlib.pyplot as plt
import numpy as np

# Data
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# Create figure with Object-Oriented interface
fig, ax = plt.subplots(figsize=(8, 5))

# Plot data
ax.plot(x, y1, label=r'$\sin(x)$', linewidth=2, color='#2E86AB')
ax.plot(x, y2, label=r'$\cos(x)$', linewidth=2, color='#A23B72', linestyle='--')

# Customize for publication
ax.set_xlabel('Time (s)', fontsize=12)
ax.set_ylabel('Amplitude', fontsize=12)
ax.set_title('Trigonometric Functions', fontsize=14, fontweight='bold')
ax.legend(frameon=True, fancybox=True, shadow=True)
ax.grid(True, alpha=0.3, linestyle=':')

# Remove top and right spines for cleaner look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Save in vector format for publication
plt.savefig('figure_1.eps', format='eps', dpi=300, bbox_inches='tight')
plt.savefig('figure_1.pdf', format='pdf', dpi=300, bbox_inches='tight')
plt.close()
```

### Seaborn - Statistical Visualization

```python
import seaborn as sns
import pandas as pd

# Set style for consistent, professional look
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.2)

# Load example dataset
tips = sns.load_dataset("tips")

# Create statistical visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Restaurant Tips Analysis', fontsize=16, fontweight='bold')

# Box plot
sns.boxplot(data=tips, x='day', y='total_bill', ax=axes[0, 0])
axes[0, 0].set_title('Bill Distribution by Day')

# Violin plot
sns.violinplot(data=tips, x='day', y='total_bill', ax=axes[0, 1])
axes[0, 1].set_title('Bill Distribution (Violin)')

# Scatter plot with regression
sns.regplot(data=tips, x='total_bill', y='tip', ax=axes[1, 0])
axes[1, 0].set_title('Bill vs Tip (with regression)')

# Categorical scatter
sns.swarmplot(data=tips, x='day', y='tip', ax=axes[1, 1])
axes[1, 1].set_title('Tips by Day (Swarm plot)')

plt.tight_layout()
plt.savefig('statistical_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
```

### Plotly - Interactive 3D Scatter

```python
import plotly.express as px
import pandas as pd

# Create sample data
df = px.data.iris()

# Create interactive 3D scatter
fig = px.scatter_3d(
    df,
    x='sepal_length',
    y='sepal_width',
    z='petal_width',
    color='species',
    size='petal_length',
    hover_data=['petal_length', 'petal_width'],
    title='Iris Dataset - 3D Visualization'
)

# Customize layout
fig.update_layout(
    scene=dict(
        xaxis_title='Sepal Length (cm)',
        yaxis_title='Sepal Width (cm)',
        zaxis_title='Petal Width (cm)',
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
    ),
    font=dict(size=12),
    showlegend=True,
    width=900,
    height=700
)

# Save as interactive HTML
fig.write_html('iris_3d_interactive.html')
fig.show()
```

## LaTeX Integration for Publications

### Enabling LaTeX in Matplotlib

```python
import matplotlib.pyplot as plt

# Enable LaTeX rendering
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
    "figure.titlesize": 16
})

# Use LaTeX in labels
fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_xlabel(r'Time, $t$ (s)')
ax.set_ylabel(r'Amplitude, $A$ (mV)')
ax.set_title(r'Signal with $\alpha = 0.05$ significance')
ax.text(0.5, 0.5, r'$f(x) = \frac{1}{\sqrt{2\pi}} e^{-\frac{x^2}{2}}$',
        transform=ax.transAxes, fontsize=14)
```

## Color Schemes for Science

### Perceptually Uniform Colormaps (Recommended)

```python
import matplotlib.pyplot as plt
import numpy as np

# Sample data
data = np.random.randn(20, 20)

# Good colormaps (perceptually uniform)
good_cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

for idx, cmap in enumerate(good_cmaps):
    im = axes[idx].imshow(data, cmap=cmap)
    axes[idx].set_title(f'{cmap}')
    plt.colorbar(im, ax=axes[idx], fraction=0.046, pad=0.04)

plt.tight_layout()
plt.savefig('perceptually_uniform_colormaps.png', dpi=300, bbox_inches='tight')
plt.close()
```

### Colorblind-Friendly Palettes

```python
import seaborn as sns

# Colorblind-friendly palette
colorblind_palette = sns.color_palette("colorblind", 10)

# Use in plots
sns.set_palette(colorblind_palette)

# Or define custom palette
custom_palette = ['#0173b2', '#de8f05', '#029e73', '#cc78bc', 
                   '#ca9161', '#fbafe4', '#949494', '#ece133']
```

## Multi-Panel Figures

### Using GridSpec for Complex Layouts

```python
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Create figure with GridSpec
fig = plt.figure(figsize=(12, 8))
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

# Panel A - Large top row
axA = fig.add_subplot(gs[0, :])
axA.plot(x, y1, linewidth=2)
axA.set_title('(A) Overview', loc='left', fontweight='bold')

# Panel B - Left column, rows 2-3
axB = fig.add_subplot(gs[1:, 0])
axB.scatter(x, y2, alpha=0.6)
axB.set_title('(B) Details', loc='left', fontweight='bold')

# Panel C - Center, row 2
axC = fig.add_subplot(gs[1, 1])
axC.hist(data, bins=30, edgecolor='black')
axC.set_title('(C) Distribution', loc='left', fontweight='bold')

# Panel D - Center, row 3
axD = fig.add_subplot(gs[2, 1])
axD.boxplot([data1, data2, data3])
axD.set_title('(D) Comparison', loc='left', fontweight='bold')

# Panel E - Right column, rows 2-3
axE = fig.add_subplot(gs[1:, 2])
im = axE.imshow(correlation_matrix, cmap='RdBu_r')
axE.set_title('(E) Correlation', loc='left', fontweight='bold')
plt.colorbar(im, ax=axE, fraction=0.046, pad=0.04)

plt.savefig('multi_panel_figure.pdf', format='pdf', bbox_inches='tight')
plt.close()
```

## Export Formats Guide

### Choosing the Right Format

| Format | Use Case | Advantages | Disadvantages |
|--------|-----------|-------------|----------------|
| **PDF** | Publications, presentations | Vector, scalable, small file | Requires PDF reader |
| **SVG** | Web, editing | Vector, editable in Illustrator | Larger file size |
| **PNG** | Web, previews | Universal support | Rasterized, fixed resolution |
| **EPS** | LaTeX documents | Vector, LaTeX-compatible | Outdated format |
| **TIFF** | Print publications | High quality, lossless | Very large file size |

### High-Resolution Export

```python
fig, ax = plt.subplots()

# Plot your data
ax.plot(x, y)

# Save in multiple formats with proper settings
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

## Statistical Visualization with Seaborn

### Distribution Analysis

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Set style
sns.set_style("ticks")
sns.set_context("talk")

# Load data
df = sns.load_dataset("penguins")

# Create distribution analysis
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Penguin Morphology Analysis', fontsize=18, fontweight='bold')

# Histogram with KDE
sns.histplot(data=df, x='bill_length_mm', hue='species', 
             element='step', stat='density', common_norm=False, 
             ax=axes[0, 0])
axes[0, 0].set_title('Bill Length Distribution')

# KDE plot
sns.kdeplot(data=df, x='flipper_length_mm', hue='species',
             fill=True, common_norm=False, alpha=0.4, ax=axes[0, 1])
axes[0, 1].set_title('Flipper Length Density')

# ECDF plot
sns.ecdfplot(data=df, x='body_mass_g', hue='species', ax=axes[1, 0])
axes[1, 0].set_title('Body Mass ECDF')

# Rug plot with strip plot
sns.stripplot(data=df, x='species', y='bill_depth_mm', 
               hue='species', jitter=True, alpha=0.7, ax=axes[1, 1])
axes[1, 1].set_title('Bill Depth by Species')

plt.tight_layout()
plt.savefig('penguin_distribution_analysis.pdf', bbox_inches='tight')
plt.close()
```

## 3D Visualization

### Surface and Wireframe Plots

```python
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Create 3D data
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

# Create 3D figure
fig = plt.figure(figsize=(12, 5))

# Surface plot
ax1 = fig.add_subplot(131, projection='3d')
surf = ax1.plot_surface(X, Y, Z, cmap='viridis', 
                         linewidth=0, antialiased=True)
ax1.set_title('Surface Plot')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
fig.colorbar(surf, ax=ax1, shrink=0.5, aspect=10)

# Wireframe plot
ax2 = fig.add_subplot(132, projection='3d')
wire = ax2.plot_wireframe(X, Y, Z, color='navy', alpha=0.8)
ax2.set_title('Wireframe Plot')

# Contour plot (2D projection)
ax3 = fig.add_subplot(133)
contour = ax3.contourf(X, Y, Z, levels=20, cmap='RdBu')
ax3.set_title('Contour Plot')
ax3.set_aspect('equal')
plt.colorbar(contour, ax=ax3)

plt.tight_layout()
plt.savefig('3d_visualization.png', dpi=300, bbox_inches='tight')
plt.close()
```

## Error Bars and Confidence Intervals

### Adding Uncertainty Representation

```python
import matplotlib.pyplot as plt
import numpy as np

# Data with uncertainty
x = np.arange(5)
y = np.array([10, 15, 13, 18, 16])
yerr = np.array([1.2, 0.8, 1.5, 1.0, 0.9])  # Standard error

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Symmetric error bars
axes[0].errorbar(x, y, yerr=yerr, fmt='o-', capsize=5, 
                  capthick=2, label='Data with SE')
axes[0].set_title('Symmetric Error Bars')
axes[0].legend()

# Asymmetric error bars
yerr_asym = np.array([[0.8, 1.0, 1.2, 0.7, 0.9],   # Lower error
                      [1.5, 1.2, 1.8, 1.3, 1.1]]).T  # Upper error
axes[1].errorbar(x, y, yerr=yerr_asym, fmt='s--', capsize=8,
                  color='darkred', label='Asymmetric Errors')
axes[1].set_title('Asymmetric Error Bars')
axes[1].legend()

# Confidence interval as shaded region
x_continuous = np.linspace(0, 10, 100)
y_continuous = 2 * x_continuous + 1
y_ci_lower = y_continuous - 2
y_ci_upper = y_continuous + 2

axes[2].plot(x_continuous, y_continuous, 'k-', linewidth=2, label='Mean')
axes[2].fill_between(x_continuous, y_ci_lower, y_ci_upper, 
                      alpha=0.3, color='gray', label='95% CI')
axes[2].set_title('Confidence Interval')
axes[2].legend()

plt.tight_layout()
plt.savefig('error_visualization.pdf', bbox_inches='tight')
plt.close()
```

## Best Practices for Scientific Charts

### DO's ✅

1. **Use vector formats for publications** (PDF, EPS, SVG)
2. **Set DPI appropriately** - 300+ for print, 72-150 for screen
3. **Always label axes** with units
4. **Use `bbox_inches='tight'`** when saving to prevent clipping
5. **Close figures in loops** to prevent memory leaks
6. **Use colorblind-friendly palettes** (viridis, colorblind)
7. **Include error bars** when showing experimental data
8. **Use consistent styling** across multi-panel figures
9. **Test at target size** - Will it be readable when printed?
10. **Use LaTeX for mathematical notation**

### DON'T's ❌

1. **Avoid rainbow colormap** (jet) - Use perceptually uniform instead
2. **Don't use 3D when 2D suffices** - Harder to read accurately
3. **Don't over-smooth data** - Preserve important features
4. **Don't use pie charts for precise comparison** - Bar charts are better
5. **Don't rely on color alone** - Use markers/shapes for differentiation
6. **Don't forget to cite data sources**
7. **Don't use misleading axes** (always start at 0 for bar charts)
8. **Don't overcrowd with text** - Let the data speak
9. **Don't use default styles for publication** - Always customize
10. **Don't ignore accessibility** - Consider colorblind viewers

## Common Chart Templates

See `references/chart_templates.py` for complete, ready-to-use templates for:
- Line charts with multiple series
- Scatter plots with regression
- Bar charts (grouped, stacked)
- Heatmaps with annotations
- Box plots with significance markers
- Time series with trend lines

## Troubleshooting

### Font Rendering Issues

```python
# If LaTeX fails, use mathtext instead
plt.rcParams.update({
    "text.usetex": False,
    "mathtext.fontset": "cm"  # Computer Modern
})
```

### Memory Issues with Large Datasets

```python
# Use downsampling for large datasets
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

# Downsample before plotting
if len(x) > 10000:
    indices = np.linspace(0, len(x)-1, 10000, dtype=int)
    x = x[indices]
    y = y[indices]

# Close all figures after saving
plt.close('all')
```

### Colorbar Alignment

```python
from mpl_toolkits.axes_grid1 import make_axes_locatable

fig, ax = plt.subplots()
im = ax.imshow(data, cmap='viridis')

# Proper colorbar alignment
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
plt.colorbar(im, cax=cax)
```

## References

- Matplotlib Gallery: https://matplotlib.org/stable/gallery/index.html
- Seaborn Tutorial: https://seaborn.pydata.org/tutorial.html
- Plotly Documentation: https://plotly.com/python/
- Colorbrewer (Color schemes): https://colorbrewer2.org/
- Nature Journal Guidelines: https://www.nature.com/nature/for-authors/formatting-guide
