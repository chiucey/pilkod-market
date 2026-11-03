# 美团设计系统

美团的本地生活服务设计语言。

## 设计理念

美团追求**本地**、**生活**、**品质**。连接人与服务。

## 色彩系统

### 品牌色
- Primary: `#FFD100` (美团黄)
- Primary Dark: `#FFAB00`

### 辅助色
- Fresh: `#83D14F` (新鲜绿)
- Travel: `#34C2CF` (旅行蓝)
- Hotel: `#FF8255` (酒店橙)

### 背景色
- Background: `#FFFFFF`
- Background Secondary: `#F5F5F5`
- Background Dark: `#1A1A1A`

### 文字色
- Text Primary: `#333333`
- Text Secondary: `#666666`
- Text Tertiary: `#999999`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif
```

### 字号
- Display: 28px
- H1: 22px
- H2: 18px
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

### 按钮

**主要按钮**
- Background: `#FFD100`
- Color: `#333333`
- Border Radius: 8px
- Height: 40px

**次要按钮**
- Background: `#F5F5F5`
- Color: `#333333`

### 卡片

- Background: `#FFFFFF`
- Border Radius: 12px
- Padding: 16px

## 适用场景

- 🍔 外卖点餐
- 🏨 酒店预订
- 🎬 电影票
- 🚗 打车出行

## 组件示例 HTML 结构

```html
<button class="meituan-btn-primary">立即预订</button>
<div class="meituan-card">
  <img src="store.jpg" alt="商家">
  <div class="meituan-title">商家名称</div>
  <div class="meituan-price">¥99</div>
</div>
```
