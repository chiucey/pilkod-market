---
name: ultimate-design-master
description: 终极设计大师技能，涵盖所有设计领域。当用户要求进行UI设计、UX设计、视觉设计、品牌设计、网页设计、移动端设计、数据可视化设计、插画设计、图标设计、海报设计、PPT设计、包装设计，或询问设计原则、设计趋势、设计风格、设计配色、设计排版、设计布局、设计系统、响应式设计、无障碍设计、原型设计、设计规范时使用。此技能提供从创意构思到最终交付的完整设计解决方案。
---

# 终极设计大师 (Ultimate Design Master)

这是世界上最全面的设计技能，涵盖所有设计领域和方法论。

## 设计工作流程

### 阶段一：需求分析与创意探索

1. **理解用户意图** - 明确设计目标、受众群体和使用场景
2. **竞品分析** - 研究行业最佳实践和设计趋势
3. **创意头脑风暴** - 提出多个设计方向和概念

### 阶段二：设计规划

1. **选择设计风格** - 根据项目特性选择最合适的设计语言
2. **制定设计系统** - 定义色彩、字体、间距、动效等核心元素
3. **绘制线框图** - 用ASCII或草图快速验证布局结构

### 阶段三：设计执行

1. **视觉设计** - 应用设计系统进行精细化设计
2. **动效设计** - 添加微交互和过渡动画
3. **响应式适配** - 确保跨设备一致性体验

### 阶段四：验证与交付

1. **可访问性检查** - 确保符合WCAG标准
2. **设计文档化** - 编写完整的设计规范
3. **交付物准备** - 输出设计文件和资源

---

## 一、色彩设计体系

### 色彩理论核心

**三要素：**
- 色相 (Hue) - 颜色的基本属性
- 明度 (Lightness) - 颜色的明暗程度
- 饱和度 (Chroma) - 颜色的纯度或强度

**色彩心理学：**
```
红色系：激情、紧迫感、行动号召
橙色系：活力、温暖、友好
黄色系：乐观、创意、警示
绿色系：自然、成长、成功
蓝色系：信任、专业、平静
紫色系：奢华、创意、神秘
中性色：平衡、专业、通用
```

### 现代色彩定义方法

**推荐使用 oklch() 色彩空间：**
```css
/* 亮色主题 */
:root {
  --primary: oklch(55% 0.2 250);
  --secondary: oklch(65% 0.15 180);
  --accent: oklch(75% 0.2 30);
  --success: oklch(65% 0.2 145);
  --warning: oklch(75% 0.18 75);
  --error: oklch(55% 0.25 25);
  --background: oklch(98% 0.01 250);
  --foreground: oklch(15% 0.02 250);
  --muted: oklch(95% 0.01 250);
  --border: oklch(90% 0.01 250);
}

/* 深色主题 */
[data-theme="dark"] {
  --background: oklch(15% 0.02 250);
  --foreground: oklch(98% 0.01 250);
  --muted: oklch(25% 0.02 250);
  --border: oklch(35% 0.02 250);
}
```

**语义化色彩命名：**
```css
:root {
  /* 功能性色彩 */
  --color-interactive: var(--primary);
  --color-destructive: var(--error);
  --color-success: var(--success);
  --color-warning: var(--warning);

  /* 层级色彩 */
  --surface-ground: var(--background);
  --surface-elevated: oklch(100% 0 0);
  --surface-overlay: oklch(0 0 0 / 50%);

  /* 文字色彩 */
  --text-primary: var(--foreground);
  --text-secondary: oklch(55% 0.02 250);
  --text-disabled: oklch(70% 0.01 250);
  --text-inverse: oklch(0 0 0);
}
```

---

## 二、排版设计体系

### 字体选择指南

**现代无衬线字体：**
```
显示标题：Inter, Outfit, Plus Jakarta Sans, Clash Display, Satoshi
正文文本：Inter, DM Sans, Manrope, General Sans, Neue Montreal
用户界面：Inter, SF Pro, Roboto, Nunito Sans
```

**衬线字体：**
```
编辑内容：Merriweather, Source Serif Pro, Lora, Libre Baskerville
品牌标识：Playfair Display, Cormorant Garamond, Canela
```

**等宽字体：**
```
代码展示：JetBrains Mono, Geist Mono, Fira Code, IBM Plex Mono
数据表格：Tabular Figures (使用 font-variant-numeric)
```

### 字体系统定义

```css
:root {
  /* 字体栈 */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-serif: 'Merriweather', Georgia, 'Times New Roman', serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;

  /* 字号比例 (Major Third: 1.25) */
  --text-xs: 0.64rem;    /* 10.24px */
  --text-sm: 0.8rem;     /* 12.8px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.25rem;    /* 20px */
  --text-xl: 1.563rem;   /* 25px */
  --text-2xl: 1.953rem;  /* 31.25px */
  --text-3xl: 2.441rem;  /* 39px */
  --text-4xl: 3.052rem;  /* 48.8px */

  /* 行高 */
  --leading-tight: 1.1;
  --leading-snug: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* 字间距 */
  --tracking-tight: -0.025em;
  --tracking-normal: 0;
  --tracking-wide: 0.025em;
  --tracking-wider: 0.05em;
}
```

### 排版层级

```html
<!-- 文章排版 -->
<article class="prose">
  <h1>文章标题 (text-4xl, font-bold)</h1>
  <p class="lead">导语段落 (text-xl, text-muted-foreground)</p>
  <h2>二级标题 (text-2xl, font-semibold)</h2>
  <p>正文内容 (text-base, leading-relaxed)</p>
  <h3>三级标题 (text-lg, font-semibold)</h3>
  <ul>列表内容...</ul>
  <blockquote>引用内容...</blockquote>
</article>
```

---

## 三、布局设计体系

### 经典布局模式

```
┌─────────────────────────────────────────────────────┐
│                    HEADER (Sticky)                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│                     HERO SECTION                    │
│              (Full-width, 60-80vh)                  │
│                                                     │
├─────────────────────────────────────────────────────┤
│   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   │
│   │ CARD  │   │ CARD  │   │ CARD  │   │ CARD  │   │
│   └───────┘   └───────┘   └───────┘   └───────┘   │
│                    FEATURES GRID                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│              CONTENT SECTION (Wide)                  │
│         (max-width: 1200px, centered)               │
│                                                     │
├─────────────────────────────────────────────────────┤
│                     FOOTER                          │
└─────────────────────────────────────────────────────┘
```

### 栅格系统

```css
:root {
  /* 12列栅格 */
  --grid-cols: 12;
  --grid-gap: 1.5rem; /* 24px */

  /* 断点 */
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;

  /* 容器宽度 */
  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;
  --container-2xl: 1400px;
}

/* 容器 */
.container {
  width: 100%;
  max-width: var(--container-xl);
  margin-inline: auto;
  padding-inline: 1rem;
}

@media (min-width: 640px) {
  .container { padding-inline: 2rem; }
}
```

### 间距系统

```css
:root {
  /* 4px基础间距 */
  --space-0: 0;
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;     /* 8px */
  --space-3: 0.75rem;    /* 12px */
  --space-4: 1rem;       /* 16px */
  --space-5: 1.25rem;    /* 20px */
  --space-6: 1.5rem;     /* 24px */
  --space-8: 2rem;       /* 32px */
  --space-10: 2.5rem;    /* 40px */
  --space-12: 3rem;      /* 48px */
  --space-16: 4rem;      /* 64px */
  --space-20: 5rem;      /* 80px */
  --space-24: 6rem;      /* 96px */
  --space-32: 8rem;      /* 128px */
}
```

---

## 四、设计风格库

### 1. 极简主义 (Minimalism)

```css
:root {
  --minimal-bg: oklch(1 0 0);
  --minimal-fg: oklch(0.15 0 0);
  --minimal-accent: oklch(0.5 0 0);
  --minimal-border: oklch(0.92 0 0);
  --minimal-radius: 0.25rem;
  --minimal-shadow: none;
  --minimal-spacing: 2rem;
}
```

**特征：**
- 大量留白
- 有限色彩
- 简洁线条
- 功能优先

### 2. 新拟态 (Neumorphism)

```css
:root {
  --neu-bg: oklch(0.95 0.02 250);
  --neu-light: oklch(1 0 0);
  --neu-dark: oklch(0.85 0.01 250);
  --neu-radius: 1rem;
}

.neu-button {
  background: var(--neu-bg);
  border-radius: var(--neu-radius);
  box-shadow:
    8px 8px 16px var(--neu-dark),
    -8px -8px 16px var(--neu-light);
}
```

**特征：**
- 柔和阴影
- 同色调系
- 触感界面
- 微妙的深度

### 3. 玻璃拟态 (Glassmorphism)

```css
.glass-panel {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 1rem;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 0 0 1px rgba(255, 255, 255, 0.1);
}
```

**特征：**
- 半透明背景
- 模糊效果
- 光泽边框
- 渐变叠加

### 4. 新粗野主义 (Neo-Brutalism)

```css
:root {
  --brut-bg: oklch(1 0 0);
  --brut-primary: oklch(65% 0.25 55);
  --brut-secondary: oklch(70% 0.22 285);
  --brut-fg: oklch(0.1 0 0);
  --brut-border: 3px solid oklch(0.1 0 0);
  --brut-radius: 0;
  --brut-shadow: 4px 4px 0 oklch(0.1 0 0);
}

.brut-card {
  border: var(--brut-border);
  box-shadow: var(--brut-shadow);
  transform: translate(-2px, -2px);
  transition: all 100ms;
}

.brut-card:hover {
  transform: translate(0, 0);
  box-shadow: none;
}
```

**特征：**
- 鲜明色彩
- 硬边框
- 粗体阴影
- 原始质感

### 5. 渐变主义 (Gradientism)

```css
:root {
  --grad-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --grad-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  --grad-tertiary: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.vibrant-card {
  background: var(--grad-primary);
  color: white;
  border-radius: 1rem;
  padding: 2rem;
}
```

**特征：**
- 多色渐变
- 鲜艳色调
- 动态背景
- 视觉冲击

### 6. 等距设计 (Isometric Design)

```
      ┌─────┐
     /       \
    └─────┬───┘
     \   /│
      \ / │
       \ /
     LAYER 1
```

**特征：**
- 2.5D效果
- 固定角度
- 几何形状
- 立体感

---

## 五、设计系统构建

### 组件层级架构

```
Design System
├── Foundations (基础层)
│   ├── Colors (色彩)
│   ├── Typography (排版)
│   ├── Spacing (间距)
│   ├── Shadows (阴影)
│   ├── Borders (边框)
│   └── Motion (动效)
│
├── Components (组件层)
│   ├── Buttons
│   │   ├── Primary Button
│   │   ├── Secondary Button
│   │   ├── Ghost Button
│   │   └── Icon Button
│   ├── Inputs
│   │   ├── Text Input
│   │   ├── Select
│   │   ├── Checkbox
│   │   └── Radio
│   ├── Cards
│   ├── Navigation
│   └── Feedback
│
└── Patterns (模式层)
    ├── Forms
    ├── Tables
    ├── Modals
    └── Empty States
```

### 组件设计规范

**按钮组件：**

```css
/* 按钮基础 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: 0.5rem;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 150ms ease;
  min-height: 44px; /* 触摸友好 */
  min-width: 44px;
}

/* 按钮变体 */
.btn-primary {
  background: var(--primary);
  color: var(--primary-foreground);
}

.btn-primary:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: scale(0.98);
}

.btn-secondary {
  background: var(--secondary);
  color: var(--secondary-foreground);
  border-color: var(--border);
}

.btn-ghost {
  background: transparent;
  color: var(--foreground);
}

.btn-ghost:hover {
  background: var(--muted);
}

/* 按钮尺寸 */
.btn-sm { padding: 0.5rem 1rem; font-size: 0.75rem; }
.btn-lg { padding: 1rem 2rem; font-size: 1rem; }
.btn-icon { padding: 0.75rem; aspect-ratio: 1; }
```

**输入框组件：**

```css
.input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: all 150ms ease;
  min-height: 44px;
}

.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-alpha-20);
}

.input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-error {
  border-color: var(--error);
}

.input-helper {
  font-size: 0.75rem;
  color: var(--muted-foreground);
  margin-top: 0.25rem;
}

.input-error-message {
  font-size: 0.75rem;
  color: var(--error);
  margin-top: 0.25rem;
}
```

**卡片组件：**

```css
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all 200ms ease;
}

.card:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.card-body {
  padding: 1.5rem;
}

.card-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border);
  background: var(--muted);
}
```

---

## 六、动效设计体系

### 动效原则

1. **有目的** - 每个动画都应有意义
2. **快速响应** - 交互反馈应在150ms内
3. **自然流畅** - 使用缓动曲线而非线性
4. **克制使用** - 避免过度动画造成干扰

### 动效时间系统

```css
:root {
  --duration-instant: 50ms;
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --duration-slower: 600ms;

  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
```

### 动效微语法

```
button:scale(1→0.95→1) duration:100ms ease-out
hover:translateY(-2px) shadow(0→8px) duration:200ms ease-out
entrance:fadeIn opacity(0→1) translateY(20px→0) duration:400ms ease-out
exit:fadeOut opacity(1→0) duration:200ms ease-in
loading:rotate 360deg duration:1s linear infinite
skeleton:shimmer gradient position duration:1.5s ease-in-out infinite
```

### 常用动画模式

```css
/* 入场动画 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 骨架屏动画 */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--muted) 25%,
    var(--muted-light) 50%,
    var(--muted) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

/* 脉冲动画 */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 旋转动画 */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

---

## 七、响应式设计

### 断点策略

```css
/* 移动优先策略 */
/* 默认：320px - 639px */

/* 小屏幕平板 */
@media (min-width: 640px) { /* sm */ }

/* 大屏幕平板 */
@media (min-width: 768px) { /* md */ }

/* 桌面显示器 */
@media (min-width: 1024px) { /* lg */ }

/* 大屏幕桌面 */
@media (min-width: 1280px) { /* xl */ }

/* 超大屏幕 */
@media (min-width: 1536px) { /* 2xl */ }
```

### 响应式布局模式

```css
/* 移动优先网格 */
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 640px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .grid { grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
}

@media (min-width: 1280px) {
  .grid { grid-template-columns: repeat(4, 1fr); }
}

/* 响应式间距 */
.section {
  padding-block: 3rem;
}

@media (min-width: 768px) {
  .section { padding-block: 4rem; }
}

@media (min-width: 1024px) {
  .section { padding-block: 6rem; }
}
```

### 容器查询 (Container Queries)

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
  }
}
```

---

## 八、无障碍设计 (A11Y)

### WCAG 2.1 AA 标准

**可感知性：**
- 文字对比度至少 4.5:1
- 大文字对比度至少 3:1
- 非文本对比度至少 3:1
- 提供文本替代方案

**可操作性：**
- 所有功能键盘可访问
- 有足够的时间阅读内容
- 避免闪烁内容
- 提供导航和定位帮助

**可理解性：**
- 语言应该是可读的
- 操作可预测
- 防止错误

**健壮性：**
- 兼容辅助技术
- 语义化HTML

### 无障碍设计实现

```css
/* 焦点样式 */
:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

/* 跳过链接 */
.skip-link {
  position: absolute;
  top: -100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 1rem 2rem;
  background: var(--primary);
  color: var(--primary-foreground);
  z-index: 9999;
}

.skip-link:focus {
  top: 0;
}

/* 屏幕阅读器专用 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  :root {
    --border: oklch(0 0 0);
    --muted: oklch(0.95 0 0);
  }
}
```

---

## 九、数据可视化设计

### 图表设计原则

```
1. 选择正确的图表类型
   - 比较：柱状图、条形图
   - 趋势：折线图、面积图
   - 占比：饼图、环形图
   - 关系：散点图、气泡图
   - 分布：直方图、箱线图

2. 简化数据墨水比
   - 移除不必要的网格线
   - 减少装饰元素
   - 突出关键数据点

3. 清晰的标签和图例
   - 直接标注数据
   - 图例位置合理
   - 单位说明清晰
```

### 图表配色

```css
/* 数据可视化调色板 */
.chart-colors {
  --chart-1: oklch(65% 0.2 250);  /* 蓝色 */
  --chart-2: oklch(70% 0.18 145); /* 绿色 */
  --chart-3: oklch(75% 0.2 45);   /* 黄色 */
  --chart-4: oklch(60% 0.22 25);  /* 红色 */
  --chart-5: oklch(65% 0.18 285); /* 紫色 */
  --chart-6: oklch(70% 0.15 180); /* 青色 */
}
```

---

## 十、设计交付规范

### 输出物清单

**视觉设计文件：**
- Figma/Sketch 源文件
- 导出的 PNG/JPG/WebP 图片
- SVG 矢量图标和插画
- PDF 设计规范文档

**前端实现：**
- CSS 设计令牌 (JSON)
- 组件库代码
- 设计系统文档站点

**标注与说明：**
- 像素标注
- 间距说明
- 交互说明
- 状态说明

### 命名规范

```
文件夹结构：
├── design/
│   ├── foundations/
│   │   ├── colors/
│   │   ├── typography/
│   │   └── icons/
│   ├── components/
│   │   ├── button/
│   │   └── input/
│   └── patterns/
│
文件命名：
组件名称-状态.格式
例：button-primary-hover.png
    icon-arrow-down.svg
    card-feature-active.webp
```

---

## 快速参考表

| 设计维度 | 推荐值 |
|---------|--------|
| 主字体 | Inter, Plus Jakarta Sans |
| 代码字体 | JetBrains Mono, Geist Mono |
| 基础字号 | 16px |
| 基础间距 | 4px (0.25rem) |
| 圆角 | 0.5rem - 1rem (现代), 0 (粗野) |
| 阴影 | 轻柔，1-2层，避免过重 |
| 动效时长 | 150-400ms |
| 动效曲线 | ease-out (入场), ease-in (退场) |
| 触控目标 | 最小 44x44px |
| 对比度 | 4.5:1 (AA), 7:1 (AAA) |
| 色彩空间 | oklch() (现代), hsl() (兼容) |

---

*终极设计大师 - 赋能每一次创意实现*
