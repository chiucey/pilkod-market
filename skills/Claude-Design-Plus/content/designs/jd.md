# 京东设计系统

京东的电商设计代表品质与效率。

## 设计理念

京东追求**品质**、**速度**、**可靠**。强调多快好省。

## 色彩系统

### 品牌色
- Primary: `#E2231A` (京东红)
- Primary Hover: `#C81E1A`
- Primary Dark: `#A91512`

### 辅助色
- Success: `#52C41A`
- Warning: `#FF9A00`
- Error: `#E2231A`
- Info: `#1677FF`

### 背景色
- Background: `#FFFFFF`
- Background Secondary: `#F7F7F7`
- Background Dark: `#1A1A1A`

### 文字色
- Text Primary: `#1A1A1A`
- Text Secondary: `#666666`
- Text Tertiary: `#999999`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif
```

### 字号
- Display: 32px
- H1: 24px
- H2: 20px
- H3: 16px
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
- Background: `#E2231A`
- Color: `#FFFFFF`
- Border Radius: 4px
- Height: 40px
- Padding: 0 24px

**次要按钮**
- Background: `#FFF`
- Color: `#E2231A`
- Border: 1px solid `#E2231A`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E8E8E8`
- Border Radius: 4px
- Height: 40px
- Focus Border: `#E2231A`

### 商品卡片

- Background: `#FFFFFF`
- Border Radius: 4px
- Padding: 12px
- Hover: shadow

## 适用场景

- 🛒 电商购物
- 📦 物流配送
- 💳 京东支付
- 🏪 京东到家

## 组件示例 HTML 结构

```html
<button class="jd-btn-primary">立即购买</button>
<button class="jd-btn-secondary">加入购物车</button>
<div class="jd-product-card">
  <img src="product.jpg" alt="商品">
  <div class="jd-price">¥99</div>
</div>
```
