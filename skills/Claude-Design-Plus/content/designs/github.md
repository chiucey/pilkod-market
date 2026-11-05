# GitHub Design System

GitHub 的设计系统，代表开发者友好的设计风格。

## 设计理念

GitHub 设计追求**功能清晰**、**易于理解**、**高效协作**。

## 色彩系统

### 主色
- Primary: `#238636` (GitHub 绿)
- Primary Hover: `#2EA043`

### 深色
- Canvas Default: `#0D1117`
- Canvas Subtle: `#161B22`
- Canvas Insset: `#010409`

### 边框
- Border Default: `#30363D`
- Border Muted: `#21262D`

### 文字
- Text Primary: `#C9D1D9`
- Text Secondary: `#8B949E`
- Text Tertiary: `#6E7681`
- Text Disabled: `#484F58`

### 功能色
- Success: `#238636`
- Success Emphasis: `#2EA043`
- Warning: `#D29922`
- Warning Emphasis: `#E3B341`
- Danger: `#DA3633`
- Danger Emphasis: `#FF7B72`
- Accent: `#58A6FF`
- Accent Emphasis: `#79C0FF`

### 蓝色系
- Done: `#8957E5`
- Done Emphasis: `#A371F7`

### 饱和色
- Sponsors: `#DB61A2`
- sponsors Emphasis: `#F778BA`

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji'
```

### 字号
- Display: 48px
- H1: 32px
- H2: 24px
- H3: 20px
- H4: 16px
- Body: 14px
- Small: 12px
- Micro: 11px

### 字重
- Light: 300
- Normal: 400
- Semibold: 600
- Bold: 700

## 间距系统

基于 8px 网格：
- 1: 4px
- 2: 8px
- 3: 12px
- 4: 16px
- 5: 24px
- 6: 32px
- 7: 40px
- 8: 48px

## 圆角

- xs: 4px
- sm: 6px
- md: 8px
- lg: 12px
- xl: 16px
- full: 9999px

## 阴影

### 按钮悬停
```css
box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
```

### 下拉菜单
```css
box-shadow: 0 8px 24px rgba(1, 4, 9, 0.45);
```

## 组件样式

### 按钮

**主要按钮**
- Background: `#238636`
- Color: `#FFFFFF`
- Border: 1px solid `#238636`
- Border Radius: 6px
- Padding: 5px 16px
- Font Size: 14px
- Font Weight: 500

**次要按钮**
- Background: `#21262D`
- Color: `#C9D1D9`
- Border: 1px solid `#30363D`

**-outline 按钮**
- Background: transparent
- Color: `#58A6FF`
- Border: 1px solid `#58A6FF`

**危险按钮**
- Background: `#DA3633`
- Hover: `#FF7B72`

### 输入框

- Background: `#0D1117`
- Border: 1px solid `#30363D`
- Border Radius: 6px
- Padding: 5px 12px
- Font Size: 14px
- Focus Border: `#58A6FF`

### 卡片

- Background: `#161B22`
- Border: 1px solid `#30363D`
- Border Radius: 6px
- Padding: 16px

### 标签/徽章

- Border Radius: 9999px (full)
- Padding: 0 7px
- Font Size: 12px
- Font Weight: 500

### 分隔线

- Border Top: 1px solid `#30363D`

### 头像

- Border Radius: 50%
- Sizes: 24px / 32px / 40px / 48px / 64px / 80px / 96px

## 代码块

### 代码字体
```
'ui-monospace', 'SFMono-Regular', 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace
```

### 代码块背景
- Default: `#0D1117`
- Emphasis: `#161B22`

## Markdown 样式

### 标题
- H1: 32px, border-bottom 1px `#30363D`
- H2: 24px, border-bottom 1px `#30363D`
- H3: 20px

### 链接
- Default: `#58A6FF`
- Hover: `#79C0FF`
- Visited: `#A371F7`

### 列表
- ul: 左侧 padding 24px, list-style disc
- li: margin 4px 0

## 设计注意事项

1. **开发者优先** - 代码展示清晰
2. **暗色主题** - 默认深色模式
3. **功能清晰** - 操作明确
4. **信息密度** - 高效利用空间
5. **键盘友好** - 支持快捷键

## 适用场景

- 🏢 开发者工具
- 📝 文档网站
- 💻 代码展示
- 🤝 协作平台
- 📦 包管理界面

## 组件示例 HTML 结构

```html
<!-- 按钮 -->
<button class="gh-btn gh-btn-primary">主要</button>
<button class="gh-btn gh-btn-secondary">次要</button>
<button class="gh-btn gh-btn-outline">轮廓</button>
<button class="gh-btn gh-btn-danger">危险</button>

<!-- 输入框 -->
<input class="gh-input" type="text" placeholder="输入">

<!-- 卡片 -->
<div class="gh-card">
  <div class="gh-card-header">标题</div>
  <div class="gh-card-body">内容</div>
</div>

<!-- 标签 -->
<span class="gh-badge gh-badge-success">成功</span>
<span class="gh-badge gh-badge-danger">危险</span>

<!-- 代码块 -->
<pre class="gh-code-block"><code>代码</code></pre>
```
