# Anthropic Design System

Anthropic 的设计代表 AI 安全和可靠的美学。

## 设计理念

Anthropic 追求**清晰**、**诚实**、**有帮助**。设计体现 AI 的可靠性。

## 色彩系统

### 品牌色
- Primary: `#B8860B` (Anthropic 金)
- Primary Light: `#D4A84B`
- Primary Dark: `#8B6508`

### 背景色

#### 浅色模式
- Background: `#F9F7F4`
- Background Secondary: `#F0EDE8`
- Background Card: `#FFFFFF`

#### 深色模式
- Background Dark: `#1A1A1A`
- Background Dark Secondary: `#252525`
- Background Dark Card: `#2D2D2D`

### 文字色

#### 浅色模式
- Text Primary: `#2B2B2B`
- Text Secondary: `#666666`
- Text Tertiary: `#999999`

#### 深色模式
- Text Dark Primary: `#E5E5E5`
- Text Dark Secondary: `#A0A0A0`
- Text Dark Tertiary: `#6B6B6B`

### 边框色
- Border: `#E0DCD4`
- Border Dark: `#3D3D3D`

## 字体

### 字体栈
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 32px
- H1: 24px
- H2: 20px
- H3: 16px
- Body: 15px
- Small: 13px

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

**主要按钮**
- Background: `#B8860B`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 40px
- Padding: 0 20px

**次要按钮**
- Background: `#F0EDE8`
- Color: `#2B2B2B`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E0DCD4`
- Border Radius: 8px
- Height: 44px
- Focus Border: `#B8860B`

### 消息气泡

**AI 消息**
- Background: `#F9F7F4`
- Color: `#2B2B2B`
- Border Radius: 16px
- Border: 1px solid `#E0DCD4`

**用户消息**
- Background: `#B8860B`
- Color: `#FFFFFF`
- Border Radius: 16px

## 适用场景

- 🤖 AI 聊天界面
- 💬 对话产品
- 🧠 AI 助手
- 📝 写作辅助

## 组件示例 HTML 结构

```html
<div class="anthropic-message anthropic-message-ai">
  <p>AI 回复内容</p>
</div>
<div class="anthropic-message anthropic-message-user">
  <p>用户输入</p>
</div>
<button class="anthropic-btn-primary">发送</button>
```
