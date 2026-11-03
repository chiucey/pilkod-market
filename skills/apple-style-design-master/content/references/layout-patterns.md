# 布局模式库

## 页面结构

### 经典着陆页 (Classic Landing)
```
┌─────────────────────────────────────────┐
│              Navigation (固定)            │  透明背景，高度64px
├─────────────────────────────────────────┤
│                                         │
│              Hero Section               │  视口80%高度
│           (核心信息 + CTA)               │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│             Feature Grid                │  三列/四列特性展示
│                                         │
├─────────────────────────────────────────┤
│                                         │
│            Product Showcase             │  大图 + 描述
│                                         │
├─────────────────────────────────────────┤
│                                         │
│               CTA Section               │  渐变背景 + 主CTA
│                                         │
├─────────────────────────────────────────┤
│                 Footer                  │  简洁链接 + 版权
└─────────────────────────────────────────┘
```

### 全屏沉浸式 (Full Immersion)
```
┌─────────────────────────────────────────┐
│              Navigation (透明)           │
├─────────────────────────────────────────┤
│                                         │
│           Hero (100vh)                  │  全屏视觉冲击
│        背景图 + 中心文字                 │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│          Content Section                │  滚动内容
│                                         │
├─────────────────────────────────────────┤
│              Footer                     │
└─────────────────────────────────────────┘
```

### 双栏对比 (Side by Side)
```
┌─────────────────────────────────────────┐
│              Navigation                  │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │              │  │              │   │
│  │    左侧内容   │  │    右侧内容   │   │
│  │              │  │              │   │
│  │   产品图     │  │   产品图     │   │
│  │   + 描述     │  │   + 描述     │   │
│  │              │  │              │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
├─────────────────────────────────────────┤
│              Footer                     │
└─────────────────────────────────────────┘
```

## 网格系统

### 基础12列网格
```css
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
}

/* 列宽辅助类 */
.col-1 { grid-column: span 1; }
.col-2 { grid-column: span 2; }
.col-3 { grid-column: span 3; }
.col-4 { grid-column: span 4; }
.col-6 { grid-column: span 6; }
.col-8 { grid-column: span 8; }
.col-12 { grid-column: span 12; }
```

### 响应式断点
```css
/* 移动端优先断点 */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }

/* 常用响应式布局 */
.grid-2 {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}
@media (min-width: 768px) {
  .grid-2 { grid-template-columns: repeat(2, 1fr); }
}

.grid-3 {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}
@media (min-width: 768px) {
  .grid-3 { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 1024px) {
  .grid-3 { grid-template-columns: repeat(3, 1fr); }
}

.grid-4 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}
@media (min-width: 1024px) {
  .grid-4 { grid-template-columns: repeat(4, 1fr); }
}
```

## 间距系统

### 基础间距
```css
:root {
  /* 空间比例 */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  --space-8: 64px;
  --space-9: 96px;
  --space-10: 128px;

  /* 组件内间距 */
  --padding-sm: 16px;
  --padding-md: 24px;
  --padding-lg: 48px;
  --padding-xl: 96px;

  /* 区块间距 */
  --section-gap: 96px;
  --section-gap-sm: 64px;
}
```

### 垂直节奏
```css
/* 段落内间距 */
p {
  margin-top: 0;
  margin-bottom: 16px;
}

p:last-child {
  margin-bottom: 0;
}

/* 列表间距 */
ul, ol {
  margin-top: 0;
  margin-bottom: 16px;
  padding-left: 24px;
}

li {
  margin-bottom: 8px;
}

li:last-child {
  margin-bottom: 0;
}
```

## Hero Section 布局

### 居中布局 (Center Aligned)
```css
.hero {
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 96px 24px;
}

.hero-title {
  font-size: clamp(40px, 8vw, 72px);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin-bottom: 24px;
}

.hero-subtitle {
  font-size: clamp(18px, 2vw, 24px);
  color: #86868b;
  max-width: 600px;
  line-height: 1.5;
  margin-bottom: 40px;
}
```

### 左对齐布局 (Left Aligned)
```css
.hero-left {
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 96px 0;
}

.hero-content {
  max-width: 720px;
}

.hero-title {
  font-size: clamp(36px, 6vw, 64px);
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 24px;
}

.hero-subtitle {
  font-size: 20px;
  color: #86868b;
  line-height: 1.6;
  margin-bottom: 40px;
}
```

### 全屏背景布局 (Full Screen Background)
```css
.hero-fullscreen {
  position: relative;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
}

.hero-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: white;
  padding: 24px;
}
```

## 产品展示布局

### 单品大图 (Single Product Large)
```css
.product-showcase {
  display: grid;
  grid-template-columns: 1fr;
  gap: 48px;
  align-items: center;
}

@media (min-width: 768px) {
  .product-showcase {
    grid-template-columns: 1fr 1fr;
  }
}

.product-image {
  border-radius: 24px;
  overflow: hidden;
}

.product-info {
  padding: 24px 0;
}
```

### 产品画廊 (Product Gallery)
```css
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.product-card {
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}
```

### 斜向布局 (Diagonal Layout)
```css
.diagonal-section {
  position: relative;
  padding: 96px 0;
  background: #f5f5f7;
}

.diagonal-section::before {
  content: '';
  position: absolute;
  top: -50px;
  left: 0;
  right: 0;
  height: 100px;
  background: #f5f5f7;
  transform: skewY(-2deg);
}
```

## CTA 区块布局

### 居中 CTA
```css
.cta-section {
  padding: 96px 24px;
  text-align: center;
  background: linear-gradient(180deg, #f5f5f7 0%, #ffffff 100%);
}

.cta-title {
  font-size: clamp(28px, 4vw, 40px);
  font-weight: 600;
  margin-bottom: 16px;
}

.cta-subtitle {
  font-size: 18px;
  color: #86868b;
  margin-bottom: 32px;
}

.cta-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}
```

### 全宽 CTA
```css
.cta-fullwidth {
  padding: 64px 24px;
  background: #0071e3;
  color: white;
}

.cta-fullwidth .container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 24px;
}

.cta-fullwidth h2 {
  font-size: 28px;
  font-weight: 600;
  margin: 0;
}
```

## Footer 布局

### 简洁 Footer
```css
.footer {
  padding: 48px 24px 32px;
  background: #f5f5f7;
  border-top: 1px solid #d2d2d7;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 48px;
  margin-bottom: 48px;
}

.footer-bottom {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 24px;
  border-top: 1px solid #d2d2d7;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.footer-links {
  display: flex;
  gap: 24px;
}

.footer-link {
  color: #86868b;
  text-decoration: none;
  font-size: 14px;
}

.footer-link:hover {
  color: #0071e3;
}
```

### 极简 Footer
```css
.footer-minimal {
  padding: 32px 24px;
  text-align: center;
  background: #ffffff;
}

.footer-copyright {
  font-size: 14px;
  color: #86868b;
}

.footer-social {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 16px;
}
```

## 间距使用指南

### 区块间距
| 场景 | 桌面间距 | 移动端间距 |
|------|----------|------------|
| 大区块间 | 96px | 64px |
| 内容区间 | 64px | 48px |
| 小区块间 | 32px | 24px |

### 内容间距
| 场景 | 间距 |
|------|------|
| 标题与内容 | 16-24px |
| 段落间距 | 24px |
| 列表项间距 | 8-12px |
| 卡片内间距 | 24-32px |

### 边距系统
```css
/* 容器边距 */
.container-padding {
  padding-left: 24px;
  padding-right: 24px;
}

@media (min-width: 768px) {
  .container-padding {
    padding-left: 48px;
    padding-right: 48px;
  }
}

/* 内容最大宽度 */
.content-narrow { max-width: 640px; }
.content-medium { max-width: 768px; }
.content-wide { max-width: 1024px; }
.content-full { max-width: 1200px; }
```

## 视觉节奏

### 黄金比例留白
```css
.hero {
  padding-top: 120px;   /* 留白 */
  padding-bottom: 80px; /* 内容 */
}

.feature-section {
  padding-top: 80px;    /* 内容 */
  padding-bottom: 120px; /* 留白 */
}
```

### 渐进式密度
```
┌─────────────────────────────────────────┐
│           开阔留白 (Hero)                │  视觉呼吸区
├─────────────────────────────────────────┤
│                                         │
│         适度密集 (Features)              │  信息传递
│                                         │
├─────────────────────────────────────────┤
│           开阔留白 (CTA)                 │  视觉聚焦
│                                         │
├─────────────────────────────────────────┤
│         适度密集 (Footer)                │  信息汇总
└─────────────────────────────────────────┘
```
