# 指标卡模式(2026-07-08 新增,北京市资源剩余风格)

> **核心**: 左环形 + 右大数字 + 副标题,4 个一组的网格布局

---

## 一、布局结构

```
┌────────────────────────────┐
│ 资源剩余情况        [北京市] │  <- 标题 + 标签
├────────────────────────────┤
│ ┌──────────┐  ┌──────────┐  │
│ │ (环形图) │  │ (环形图) │  │  <- 2x2 网格
│ │  8%      │  │  34%     │  │
│ │ 机柜剩余 │  │出口带宽剩│  │
│ │ 25 台    │  │392 G     │  │
│ │ 已使用   │  │已使用    │  │
│ │ 1100G    │  │9956G     │  │
│ └──────────┘  └──────────┘  │
│ ┌──────────┐  ┌──────────┐  │
│ │ (环形图) │  │ (环形图) │  │
│ │  27%     │  │  54%     │  │
│ │IP地址剩余 │  │配电容量剩│  │
│ │ 670 个   │  │3630 KW  │  │
│ └──────────┘  └──────────┘  │
└────────────────────────────┘
```

---

## 二、配色(4 种指标,4 种主题色)

| 指标类型 | 主题色 | 适用场景 |
|---|---|---|
| **主色(蓝)** | `#5b8ff9` | 容量类 / CPU / 存储等 |
| **警示(橙)** | `#f59e0b` | 带宽 / 网络流量 / 高风险 |
| **良好(绿)** | `#22c55e` | 节能 / 利用率 / 正常状态 |
| **特殊(紫)** | `#a78bfa` | 配额 / IP地址 / 自定义 |

### 环形图配色
```js
const COLORS = {
    blue:   { main: '#5b8ff9', light: 'rgba(91,143,249,0.15)' },
    orange: { main: '#f59e0b', light: 'rgba(245,158,11,0.15)' },
    green:  { main: '#22c55e', light: 'rgba(34,197,94,0.15)' },
    purple: { main: '#a78bfa', light: 'rgba(167,139,250,0.15)' }
};
```

环形由两部分组成:
- 背景环(浅色 `light`): `#eef3fb` 灰色
- 进度弧(主色): 按百分比

---

## 三、HTML + CSS 模板

```html
<div class="indicator-card">
    <div class="indicator-header">
        <span class="title">资源剩余情况</span>
        <span class="badge">北京市</span>
    </div>
    <div class="indicator-grid">
        <div class="indicator-item">
            <div class="ring-chart" data-percent="8" data-color="orange">8%</div>
            <div class="info">
                <div class="label">机柜剩余</div>
                <div class="value">25 <span class="unit">台</span></div>
                <div class="sub">已使用 <b>1100G</b></div>
            </div>
        </div>
        <!-- 重复 3 个 indicator-item -->
    </div>
</div>
```

```css
.indicator-card {
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(143, 188, 255, 0.4);
    border-radius: 4px;
    padding: 16px 18px;
    position: relative;
    /* 四角装饰 */
    border-image: linear-gradient(135deg, #4a7bb8 0 12px, transparent 12px) 1 / 0 0 0 0;
}
.indicator-card::before, .indicator-card::after,
.indicator-card > .corner-tl, .indicator-card > .corner-tr,
.indicator-card > .corner-bl, .indicator-card > .corner-br {
    content: ''; position: absolute;
    width: 12px; height: 12px;
    border-color: #4a7bb8; border-style: solid;
}
.indicator-card::before { top: -1px; left: -1px; border-top: 2px; border-left: 2px; }
.indicator-card::after  { top: -1px; right: -1px; border-top: 2px; border-right: 2px; }
.indicator-card > .corner-bl { bottom: -1px; left: -1px; border-bottom: 2px; border-left: 2px; }
.indicator-card > .corner-br { bottom: -1px; right: -1px; border-bottom: 2px; border-right: 2px; }

.indicator-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
}
.indicator-header .title {
    font-size: 16px;
    font-weight: 700;
    color: #1e3a6e;
    padding-left: 10px;
    border-left: 3px solid #4a7bb8;
}
.indicator-header .badge {
    font-size: 12px;
    color: #fff;
    background: #4a7bb8;
    padding: 3px 10px;
    border-radius: 12px;
}

.indicator-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}

.indicator-item {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px;
    background: rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(143, 188, 255, 0.3);
    border-radius: 4px;
}

/* 环形图(用 SVG 或 ECharts gauge) */
.indicator-item .ring-chart {
    width: 60px;
    height: 60px;
    flex-shrink: 0;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 700;
    color: #1e3a6e;
    background: conic-gradient(
        var(--ring-color, #5b8ff9) calc(var(--percent, 0) * 3.6deg),
        #eef3fb 0
    );
    position: relative;
}
.indicator-item .ring-chart::before {
    content: '';
    position: absolute;
    inset: 6px;
    background: #ffffff;
    border-radius: 50%;
}
.indicator-item .ring-chart > * {
    position: relative;
    z-index: 1;
}

.indicator-item .info {
    flex: 1;
    min-width: 0;
}
.indicator-item .label {
    font-size: 13px;
    color: #6b8fc4;
    margin-bottom: 2px;
}
.indicator-item .value {
    font-size: 24px;
    font-weight: 700;
    color: #1e3a6e;
    font-family: 'Consolas', monospace;
    line-height: 1.2;
}
.indicator-item .value .unit {
    font-size: 12px;
    color: #8aa7c9;
    margin-left: 3px;
    font-weight: normal;
}
.indicator-item .sub {
    font-size: 12px;
    color: #8aa7c9;
    margin-top: 2px;
}
.indicator-item .sub b {
    color: #1e3a6e;
    font-weight: 700;
}
```

---

## 四、ECharts gauge 实现(更精确)

```js
// 4 个 gauge 图表
function createIndicatorCharts(items) {
    items.forEach(item => {
        const chart = echarts.init(document.getElementById(item.id));
        const color = COLORS[item.color];
        chart.setOption({
            series: [{
                type: 'gauge',
                radius: '90%',
                startAngle: 90,
                endAngle: -270,
                pointer: { show: false },
                progress: {
                    show: true,
                    overlap: false,
                    roundCap: true,
                    clip: false,
                    itemStyle: { color: color.main }
                },
                axisLine: { lineStyle: { width: 6, color: [[1, color.light]] } },
                splitLine: { show: false },
                axisTick: { show: false },
                axisLabel: { show: false },
                data: [{ value: item.percent }],
                title: { show: false },
                detail: {
                    valueAnimation: true,
                    fontSize: 18,
                    color: '#1e3a6e',
                    fontWeight: 700,
                    formatter: '{value}%',
                    offsetCenter: ['0%', '0%']
                }
            }]
        });
    });
}
```

---

## 五、JS 数据结构

```js
window.INDICATOR_DATA = [
    { id: 'chart-1', label: '机柜剩余', value: 25, unit: '台', percent: 8, color: 'orange', sub: { used: 1100, unit: 'G' } },
    { id: 'chart-2', label: '出口带宽剩余', value: 392, unit: 'G', percent: 34, color: 'blue', sub: { used: 9956, unit: 'G' } },
    { id: 'chart-3', label: 'IP地址剩余', value: 670, unit: '个', percent: 27, color: 'green', sub: { used: 1305200, unit: '个' } },
    { id: 'chart-4', label: '配电容量剩余', value: 3630, unit: 'KW', percent: 54, color: 'purple', sub: { used: 63889, unit: 'Q' } }
];
```

---

## 六、4 种典型场景(颜色 → 含义)

| 颜色 | 含义 | 用法 |
|---|---|---|
| 🔵 蓝 (`#5b8ff9`) | 容量 / 配额 / 资源类 | 默认 / 中性 |
| 🟠 橙 (`#f59e0b`) | 警示 / 流量 / 网络 | 偏高 / 监控类 |
| 🟢 绿 (`#22c55e`) | 良好 / 节能 / 利用率 | 健康状态 |
| 🟣 紫 (`#a78bfa`) | 特殊 / IP / 配额 | 自定义指标 |

> **核心原则**:4 种颜色固定对应 4 种语义,不要乱用(避免"绿灯"显示"危险")。

---

## 七、何时用此模式

✅ **适合**:
- 资源监控(机柜/带宽/IP/电力)
- 容量管理(配额/使用率)
- 健康度指标(系统状态)
- 4 个并排同类指标

❌ **不适合**:
- 5 个以上指标(网格会太挤)
- 不同维度指标(用仪表盘各自独立)
- 需要历史趋势(用 line chart)

---

## 八、与其他模式对比

| 模式 | 用途 | 大小 |
|---|---|---|
| **指标卡(本文)** | 4 资源剩余 / 容量监控 | 2x2 网格 |
| 单大数字 + sparkline | 1 主指标 + 趋势 | 单卡 |
| 环形图 + 文字 | 1 占比 + 文字 | 单卡 |
| 柱状图 | 多项对比 | 整图 |

---

## 九、变体

### 1. 6 个指标(3x2 网格)
```css
.indicator-grid { grid-template-columns: 1fr 1fr 1fr; }
```

### 2. 大数字 + 副数字(无环)
```html
<div class="info">
    <div class="value">7,366,789 <span class="unit">MWH</span></div>
    <div class="sub">较昨日 +1.2% ↑</div>
</div>
```

### 3. 环形图 + 多指标(单卡 3 项)
```html
<div class="indicator-item vertical">
    <div class="ring-chart">75%</div>
    <div class="info">
        <div class="metric">CPU <b>75%</b></div>
        <div class="metric">内存 <b>60%</b></div>
        <div class="metric">磁盘 <b>40%</b></div>
    </div>
</div>
```

---

## 十、避坑

- ❌ **不要用 5+ 颜色**(4 色已固定语义,多了乱)
- ❌ **不要把"剩余"和"使用"用同色**(语义要区分)
- ❌ **不要副文字比主数字更显眼**(信息层级要清晰)
- ❌ **不要"已使用"用红色**(已使用是中性,警示色留给异常)
- ❌ **不要单位混乱**(`台 / 个 / KW / G`)— 风格要统一

---

## 十一、参考图归档

| 文件 | 路径 | 描述 |
|---|---|---|
| 用户原图 | `/workspace/attachments/` | 资源剩余情况 - 北京市 |
| 关键特征 | 浅蓝渐变 + 4 色指标 + 环形图 + 数字 | 4 指标横向排列,2x2 网格 |
| 配色比例 | 蓝 30% + 橙 25% + 绿 25% + 紫 20% | 4 色平衡(不是 60/30/10) |

> 注:指标卡场景的 4 色配色**不适用**整个大屏的 60/30/10 原则。指标卡内部的 4 色是 4 个并列指标,各占 25%,允许。
> 整体大屏的配色仍然遵循 60/30/10。