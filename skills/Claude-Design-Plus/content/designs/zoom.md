# Zoom Design System

Zoom 的视频会议设计美学。

## 设计理念

Zoom 追求**专注**、**连接**、**可靠**。让会议变得简单高效。

## 色彩系统

### 品牌色
- Primary: `#2D8CFF` (Zoom 蓝)
- Primary Hover: `#0D7AF5`
- Primary Dark: `#0056B3`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F5F7FA`
- Background Dark: `#0D0D0D`

#### 深色模式
- Background Dark Primary: `#040404`
- Background Dark Secondary: `#1C1C1C`
- Background Dark Card: `#262626`

### 文字色

#### 浅色模式
- Text Primary: `#1A1A1A`
- Text Secondary: `#6B6B6B`
- Text Tertiary: `#9B9B9B`

#### 深色模式
- Text Dark Primary: `#FFFFFF`
- Text Dark Secondary: `#A0A0A0`
- Text Dark Tertiary: `#6B6B6B`

### 会议状态色
- In Meeting: `#F5222D`
- Available: `#52C41A`
- Busy: `#FAAD14`
- Away: `#A0A0A0`

## 字体

### 字体栈
```
'Zoom Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 24px / 700
- H1: 20px / 600
- H2: 16px / 600
- Body: 14px / 400
- Small: 12px / 400
- Caption: 11px / 400

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
- md: 8px
- lg: 12px
- xl: 16px
- full: 9999px
- button: 6px

## 组件样式

### 视频会议控件

- Background: `#363636`
- Border Radius: 8px
- Height: 56px
- Icon Size: 24px
- Active Background: `#2D8CFF`

### 按钮

**主要按钮**
- Background: `#2D8CFF`
- Color: `#FFFFFF`
- Border Radius: 6px
- Height: 36px
- Padding: 0 20px

**Secondary 按钮**
- Background: `#F5F7FA`
- Color: `#1A1A1A`

### 用户头像

- Border Radius: 50%
- Border: 2px solid `#FFFFFF`
- Sizes: 28px / 36px / 48px / 72px

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#D9D9D9`
- Border Radius: 4px
- Height: 32px
- Focus Border: `#2D8CFF`

## 设计注意事项

1. **视频优先** - 视频画面是核心
2. **简单控制** - 一键操作
3. **品牌蓝** - Zoom 蓝贯穿始终
4. **深色模式** - 会议中常用深色

## 适用场景

- 📹 视频会议
- 🎥 网络研讨会
- 📞 语音通话
- 💻 屏幕共享

## 组件示例 HTML 结构

```html
<div class="zoom-meeting">
  <div class="zoom-video-grid">
    <div class="zoom-video">
      <img src="participant.jpg" alt="参会者">
      <div class="zoom-username">用户名</div>
    </div>
  </div>
  <div class="zoom-controls">
    <button class="zoom-btn-mute">静音</button>
    <button class="zoom-btn-video">视频</button>
    <button class="zoom-btn-share">共享</button>
    <button class="zoom-btn-end">结束</button>
  </div>
</div>
<button class="zoom-btn-primary">加入会议</button>
```
