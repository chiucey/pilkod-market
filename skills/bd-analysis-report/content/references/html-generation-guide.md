# HTML生成技术指南

本指南用于将BD分析报告从Markdown转换为专业HTML格式。

---

## 1. 页面结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>企业BD分析范例：[企业名]</title>
<style>
/* CSS变量 */
:root {
  --bg: #ffffff;
  --bg2: #f8f9fa;
  --text: #1a1a2e;
  --text2: #4a4a6a;
  --accent: #2563eb;
  --accent-light: #eff6ff;
  --border: #e5e7eb;
  --header-from: #1a1a2e;
  --header-to: #2d2d44;
}
/* 完整CSS见下方 */
</style>
</head>
<body>
<!-- Header -->
<div class="header">
  <span class="badge">BD Analysis / Phase [X]</span>
  <h1>企业BD分析范例：<span>[企业名]</span></h1>
  <div class="meta">
    <span>分析日期：YYYY-MM-DD</span>
   
  </div>
</div>

<!-- 章节内容 -->
<div class="sec">
  <span class="sec-num">一</span>
  <h2>企业基本信息</h2>
  <!-- 内容 -->
</div>

<div class="sec">
  <span class="sec-num">二</span>
  <h2>BD评分与Phase判定</h2>
  <!-- 内容 -->
</div>

<!-- 更多章节... -->

<!-- Footer -->
<div class="footer">
  本报告基于行业细分画像评分及输出标准完成 · 仅供BD决策参考
</div>
</body>
</html>
```

---

## 2. 核心CSS

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.8;
  max-width: 1100px;
  margin: 0 auto;
}

/* Header */
.header {
  background: linear-gradient(135deg, var(--header-from), var(--header-to));
  color: #fff;
  padding: 3rem 2rem 2rem;
  border-radius: 0 0 12px 12px;
}

.header .badge {
  display: inline-block;
  background: rgba(255,255,255,.15);
  padding: .3rem .8rem;
  border-radius: 20px;
  font-size: .8rem;
  letter-spacing: .05em;
}

.header h1 {
  font-size: 1.8rem;
  margin: 1rem 0 .5rem;
}

.header h1 span {
  color: #60a5fa;
}

.header .meta {
  font-size: .85rem;
  opacity: .85;
  display: flex;
  gap: 2rem;
}

/* Sections */
.sec {
  padding: 2rem 2rem 1rem;
  border-bottom: 1px solid var(--border);
}

.sec-num {
  display: inline-block;
  background: var(--accent);
  color: #fff;
  width: 2rem;
  height: 2rem;
  line-height: 2rem;
  text-align: center;
  border-radius: 50%;
  font-size: .9rem;
  margin-right: .5rem;
}

.sec h2 {
  display: inline;
  font-size: 1.3rem;
  color: var(--text);
}

.sec h3 {
  font-size: 1.1rem;
  margin: 1.5rem 0 .5rem;
  color: var(--text2);
}

.sec h4 {
  font-size: 1rem;
  margin: 1rem 0 .5rem;
}

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: .9rem;
}

thead {
  background: var(--bg2);
}

thead th {
  padding: .6rem .8rem;
  text-align: left;
  font-weight: 600;
  font-size: .75rem;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: var(--text2);
}

tbody td {
  padding: .6rem .8rem;
  border-bottom: 1px solid var(--border);
}

tbody tr:hover {
  background: rgba(37, 99, 235, .02);
}

td:first-child, th:first-child {
  font-weight: 500;
}

/* AI提示块 */
.aih {
  border-left: 4px solid var(--accent);
  background: var(--accent-light);
  padding: .8rem 1rem;
  margin: 1rem 0;
  border-radius: 0 6px 6px 0;
  font-size: .9rem;
  color: var(--text2);
}

.aih hr {
  border: none;
  border-top: 1px solid rgba(37, 99, 235, .15);
  margin-top: .5rem;
}

/* Blockquote */
blockquote {
  border-left: 3px solid var(--accent);
  margin: 1rem 0;
  padding: .5rem 1rem;
  color: var(--text2);
  background: var(--bg2);
  border-radius: 0 6px 6px 0;
}

/* Code blocks */
pre {
  background: var(--bg2);
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  font-size: .85rem;
}

/* Footer */
.footer {
  background: var(--bg2);
  padding: 1.5rem 2rem;
  text-align: center;
  font-size: .8rem;
  color: var(--text2);
  border-radius: 12px 12px 0 0;
  margin-top: 2rem;
}

/* Responsive */
@media (max-width: 768px) {
  body { font-size: .9rem; }
  .header { padding: 2rem 1rem 1.5rem; }
  .header h1 { font-size: 1.4rem; }
  .header .meta { flex-direction: column; gap: .5rem; }
  .sec { padding: 1.5rem 1rem .5rem; }
  table { font-size: .8rem; }
}
```

---

## 3. 关键规则

### 3.1 章节div必须平级开闭

```html
<!-- 正确：平级 -->
<div class="sec">...</div>
<div class="sec">...</div>

<!-- 错误：嵌套 -->
<div class="sec">
  <div class="sec">...</div>
</div>
```

每个新章节先`</div>`关闭上一章，再`<div class="sec">`开启新章。

### 3.2 子标题编号跟随章节

- 第二章的子标题是2.1/2.2/2.3/2.4
- 第三章是3.1/3.2/3.3/3.4
- 第六章的子标题是6.1-6.8
- 第六章内部的更细分级（如产品分析h4）不需要编号

### 3.3 特殊CSS类

| 类名 | 用途 |
|------|------|
| `.aih` | AI提示块（蓝左框+淡蓝背景） |
| `.gc` | 灰色卡片容器 |
| `.sec-num` | 章节编号圆角标签 |
| `.badge` | Header中的Phase标签 |
| `.header` | 深色渐变头部区域 |
| `.footer` | 浅灰底部版权区 |

### 3.4 表格处理

- thead用浅灰背景(`var(--bg2)`) + 小字大写
- 第一列加粗(`font-weight:500`)
- hover行高亮(`rgba(37,99,235,.02)`)

---

## 4. Markdown→HTML转换注意事项

1. **MD中的`---`分隔线**：在HTML中不渲染为`<hr>`，而是作为章节切换点（关闭上一个`.sec`，开启新的`.sec`）
2. **章节编号**：MD中"一、二、三..."对应HTML中`.sec-num`的"一、二、三..."
3. **AI提示块**：
   - MD格式：`> **AI提示：** [内容]`
   - HTML格式：`<div class="aih"><strong>AI提示：</strong>[内容]<hr></div>`
4. **代码块**：MD中的`<pre><code>`在HTML中保持原样渲染
5. **blockquote**：MD中的`>`转换为`<blockquote>`
6. **表格**：标准MD表格转换为HTML `<table>`
