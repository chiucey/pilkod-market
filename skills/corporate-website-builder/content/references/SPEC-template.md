# 企业官网设计规范模板

## 1. Concept & Vision

定义网站的核心概念和视觉愿景。例如：打造一个具有未来科技感的现代企业官网，以「星际航行」为视觉隐喻——企业如同探索宇宙的飞船，带领客户穿越数字时代的未知领域。

## 2. Design Language

### 美学方向
- 描述整体设计风格（科技风、简约风、商务风等）
- 定义视觉隐喻和设计理念

### 色彩系统
```css
:root {
  /* 主背景色 */
  --color-bg-primary: #0a0a0f;
  --color-bg-secondary: #12121a;
  --color-surface: rgba(255, 255, 255, 0.03);
  --color-border: rgba(255, 255, 255, 0.08);

  /* 文字色 */
  --color-text-primary: #ffffff;
  --color-text-secondary: rgba(255, 255, 255, 0.6);
  --color-text-muted: rgba(255, 255, 255, 0.4);

  /* 强调色 */
  --color-accent-primary: #6366f1;
  --color-accent-secondary: #8b5cf6;
  --color-accent-glow: rgba(99, 102, 241, 0.4);

  /* 渐变 */
  --gradient-hero: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
}
```

### 字体系统
- 标题字体: `"Outfit", "Noto Sans SC", sans-serif`
- 正文字体: `"Inter", "Noto Sans SC", sans-serif`
- 字号层级: 72/48/36/24/18/16/14px

### 空间系统
- 基础间距单位: 8px
- 区块间距: 120px (移动端 64px)
- 卡片圆角: 16px
- 按钮圆角: 12px

### 动效哲学
- 入场动画: 元素从下方淡入上移
- 悬停效果: scale + 光晕增强
- 滚动视差: 背景微妙位移
- 过渡时长: 0.3s ease

## 3. Layout & Structure

### 页面架构
```
┌─────────────────────────────────────┐
│  Navigation (固定顶部，滚动透明化)    │
├─────────────────────────────────────┤
│  Hero Section (全屏，视差背景)       │
├─────────────────────────────────────┤
│  Stats Section (数据展示横条)        │
├─────────────────────────────────────┤
│  Services Section (服务项目网格)     │
├─────────────────────────────────────┤
│  About Section (左右分栏)            │
├─────────────────────────────────────┤
│  Team Section (团队成员轮播)         │
├─────────────────────────────────────┤
│  Testimonials (客户评价)             │
├─────────────────────────────────────┤
│  Contact Section (联系表单)          │
├─────────────────────────────────────┤
│  Footer (多列链接)                   │
└─────────────────────────────────────┘
```

### 响应式断点
- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px

## 4. Features & Interactions

### Navigation
- 滚动超过 100px 后背景变化
- Logo 点击返回顶部
- 导航链接悬停动画
- 移动端汉堡菜单

### Hero Section
- 动态背景效果（粒子/渐变）
- CTA 按钮组
- 向下滚动箭头

### Stats Counter
- 数字进入视口时触发计数动画
- 数值格式: 带分隔符 (1,234+)

### Service Cards
- 卡片网格布局
- 悬停: 边框发光效果

### Team Cards
- 3D 翻转效果
- 自动轮播

### Contact Form
- 实时表单验证
- 提交按钮 loading 状态
- 成功/失败 toast 提示

### 全局交互
- 平滑滚动
- 自定义滚动条
- 返回顶部按钮

## 5. Component Inventory

### Button
- Primary: 渐变背景，白色文字
- Secondary: 透明背景，边框
- States: default, hover, active, disabled

### Card
- 背景: var(--color-surface)
- 边框: 1px solid var(--color-border)
- 悬停: 边框渐变发光

### Input
- 背景: rgba(255,255,255,0.05)
- Focus: 边框渐变色，box-shadow 发光

### Toast
- 位置: 右上角
- 自动消失: 3s

## 6. Technical Approach

### 技术栈
- 框架: 原生 HTML5 + CSS3 + Vanilla JavaScript
- 构建: 单文件部署，无需打包
- 动画: CSS Animations + Intersection Observer API
- 响应式: CSS Grid + Flexbox + CSS Variables

### 性能优化
- 图片 lazy loading
- CSS will-change 优化动画
- 防抖处理滚动事件
- requestAnimationFrame

### 浏览器兼容
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 7. 代码模板

### 响应式布局模板
```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
```

### 动画入场模板
```css
.fade-in {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease;
}

.fade-in.visible {
  opacity: 1;
  transform: translateY(0);
}
```

### 数字滚动动画
```javascript
function animateCounter(element, target) {
  let current = 0;
  const increment = target / 60;
  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      element.textContent = target + '+';
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current);
    }
  }, 33);
}
```
