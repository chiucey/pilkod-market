# B站设计系统

哔哩哔哩的弹幕视频设计美学。

## 设计理念

B站追求**年轻**、**创意**、**社区**。打造Z世代的文化聚集地。

## 色彩系统

### 品牌色
- Primary: `#FB7299` (B站粉)
- Primary Hover: `#E66589`
- Primary Dark: `#CC5888`

### 辅助色
- Blue: `#23ADE5`
- Orange: `#FFA631`
- Green: `#66CC33`

### 背景色

#### 浅色模式
- Background: `#F4F5F7`
- Background Secondary: `#FFFFFF`
- Background Dark: `#1D1D1D`

#### 深色模式
- Background Dark Primary: `#181818`
- Background Dark Secondary: `#222222`
- Background Dark Card: `#2D2D2D`

### 文字色

#### 浅色模式
- Text Primary: `#181818`
- Text Secondary: `#666666`
- Text Tertiary: `#999999`

#### 深色模式
- Text Dark Primary: `#E8E8E8`
- Text Dark Secondary: `#A8A8A8`
- Text Dark Tertiary: `#6B6B6B`

### 弹幕色
- White: `#FFFFFF`
- Yellow: `#FFFF00`
- Red: `#FF4B4B`
- Blue: `#00A1D6`
- Green: `#66CC33`
- Orange: `#FFA631`

## 字体

### 字体栈
```
'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif
```

### 字号
- Display: 28px
- H1: 24px
- H2: 20px
- Body: 14px
- Caption: 12px
- Danmaku: 18px

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px

## 圆角

- sm: 2px
- md: 4px
- lg: 8px
- xl: 12px

## 组件样式

### 视频播放器

- Background: `#000000`
- Control Bar: 高度 48px
- Progress Bar: 高度 3px

### 弹幕

- Font Size: 18px
- Speed: 6px/帧
- Color: 白色/黄色/红色
- Border: 1px黑色(可选)

### 按钮

**主要按钮**
- Background: `#FB7299`
- Color: `#FFFFFF`
- Border Radius: 4px
- Height: 36px

**次要按钮**
- Background: `#FFFFFF`
- Color: `#FB7299`
- Border: 1px solid `#FB7299`

### 用户头像

- Border Radius: 50%
- Sizes: 24px / 32px / 40px / 64px
- 粉丝牌: 渐变边框

### 专栏卡片

- Background: `#FFFFFF`
- Border Radius: 8px
- Padding: 16px
- Image Aspect: 16:9

## 设计注意事项

1. **弹幕文化** - 弹幕是核心特色
2. **年轻化** - 粉色品牌，活泼设计
3. **社区化** - 评论、点赞、投币
4. **二次元** - ACG 文化元素

## 适用场景

- 🎬 弹幕视频
- 🎮 游戏直播
- 🎵 音乐/舞蹈
- 📺 番剧动漫

## 组件示例 HTML 结构

```html
<div class="bilibili-player">
  <video class="bilibili-video">视频</video>
  <div class="bilibili-danmaku">弹幕内容</div>
  <div class="bilibili-controls">控制栏</div>
</div>
<div class="bilibili-card">
  <img class="bilibili-thumbnail" src="cover.jpg" alt="封面">
  <div class="bilibili-info">
    <h3>标题</h3>
    <span>UP主</span>
    <span>100万播放</span>
  </div>
</div>
<button class="bilibili-btn-primary">三连</button>
```
