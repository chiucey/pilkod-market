# Microsoft Fluent Design System

Microsoft 的 Fluent Design 设计系统。

## 设计理念

Fluent 追求**移动优先**、**内容为王**、**无缝体验**。跨越设备和平台的统一设计语言。

## 色彩系统

### 品牌色
- Primary: `#0078D4` (Fluent 蓝)
- Primary Light: `#60CDFF`
- Primary Dark: `#004FB8`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F3F2F1`
- Background Tertiary: `#EDEBE9`
- Background Overlay: `#00000066`

#### 深色模式
- Background Dark: `#000000`
- Background Dark Secondary: `#1F1F1F`
- Background Dark Tertiary: `#2D2D2D`

### 文字色

#### 浅色模式
- Text Primary: `#000000`
- Text Secondary: `#605E5C`
- Text Tertiary: `#A19F9D`
- Text Disabled: `#C8C8C8`

#### 深色模式
- Text Dark Primary: `#FFFFFF`
- Text Dark Secondary: `#C4C4C4`
- Text Dark Tertiary: `#8A8A8A`

### 功能色
- Success: `#107C10`
- Warning: `#FFB900`
- Error: `#D13438`
- Info: `#0078D4`

## 字体

### 字体栈
```
'Segoe UI Variable', 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif
```

### 字号
- Display: 60px / 200
- Display Small: 28px / 200
- Headline: 32px / 600
- Title: 22px / 600
- Body Strong: 14px / 600
- Body: 14px / 400
- Caption: 12px / 400

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px

## 圆角

- none: 0
- sm: 4px
- md: 6px
- lg: 8px
- xl: 12px
- 2xl: 16px
- full: 9999px

## 阴影

### 轻微
```css
box-shadow: 0 1.3px 4px rgba(0, 0, 0, 0.13);
```

### 高度
```css
box-shadow: 0 3.5px 9px rgba(0, 0, 0, 0.13);
```

### 较高
```css
box-shadow: 0 7.5px 17.5px rgba(0, 0, 0, 0.13);
```

## 组件样式

### Button

**Primary**
- Background: `#0078D4`
- Color: `#FFFFFF`
- Border Radius: 4px
- Height: 32px
- Padding: 0 20px

**Secondary**
- Background: `#FFFFFF`
- Color: `#0078D4`
- Border: 1px solid `#8A8886`
- Border Radius: 4px

**Transparent**
- Background: transparent
- Color: `#0078D4`

### Input

- Background: `#FFFFFF`
- Border: 1px solid `#8A8886`
- Border Radius: 4px
- Height: 32px
- Padding: 0 12px
- Focus Border: `#0078D4`

### Card

- Background: `#FFFFFF`
- Border Radius: 8px
- Padding: 16px
- Border: 1px solid `#EDEBE9`

### Avatar

- Border Radius: 50%
- Sizes: 24px / 32px / 40px / 56px / 80px

### Chip

- Background: `#F3F2F1`
- Border Radius: 16px
- Height: 24px
- Padding: 0 12px
- Font: 14px

## 设计注意事项

1. **跨平台** - Windows/Mac/Web/iOS/Android
2. **内容优先** - 内容比 chrome 重要
3. **Acrylic** - 半透明毛玻璃效果
4. **深度** - Z 轴层次

## 适用场景

- 💻 Windows 应用
- 📱 Office 产品
- 🌐 Web 应用
- 🔧 工具软件

## 组件示例 HTML 结构

```html
<button class="fluent-btn-primary">主要</button>
<button class="fluent-btn-secondary">次要</button>
<input class="fluent-input" type="text" placeholder="输入">
<div class="fluent-card">
  <img class="fluent-avatar" src="avatar.jpg" alt="">
  <div class="fluent-card-content">
    <h3>标题</h3>
    <p>内容</p>
  </div>
</div>
<div class="fluent-chip">标签</div>
```
