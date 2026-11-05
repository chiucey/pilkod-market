# Chart Generation Reference - 高端数据趋势图

## 核心原则

每个数据表必须配一张高端折线趋势图。图表紧随对应表格之后，形成"表+图"组合。

## 图表分类与生成规则

### Category 1: 血糖组合图 (Glucose Combo)
- **指标**: 空腹血糖(FPG)、餐后2h血糖(PPG)、HbA1c
- **类型**: 双Y轴组合图
- **左Y轴**: FPG/PPG (mmol/L)，范围 0-20
- **右Y轴**: HbA1c (%)，范围 4-14
- **参考线**: FPG 6.1 (虚线), PPG 7.8 (虚线), HbA1c 6.5 (虚线)

### Category 2: 胰岛功能图 (Pancreatic Function)
- **指标**: 空腹C肽、空腹胰岛素
- **类型**: 双Y轴图
- **左Y轴**: C肽 (nmol/L)
- **右Y轴**: 胰岛素 (mIU/L 或 pmol/L)

### Category 3: 血脂多线图 (Lipids Multi-Line)
- **指标**: TG、TC、LDL-C、HDL-C
- **类型**: 4线折线图
- **参考线**: TG 1.7, TC 5.7, LDL-C 3.36, HDL-C 0.9 (各指标上限/下限)
- **注意**: HDL-C为下限参考线，其余为上限

### Category 4: 肾功能双轴图 (Renal Dual-Axis)
- **指标**: 肌酐(CREA)、eGFR
- **类型**: 双Y轴图
- **左Y轴**: CREA (umol/L)，范围 0-200
- **右Y轴**: eGFR (mL/min)，范围 0-150，反向显示
- **关键**: eGFR与CREA趋势相反，需在图中直观呈现

### Category 5: 肝功能多线图 (Liver Multi-Line)
- **指标**: ALT、AST、GGT
- **类型**: 3线折线图
- **参考线**: ALT 50, AST 40, GGT 60 (虚线)

### Category 6: 血常规多线图 (Hematology Multi-Line)
- **指标**: WBC、RBC、Hb、PLT
- **类型**: 因单位差异大，拆分为2个子图
  - 子图A: WBC + PLT (10^9/L 量级)
  - 子图B: RBC + Hb (10^12/L 和 g/L 量级)

### Category 7: 炎症/肿标图 (Inflammation/Tumor Markers)
- **指标**: CRP、CEA、CA19-9、CA125等
- **类型**: 多线折线图
- **Y轴**: 对数刻度 (log scale) 当数据跨度>10倍时

### Category 8: 电解质图 (Electrolytes)
- **指标**: K、Na、Cl
- **类型**: 多线折线图

### Category 9: 尿肾功能图 (Urinary Renal)
- **指标**: UACR、尿微量白蛋白
- **类型**: 单线/多线折线图

### Category 10: 其他指标图 (Other)
- **指标**: 同型半胱氨酸(Hcy)、维生素D、TSH等
- **类型**: 单线折线图

### Category 11: 影像测量值趋势图 (Imaging Measurements)
- **指标**: 同一影像项目中有具体测量值的器质性改变，如肝囊肿最大径、肺结节最大径、前列腺最大径、息肉大小等
- **类型**: 单线折线图，每个测量项目一张，一排两个排版（图N紧随影像对比表之后）
- **X轴**: 该项目的影像检查日期轴（可与血液指标时间轴不同，按实际检查日期标注）
- **数据规则**:
  - 仅绘制原始报告中真实存在的测量数值
  - 未测量的时间点不得虚构/插值，在该点位置标注"未测量"，折线在缺失处自然断开
  - 同一图内单位统一（cm 或 mm），不同单位项目必须分图绘制
- **参考线**: 有临床意义界值时加虚线参考线（如肺结节 8mm）
- **样式**: 沿用统一高端图表样式（隐藏上/右边框、虚线网格、数据点标签加粗显示）

### Category 12: 定性结果阶梯图 (Qualitative Step Charts)
- **指标**: 定性/半定性结果，如 HPV 分型阴性/阳性、尿潜血 -/+、幽门螺杆菌 -/+
- **类型**: 阶梯图 (plt.step)，将定性状态映射为离散层级（如 阴性=0, 弱阳=0.5, 阳性=1），Y轴用文字刻度标注状态
- **适用场景**: 同一项目 >=3 个时间点且状态发生过变化（如 HPV52 连续两年阳性后转阴）；状态从未变化时表格即可，不必配图
- **数据规则**: 仅映射原始报告中出现的真实状态，未查时间点留空

## 统一高端图表样式

### matplotlib 配置

```python
import matplotlib.pyplot as plt
import numpy as np

COLOR_PRIMARY = '#005293'
COLOR_SECONDARY = '#5983AF'
COLOR_RED = '#E85D4E'
COLOR_GREEN = '#4CAF50'
COLOR_GRAY = '#808080'
COLOR_BORDER = '#C8D2DC'
COLOR_BG = '#FAFBFC'
COLOR_GRID = '#E8ECF0'

LINE_COLORS = ['#005293', '#E85D4E', '#4CAF50', '#5983AF', '#FF9800', '#9C27B0']
MARKER_STYLES = ['o', 's', 'D', '^', 'v', '<']

plt.rcParams['font.family'] = ['WenQuanYi Zen Hei', 'Noto Sans CJK SC', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def apply_premium_style(ax, title=''):
    ax.set_facecolor(COLOR_BG)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_BORDER)
    ax.spines['bottom'].set_color(COLOR_BORDER)
    ax.grid(True, axis='y', linestyle='--', alpha=0.4, color=COLOR_GRID, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis='both', colors=COLOR_GRAY, labelsize=9)
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold', color=COLOR_PRIMARY, pad=20, loc='left')
```

## 图表输出规范

| 属性 | 值 |
|------|-----|
| figsize | (12, 6) 标准, (14, 7) 多线复杂图 |
| dpi | 200 |
| 格式 | PNG |
| 嵌入方式 | base64 encode -> HTML img 标签 |

## 图表与表格的排版关系

```
### 6.X 系统名称
[说明文字 1-2行]
[数据对比表格]
[趋势折线图]  <- 紧跟表格
[关键发现 2-3行]
```
