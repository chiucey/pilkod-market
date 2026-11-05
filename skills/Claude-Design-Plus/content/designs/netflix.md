# Netflix Design System

Netflix 的流媒体设计美学。

## 设计理念

Netflix 追求**沉浸**、**发现**、**娱乐**。让用户沉浸在内容中。

## 色彩系统

### 品牌色
- Primary: `#E50914` (Netflix 红)
- Primary Hover: `#B20710`
- Primary Dark: `#831013`

### 背景色

#### 深色模式 (主模式)
- Background: `#000000`
- Background Secondary: `#141414`
- Background Card: `#1F1F1F`
- Background Hover: `#2A2A2A`

### 文字色

#### 深色模式
- Text Primary: `#FFFFFF`
- Text Secondary: `#B3B3B3`
- Text Tertiary: `#666666`

### 功能色
- Red: `#E50914`
- Black: `#000000`
- White: `#FFFFFF`

## 字体

### 字体栈
```
'Netflix Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif
```

### 中文
```
'Netflix Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif
```

### 字号
- Display: 48px / 700
- H1: 36px / 700
- H2: 24px / 600
- H3: 18px / 600
- Body: 16px / 400
- Small: 14px / 400
- Caption: 12px / 400

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
- md: 6px
- lg: 8px
- card: 4px

## 组件样式

### 海报/缩略图

- Aspect Ratio: 2:3 (海报) / 16:9 (预告片)
- Border Radius: 4px
- Hover: Scale 1.05
- Hover Effect: 显示预览/信息

### 播放按钮

- Size: 48px
- Background: `#E50914`
- Border Radius: 50%
- Icon: 播放 ▶

### 进度条

- Track: `#404040`
- Progress: `#E50914`
- Height: 4px

### 按钮

**Play 按钮**
- Background: `#E50914`
- Color: `#FFFFFF`
- Border Radius: 4px
- Height: 36px
- Padding: 0 16px

**Secondary 按钮**
- Background: `rgba(109, 109, 110, 0.7)`
- Color: `#FFFFFF`
- Border Radius: 4px

**Icon 按钮**
- Background: transparent
- Color: `#FFFFFF`
- Border: 1px solid `#404040`

### 简介卡片

- Background: `#141414`
- Border Radius: 4px
- Padding: 24px

### 个人头像

- Border Radius: 50%
- Sizes: 24px / 32px / 48px
- Border: 2px solid `#2A2A2A`

## 设计注意事项

1. **内容为王** - 海报/缩略图是核心
2. **极简界面** - 深色背景，内容突出
3. **红色强调** - Netflix 红用于 CTA
4. **个性化推荐** - "因为您看过..."

## 适用场景

- 🎬 视频流媒体
- 📺 电视剧/电影
- 🎥 原创内容
- 🌐 全球内容平台

## 组件示例 HTML 结构

```html
<div class="netflix-row">
  <div class="netflix-card">
    <img class="netflix-poster" src="poster.jpg" alt="海报">
    <div class="netflix-overlay">
      <button class="netflix-play-btn">▶</button>
    </div>
  </div>
</div>
<div class="netflix-hero">
  <h1 class="netflix-title">标题</h1>
  <p class="netflix-description">描述</p>
  <button class="netflix-btn-primary">▶ 播放</button>
  <button class="netflix-btn-secondary">更多信息</button>
</div>
```
