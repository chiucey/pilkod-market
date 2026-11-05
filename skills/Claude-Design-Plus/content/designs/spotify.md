# Spotify Design System

Spotify 的音乐流媒体设计美学。

## 设计理念

Spotify 追求**音乐**、**发现**、**个性化**。让音乐触手可及。

## 色彩系统

### 品牌色
- Primary: `#1DB954` (Spotify 绿)
- Primary Hover: `#1ED760`
- Primary Dark: `#169C46`

### 背景色

#### 深色模式 (主模式)
- Background: `#000000`
- Background Secondary: `#121212`
- Background Tertiary: `#1E1E1E`
- Background Card: `#181818`
- Background Elevated: `#282828`

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F6F6F6`
- Background Card: `#F0F0F0`

### 文字色

#### 深色模式
- Text Primary: `#FFFFFF`
- Text Secondary: `#B3B3B3`
- Text Tertiary: `#535353`

#### 浅色模式
- Text Primary: `#191414`
- Text Secondary: `#5F5F5F`
- Text Tertiary: `#B3B3B3`

### 功能色
- Green: `#1DB954`
- Blue: `#509BF5`
- Purple: `#8C67AB`
- Pink: `#E9148C`
- Orange: `#F0374D`

## 字体

### 字体栈
```
'Spotify Circular', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif
```

### 字号
- Display: 32px / 700
- H1: 24px / 700
- H2: 20px / 700
- H3: 16px / 600
- Body: 15px / 400
- Small: 13px / 400
- Micro: 11px / 400

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
- full: 9999px
- card: 8px

## 组件样式

### 专辑封面

- Aspect Ratio: 1:1
- Border Radius: 8px
- Shadow: `0 4px 60px rgba(0, 0, 0, 0.5)`

### 播放列表卡片

- Background: `#181818`
- Border Radius: 8px
- Padding: 16px
- Hover Background: `#282828`

### 播放按钮

- Size: 48px
- Background: `#1DB954`
- Border Radius: 50%
- Icon: 播放/暂停

### 进度条

- Track Color: `#4D4D4D`
- Progress Color: `#B3B3B3`
- Height: 4px
- Hover Height: 6px

### 专辑封面网格

- Grid Gap: 24px
- Card Width: 100% (最小 180px)

### 侧边栏导航

- Background: `#000000`
- Width: 240px
- Item Height: 48px
- Active Indicator: `#1DB954`

## 设计注意事项

1. **音乐可视化** - 专辑封面是核心
2. **暗色优先** - 深色主题是主模式
3. **绿色品牌** - Spotify 绿是标志
4. **个性化** - 推荐和发现是核心

## 适用场景

- 🎵 音乐播放器
- 🎧 播客平台
- 📻 音频流
- 🎶 歌单分享

## 组件示例 HTML 结构

```html
<div class="spotify-card">
  <img class="spotify-cover" src="album.jpg" alt="专辑封面">
  <div class="spotify-play-button">▶</div>
  <h3 class="spotify-title">专辑标题</h3>
  <p class="spotify-artist">艺术家</p>
</div>
<div class="spotify-playlist">
  <div class="spotify-track">
    <span class="spotify-track-number">1</span>
    <img class="spotify-track-cover" src="cover.jpg" alt="">
    <div class="spotify-track-info">
      <span class="spotify-track-title">歌曲</span>
      <span class="spotify-track-artist">艺术家</span>
    </div>
    <span class="spotify-track-duration">3:45</span>
  </div>
</div>
<div class="spotify-player-bar">
  <div class="spotify-progress-bar">
    <div class="spotify-progress" style="width: 45%;"></div>
  </div>
</div>
```
