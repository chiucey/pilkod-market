# Cursor Design System

Cursor 代表 AI 代码编辑器的设计美学。

## 设计理念

Cursor 追求**专注**、**效率**、**智能**。简洁的界面让 AI 成为你的编程伙伴。

## 色彩系统

### 主色
- Primary: `#10A37F` (Cursor 绿)
- Primary Hover: `#149267`

### 背景色

#### 深色模式 (主模式)
- Background: `#0A0A0A`
- Background Secondary: `#141414`
- Background Tertiary: `#1E1E1E`
- Background Elevated: `#252525`

#### 浅色模式
- Background: `#FFFFFF`
- Background Secondary: `#F5F5F5`

### 文字色

#### 深色模式
- Text Primary: `#ECECF1`
- Text Secondary: `#A3A3A3`
- Text Tertiary: `#6B6B6B`
- Text Muted: `#4A4A4A`

#### 浅色模式
- Text Primary: `#1E1E1E`
- Text Secondary: `#6B6B6B`

### 边框色

- Border: `#2E2E2E`
- Border Light: `#E5E5E5`

### 功能色

- Success: `#10A37F`
- Warning: `#F5A623`
- Error: `#E53935`
- Info: `#4285F4`

### AI 色

- AI Blue: `#7B61FF`
- AI Purple: `#9B8AFF`

## 字体

### 字体栈
```
'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
```

### 代码字体
```
'JetBrains Mono', 'Fira Code', 'SF Mono', Monaco, Consolas, monospace
```

### 字号
- Display: 28px
- H1: 22px
- H2: 18px
- H3: 14px
- Body: 14px
- Small: 12px
- Code: 13px

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px
- 2xl: 32px

## 圆角

- sm: 4px
- md: 6px
- lg: 8px
- xl: 12px

## 组件样式

### 按钮

**主要按钮**
- Background: `#10A37F`
- Color: `#FFFFFF`
- Border Radius: 6px
- Height: 32px
- Padding: 0 16px
- Font Size: 14px

**次要按钮**
- Background: `#1E1E1E`
- Color: `#ECECF1`
- Border: 1px solid `#2E2E2E`

**Ghost 按钮**
- Background: transparent
- Color: `#A3A3A3`

### 输入框

- Background: `#1E1E1E`
- Border: 1px solid `#2E2E2E`
- Border Radius: 6px
- Height: 36px
- Padding: 0 12px
- Color: `#ECECF1`
- Focus Border: `#10A37F`

### 终端面板

- Background: `#0A0A0A`
- Border: 1px solid `#2E2E2E`
- Border Radius: 8px
- Padding: 16px
- Font Family: JetBrains Mono

### 代码编辑器

- Background: `#0A0A0A`
- Line Height: 1.6
- Gutter: 48px
- Line Number Color: `#4A4A4A`

## 设计注意事项

1. **深色优先** - 开发者习惯深色模式
2. **代码清晰** - 等宽字体，高对比度
3. **AI 集成** - AI 对话框突出显示
4. **最小干扰** - 界面简洁，专注代码

## 适用场景

- 💻 代码编辑器
- 🤖 AI 编程工具
- 🖥️ 开发者 IDE
- ⚡ 技术文档

## 组件示例 HTML 结构

```html
<button class="cursor-btn cursor-btn-primary">主要</button>
<button class="cursor-btn cursor-btn-secondary">次要</button>
<input class="cursor-input" type="text" placeholder="输入命令">
<pre class="cursor-code">const cursor = true;</pre>
```
