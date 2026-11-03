# 小米 MIUI Design System

小米 MIUI 的设计语言。

## 设计理念

MIUI 追求**简约**、**年轻**、**智能**。为发烧而生的用户体验。

## 色彩系统

### 品牌色
- Primary: `#FF6600` (小米橙)
- Primary Hover: `#FF8533`
- Primary Dark: `#CC5200`

### 辅助色
- Success: `#1ABA1A`
- Warning: `#FFC107`
- Error: `#F5222D`
- Info: `#007AFF`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F5F5F5`
- Background Tertiary: `#EEEEEE`

#### 深色模式
- Background Dark: `#1A1A1A`
- Background Dark Secondary: `#242424`
- Background Dark Tertiary: `#2D2D2D`

### 文字色

#### 浅色模式
- Text Primary: `#1A1A1A`
- Text Secondary: `#757575`
- Text Tertiary: `#A6A6A6`

#### 深色模式
- Text Dark Primary: `#FFFFFF`
- Text Dark Secondary: `#A0A0A0`
- Text Dark Tertiary: `#6B6B6B`

## 字体

### 字体栈
```
'MI Lan Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 中文
```
'MI Lan Pro', 'PingFang SC', 'Microsoft YaHei', sans-serif
```

### 字号
- Display: 36px
- H1: 28px
- H2: 22px
- H3: 18px
- Body: 16px
- Caption: 12px

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
- full: 9999px

## 组件样式

### 按钮

**主要按钮**
- Background: `#FF6600`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 44px
- Padding: 0 24px

**次要按钮**
- Background: `#F5F5F5`
- Color: `#1A1A1A`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E0E0E0`
- Border Radius: 8px
- Height: 44px
- Focus Border: `#FF6600`

### 卡片

- Background: `#FFFFFF`
- Border Radius: 12px
- Padding: 16px

## 适用场景

- 📱 MIUI 系统
- 🏠 智能家居
- 📺 电视系统
- ⚡ 性能优化

## 组件示例 HTML 结构

```html
<button class="miui-btn-primary">主要</button>
<button class="miui-btn-secondary">次要</button>
<input class="miui-input" type="text" placeholder="输入">
<div class="miui-card">
  <h3>标题</h3>
  <p>内容</p>
</div>
```
