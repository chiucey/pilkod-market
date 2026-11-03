# 布局系统(三栏 + 地图底层 + 浮层面板)

## 总布局原则
1. **设计稿固定 1920×1080**
2. **三栏 + 头部**: grid-template-areas `header header header / left main right`
3. **地图作为底层背景(满屏)**: position absolute 占满整个主区域(含左右两侧),所有 panel 浮在上面
4. **所有 panel 半透明浮层**: `rgba(255,255,255,0.78)` + `backdrop-filter: blur(6px)`

## 地图满屏(关键)
中国地图占满 #app 除 header 以外的所有区域,包括左右两侧 panel 位置。
```css
.map-bg {
    position: absolute;
    top: 80px;          /* 跳过 header */
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1;
}
```
这样 map-bg 不依赖于 grid 列宽,能延伸到面板区域后面,作为大屏"底色"。

## HTML 结构模板
```html
<div id="app">
    <header class="header">...</header>
    
    <aside class="col left-col">
        <section class="panel">面板1</section>
        <section class="panel">面板2</section>
        ...
    </aside>
    
    <main class="col main-col"></main>
    
    <!-- 地图底层背景(跳出 grid) -->
    <section class="map-bg">
        <span class="corner-tl"></span>...<span class="corner-br"></span>
        <div id="mapChart"></div>
        <div class="marquee">...</div>
        <footer class="tabs-floating">
            <div class="tab-item active">能源观测</div>
            <div class="tab-item">设备中心</div>
        </footer>
    </section>
    
    <aside class="col right-col">
        <div class="summary-main">总计卡片</div>
        <div class="summary-grid">...</div>
        <section class="panel">面板</section>
        ...
    </aside>
</div>
```

## CSS 核心规则

### #app 容器
```css
#app {
    width: 1920px;
    height: 1080px;
    display: grid;
    grid-template-columns: 360px 1fr 360px;     /* 左右各 360 */
    grid-template-rows: 80px 1fr;                /* 头部 + 内容 */
    grid-template-areas:
        "header header header"
        "left   main   right";
    gap: 14px;
    padding: 14px;
    position: absolute;
    left: 50%; top: 50%;
    transform-origin: center center;
    transform: translate(-50%, -50%) scale(var(--scale));
}
```

### 头部 .header
```css
.header {
    grid-area: header;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    position: relative;  /* 装分隔线 */
}
.header::before, .header::after {
    content: ''; position: absolute; bottom: 0;
    width: 35%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-light), transparent);
}
```

### 列容器 .col
```css
.col {
    display: flex;
    flex-direction: column;
    gap: 14px;
    z-index: 3;             /* 浮在地图之上 */
    pointer-events: none;   /* 容器不阻挡点击 */
}
.col > * { pointer-events: auto; }  /* 子面板恢复点击 */
```

### .panel 通用
```css
.panel {
    background: var(--panel-bg);
    border: 1px solid var(--panel-border);
    border-radius: 4px;
    padding: 14px 12px 12px;
    backdrop-filter: blur(6px);
    box-shadow: var(--shadow);
    flex: 1 1 0;            /* 等分剩余空间 */
    display: flex;
    flex-direction: column;
    position: relative;
}

/* 四角装饰 */
.panel::before, .panel::after,
.panel > .corner-tl, .panel > .corner-tr,
.panel > .corner-bl, .panel > .corner-br {
    content: ''; position: absolute;
    width: 12px; height: 12px;
    border-color: var(--accent);
    border-style: solid;
}
.panel::before { top: -1px; left: -1px; border-top-width: 2px; border-left-width: 2px; }
.panel::after { top: -1px; right: -1px; border-top-width: 2px; border-right-width: 2px; }
.panel > .corner-bl { bottom: -1px; left: -1px; border-bottom-width: 2px; border-left-width: 2px; }
.panel > .corner-br { bottom: -1px; right: -1px; border-bottom-width: 2px; border-right-width: 2px; }
```

### 地图作为底层 .map-bg(满屏)
```css
/* 满屏版: 覆盖整个主区域(含左右两侧) */
.map-bg {
    position: absolute;
    top: 80px;        /* 跳过 header */
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(245, 249, 253, 0.5);
    border: 1px solid rgba(143, 188, 255, 0.4);
    border-radius: 0;  /* 满屏不需要圆角 */
    z-index: 2;
    overflow: hidden;
}

/* 局限版本: 只覆盖中间列(在两侧 panel 不需要地图背景时使用) */
.map-bg.compact {
    left: calc(360px + 14px * 2);
    right: calc(360px + 14px * 2);
    top: calc(80px + 14px);
    bottom: 14px;
    border-radius: 4px;
}

#mapChart { width: 100%; height: 100%; }
```

默认用 **满屏版**(用户体感更震撼)。只有需要精确左/右边界时不加满屏。

### Tab 浮在底部
```css
.tabs-floating {
    position: absolute;
    bottom: 14px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 80px;
    z-index: 10;
    padding: 8px 24px;
    background: rgba(255, 255, 255, 0.4);
    backdrop-filter: blur(6px);
    border-radius: 4px;
}

.tab-item.active::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 8px;
    background: radial-gradient(ellipse, rgba(143, 188, 255, 0.8) 0%, transparent 70%);
    box-shadow: 0 4px 16px rgba(143, 188, 255, 0.6);
    border-radius: 50%;
}
```

## 模块尺寸参考(1920×1080 基准)
- 头部高度: 80px
- 左右列宽度: 360px
- gap: 14px
- panel padding: 14px
- panel 标题字号: 18px
- 总计大数字字号: 38px
- 时钟字号: 40px

## 自适应断点
```css
@media (max-height: 900px) {
    .header-title { font-size: 36px; }
    .header-time .clock { font-size: 32px; }
}
@media (max-height: 768px) {
    .header-title { font-size: 30px; }
    .panel-title { font-size: 14px; }
    .panel { padding: 10px; }
}
```
即使有断点,主网格 #app 始终是 transform: scale 缩放,不需要重排版。

## 注意点
1. 不要在 panel 里写 `width: 100%`,flex 容器会撑满
2. 地图 .map-bg 必须 `position: absolute` 跳出 grid
3. Tab .tabs-floating 用 z-index 比 .col 大但比模态层小(默认 10)
4. .map-bg 的 left/right/inset 精确计算才能让 panel 对齐

