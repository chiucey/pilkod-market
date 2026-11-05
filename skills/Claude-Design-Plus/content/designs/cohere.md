# Cohere Design System

Cohere 的企业 AI 设计语言。

## 设计理念

Cohere 追求**企业级**、**可靠**、**专业**。服务于企业 AI 需求。

## 色彩系统

### 品牌色
- Primary: `#5B4DFF` (Cohere 紫)
- Primary Hover: `#7B6FFF`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F8F8FA`
- Background Tertiary: `#F0F0F5`

#### 深色模式
- Background Dark: `#0F0F12`
- Background Dark Secondary: `#1A1A1F`
- Background Dark Tertiary: `#252530`

### 文字色

#### 浅色模式
- Text Primary: `#1A1A2E`
- Text Secondary: `#5C5C72`
- Text Tertiary: `#9090A0`

#### 深色模式
- Text Dark Primary: `#EDEDF5`
- Text Dark Secondary: `#A0A0B0`
- Text Dark Tertiary: `#6B6B80`

## 字体

### 字体栈
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 32px
- H1: 24px
- H2: 20px
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
- Background: `#5B4DFF`
- Color: `#FFFFFF`
- Border Radius: 6px
- Height: 40px

**次要按钮**
- Background: `#F8F8FA`
- Color: `#1A1A2E`
- Border: 1px solid `#E0E0E8`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E0E0E8`
- Border Radius: 6px
- Height: 44px
- Focus Border: `#5B4DFF`

## 适用场景

- 💼 企业 AI
- 🔍 搜索增强
- 📊 数据分析
- 🤖 聊天机器人

## 组件示例 HTML 结构

```html
<button class="cohere-btn-primary">主要</button>
<button class="cohere-btn-secondary">次要</button>
<input class="cohere-input" type="text" placeholder="输入">
```
