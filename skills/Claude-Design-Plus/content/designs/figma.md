# Figma Design System

Figma 的设计系统代表协作设计的最高水准。

## 设计理念

Figma 追求**协作**、**创意**、**专业**。每个细节都为设计师和开发者协作而生。

## 色彩系统

### 主色
- Primary: `#F24E1E` (Figma 红)
- Primary Variant: `#FF7262`
- Secondary: `#A259FF` (Figma 紫)
- Accent: `#1ABCFE` (Figma 蓝)

### Figma 四色
- Coral: `#F24E1E`
- Purple: `#A259FF`
- Blue: `#1ABCFE`
- Green: `#0ACF83`
- Yellow: `#FFC700`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#E8ECEF`
- Background Tertiary: `#F5F5F5`

#### 深色模式
- Background Dark: `#1E1E1E`
- Background Dark Secondary: `#2C2C2C`
- Background Dark Tertiary: `#333333`

### 文字色

#### 浅色模式
- Text Primary: `#333333`
- Text Secondary: `#666666`
- Text Tertiary: `#999999`

#### 深色模式
- Text Dark Primary: `#FFFFFF`
- Text Dark Secondary: `#A3A3A3`
- Text Dark Tertiary: `#757575`

### 边框色

- Border: `#E0E0E0`
- Border Dark: `#404040`

## 字体

### 字体栈
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 字号
- Display: 32px / 700
- H1: 24px / 600
- H2: 18px / 600
- H3: 14px / 600
- Body: 14px / 400
- Small: 12px / 400
- Micro: 10px / 400

## 间距系统

基于 8px 网格：
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
- full: 9999px

## 组件样式

### 按钮

**主要按钮**
- Background: `#F24E1E`
- Color: `#FFFFFF`
- Border Radius: 6px
- Height: 32px
- Padding: 0 16px

**次要按钮**
- Background: `#E8ECEF`
- Color: `#333333`
- Border Radius: 6px

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E0E0E0`
- Border Radius: 4px
- Height: 32px
- Focus Border: `#1ABCFE`

### 标签

- Border Radius: 4px
- Padding: 2px 8px
- Font Size: 11px
- Font Weight: 500

## 设计注意事项

1. **四色系统** - Figma Logo 四色可作为强调色
2. **协作优先** - 评论、共享组件
3. **组件化** - 每个元素可复用

## 适用场景

- 🎨 设计工具界面
- 🖼️ 创意平台
- 👥 协作设计
- 📐 原型设计

## 组件示例 HTML 结构

```html
<button class="figma-btn-primary">主要</button>
<button class="figma-btn-secondary">次要</button>
<input class="figma-input" type="text" placeholder="输入">
```
