# CSS 布局模式参考

## 1. 基础幻灯片结构

```css
/* 变量定义 */
:root {
  --page-w-mm: 338.67mm;
  --page-h-mm: 190.5mm;
  --page-ratio: 16 / 9;
  --root-fs: 18px;
  --gap: 0.8rem;
  --pad: 1.2rem;
  --text-primary: #1a1a1a;
  --text-secondary: #4a4a4a;
  --bg: #ffffff;
  --accent: #2563eb;
  --gray-light: #f3f4f6;
}

/* 幻灯片容器 */
.slide {
  width: 100%;
  max-width: calc(100vh * var(--page-ratio));
  aspect-ratio: var(--page-ratio);
  margin: 0 auto;
  background: var(--bg);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 页眉 */
.slide-header {
  padding: var(--pad) var(--pad) 0;
  flex-shrink: 0;
}

.slide-header h2 {
  margin: 0;
  font-size: 1.4em;
  font-weight: 600;
  color: var(--text-primary);
}

/* 内容区 */
.slide-body {
  flex: 1;
  padding: var(--gap) var(--pad) var(--pad);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 列表 */
.slide-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.slide-list li {
  font-size: 1.05em;
  line-height: 1.6;
  margin-bottom: 0.6em;
  color: var(--text-primary);
}

/* 段落 */
.slide-body p {
  font-size: 1em;
  line-height: 1.7;
  margin: 0 0 0.8em;
  color: var(--text-secondary);
}

/* 页脚 */
.slide-footer {
  padding: 0 var(--pad) var(--pad);
  font-size: 0.75em;
  color: var(--text-secondary);
  flex-shrink: 0;
}
```

## 2. 双栏布局

```css
/* 双栏基础 */
.slide-body--cols {
  display: grid;
  grid-template-columns: 38% 62%;
  grid-template-rows: minmax(0, 1fr);
  gap: 1.5rem;
  height: 100%;
}

/* 图在左 */
.slide-body--chart-left {
  grid-template-columns: 62% 38%;
}

/* 图在右 */
.slide-body--chart-right {
  grid-template-columns: 38% 62%;
}

/* 文本列 */
.slide-text {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 图表列 */
.slide-chart {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding-top: 1rem;
}

/* 图表容器 */
.chart-wrap {
  width: 100%;
  height: 100%;
  min-height: 0;
}

/* 确保 canvas 响应 */
.chart-wrap canvas {
  max-width: 100%;
  max-height: 100%;
}
```

## 3. 封面样式

```css
.slide--cover {
  justify-content: center;
  align-items: center;
  text-align: center;
  background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
  color: white;
}

.slide--cover .slide-body {
  justify-content: center;
  align-items: center;
}

.slide--cover h1 {
  font-size: 3em;
  font-weight: 700;
  margin: 0 0 0.5em;
  line-height: 1.2;
}

.slide--cover .subtitle {
  font-size: 1.5em;
  opacity: 0.9;
  margin: 0;
}

.slide--cover .meta {
  margin-top: 2em;
  font-size: 1em;
  opacity: 0.7;
}
```

## 4. 打印样式

```css
@media print {
  @page {
    size: 338.67mm 190.5mm;
    margin: 0;
  }

  html, body {
    width: 338.67mm;
    height: 190.5mm;
    margin: 0;
    padding: 0;
  }

  .slide {
    max-width: none;
    width: 100%;
    height: 190.5mm;
    min-height: 190.5mm;
    max-height: 190.5mm;
    aspect-ratio: auto;
    page-break-after: always;
    break-after: page;
    overflow: hidden;
  }

  .slide:last-child {
    page-break-after: auto;
    break-after: auto;
  }

  /* 打印时保持颜色 */
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    color-adjust: exact !important;
  }

  /* 隐藏打印按钮 */
  .print-btn {
    display: none !important;
  }
}
```

## 5. 响应式调整

```css
/* 含图表的双栏页面，缩小页眉 */
.slide-body--cols .slide-header {
  padding-top: 0.6rem;
}

.slide-body--cols .slide-header h2 {
  font-size: 1.2em;
}
```

## 6. 常用工具类

```css
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.font-bold { font-weight: 700; }
.font-semibold { font-weight: 600; }

.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-accent { color: var(--accent); }

.mt-auto { margin-top: auto; }
.mb-0 { margin-bottom: 0; }

.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}
```
