# Vercel Design System

Vercel 代表极简、速度和现代前端美学。

## 设计理念

Vercel 设计追求**极简**、**速度感**、**技术美学**。适合现代 Web 产品和开发者工具。

## 色彩系统

### 主色
- Primary: `#000000` (纯黑)
- Primary Light: `#333333`

### 强调色
- Accent: `#FFFFFF` (白色)
- Accent Secondary: `#E8E8E8`

### 语义色
- Success: `#10B981`
- Warning: `#F59E0B`
- Error: `#EF4444`

### 边框
- Border: `#E5E5E5`
- Border Dark: `#333333`

### 文字
- Text: `#000000`
- Text Secondary: `#666666`
- Text Muted: `#999999`

### 背景
- Background: `#FFFFFF`
- Background Dark: `#000000`
- Background Subtle: `#F9F9F9`

## 字体

### 字体栈
```
'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif
```

### 无衬线 (Inter)
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 代码字体
```
'Geist Mono', 'SF Mono', Monaco, 'Cascadia Code', Consolas, monospace
```

### 字号
- Display: 64px / 72px / -0.03em
- H1: 48px / 56px / -0.02em
- H2: 36px / 44px / -0.02em
- H3: 24px / 32px / -0.01em
- H4: 20px / 28px / 0
- Body: 16px / 24px / 0
- Caption: 14px / 20px / 0
- Micro: 12px / 16px / 0

### 字重
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

## 间距系统

基于 4px 网格：
- 0.5: 2px
- 1: 4px
- 2: 8px
- 3: 12px
- 4: 16px
- 6: 24px
- 8: 32px
- 10: 40px
- 12: 48px
- 16: 64px
- 20: 80px
- 24: 96px

## 圆角

- none: 0
- sm: 4px
- md: 8px
- lg: 12px
- xl: 16px
- 2xl: 24px
- 3xl: 32px
- full: 9999px

## 阴影

### 边框式阴影
```css
box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.1);
```

### 悬停阴影
```css
box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.3);
```

### 黑色投影
```css
box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
```

## 组件样式

### 按钮

**主要按钮 (黑色)**
- Background: `#000000`
- Color: `#FFFFFF`
- Border: none
- Border Radius: 6px
- Padding: 12px 20px
- Font Weight: 500
- Font Size: 14px
- Hover: `#333333`

**次要按钮 (白色)**
- Background: `#FFFFFF`
- Color: `#000000`
- Border: 1px solid `#E5E5E5`
- Hover: `#F5F5F5`

**幽灵按钮**
- Background: transparent
- Color: `#666666`
- Hover: `#000000`

**聚焦样式**
```css
outline: 2px solid #000000;
outline-offset: 2px;
```

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E5E5E5`
- Border Radius: 6px
- Padding: 10px 14px
- Font Size: 14px
- Focus Border: `#000000`

### 卡片

- Background: `#FFFFFF`
- Border: 1px solid `#E5E5E5`
- Border Radius: 12px
- Padding: 24px

### 代码块

- Background: `#000000`
- Color: `#FFFFFF`
- Border Radius: 8px
- Padding: 24px
- Font Family: Geist Mono

### 导航

- Height: 64px
- Border Bottom: 1px solid `#E5E5E5`
- Logo Size: 24px

## 设计注意事项

1. **极简主义** - 少即是多
2. **黑白优先** - 主色调黑白
3. **清晰对比** - 高对比度
4. **技术感** - 代码块、开发者风格
5. **微动效** - 微妙的状态变化

## 适用场景

- 🌐 前端项目
- 🚀 SaaS 产品
- 💻 开发者工具
- 📊 技术文档
- 🎨 创意作品集

## 组件示例 HTML 结构

```html
<!-- 按钮 -->
<button class="vercel-btn vercel-btn-primary">Deploy</button>
<button class="vercel-btn vercel-btn-secondary">Learn More</button>

<!-- 输入框 -->
<input class="vercel-input" type="email" placeholder="email@example.com">

<!-- 卡片 -->
<div class="vercel-card">
  <h3 class="vercel-card-title">Title</h3>
  <p class="vercel-card-description">Description</p>
</div>

<!-- 代码块 -->
<pre class="vercel-code">npm install vercel</pre>

<!-- 导航栏 -->
<nav class="vercel-nav">
  <span class="vercel-logo">▶</span>
  <span>Vercel</span>
</nav>
```
