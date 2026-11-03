# Shopify Design System

Shopify 的设计代表电商平台的最佳实践。

## 设计理念

Shopify 追求**商业**、**信任**、**增长**。帮助商家成功卖出商品。

## 色彩系统

### 品牌色
- Primary: `#008060` (Shopify 绿)
- Primary Hover: `#006E52`
- Primary Dark: `#004C3F`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#FBFBFC`
- Background Tertiary: `#F6F6F7`
- Background Dark: `#1A1A1A`

#### 深色模式
- Background Dark Primary: `#0F0F0F`
- Background Dark Secondary: `#1A1A1A`
- Background Dark Card: `#242424`

### 文字色

#### 浅色模式
- Text Primary: `#212B36`
- Text Secondary: `#637381`
- Text Tertiary: `#919EAB`

#### 深色模式
- Text Dark Primary: `#E3E3E3`
- Text Dark Secondary: `#8C8C8C`
- Text Dark Tertiary: `#6B6B6B`

### 功能色
- Success: `#008060`
- Warning: `#B98900`
- Error: `#D72B2B`
- Info: `#0064FF`

### 销售色
- Sale: `#DF2700`
- Discount: `#008060`

## 字体

### 字体栈
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 32px / 600
- H1: 28px / 600
- H2: 24px / 600
- H3: 20px / 600
- H4: 16px / 600
- Body: 15px / 400
- Small: 13px / 400

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px

## 圆角

- sm: 4px
- md: 8px
- lg: 12px
- xl: 16px
- full: 9999px

## 组件样式

### 按钮

**Primary 按钮**
- Background: `#008060`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 40px
- Padding: 0 20px
- Font Weight: 500

**Secondary 按钮**
- Background: `#F6F6F7`
- Color: `#212B36`
- Border: 1px solid `#C4CDD5`

**Outline 按钮**
- Background: transparent
- Color: `#008060`
- Border: 1px solid `#008060`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#C4CDD5`
- Border Radius: 8px
- Height: 40px
- Padding: 0 12px
- Focus Border: `#008060`
- Focus Shadow: `0 0 0 3px rgba(0, 128, 96, 0.1)`

### 卡片

- Background: `#FFFFFF`
- Border: 1px solid `#E3E4E8`
- Border Radius: 12px
- Padding: 20px

### 产品卡片

- Image Aspect Ratio: 1:1
- Border Radius: 12px
- Title: 15px / 600
- Price: 15px / 600
- Compare Price: 13px / 400 / `#919EAB` / line-through

### 导航栏

- Background: `#FFFFFF`
- Height: 64px
- Border Bottom: 1px solid `#E3E4E8`

## 设计注意事项

1. **商业导向** - 促进销售是核心目标
2. **信任建立** - 绿色代表信任和安全
3. **清晰定价** - 价格信息突出显示
4. **移动优先** - 移动端体验重要

## 适用场景

- 🛒 电商平台
- 📦 商品展示
- 🛍️ 购物车
- 💳 结算流程

## 组件示例 HTML 结构

```html
<div class="shopify-product-card">
  <img class="shopify-product-image" src="product.jpg" alt="商品图">
  <h3 class="shopify-product-title">商品标题</h3>
  <div class="shopify-product-price">
    <span class="shopify-price">¥299</span>
    <span class="shopify-compare-price">¥399</span>
  </div>
  <button class="shopify-btn-primary">加入购物车</button>
</div>
<button class="shopify-btn-primary">购买</button>
<button class="shopify-btn-secondary">次要操作</button>
<input class="shopify-input" type="text" placeholder="搜索">
```
