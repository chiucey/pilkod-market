---
name: nature-figure
description: 生成符合Nature期刊视觉标准的科研图表。当用户要求图表、figure、绘图、matplotlib、绘制、科研图片或生成图表时使用。
---

# Nature Figure 科研绘图技能

## 核心规则

### 字体规范
- 字体族：sans-serif
- 推荐字体：Arial, DejaVu Sans, Liberation Sans
- 字号：**7pt**

### 输出格式
| 格式 | 用途 |
|------|------|
| .svg | 主格式（矢量，文字可编辑） |
| .png | 备选（300dpi） |

### 配色方案 (NMI Pastel)

| 颜色 | 色值 |
|------|------|
| Blue | #6BAED6 |
| Orange | #FD8D3C |
| Green | #74C476 |
| Purple | #9E9AC8 |
| Red | #FC8D59 |

### 面板标注
- 使用小写字母：a, b, c
- 加粗显示，左对齐
- 位置：左上角

## 支持的图表类型

1. **条形图**：堆叠条形图、分组条形图、水平消融条形图
2. **折线图**：趋势图、置信区间图
3. **热力图**：顺序热力图、发散型Z-score热力图
4. **散点图**：气泡散点图
5. **雷达图**：极坐标图
6. **3D图**：球体示意图
7. **面积图**：填充面积图
8. **对数图**：对数刻度条形图
9. **多面板**：GridSpec多面板图表

## 工作流程

1. **需求解析**：确定图表类型和数据结构
2. **模板选择**：选择适合的图表模板
3. **样式应用**：应用Nature视觉规范
4. **数据绑定**：绑定实际数据
5. **导出输出**：生成svg/png格式

## 核心代码模式

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# Nature 风格设置
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'font.size': 7,
    'axes.linewidth': 0.5,
    'axes.labelsize': 7,
    'xtick.labelsize': 6,
    'ytick.labelsize': 6
})
```

## 示例

**输入**：生成一个对比实验组和对照组正确率的条形图

**输出**：Python matplotlib代码，Nature风格设置

## 质量检查清单

- [ ] 字体为 sans-serif，字号 7pt
- [ ] 使用 NMI Pastel 配色
- [ ] 面板标注为加粗 a, b, c
- [ ] 输出 svg 和 png 格式
- [ ] 坐标轴标签清晰