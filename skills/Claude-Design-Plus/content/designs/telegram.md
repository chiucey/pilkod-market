# Telegram Design System

Telegram 的设计代表快速、安全、简洁的通讯美学。

## 设计理念

Telegram 追求**速度**、**安全**、**简洁**。极简界面，专注消息本身。

## 色彩系统

### 品牌色
- Primary: `#0088CC` (Telegram 蓝)
- Primary Light: `#229ED9`
- Primary Dark: `#0077B5`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F5F5F5`
- Background Tertiary: `#EFEFF2`
- Background Chat: `#EFFDFF`

#### 深色模式
- Background Dark: `#000000`
- Background Dark Secondary: `#17212B`
- Background Dark Tertiary: `#1F2C34`
- Background Dark Chat: `#0E1D24`

### 文字色

#### 浅色模式
- Text Primary: `#000000`
- Text Secondary: `#8E8E93`
- Text Tertiary: `#B8BCC2`

#### 深色模式
- Text Dark Primary: `#FFFFFF`
- Text Dark Secondary: `#8E8E93`
- Text Dark Tertiary: `#6B7B85`

### 功能色
- Sent: `#0088CC`
- Received: `#EFFDFF`
- Online: `#4FC3F7`
- Unread: `#5EB9F0`

## 字体

### 字体栈
```
'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif
```

### 中文
```
'PingFang SC', 'Microsoft YaHei', 'Heiti SC', sans-serif
```

### 字号
- Display: 24px / 500
- H1: 20px / 500
- H2: 17px / 500
- Body: 15px / 400
- Small: 13px / 400
- Caption: 11px / 400

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px

## 圆角

- sm: 4px
- md: 8px
- lg: 12px
- xl: 18px
- bubble: 18px (消息气泡)

## 组件样式

### 消息气泡

**发送 (右侧)**
- Background: `#0088CC`
- Color: `#FFFFFF`
- Border Radius: 18px 18px 4px 18px
- Max Width: 70%

**接收 (左侧)**
- Background: `#EFFDFF`
- Color: `#000000`
- Border Radius: 18px 18px 18px 4px

### 头像

- Border Radius: 50%
- Sizes: 40px / 48px
- Online Indicator: 12px `#4FC3F7`

### 按钮

**Telegram 按钮**
- Background: `#0088CC`
- Color: `#FFFFFF`
- Border Radius: 20px
- Height: 48px
- Padding: 0 24px

### 输入框

- Background: `#FFFFFF` (浅色) / `#17212B` (深色)
- Border: none
- Border Radius: 20px
- Height: 40px
- Padding: 0 16px

### 贴纸

- Size: 100px / 200px / 320px
- 网格布局: 5列

## 设计注意事项

1. **极简主义** - 界面元素最少
2. **消息气泡** - 圆角消息气泡是标志
3. **蓝色主调** - Telegram 蓝贯穿始终
4. **隐私优先** - 隐私功能突出

## 适用场景

- 💬 即时通讯
- 📱 移动应用
- 🔒 安全通讯
- 👥 群组社交

## 组件示例 HTML 结构

```html
<div class="telegram-chat">
  <div class="telegram-message telegram-message-sent">
    <p>发送的消息</p>
    <span class="telegram-time">10:30</span>
  </div>
  <div class="telegram-message telegram-message-received">
    <p>接收的消息</p>
    <span class="telegram-time">10:31</span>
  </div>
</div>
<div class="telegram-avatar">
  <img src="avatar.jpg" alt="头像">
  <span class="telegram-online"></span>
</div>
<button class="telegram-btn">发送</button>
```
