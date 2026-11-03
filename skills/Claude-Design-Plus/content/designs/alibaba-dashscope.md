# 阿里通义千问设计系统

阿里云通义千问的设计语言。

## 设计理念

通义千问追求**智能**、**可靠**、**开放**。服务于阿里云生态系统。

## 色彩系统

### 品牌色
- Primary: `#3370FF` (阿里蓝)
- Primary Hover: `#4F8AFF`
- Primary Dark: `#2860CC`

### 辅助色
- Success: `#00A870`
- Warning: `#FF9A00`
- Error: `#E53333`
- Info: `#3370FF`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F5F7FA`
- Background Tertiary: `#EDF0F5`

#### 深色模式
- Background Dark: `#1F1F1F`
- Background Dark Secondary: `#292929`

### 文字色

#### 浅色模式
- Text Primary: `#1D2129`
- Text Secondary: `#4E5969`
- Text Tertiary: `#86909C`

#### 深色模式
- Text Dark Primary: `#E5E6EB`
- Text Dark Secondary: `#8F939E`
- Text Dark Tertiary: `#6B7280`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
```

### 中文
```
'PingFang SC', 'Microsoft YaHei', sans-serif
```

### 字号
- Display: 36px
- H1: 28px
- H2: 22px
- H3: 18px
- Body: 14px
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
- md: 6px
- lg: 8px
- xl: 12px

## 组件样式

### 按钮

**主要按钮**
- Background: `#3370FF`
- Color: `#FFFFFF`
- Border Radius: 6px
- Height: 36px
- Padding: 0 20px

**次要按钮**
- Background: `#F5F7FA`
- Color: `#1D2129`
- Border: 1px solid `#E5E6EB`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E5E6EB`
- Border Radius: 6px
- Height: 36px
- Focus Border: `#3370FF`

### 卡片

- Background: `#FFFFFF`
- Border: 1px solid `#E5E6EB`
- Border Radius: 8px
- Padding: 20px

## 适用场景

- 💬 AI 对话
- 📚 知识问答
- 🔧 API 服务
- ☁️ 云产品

## 组件示例 HTML 结构

```html
<button class="tongyi-btn-primary">提问</button>
<button class="tongyi-btn-secondary">次要</button>
<input class="tongyi-input" type="text" placeholder="请输入问题">
<div class="tongyi-card">
  <div class="tongyi-card-header">通义千问</div>
  <div class="tongyi-card-body">回复内容</div>
</div>
```
