# Blank Design Template

空白设计模板，你可以基于此创建自定义设计系统。

## 设计理念

自定义设计系统的起点。根据你的品牌需求填充以下内容。

## 品牌色

```css
:root {
  /* 主色 */
  --color-primary: #000000;
  --color-primary-hover: #333333;
  --color-primary-active: #666666;

  /* 辅助色 */
  --color-success: #00C853;
  --color-warning: #FFB300;
  --color-error: #D50000;
  --color-info: #2196F3;

  /* 背景色 */
  --color-bg: #FFFFFF;
  --color-bg-secondary: #F5F5F5;
  --color-bg-dark: #121212;

  /* 文字色 */
  --color-text-primary: #000000;
  --color-text-secondary: #666666;
  --color-text-tertiary: #999999;
  --color-text-disabled: #CCCCCC;

  /* 边框色 */
  --color-border: #E0E0E0;
  --color-border-hover: #BDBDBD;
}
```

## 字体

```css
:root {
  /* 字体栈 */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;

  /* 字号 */
  --font-size-display: 48px;
  --font-size-h1: 32px;
  --font-size-h2: 24px;
  --font-size-h3: 20px;
  --font-size-h4: 16px;
  --font-size-body: 14px;
  --font-size-small: 12px;
  --font-size-micro: 11px;

  /* 字重 */
  --font-weight-light: 300;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* 行高 */
  --line-height-tight: 1.2;
  --line-height-normal: 1.5;
  --line-height-loose: 1.75;
}
```

## 间距

```css
:root {
  /* 基于 4px 或 8px 网格 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
  --spacing-3xl: 64px;
  --spacing-4xl: 96px;
}
```

## 圆角

```css
:root {
  --radius-xs: 2px;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;
  --radius-full: 9999px;
}
```

## 阴影

```css
:root {
  /* 无阴影 */
  --shadow-none: none;

  /* 轻阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);

  /* 中阴影 */
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);

  /* 重阴影 */
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* 特大阴影 */
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
}
```

## 动效

```css
:root {
  /* 时长 */
  --duration-fast: 100ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --duration-slower: 500ms;

  /* 缓动函数 */
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

## 组件模板

### 按钮

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--color-primary-hover);
}

.btn-secondary {
  background-color: transparent;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}
```

### 输入框

```css
.input {
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background-color: var(--color-bg);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
}
```

### 卡片

```css
.card {
  background-color: var(--color-bg);
  border-radius: 12px;
  padding: 24px;
  box-shadow: var(--shadow-md);
}
```

### 导航栏

```css
.navbar {
  display: flex;
  align-items: center;
  height: 64px;
  padding: 0 24px;
  background-color: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
}
```

## 使用指南

1. **定义品牌色** - 选择主色和辅助色
2. **选择字体** - 确定字体栈和字号
3. **建立网格** - 定义间距和圆角
4. **设计组件** - 按钮、表单、卡片等
5. **定义模式** - 亮色/暗色模式

## 示例 HTML 结构

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    :root {
      --color-primary: #000000;
      --color-primary-hover: #333333;
      --spacing-md: 16px;
      --spacing-lg: 24px;
      --radius-md: 8px;
      --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: #FAFAFA;
      color: #000000;
      margin: 0;
      padding: 24px;
    }

    .btn {
      padding: 12px 24px;
      border-radius: 8px;
      font-weight: 500;
      cursor: pointer;
      border: none;
    }

    .btn-primary {
      background-color: var(--color-primary);
      color: white;
    }

    .card {
      background: white;
      border-radius: 12px;
      padding: 24px;
      box-shadow: var(--shadow-md);
    }

    .input {
      padding: 12px 16px;
      border: 1px solid #E0E0E0;
      border-radius: 8px;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <button class="btn btn-primary">主要按钮</button>

  <div class="card">
    <h2>卡片标题</h2>
    <p>卡片内容</p>
  </div>

  <input class="input" type="text" placeholder="输入框">
</body>
</html>
```
