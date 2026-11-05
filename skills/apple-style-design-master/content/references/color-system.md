# 完整色彩系统指南

## Apple官方色彩系统

### 基础色板

```css
:root {
  /* 黑色系 */
  --black: #000000;
  --gray-900: #1d1d1f;
  --gray-800: #2d2d2f;
  --gray-700: #424245;
  --gray-600: #636366;
  --gray-500: #86868b;
  --gray-400: #a1a1a6;
  --gray-300: #c7c7cc;
  --gray-200: #d2d2d7;
  --gray-100: #e5e5ea;
  --gray-50: #f5f5f7;

  /* 白色系 */
  --white: #ffffff;

  /* 强调色 */
  --blue: #0071e3;
  --blue-dark: #0077ed;
  --blue-light: #2997ff;

  /* 功能色 */
  --green: #34c759;
  --orange: #ff9500;
  --red: #ff3b30;
  --pink: #ff2d55;
  --purple: #af52de;
  --yellow: #ffcc00;
  --teal: #5ac8fa;
}
```

## 语义化色彩命名

### 主色调应用
```css
.text-primary { color: var(--gray-900); }
.text-secondary { color: var(--gray-500); }
.text-link { color: var(--blue); }

.bg-primary { background-color: var(--white); }
.bg-secondary { background-color: var(--gray-50); }
.bg-dark { background-color: var(--gray-900); }
```

### 交互状态色
```css
/* 默认状态 */
.btn-primary {
  background: var(--blue);
  color: var(--white);
}

/* 悬浮状态 */
.btn-primary:hover {
  background: var(--blue-dark);
}

/* 按下状态 */
.btn-primary:active {
  background: var(--blue);
  transform: scale(0.98);
}

/* 禁用状态 */
.btn-primary:disabled {
  background: var(--gray-300);
  cursor: not-allowed;
}
```

## 渐变系统

### 背景渐变
```css
/* 微妙渐变 - 主要使用 */
.gradient-subtle {
  background: linear-gradient(
    180deg,
    var(--white) 0%,
    var(--gray-50) 100%
  );
}

/* 品牌渐变 */
.gradient-brand {
  background: linear-gradient(
    135deg,
    var(--gray-900) 0%,
    var(--gray-700) 100%
  );
}

/* 暗色渐变 */
.gradient-dark {
  background: linear-gradient(
    180deg,
    var(--gray-900) 0%,
    var(--black) 100%
  );
}
```

## 透明度系统

```css
.overlay-light { background: rgba(0, 0, 0, 0.05); }
.overlay-medium { background: rgba(0, 0, 0, 0.1); }
.overlay-dark { background: rgba(0, 0, 0, 0.5); }
.overlay-darker { background: rgba(0, 0, 0, 0.8); }

.text-opacity-50 { color: rgba(0, 0, 0, 0.5); }
.text-opacity-30 { color: rgba(0, 0, 0, 0.3); }
```

## 阴影与层次

```css
.shadow-sm {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.shadow-base {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.shadow-md {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.shadow-lg {
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.shadow-xl {
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}
```

## 边框系统

```css
.border-light { border: 1px solid var(--gray-100); }
.border-base { border: 1px solid var(--gray-200); }
.border-dark { border: 1px solid var(--gray-300); }

.border-focus {
  border-color: var(--blue);
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.2);
}
```

## 色彩使用原则

1. **克制**：限制页面中使用的颜色数量
2. **一致**：相同类型元素使用相同颜色
3. **对比**：确保文字与背景有足够对比度
4. **情感**：颜色传达情感，但不过度
5. **可访问性**：满足 WCAG 对比度要求

## 无障碍色彩检查

```css
/* 确保文字可读 */
.text-primary {
  color: var(--gray-900); /* 对比度 > 4.5:1 */
}
.text-secondary {
  color: var(--gray-500); /* 对比度 > 3:1 (大文本) */
}
```
