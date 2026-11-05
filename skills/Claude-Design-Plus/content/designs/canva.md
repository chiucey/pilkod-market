# Canva Design System

Canva 的在线设计平台设计美学。

## 设计理念

Canva 追求**创意**、**简单**、**人人可用**。让设计触手可及。

## 色彩系统

### 品牌色
- Primary: `#00C4CC` (Canva 青)
- Primary Hover: `#00B5BA`
- Primary Dark: `#009B9F`

### 辅助色
- Purple: `#7B61FF`
- Pink: `#FF61DC`
- Orange: `#FF8B4C`
- Yellow: `#FFD52E`
- Green: `#00C853`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F5F5F5`
- Background Tertiary: `#EEEEEE`

#### 深色模式
- Background Dark: `#1A1A1A`
- Background Dark Secondary: `#242424`

### 文字色

#### 浅色模式
- Text Primary: `#2D2D2D`
- Text Secondary: `#666666`
- Text Tertiary: `#999999`

#### 深色模式
- Text Dark Primary: `#FFFFFF`
- Text Dark Secondary: `#A0A0A0`
- Text Dark Tertiary: `#6B6B6B`

## 字体

### 字体栈
```
'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 32px / 700
- H1: 24px / 600
- H2: 20px / 600
- H3: 16px / 600
- Body: 14px / 400
- Caption: 12px / 400

## 间距系统

基于 8px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px

## 圆角

- sm: 4px
- md: 8px
- lg: 12px
- xl: 16px

## 组件样式

### 按钮

**主要按钮**
- Background: `#00C4CC`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 40px
- Padding: 0 24px

**次要按钮**
- Background: `#F5F5F5`
- Color: `#2D2D2D`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E0E0E0`
- Border Radius: 8px
- Height: 40px
- Focus Border: `#00C4CC`

### 模板卡片

- Background: `#FFFFFF`
- Border Radius: 12px
- Padding: 16px
- Hover: shadow

## 适用场景

- 🎨 在线设计
- 📄 文档制作
- 🖼️ 海报设计
- 📱 社交媒体

## 组件示例 HTML 结构

```html
<button class="canva-btn-primary">创建设计</button>
<button class="canva-btn-secondary">浏览模板</button>
<div class="canva-template-card">
  <img src="template.jpg" alt="模板">
  <h3>模板标题</h3>
</div>
```
