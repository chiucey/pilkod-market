# Stripe Design System

Stripe 的设计系统以简洁、专业和信任感著称。

## 设计理念

Stripe 代表金融基础设施，设计的核心是**清晰**、**精确**、**优雅**。

## 色彩系统

### 主色
- Primary: `#635BFF` (Stripe 紫)
- Primary Hover: `#7A73FF`

### 背景色
- Background: `#FFFFFF`
- Background Secondary: `#F6F9FC`
- Background Dark: `#1A1F36`

### 文字色
- Text Primary: `#1A1F36`
- Text Secondary: `#697386`
- Text Tertiary: `#A8B0BD`
- Text Inverse: `#FFFFFF`

### 功能色
- Success: `#30D158`
- Warning: `#FF9500`
- Error: `#FF3B30`
- Info: `#007AFF`

### 边框
- Border: `#E6E8EB`
- Border Hover: `#C7CBD3`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
```

### 字号
- Display: 48px / 56px line-height / -0.02em tracking
- H1: 32px / 40px / -0.02em
- H2: 24px / 32px / -0.01em
- H3: 20px / 28px / 0
- Body: 16px / 24px / 0
- Caption: 14px / 20px / 0
- Micro: 12px / 16px / 0

### 字重
- Regular: 400
- Medium: 500
- Semibold: 600

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
- 3xl: 64px

## 圆角

- sm: 4px
- md: 8px
- lg: 12px
- xl: 16px
- full: 9999px (胶囊形)

## 阴影

### 卡片阴影
```css
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
```

### 悬停阴影
```css
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06);
```

### 模态框阴影
```css
box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

## 组件样式

### 按钮

**主要按钮**
- Background: `#635BFF`
- Color: `#FFFFFF`
- Padding: 12px 24px
- Border Radius: 8px
- Font Weight: 500
- Hover: `#7A73FF`

**次要按钮**
- Background: `#F6F9FC`
- Color: `#1A1F36`
- Border: 1px solid `#E6E8EB`
- Hover Background: `#E6E8EB`

**文字按钮**
- Color: `#635BFF`
- Hover: 下划线

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E6E8EB`
- Border Radius: 6px
- Padding: 12px 16px
- Focus Border: `#635BFF`
- Focus Shadow: `0 0 0 3px rgba(99, 91, 255, 0.1)`

### 卡片

- Background: `#FFFFFF`
- Border: 1px solid `#E6E9ED`
- Border Radius: 12px
- Padding: 24px

### 徽章/标签

- Border Radius: full
- Padding: 4px 12px
- Font Size: 14px
- Font Weight: 500

## 图标风格

- 线条粗细: 1.5px
- 圆角: 3px
- 尺寸: 16px / 20px / 24px / 32px
- 颜色: 继承文字颜色

## 设计注意事项

1. **保持简洁** - 不要过度装饰
2. **强调信任** - 使用 Stripe 紫色作为品牌强调色
3. **清晰层次** - 明确的视觉层级
4. **一致间距** - 使用 4px 网格系统
5. **微妙阴影** - 阴影应该柔和，不突兀

## 适用场景

- 💰 支付页面
- 💳 信用卡表单
- 📊 财务仪表盘
- 🏢 企业后台
- 📱 SaaS 产品

## 组件示例 HTML 结构

```html
<!-- 按钮 -->
<button class="stripe-btn-primary">继续</button>
<button class="stripe-btn-secondary">取消</button>

<!-- 输入框 -->
<input class="stripe-input" type="text" placeholder="邮箱">

<!-- 卡片 -->
<div class="stripe-card">
  <h3 class="stripe-card-title">标题</h3>
  <p class="stripe-card-body">内容</p>
</div>

<!-- 表单 -->
<form class="stripe-form">
  <div class="stripe-form-group">
    <label class="stripe-label">邮箱</label>
    <input class="stripe-input" type="email">
  </div>
</form>
```
