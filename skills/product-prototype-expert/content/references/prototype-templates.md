# Product Prototype Templates

## Template 1: E-commerce App

**Input**: "E-commerce App: Login, Home (Search + Banner + Recommendations), Product Detail (Image + Price + Reviews), Cart (List + Checkout)"

**Output**:
```
# E-commerce App Prototype Framework

## Overview
- Product Type: E-commerce Mobile App
- Platform: iOS / Android
- Total Pages: 6 pages

---

## Page 1: Login Page

### Core Functions
- Phone number input
- Password input
- SMS verification login
- Social login (WeChat, Alipay)
- Forgot password link

### Wireframe
```
┌─────────────────────────┐
│                         │
│         [LOGO]          │  <- Top 1/6, centered
│                         │
│   ┌─────────────────┐   │
│   │ +86 | Phone     │   │  <- Input fields
│   └─────────────────┘   │
│                         │
│   ┌─────────────────┐   │
│   │ Password        │   │
│   └─────────────────┘   │
│                         │
│   ┌─────────────────┐   │
│   │   LOGIN         │   │  <- Primary button (48px)
│   └─────────────────┘   │
│                         │
│   [Register]  [Forgot?] │  <- Links
│                         │
└─────────────────────────┘
```

---

## Page 2: Home Page

### Core Functions
- Search bar with voice input
- Banner carousel (3-5 images)
- Category icons (8-10 categories)
- Flash sale section
- Product recommendations grid

### Wireframe
```
┌─────────────────────────┐
│ [🔍 Search...]  [🛒]   │  <- Top bar (56px)
├─────────────────────────┤
│                         │
│ ┌─────────────────────┐ │
│ │    Banner 1/3       │ │  <- Carousel (200px)
│ │    [Dot] [○] [○]    │ │
│ └─────────────────────┘ │
├─────────────────────────┤
│ [分类1][分类2][分类3].. │  <- Category (80px)
├─────────────────────────┤
│ 🔥 限时抢购             │
│ ┌─────┐ ┌─────┐        │
│ │Prod │ │Prod │        │  <- Flash sale (2 columns)
│ └─────┘ └─────┘        │
├─────────────────────────┤
│ 👑 推荐商品             │
│ ┌─────┐ ┌─────┐        │
│ │Prod │ │Prod │        │
│ │Name │ │Name │        │  <- Product grid
│ │ ¥99 │ │ ¥88 │        │
│ └─────┘ └─────┘        │
│ ┌─────┐ ┌─────┐        │
│ │Prod │ │Prod │        │
│ └─────┘ └─────┘        │
└─────────────────────────┘
```

---

## Page 3: Product Detail Page

### Core Functions
- Product image gallery
- Product title & price
- Specification selector (size, color)
- Quantity selector
- Add to cart button
- Buy now button
- Product description tabs
- Reviews section

### Wireframe
```
┌─────────────────────────┐
│ [←] [♡] [↗] [≡]        │  <- Navigation bar
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │                     │ │
│ │   Product Image     │ │  <- Image gallery
│ │                     │ │
│ │   [○] [●] [○] [○]   │ │  <- Image dots
│ └─────────────────────┘ │
├─────────────────────────┤
│ ¥199.00    ¥299.00      │  <- Price (strike-through)
│ 产品名称商品标题        │  <- Title
│ 销量 1000+ 收藏 500+    │  <- Stats
├─────────────────────────┤
│ 规格: [M] [L] [XL]      │  <- Spec selector
│ 颜色: [●] [○] [○]       │
├─────────────────────────┤
│ 数量: [-] [1] [+]       │  <- Quantity
├─────────────────────────┤
│ ┌─────────┐ ┌─────────┐  │
│ │ 加入购物车│ │ 立即购买 │  │  <- Bottom CTAs
│ └─────────┘ └─────────┘  │
├─────────────────────────┤
│ [详情] [规格] [评价(99+)]│  <- Tabs
├─────────────────────────┤
│ 商品详细描述内容...      │
└─────────────────────────┘
```

---

## Page 4: Shopping Cart Page

### Core Functions
- Seller/shop info
- Product list with checkboxes
- Quantity adjustment
- Delete items
- Select all
- Total calculation
- Checkout button

### Wireframe
```
┌─────────────────────────┐
│ [←] 购物车    [编辑]    │  <- Header
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ ☑ [Shop Name]      │ │  <- Shop section
│ │ ☑ [Img] Product A  │ │
│ │     ¥99 x1  [-][1][+]││  <- Item with quantity
│ │     [删除]          │ │
│ ├─────────────────────┤ │
│ │ ☑ [Img] Product B   │ │
│ │     ¥88 x2          │ │
│ └─────────────────────┘ │
├─────────────────────────┤
│ ☑ 全选                │
│ 合计: ¥275.00          │  <- Total
│ ┌─────────────────────┐ │
│ │    去结算 (3)        │ │  <- Checkout button
│ └─────────────────────┘ │
└─────────────────────────┘
```

---

## Page 5: Checkout Page

### Core Functions
- Delivery address selection
- Invoice option
- Product summary
- Payment method
- Order total
- Submit order

### Wireframe
```
┌─────────────────────────┐
│ [←] 确认订单            │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ 📍 张三 138****8888 │ │
│ │ 北京市朝阳区xxx路xx号│ │
│ │        [修改 >]      │ │  <- Address card
│ └─────────────────────┘ │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ Product A x1        │ │
│ │ Product B x2        │ │  <- Order items
│ └─────────────────────┘ │
├─────────────────────────┤
│ 配送方式: 标准配送      │
│ 发票信息: 个人          │
│ 优惠券: [- 未使用]      │
├─────────────────────────┤
│ 商品金额:   ¥275.00     │
│ 运费:       ¥0.00      │
│ 优惠:      -¥10.00     │
├─────────────────────────┤
│ 合计:       ¥265.00     │
│ ┌─────────────────────┐ │
│ │    提交订单          │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

---

## Page 6: Order Confirmation

### Core Functions
- Order success indicator
- Order number
- Order summary
- Payment button
- Return to home

### Wireframe
```
┌─────────────────────────┐
│                         │
│       [✓ Success]       │  <- Big icon
│                         │
│      订单提交成功        │
│      订单号: 20240325001 │
│                         │
├─────────────────────────┤
│ 订单金额: ¥265.00       │
│ 配送地址: 北京市朝阳区   │
│ 预计送达: 3-5天          │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │   立即支付 ¥265.00   │ │
│ └─────────────────────┘ │
│                         │
│ [查看订单]  [返回首页]   │  <- Secondary buttons
└─────────────────────────┘
```

---

## User Flow

### Main Purchase Flow
```
Login → Home → Product Detail → Cart → Checkout → Pay → Success
```

### Alternative Flows
1. Home → Search → Product List → Product Detail → Cart
2. Home → Banner → Product Detail
3. Home → Category → Product List → Product Detail

---

## Common UI Components

### Button States
```
[  Primary Button  ]  <- Blue, 48px height
[ Secondary Button ]  <- White with border, 44px
[  Disabled Button ]  <- Gray, 50% opacity
```

### Input States
```
[  Normal Input  ]    <- Gray border
[  Focused Input ]    <- Blue border, shadow
[   Error Input  ]    <- Red border, error text
[ Disabled Input ]    <- Gray background
```

### List Item Variations
```
Simple:     [Icon] Title          [>]
With desc:  [Icon] Title         [>]
                   Description    [>]
With img:   [Img] Title    [x]  [>]
                   Desc     [-][1][+]
With price: [Img] Title          ¥99
                   x1            [>]
```

---

## Mobile App Design Standards

### iOS (Human Interface Guidelines)
- Safe area: 44px top, 34px bottom
- Navigation bar: 44px
- Tab bar: 49px (83px with home indicator)
- Touch targets: 44x44px minimum

### Android (Material Design)
- Status bar: 24px
- Navigation bar: 48-56px
- FAB: 56px
- Touch targets: 48x48dp minimum

### General Mobile
- Screen width: 375px (iPhone), 360px (Android)
- Grid: 12 columns, 16px gutter
- Margins: 16px horizontal
- Card radius: 8-12px
- Button radius: 4-8px
