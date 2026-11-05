# 飞书设计系统

字节跳动飞书的企业协作设计语言。

## 设计理念

飞书追求**高效**、**协同**、**专业**。新一代企业协作方式。

## 色彩系统

### 品牌色
- Primary: `#244BFF` (飞书蓝)
- Primary Hover: `#3D61FF`
- Primary Dark: `#1C3DB8`

### 辅助色
- Success: `#00C4B8`
- Warning: `#FFB800`
- Error: `#FF583D`
- Info: `#244BFF`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F7F8FA`
- Background Tertiary: `#F2F3F7`

#### 深色模式
- Background Dark: `#1F1F1F`
- Background Dark Secondary: `#292929`

### 文字色

#### 浅色模式
- Text Primary: `#1F2329`
- Text Secondary: `#646A73`
- Text Tertiary: `#8B8E97`

#### 深色模式
- Text Dark Primary: `#E8E9EB`
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
- Background: `#244BFF`
- Color: `#FFFFFF`
- Border Radius: 8px
- Height: 36px
- Padding: 0 20px

**次要按钮**
- Background: `#F7F8FA`
- Color: `#1F2329`
- Border: 1px solid `#E2E4EB`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#E2E4EB`
- Border Radius: 8px
- Height: 36px
- Focus Border: `#244BFF`

### 卡片

- Background: `#FFFFFF`
- Border: 1px solid `#E2E4EB`
- Border Radius: 12px
- Padding: 20px

### 文档

- Max Width: 800px
- Line Height: 1.8
- Font Size: 15px

## 适用场景

- 📝 在线文档
- 💬 即时通讯
- 📊 表格
- 📅 日历

## 组件示例 HTML 结构

```html
<button class="feishu-btn-primary">主要</button>
<button class="feishu-btn-secondary">次要</button>
<input class="feishu-input" type="text" placeholder="输入">
<div class="feishu-card">
  <h3>标题</h3>
  <p>内容</p>
</div>
<div class="feishu-doc">
  <h1>文档标题</h1>
  <p>正文内容...</p>
</div>
```
