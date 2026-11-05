# Notion Design System

Notion 代表知识管理的艺术和灵活的块编辑美学。

## 设计理念

Notion 追求**优雅**、**灵活**、**专注**。像白纸一样自由，又像工具一样强大。

## 色彩系统

### 主色
- Primary: `#000000` (Notion 黑)
- Primary Hover: `#37352F`

### 背景色

#### 浅色模式
- Background: `#FFFFFF`
- Background Gray: `#F7F6F3`
- Background Brown: `#F5F3EF`
- Background Orange: `#FAEBDD`
- Background Yellow: `#FBF3DB`
- Background Green: `#E8F5E9`
- Background Blue: `#E7F3FD`
- Background Purple: `#F3F0F9`
- Background Pink: `#FDF2F2`
- Background Red: `#FFE7E7`

#### 深色模式
- Background Dark: `#191919`
- Background Dark Gray: `#202020`
- Background Dark Brown: `#2A211D`
- Background Dark Orange: `#2D2015`
- Background Dark Yellow: `#28220F`
- Background Dark Green: `#1A2917`
- Background Dark Blue: `#1A2430`
- Background Dark Purple: `#261E2E`
- Background Dark Pink: `#2D1F20`
- Background Dark Red: `#2A1414`

### 文字色

#### 浅色模式
- Text: `#37352F`
- Text Secondary: `#787774`
- Text Tertiary: `#9B9A97`
- Text Disabled: `#D6D4D0`

#### 深色模式
- Text Dark: `#EBEBEB`
- Text Dark Secondary: `#9B9B9B`
- Text Dark Tertiary: `#6B6B6B`

### 边框色

- Border: `#E9E9E7`
- Border Dark: `#373737`
- Border Light: `#F7F7F5`

### 语义色

| 用途 | 颜色 |
|------|------|
| Red | `#EB5757` |
| Orange | `#FA8E16` |
| Yellow | `#FBAB10` |
| Green | `#21A366` |
| Blue | `#2B7CF4` |
| Purple | `#8854D4` |
| Pink | `#E3509D` |
| Brown | `#9F714D` |
| Gray | `#9B9A97` |

## 字体

### 字体栈
```
ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji'
```

### 等宽字体
```
ui-monospace, 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace
```

### 中文、日文、韩文字体
```
'Noto Sans CJK SC', 'Noto Sans CJK TC', 'Noto Sans CJK JP', sans-serif
```

### 字号 (块编辑)

- Page Title: 40px / 700
- Header: 30px / 600
- Subheader: 24px / 600
- Subheader 2: 20px / 600
- Body: 16px / 400
- Small: 14px / 400
- Caption: 12px / 400

### 行高
- Page Title: 1.1
- Header: 1.3
- Body: 1.5

## 间距系统

基于 5px 网格：
- 1: 4px
- 2: 8px
- 3: 12px
- 4: 16px
- 5: 20px
- 6: 24px
- 8: 32px
- 10: 40px

## 圆角

- none: 0
- sm: 3px
- md: 5px
- lg: 8px
- full: 9999px

## 阴影

### 块悬停
```css
box-shadow: -3px 0 0 0 #2383E2;
```

### 拖拽阴影
```css
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
```

### 模态框
```css
box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
```

## 组件样式

### 按钮

**主要按钮**
- Background: `#2383E2`
- Color: `#FFFFFF`
- Border Radius: 5px
- Padding: 4px 12px
- Font Size: 14px

**次要按钮**
- Background: transparent
- Color: `#37352F`
- Border: 1px solid `#E9E9E7`
- Border Radius: 5px

**幽灵按钮**
- Background: transparent
- Color: `#787774`
- Hover Background: `#F7F6F3`

### 输入框

- Border: 1px solid transparent
- Border Radius: 3px
- Padding: 4px 8px
- Focus Border: `#2383E2`

### 页面容器

- Max Width: 900px
- Padding: 80px 96px
- Margin: 0 auto

### 侧边栏

- Width: 240px
- Background: `#F7F6F3`
- Border Right: 1px solid `#E9E9E7`

### 工作区

- Background: `#FFFFFF`
- Border Right: 1px solid `#E9E9E7`
- Width: 240px

### 块 (Block)

- Padding Left: 24px
- Position: relative
- Margin Bottom: 2px

### 模态框

- Background: `#FFFFFF`
- Border Radius: 8px
- Padding: 24px
- Max Width: 640px

## 块类型样式

### 文本块
```css
.block {
  font-size: 16px;
  line-height: 1.5;
  color: #37352F;
}
```

### 待办事项
```css
.checkbox {
  width: 16px;
  height: 16px;
  border: 2px solid #C4C4C4;
  border-radius: 3px;
}
```

### 折叠列表
```css
.toggle {
  width: 20px;
  height: 20px;
  border: 2px solid #C4C4C4;
  border-radius: 3px;
}
```

### 提及 (Mention)
```css
.mention {
  background: #E7F3FD;
  color: #2B7CF4;
  border-radius: 3px;
  padding: 0 4px;
}
```

### 内联代码
```css
.inline-code {
  background: #F7F6F3;
  color: #EB5757;
  font-family: ui-monospace;
  font-size: 0.9em;
  border-radius: 3px;
  padding: 2px 4px;
}
```

## 设计注意事项

1. **白纸隐喻** - 页面即白纸
2. **块编辑** - 每个元素都是块
3. **空格节奏** - 充足的留白
4. **柔和色彩** - 低饱和度色调
5. **可嵌套** - 层级结构
6. **键盘优先** - 斜杠命令

## 适用场景

- 📝 笔记应用
- 📋 项目管理
- 📚 知识库
- 🏢 企业 wiki
- ⚡ 灵活文档

## 组件示例 HTML 结构

```html
<!-- 页面容器 -->
<div class="notion-page">
  <h1 class="notion-title">页面标题</h1>
  <div class="notion-block">文本内容</div>
</div>

<!-- 侧边栏 -->
<aside class="notion-sidebar">
  <div class="notion-workspace">工作区</div>
  <div class="notion-nav-item">页面1</div>
  <div class="notion-nav-item">页面2</div>
</aside>

<!-- 块 -->
<div class="notion-block notion-text">文本块</div>
<div class="notion-block notion-heading">标题</div>
<div class="notion-block notion-todo">
  <input type="checkbox">
  <span>待办事项</span>
</div>

<!-- 代码块 -->
<pre class="notion-code">代码</pre>

<!-- 列表 -->
<div class="notion-block notion-bulleted-list">• 列表项</div>
```
