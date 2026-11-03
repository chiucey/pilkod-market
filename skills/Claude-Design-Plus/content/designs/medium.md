# Medium Design System

Medium 的内容平台设计美学。

## 设计理念

Medium 追求**阅读**、**写作**、**思想**。专注于内容的极致阅读体验。

## 色彩系统

### 品牌色
- Primary: `#000000` (Medium 黑)
- Primary Hover: `#333333`
- Accent: `#1A8917` (Medium 绿)

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F9F9F9`
- Background Tertiary: `#F3F3F3`
- Background Article: `#FEFEFE`

#### 深色模式
- Background Dark: `#191919`
- Background Dark Secondary: `#242424`
- Background Dark Article: `#121212`

### 文字色

#### 浅色模式
- Text Primary: `#292929`
- Text Secondary: `#757575`
- Text Tertiary: `#AAAAAA`

#### 深色模式
- Text Dark Primary: `#E0E0E0`
- Text Dark Secondary: `#9B9B9B`
- Text Dark Tertiary: `#6B6B6B`

## 字体

### 阅读字体
```
'Charter', Georgia, 'Times New Roman', serif
```

### 界面字体
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 中文
```
'PingFang SC', 'Microsoft YaHei', 'Source Han Sans CN', sans-serif
```

### 字号

#### 文章内容
- Display: 42px / 700
- H1: 36px / 700
- H2: 28px / 600
- H3: 24px / 600
- Body: 18px / 400 / 1.8 line-height
- Caption: 15px / 400

#### 界面
- Nav: 14px / 500
- Button: 15px / 500
- Small: 13px / 400

## 间距系统

基于 8px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px
- 3xl: 64px

### 文章最大宽度
- Article: 680px
- Wide Image: 960px
- Full Width: 100%

## 圆角

- sm: 4px
- md: 6px
- lg: 8px

## 组件样式

### 文章标题

- Font: Charter / Georgia
- Size: 42px
- Weight: 700
- Line Height: 1.2

### 文章正文

- Font: Charter / Georgia
- Size: 18px
- Weight: 400
- Line Height: 1.8
- Max Width: 680px

### 作者信息

- Avatar: 48px / 64px
- Name: 18px / 500
- Bio: 15px / 400
- Date: 15px / 400 / `#757575`

### 标签

- Background: `#F3F3F3`
- Color: `#757575`
- Border Radius: 20px
- Padding: 4px 12px
- Font Size: 13px

### 按钮

**关注按钮**
- Background: `#1A8917`
- Color: `#FFFFFF`
- Border Radius: 20px
- Height: 36px
- Padding: 0 20px

**文字按钮**
- Color: `#1A8917`

### 阅读进度条

- Background: `#F3F3F3`
- Progress: `#1A8917`
- Height: 3px

## 设计注意事项

1. **阅读优先** - 字体和排版是核心
2. **内容为王** - 极简界面，突出内容
3. **衬线字体** - Charter/Georgia 增强阅读感
4. **绿色强调** - Medium 绿用于 CTA

## 适用场景

- 📝 博客平台
- 📖 文章阅读
- ✍️ 内容创作
- 💡 知识分享

## 组件示例 HTML 结构

```html
<article class="medium-article">
  <h1 class="medium-title">文章标题</h1>
  <div class="medium-author">
    <img class="medium-avatar" src="avatar.jpg" alt="头像">
    <div class="medium-author-info">
      <span class="medium-author-name">作者名</span>
      <span class="medium-date">2024年1月1日</span>
    </div>
  </div>
  <div class="medium-content">
    <p>正文内容...</p>
  </div>
  <div class="medium-tags">
    <span class="medium-tag">标签</span>
  </div>
</article>
<button class="medium-follow-btn">关注</button>
```
