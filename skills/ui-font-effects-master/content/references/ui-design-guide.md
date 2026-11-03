# 现代UI设计规范参考

## 1. 设计系统基础

### 1.1 色彩系统

#### 主色板
```css
:root {
  /* Primary */
  --primary-50: #EEF2FF;
  --primary-100: #E0E7FF;
  --primary-200: #C7D2FE;
  --primary-300: #A5B4FC;
  --primary-400: #818CF8;
  --primary-500: #6366F1;
  --primary-600: #4F46E5;
  --primary-700: #4338CA;
  --primary-800: #3730A3;
  --primary-900: #312E81;

  /* Neutral */
  --neutral-50: #F8FAFC;
  --neutral-100: #F1F5F9;
  --neutral-200: #E2E8F0;
  --neutral-300: #CBD5E1;
  --neutral-400: #94A3B8;
  --neutral-500: #64748B;
  --neutral-600: #475569;
  --neutral-700: #334155;
  --neutral-800: #1E293B;
  --neutral-900: #0F172A;

  /* Semantic */
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  --info: #3B82F6;
}
```

#### 暗色模式适配
```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #0F172A;
    --bg-secondary: #1E293B;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --border-color: #334155;
  }
}
```

### 1.2 字体系统

#### 字体栈
```css
/* 中文优先字体栈 */
--font-sans: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
--font-serif: 'Playfair Display', 'Noto Serif SC', Georgia, serif;
--font-mono: 'JetBrains Mono', 'Fira Code', Consolas, monospace;

/* 字号系统 */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
--text-5xl: 3rem;      /* 48px */

/* 行高 */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

#### 字体使用规范
| 场景 | 字体 | 字号 | 字重 |
|------|------|------|------|
| 页面标题 | Sans-serif | 32-48px | 700 |
| 区块标题 | Sans-serif | 24-28px | 600 |
| 正文 | Sans-serif | 16px | 400 |
| 辅助文字 | Sans-serif | 14px | 400 |
| 按钮文字 | Sans-serif | 14-16px | 500-600 |

### 1.3 间距系统

```css
/* 基础间距单位: 4px */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */

/* 组件间距 */
--component-padding: 16px;
--card-padding: 24px;
--section-gap: 64px;
```

### 1.4 圆角与阴影

```css
/* 圆角 */
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-2xl: 24px;
--radius-full: 9999px;

/* 阴影 */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* 暗色阴影 */
--shadow-dark: 0 4px 20px rgba(0, 0, 0, 0.3);
```

## 2. 组件设计规范

### 2.1 按钮

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  border-radius: var(--radius-lg);
  transition: all 0.2s ease;
  cursor: pointer;
}

.btn-primary {
  background: var(--primary-500);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-600);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
}

.btn-ghost:hover {
  background: var(--bg-secondary);
}
```

### 2.2 卡片

```css
.card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--card-padding);
  transition: all 0.3s ease;
}

.card:hover {
  border-color: var(--primary-300);
  box-shadow: var(--shadow-lg);
}

.card-interactive {
  cursor: pointer;
}

.card-interactive:hover {
  transform: translateY(-4px);
}
```

### 2.3 输入框

```css
.input {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px var(--primary-100);
}

.input::placeholder {
  color: var(--text-secondary);
}
```

## 3. 响应式断点

```css
/* 移动端优先断点 */
/* sm: 640px */
@media (min-width: 640px) { }

/* md: 768px */
@media (min-width: 768px) { }

/* lg: 1024px */
@media (min-width: 1024px) { }

/* xl: 1280px */
@media (min-width: 1280px) { }

/* 2xl: 1536px */
@media (min-width: 1536px) { }
```

### 栅格系统
```css
.grid {
  display: grid;
  gap: 24px;
}

.grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
.grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
.grid-cols-3 { grid-template-columns: repeat(3, 1fr); }
.grid-cols-4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 768px) {
  .md\:grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 640px) {
  .sm\:grid-cols-1 { grid-template-columns: repeat(1, 1fr); }
}
```

## 4. 页面结构模板

### 4.1 登录页结构
```
┌────────────────────────────────────┐
│           Logo / Brand             │
├────────────────────────────────────┤
│                                    │
│         ┌──────────────────┐       │
│         │   欢迎回来        │       │
│         │   请登录您的账户   │       │
│         ├──────────────────┤       │
│         │  邮箱 / 手机号    │       │
│         ├──────────────────┤       │
│         │  密码             │       │
│         ├──────────────────┤       │
│         │  [ 登录按钮 ]     │       │
│         │  忘记密码？       │       │
│         └──────────────────┘       │
│                                    │
│         还没有账户？注册            │
└────────────────────────────────────┘
```

### 4.2 首页结构
```
┌────────────────────────────────────┐
│  Logo    Nav Links    User/Auth   │ ← 导航栏
├────────────────────────────────────┤
│                                    │
│      Hero: 大标题 + 副标题         │ ← Hero区域
│      [CTA按钮] [次要按钮]          │
│                                    │
├────────────────────────────────────┤
│   Feature 1  │  Feature 2  │ F3   │ ← 特色展示
├────────────────────────────────────┤
│                                    │
│        内容区域 1                   │ ← 内容区块
│                                    │
├────────────────────────────────────┤
│        内容区域 2                   │
├────────────────────────────────────┤
│         Footer / 版权               │
└────────────────────────────────────┘
```

### 4.3 仪表盘结构
```
┌────────────────────────────────────────┐
│  Logo    Search    Notifications  User │
├────────┬───────────────────────────────┤
│        │                               │
│  Nav   │    Stats Cards (4列)         │
│        │                               │
│  Home  │    ┌─────────┐ ┌─────────┐   │
│  Stats │    │ 图表1   │ │ 图表2   │   │
│  Users │    └─────────┘ └─────────┘   │
│  Set   │                               │
│        │    数据表格 / 列表             │
│        │                               │
└────────┴───────────────────────────────┘
     侧边栏
```

## 5. 动画与过渡

```css
/* 基础过渡 */
.transition {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 悬停效果 */
.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}

/* 点击效果 */
.press-effect:active {
  transform: scale(0.98);
}

/* 入场动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 0.6s ease-out;
}

/* 加载动画 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
```
