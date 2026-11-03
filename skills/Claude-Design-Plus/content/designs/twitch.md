# Twitch Design System

Twitch 的直播平台设计美学。

## 设计理念

Twitch 追求**直播**、**社区**、**游戏**。让玩家找到自己的归属。

## 色彩系统

### 品牌色
- Primary: `#9146FF` (Twitch 紫)
- Primary Hover: `#7B5FCC`
- Primary Dark: `#6440A8`

### 背景色

#### 深色模式 (主模式)
- Background: `#0E0E10`
- Background Secondary: `#18181B`
- Background Tertiary: `#1F1F23`
- Background Card: `#1F1F23`

#### 浅色模式
- Background: `#FAFAFA`
- Background Secondary: `#F7F7F7`

### 文字色

#### 深色模式
- Text Primary: `#EFEFF1`
- Text Secondary: `#ADADB8`
- Text Tertiary: `#6B6B76`

#### 浅色模式
- Text Primary: `#0E0E10`
- Text Secondary: `#53535F`
- Text Tertiary: `#80808F`

### 直播状态色
- Live: `#E91916`
- Offline: `#6B6B76`

## 字体

### 字体栈
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 28px / 700
- H1: 22px / 600
- H2: 18px / 600
- Body: 14px / 400
- Small: 12px / 400
- Micro: 11px / 400

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px

## 圆角

- sm: 4px
- md: 6px
- lg: 8px
- full: 9999px

## 组件样式

### 直播卡片

- Background: `#1F1F23`
- Border Radius: 6px
- Hover Background: `#2F2F33`

### Live 标签

- Background: `#E91916`
- Color: `#FFFFFF`
- Border Radius: 4px
- Padding: 2px 6px
- Font Size: 11px
- Font Weight: 600

### 头像

- Border Radius: 50%
- Sizes: 28px / 32px / 40px / 48px
- Live Ring: 3px `#E91916`

### 按钮

**Primary 按钮**
- Background: `#9146FF`
- Color: `#FFFFFF`
- Border Radius: 6px
- Height: 36px
- Padding: 0 20px

**Secondary 按钮**
- Background: `#2F2F33`
- Color: `#EFEFF1`

### 聊天输入框

- Background: `#18181B`
- Border: none
- Border Radius: 6px
- Height: 36px
- Padding: 0 12px

### 进度条

- Track: `#3A3A3D`
- Progress: `#9146FF`

## 设计注意事项

1. **直播优先** - 直播卡片突出显示
2. **暗色主题** - 深色模式是主模式
3. **紫色品牌** - Twitch 紫是标志
4. **社区氛围** - 聊天是核心功能

## 适用场景

- 🎮 游戏直播
- 🎬 创意直播
- 🎵 音乐直播
- 💬 社区互动

## 组件示例 HTML 结构

```html
<div class="twitch-stream-card">
  <div class="twitch-thumbnail">
    <img src="stream.jpg" alt="直播">
    <span class="twitch-live-tag">LIVE</span>
    <span class="twitch-viewers">10K viewers</span>
  </div>
  <div class="twitch-streamer">
    <img class="twitch-avatar" src="avatar.jpg" alt="主播">
    <div class="twitch-info">
      <span class="twitch-name">主播名</span>
      <span class="twitch-title">直播标题</span>
    </div>
  </div>
</div>
<button class="twitch-btn-primary">关注</button>
<div class="twitch-chat">
  <input class="twitch-chat-input" type="text" placeholder="发送消息">
</div>
```
