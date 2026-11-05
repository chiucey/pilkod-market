# 腾讯游戏设计系统

腾讯游戏的设计美学。

## 设计理念

腾讯游戏追求**竞技**、**社交**、**娱乐**。打造全民游戏体验。

## 色彩系统

### 品牌色
- Primary: `#F73131` (腾讯红)
- Primary Hover: `#E62E2E`
- Primary Dark: `#CC2A2A`

### 辅助色
- Gold: `#FFB800`
- Blue: `#0080FF`
- Green: `#00A650`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F5F5F5`
- Background Dark: `#1A1A1A`

#### 深色模式
- Background Dark Primary: `#0D0D0D`
- Background Dark Secondary: `#1A1A1A`

### 文字色

#### 浅色模式
- Text Primary: `#1A1A1A`
- Text Secondary: `#6B6B6B`
- Text Tertiary: `#9B9B9B`

#### 深色模式
- Text Dark Primary: `#FFFFFF`
- Text Dark Secondary: `#A0A0A0`
- Text Dark Tertiary: `#6B6B6B`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Microsoft YaHei', sans-serif
```

### 字号
- Display: 32px
- H1: 24px
- H2: 20px
- Body: 14px
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

## 组件样式

### 游戏卡片

- Background: `#FFFFFF`
- Border Radius: 12px
- Image Aspect: 16:9
- Hover: scale(1.02)

### 按钮

**主要按钮**
- Background: `#F73131`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 44px

**次要按钮**
- Background: `#F5F5F5`
- Color: `#1A1A1A`

### 荣誉标签

- VIP: 金色 `#FFB800`
- 年费: 红色渐变

## 适用场景

- 🎮 游戏平台
- 🏆 电竞赛事
- 👥 游戏社交
- 🎁 礼包系统

## 组件示例 HTML 结构

```html
<div class="tencent-game-card">
  <img class="tencent-game-image" src="game.jpg" alt="游戏">
  <div class="tencent-game-info">
    <h3>游戏名称</h3>
    <span class="tencent-game-tag">热门</span>
  </div>
</div>
<button class="tencent-btn-primary">开始游戏</button>
<button class="tencent-btn-secondary">游戏详情</button>
<div class="tencent-vip-badge">VIP</div>
```
