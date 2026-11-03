# Arco Design 系统

字节跳动出品的企业级设计系统。

## 设计理念

Arco Design 追求**确定**、**一致**、**丰富**。服务于字节跳动众多产品线。

## 色彩系统

### 品牌色
- Primary: `#165DFF`
- Primary Hover: `#4080FF`
- Primary Active: `#0043CC`

### 功能色
- Success: `#00B42A`
- Warning: `#FF7D00`
- Error: `#F53F3F`
- Info: `#165DFF`

### 中性色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F7F8FA`
- Background Tertiary: `#F2F3F5`
- Text Primary: `#1D2129`
- Text Secondary: `#4E5969`
- Text Tertiary: `#86909C`
- Border: `#E5E6EB`
- Border Secondary: `#F1F2F5`

#### 深色模式
- Background Dark: `#1D1D1D`
- Background Dark Secondary: `#252526`
- Background Dark Tertiary: `#2E2E30`
- Text Dark Primary: `#E5E6EB`
- Text Dark Secondary: `#8F939E`
- Text Dark Tertiary: `#6B7280`
- Border Dark: `#3D3D3D`

### 语义色
- Red: `#F53F3F`
- Orangered: `#F77234`
- Orange: `#FF7D00`
- Gold: `#F5A623`
- Yellow: `#FADC19`
- Lime: `#A0D911`
- Green: `#00B42A`
- Cyan: `#14C9C9`
- Blue: `#165DFF`
- Purple: `#722ED1`
- Magenta: `#D91AD9`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
```

### 中文
```
'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif
```

### 字号
- Display: 36px
- H1: 28px
- H2: 24px
- H3: 20px
- H4: 16px
- Body: 14px
- Caption: 12px
- Small: 12px

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px

## 圆角

- xs: 2px
- sm: 4px
- md: 6px
- lg: 8px
- xl: 12px
- 2xl: 16px
- full: 9999px

## 阴影

### 浅色模式
```css
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
```

### 深色模式
```css
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.36);
```

## 组件样式

### 按钮

**主要按钮**
- Background: `#165DFF`
- Color: `#FFFFFF`
- Border Radius: 6px
- Height: 32px
- Padding: 0 16px

**次要按钮**
- Background: `#F7F8FA`
- Color: `#1D2129`
- Border: 1px solid `#E5E6EB`

**文字按钮**
- Color: `#165DFF`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E5E6EB`
- Border Radius: 6px
- Height: 32px
- Focus Border: `#165DFF`

### 卡片

- Background: `#FFFFFF`
- Border Radius: 8px
- Padding: 20px
- Border: 1px solid `#E5E6EB`

### 表格

- Header Background: `#F7F8FA`
- Row Border: `#F1F2F5`
- Hover: `#F7F8FA`

## 适用场景

- 🏢 企业后台
- 📊 数据平台
- 💼 办公系统
- 📱 管理工具

## 组件示例 HTML 结构

```html
<button class="arco-btn arco-btn-primary">主要</button>
<button class="arco-btn arco-btn-secondary">次要</button>
<input class="arco-input" type="text" placeholder="输入">
<div class="arco-card">
  <div class="arco-card-header">标题</div>
  <div class="arco-card-body">内容</div>
</div>
```
