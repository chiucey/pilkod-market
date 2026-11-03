# Element Plus Design System

饿了么 Element Plus Vue 3 组件库设计语言。

## 设计理念

Element Plus 追求**一致**、**简洁**、**可控**。开箱即用的企业级 Vue 3 组件库。

## 色彩系统

### 品牌色
- Primary: `#409EFF` (Element 蓝)
- Primary Hover: `#66B1FF`
- Primary Dark: `#337AFA`

### 功能色
- Success: `#67C23A`
- Warning: `#E6A23C`
- Error: `#F56C6C`
- Info: `#909399`

### 中性色

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F5F7FA`
- Text Primary: `#303133`
- Text Secondary: `#606266`
- Text Tertiary: `#909399`
- Border: `#DCDFE6`
- Border Light: `#E4E7ED`

#### 深色模式
- Background Dark: `#1D1e1e`
- Background Dark Secondary: `#262727`
- Text Dark Primary: `#E5EAF3`
- Text Dark Secondary: `#CFD3DC`
- Border Dark: `#4A4A4D`

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
- H1: 28px
- H2: 24px
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

- xs: 2px
- sm: 4px
- md: 6px
- lg: 8px
- xl: 12px
- full: 9999px

## 组件样式

### Button

**Primary**
- Background: `#409EFF`
- Color: `#FFFFFF`
- Border Radius: 4px
- Height: 32px
- Padding: 0 20px

**Small**
- Height: 28px
- Padding: 0 15px
- Font Size: 12px

### Input

- Background: `#FFFFFF`
- Border: 1px solid `#DCDFE6`
- Border Radius: 4px
- Height: 32px
- Focus Border: `#409EFF`

### Table

- Header Background: `#F5F7FA`
- Header Color: `#606266`
- Row Border: `#EBEEF5`
- Row Hover: `#F5F7FA`

### Dialog

- Background: `#FFFFFF`
- Border Radius: 8px
- Padding: 24px
- Header Border Bottom: 1px solid `#EBEEF5`

### Select

- Option Height: 34px
- Dropdown Border: 1px solid `#E4E7ED`
- Dropdown Shadow: `0 2px 12px rgba(0, 0, 0, 0.1)`

## 设计注意事项

1. **Vue 3** - 基于最新 Vue 3 Composition API
2. **企业级** - 适合中后台系统
3. **主题定制** - CSS 变量覆盖
4. **无障碍** - 符合 WCAG 标准

## 适用场景

- 🏢 企业后台
- 📊 管理后台
- 💼 管理系统
- 📱 响应式后台

## 组件示例 HTML 结构

```html
<button class="el-button el-button-primary">主要</button>
<button class="el-button el-button-default">默认</button>
<button class="el-button el-button-small">小型</button>
<input class="el-input" type="text" placeholder="输入">
<table class="el-table">
  <thead class="el-table-thead">
    <tr><th>列1</th><th>列2</th></tr>
  </thead>
  <tbody class="el-table-tbody">
    <tr><td>数据1</td><td>数据2</td></tr>
  </tbody>
</table>
<div class="el-dialog">
  <div class="el-dialog-header">标题</div>
  <div class="el-dialog-body">内容</div>
</div>
```
