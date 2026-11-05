# 抖音设计系统

抖音代表年轻、潮流、视觉冲击的短视频美学。

## 设计理念

抖音追求**酷炫**、**年轻**、**沉浸式**。大胆用色，动感十足。

## 色彩系统

### 品牌色
- Primary: `#FE2C55` (抖音红)
- Primary Dark: `#E6264D`
- Secondary: `#25F4EE` (抖音青)
- Secondary Dark: `#20D9D2`

### 渐变色
- Gradient Start: `#FE2C55`
- Gradient End: `#25F4EE`
- Gradient: `linear-gradient(135deg, #FE2C55, #25F4EE)`

### 背景色

#### 深色模式 (主模式)
- Background: `#000000`
- Background Secondary: `#161823`
- Background Tertiary: `#1F1F1F`
- Background Elevated: `#2A2A2A`

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F8F8F8`

### 文字色

#### 深色模式
- Text Primary: `#FFFFFF`
- Text Secondary: `#A6A6A6`
- Text Tertiary: `#767676`

#### 浅色模式
- Text Primary: `#000000`
- Text Secondary: `#767676`

### 功能色
- Success: `#07C160`
- Warning: `#FF9500`
- Error: `#FA5151`

### 状态色
- Live: `#FE2C55`
- VIP: `#FFD700`
- Hot: `#FF3C3C`

## 字体

### 字体栈
```
'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif
```

### 字号

#### 主标题
- Size: 17px
- Weight: 600

#### 正文
- Size: 15px
- Weight: 400

#### 副标题
- Size: 13px
- Weight: 400

#### 评论区
- Size: 14px
- Weight: 400

#### 小字
- Size: 11px
- Weight: 400

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
- 2xl: 24px
- full: 9999px

## 阴影

### 卡片阴影
```css
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
```

### 悬浮阴影
```css
box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
```

### 底部导航阴影
```css
box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.15);
```

## 组件样式

### 按钮

**主要按钮 (实心)**
- Background: `#FE2C55`
- Color: `#FFFFFF`
- Border Radius: 22px
- Height: 44px
- Padding: 0 24px
- Font Size: 16px
- Font Weight: 600

**次要按钮 (轮廓)**
- Background: transparent
- Color: `#FFFFFF`
- Border: 1px solid `#FFFFFF`
- Border Radius: 22px

**幽灵按钮**
- Background: rgba(255, 255, 255, 0.2)
- Color: `#FFFFFF`
- Border Radius: 22px

### 输入框

- Background: rgba(255, 255, 255, 0.1)
- Border: none
- Border Radius: 22px
- Height: 44px
- Padding: 0 16px
- Font Size: 16px
- Color: `#FFFFFF`
- Placeholder Color: `#A6A6A6`

### 头像

- Border Radius: 50%
- Sizes:
  - 迷你: 24px
  - 小: 32px
  - 中: 40px
  - 大: 56px
  - 特大: 88px
- 粉丝环: 2px `#FE2C55`

### 视频封面

- Border Radius: 8px
- 封面比: 16:9
- 播放按钮: 居中，白色，64px

### Tab 栏

- Height: 44px
- Tab 间距: 32px
- Active Font: 17px / 600
- Inactive Font: 14px / 400
- Indicator: 2px `#FE2C55`

### 底部导航栏

- Background: `#161823` / 0.95
- Height: 56px + safe-area
- Icon Size: 28px
- Label Size: 10px
- Active Color: `#FE2C55`

### 评论卡片

- Background: `#161823`
- Border Radius: 12px
- Padding: 12px

### 点赞动画

- 爱心图标 `#FE2C55`
- 双击触发: 心形粒子效果
- 持续时间: 1.5s

## 图标

### 常用图标

| 名称 | 用途 |
|------|------|
| 主页 | 首页导航 |
| 发现 | 搜索发现 |
| + | 发布 |
| 消息 | 通知消息 |
| 我的 | 个人主页 |

### 图标样式

- 线性图标
- 线宽: 2px
- 圆角: 跟随图形
- 颜色: 继承当前色

## 设计注意事项

1. **年轻化** - 面向 Z 世代
2. **沉浸式** - 全屏体验
3. **动效丰富** - 微交互和动画
4. **大胆用色** - 红黑经典配色
5. **竖屏优先** - 9:16 竖屏格式
6. **大触摸** - 操作区域大

## 适用场景

- 🎬 短视频应用
- 🎵 音乐/舞蹈内容
- 🎭 才艺展示
- 📱 年轻化产品
- 🎮 娱乐应用

## 组件示例 HTML 结构

```html
<!-- 视频封面 -->
<div class="video-cover">
  <img src="cover.jpg" alt="封面">
  <div class="play-btn">▶</div>
  <div class="video-info">
    <span>100万播放</span>
    <span>1.2万点赞</span>
  </div>
</div>

<!-- 头像 -->
<div class="avatar avatar-large">
  <img src="avatar.jpg" alt="头像">
  <div class="follow-badge">+</div>
</div>

<!-- 底部导航 -->
<nav class="douyin-tab-bar">
  <div class="tab-item active">首页</div>
  <div class="tab-item">发现</div>
  <div class="tab-item douyin-plus">+</div>
  <div class="tab-item">消息</div>
  <div class="tab-item">我的</div>
</nav>

<!-- 评论 -->
<div class="comment-card">
  <div class="comment-avatar">头像</div>
  <div class="comment-content">
    <div class="comment-user">用户名</div>
    <div class="comment-text">评论内容</div>
    <div class="comment-actions">
      <span>1小时前</span>
      <span>回复</span>
      <span>❤️ 999</span>
    </div>
  </div>
</div>

<!-- 发布按钮 -->
<button class="douyin-btn-primary">发布作品</button>
```
