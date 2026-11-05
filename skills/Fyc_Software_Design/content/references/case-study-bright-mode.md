# 案例研究: B 端应用门户配色风格(亮色活力版, 2026-10-14 抽取)

> **来源**: 4 张参考图(General statistics / 大数据可视化分享·浅色系 / 采购大数据监控平台 / 智能体中心)
> **定位**: 不只做大屏, 还要做"应用门户 / B 端管理后台 / 业务监控首页"
> **核心**: 5 色 brand 渐变 + 胶囊按钮 + 多色 KPI 大卡 + 白底圆角 UI

---

## 一、4 张图一览

| # | 名称 | 主题 | 关键特征 |
|---|---|---|---|
| 1 | General statistics | 运营总览 | 浅蓝白 + 蜂窝背景 + 5 色 brand + 城市数据气泡 |
| 2 | 大数据可视化分享·浅色系 | 设计分享 | 渐变浅蓝绿 + 胶囊 tab + 云朵装饰 + 多面板网格 |
| 3 | 采购大数据监控平台 | B 端业务 | 顶部波浪 + 4 大色卡 + 环形大数 + 排名表 |
| 4 | 智能体中心 | B 端门户 | 蓝渐变 navbar + 侧边栏 + 6 应用卡 + 状态徽章 |

**共同点(提炼)**:
- 浅色基调(白 / 浅蓝白 / 极淡蓝)
- **5 色 brand 渐变** 是核心(紫 / 橙 / 绿 / 青 / 黄)
- 圆角组件(border-radius: 8-24px)
- 胶囊形按钮(高度 40-56px, 圆角 9999px)
- 大图标(32-48px) + 白底圆角图标容器
- 状态徽章(热门/推荐/新/高级/管理)

---

## 二、第 4 档配色主题(2026-10-14 新增,后扩到 9 档)

### 2.1 主题命名(9 档)
- **原 3 档**: cream(奶油白) / dark-tech(深色科技蓝) / light-blue(淡蓝)
- **🆕 第 4 档**: **bright-portal**(B 端应用门户·亮色活力版)
- **🆕 2026-10-14 扩展到 9 档**(按 3×3 九宫格分布):
  - 第 5 档: **green-fresh**(单色绿·清新,医疗/环保/农业)
  - 第 6 档: **orange-energy**(单色橙·活力,销售/电商/营销)
  - 第 7 档: **purple-elegant**(单色紫·优雅,金融/律所/高端)
  - 第 8 档: **pink-creative**(单色粉·创意,内容/媒体/娱乐)
  - 第 9 档: **dark-portal**(5 色·深底,科技产品/夜间模式)

→ 9 张 SVG 预览见 `templates/theme-preview.html`

### 2.2 色板(CSS 变量)
```css
:root {
    /* 中性色(60% - 底色/文字/面板) */
    --bg-page:    linear-gradient(180deg, #F5F8FE 0%, #FFFFFF 100%);
    --bg-section: #FFFFFF;
    --bg-card:    rgba(255, 255, 255, 0.78);
    --border-soft: rgba(15, 23, 42, 0.06);
    --text-primary:   #0F172A;
    --text-secondary: #475569;
    --text-muted:     #94A3B8;
    
    /* 5 色 brand(每色 30% / 10% 强调) */
    --brand-purple: #7C3AED;
    --brand-orange: #F97316;
    --brand-green:  #10B981;
    --brand-cyan:   #06B6D4;
    --brand-yellow: #F59E0B;
    
    /* 5 色渐变(用于按钮/卡片) */
    --grad-purple: linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%);
    --grad-orange: linear-gradient(135deg, #F97316 0%, #FDBA74 100%);
    --grad-green:  linear-gradient(135deg, #10B981 0%, #6EE7B7 100%);
    --grad-cyan:   linear-gradient(135deg, #06B6D4 0%, #67E8F9 100%);
    --grad-yellow: linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%);
    
    /* 阴影 */
    --shadow-card: 0 4px 24px rgba(15, 23, 42, 0.04);
    --shadow-pop:  0 8px 32px rgba(15, 23, 42, 0.08);
}
```

### 2.3 何时用 bright-portal vs cream
| 场景 | 推荐主题 |
|---|---|
| 业务监控大屏(单屏驾驶舱) | **cream** |
| 数据中心/IT 监控(深色仪表盘) | dark-tech |
| 浅色能源/工业监控 | light-blue |
| **B 端应用门户**(多入口/多应用) | **🆕 bright-portal** |
| **B 端管理首页**(运营/采购/HR) | **🆕 bright-portal** |
| **业务大屏带 KPI 大卡**(4 色块) | **🆕 bright-portal** |

---

## 三、9 种新 UI 模式(2026-10-14 抽取)

### 3.1 **蜂窝背景图案**(图 1)
```html
<div class="bg-honeycomb"></div>
```
```css
.bg-honeycomb {
    position: absolute; inset: 0;
    background-color: #F5F8FE;
    background-image:
        radial-gradient(circle at 20% 20%, #C7D2FE 0%, transparent 50%),
        radial-gradient(circle at 80% 60%, #BAE6FD 0%, transparent 50%);
    overflow: hidden;
}
.bg-honeycomb::before {
    content: '';
    position: absolute; inset: 0;
    /* 蜂窝 SVG 内联 */
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='60' height='52' viewBox='0 0 60 52'><path d='M30 0l25.98 15v22L30 52 4.02 37V15z' fill='none' stroke='%23CBD5E1' stroke-width='0.5' opacity='0.3'/></svg>");
    background-size: 60px 52px;
    opacity: 0.6;
}
```

### 3.2 **顶部波浪装饰**(图 3)
```html
<svg class="bg-wave" viewBox="0 0 1920 120" preserveAspectRatio="none">
    <path d="M0,60 Q480,10 960,60 T1920,60 L1920,0 L0,0 Z" fill="#E0F2FE"/>
</svg>
```
```css
.bg-wave {
    position: absolute; top: 0; left: 0; right: 0;
    height: 120px; z-index: 0;
    pointer-events: none;
}
```

### 3.3 **胶囊形渐变按钮**(5 色 × 3 尺寸)
详见 `templates/capsule-buttons.md`, 含完整代码。

```html
<button class="btn btn-purple btn-md">智能咨询</button>
<button class="btn btn-orange btn-lg">立即试用</button>
```

### 3.4 **大色块 KPI 卡**(图 3)
**结构**: 圆角矩形 + 渐变填充 + 左上小图标 + 大数字 + 单位 + 描述
```html
<div class="kpi-card kpi-orange">
    <div class="kpi-icon">📋</div>
    <div class="kpi-meta">当月项目数量</div>
    <div class="kpi-value">39,028</div>
    <div class="kpi-spark">↑ 12.3%</div>
</div>
```
```css
.kpi-card {
    border-radius: 16px;
    padding: 24px;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-card);
}
.kpi-orange { background: linear-gradient(135deg, #F97316 0%, #FB923C 100%); }
.kpi-blue   { background: linear-gradient(135deg, #4A8BFF 0%, #7BA8FF 100%); }
.kpi-cyan   { background: linear-gradient(135deg, #06B6D4 0%, #67E8F9 100%); }
.kpi-green  { background: linear-gradient(135deg, #10B981 0%, #6EE7B7 100%); }
.kpi-value {
    font-size: 38px;
    font-weight: 800;
    margin: 12px 0 4px;
    line-height: 1;
}
.kpi-icon {
    position: absolute; top: 20px; right: 20px;
    width: 40px; height: 40px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
}
```

### 3.5 **环形大数卡**(图 3 中心)
**结构**: 中心大数字 + 外环进度 + 上下小字
```html
<div class="ring-card">
    <div class="ring-text">供应商总数</div>
    <div class="ring-canvas" id="ring1"></div>
    <div class="ring-stat">
        <div class="item">合格供应商 <b>17818</b> <span class="badge">34%</span></div>
        <div class="item">合格供应商 <b>17818</b> <span class="badge">34%</span></div>
    </div>
</div>
```
```js
// ECharts 半环
echarts.init(document.getElementById('ring1')).setOption({
    series: [{
        type: 'gauge',
        startAngle: 200, endAngle: -20,
        min: 0, max: 100,
        axisLine: { lineStyle: { width: 16, color: [[1, '#06B6D4']] } },
        progress: { show: true, width: 16 },
        axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false },
        pointer: { show: false },
        anchor: { show: false },
        title: { show: false },
        detail: { valueAnimation: true, fontSize: 48, color: '#0F172A', fontWeight: 800, formatter: '{value}', offsetCenter: [0, '-5%'] },
        data: [{ value: 34 }]
    }]
});
```

### 3.6 **应用门户卡片网格**(图 4)
**结构**: 6 张卡 + 圆角大图标 + 状态徽章 + 统计
```html
<a class="app-card" href="#/consult">
    <div class="app-icon"><svg>...</svg></div>
    <div class="app-title">智能咨询</div>
    <div class="app-desc">基于知识库的快速回答, 引用可溯源</div>
    <div class="app-meta">
        <span class="badge badge-hot">热门</span>
        <span class="app-stat">1,283 次使用</span>
    </div>
</a>
```
```css
.app-card {
    background: var(--bg-card);
    border: 1px solid var(--border-soft);
    border-radius: 12px;
    padding: 24px;
    transition: all 0.2s;
}
.app-card:hover {
    border-color: var(--brand-blue);
    box-shadow: var(--shadow-pop);
    transform: translateY(-2px);
}
.app-icon {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, #4A8BFF, #7BA8FF);
    border-radius: 12px;
    color: white;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 16px;
}
```

### 3.7 **状态徽章**(5 状态)
```html
<span class="badge badge-hot">热门</span>     <!-- 1,283 次使用 -->
<span class="badge badge-recommend">推荐</span> <!-- 856 次使用 -->
<span class="badge badge-new">新</span>        <!-- 124 次使用 -->
<span class="badge badge-advanced">高级</span> <!-- 567 次使用 -->
<span class="badge badge-manage">管理</span>   <!-- 2,341 文档 -->
```
```css
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
}
.badge-hot       { background: #FEF3C7; color: #F59E0B; }
.badge-recommend { background: #DBEAFE; color: #4A8BFF; }
.badge-new       { background: #D1FAE5; color: #10B981; }
.badge-advanced  { background: #FFEDD5; color: #F97316; }
.badge-manage    { background: #FEF3C7; color: #CA8A04; }
```

### 3.8 **侧边栏图标导航**(图 4)
```html
<aside class="sidebar">
    <a class="side-item active">
        <span class="side-icon">💬</span>
        <span class="side-label">智能咨询</span>
    </a>
    <a class="side-item">
        <span class="side-icon">📋</span>
        <span class="side-label">政策解读</span>
    </a>
</aside>
```
```css
.sidebar {
    width: 200px;
    background: white;
    border-right: 1px solid var(--border-soft);
    padding: 16px 8px;
}
.side-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px;
    border-radius: 10px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.15s;
}
.side-item:hover { background: #F1F5F9; color: var(--text-primary); }
.side-item.active {
    background: linear-gradient(90deg, #DBEAFE 0%, transparent 100%);
    color: #4A8BFF;
    font-weight: 600;
    border-left: 3px solid #4A8BFF;
}
```

### 3.9 **数据气泡·白底圆角**(图 1 城市标签)
```html
<div class="city-bubble">
    <div class="city-icon" style="background:#7C3AED">🏛️</div>
    <div class="city-info">
        <div class="city-name">Toronto</div>
        <div class="city-value">53,430,001</div>
    </div>
</div>
```
```css
.city-bubble {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 12px;
    background: white;
    border-radius: 9999px;
    box-shadow: var(--shadow-pop);
}
.city-icon {
    width: 24px; height: 24px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px;
    color: white;
}
```

---

## 四、Top 10 经验沉淀

### 4.1 5 色 brand 优于 1 色主导
**单色主导** 适合严肃场景(大屏/监控), **5 色渐变** 适合应用门户/管理后台(活力/多业务并行)

### 4.2 胶囊按钮 3 尺寸规范
- `btn-sm` 32px (表格内/次要操作)
- `btn-md` 40px (普通按钮, 默认)
- `btn-lg` 48px (主操作/CTA)
- `btn-xl` 56px (登录按钮/首屏 CTA)

### 4.3 渐变按钮的 3 个隐性要求
- 圆角 9999px (胶囊)
- 白字 + font-weight: 600
- 阴影用同色系 rgba, 例如 `box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3)`

### 4.4 大色块 KPI 卡 vs 圆环 KPI 卡
- **大色块**: 4 个不同色, 用于"分类明确"场景(订单/支付/退款/咨询)
- **圆环 KPI**: 同色渐变, 用于"单一指标"场景(总用户数/总销售额)

### 4.5 状态徽章的 5 种语义
| 状态 | 颜色 | 适用 |
|---|---|---|
| 热门 | 黄 | 用户量 > 1000 |
| 推荐 | 蓝 | 系统推荐/编辑精选 |
| 新 | 绿 | 上线 < 30 天 |
| 高级 | 橙 | 付费功能/企业版 |
| 管理 | 暗黄 | 后台配置类 |

### 4.6 应用门户的导航层级
- **一级**: 顶部 navbar(系统名 + 全局操作)
- **二级**: 左侧 sidebar(模块分组, 5-8 项)
- **三级**: 卡片网格(具体应用, 5-6 张)
- **四级**: 详情页(具体功能)

### 4.7 蜂窝/几何背景的取舍
- 适合**大屏背景**, 表达"数据海洋/科技感"
- 不适合**应用门户**背景(干扰阅读, 用纯白 + 极淡蓝渐变)

### 4.8 顶部波浪装饰
- 适合大屏**首屏 hero 区**或**门户欢迎页**
- 高度 80-120px, 1-2 条 curve 即可, 不要堆叠

### 4.9 圆环大数卡 1 vs 4
- **1 个**大圆环: 中心数字突出
- **4 个**小圆环: 多指标并排
- 数据少用 1, 数据多用 4

### 4.10 浅色活力版的"克制"
- 5 色用全, 但**单屏只用 2-3 色** (主 + 辅)
- 留白要够, 卡片间距 16-24px
- 字体仍然要保持 14-16px, 数字 32-48px
- 不要堆渐变(超过 3 个会让界面花)

---

## 五、配色 vs 场景速查

| 业务类型 | 推荐主题 | 关键色 |
|---|---|---|
| 监控大屏(单屏) | cream | 1 色蓝主导 |
| 数据中心深色 | dark-tech | 1 色蓝+深色 |
| 工业能源 | light-blue | 1 色蓝+淡蓝 |
| **应用门户** | **bright-portal** | **5 色渐变** |
| **B 端管理首页** | **bright-portal** | **5 色渐变** |
| **业务大屏带 KPI** | **bright-portal** | **5 色渐变** |
| 金融/政企 | light-blue | 1 色蓝, 偏严肃 |
| 互联网产品 | **bright-portal** | **5 色, 活力** |

---

## 六、参考图源

| 图 | 场景 |
|---|---|
| 图 1 | 运营总览(英文, 蜂窝背景, 5 色 brand) |
| 图 2 | 大数据可视化分享·浅色系(中文, 渐变蓝绿, 胶囊 tab) |
| 图 3 | 采购大数据监控平台(中文, 顶部波浪, 4 大色卡) |
| 图 4 | 智能体中心(中文, 蓝渐变 navbar, 6 应用卡) |

**关键发现**: 4 张图共同指向「**B 端应用门户**」设计语言——不是单纯大屏, 是"**多应用聚合 + 业务运营首页**"。

---

## 七、给后续项目的指引

1. **新项目先问类型**:
   - "做大屏(单屏监控)" → cream
   - "做应用门户(多入口)" → **bright-portal** 🆕
   - "做管理后台首页" → **bright-portal** 🆕
   - "做数据中心" → dark-tech

2. **bright-portal 必备元素**:
   - 顶部 navbar 蓝渐变
   - 5 色胶囊按钮(尺寸 40/48/56)
   - 4 大色块 KPI 卡
   - 应用卡 + 状态徽章
   - 侧边栏图标导航

3. **避免错误**:
   - 不要在 cream 主题里混用 5 色 brand (破坏严肃感)
   - 不要在 bright-portal 主题里全用单色 (失去活力)
   - 不要把 cream 的"奶油白渐变" 套到 bright-portal (背景风格不同)

4. **可复用**:
   - 5 色按钮 / 5 色徽章 / 5 色 KPI 卡 = 完整组件库
   - 顶部 navbar / 侧边栏 = B 端骨架
   - 4 大色卡 = 4 大类业务分类(订单/支付/用户/产品)
---

## 十一、9 套配色方案(每套严格 4 色 + 色彩理论协调,2026-10-14)

**核心原则**: 4 色 = **主色 + 辅色 + 背景 + 文字**,36 色色板,5 种色彩理论,严格不超 4 色。

### 11.1 5 种色彩理论速查

| 理论 | 原理 | 视觉感受 | 适用 |
|---|---|---|---|
| **单色 Monochromatic** | 同色相不同明度饱和度 | 极致协调, 不会出错 | 严肃/金融/政企 |
| **互补 Complementary** | 色环 180° 对比 | 强对比, 重点突出 | KPI/营销/重点突出 |
| **类比 Analogous** | 色环相邻 30° 内 | 温和自然, 视觉舒适 | 同一色系主题 |
| **三元 Triadic** | 色环等距 120° | 平衡丰富 | 多元业务并重 |
| **分裂补 Split-Complement** | 主色 + 补色相邻两色 | 强对比但不刺眼 | 科技/极客 |

### 11.2 9 套配色速查(36 色色板, 全部浅底色)

| # | 主题名 | 理论 | 来源图 | 背景 | 主色 | 辅色 | 文字 | 适合 |
|---|---|---|---|---|---|---|---|---|
| 1 | **mono-blue**(默认) | 单色 | — | `#F0F9FF` | `#0284C7` | `#BAE6FD` | `#0C4A6E` | 业务监控 |
| 2 | mono-sky | 单色 | — | `#F0F9FF` | `#0EA5E9` | `#E0F2FE` | `#0C4A6E` | 政企金融 |
| 3 | blue-orange | 互补 | — | `#F0F9FF` | `#0284C7` | `#F97316` | `#0F172A` | 应用门户 |
| 4 | **cyan-blue** | 互补 | 📷 图1 | `#ECFEFF` | `#06B6D4` | `#0284C7` | `#164E63` | 运营总览 |
| 5 | green-cyan | 类比 | — | `#F0FDF4` | `#10B981` | `#0EA5E9` | `#064E3B` | 医疗环保 |
| 6 | warm-amber | 类比 | — | `#FFFBEB` | `#F97316` | `#F59E0B` | `#7C2D12` | 销售营销 |
| 7 | **portal-mint** | 类比 | 📷 图2 | `#F0FDFA` | `#14B8A6` | `#0EA5E9` | `#134E4A` | 数据分享 |
| 8 | **portal-bright** | 混合 | 📷 图3 | `#F0F9FF` | `#4A8BFF` | `#10B981` | `#0F172A` | 采购大屏 |
| 9 | **gold-bright** | 类比 | 📷 图1 | `#FEFCE8` | `#F59E0B` | `#10B981` | `#0F172A` | 业务总览 |

**剔除的 5 套**(用户反馈不要): mono-dark / triadic-purple / analogous-pink / split-complement-violet / 严格 4 色限制下不能加的更多

### 11.3 为什么"严格 4 色"是更好的选择

| 项 | 5 色 / 多色 | 严格 4 色 |
|---|---|---|
| 视觉协调 | 容易撞色 | 几乎不出错 |
| 维护成本 | 设计稿难改 | 一改全改,简单 |
| 业务扩展 | 加新业务要扩色 | 已有 4 色足够 |
| 学习成本 | 设计/开发都要学 | 规律强,易掌握 |

### 11.4 选哪一套的速查流程

```
1. 业务类型?
   - 监控/政企 → 选单色(1/2/3)
   - 强对比突出 → 选互补(4)
   - 同一主题 → 选类比(5/6/8)
   - 多业务并重 → 选三元(7)
   - 科技/极客 → 选分裂补(9)

2. 深色 / 浅色?
   - 7×24 / 暗室 → 选深底(2/9)
   - 常规 → 选浅底(1/3/4/5/6/7/8)

3. 主色冷暖?
   - 冷色(蓝/绿/紫) → 1/2/3/5/7/9
   - 暖色(橙/粉) → 6/8
   - 蓝橙对比 → 4
```

### 11.5 案例对应

- v1 风力能源监控 → **mono-blue**(单色蓝, 业务监控)
- AI-GIS 智能问图 → **complement-blue-orange**(强对比突出 AI 高亮)
- 北京市 IDC → **mono-blue**(传统大屏风格)
- 智能体中心 → **complement-blue-orange**(5 色强对比门户)
- 采购大数据 → **complement-blue-orange**(4 大色块)
- 内容运营/MCN → **analogous-pink**(创意粉)
- 销售/CRM → **analogous-warm**(活力橙)
- 资管/律所 → **triadic-purple**(优雅紫)
- 科技产品 → **portal-bright / cyan-blue**(深蓝科技)
- 健康/医疗 → **green-cyan**(清新绿)
- 运营总览(图1) → **cyan-blue**
- 数据可视化(图2) → **portal-mint**
- 采购大屏(图3) → **portal-bright**
- 业务总览(图1选色) → **gold-bright**
