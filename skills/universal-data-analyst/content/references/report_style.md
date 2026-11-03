---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022075a935eca32e68e2cbd3d334901c88c52498cb8b4041aa960869d39aaf71149f022100f5327247a30d0f3a36ab91b8d97b70b7cad6869c46a8bdf82e3fb4dea2ff20f6
    ReservedCode2: 3045022100ddd94fe28212e6a7a40495e9cb35ae6758d99369d064e2046574f77ff98f5327022026026ae3ba6283ab043857b74dd2c33ed05a426aad6b08a1a68c3ddb0aa0d56c
---

# 报告样式规范

## 报告结构

### HTML 报告

```
analysis_report.html
├── 头部信息
│   ├── 报告标题
│   ├── 生成时间
│   └── 数据源信息
│
├── 关键指标卡片
│   └── 核心数字一览
│
├── 1. 数据质量诊断
│   ├── 质量评分
│   ├── 问题列表
│   └── 清洗建议
│
├── 2. 数据特征描述
│   ├── 实体类型
│   ├── 生成机制
│   ├── 核心维度
│   └── 关键词标签
│
├── 3. 分析方法规划
│   ├── 问题类型判定
│   ├── 推荐框架
│   └── 分析步骤
│
├── 4. 分析结果
│   ├── 执行摘要
│   ├── 详细发现
│   └── 可视化图表
│
└── 5. 结论与建议
    ├── 主要结论
    ├── 行动建议
    └── 数据局限性
```

### Markdown 报告

```markdown
# 数据分析报告

> 生成时间：YYYY-MM-DD HH:MM
> 数据源：filename.csv

---

## 1. 数据质量诊断

### 1.1 数据规模
- 原始数据：X 行 × Y 列

### 1.2 发现的问题
- [WARNING] column: 描述

## 2. 数据特征描述

### 2.1 实体类型
- 判定：交易/事件型

### 2.2 数据生成机制
- 判定：观测型

## 3. 分析方法规划

### 3.1 问题类型
- 描述型

### 3.2 推荐框架
- RFM分析

## 4. 分析结果

### 4.1 执行摘要
- 核心发现...

## 5. 结论与建议
```

## 样式规则

### 数字格式

```html
<!-- 千分位 -->
1,234,567

<!-- 百分比 -->
85.5%

<!-- 货币 -->
¥1,234.56 或 $1,234.56

<!-- 科学计数 -->
1.23e+05
```

### 表格样式

```html
<table class="financial-table">
  <thead>
    <tr>
      <th>指标</th>
      <th>数值</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>总销售额</td>
      <td class="num">1,234,567</td>
    </tr>
  </tbody>
</table>
```

### 图表容器

```html
<div class="chart-container">
  <img src="chart.png" alt="图表描述" />
  <div class="chart-caption">图1: 销售趋势图</div>
</div>
```

### 结论框

```html
<div class="conclusion-box">
  <div class="conclusion-title">结论</div>
  <ul class="conclusion-list">
    <li>结论1</li>
    <li>结论2</li>
  </ul>
</div>
```

### 问题/警告框

```html
<div class="issue-item warning">
  <span class="issue-field">price</span>：存在异常值
</div>
```

## CSS 变量

```css
:root {
  --color-primary: #1a1a1a;
  --color-secondary: #666666;
  --color-accent: #2196F3;
  --color-warning: #f39c12;
  --color-danger: #c00;
  --color-success: #27ae60;
  --color-bg: #ffffff;
  --color-bg-alt: #f8f9fa;
  --font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  --font-mono: 'Consolas', 'Monaco', monospace;
}
```

## 响应式设计

- 最大宽度: 900px
- 移动端适配: 单列布局
- 图表: max-width 100%

## 图表规范

### 文件命名

```
charts/
├── distribution_xxx.png    # 分布图
├── trend_xxx.png          # 趋势图
├── correlation_xxx.png    # 相关性图
├── heatmap_xxx.png       # 热力图
└── bar_chart_xxx.png     # 柱状图
```

### 图表尺寸

- 宽度: 600-800px
- 高度: 400-600px
- 分辨率: 150 DPI (屏幕)
- 格式: PNG

### 图表标题

- 位置: 上方
- 字体: 14px 粗体
- 内容: 简明描述

## 输出文件结构

```
session_YYYYMMDD_HHMMSS/
├── SESSION_SUMMARY.json          # 会话摘要
├── step1_data_info.json          # 数据基本信息
├── step2_validation_report.json   # 数据校验报告
├── step2_cleaning_report.txt     # 清洗建议
├── step3_ontology_prompt.txt     # 本体识别提示词
├── step4_planning_prompt.txt     # 方案规划提示词
├── step5_script_prompt.txt       # 脚本生成提示词
├── FLOW_HEALTH_REPORT.json       # 流程健康报告
├── analysis_report.html          # HTML报告
├── analysis_report.md            # Markdown报告
└── output/
    ├── analysis_script.py        # 分析脚本
    ├── figures/                  # 图表目录
    │   ├── chart_1.png
    │   └── chart_2.png
    └── results.json              # 数值结果
```
