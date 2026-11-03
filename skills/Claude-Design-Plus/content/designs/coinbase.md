# Coinbase Design System

Coinbase 的加密货币设计语言。

## 设计理念

Coinbase 追求**信任**、**简洁**、**安全**。让加密货币触手可及。

## 色彩系统

### 品牌色
- Primary: `#0052FF` (Coinbase 蓝)
- Primary Hover: `#3D6FFF`
- Primary Dark: `#0044CC`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F5F7FF`
- Background Tertiary: `#EBEDF2`

#### 深色模式
- Background Dark: `#0A0A0B`
- Background Dark Secondary: `#141417`
- Background Dark Tertiary: `#1E1E22`

### 文字色

#### 浅色模式
- Text Primary: `#0A0A0B`
- Text Secondary: `#5E6672`
- Text Tertiary: `#8C94A3`

#### 深色模式
- Text Dark Primary: `#FFFFFF`
- Text Dark Secondary: `#A3A9B8`
- Text Dark Tertiary: `#6B7280`

### 加密货币色
- Bitcoin Orange: `#F7931A`
- Ethereum Purple: `#627EEA`
- Litecoin Silver: `#BFBBBB`
- Bitcoin Cash Green: `#0ACA18`

### 功能色
- Success: `#05D58B`
- Warning: `#F5A623`
- Error: `#EF4444`
- Info: `#0052FF`

## 字体

### 字体栈
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 36px / 700
- H1: 28px / 600
- H2: 22px / 600
- H3: 18px / 600
- Body: 16px / 400
- Small: 14px / 400
- Caption: 12px / 400

## 间距系统

基于 8px 网格：
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

## 组件样式

### 按钮

**Primary 按钮**
- Background: `#0052FF`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 48px
- Padding: 0 24px

**Secondary 按钮**
- Background: `#F5F7FF`
- Color: `#0052FF`
- Border: 1px solid `#0052FF`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E5E7EB`
- Border Radius: 8px
- Height: 48px
- Padding: 0 16px
- Focus Border: `#0052FF`

### 加密货币卡片

- Background: `#F5F7FF`
- Border Radius: 12px
- Padding: 16px
- Crypto Icon Size: 40px

### 价格显示

- Current Price: 32px / 700
- Change Positive: `#05D58B`
- Change Negative: `#EF4444`

## 适用场景

- 💰 加密货币交易
- 📊 资产管理
- 💳 支付钱包
- 📈 价格图表

## 组件示例 HTML 结构

```html
<div class="coinbase-asset-card">
  <img class="coinbase-asset-icon" src="btc.png" alt="BTC">
  <div class="coinbase-asset-info">
    <span class="coinbase-asset-name">Bitcoin</span>
    <span class="coinbase-asset-symbol">BTC</span>
  </div>
  <div class="coinbase-asset-price">$45,000</div>
  <div class="coinbase-asset-change positive">+2.5%</div>
</div>
<button class="coinbase-btn-primary">买入</button>
<button class="coinbase-btn-secondary">卖出</button>
```
