# 小红书设计系统

小红书的生活方式美学设计。

## 设计理念

小红书追求**美好**、**真实**、**分享**。打造精致生活分享社区。

## 色彩系统

### 品牌色
- Primary: `#FF2442` (小红书红)
- Primary Hover: `#E6213B`
- Primary Dark: `#CC1D30`

### 背景色

#### 浅色模式
- Background: `#FFFBF8`
- Background Secondary: `#FFF8F5`
- Background Card: `#FFFFFF`

#### 深色模式
- Background Dark: `#1A1A1A`
- Background Dark Secondary: `#242424`

### 文字色

#### 浅色模式
- Text Primary: `#2B2B2B`
- Text Secondary: `#666666`
- Text Tertiary: `#999999`

#### 深色模式
- Text Dark Primary: `#FFFFFF`
- Text Dark Secondary: `#A0A0A0`
- Text Dark Tertiary: `#6B6B6B`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif
```

### 字号
- Display: 24px / 600
- H1: 20px / 600
- H2: 17px / 600
- Body: 15px / 400
- Small: 13px / 400

## 间距系统

基于 8px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px

## 圆角

- sm: 4px
- md: 8px
- lg: 12px
- xl: 16px
- card: 12px

## 组件样式

### 笔记卡片

- Background: `#FFFFFF`
- Border Radius: 12px
- Padding: 16px
- Image Aspect: 3:4 / 16:9

### 头像

- Border Radius: 50%
- Border: 2px solid `#FF2442`
- Sizes: 36px / 44px / 56px

### 按钮

**主要按钮**
- Background: `#FF2442`
- Color: `#FFFFFF`
- Border Radius: 20px
- Height: 40px
- Padding: 0 24px

**次要按钮**
- Background: `#FFF8F5`
- Color: `#FF2442`

### 标签

- Background: `#FFF0F2`
- Color: `#FF2442`
- Border Radius: 12px
- Padding: 4px 12px
- Font Size: 12px

## 设计注意事项

1. **图片优先** - 精美的图片是核心
2. **真实分享** - 强调真实用户体验
3. **生活方式** - 美妆、穿搭、旅行、家居
4. **社区氛围** - 点赞、评论、收藏

## 适用场景

- 📝 种草笔记
- 🛍️ 商品推荐
- 💄 美妆分享
- ✈️ 旅行攻略

## 组件示例 HTML 结构

```html
<div class="xhs-note-card">
  <img class="xhs-note-image" src="note.jpg" alt="笔记">
  <div class="xhs-note-title">笔记标题</div>
  <div class="xhs-note-user">
    <img class="xhs-avatar" src="avatar.jpg" alt="头像">
    <span>用户名</span>
  </div>
</div>
<button class="xhs-btn-primary">关注</button>
<div class="xhs-tag">种草</div>
```
