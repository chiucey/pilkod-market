---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30450221008b242e30f63ef5ccf3490134fae1b7de11bb1ae9f95b3736e4b67aa1be6c943902207f9d170d053b0077090acdd6b77b3a0ac84974722f95e1ee3409cf2ef011d7e5
    ReservedCode2: 3045022100c0a78030409af154d95b8f638288a0474987c42e77ae73ec64e851b82a350a80022054c676855ff125c0a6ea119829d49472c791bcec930a22bc9166ac1c5a8015f7
---

# CSS变量速查表 · CSS Variables Cheatsheet

> 本文档是HTML PPT Generator Skill的CSS变量速查表，涵盖所有可用的设计Token，方便快速查阅和定制。

---

## 目录

1. [字体变量](#1-字体变量)
2. [颜色变量](#2-颜色变量)
3. [间距系统](#3-间距系统)
4. [过渡与动画](#4-过渡与动画)
5. [阴影与发光](#5-阴影与发光)
6. [完整变量清单](#6-完整变量清单)

---

## 1. 字体变量

### 字体族定义

| 变量名 | 用途 | 默认值 |
|--------|------|--------|
| `--font-serif` | 衬线字体（标题、金句、数字） | Noto Serif SC, Source Han Serif SC |
| `--font-sans` | 非衬线字体（正文） | Noto Sans SC, Microsoft YaHei |
| `--font-mono` | 等宽字体（装饰、元信息） | IBM Plex Mono |
| `--font-display` | 展示字体（英文大标题） | Playfair Display |

### 字体类对照

| Class | 用途 | 字号参考 |
|-------|------|----------|
| `.display` | 超大英文标题 | 11vw |
| `.display-zh` | 超大中文标题 | 7.8vw |
| `.h1-zh` | 页面主标题 | 4.6vw |
| `.h2-zh` | 副标题 | 3.2vw |
| `.h3-zh` | 章节标题 | 2.2vw |
| `.h4-zh` | 小节标题 | 1.6vw |
| `.lead` | 引导段落 | 1.9vw |
| `.body-zh` | 正文描述 | 1.22vw |
| `.body-serif` | 正文（衬线） | 1.3vw |
| `.kicker` | 小节提示 | 12px uppercase |
| `.meta` | 元信息 | 0.88vw uppercase |
| `.big-num` | 巨型数字 | 10vw |
| `.mid-num` | 中号数字 | 5.5vw |

### 使用示例

```css
h1 {
  font-family: var(--font-serif);
  font-size: var(--h1-size, 4.6vw);
}

.body-text {
  font-family: var(--font-sans);
  font-size: var(--body-size, 1.22vw);
}
```

---

## 2. 颜色变量

### 背景与前景

| 变量名 | 用途 | 浅色主题默认值 |
|--------|------|----------------|
| `--bg` | 主背景色 | #FFFFFF |
| `--fg` | 主前景色（文字） | #1F2937 |
| `--bg-secondary` | 次要背景色 | #F3F4F6 |

### 强调色系

| 变量名 | 用途 | 政务庄重 | 政务科技 | 科技未来 |
|--------|------|----------|----------|----------|
| `--accent` | 主强调色 | #C41E3A | #0369A1 | #06B6D4 |
| `--accent-light` | 浅强调色（背景） | #FEE2E2 | #BAE6FD | #0891B2 |
| `--accent-dark` | 深强调色 | #9B1C1C | #0284C7 | #22D3EE |
| `--accent-secondary` | 辅助强调色 | #FFD700 | #6366F1 | #8B5CF6 |

### 功能色

| 变量名 | 语义 | 默认值 |
|--------|------|--------|
| `--success` | 成功/正面 | #059669 |
| `--warning` | 警告/注意 | #D97706 |
| `--error` | 错误/负面 | #DC2626 |
| `--info` | 信息/提示 | #3B82F6 |

### 灰度阶梯

| 变量名 | 用途 | 浅色主题 | 深色主题 |
|--------|------|----------|----------|
| `--gray-1` | 最深文字 | #111827 | #F9FAFB |
| `--gray-2` | 主文字 | #1F2937 | #E5E7EB |
| `--gray-3` | 次要文字 | #374151 | #D1D5DB |
| `--gray-4` | 辅助文字 | #6B7280 | #9CA3AF |
| `--gray-5` | 占位文字 | #9CA3AF | #6B7280 |
| `--gray-6` | 边框/分割线 | #D1D5DB | #374151 |
| `--gray-7` | 最浅背景 | #E5E7EB | #1F2937 |

### 图表色板（数据专业主题）

| 变量名 | 用途 | 默认值 |
|--------|------|--------|
| `--chart-1` | 图表色1 | #58A6FF |
| `--chart-2` | 图表色2 | #3FB950 |
| `--chart-3` | 图表色3 | #F78166 |
| `--chart-4` | 图表色4 | #D29922 |
| `--chart-5` | 图表色5 | #A371F7 |
| `--chart-6` | 图表色6 | #DB61A2 |

### 渐变色

| 变量名 | 用途 | 科技未来 | 政务科技 |
|--------|------|----------|----------|
| `--gradient-start` | 渐变起始色 | #06B6D4 | #0284C7 |
| `--gradient-end` | 渐变结束色 | #8B5CF6 | #6366F1 |

### 颜色使用规范

```css
/* 主标题 - 使用强调色 */
h1 {
  color: var(--accent);
}

/* 正文 - 使用前景色 */
p {
  color: var(--fg);
}

/* 次要文字 - 使用灰色 */
.subtitle {
  color: var(--gray-3);
}

/* 边框 - 使用浅灰 */
.border {
  border-color: var(--gray-6);
}

/* 背景卡片 - 使用次要背景 */
.card {
  background: var(--bg-secondary);
}

/* 成功状态 */
.success-text {
  color: var(--success);
}

/* 警告状态 */
.warning-text {
  color: var(--warning);
}

/* 错误状态 */
.error-text {
  color: var(--error);
}
```

---

## 3. 间距系统

### 页面与元素间距

| 变量名 | 用途 | 默认值 |
|--------|------|--------|
| `--page-padding` | 页面左右内边距 | 4vw |
| `--element-gap` | 元素间垂直间距 | 2vh |
| `--grid-gap` | 网格间距 | 3vw |

### 常用高度类

| Class | 高度 | 用途 |
|-------|------|------|
| `.h-16` | 16vh | 小型面板 |
| `.h-18` | 18vh | 紧凑条形 |
| `.h-22` | 22vh | 标准网格 |
| `.h-26` | 26vh | 突出展示 |
| `.h-28` | 28vh | 大图展示 |

### 间距使用示例

```css
/* 页面内容容器 */
.page-content {
  padding: 0 var(--page-padding);
}

/* 元素间垂直间距 */
.section {
  margin-bottom: var(--element-gap);
}

/* 网格布局间距 */
.grid {
  gap: var(--grid-gap);
}

/* 固定高度图片容器 */
.frame-img.h-22 {
  height: 22vh;
}
```

---

## 4. 过渡与动画

### 过渡时长

| 变量名 | 用途 | 默认值 |
|--------|------|--------|
| `--transition-fast` | 快速过渡 | 0.2s ease |
| `--transition-normal` | 正常过渡 | 0.4s ease |
| `--transition-slow` | 慢速过渡 | 0.6s ease |

### 过渡使用示例

```css
/* 默认过渡效果 */
.button {
  transition: var(--transition-fast);
}

.button:hover {
  background: var(--accent-light);
}

/* 自定义过渡 */
.card {
  transition: all var(--transition-normal);
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}
```

---

## 5. 阴影与发光

### 阴影变量

| 变量名 | 用途 | 浅色主题默认值 | 深色主题默认值 |
|--------|------|----------------|----------------|
| `--shadow` | 基础阴影 | rgba(0,0,0,0.1) | rgba(0,0,0,0.4) |
| `--glow` | 发光效果 | rgba(196,30,58,0.2) | rgba(239,68,68,0.3) |
| `--overlay` | 遮罩层 | rgba(255,255,255,0.9) | rgba(31,41,55,0.9) |

### 阴影使用示例

```css
/* 卡片阴影 */
.card {
  box-shadow: 0 4px 6px var(--shadow);
}

/* 悬停阴影 */
.card:hover {
  box-shadow: 0 10px 15px var(--shadow);
}

/* 发光效果（科技主题） */
.highlight {
  box-shadow: 0 0 20px var(--glow);
}

/* 遮罩层 */
.modal-overlay {
  background: var(--overlay);
}

/* 玻璃态效果 */
.glass {
  background: var(--overlay);
  backdrop-filter: blur(10px);
}
```

---

## 6. 完整变量清单

### 完整:root定义示例

```css
:root {
  /* 字体定义 */
  --font-serif: 'Noto Serif SC', 'Source Han Serif SC', 'SimSun', serif;
  --font-sans: 'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC', sans-serif;
  --font-mono: 'IBM Plex Mono', 'SF Mono', 'Consolas', monospace;
  --font-display: 'Playfair Display', 'Noto Serif SC', serif;

  /* 背景与前景 */
  --bg: #FFFFFF;
  --fg: #1F2937;
  --bg-secondary: #F3F4F6;

  /* 强调色 */
  --accent: #C41E3A;
  --accent-light: #FEE2E2;
  --accent-dark: #9B1C1C;
  --accent-secondary: #FFD700;

  /* 功能色 */
  --success: #059669;
  --warning: #D97706;
  --error: #DC2626;
  --info: #3B82F6;

  /* 灰度阶梯 */
  --gray-1: #111827;
  --gray-2: #1F2937;
  --gray-3: #374151;
  --gray-4: #6B7280;
  --gray-5: #9CA3AF;
  --gray-6: #D1D5DB;
  --gray-7: #E5E7EB;

  /* 图表色板 */
  --chart-1: #58A6FF;
  --chart-2: #3FB950;
  --chart-3: #F78166;
  --chart-4: #D29922;
  --chart-5: #A371F7;
  --chart-6: #DB61A2;

  /* 渐变色 */
  --gradient-start: #06B6D4;
  --gradient-end: #8B5CF6;

  /* 透明度变量 */
  --overlay: rgba(255, 255, 255, 0.9);
  --shadow: rgba(0, 0, 0, 0.1);
  --glow: rgba(196, 30, 58, 0.2);

  /* 间距系统 */
  --page-padding: 4vw;
  --element-gap: 2vh;
  --grid-gap: 3vw;

  /* 过渡动画 */
  --transition-fast: 0.2s ease;
  --transition-normal: 0.4s ease;
  --transition-slow: 0.6s ease;
}
```

### 深色主题变量覆盖示例

```css
[data-theme="dark"] {
  --bg: #1F2937;
  --fg: #F9FAFB;
  --bg-secondary: #111827;
  --accent: #EF4444;
  --accent-light: rgba(239, 68, 68, 0.2);
  --accent-secondary: #FCD34D;
  --overlay: rgba(31, 41, 55, 0.9);
  --shadow: rgba(0, 0, 0, 0.4);
  --glow: rgba(239, 68, 68, 0.3);
  --gray-1: #F9FAFB;
  --gray-2: #E5E7EB;
  --gray-3: #D1D5DB;
  --gray-4: #9CA3AF;
  --gray-5: #6B7280;
  --gray-6: #374151;
  --gray-7: #1F2937;
}
```

---

## 快速参考卡

### 常用颜色组合

```
浅色背景 + 深色文字
  --bg: #FFFFFF → --fg: #1F2937 ✓

深色背景 + 浅色文字
  --bg: #1F2937 → --fg: #F9FAFB ✓

强调色作为文字
  color: var(--accent); ✓

次要文字使用灰色
  color: var(--gray-3); ✓

卡片使用次要背景
  background: var(--bg-secondary); ✓
```

### 常用阴影

```
基础卡片阴影
  box-shadow: 0 4px 6px var(--shadow);

悬停阴影增强
  box-shadow: 0 10px 15px var(--shadow);

科技发光效果
  box-shadow: 0 0 20px var(--glow);

玻璃态背景
  background: var(--overlay);
  backdrop-filter: blur(10px);
```

### 主题色快速切换

```html
<!-- 方法1：直接覆盖:root变量 -->
<style>
  :root {
    --accent: #0369A1; /* 政务科技 */
  }
</style>

<!-- 方法2：通过data属性切换预设 -->
<section class="slide" data-theme="dark">
  <!-- 使用深色主题变体 -->
</section>

<!-- 方法3：行内样式覆盖 -->
<h1 style="color: var(--accent);">
  自定义颜色
</h1>
```

---

## 下一步

- 查看 [references/themes.md](./references/themes.md) 了解7套预设主题
- 查看 [references/components.md](./references/components.md) 了解组件样式
- 查看 [references/layouts.md](./references/layouts.md) 了解布局样式

**灵活运用CSS变量，打造属于你的专业PPT！**