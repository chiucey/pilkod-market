# 支付宝设计系统

支付宝的金融支付设计语言。

## 设计理念

支付宝追求**信任**、**安全**、**便捷**。打造数字生活钱包。

## 色彩系统

### 品牌色
- Primary: `#1677FF` (支付宝蓝)
- Primary Hover: `#4096FF`
- Primary Dark: `#0958D9`

### 辅助色
- Success: `#00B42A`
- Warning: `#FF9A00`
- Error: `#F53F3F`
- Info: `#1677FF`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F5F7FA`
- Background Tertiary: `#EDF0F5`

#### 深色模式
- Background Dark: `#1F1F1F`
- Background Dark Secondary: `#292929`

### 文字色

#### 浅色模式
- Text Primary: `#1D2129`
- Text Secondary: `#4E5969`
- Text Tertiary: `#86909C`

#### 深色模式
- Text Dark Primary: `#E5E6EB`
- Text Dark Secondary: `#8F939E`
- Text Dark Tertiary: `#6B7280`

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
- Background: `#1677FF`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 44px

**次要按钮**
- Background: `#F5F7FA`
- Color: `#1677FF`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E5E6EB`
- Border Radius: 8px
- Height: 44px
- Focus Border: `#1677FF`

### 付款码

- Background: `#1677FF`
- 二维码区域: 白色

### 金额显示

- Amount: 36px / 700
- Currency: 20px

## 适用场景

- 💰 支付付款
- 💳 信用借贷
- 💼 资产管理
- 🏪 商家收款

## 组件示例 HTML 结构

```html
<button class="alipay-btn-primary">立即支付</button>
<div class="alipay-payment-code">
  <div class="alipay-qrcode">二维码</div>
  <div class="alipay-amount">¥99.00</div>
</div>
<div class="alipay-card">
  <span class="alipay-title">账单</span>
  <span class="alipay-amount">¥99.00</span>
</div>
```
