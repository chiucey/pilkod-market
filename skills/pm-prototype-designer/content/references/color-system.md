# 色彩系统参考

## 色彩设计原则

1. **可访问性**：文本与背景的对比度 ≥ 4.5:1（WCAG AA）
2. **一致性**：全产品线使用统一的色彩语义
3. **克制**：主色单一，辅助色精简
4. **情感匹配**：色彩传达正确的产品调性

---

## 主色彩板

### 主色（Primary）

主色是产品最具识别度的色彩，用于主要操作按钮、链接、活跃状态等核心UI元素。

```css
:root {
  /* 靛蓝-紫主色调 */
  --color-primary-50: #eef2ff;
  --color-primary-100: #e0e7ff;
  --color-primary-200: #c7d2fe;
  --color-primary-300: #a5b4fc;
  --color-primary-400: #818cf8;
  --color-primary-500: #6366f1;  /* 主色基准 */
  --color-primary-600: #4f46e5;
  --color-primary-700: #4338ca;
  --color-primary-800: #3730a3;
  --color-primary-900: #312e81;
}
```

**使用场景**
| 色阶 | 用途 | 示例 |
|------|------|------|
| 50-100 | 浅色背景/hover态 | 表格hover行 |
| 200-300 | 边框/分割线 | 输入框边框 |
| 400-500 | 图标/文字 | 活跃状态图标 |
| 500-600 | 按钮背景 | 主要CTA |
| 700-900 | 深色文字 | 深色主题 |

---

### 辅助色（Secondary）

用于次要操作、辅助信息和次要强调。

```css
:root {
  /* 紫罗兰辅助色调 */
  --color-secondary-50: #f5f3ff;
  --color-secondary-100: #ede9fe;
  --color-secondary-200: #ddd6fe;
  --color-secondary-300: #c4b5fd;
  --color-secondary-400: #a78bfa;
  --color-secondary-500: #8b5cf6;  /* 辅助色基准 */
  --color-secondary-600: #7c3aed;
  --color-secondary-700: #6d28d9;
  --color-secondary-800: #5b21b6;
  --color-secondary-900: #4c1d95;
}
```

---

## 功能色彩板

### 成功色（Success）

表示操作成功、状态正常、正向数据。

```css
:root {
  --color-success-50: #ecfdf5;
  --color-success-100: #d1fae5;
  --color-success-200: #a7f3d0;
  --color-success-300: #6ee7b7;
  --color-success-400: #34d399;
  --color-success-500: #10b981;  /* 基准 */
  --color-success-600: #059669;
  --color-success-700: #047857;
  --color-success-800: #065f46;
  --color-success-900: #064e3b;
}
```

**语义**
- ✓ 成功提示
- ✓ 完成状态
- ✓ 正向指标
- ✓ 确认操作

---

### 警告色（Warning）

表示需要注意、待处理、可能的风险。

```css
:root {
  --color-warning-50: #fffbeb;
  --color-warning-100: #fef3c7;
  --color-warning-200: #fde68a;
  --color-warning-300: #fcd34d;
  --color-warning-400: #fbbf24;
  --color-warning-500: #f59e0b;  /* 基准 */
  --color-warning-600: #d97706;
  --color-warning-700: #b45309;
  --color-warning-800: #92400e;
  --color-warning-900: #78350f;
}
```

**语义**
- ⚠ 警告提示
- ⚡ 待处理状态
- 📊 中性指标
- 🔔 提醒通知

---

### 错误色（Error/Danger）

表示错误、失败、危险操作。

```css
:root {
  --color-error-50: #fef2f2;
  --color-error-100: #fee2e2;
  --color-error-200: #fecaca;
  --color-error-300: #fca5a5;
  --color-error-400: #f87171;
  --color-error-500: #ef4444;  /* 基准 */
  --color-error-600: #dc2626;
  --color-error-700: #b91c1c;
  --color-error-800: #991b1b;
  --color-error-900: #7f1d1d;
}
```

**语义**
- ✕ 错误提示
- ✖ 失败状态
- 🔴 危险操作
- ⛔ 禁止状态

---

### 信息色（Info）

表示提示信息、引导操作、进度状态。

```css
:root {
  --color-info-50: #eff6ff;
  --color-info-100: #dbeafe;
  --color-info-200: #bfdbfe;
  --color-info-300: #93c5fd;
  --color-info-400: #60a5fa;
  --color-info-500: #3b82f6;  /* 基准 */
  --color-info-600: #2563eb;
  --color-info-700: #1d4ed8;
  --color-info-800: #1e40af;
  --color-info-900: #1e3a8a;
}
```

**语义**
- ℹ 信息提示
- 📖 引导说明
- 🔵 进度状态
- 🔗 帮助链接

---

## 中性色彩板

用于文字、边框、背景等中性元素。

```css
:root {
  /* 灰色中性色调 */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;  /* 正文文字 */
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;  /* 标题文字 */
  --color-gray-950: #030712;  /* 深色背景 */
}
```

**语义分配**
| 色阶 | 用途 |
|------|------|
| 50 | 页面背景（亮色） |
| 100 | 卡片/容器背景 |
| 200 | 分割线/边框 |
| 300 | 占位符文字 |
| 400 | 辅助文字 |
| 500 | 正文文字 |
| 600-700 | 次要标题 |
| 800-900 | 主要标题/深色背景 |

---

## 语义变量

推荐使用语义化变量而非直接使用颜色值：

```css
:root {
  /* 背景 */
  --bg-primary: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-tertiary: #f3f4f6;
  --bg-inverse: #111827;

  /* 文字 */
  --text-primary: #111827;
  --text-secondary: #4b5563;
  --text-tertiary: #9ca3af;
  --text-inverse: #ffffff;

  /* 边框 */
  --border-default: #e5e7eb;
  --border-strong: #d1d5db;
  --border-focus: #6366f1;

  /* 交互 */
  --interactive-primary: #6366f1;
  --interactive-hover: #4f46e5;
  --interactive-pressed: #4338ca;

  /* 功能 */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;
}
```

---

## 暗色模式

```css
[data-theme="dark"] {
  /* 背景反转 */
  --bg-primary: #111827;
  --bg-secondary: #1f2937;
  --bg-tertiary: #374151;

  /* 文字反转 */
  --text-primary: #f9fafb;
  --text-secondary: #d1d5db;
  --text-tertiary: #9ca3af;

  /* 边框调整 */
  --border-default: #374151;
  --border-strong: #4b5563;

  /* 保持主色不变或轻微调整 */
  --interactive-primary: #818cf8;
  --interactive-hover: #a5b4fc;
}
```

---

## 渐变色

### 主渐变

```css
/* 背景渐变 */
.gradient-primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}

/* 文字渐变 */
.text-gradient {
  background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 阴影渐变 */
.shadow-gradient {
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3);
}
```

### 毛玻璃效果

```css
.glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

[data-theme="dark"] .glass {
  background: rgba(17, 24, 39, 0.8);
}
```

---

## 可访问性对照表

| 对比组合 | 对比率 | WCAG等级 | 适用场景 |
|----------|--------|----------|----------|
| 白色 #fff → 灰色-900 #111827 | 19.5:1 | AAA | 标题/正文 |
| 白色 #fff → 灰色-600 #4b5563 | 7.5:1 | AAA | 正文 |
| 白色 #fff → 灰色-500 #6b7280 | 4.7:1 | AA | 正文（14px+） |
| 灰色-100 #f3f4f6 → 灰色-900 #111827 | 15.1:1 | AAA | 浅色背景文字 |
| 灰色-100 #f3f4f6 → 灰色-700 #374151 | 8.4:1 | AAA | 浅色背景文字 |
| 主色-500 #6366f1 → 白色 #fff | 4.6:1 | AA | 主色按钮文字 |
| 错误-500 #ef4444 → 白色 #fff | 4.6:1 | AA | 错误态按钮文字 |

---

## 图标色彩

图标颜色应与周围文字颜色保持一致：

```css
/* 继承文字颜色 */
.icon {
  width: 20px;
  height: 20px;
  color: currentColor;
}

/* 功能色图标 */
.icon-success { color: var(--color-success); }
.icon-warning { color: var(--color-warning); }
.icon-error { color: var(--color-error); }
.icon-info { color: var(--color-info); }
```
