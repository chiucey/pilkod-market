# 腾讯 CDC 设计系统

腾讯 CDC (Customer Design Center) 出品的设计规范。

## 设计理念

CDC 追求**体验**、**创新**、**一致**。服务于腾讯全系列产品。

## 色彩系统

### 品牌色
- Primary: `#07C160` (微信绿)
- Primary Dark: `#06AD56`
- Primary Light: `#10D174`

### 辅助色
- Blue: `#1AAD19`
- Orange: `#FF6600`
- Red: `#F5222D`
- Yellow: `#FAAD14`
- Purple: `#722ED1`

### 背景色
- Background: `#FFFFFF`
- Background Secondary: `#F5F5F5`
- Background Dark: `#1F1F1F`

### 文字色
- Text Primary: `#000000`
- Text Secondary: `#666666`
- Text Tertiary: `#999999`
- Text Inverse: `#FFFFFF`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif
```

### 中文
```
'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif
```

### 字号
- Display: 36px
- H1: 28px
- H2: 22px
- H3: 18px
- Body: 14px
- Caption: 12px

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px

## 圆角

- sm: 2px
- md: 4px
- lg: 8px
- xl: 12px
- full: 9999px

## 组件样式

### 按钮

**主要按钮**
- Background: `#07C160`
- Color: `#FFFFFF`
- Border Radius: 4px
- Height: 40px
- Padding: 0 24px

**次要按钮**
- Background: `#FFFFFF`
- Color: `#666666`
- Border: 1px solid `#D9D9D9`

### 输入框

- Border: 1px solid `#D9D9D9`
- Border Radius: 4px
- Height: 40px
- Padding: 0 12px
- Focus Border: `#07C160`

### 卡片

- Background: `#FFFFFF`
- Border: 1px solid `#E5E5E5`
- Border Radius: 8px
- Padding: 20px

## 适用场景

- 💬 社交通讯
- 🎮 游戏平台
- 💰 金融产品
- 🏢 企业服务

## 组件示例 HTML 结构

```html
<button class="tencent-btn-primary">主要</button>
<button class="tencent-btn-secondary">次要</button>
<input class="tencent-input" type="text" placeholder="输入">
<div class="tencent-card">
  <h3>标题</h3>
  <p>内容</p>
</div>
```
