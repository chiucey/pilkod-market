# OpenAI Design System

OpenAI 的设计代表 AI 技术的最前沿。

## 设计理念

OpenAI 追求**简洁**、**专业**、**可信赖**。设计体现 AI 的先进性和易用性。

## 色彩系统

### 品牌色
- Primary: `#10A37F` (OpenAI 绿)
- Primary Hover: `#0D8A6A`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F7F7F8`
- Background Tertiary: `#ECECEC`

#### 深色模式
- Background Dark: `#1A1A1A`
- Background Dark Secondary: `#2D2D2D`
- Background Dark Tertiary: `#404040`

### 文字色

#### 浅色模式
- Text Primary: `#1A1A1A`
- Text Secondary: `#666666`
- Text Tertiary: `#999999`

#### 深色模式
- Text Dark Primary: `#FAFAFA`
- Text Dark Secondary: `#A0A0A0`
- Text Dark Tertiary: `#6B6B6B`

### 功能色
- Success: `#10A37F`
- Warning: `#F5A623`
- Error: `#E53935`
- Info: `#4285F4`

## 字体

### 字体栈
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 28px
- H1: 22px
- H2: 18px
- H3: 15px
- Body: 15px
- Small: 13px

## 间距系统

基于 8px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px

## 圆角

- sm: 4px
- md: 6px
- lg: 8px
- xl: 12px

## 组件样式

### 按钮

**主要按钮**
- Background: `#10A37F`
- Color: `#FFFFFF`
- Border Radius: 6px
- Height: 40px
- Padding: 0 20px
- Font Size: 15px

**次要按钮**
- Background: `#F7F7F8`
- Color: `#1A1A1A`
- Border: 1px solid `#ECECEC`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#D1D1D1`
- Border Radius: 6px
- Height: 44px
- Padding: 0 16px
- Font Size: 15px
- Focus Border: `#10A37F`

### 消息组件

**用户消息**
- Background: `#F7F7F8`
- Color: `#1A1A1A`
- Border Radius: 20px
- Padding: 12px 16px

**AI 消息**
- Background: `#F7F7F8`
- Color: `#1A1A1A`
- Border Radius: 20px
- Padding: 12px 16px

## 适用场景

- 🤖 AI 聊天
- 📝 写作助手
- 💻 代码生成
- 🎨 图像生成

## 组件示例 HTML 结构

```html
<div class="openai-message openai-message-user">
  <p>用户输入</p>
</div>
<div class="openai-message openai-message-assistant">
  <p>AI 回复</p>
</div>
<button class="openai-btn-primary">发送</button>
<input class="openai-input" type="text" placeholder="输入...">
```
