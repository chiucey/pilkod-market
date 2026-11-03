# Premium Frontend Design Patterns

高级感前端设计模式参考手册

---

## 一、配色方案库

### 1.1 深色主题配色

```
背景主色: #0a0a0f (深空黑，非纯黑)
背景次色: #111118 (卡片背景)
边框色: rgba(255, 255, 255, 0.08)
文字主色: #fafafa (接近纯白但有呼吸感)
文字次色: #a0a0a0
文字辅助: #666666

渐变方案:
- 紫色渐变: linear-gradient(135deg, #6366f1, #8b5cf6)
- 蓝色渐变: linear-gradient(135deg, #3b82f6, #06b6d4)
- 绿松石: linear-gradient(135deg, #10b981, #14b8a6)
```

### 1.2 浅色主题配色

```
背景主色: #fafafa
背景次色: #ffffff
边框色: rgba(0, 0, 0, 0.06)
文字主色: #0a0a0f
文字次色: #525252
文字辅助: #a3a3a3

渐变方案:
- 柔粉: linear-gradient(135deg, #fdf2f8, #fce7f3)
- 淡蓝: linear-gradient(135deg, #eff6ff, #e0e7ff)
- 米白: linear-gradient(135deg, #fefce8, #fef9c3)
```

### 1.3 品牌色参考

```
Linear 风格: #5e6ad2 (靛蓝紫)
Vercel 风格: #000000 (极简黑)
Stripe 风格: #635bff (明亮紫)
GitHub 风格: #0969da (科技蓝)
Apple 风格: #1d1d1f (深灰)
```

---

## 二、字体系统

### 2.1 推荐字体组合

```
现代科技感:
- 标题: Inter (700, 600)
- 正文: Inter (400, 500)
- 代码: JetBrains Mono

优雅高端:
- 标题: Playfair Display (600, 700)
- 正文: DM Sans (400, 500)
- 辅助: Cormorant Garamond

创意活力:
- 标题: Clash Display (600, 700)
- 正文: Satoshi (400, 500)

极简日式:
- 标题: Noto Sans JP (600)
- 正文: Noto Sans SC (400)
```

### 2.2 字号层级

```css
:root {
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
  --text-5xl: 3rem;      /* 48px */
  --text-6xl: 3.75rem;  /* 60px */
}
```

---

## 三、布局模式

### 3.1 非对称网格

```css
/* 不均匀两列 */
.grid-asymmetric {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 4rem;
}

/* 错落三列 */
.grid-staggered {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.grid-staggered > *:nth-child(1) { margin-top: 0; }
.grid-staggered > *:nth-child(2) { margin-top: 3rem; }
.grid-staggered > *:nth-child(3) { margin-top: 1.5rem; }

/* 瀑布流感 */
.grid-masonry {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-auto-rows: 20px;
}
```

### 3.2 容器宽度策略

```css
/* 紧凑内容 */
.container-narrow { max-width: 640px; margin: 0 auto; }

/* 标准内容 */
.container-base { max-width: 1024px; margin: 0 auto; }

/* 宽幅展示 */
.container-wide { max-width: 1280px; margin: 0 auto; }

/* 全幅出血 */
.container-full { max-width: 1440px; margin: 0 auto; }
```

### 3.3 留白节奏

```css
/* 密集区 */
.section-dense { padding: 2rem 0; }

/* 标准区 */
.section-normal { padding: 4rem 0; }

/* 呼吸区 */
.section-spacious { padding: 8rem 0; }
```

---

## 四、阴影系统

### 4.1 多层阴影

```css
/* 微妙漂浮 */
.shadow-subtle {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.05),
    0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 标准卡片 */
.shadow-card {
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.08),
    0 4px 16px rgba(0, 0, 0, 0.06);
}

/* 悬浮效果 */
.shadow-elevated {
  box-shadow:
    0 2px 4px rgba(0, 0, 0, 0.02),
    0 8px 24px rgba(0, 0, 0, 0.08),
    0 24px 48px rgba(0, 0, 0, 0.04);
}

/* 发光边框 */
.shadow-glow {
  box-shadow:
    0 0 0 1px rgba(99, 102, 241, 0.1),
    0 0 20px rgba(99, 102, 241, 0.15);
}
```

### 4.2 彩色阴影

```css
.shadow-purple {
  box-shadow:
    0 4px 16px rgba(139, 92, 246, 0.15),
    0 12px 40px rgba(139, 92, 246, 0.1);
}

.shadow-blue {
  box-shadow:
    0 4px 16px rgba(59, 130, 246, 0.15),
    0 12px 40px rgba(59, 130, 246, 0.1);
}
```

---

## 五、圆角系统

### 5.1 差异化圆角

```css
:root {
  --radius-sm: 4px;   /* 小按钮、标签 */
  --radius-md: 8px;   /* 输入框、小卡片 */
  --radius-lg: 12px;  /* 中等卡片 */
  --radius-xl: 16px;  /* 大卡片 */
  --radius-2xl: 24px; /* Hero 卡片 */
  --radius-full: 9999px; /* 圆形、药丸 */
}
```

---

## 六、边框与轮廓

### 6.1 半透明边框

```css
.border-subtle {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
}

.border-hover {
  border: 1px solid rgba(255, 255, 255, 0.12);
  transition: border-color 0.2s ease;
}

.border-hover:hover {
  border-color: rgba(255, 255, 255, 0.2);
}
```

### 6.2 渐变边框

```css
.border-gradient {
  position: relative;
  background: #111118;
  border-radius: 16px;
}

.border-gradient::before {
  content: '';
  position: absolute;
  inset: 0;
  padding: 1px;
  border-radius: inherit;
  background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}
```

### 6.3 发光效果

```css
.glow {
  box-shadow:
    0 0 20px rgba(99, 102, 241, 0.3),
    0 0 40px rgba(99, 102, 241, 0.2),
    0 0 60px rgba(99, 102, 241, 0.1);
}
```

---

## 七、动效系统

### 7.1 入场动画

```css
/* 淡入上浮 */
@keyframes fade-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 交错入场 */
.fade-up-stagger > * {
  opacity: 0;
  animation: fade-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.fade-up-stagger > *:nth-child(1) { animation-delay: 0ms; }
.fade-up-stagger > *:nth-child(2) { animation-delay: 100ms; }
.fade-up-stagger > *:nth-child(3) { animation-delay: 200ms; }
.fade-up-stagger > *:nth-child(4) { animation-delay: 300ms; }
```

### 7.2 悬停交互

```css
/* 上浮 + 阴影 */
.hover-lift {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow:
    0 8px 24px rgba(0, 0, 0, 0.12),
    0 24px 48px rgba(0, 0, 0, 0.08);
}

/* 边框渐变 */
.hover-border-glow {
  position: relative;
  transition: transform 0.3s ease;
}

.hover-border-glow::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
}

.hover-border-glow:hover::before {
  opacity: 1;
}

.hover-border-glow:hover {
  transform: translateY(-2px);
}
```

### 7.3 背景动效

```css
/* 渐变流动 */
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.gradient-animated {
  background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899, #f43f5e);
  background-size: 300% 300%;
  animation: gradient-shift 8s ease infinite;
}
```

### 7.4 时间曲线

```css
/* 标准缓出 */
transition: all 0.3s ease-out;

/* 弹性效果 */
transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);

/* 弹性按压 */
transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
```

---

## 八、组件示例

### 8.1 高级感卡片

```html
<div class="premium-card">
  <div class="premium-card__icon">
    <svg>...</svg>
  </div>
  <h3 class="premium-card__title">Title</h3>
  <p class="premium-card__desc">Description text...</p>
  <a href="#" class="premium-card__link">
    Learn more
    <svg class="arrow">...</svg>
  </a>
</div>
```

```css
.premium-card {
  position: relative;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.premium-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.premium-card:hover {
  transform: translateY(-4px);
  border-color: rgba(99, 102, 241, 0.2);
  box-shadow:
    0 8px 24px rgba(0, 0, 0, 0.2),
    0 24px 48px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(99, 102, 241, 0.1);
}

.premium-card:hover::before {
  opacity: 1;
}
```

### 8.2 渐变按钮

```html
<button class="btn-gradient">
  <span class="btn-gradient__text">Get Started</span>
  <span class="btn-gradient__icon">
    <svg>...</svg>
  </span>
</button>
```

```css
.btn-gradient {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  font-size: 0.9375rem;
  font-weight: 500;
  color: white;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
}

.btn-gradient::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.btn-gradient:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
}

.btn-gradient:hover::before {
  opacity: 1;
}

.btn-gradient__text,
.btn-gradient__icon {
  position: relative;
  z-index: 1;
}
```

### 8.3 玻璃态导航栏

```css
.nav-glass {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 1rem 2rem;
  background: rgba(10, 10, 15, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
```

---

## 九、案例解析

### 9.1 Linear 风格特征

- 深色背景 + 紫色强调
- 密集的微交互
- 卡片带发光边框
- 不对称布局
- 大量留白

### 9.2 Vercel 风格特征

- 极简黑白
- 大胆的版式
- 几何形状装饰
- 网格系统严谨
- 动效克制但精致

### 9.3 Stripe 风格特征

- 渐变色系统
- 层次分明的卡片
- 流畅的滚动动画
- 精致的阴影
- 色彩克制但精准

---

## 十、检查清单

生成代码前自检：

```
□ 配色：没有纯黑/纯白？
□ 圆角：大元素大圆角，小元素小圆角？
□ 阴影：多层阴影叠加？
□ 渐变：同色系或相邻色？
□ 布局：非对称/错落感？
□ 动效：交切入场 + 悬停上浮？
□ 边框：半透明或发光效果？
□ 字体：使用 Google Fonts？
□ 过渡：不是 transition: all？
□ 响应式：移动端优先？
```
