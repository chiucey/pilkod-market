---
name: car-user-profile-report
description: 生成车型用户价值链分析报告。当用户要求分析汽车用户评价、创建懂车帝/汽车之家/小红书/抖音用户评价报告、制作车型对比报告、用户画像分析、感知层分析（驾驶体验/静态感受/特殊场景/智能驾驶）、竞品分析报告，或进行A/A0级两厢车等细分市场研究时使用。
---

# 车型用户画像分析报告生成器

## 概述

这是一个基于 NCBS (New Car Buyer Survey) 调研数据、市场销量数据和 UGC 用户评价数据的车型用户画像分析报告生成系统。报告以交互式 HTML 形式呈现，支持折叠展开、数据可视化、图表交互等功能。

## 核心功能

### 1. 数据整合
- **NCBS 调研数据**：用户人口统计、购车原因、使用场景等
- **市场销量数据**：月度销量趋势、累计排名
- **UGC 数据**：懂车帝/汽车之家/小红书/抖音用户评价关键词
- **车型参数**：入门成交价、车身长度等

### 2. 报告结构（10个板块）

| 板块 | 内容 |
|------|------|
| 一、市场概览 | 核心数据统计卡片 |
| 二、销量分析 | 月度趋势图（10+车型）、累计排名、价格-尺寸散点图 |
| 三、人口统计 | 年龄/性别/学历/收入/家庭结构分布 |
| 四、购车行为 | 购车原因、使用场景、年均里程 |
| 五、UGC分析 | 关键词云、各车型热词 |
| 六、车型对比 | 详细参数对比表 |
| 七、用户画像 | 四款车型典型用户卡片 |
| 八、共同特征 | 市场共性 vs 车型差异 |
| 九、新车预告 | 半年内上市新车 |
| 十、结论建议 | 市场机会与营销建议 |

### 3. 交互功能

- **折叠展开**：所有板块支持点击展开/收起
- **图表交互**：柱状图支持点击高亮、再次点击恢复
- **散点图**：气泡大小代表销量，悬停显示详情
- **数据溯源**：每个图表标注 Source，点击可展开问卷信息

### 4. 设计规范

- **配色方案**：
  - Primary: `#667eea` (渐变紫)
  - Golf: `#ff6b6b` (红色)
  - ID.3: `#4ecdc4` (青色)
  - Smart: `#ffe66d` (黄色)
  - Dolphin: `#95e1d3` (薄荷绿)

- **图表库**：Chart.js + chartjs-plugin-datalabels

- **响应式设计**：支持 1024px/768px 断点

## 使用方法

### 基本命令

```
创建车型用户画像报告 - 包含NCBS调研、市场销量、UGC数据
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| segment | string | 市场细分，如 "A/A0级两厢新能源" |
| models | string[] | 核心分析车型，如 ["大众高尔夫纯电", "上汽ID.3"] |
| dataSource | object | 数据源配置 |

### 数据格式

#### NCBS Excel 数据结构
```javascript
// Sheet: %commute
// D4/D5 Commuting to and from work
{
  "Almost every day": 0.8647,      // 86.5%
  "At least once a week": 0.1113, // 11.1%
  "Never": 0.0118
}

// Sheet: %child back
// D4/D5 Carrying children on second row
{
  "Almost every day": 0.1167,     // 11.7%
  "At least once a week": 0.4977, // 49.8%
  "Weekly+ (合计)": 0.6143        // 61.4%
}

// Sheet: %adult back
// D4/D5 Carrying adults on second row
{
  "Almost every day": 0.0616,     // 6.2%
  "At least once a week": 0.6859, // 68.6%
  "Weekly+ (合计)": 0.7475        // 74.8%
}
```

#### 销量数据结构
```javascript
{
  "monthly": {
    "2025-01": { "吉利星愿": 28146, "比亚迪海豚": 4655, ... },
    "2025-02": { ... }
  },
  "cumulative": {
    "吉利星愿": 475775,
    "比亚迪海豚": 155720
  }
}
```

## 输出示例

部署后的 HTML 报告 URL 格式：
```
https://{project-name}-{hash}.space.minimaxi.com
```

## 技术实现要点

### 1. 柱状图交互实现

```javascript
// 存储原始颜色
const originalColorsMap = new Map();

function setupChartInteraction(chart) {
  chart.data.datasets.forEach((dataset, index) => {
    originalColorsMap.set(chart.canvas.id + '_' + index,
      JSON.parse(JSON.stringify(dataset.backgroundColor)));
  });

  chart.canvas.onclick = function(event) {
    const points = chart.getElementAtEvent(event);
    if (points.length > 0) {
      toggleDatasetHighlight(chart, points[0].datasetIndex);
    } else {
      resetAllDatasets(chart);
    }
  };
}

function toggleDatasetHighlight(chart, activeIndex) {
  chart.data.datasets.forEach((dataset, index) => {
    const key = chart.canvas.id + '_' + index;
    const original = originalColorsMap.get(key);

    if (index === activeIndex) {
      // 高亮 - 恢复原色
      dataset.backgroundColor = original;
    } else {
      // 变暗 - 降低透明度至15%
      if (Array.isArray(original)) {
        dataset.backgroundColor = original.map(c =>
          c.replace(/[\d.]+\)$/, '0.15)')
        );
      }
    }
  });
  chart.update();
}
```

### 2. 散点图实现（价格vs尺寸）

```javascript
new Chart(document.getElementById('priceScatterChart'), {
  type: 'bubble',
  data: {
    datasets: [{
      label: '吉利星愿',
      data: [{ x: 4135, y: 6.88, r: 45 }], // x=车身长度, y=价格, r=销量
      backgroundColor: 'rgba(16, 185, 129, 0.7)'
    }]
  },
  options: {
    scales: {
      x: { title: { text: '车身长度 (mm)' }, min: 3500, max: 4700 },
      y: { title: { text: '入门成交价 (万)' }, min: 4, max: 18 }
    }
  }
});
```

### 3. 使用场景数据计算

```python
# 接送孩子 (61.4%) = Almost every day + At least once a week
daily = df_child.iloc[3, 8]   # 11.7%
weekly = df_child.iloc[4, 8]   # 49.8%
child_weekly = daily + weekly # 61.4%

# 周末出行 (70.3%) = 后排搭载成人 每周至少一次
adult_daily = df_adult.iloc[3, 8]   # 6.2%
adult_weekly = df_adult.iloc[4, 8]   # 68.6%
adult_weekly_total = adult_daily + adult_weekly # 74.8%
```

## 依赖项

- Chart.js 4.x
- chartjs-plugin-datalabels
- chartjs-plugin-annotation (用于销量趋势标注)

## 最佳实践

1. **数据溯源**：每个图表必须标注 Source，说明数据来源和问卷题号
2. **交互反馈**：柱状图点击应有视觉反馈（高亮/变暗）
3. **响应式**：确保图表在移动端可读
4. **性能优化**：大量数据时使用 Chart.js 的 data sampling
5. **Accessibility**：确保颜色对比度足够，考虑色盲用户

## 扩展建议

- 添加数据导出功能（Excel/PDF）
- 支持多语言切换
- 添加数据筛选器（年份、品牌、价格区间）
- 集成实时数据更新
