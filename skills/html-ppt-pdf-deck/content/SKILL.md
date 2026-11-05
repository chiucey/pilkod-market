---
name: html-ppt-pdf-deck
description: 构建基于 HTML + CSS + JS 的 16:9 宽屏幻灯片演示文稿，支持浏览器打印为 PDF，集成 Chart.js 图表。Use when creating printable presentations, slide PDFs, HTML PPT, wide-screen slides, exporting deck to PDF from browser, or generating slides with charts.
---

# HTML 宽屏幻灯片 → 打印 PDF

用静态网页实现 **16:9 宽屏**、**一页一屏**、**浏览器另存 PDF**，图表用 **Chart.js（CDN）**，工程上 **HTML / CSS / JS 分文件**。

## 快速开始

### 文件结构

```
project/
├── index.html          # section.slide 逐页内容
├── css/slides.css      # 屏上 + @media print 样式
├── js/charts.js        # Chart.js 配置与刷新函数
└── js/app.js           # 打印按钮与 beforeprint 事件
```

### 基础模板

**index.html**
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>演示文稿</title>
  <link rel="stylesheet" href="css/slides.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
  <!-- 封面 -->
  <section class="slide slide--cover">
    <div class="slide-body">
      <h1>标题</h1>
      <p>副标题</p>
    </div>
  </section>

  <!-- 内容页 -->
  <section class="slide">
    <div class="slide-header"><h2>章节标题</h2></div>
    <div class="slide-body">
      <ul class="slide-list">
        <li>要点一</li>
        <li>要点二</li>
      </ul>
    </div>
  </section>

  <!-- 图表页 -->
  <section class="slide">
    <div class="slide-header"><h2>数据分析</h2></div>
    <div class="slide-body slide-body--cols slide-body--chart-right">
      <div class="slide-text">
        <p>说明文字</p>
      </div>
      <div class="slide-chart">
        <div class="chart-wrap">
          <canvas id="chart1"></canvas>
        </div>
      </div>
    </div>
  </section>

  <!-- 打印按钮 -->
  <button class="print-btn" onclick="window.print()">导出 PDF</button>

  <script src="js/charts.js"></script>
  <script src="js/app.js"></script>
</body>
</html>
```

## CSS 核心约定

### 变量定义 (slides.css)

```css
:root {
  --page-w-mm: 338.67mm;
  --page-h-mm: 190.5mm;
  --page-ratio: 16 / 9;
  --root-font-size: 18px;
  --text-primary: #1a1a1a;
  --text-secondary: #4a4a4a;
  --bg-color: #ffffff;
  --accent-color: #2563eb;
}

@media print {
  :root {
    --root-font-size: 14pt;
  }
}
```

### 幻灯片容器

```css
/* 屏上：居中 + 比例锁定 */
.slide {
  width: 100%;
  max-width: calc(100vh * var(--page-ratio));
  aspect-ratio: var(--page-ratio);
  margin: 0 auto;
  background: var(--bg-color);
  position: relative;
  overflow: hidden;
}

/* 打印：铺满纸张 */
@media print {
  @page {
    size: 338.67mm 190.5mm;
    margin: 0;
  }

  .slide {
    max-width: none;
    width: 100%;
    height: 190.5mm;
    min-height: 190.5mm;
    max-height: 190.5mm;
    page-break-after: always;
    break-after: page;
    overflow: hidden;
  }

  .slide:last-child {
    page-break-after: auto;
    break-after: auto;
  }
}
```

### 双栏布局

```css
.slide-body--cols {
  display: grid;
  grid-template-columns: 62% 38%;
  grid-template-rows: minmax(0, 1fr);
  height: 100%;
  gap: 1rem;
}

.slide-body--chart-left {
  grid-template-columns: 62% 38%;
}

.slide-body--chart-right {
  grid-template-columns: 38% 62%;
}

.slide-chart {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding-top: 1.5rem;
}

.chart-wrap {
  width: 100%;
  height: 100%;
}
```

## Chart.js 图表要点

### charts.js 示例

```javascript
const charts = {};

function initCharts() {
  const ctx = document.getElementById('chart1');
  if (!ctx) return;

  charts.chart1 = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['A', 'B', 'C'],
      datasets: [{
        data: [30, 50, 20],
        backgroundColor: ['#2563eb', '#16a34a', '#dc2626']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 1.5,
      plugins: {
        legend: {
          position: 'right',
          labels: { padding: 12, font: { size: 12 } }
        },
        title: {
          display: true,
          text: '图表标题',
          padding: { top: 10, bottom: 15 }
        }
      }
    }
  });
}

function refreshChartsForPrint() {
  Object.values(charts).forEach(chart => {
    if (chart) {
      chart.resize();
      chart.update('none');
    }
  });
}

window.addEventListener('beforeprint', refreshChartsForPrint);

// 打印按钮触发
document.querySelector('.print-btn')?.addEventListener('click', () => {
  refreshChartsForPrint();
  setTimeout(() => window.print(), 150);
});
```

## 打印 PDF 指南

### 浏览器设置（必须严格按此配置）

| 设置项 | 正确值 |
|--------|--------|
| 边距 | 无 |
| 缩放 | 100% |
| 勾选"背景图形" | 必须勾选 |
| 纸张大小 | 自定义 338.67mm × 190.5mm |

### 常见问题对照表

| 现象 | 原因 | 解决方案 |
|------|------|----------|
| PDF 右侧/下方大白边 | `.slide` 仍用固定宽度 | 打印用 `width: 100%` |
| 图表被上下页切开 | 片高被内容撑破 | 锁片高 `height: 190.5mm` + `overflow: hidden` |
| 圆环变椭圆 | `maintainAspectRatio: false` | 改为 `true` + 设 `aspectRatio` |
| 图表贴顶 | `.chart-wrap` 垂直居中 | 改为 `align-items: flex-start` |

## 验证清单

- [ ] 打印预览每页一屏、无断图
- [ ] 圆环保持正圆
- [ ] 图表不贴顶
- [ ] 双栏比例与图左/图右一致
- [ ] `refreshChartsForPrint` 在 beforeprint 和打印按钮中均可触发

## 技术栈默认值

- 图表：**Chart.js** (cdn.jsdelivr.net)
- 字体：Microsoft YaHei / PingFang SC / Noto Sans SC
- 宽屏比例：16:9 (338.67mm × 190.5mm)
