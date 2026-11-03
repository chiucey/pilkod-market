# 淘宝设计系统

淘宝的电商设计代表中国电商的最高水准。

## 设计理念

淘宝追求**丰富**、**热闹**、**促销**。打造购物狂欢的体验。

## 色彩系统

### 品牌色
- Primary: `#FF5000` (淘宝橙)
- Primary Hover: `#FF6A23`
- Primary Dark: `#E54600`

### 辅助色
- Success: `#52C41A`
- Warning: `#FAAD14`
- Error: `#F5222D`
- Info: `#1677FF`

### 背景色
- Background: `#FFFFFF`
- Background Secondary: `#F5F5F5`
- Background Dark: `#1C1C1C`

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
- Display: 32px
- H1: 24px
- H2: 20px
- H3: 16px
- Body: 14px
- Caption: 12px

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px

## 圆角

- sm: 4px
- md: 8px
- lg: 12px
- xl: 16px

## 组件样式

### 按钮

**主要按钮**
- Background: `#FF5000`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 40px
- Padding: 0 24px

**次要按钮**
- Background: `#FFF0E6`
- Color: `#FF5000`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E8E8E8`
- Border Radius: 4px
- Height: 40px
- Focus Border: `#FF5000`

### 商品卡片

- Background: `#FFFFFF`
- Border Radius: 8px
- Padding: 12px
- Image Aspect: 1:1

### 价格

- Current Price: `#FF5000`
- Original Price: `#999999` / line-through

## 适用场景

- 🛒 电商购物
- 🔥 促销活动
- 📱 移动电商
- 🏪 店铺装修

## 组件示例 HTML 结构

```html
<button class="taobao-btn-primary">立即购买</button>
<button class="taobao-btn-secondary">加入购物车</button>
<div class="taobao-product-card">
  <img src="product.jpg" alt="商品">
  <div class="taobao-price">
    <span class="taobao-price-current">¥99</span>
    <span class="taobao-price-original">¥199</span>
  </div>
</div>
```
