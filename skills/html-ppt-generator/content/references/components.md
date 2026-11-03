---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100bbbd1f62272281076cca3854638d666bbda85c5fc760bc775e65273ac2ee9a3602204187078250f98e0aea3db5b08dba0c8ac10148a0128bc78765fe5e017643b5c6
    ReservedCode2: 3045022100ca8a358a1d5a12bbc0f67af03008aacbe1dd5d125869602b51d9fb48d56801ce02207e1969a29db5b7d623c50b52621d8f8969fc6da045d7c0a3ff72f0887d0a629b
---

# 组件参考手册 · Components

> 这是html-ppt-generator skill的组件手册。template.html已经定义好了所有样式，这里只写"这个组件长什么样、怎么用"。

## 目录

- [基础Slide外壳](#基础slide外壳)
- [字体系统](#字体系统)
- [Chrome页眉](#chrome页眉)
- [Foot页脚](#foot页脚)
- [Callout引用框](#callout引用框)
- [Stat数字卡片](#stat数字卡片)
- [Grid网格布局](#grid网格布局)
- [Pillar支柱卡](#pillar支柱卡)
- [Rowline表格行](#rowline表格行)
- [Figure图片框](#figure图片框)
- [Timeline时间线](#timeline时间线)
- [Pipeline流程](#pipeline流程)
- [Chart图表组件](#chart图表组件)
- [Tag标签](#tag标签)
- [Kicker小节提示](#kicker小节提示)
- [Highlight荧光标记](#highlight荧光标记)
- [Ghost巨型背景字](#ghost巨型背景字)
- [图标系统](#图标系统)
- [动画系统](#动画系统)

---

## 基础Slide外壳

每一页都是一个`<section class="slide">`，必须包含`data-theme`属性（`light`或`dark`），翻页时会根据这个属性切换背景。

```html
<section class="slide" data-theme="light">
  <div class="chrome">...</div>
  <div class="content">...</div>
  <div class="foot">...</div>
</section>
```

**light vs dark的使用规则**：

- 交替使用，每2-3页切换一次主题
- 避免连续超过3页使用相同主题
- 翻页时背景会在两个颜色之间渐变过渡

**hero类的使用规则**：

- 只给视觉主导的页面添加（封面、金句页、章节过渡、结尾）
- 添加hero后遮罩降到12-16%，背景效果会大幅透出
- 不要在hero页上放太多文字，保持简洁

---

## 字体系统

字体分工是本模板最重要的规则，严禁混用。

### 字体级别对照表

| Class | 用途 | 字体 | 字号参考 |
|-------|------|------|----------|
| `.display` | 超大号英文 | Playfair Display | 11vw |
| `.display-zh` | 超大号中文标题 | Noto Serif SC | 7.8vw |
| `.h1-zh` | 页面主标题 | Noto Serif SC | 4.6vw |
| `.h2-zh` | 副标题 | Noto Serif SC | 3.2vw |
| `.h3-zh` | 章节标题 | Noto Serif SC | 2.2vw |
| `.h4-zh` | 小节标题 | Noto Sans SC | 1.6vw |
| `.lead` | 引导段落 | Noto Sans SC | 1.9vw |
| `.body-zh` | 正文描述 | Noto Sans SC | 1.22vw |
| `.body-serif` | 正文（衬线） | Noto Serif SC | 1.3vw |
| `.kicker` | 小节提示 | IBM Plex Mono | 12px uppercase |
| `.meta` | 元信息 | IBM Plex Mono | 0.88vw uppercase |
| `.big-num` | 巨型数字 | Playfair Display | 10vw |
| `.mid-num` | 中号数字 | Playfair Display | 5.5vw |

### 字体使用原则

**衬线字体（serif）用于**：

- 各级标题
- 重要金句
- 数字展示
- 视觉重音位置

**非衬线字体（sans）用于**：

- 正文描述
- 大段阅读内容
- 信息密度位置

**等宽字体（mono）用于**：

- kicker（标题上方小提示）
- meta（页眉页脚元信息）
- foot的英文标签
- 装饰节奏

### 强调技巧

```html
<!-- 英文词斜体 -->
<p>这是<em>Thin Harness, Fat Skills</em>的核心要义</p>

<!-- 短语强调 -->
<h2>做减法<em>比做加法</em>更难</h2>
```

---

## Chrome页眉

每一页的顶部元信息条，定义页面导航上下文。

```html
<div class="chrome">
  <div class="left">章节名 · 小节名</div>
  <div class="center"></div>
  <div class="right">03</div>
</div>
```

**规则**：

- `chrome.left`：当前章节名称，使用衬线字体
- `chrome.center`：可选，用于特殊标记
- `chrome.right`：当前页码（纯数字格式如"03"）

---

## Foot页脚

每一页的底部元信息条，定义页面导航上下文。

```html
<div class="foot">
  <div class="left">03 / 15</div>
  <div class="center">项目名称</div>
  <div class="right">Chapter · Section</div>
</div>
```

**规则**：

- `foot.left`：页码（当前/总数）
- `foot.center`：项目或汇报名称
- `foot.right`：章节英文标记

---

## Callout引用框

展示金句、关键观点、他人引言。

```html
<blockquote class="callout">
  <p>"数字化转型不是选择题，而是生存题。谁先完成转型，谁就赢得未来。"</p>
  <cite>— 某市数字化改革工作领导小组</cite>
</blockquote>
```

**变体**：

```html
<!-- 不带引言来源 -->
<blockquote class="callout">
  <p>核心观点内容</p>
</blockquote>

<!-- 带英文金句 -->
<p>这是<em>"Thin Harness, Fat Skills"</em>的精髓</p>

<!-- 在hero页使用（避免被背景遮挡） -->
<div style="position:relative;z-index:2;">
  <blockquote class="callout">...</blockquote>
</div>
```

---

## Stat数字卡片

展示关键数据指标，配合`.grid-6`或`.grid-4`使用。

```html
<div class="stat-card">
  <div class="m">Duration</div>
  <div class="n">64 <small>*天*</small></div>
  <div class="l">从0到现在</div>
</div>
```

**三段式结构**：

- `.m`：等宽小标签（如"平台接入量"）
- `.n`：巨型数字（如"2,847"），数字后的单位用`small`缩小到0.4em
- `.l`：描述说明（如"同比提升156%"）

**常用布局容器**：

- `.grid-6`：3×2网格（最常用，6个stat）
- `.grid-4`：2×2网格（4个stat）
- `.grid-3`：3等分单行（3个stat）
- 自定义网格：`style="display:grid;grid-template-columns:repeat(3,1fr);gap:2vw;"`

---

## Grid网格布局

网格系统用于排列多个元素。

### 预定义网格类

| 类名 | 布局 | 适用场景 |
|------|------|----------|
| `.grid-6` | 3×2 | 6个数据卡片 |
| `.grid-4` | 2×2 | 4个数据卡片 |
| `.grid-3` | 3列 | 3个支柱或数据 |
| `.grid-2-7-5` | 2:7:5 | 左文右图（窄左） |
| `.grid-2-6-6` | 2:6:6 | 左文右图（等分） |
| `.grid-2-8-4` | 2:8:4 | 左文右图（宽右） |

### 自定义网格

```html
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1.5vw;">
  <!-- 4列网格内容 -->
</div>
```

### 高度类（用于图片网格）

| 类名 | 高度 | 适用场景 |
|------|------|----------|
| `.h-16` | 16vh | 小型面板 |
| `.h-18` | 18vh | 紧凑条形 |
| `.h-22` | 22vh | 标准网格 |
| `.h-26` | 26vh | 突出展示 |
| `.h-28` | 28vh | 大图展示 |

---

## Pillar支柱卡

三支柱结构，用于概念并列、优势展示。

```html
<div class="pillar">
  <div class="ic">01</div>
  <div class="ti">三层<br>文档体系</div>
  <div class="desc">CLAUDE.md<br>+ 项目知识库<br>+ 护栏文件</div>
</div>
```

**带图标的pillar变体**：

```html
<div class="pillar">
  <div class="ic">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
      <path d="M12 16v-4"></path>
      <path d="M12 8h.01"></path>
    </svg>
  </div>
  <div class="ti">判断力</div>
  <div class="desc">决策和方向的权威。<br>取舍、品味、方向感。</div>
</div>
```

**规则**：

- `.ic`可以是序号（01/02/03或A./B./C.），也可以是Lucide图标
- `.ti`是标题，使用衬线字体
- `.desc`是描述说明，使用非衬线字体

---

## Rowline表格行

列表式内容，每行一个条目。

```html
<div class="rowline">
  <div class="k">CLAUDE.md</div>
  <div class="v">你该怎么做事 —— 行为规则 + 工作偏好 + 禁止事项</div>
  <div class="m">EMPLOYEE · HANDBOOK</div>
</div>
```

**三列结构**：

- `.k`：衬线关键词
- `.v`：正文描述
- `.m`：等宽标签（右对齐）

**2列变体**：

```html
<div class="rowline" style="grid-template-columns:1fr 3fr;">
  <div class="k">关键词</div>
  <div class="v">描述内容</div>
</div>
```

**规则**：

- 第一个和最后一个rowline自动加上下边框
- 同一组rowline之间的间隔为0

---

## Figure图片框

**这是最容易被踩坑的组件，务必遵守以下规则**。

### 基础结构

```html
<figure class="figure">
  <div class="frame-img h-22">
    <img src="/assets/xxx.png" alt="" loading="lazy">
  </div>
  <figcaption>
    <div class="title">图片标题</div>
    <div class="stat">补充说明</div>
  </figcaption>
</figure>
```

### 关键约束（血泪经验）

**1. 图片网格必须用height:Nvh固定高度**

禁止使用`aspect-ratio`，这会导致网格布局不稳定。

```html
<!-- 正确写法 -->
<div class="frame-img h-22">
  <img src="..." alt="...">
</div>

<!-- 错误写法 -->
<div class="frame-img" style="aspect-ratio:16/9;">
  <img src="..." alt="...">
</div>
```

**2. 图片裁剪规则**

`object-position:top center`已在CSS中设好，只允许裁掉图片底部。严禁裁剪左右和顶部——那是图片的核心身份信息区。

**3. 多图网格用内联grid**

```html
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.5vh;">
  <figure class="figure">...</figure>
  <figure class="figure">...</figure>
  <figure class="figure">...</figure>
</div>
```

**4. 信息图/截图处理**

给`.frame-img`同时添加`.fit-contain`，避免图内文字被裁切：

```html
<div class="frame-img h-22 fit-contain">
  <img src="..." alt="...">
</div>
```

### Frame Caption变体

```html
<figure class="figure">
  <div class="frame-img h-18">
    <img src="" alt="">
    <div class="frame-badge">
      <span class="idx">01</span>
      <span class="label">功能说明</span>
    </div>
  </div>
  <figcaption>
    <div class="title">功能名称</div>
  </figcaption>
</figure>
```

### 图片占位符

图片未就位时，用虚线框占位：

```html
<div class="frame-img h-22" style="border:2px dashed var(--gray-4);display:flex;align-items:center;justify-content:center;color:var(--gray-4);">
  <span>+ 图片位置说明</span>
</div>
```

---

## Timeline时间线

展示时间维度的进展和里程碑。

```html
<div class="timeline" style="position:relative;padding-left:3vw;">
  <!-- 时间线主轴 -->
  <div style="position:absolute;left:1vw;top:0;bottom:0;width:2px;background:var(--gray-6);"></div>

  <!-- 里程碑 -->
  <div style="position:relative;padding-left:3vw;margin-bottom:4vh;">
    <div style="position:absolute;left:-0.6vw;top:0.5vh;width:1.2vw;height:1.2vw;border-radius:50%;background:var(--accent);"></div>
    <div class="meta" style="color:var(--accent);">2024年6月</div>
    <h4 class="h4-zh">一期上线</h4>
    <p class="body-zh" style="color:var(--gray-3);">里程碑说明文字</p>
  </div>
</div>
```

**关键点**：

- 时间线主轴用2px宽的灰线
- 每个里程碑用圆点标记
- 已完成用强调色（如accent或success）
- 待完成用灰色（如gray-4）

---

## Pipeline流程

分步骤展示流程或路径，支持交互点亮。

```html
<div class="pipeline">
  <div class="step" data-anim="step">
    <div class="step-nb">01</div>
    <div class="step-title">基础夯实</div>
    <div class="step-desc">完成基础设施建设和数据归集</div>
    <div class="step-meta">2024.Q1-Q2</div>
  </div>
  <!-- 更多步骤 -->
</div>
```

**结构**：

- `.step-nb`：步骤编号
- `.step-title`：步骤标题
- `.step-desc`：步骤说明
- `.step-meta`：时间标签

**动画属性**：

- 添加`data-anim="step"`启用逐个点亮效果
- 使用`data-animate="pipeline"`启用交互式流程演示
- 翻到Pipeline页时步骤保持15%透明，按→/空格/滚轮逐个点亮

---

## Chart图表组件

数据可视化是政务汇报的核心，本Skill提供多种图表组件。使用CSS实现，无需JavaScript库。

### 柱状图

展示多维度数据对比，垂直柱状。

```html
<div class="chart-container">
  <div class="chart-title">季度办件量统计</div>
  <div class="chart-content">
    <div class="bar-chart">
      <div class="bar-item">
        <div class="bar-value">2.8万</div>
        <div class="bar" style="height:70%;"></div>
        <div class="bar-label">Q1</div>
      </div>
      <div class="bar-item">
        <div class="bar-value">3.5万</div>
        <div class="bar" style="height:85%;"></div>
        <div class="bar-label">Q2</div>
      </div>
      <div class="bar-item">
        <div class="bar-value">4.2万</div>
        <div class="bar" style="height:95%;"></div>
        <div class="bar-label">Q3</div>
      </div>
      <div class="bar-item">
        <div class="bar-value">5.1万</div>
        <div class="bar" style="height:100%;"></div>
        <div class="bar-label">Q4</div>
      </div>
    </div>
  </div>
</div>
```

### 横向条形图

适合展示排名或进度对比。

```html
<div class="chart-container">
  <div class="chart-title">各部门办件效率排名</div>
  <div class="h-bar-chart">
    <div class="h-bar-item">
      <div class="h-bar-label">市场监管局</div>
      <div class="h-bar-track">
        <div class="h-bar-fill" style="width:92%;"></div>
      </div>
      <div class="h-bar-value">92%</div>
    </div>
    <div class="h-bar-item">
      <div class="h-bar-label">人社局</div>
      <div class="h-bar-track">
        <div class="h-bar-fill" style="width:87%;"></div>
      </div>
      <div class="h-bar-value">87%</div>
    </div>
    <div class="h-bar-item">
      <div class="h-bar-label">民政局</div>
      <div class="h-bar-track">
        <div class="h-bar-fill" style="width:78%;"></div>
      </div>
      <div class="h-bar-value">78%</div>
    </div>
  </div>
</div>
```

### 环形图/饼图

展示占比和分布情况。

```html
<div class="chart-container">
  <div class="chart-title">服务渠道分布</div>
  <div style="display:flex;gap:3vw;align-items:center;">
    <div class="donut-chart">
      <svg viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="40" stroke="var(--accent)" stroke-dasharray="150.8 100.5" />
        <circle cx="50" cy="50" r="40" stroke="var(--success)" stroke-dasharray="75.4 100.5" stroke-dashoffset="-150.8" />
        <circle cx="50" cy="50" r="40" stroke="var(--warning)" stroke-dasharray="50.3 100.5" stroke-dashoffset="-226.2" />
      </svg>
      <div class="donut-center">
        <div class="donut-value">5.6万</div>
        <div class="donut-label">总办件</div>
      </div>
    </div>
    <div class="chart-legend" style="flex-direction:column;align-items:flex-start;">
      <div class="legend-item"><div class="legend-color" style="background:var(--accent);"></div>PC端 60%</div>
      <div class="legend-item"><div class="legend-color" style="background:var(--success);"></div>移动端 30%</div>
      <div class="legend-item"><div class="legend-color" style="background:var(--warning);"></div>自助终端 10%</div>
    </div>
  </div>
</div>
```

### 进度条

展示目标完成率或进度。

```html
<div class="chart-container">
  <div class="chart-title">年度目标完成情况</div>
  <div class="progress-container">
    <div class="progress-item">
      <div class="progress-header">
        <div class="progress-label">平台接入率</div>
        <div class="progress-value">92%</div>
      </div>
      <div class="progress-track"><div class="progress-fill" style="width:92%;"></div></div>
    </div>
    <div class="progress-item">
      <div class="progress-header">
        <div class="progress-label">数据共享率</div>
        <div class="progress-value">85%</div>
      </div>
      <div class="progress-track"><div class="progress-fill" style="width:85%;"></div></div>
    </div>
    <div class="progress-item">
      <div class="progress-header">
        <div class="progress-label">用户活跃度</div>
        <div class="progress-value">78%</div>
      </div>
      <div class="progress-track"><div class="progress-fill" style="width:78%;"></div></div>
    </div>
  </div>
</div>
```

### 迷你数据卡片网格

快速展示多个关键指标。

```html
<div class="mini-chart-grid">
  <div class="mini-chart-card">
    <div class="mini-chart-label">办件总量</div>
    <div class="mini-chart-value">15.6万</div>
    <div class="mini-chart-trend up">↑ 23.5%</div>
  </div>
  <div class="mini-chart-card">
    <div class="mini-chart-label">好评率</div>
    <div class="mini-chart-value">96.8%</div>
    <div class="mini-chart-trend up">↑ 2.1%</div>
  </div>
  <div class="mini-chart-card">
    <div class="mini-chart-label">平均时长</div>
    <div class="mini-chart-value">2.3天</div>
    <div class="mini-chart-trend down">↓ 18.2%</div>
  </div>
</div>
```

**图表配色使用CSS变量**：

- 主色：`var(--accent)`
- 成功色：`var(--success)`
- 警告色：`var(--warning)`
- 信息色：`var(--info, #3B82F6)`

---

## Tag标签

独立的标签胶囊，用于关键词标记。

```html
<span class="tag">数字化转型</span>
<span class="tag">智能治理</span>
<span class="tag">数据驱动</span>
```

**样式**：

- 带边框的胶囊形状
- 与背景形成对比
- 用于强调关键词

---

## Kicker小节提示

标题上方的小提示文字，用于标注章节或内容类型。

```html
<div class="kicker">过去64天 · 开发篇</div>
<h1 class="h-xl">一个人，做了什么。</h1>
```

**特点**：

- 等宽字体，全大写
- 小字号（12-14px）
- 位于标题上方
- 用于装饰和节奏

---

## Highlight荧光标记

行内短语的强调效果。

```html
<p>这是<span class="highlight">关键信息</span>的强调</p>

<!-- 或使用mark元素 -->
<p>这是<mark>关键信息</mark>的强调</p>
```

**效果**：在文字底部生成一条半透明高亮条。深色主题用亮条，浅色主题用暗条。

**规则**：只对关键1-3个词使用，不要大面积使用。

---

## Ghost巨型背景字

用作装饰性背景字，极低透明度，营造杂志感。

```html
<div class="ghost">BUT</div>
<div class="ghost">Harness</div>
```

**特点**：

- 字号34vw，opacity 0.06
- 常用定位：`right:-6vw;top:-8vh`（右上超出）或`left:-8vw;bottom:-18vh`（左下超出）
- 内容：英文单词或数字（章节序号、关键词）

**注意事项**：使用ghost的页面里，其他内容要添加`position:relative;z-index:2`避免被压到下面。

---

## 图标系统

**严禁使用emoji**，使用Lucide图标库。

### 引入方式

```html
<!-- template.html已通过CDN引入，无需手动添加 -->
<script src="https://unpkg.com/lucide@latest"></script>
```

### 使用方式

```html
<svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
  <circle cx="12" cy="12" r="10"></circle>
  <path d="M12 16v-4"></path>
  <path d="M12 8h.01"></path>
</svg>
```

### 常用图标速查

**判断类**：`compass`、`target`、`crosshair`、`search-check`

**关系类**：`share-2`、`users`、`network`、`link`、`handshake`

**品牌类**：`crown`、`gem`、`award`、`star`、`badge-check`

**流程类**：`workflow`、`route`、`arrow-right-left`、`repeat`

**数据类**：`grid-2x2`、`bar-chart-3`、`trending-up`、`activity`

**审美类**：`palette`、`brush`、`eye`、`sparkles`

**对错类**：`check-circle`、`x-circle`、`check`、`x`

**方向类**：`arrow-right`、`arrow-up-right`、`corner-down-right`

### 图标与文字inline组合

```html
<p>
  <svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>
  判断 — 什么值得写
</p>
```

---

## 动画系统

本模板内置翻页入场动画，由Motion One驱动（约4KB）。

### 加载机制

`assets/template.html`底部的module script会尝试加载本地motion.min.js，失败则回落到jsdelivr CDN，两者都失败则强制把所有带`data-anim`的元素设为`opacity:1`——内容永远可读，动画不依赖网络。

### 数据属性

你只需要在HTML里添加两种属性：

- `data-anim`：默认值为cascade
- `data-animate`：决定animation recipe

```html
<section class="slide hero">
  <h1 data-anim>大标题</h1>
  <p data-anim>引导段落</p>
  <div class="grid-2">
    <div data-anim>左列内容</div>
    <div data-anim>右列内容</div>
  </div>
</section>
```

### 5种动画配方

| Recipe | 触发方式 | 行为 | 代表布局 |
|--------|----------|------|----------|
| `cascade`（默认） | 不加data-animate | 所有data-anim逐个stagger淡入，75ms/step | Layout 3/4/5/10 |
| `hero` | .hero slide自动 | 慢节奏stagger，仪式感更强，160ms/step | Layout 1/2/12 |
| `quote` | data-animate="quote" | 其他元素先出，data-anim="line"的行550ms间隔逐句揭示 | Layout 6 |
| `directional` | data-animate="directional" | 左列从左滑入，右列从右滑入 | Layout 7 |
| `pipeline` | data-animate="pipeline" | 翻到页时steps保持15%透明，按→逐个点亮 | Layout 5 |

### 配方选择决策树

1. **它是.hero slide吗？** → 不用加data-animate，自动用hero
2. **它是大引用金句页？** → data-animate="quote"，每句用`<span data-anim="line">`
3. **它是左右对比Before/After？** → data-animate="directional"，左列data-anim="left"、右列data-anim="right"
4. **它是流水线分步讲解？** → data-animate="pipeline"，每步data-anim="step"
5. **其他所有正文页** → 什么也不加，自动用cascade

### 什么元素该加data-anim

✅ 加：

- 每一层有独立语义的块：kicker/h1/h-xl/lead/callout/stat-card/figure/tag/rowline
- 多列结构里每一列，让它们逐列淡入而不是一起

❌ 不加：

- 不要在容器（.grid-6/.frame）上加，只加给叶子元素
- 不要在每个`<li>`上加，一般在`<div>`层加就够
- 如果某页不想要任何动画（如过渡页），整页不加data-anim即可

---

## 总结：使用原则

1. **字体严格分工**：衬线用于标题/金句/数字，非衬线用于正文，等宽用于装饰
2. **交替使用light/dark主题**：每2-3页切换一次，避免连续超过3页同色
3. **hero类只用于视觉主导页面**：封面、金句页、章节过渡、结尾
4. **图片网格必须用高度固定**：用`height:Nvh`而不是aspect-ratio
5. **图标使用Lucide**：严禁使用emoji
6. **动画按需添加**：根据页面类型选择合适的recipe，形成张弛有度的节奏