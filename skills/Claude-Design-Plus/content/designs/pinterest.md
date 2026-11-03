# Pinterest Design System

Pinterest 的设计代表视觉发现的艺术。

## 设计理念

Pinterest 追求**发现**、**灵感**、**美学**。让用户沉浸在视觉灵感中。

## 色彩系统

### 品牌色
- Primary: `#E60023` (Pinterest 红)
- Primary Hover: `#AD081B`
- Primary Dark: `#9B0618`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#FAFAFA`
- Background Tertiary: `#EFEFEF`

#### 深色模式
- Background Dark: `#0D0D0D`
- Background Dark Secondary: `#1A1A1A`

### 文字色

#### 浅色模式
- Text Primary: `#111111`
- Text Secondary: `#5F5F5F`
- Text Tertiary: `#8E8E8E`

#### 深色模式
- Text Dark Primary: `#FFFFFF`
- Text Dark Secondary: `#A8A8A8`
- Text Dark Tertiary: `#767676`

### 功能色
- Red: `#E60023`
- Dark Red: `#9B0618`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif
```

### 中文
```
'PingFang SC', 'Microsoft YaHei', sans-serif
```

### 字号
- Display: 28px / 700
- H1: 22px / 600
- H2: 18px / 600
- Body: 14px / 400
- Small: 12px / 400
- Pin Title: 16px / 600

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px
- 2xl: 32px

## 圆角

- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px
- pin: 16px

## 组件样式

### Pin 卡片

- Border Radius: 16px
- Background: `#FFFFFF`
- Shadow: `0 1px 2px rgba(0, 0, 0, 0.05)`
- Hover Shadow: `0 4px 12px rgba(0, 0, 0, 0.15)`

### 保存按钮

- Background: `#E60023`
- Color: `#FFFFFF`
- Border Radius: 20px
- Height: 36px
- Padding: 0 16px
- Font Weight: 600

### 输入框

- Background: `#F1F1F1`
- Border: none
- Border Radius: 20px
- Height: 40px
- Padding: 0 16px
- Focus Background: `#FFFFFF`
- Focus Border: 2px `#E60023`

### 搜索栏

- Background: `#EFEFEF`
- Border Radius: 24px
- Height: 48px
- Icon: 搜索图标 `#5F5F5F`

### 导航栏

- Background: `#FFFFFF`
- Height: 56px
- Border Bottom: 1px solid `#EFEFEF`

## 设计注意事项

1. **视觉优先** - 图片是核心
2. **瀑布流** - Masonry 布局
3. **保存功能** - 红心是核心交互
4. **发现感** - 无限滚动探索

## 适用场景

- 🎨 视觉灵感
- 🛍️ 电商发现
- 📸 图片收藏
- 💡 创意灵感

## 组件示例 HTML 结构

```html
<div class="pinterest-pin">
  <img class="pinterest-pin-image" src="image.jpg" alt="Pin">
  <button class="pinterest-save-btn">保存</button>
</div>
<div class="pinterest-search">
  <input type="text" placeholder="搜索">
</div>
<nav class="pinterest-nav">
  <span class="pinterest-logo">P</span>
</nav>
```
