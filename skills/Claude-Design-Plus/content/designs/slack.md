# Slack Design System

Slack 的设计代表现代办公协作美学。

## 设计理念

Slack 追求**清晰**、**高效**、**协作**。简洁的界面提升团队效率。

## 色彩系统

### 品牌色
- Primary: `#611F69` (Slack 紫)
- Primary Hover: `#7A2B82`
- Primary Dark: `#4A154B`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F8F8F8`
- Background Tertiary: `#EFEFF1`
- Background Dark: `#1D1C1D`

#### 深色模式
- Background Dark Primary: `#191716`
- Background Dark Secondary: `#1D1C1D`
- Background Dark Tertiary: `#2D2A2E`

### 文字色

#### 浅色模式
- Text Primary: `#1D1C1D`
- Text Secondary: `#616061`
- Text Tertiary: `#868686`
- Text Inverse: `#FFFFFF`

#### 深色模式
- Text Dark Primary: `#D1D1D1`
- Text Dark Secondary: `#A3A3A3`
- Text Dark Tertiary: `#6B6B6B`

### 功能色
- Success: `#2EA67B`
- Warning: `#ECB22E`
- Error: `#E01E5A`
- Info: `#36C5F0`

### 工作区色
- A: `#36C5F0` (蓝)
- B: `#2EA67B` (绿)
- C: `#DEEBE7` (浅绿)
- D: `#F2C60` (黄)
- E: `#ECB22E` (橙)
- F: `#E01E5A` (红)
- G: `#4A154B` (紫)

## 字体

### 字体栈
```
'Slack Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 28px / 700
- H1: 22px / 700
- H2: 18px / 700
- H3: 16px / 700
- Body: 15px / 400
- Small: 13px / 400
- Micro: 11px / 400

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px
- 2xl: 32px

## 圆角

- sm: 4px
- md: 6px
- lg: 8px
- xl: 12px
- full: 9999px

## 组件样式

### 按钮

**Primary 按钮**
- Background: `#611F69`
- Color: `#FFFFFF`
- Border Radius: 4px
- Height: 36px
- Padding: 0 16px

**Secondary 按钮**
- Background: `#F8F8F8`
- Color: `#1D1C1D`
- Border: 1px solid `#6B6B6B`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E8E8E8`
- Border Radius: 4px
- Height: 36px
- Padding: 0 12px
- Focus Border: `#611F69`

### 消息气泡

- Background: `#FFFFFF`
- Border Left: 4px `#E8E8E8`
- Padding: 8px 12px
- User Name Color: `#1D1C1D`
- Timestamp: `#616061`

### 侧边栏

- Background: `#F8F8F8`
- Width: 260px
- Item Height: 28px
- Item Padding: 0 8px 0 12px

### Emoji 反应

- Background: `#F8F8F8`
- Border Radius: 4px
- Padding: 4px 8px
- Font Size: 18px

## 设计注意事项

1. **工作区色彩** - 每个工作区可自定义强调色
2. **消息优先** - 消息是核心
3. **搜索强大** - 搜索是核心功能
4. **频道组织** - 频道/群组/DM 层级

## 适用场景

- 💼 企业办公
- 👥 团队协作
- 💬 即时通讯
- 📁 文件共享

## 组件示例 HTML 结构

```html
<aside class="slack-sidebar">
  <div class="slack-workspace">工作区</div>
  <div class="slack-channel"># 频道</div>
</aside>
<div class="slack-message">
  <div class="slack-avatar">头像</div>
  <div class="slack-message-content">
    <span class="slack-username">用户名</span>
    <p>消息</p>
  </div>
</div>
<div class="slack-emoji-reaction">👍 5</div>
<button class="slack-btn-primary">发送</button>
```
