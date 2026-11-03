# 百度 AI 设计系统

百度 AI 产品设计语言。

## 设计理念

百度追求**科技**、**智能**、**创新**。服务于百度 AI 生态系统。

## 色彩系统

### 品牌色
- Primary: `#2932E1` (百度蓝)
- Primary Hover: `#3948F0`
- Primary Dark: `#1C24B3`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F5F7FA`
- Background Tertiary: `#EDF0F5`

#### 深色模式
- Background Dark: `#1A1A1A`
- Background Dark Secondary: `#252525`

### 文字色

#### 浅色模式
- Text Primary: `#1D1D1F`
- Text Secondary: `#646473`
- Text Tertiary: `#91929A`

#### 深色模式
- Text Dark Primary: `#FFFFFF`
- Text Dark Secondary: `#A1A1A6`
- Text Dark Tertiary: `#6B6B73`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
```

### 中文
```
'PingFang SC', 'Microsoft YaHei', 'Heiti SC', sans-serif
```

### 字号
- Display: 36px
- H1: 28px
- H2: 22px
- H3: 18px
- Body: 14px
- Caption: 12px

## 间距系统

基于 8px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px

## 圆角

- sm: 4px
- md: 6px
- lg: 8px
- xl: 12px

## 组件样式

### 按钮

**主要按钮**
- Background: `#2932E1`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 40px

**次要按钮**
- Background: `#F5F7FA`
- Color: `#1D1D1F`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#D8D8D8`
- Border Radius: 6px
- Height: 40px
- Focus Border: `#2932E1`

## 适用场景

- 🔍 搜索引擎
- 🤖 AI 对话
- 🗣️ 语音助手
- 🚗 自动驾驶

## 组件示例 HTML 结构

```html
<button class="baidu-btn-primary">百度一下</button>
<button class="baidu-btn-secondary">次要</button>
<input class="baidu-input" type="text" placeholder="搜索">
```
