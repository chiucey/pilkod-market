# 案例研究: 北京市 IDC 数量分布大屏(2026-07-08 抽取)

> **来源**: 用户提供的 zip 案例,北京市"运维支撑系统"大屏(运营管理类)

---

## 一、案例总览

```
+--------------------------------------------------------+
|  运维支撑系统 首页/流量管理/运维分析/三维可视化  时间  |
+--------+----------------------------------+-----------+
| IDC 总 |  北京市IDC数量分布               | 资源剩余情况|
| 数 29   |                                  | 4 卡片 2x2 |
| 园区18  |     [北京市地图]                +-----------+
| 传统 8  |                                  | 客户流量分析|
| 合作 3  |     数字气泡 (区编号)            | 6 指标+柱状图|
| 楼栋23  |                                  +-----------+
| 机房86  |     [hover popup: 客户 TOP3]     | 网络质量分析|
| 货架293 |                                  | 表格+状态条  |
| 带宽1350|                                  |            |
| IP池2480|                                  |            |
+--------+----------------------------------+-----------+
```

**关键观察**:
- **三栏布局**(沿用 360/1fr/360)
- **中国地图 → 改成了北京市地图**(更聚焦)
- **底部没有 tab**(单页 dashboard,顶部 nav 切换)
- 主题: **运营商 / 政企管理**类大屏

---

## 二、配色设计(实测采样)

### 2.1 基础配色
```css
--bg-primary: #ffffff;
--bg-gradient: linear-gradient(180deg, #f8fbff 0%, #e8f1fa 50%, #ffffff 100%);
--panel-bg: rgba(255, 255, 255, 0.78);
--panel-border: rgba(143, 188, 255, 0.4);
--text-primary: #1e3a6e;
--text-secondary: #3a5a8c;
--text-muted: #6b8fc4;
--text-faint: #8aa7c9;
--accent: #4a7bb8;
--accent-light: #8fbcff;
```

### 2.2 客户品牌色(流量分析独有)

| 品牌 | 颜色 | HEX | 场景 |
|---|---|---|---|
| 美团 | 橙 | `#ff5722` / `#ff6600` | 客户流量排名 |
| IQIYI | 绿 | `#00be06` / `#22c55e` | 爱奇艺 |
| 小米 | 橙红 | `#ff5722` | 客户流量 |
| 百度 | 蓝 | `#2932e1` | 流量 |
| 阿里 | 橙 | `#ff6a00` | 淘宝 |
| 字节 | 红 | `#1d63ff` | 抖音 |

**关键洞察**: 客户/品牌相关的图表,**用品牌色**而不是统一蓝,让"美团/IQIYI/小米"一眼可辨。

```js
const BRAND_COLORS = {
    '美团': '#ff5722',
    'IQIYI': '#00be06',
    '小米': '#ff5722',
    '百度': '#2932e1',
    '阿里': '#ff6a00',
    '字节': '#1d63ff',
    '腾讯': '#00a4ff',
    '京东': '#e1251b'
};
```

### 2.3 4 种状态色
```css
--success: #4ade80;  /* 绿 - 正常/良好 */
--warning: #f59e0b;  /* 橙 - 警示 */
--danger:  #f87171;  /* 红 - 危险 */
--info:    #5b8ff9;  /* 蓝 - 信息/中性 */
```

---

## 三、统计图表展示方式(9 种新模式)

### 3.1 **运维指标列表**(左侧栏)

**结构**: 垂直堆叠的指标项,每项:
- 左侧: 小图标(圆角矩形 + SVG)
- 中间: 数字 + 单位
- 右侧: 趋势箭头(绿色 ↑ 表示增长)

```html
<div class="metric-row">
    <div class="icon icon-building">🏢</div>
    <div class="info">
        <div class="label">楼栋总数</div>
        <div class="value">23 <span class="unit">处</span> <span class="trend up">↑</span></div>
    </div>
</div>
```

```css
.metric-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid rgba(143, 188, 255, 0.15);
}
.metric-row .icon {
    width: 32px; height: 32px;
    border-radius: 6px;
    background: linear-gradient(135deg, #5b8ff9, #4a7bb8);
    color: #fff;
    display: flex; align-items: center; justify-content: center;
}
.metric-row .value {
    font-size: 18px;
    font-weight: 700;
    color: #1e3a6e;
    font-family: 'Consolas', monospace;
}
.metric-row .value .unit {
    font-size: 11px;
    color: #8aa7c9;
    margin-left: 3px;
    font-weight: normal;
}
.metric-row .value .trend {
    font-size: 11px;
    color: #4ade80;  /* 绿 */
    margin-left: 4px;
    font-weight: 700;
}
```

### 3.2 **3-分类小柱**(园区化/传统/合作 IDC)

**结构**: 同一指标下,3 个分类用横向小条 + 数字
```html
<div class="metric-row">
    <div class="icon icon-building">🏢</div>
    <div class="info">
        <div class="label">IDC 总数 <b>29</b> 个 <span class="trend">↑</span></div>
        <div class="breakdown">
            <div class="item"><span class="dot blue"></span>园区化 IDC <b>18</b> 个</div>
            <div class="item"><span class="dot orange"></span>传统机楼 IDC <b>8</b> 个</div>
            <div class="item"><span class="dot green"></span>合作 IDC <b>3</b> 个</div>
        </div>
    </div>
</div>
```

```css
.breakdown { display: flex; gap: 16px; margin-top: 4px; }
.breakdown .item { font-size: 12px; color: #6b8fc4; }
.breakdown .item b { color: #1e3a6e; font-weight: 700; }
.breakdown .dot {
    display: inline-block; width: 8px; height: 8px;
    border-radius: 50%; margin-right: 4px;
    vertical-align: middle;
}
.breakdown .dot.blue   { background: #5b8ff9; }
.breakdown .dot.orange { background: #f59e0b; }
.breakdown .dot.green  { background: #4ade80; }
```

### 3.3 **数字气泡 + 地图**(中间)

**结构**: 地图每个区/县上画一个圆形数字气泡(区编号 1-9)
```js
{
    type: 'effectScatter',
    coordinateSystem: 'geo',
    data: [
        { name: '海淀区', value: [116.31, 39.96, 1] },  // 数字 1
        { name: '朝阳区', value: [116.48, 39.92, 1] },
        // ...
    ],
    symbolSize: 28,
    itemStyle: {
        color: '#5b8ff9',
        borderColor: '#fff',
        borderWidth: 2,
        shadowBlur: 8
    },
    label: {
        show: true,
        formatter: '{b}',  // 显示区名
        color: '#fff',
        fontWeight: 700
    }
}
```

### 3.4 **hover popup + 品牌色排名**(地图交互)

**结构**: 点击地图某区,弹出 popup 显示 TOP3 客户(品牌色)
```js
chart.on('click', params => {
    if (params.componentType === 'series' && params.seriesType === 'map') {
        showPopup({
            title: '客户流量分析',
            badge: '北京市',
            top3: [
                { brand: '美团', color: '#ff5722', value: '365 GB', percent: '33.2%' },
                { brand: 'IQIYI', color: '#00be06', value: '191 GB', percent: '17.4%' },
                { brand: '小米', color: '#ff5722', value: '191 GB', percent: '17.4%' }
            ]
        });
    }
});
```

### 3.5 **TOP10 排名 + 品牌色柱状图**(流量排名)

**结构**: 横向柱状图,每条柱用品牌色
```js
{
    type: 'bar',
    data: [
        { value: 64, itemStyle: { color: '#5b8ff9' } },   // 百度
        { value: 56, itemStyle: { color: '#00be06' } },   // IQIYI
        { value: 48, itemStyle: { color: '#ff5722' } },   // 美团
        // ...
    ],
    barWidth: 8,
    itemStyle: { borderRadius: [0, 4, 4, 0] }
}
```

### 3.6 **网络质量分析表**(带状态条)

**结构**: 表格每行:排名/区名/状态条(横向条形)/TOP5 客户数/平均时延
```html
<tr>
    <td class="rank">1</td>
    <td>海淀区</td>
    <td class="bar-cell">
        <div class="bar" style="width: 100%"></div>
    </td>
    <td>5</td>
    <td>0.64s</td>
</tr>
```

```css
.bar-cell { padding: 4px 0; }
.bar-cell .bar {
    height: 6px;
    background: linear-gradient(90deg, #5b8ff9, #8fbcff);
    border-radius: 3px;
    box-shadow: 0 0 6px rgba(91, 143, 249, 0.4);
}
```

### 3.7 **环形百分比 + 数字**(资源剩余 4 卡片)

(已在 `templates/indicator-card.md` 详细记录)

### 3.8 **顶部 nav + tab 切换**

```html
<nav class="top-nav">
    <div class="logo">运维支撑系统</div>
    <div class="nav-tabs">
        <a class="tab active">首页</a>
        <a class="tab">流量管理</a>
        <a class="tab">运维分析</a>
        <a class="tab">三维可视化呈现</a>
    </div>
    <div class="right">
        <span class="time">03:23:18</span>
        <span class="weather">5°C</span>
    </div>
</nav>
```

```css
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    height: 80px;
}
.nav-tab {
    padding: 8px 20px;
    color: #6b8fc4;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
}
.nav-tab.active {
    color: #1e3a6e;
    font-weight: 700;
    border-bottom: 2px solid #5b8ff9;
}
```

### 3.9 **天气/温度小部件**(右上)

```html
<div class="weather-widget">
    <span class="icon">☀</span>
    <span class="temp">5°C</span>
</div>
```

```css
.weather-widget {
    background: rgba(91, 143, 249, 0.1);
    border: 1px solid rgba(91, 143, 249, 0.3);
    border-radius: 20px;
    padding: 6px 14px;
    color: #4a7bb8;
    font-size: 14px;
}
```

---

## 四、自适配屏幕分辨率(实测验证)

| 视口 | --scale | 行为 |
|---|---|---|
| 1366×768 | 0.71 | 整体缩放到 71% |
| 1920×1080 | 1.0 | 原始尺寸 |
| 2560×1440 | 1.33 | 放大到 133% |
| **3840×2160** | **2.0** | **200% 缩放(系统 DPI 场景)** |

**实现方式**:与 `Fyc_Software_Design` 技能默认一致(1920×1080 + transform scale)
```css
#app {
    width: 1920px; height: 1080px;
    position: absolute; left: 50%; top: 50%;
    transform-origin: center center;
    transform: translate(-50%, -50%) scale(var(--scale, 1));
}
```
```js
window.addEventListener('resize', () => {
    const s = Math.min(innerWidth/1920, innerHeight/1080);
    document.documentElement.style.setProperty('--scale', s);
});
```

**关键**: 1920×1080 设计 + transform scale,**无需 vw/vh 重写**,系统 200% 缩放自动适配。

---

## 五、本案例与默认模板的差异

| 项 | 默认(FYC v1.5) | 本案例(运维) |
|---|---|---|
| 配色 | cream 奶油白 | cream 偏冷白 |
| 地图 | 中国全国 | 北京市 |
| 顶部 | 标题 + 时间 | nav tabs + 时间 + 天气 |
| 8 大图表 | 标准模板 | 9+ 多种(图标列表/分类小柱/品牌色柱/状态条等) |
| 客户标识 | 无 | **品牌色**识别(美团橙/IQIYI 绿) |
| 数字气泡 | 4 个高优 | 每个区编号(海淀区=1) |
| popup | 跑马灯 | 客户流量 popup |
| 底部 tab | 浮在地图 | 无(顶部 nav) |

**核心模式可复用,具体数据/配色按业务调整**。

---

## 六、关键经验沉淀

### 6.1 品牌色识别
**任何展示客户/品牌/合作方的图表,用对方品牌色**,不要统一蓝。
- 美团 → 橙
- 阿里 → 橙
- 百度 → 蓝
- 腾讯 → 蓝
- 字节 → 红
- IQIYI → 绿
- 小米 → 橙红
- 京东 → 红

**实现**:
```js
const BRAND = {
    '美团': '#ff5722', 'IQIYI': '#00be06',
    '百度': '#2932e1', '阿里': '#ff6a00',
    // ...
};
data.forEach(item => {
    item.itemStyle = { color: BRAND[item.name] || '#5b8ff9' };
});
```

### 6.2 数字气泡的层级
地图上"数字气泡"分 3 类:
1. **省份编号**(1-9):表示该区有几个客户
2. **数据值**(1234):直接显示数值
3. **百分比**(80%):表示进度

```js
// 用 formatter 区分
label: {
    formatter: params => {
        const type = params.data.type || 'value';
        if (type === 'index') return params.value[2];  // 编号
        if (type === 'percent') return params.value[2] + '%';
        return params.value[2].toLocaleString();
    }
}
```

### 6.3 顶部 nav vs 底部 tab
- **多页面 dashboard**:用顶部 nav(更专业,适合运营/管理场景)
- **单页面监控**:用底部 tab(更聚焦,适合监控场景)
- 用户明确"类似软件界面"用顶部 nav

### 6.4 数字 + 趋势箭头
运维场景的"数字"几乎都带"同比/环比"趋势箭头:
- ↑ 绿色(增长/正常)
- ↓ 红色(下降/异常)
- — 灰色(平稳)

```html
<div class="value">86 <span class="unit">个</span> <span class="trend up">↑</span></div>
```

### 6.5 hover popup 模式
地图上点击区/点 → 弹出 popup:
- 标题 + 徽章("北京市"蓝色徽章)
- TOP3 客户列表(品牌色)
- "查看 X" 链接(看更多)

```js
function showPopup({ title, badge, top3, link }) {
    const popup = document.createElement('div');
    popup.className = 'map-popup';
    popup.innerHTML = `
        <div class="popup-header">
            <span class="title">${title}</span>
            <span class="badge">${badge}</span>
        </div>
        <div class="popup-top3">
            ${top3.map(t => `
                <div class="brand-item">
                    <span class="logo" style="background:${t.color}">${t.brand[0]}</span>
                    <span class="name">${t.brand}</span>
                    <span class="value">${t.value}</span>
                    <span class="percent">${t.percent}</span>
                </div>
            `).join('')}
        </div>
        <a class="popup-link">${link} ›</a>
    `;
    document.body.appendChild(popup);
}
```

---

## 七、可直接复用的代码片段

### 7.1 9 种新图表快速索引

| 模式 | 文件 | 用途 |
|---|---|---|
| 运维指标列表 | `templates/ops-metric-row.html` | 左侧/右栏的"数字+单位+趋势"项 |
| 3 分类小柱 | `templates/breakdown.html` | "IDC 总数 29 / 园区 18 / 传统 8 / 合作 3" |
| 数字气泡(地图) | `assets/js/effectScatter-bubble.js` | 北京市区编号 |
| hover popup | `assets/js/map-popup.js` | 客户流量分析弹窗 |
| 品牌色柱状 | `templates/brand-color-bar.js` | TOP10 客户排名 |
| 状态条 | `templates/status-bar.html` | 网络质量表格里的进度条 |
| 顶部 nav | `templates/top-nav.html` | 多 tab 切换 |
| 天气小部件 | `templates/weather.html` | 右上角 |
| 指标卡 4 色 | `templates/indicator-card.md` | 已存在 |

### 7.2 配色速查
```js
const COLORS = {
    // 基础
    blue:   '#5b8ff9',
    orange: '#f59e0b',
    green:  '#4ade80',
    purple: '#a78bfa',
    red:    '#f87171',
    
    // 品牌
    meituan: '#ff5722',
    iqiyi:   '#00be06',
    baidu:   '#2932e1',
    alibaba: '#ff6a00',
    bytedance: '#1d63ff',
    tencent: '#00a4ff',
    jd:      '#e1251b',
    xiaomi:  '#ff5722',
    
    // 状态
    success: '#4ade80',
    warning: '#f59e0b',
    danger:  '#f87171',
    info:    '#5b8ff9'
};
```

---

## 八、参考图归档

| 文件 | 路径 |
|---|---|
| 案例 zip | `/workspace/attachments/24032535__40b68543-235e-4afd-839d-bb6498e12037.zip` |
| 实测截图 | `/tmp/cs_png/cs-1920x1080.png` (等) |
| 案例代码 | `assets/` `css/` `js/` `index.html` |

**关键截图时间**: 2026-07-08 03:23
**采样工具**: Playwright + Chromium 1920×1080/1366×768/2560×1440/3840×2160

---

## 九、给后续项目的指引

1. **新大屏 = cream 模板 + 本案例模式按需挑选**
2. **是否需要顶部 nav** vs **底部 tab**:
   - 单页监控 → 底部 tab(本技能默认)
   - 多页 dashboard → 顶部 nav(运维/政企场景)
3. **是否需要品牌色**:
   - 客户/品牌相关 → 品牌色
   - 系统/容量类 → 主色蓝
4. **是否需要 popup**:
   - 地图交互密集 → popup(点击查 TOP3)
   - 简单展示 → tooltip 即可

5. **8 大图表模块补充**:
   - 已有 8 个 + 案例新增 9 种新模式(运维列表 / 分类小柱 / 品牌色 / 状态条 / 天气等)
   - 总共 17 种可复用模式,按需裁剪

---

