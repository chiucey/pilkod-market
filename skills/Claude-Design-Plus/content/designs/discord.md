# Discord Design System

Discord 的设计代表游戏社交的活力美学。

## 设计理念

Discord 追求**活力**、**社区**、**沉浸**。大胆用色，年轻化设计。

## 色彩系统

### 品牌色
- Primary: `#5865F2` (Discord 紫)
- Primary Hover: `#4752C4`
- Primary Dark: `#3D45C4`

### Blurple
- Blurple: `#5865F2`
- Blurple Hover: `#4752C4`

### 背景色

#### 深色模式 (主模式)
- Background: `#000000`
- Background Secondary: `#2B2D31`
- Background Tertiary: `#313338`
- Background Elevated: `#383A40`

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F2F3F5`
- Background Tertiary: `#EBEDEF`

### 文字色

#### 深色模式
- Text Primary: `#F2F3F5`
- Text Secondary: `#B5BAC1`
- Text Tertiary: `#949BA4`
- Text Muted: `#6D6F78`

#### 浅色模式
- Text Primary: `#2E3338`
- Text Secondary: `#4E5664`
- Text Tertiary: `#72767D`

### 语义色
- Success: `#23A559`
- Danger: `#DA373C`
- Warning: `#F0B232`
- Info: `#00A8FC`

### 状态色
- Online: `#23A559`
- Idle: `#F0B232`
- DND: `#DA373C`
- Streaming: `#643DA8`

## 字体

### 字体栈
```
'gg sans', 'Noto Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif
```

### 中文
```
'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC', sans-serif
```

### 字号
- Display: 32px / 700
- H1: 24px / 700
- H2: 20px / 600
- H3: 16px / 600
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
- md: 8px
- lg: 12px
- xl: 16px
- 2xl: 20px
- full: 9999px

## 组件样式

### 按钮

**Primary 按钮**
- Background: `#5865F2`
- Color: `#FFFFFF`
- Border Radius: 4px
- Height: 40px
- Padding: 2px 16px

**Secondary 按钮**
- Background: `#4E5664`
- Color: `#FFFFFF`

**Outline 按钮**
- Background: transparent
- Color: `#B5BAC1`
- Border: 1px solid `#6D6F78`

### 输入框

- Background: `#383A40`
- Border: none
- Border Radius: 4px
- Height: 40px
- Padding: 0 12px
- Color: `#F2F3F5`
- Placeholder: `#6D6F78`

### 服务器列表

- Item Size: 48px
- Border Radius: 50%
- Active Indicator: 4px `#5865F2`

### 频道列表

- Item Height: 32px
- Item Padding: 0 12px
- Hover: `#383A40`
- Active: `#3D45C4`

### 成员列表

- Avatar Size: 24px / 32px
- Name: 15px / 500
- Role Color: 可自定义

## 设计注意事项

1. **暗色优先** - 用户习惯深色模式
2. **大胆配色** - Blurple 品牌色
3. **社区化** - 服务器、频道、成员层级
4. **状态指示** - 在线/离线/DND

## 适用场景

- 🎮 游戏社交
- 💬 社区聊天
- 👥 团队协作
- 🎵 语音房间

## 组件示例 HTML 结构

```html
<div class="discord-server-icon">图标</div>
<div class="discord-channel">
  <span class="discord-channel-hash">#</span>
  <span>频道名</span>
</div>
<div class="discord-message">
  <div class="discord-avatar">头像</div>
  <div class="discord-message-content">
    <span class="discord-username">用户名</span>
    <p>消息内容</p>
  </div>
</div>
<button class="discord-btn-primary">发送</button>
```
