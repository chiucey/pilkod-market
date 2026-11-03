# Epic Games Design System

Epic Games 的游戏平台设计美学。

## 设计理念

Epic Games 追求**游戏**、**沉浸**、**Epic**。打造史诗级的游戏体验。

## 色彩系统

### 品牌色
- Primary: `#2F2D2E` (Epic 黑)
- Primary Light: `#3D3B3C`

### 强调色
- Accent: `#0078F2` (Epic 蓝)
- Accent Hover: `#1A8AFF`

### 背景色

#### 深色模式 (主模式)
- Background: `#0A0A0A`
- Background Secondary: `#1A1A1A`
- Background Tertiary: `#2F2D2E`
- Background Card: `#1A1A1A`

### 文字色

#### 深色模式
- Text Primary: `#FFFFFF`
- Text Secondary: `#B3B3B3`
- Text Tertiary: `#6B6B6B`

### 功能色
- Success: `#2EA043`
- Warning: `#F5A623`
- Error: `#EF4444`

## 字体

### 字体栈
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 28px / 700
- H1: 22px / 600
- H2: 18px / 600
- Body: 14px / 400
- Small: 12px / 400

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

## 组件样式

### 游戏卡片

- Background: `#1A1A1A`
- Border Radius: 8px
- Hover: scale(1.02)
- Image Aspect: 16:9

### 按钮

**Primary 按钮**
- Background: `#0078F2`
- Color: `#FFFFFF`
- Border Radius: 4px
- Height: 40px
- Padding: 0 24px

**Secondary 按钮**
- Background: `#2F2D2E`
- Color: `#FFFFFF`

### 下载按钮

- Background: `#0078F2`
- Color: `#FFFFFF`
- Border Radius: 4px
- Height: 48px

## 适用场景

- 🎮 游戏商城
- 🏆 游戏平台
- 📦 游戏启动器
- 🎁 免费游戏

## 组件示例 HTML 结构

```html
<div class="epic-game-card">
  <img class="epic-game-image" src="game.jpg" alt="游戏">
  <div class="epic-game-info">
    <h3>游戏标题</h3>
    <span class="epic-price">免费</span>
  </div>
</div>
<button class="epic-btn-primary">安装</button>
<button class="epic-btn-secondary">更多</button>
```
