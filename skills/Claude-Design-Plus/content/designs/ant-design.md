# Ant Design 设计系统

蚂蚁金服的企业级设计系统，现代、专业、功能强大。

## 设计理念

Ant Design 代表**确定**、**自然**、**意义**。追求极致的用户体验和开发效率。

## 色彩系统

### 品牌色
- Primary: `#1677FF` (Ant Design 蓝)
- Primary Hover: `#4096FF`
- Primary Active: `#0958D9`

### 辅助色
- Success: `#52C41A`
- Warning: `#FAAD14`
- Error: `#FF4D4F`
- Info: `#1677FF`

### 中性色
- Background: `#FFFFFF`
- Background Secondary: `#FAFAFA`
- Background Dark: `#001529`
- Text Primary: `rgba(0, 0, 0, 0.88)`
- Text Secondary: `rgba(0, 0, 0, 0.65)`
- Text Tertiary: `rgba(0, 0, 0, 0.45)`
- Text Quaternary: `rgba(0, 0, 0, 0.25)`
- Border: `#D9D9D9`
- Border Secondary: `#E8E8E8`

### 浅色背景
- Primary 1: `#E6F4FF`
- Primary 2: `#BAE0FF`
- Primary 3: `#91CAFF`
- Primary 4: `#69B1FF`
- Primary 5: `#4096FF`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'
```

### 字号
- Display: 38px / 46px
- H1: 32px / 38px
- H2: 24px / 32px
- H3: 20px / 28px
- H4: 16px / 24px
- Body: 14px / 22px
- Caption: 12px / 20px

### 字重
- Light: 300
- Regular: 400
- Medium: 500
- Semibold: 600
- Bold: 700

## 间距系统

基于 8px 网格：
- xs: 8px
- sm: 12px
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
- full: 9999px

## 阴影

### 基础阴影
```css
box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02);
```

### 卡片阴影
```css
box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16), 0 3px 6px 0 rgba(0, 0, 0, 0.12), 0 5px 12px 4px rgba(0, 0, 0, 0.09);
```

### 弹窗阴影
```css
box-shadow: 0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 9px 28px 8px rgba(0, 0, 0, 0.05), 0 12px 48px 16px rgba(0, 0, 0, 0.03);
```

## 动效

### 过渡时长
- Fast: 100ms
- Normal: 200ms
- Slow: 300ms

### 缓动函数
```css
ease-out: cubic-bezier(0, 0, 0.2, 1);
ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
ease-in: cubic-bezier(0.4, 0, 1, 1);
```

## 组件样式

### 按钮

**主要按钮**
- Background: `#1677FF`
- Color: `#FFFFFF`
- Border Radius: 6px
- Height: 32px (sm), 40px (md), 48px (lg)
- Padding: 4px 15px (sm), 6px 15px (md), 7px 20px (lg)

**默认按钮**
- Background: `#FFFFFF`
- Border: 1px solid `#D9D9D9`
- Color: `rgba(0, 0, 0, 0.88)`

**危险按钮**
- Background: `#FF4D4F`
- Hover: `#FF7875`

### 输入框

- Background: `#FFFFFF`
- Border: 1px solid `#D9D9D9`
- Border Radius: 6px
- Height: 32px (sm), 40px (md)
- Padding: 4px 11px
- Focus Border: `#1677FF`
- Focus Shadow: `0 0 0 2px rgba(5, 145, 255, 0.1)`

### 卡片

- Background: `#FFFFFF`
- Border Radius: 8px
- Padding: 24px
- Border: 1px solid rgba(5, 145, 255, 0.09)

### 表格

- Header Background: `#FAFAFA`
- Header Color: `rgba(0, 0, 0, 0.88)`
- Row Border: `#F0F0F0`
- Row Hover: `#F5F5F5`

### 导航菜单

- Background: `#001529` (深色模式)
- Item Color: `rgba(255, 255, 255, 0.75)`
- Item Hover: `#FFFFFF`
- Item Active: `#1677FF`

## 图标

使用 Ant Design Icons：
- 图标字体: `anticon`
- 尺寸: 12px / 14px / 16px / 20px
- 颜色: 继承当前文字颜色

## 设计注意事项

1. **企业级标准** - 适合中后台系统和业务产品
2. **组件丰富** - 70+ 组件，覆盖各种场景
3. **主题定制** - 支持主题变量覆盖
4. **国际化** - 内置多语言支持
5. **无障碍** - 符合 WCAG 标准

## 适用场景

- 📊 中后台管理系统
- 🏢 企业内部工具
- 💰 金融类产品
- 🛒 电商后台
- 📱 管理控制台

## 组件示例 HTML 结构

```html
<!-- 按钮组 -->
<div class="ant-btn-group">
  <button class="ant-btn ant-btn-primary">主要</button>
  <button class="ant-btn ant-btn-default">默认</button>
  <button class="ant-btn ant-btn-danger">危险</button>
</div>

<!-- 输入框 -->
<input class="ant-input" type="text" placeholder="请输入">
<input class="ant-input ant-input-search" type="search" placeholder="搜索">

<!-- 表单 -->
<div class="ant-form">
  <div class="ant-form-item">
    <label class="ant-label">用户名</label>
    <input class="ant-input" type="text">
  </div>
</div>

<!-- 卡片 -->
<div class="ant-card">
  <div class="ant-card-head">标题</div>
  <div class="ant-card-body">内容</div>
</div>

<!-- 表格 -->
<table class="ant-table">
  <thead class="ant-table-thead">
    <tr><th>列1</th><th>列2</th></tr>
  </thead>
  <tbody class="ant-table-tbody">
    <tr><td>数据1</td><td>数据2</td></tr>
  </tbody>
</table>
```
