# YouTube Design System

YouTube 的视频平台设计美学。

## 设计理念

YouTube 追求**沉浸**、**发现**、**创作**。让每个人都能成为创作者。

## 色彩系统

### 品牌色
- Primary: `#FF0000` (YouTube 红)
- Primary Hover: `#CC0000`
- Primary Dark: `#990000`

### 背景色

#### 浅色模式
- Background: `#F9F9F9`
- Background Video: `#000000`
- Background Secondary: `#E5E5E5`
- Background Card: `#FFFFFF`

#### 深色模式
- Background Dark: `#0F0F0F`
- Background Dark Secondary: `#1A1A1A`
- Background Dark Card: `#212121`

### 文字色

#### 浅色模式
- Text Primary: `#0F0F0F`
- Text Secondary: `#606060`
- Text Tertiary: `#8C8C8C`

#### 深色模式
- Text Dark Primary: `#F1F1F1`
- Text Dark Secondary: `#AAAAAA`
- Text Dark Tertiary: `#717171`

## 字体

### 字体栈
```
'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif
```

### 中文
```
'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif
```

### 字号
- Display: 28px / 500
- H1: 24px / 500
- H2: 20px / 500
- H3: 16px / 500
- Body: 14px / 400
- Caption: 12px / 400

## 间距系统

基于 8px 网格：
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

## 组件样式

### 视频缩略图

- Aspect Ratio: 16:9
- Border Radius: 12px
- Hover: 显示时长标签
- Duration Badge: `#000000` / `#FFFFFF`

### 播放按钮

- Size: 48px
- Color: `#FF0000`
- Hover: Scale 1.1

### 频道头像

- Border Radius: 50%
- Sizes: 24px / 32px / 40px / 88px

### 进度条

- Track: `#5F5F5F`
- Buffer: `#393939`
- Progress: `#FF0000`
- Height: 4px
- Hover Height: 8px

### 按钮

**Subscribe 按钮**
- Background: `#FF0000`
- Color: `#FFFFFF`
- Border Radius: 20px
- Height: 36px
- Padding: 0 16px
- Hover: `#CC0000`

**Secondary 按钮**
- Background: transparent
- Color: `#065FD4`
- Border: 1px solid `#065FD4`

### 搜索栏

- Background: `#FFFFFF`
- Border: 1px solid `#CCCCCC`
- Border Radius: 20px
- Height: 40px
- Focus Border: `#065FD4`

## 设计注意事项

1. **视频优先** - 视频缩略图是核心
2. **红色品牌** - YouTube 红贯穿始终
3. **简洁导航** - 搜索是核心功能
4. **创作者导向** - 频道页面突出创作者

## 适用场景

- 🎬 视频平台
- 📺 直播平台
- 🎥 创作者工具
- 🎞️ 视频分享

## 组件示例 HTML 结构

```html
<div class="youtube-thumbnail">
  <img src="thumbnail.jpg" alt="视频">
  <span class="youtube-duration">12:34</span>
</div>
<div class="youtube-video-info">
  <img class="youtube-channel-avatar" src="avatar.jpg" alt="频道">
  <div class="youtube-video-meta">
    <h3 class="youtube-title">视频标题</h3>
    <span class="youtube-channel">频道名</span>
    <span class="youtube-views">100万次观看</span>
  </div>
</div>
<button class="youtube-subscribe-btn">订阅</button>
<div class="youtube-search">
  <input type="text" placeholder="搜索">
</div>
```
