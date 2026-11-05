# Google Material Design

Google 的 Material Design 设计系统。

## 设计理念

Material Design 追求**材料**、**动效**、**层次**。用纸张的隐喻构建数字界面。

## 色彩系统

### 品牌色
- Primary: `#4285F4` (Google 蓝)
- Primary Variant: `#1A73E8`
- Secondary: `#34A853` (Google 绿)
- Secondary Variant: `#2E9B4A`
- Error: `#EA4335` (Google 红)
- Warning: `#FBBC04` (Google 黄)

### 浅色主题
- Background: `#FFFFFF`
- Surface: `#FFFFFF`
- On Primary: `#FFFFFF`
- On Secondary: `#FFFFFF`
- On Background: `#202124`
- On Surface: `#202124`

### 深色主题
- Background: `#202124`
- Surface: `#303134`
- On Primary: `#FFFFFF`
- On Secondary: `#FFFFFF`
- On Background: `#E8EAED`
- On Surface: `#E8EAED`

## 字体

### 字体栈
```
'Google Sans', 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
```

### 字号
- Display: 57px
- Headline Large: 32px
- Headline Medium: 28px
- Headline Small: 24px
- Title Large: 22px
- Title Medium: 16px / 500
- Title Small: 14px / 500
- Body Large: 16px
- Body Medium: 14px
- Body Small: 12px
- Label Large: 14px / 500
- Label Medium: 12px / 500
- Label Small: 11px / 500

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 40px
- 3xl: 48px

## 圆角

- none: 0
- sm: 4px
- md: 8px
- lg: 12px
- xl: 16px
- xl: 28px
- full: 9999px

## 阴影

### Elevation
```css
level1: 0 1px 2px rgba(0,0,0,0.3), 0 1px 3px rgba(0,0,0,0.3)
level2: 0 2px 4px rgba(0,0,0,0.3), 0 2px 6px rgba(0,0,0,0.3)
level3: 0 4px 8px rgba(0,0,0,0.3), 0 4px 12px rgba(0,0,0,0.3)
```

## 组件样式

### Filled Button

- Background: `#4285F4`
- Color: `#FFFFFF`
- Border Radius: 20px
- Height: 40px
- Padding: 0 24px

### Outlined Button

- Background: transparent
- Color: `#4285F4`
- Border: 1px solid `#DADCE0`
- Border Radius: 20px

### Text Button

- Color: `#4285F4`

### FAB

- Background: `#4285F4`
- Color: `#FFFFFF`
- Border Radius: 16px
- Size: 56px
- Shadow: level3

### Card

- Background: `#FFFFFF`
- Border Radius: 12px
- Padding: 16px
- Shadow: level1

### Text Field

- Background: `#F1F3F4`
- Border Radius: 4px
- Height: 56px
- Focus Background: `#FFFFFF`
- Focus Border: 2px `#4285F4`

### Chip

- Background: `#E8F0FE`
- Color: `#1967D2`
- Border Radius: 8px
- Height: 32px
- Padding: 0 12px

## 设计注意事项

1. **材料隐喻** - 纸张和墨水
2. **动效设计** - 状态过渡动画
3. **色彩系统** - 主色/辅色/错误色
4. **层次阴影** - 不同海拔不同阴影

## 适用场景

- 📱 Android 应用
- 🌐 Web 应用
- 💻 桌面应用
- 🏢 企业工具

## 组件示例 HTML 结构

```html
<button class="md-btn-filled">主要按钮</button>
<button class="md-btn-outlined">轮廓按钮</button>
<button class="md-btn-text">文字按钮</button>
<div class="md-fab">+</div>
<div class="md-card">
  <h3>卡片标题</h3>
  <p>卡片内容</p>
</div>
<input class="md-text-field" type="text" placeholder="输入">
<div class="md-chip">标签</div>
```
