# 米哈游设计系统

米哈游的游戏设计美学。

## 设计理念

米哈游追求**美学**、**沉浸**、**情感**。打造二次元游戏的极致体验。

## 色彩系统

### 品牌色
- Primary: `#31A4FF` (米哈游蓝)
- Primary Hover: `#4AB4FF`
- Primary Dark: `#218FDB`

### 辅助色
- Accent: `#FF31A4` (粉色)
- Gold: `#FFD700`

### 背景色

#### 浅色模式
- Background: `#FAFAFA`
- Background Secondary: `#F5F5F7`

#### 深色模式
- Background Dark: `#0D0D0D`
- Background Dark Secondary: `#1A1A1A`
- Background Dark Card: `#252525`

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
'Genshin', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 中文
```
'Hywh', 'PingFang SC', 'Microsoft YaHei', sans-serif
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

### 角色卡片

- Background: `#1A1A1A`
- Border Radius: 12px
- Image Aspect: 3:4
- Hover: glow effect

### 按钮

**主要按钮**
- Background: `#31A4FF`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 44px

**次要按钮**
- Background: `#2A2A2A`
- Color: `#FFFFFF`

### 抽卡界面

- Background: 渐变
- Border Radius: 16px
- 五星保底: 金色光效

## 适用场景

- 🎮 手游
- 🕹️ 原神
- 👥 角色展示
- 🎁 抽卡系统

## 组件示例 HTML 结构

```html
<div class="mihoyo-character-card">
  <img class="mihoyo-character" src="character.jpg" alt="角色">
  <div class="mihoyo-rarity five-star">五星</div>
  <h3>角色名</h3>
</div>
<button class="mihoyo-btn-primary">祈愿</button>
<button class="mihoyo-btn-secondary">角色详情</button>
```
