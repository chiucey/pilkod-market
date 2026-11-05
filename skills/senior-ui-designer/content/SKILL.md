---
name: senior-ui-designer
description: 专业 UI/UX 设计师技能，专注于设计系统构建、原子化组件设计、设计规范输出。当用户要求设计界面、创建设计系统、定义 UI 规范、输出组件状态、设计暗色/亮色模式、生成 Figma 规范、设计科技感界面时使用此技能。
---

# Senior UI Designer

专业 UI/UX 设计师，具备完整的设计系统构建能力和前端协作输出能力。

## 设计理念

- **原子化设计思维**：从最小单元出发，逐层构建复杂界面
- **现代科技感**：注重留白、呼吸感、清晰的视觉层级
- **开发友好**：输出可直接对接 Tailwind CSS / CSS 变量

---

## 设计系统构建

### 颜色系统

当需要定义颜色系统时，输出以下格式：

```markdown
## 色彩规范

### 主色调 (Primary Colors)
| 名称 | 色值 | 用途 |
|------|------|------|
| Primary-500 | #3B82F6 | 主要交互元素 |
| Primary-600 | #2563EB | 悬停状态 |
| Primary-400 | #60A5FA | 浅色变体 |

### 中性色 (Neutral Colors)
| 名称 | 色值 | 用途 |
|------|------|------|
| Gray-900 | #111827 | 主文本 |
| Gray-600 | #4B5563 | 次要文本 |
| Gray-200 | #E5E7EB | 边框 |
| Gray-50 | #F9FAFB | 背景 |

### 语义色 (Semantic Colors)
| 名称 | 色值 | 用途 |
|------|------|------|
| Success-500 | #10B981 | 成功状态 |
| Warning-500 | #F59E0B | 警告状态 |
| Error-500 | #EF4444 | 错误状态 |
| Info-500 | #3B82F6 | 信息提示 |
```

### Tailwind CSS 颜色配置
```javascript
// tailwind.config.js
colors: {
  primary: {
    50: '#EFF6FF',
    100: '#DBEAFE',
    500: '#3B82F6',
    600: '#2563EB',
    700: '#1D4ED8',
  }
}
```

### CSS 变量版本
```css
:root {
  --color-primary-500: #3B82F6;
  --color-primary-600: #2563EB;
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-error: #EF4444;
}
```

---

### 字体排版系统 (Typography Scale)

```markdown
## 字体规范

### 字体族
- 主字体：`Inter, -apple-system, BlinkMacSystemFont, sans-serif`
- 等宽字体：`JetBrains Mono, Fira Code, monospace`

### 字号层级 (Type Scale)
| 名称 | 字号 | 行高 | 用途 | Tailwind |
|------|------|------|------|----------|
| text-xs | 12px | 16px | 辅助说明 | `text-xs` |
| text-sm | 14px | 20px | 次要文本 | `text-sm` |
| text-base | 16px | 24px | 正文 | `text-base` |
| text-lg | 18px | 28px | 强调正文 | `text-lg` |
| text-xl | 20px | 28px | 小标题 | `text-xl` |
| text-2xl | 24px | 32px | 标题 | `text-2xl` |
| text-3xl | 30px | 36px | 大标题 | `text-3xl` |
| text-4xl | 36px | 40px | Hero | `text-4xl` |

### 字重系统
| 名称 | 字重 | 用途 | Tailwind |
|------|------|------|----------|
| Regular | 400 | 正文 | `font-normal` |
| Medium | 500 | 强调 | `font-medium` |
| Semibold | 600 | 按钮 | `font-semibold` |
| Bold | 700 | 标题 | `font-bold` |
```

---

### 阴影层级 (Shadow System)

```markdown
## 阴影规范

| 名称 | CSS 值 | 用途 | Tailwind |
|------|--------|------|----------|
| shadow-sm | 0 1px 2px rgba(0,0,0,0.05) | 卡片悬停 | `shadow-sm` |
| shadow-md | 0 4px 6px rgba(0,0,0,0.1) | 弹出框 | `shadow-md` |
| shadow-lg | 0 10px 15px rgba(0,0,0,0.1) | 模态框 | `shadow-lg` |
| shadow-xl | 0 20px 25px rgba(0,0,0,0.15) | 高亮强调 | `shadow-xl` |
| shadow-glow | 0 0 20px rgba(59,130,246,0.3) | 发光效果 | 自定义 |

### 暗色模式阴影
```css
.dark {
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.4);
}
```

### CSS 变量版本
```css
:root {
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
  --shadow-xl: 0 20px 25px rgba(0,0,0,0.15);
}
```

---

### 间距系统 (Spacing Scale)

```markdown
## 间距规范

基于 4px 网格系统：

| 名称 | 值 | Tailwind | 用途 |
|------|-----|----------|------|
| 1 | 4px | `space-1` | 紧凑间距 |
| 2 | 8px | `space-2` | 元素内间距 |
| 3 | 12px | `space-3` | 小间距 |
| 4 | 16px | `space-4` | 标准间距 |
| 5 | 20px | `space-5` | 中等间距 |
| 6 | 24px | `space-6` | 区块内间距 |
| 8 | 32px | `space-8` | 区块间间距 |
| 10 | 40px | `space-10` | 大间距 |
| 12 | 48px | `space-12` | 区域间距 |
| 16 | 64px | `space-16` | 页面级间距 |
```

---

### 圆角系统 (Border Radius)

```markdown
## 圆角规范

| 名称 | 值 | Tailwind | 用途 |
|------|-----|----------|------|
| rounded-none | 0 | `rounded-none` | 无圆角 |
| rounded-sm | 2px | `rounded-sm` | 小元素 |
| rounded | 4px | `rounded` | 默认按钮 |
| rounded-md | 6px | `rounded-md` | 输入框 |
| rounded-lg | 8px | `rounded-lg` | 卡片 |
| rounded-xl | 12px | `rounded-xl` | 大卡片 |
| rounded-2xl | 16px | `rounded-2xl` | 模态框 |
| rounded-full | 9999px | `rounded-full` | 头像/标签 |
```

---

### 图标库规划

```markdown
## 图标规范

### 推荐图标库
- **Heroicons** (优先) - 与 Tailwind 配套
- **Lucide** - 简洁现代风格
- **Phosphor Icons** - 多变体支持

### 图标尺寸
| 名称 | 尺寸 | Tailwind | 用途 |
|------|------|----------|------|
| icon-xs | 16x16 | `h-4 w-4` | 内联文本 |
| icon-sm | 20x20 | `h-5 w-5` | 小按钮 |
| icon-md | 24x24 | `h-6 w-6` | 默认大小 |
| icon-lg | 32x32 | `h-8 w-8` | 大图标 |
| icon-xl | 48x48 | `h-12 w-12` | 装饰图标 |

### 图标使用原则
- 线条粗细统一 (stroke-width: 1.5 或 2)
- 与文字对齐使用 `inline-flex`
- 颜色继承自父元素 `currentColor`
```

---

## 组件化设计

### 原子组件设计原则

每个组件必须定义以下状态：

```markdown
## 组件状态定义

### 通用状态
- **Default** - 默认状态
- **Hover** - 悬停状态
- **Active** - 点击/激活状态
- **Focus** - 聚焦状态
- **Disabled** - 禁用状态
- **Loading** - 加载状态
- **Error** - 错误状态
```

### 按钮组件规范

```markdown
## 按钮组件 (Button)

### 尺寸变体
| 变体 | 高度 | 内边距 | 字号 | Tailwind |
|------|------|--------|------|----------|
| sm | 32px | px-3 py-1.5 | text-sm | `btn-sm` |
| md | 40px | px-4 py-2 | text-base | `btn-md` |
| lg | 48px | px-6 py-3 | text-lg | `btn-lg` |

### 类型变体
| 类型 | 背景色 | 文字色 | 边框 | Tailwind |
|------|--------|--------|------|----------|
| Primary | primary-600 | white | none | `bg-primary-600 text-white` |
| Secondary | gray-100 | gray-700 | none | `bg-gray-100 text-gray-700` |
| Outline | transparent | primary-600 | primary-600 | `border border-primary-600` |
| Ghost | transparent | gray-600 | none | `hover:bg-gray-100` |
| Danger | error-500 | white | none | `bg-error-500 text-white` |

### 状态规范
| 状态 | 效果 | Tailwind |
|------|------|----------|
| Default | 正常显示 | `bg-primary-600` |
| Hover | 背景加深 10% | `hover:bg-primary-700` |
| Active | 背景加深 15%，轻微下沉 | `active:bg-primary-800 active:translate-y-0.5` |
| Focus | 外发光 + ring | `focus:ring-2 focus:ring-primary-300` |
| Disabled | 50% 透明度，禁用指针 | `disabled:opacity-50 disabled:cursor-not-allowed` |
| Loading | 显示旋转图标 | `cursor-wait` |
```

### 输入框组件规范

```markdown
## 输入框组件 (Input)

### 尺寸
| 尺寸 | 高度 | 内边距 | 字号 | Tailwind |
|------|------|--------|------|----------|
| sm | 32px | px-3 | text-sm | `h-8` |
| md | 40px | px-4 | text-base | `h-10` |
| lg | 48px | px-5 | text-lg | `h-12` |

### 状态
| 状态 | 边框色 | 背景色 | Tailwind |
|------|--------|--------|----------|
| Default | gray-300 | white | `border-gray-300 bg-white` |
| Hover | gray-400 | white | `hover:border-gray-400` |
| Focus | primary-500 | white | `focus:border-primary-500 focus:ring-2` |
| Error | error-500 | error-50 | `border-error-500 bg-error-50` |
| Disabled | gray-200 | gray-100 | `border-gray-200 bg-gray-100 disabled:cursor-not-allowed` |
```

### 卡片组件规范

```markdown
## 卡片组件 (Card)

### 基础卡片
| 属性 | 值 | Tailwind |
|------|-----|----------|
| 背景色 | white | `bg-white` |
| 边框 | 1px gray-200 | `border border-gray-200` |
| 圆角 | lg | `rounded-lg` |
| 阴影 | sm | `shadow-sm` |
| 内边距 | 16px | `p-4` (md: p-6) |

### 卡片悬停效果
| 状态 | 效果 | Tailwind |
|------|------|----------|
| Default | 基础阴影 | `shadow-sm` |
| Hover | 阴影加深 + 轻微上移 | `hover:shadow-md hover:-translate-y-1` |
```

---

## 设计风格输出

### 暗色模式 (Dark Mode) - 优先方案

当用户未指定风格时，默认提供暗色模式设计：

```markdown
## 暗色模式配色

### 背景层级
| 层级 | 色值 | 用途 |
|------|------|------|
| Base | #0F172A (slate-900) | 主背景 |
| Elevated | #1E293B (slate-800) | 卡片背景 |
| Surface | #334155 (slate-700) | 次级表面 |
| Overlay | #475569 (slate-600) | 浮层 |

### 文字层级
| 层级 | 色值 | 用途 |
|------|------|------|
| Primary | #F8FAFC (slate-50) | 主要文本 |
| Secondary | #94A3B8 (slate-400) | 次要文本 |
| Muted | #64748B (slate-500) | 辅助文本 |

### 暗色模式 Tailwind 配置
```javascript
// tailwind.config.js
darkMode: 'class',
colors: {
  dark: {
    base: '#0F172A',
    elevated: '#1E293B',
    surface: '#334155',
    overlay: '#475569',
    border: '#334155',
  }
}
```

### 暗色模式 CSS 变量
```css
.dark {
  --bg-base: #0F172A;
  --bg-elevated: #1E293B;
  --bg-surface: #334155;
  --text-primary: #F8FAFC;
  --text-secondary: #94A3B8;
  --border-color: #334155;
}
```

---

### 极简主义风格

```markdown
## 极简主义设计原则

### 视觉特点
- 大量留白 (whitespace)
- 有限色彩 (< 3 种主色)
- 纤细边框 (1px)
- 微妙阴影
- 无装饰性元素

### 极简排版
- 正文: 16-18px, font-weight: 400
- 标题: 24-48px, font-weight: 600-700
- 字间距: 正常 (-0.01em)
- 行高: 1.5-1.75

### 极简配色
- 主色: 纯黑 #000000 或 品牌色
- 背景: 纯白 #FFFFFF 或 浅灰 #F5F5F5
- 强调: 单一亮色
```

---

### 现代科技感设计

```markdown
## 现代科技感设计特点

### 视觉特征
- 深色背景 + 渐变光效
- 毛玻璃效果 (glassmorphism)
- 微妙的发光边框
- 几何图形装饰
- 动态微交互

### 玻璃态效果
```css
.glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### 渐变光效
```css
.gradient-border {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1px;
}
.gradient-border::before {
  content: '';
  position: absolute;
  inset: 1px;
  background: #0F172A;
  border-radius: inherit;
}
```

### 科技感阴影
```css
.glow-blue {
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3),
              0 0 40px rgba(59, 130, 246, 0.1);
}
```

---

## 输出格式规范

### 设计规范文档结构

每次设计输出应包含：

```markdown
# [页面/组件名称] 设计规范

## 1. 设计概述
- 设计风格
- 核心原则
- 目标用户/场景

## 2. 视觉规范
### 2.1 颜色系统
[颜色表格]
### 2.2 字体规范
[字体表格]
### 2.3 间距与圆角
[间距表格]

## 3. 组件规范
### [组件名称]
| 状态 | 样式描述 |
|------|----------|
| Default | ... |
| Hover | ... |

## 4. 布局规范
- 网格系统
- 响应式断点
- 容器宽度

## 5. Tailwind CSS 配置
```javascript
// 相关配置代码
```

## 6. CSS 变量版本
```css
/* 相关变量 */
```
```

---

## HTML/CSS 设计图输出

当需要输出可运行的设计图时：

### HTML 结构规范

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>设计标题</title>
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Inter 字体 -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    /* 自定义 CSS 变量 */
    :root {
      --color-primary: #3B82F6;
    }
    body {
      font-family: 'Inter', sans-serif;
    }
  </style>
</head>
<body class="bg-gray-900 text-white">
  <!-- 设计内容 -->
</body>
</html>
```

### 暗色模式设计图模板

```html
<!DOCTYPE html>
<html lang="zh-CN" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>暗色模式设计</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            primary: {
              400: '#60A5FA',
              500: '#3B82F6',
              600: '#2563EB',
            }
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: 'Inter', sans-serif; }
    /* 玻璃态效果 */
    .glass {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    /* 发光效果 */
    .glow {
      box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
    }
  </style>
</head>
<body class="bg-slate-900 min-h-screen">
  <!-- 设计内容 -->
</body>
</html>
```

---

## Figma 协作输出

### Figma 风格规范说明

当用户提到 Figma 时，提供以下对应关系：

```markdown
## Figma 规范对照

| Figma 属性 | Tailwind CSS | CSS 变量 |
|------------|--------------|----------|
| Fill: #3B82F6 | `bg-[#3B82F6]` | `--color-primary` |
| Stroke: 1px | `border` | `border-width: 1px` |
| Corner Radius: 8 | `rounded-lg` | `--radius-lg` |
| Font: Inter 16px/24px | `text-base leading-6` | `--text-base` |
| Effect: Shadow/Drop | `shadow-md` | `--shadow-md` |
| Auto Layout: Hug | 根据内容撑开 | - |
| Auto Layout: Fill | 撑满容器 | `w-full` |
| Auto Layout: Fixed | 固定尺寸 | `w-[xxx]px` |
```

---

## 响应式设计规范

### 断点系统

```markdown
## 响应式断点

| 名称 | 宽度 | Tailwind | 用途 |
|------|------|----------|------|
| sm | 640px | `sm:` | 手机横屏 |
| md | 768px | `md:` | 平板 |
| lg | 1024px | `lg:` | 小屏电脑 |
| xl | 1280px | `xl:` | 标准屏幕 |
| 2xl | 1536px | `2xl:` | 大屏屏幕 |

### 容器宽度
| 名称 | 最大宽度 | Tailwind |
|------|----------|----------|
| sm | 640px | `max-w-sm` |
| md | 768px | `max-w-md` |
| lg | 1024px | `max-w-lg` |
| xl | 1280px | `max-w-xl` |
| 2xl | 1536px | `max-w-2xl` |
| full | 100% | `max-w-full` |
```

---

## 交互微交规范

```markdown
## 微交规范

### 过渡时长
| 类型 | 时长 | Tailwind |
|------|------|----------|
| instant | 0ms | - |
| fast | 150ms | `duration-150` |
| normal | 200ms | `duration-200` |
| slow | 300ms | `duration-300` |
| slower | 500ms | `duration-500` |

### 缓动函数
| 类型 | 值 | Tailwind |
|------|-----|----------|
| ease | ease | `ease` |
| in-out | ease-in-out | `ease-in-out` |
| out | ease-out | `ease-out` |
| in | ease-in | `ease-in` |

### 常见交互
```css
/* 悬停缩放 */
.hover-scale {
  transition: transform 200ms ease-out;
}
.hover-scale:hover {
  transform: scale(1.02);
}

/* 颜色过渡 */
.color-transition {
  transition: background-color 150ms ease, color 150ms ease;
}
```
