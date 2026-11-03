# 钉钉设计系统

钉钉的企业通讯设计语言。

## 设计理念

钉钉追求**高效**、**协同**、**安全**。企业数字化办公的基础设施。

## 色彩系统

### 品牌色
- Primary: `#1677FF` (钉钉蓝)
- Primary Hover: `#4096FF`
- Primary Dark: `#0958D9`

### 辅助色
- Success: `#00B42A`
- Warning: `#FF9A00`
- Error: `#F53F3F`
- Info: `#1677FF`

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
'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif
```

### 字号
- Display: 32px
- H1: 24px
- H2: 20px
- H3: 16px
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
- Background: `#1677FF`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 40px

**次要按钮**
- Background: `#F5F7FA`
- Color: `#1D2129`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E5E6EB`
- Border Radius: 8px
- Height: 40px
- Focus Border: `#1677FF`

### 卡片

- Background: `#FFFFFF`
- Border: 1px solid `#E5E6EB`
- Border Radius: 12px
- Padding: 20px

## 适用场景

- 💼 企业办公
- 👥 视频会议
- 📊 协同文档
- 🤖 智能助手

## 组件示例 HTML 结构

```html
<button class="dingtalk-btn-primary">主要</button>
<button class="dingtalk-btn-secondary">次要</button>
<input class="dingtalk-input" type="text" placeholder="输入">
<div class="dingtalk-card">
  <h3>标题</h3>
  <p>内容</p>
</div>
```
