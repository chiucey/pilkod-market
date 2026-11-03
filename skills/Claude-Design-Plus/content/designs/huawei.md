# 华为 HarmonyOS Design System

华为 HarmonyOS 的设计语言。

## 设计理念

HarmonyOS 追求**统一**、**流畅**、**安全**。万物互联的设计体验。

## 色彩系统

### 品牌色
- Primary: `#007DFF` (HarmonyOS 蓝)
- Primary Hover: `#409CFF`
- Primary Dark: `#005EB8`

### 辅助色
- Success: `#64BB5C`
- Warning: `#F7CE46`
- Error: `#E5483C`
- Info: `#64BB5C`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F1F3F5`
- Background Tertiary: `#E8EBED`

#### 深色模式
- Background Dark: `#000000`
- Background Dark Secondary: `#1C1C1D`
- Background Dark Tertiary: `#2E2E30`

### 文字色

#### 浅色模式
- Text Primary: `#182431`
- Text Secondary: `#99182431`
- Text Tertiary: `#66182431`

#### 深色模式
- Text Dark Primary: `#E6E9EB`
- Text Dark Secondary: `#99E6E9EB`
- Text Dark Tertiary: `#66E6E9EB`

## 字体

### 字体栈
```
'HarmonyOS Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
```

### 中文
```
'HarmonyOS Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif
```

### 字号
- Display: 36px
- H1: 28px
- H2: 24px
- H3: 20px
- Body: 16px
- Caption: 12px

## 间距系统

基于 4px 网格：
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

## 组件样式

### 按钮

**主要按钮**
- Background: `#007DFF`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 40px

**次要按钮**
- Background: `#F1F3F5`
- Color: `#182431`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#C6CAD1`
- Border Radius: 8px
- Height: 40px
- Focus Border: `#007DFF`

### 卡片

- Background: `#FFFFFF`
- Border Radius: 12px
- Padding: 16px

## 适用场景

- 📱 HarmonyOS 应用
- 🏠 IoT 设备
- 📺 智能屏
- 🚗 车机系统

## 组件示例 HTML 结构

```html
<button class="harmony-btn-primary">主要</button>
<button class="harmony-btn-secondary">次要</button>
<input class="harmony-input" type="text" placeholder="输入">
<div class="harmony-card">
  <h3>标题</h3>
  <p>内容</p>
</div>
```
