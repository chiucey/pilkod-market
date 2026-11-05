---
name: design-system
description: 设计系统构建与企业级设计规范。当用户要求建立设计系统、制定设计规范、设计组件库、创建 Design Token、统一多端体验、设计管理流程时使用。涵盖设计系统的规划、建设、维护到推广的完整生命周期。
---

# 设计系统 (Design System)

## 核心理念

**Max-De$ign 主张：要么设计，要么被设计。**

设计系统是组织级设计能力的沉淀，通过标准化、可复用、可扩展的设计资产和流程，实现设计效率提升和体验一致性。

---

## 1. 设计系统架构

### 设计系统层次

```
┌─────────────────────────────────────────────────────────────┐
│                    设计系统层次                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                  体验原则层                          │  │
│   │         Design Principles / Design Values           │  │
│   └─────────────────────────────────────────────────────┘  │
│                            │                                │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                  基础设计层                          │  │
│   │    色彩 / 字体 / 间距 / 图标 / 动效 / 插画          │  │
│   └─────────────────────────────────────────────────────┘  │
│                            │                                │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                  组件设计层                          │  │
│   │         基础组件 / 业务组件 / 复合组件              │  │
│   └─────────────────────────────────────────────────────┘  │
│                            │                                │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                  模式设计层                          │  │
│   │      表单模式 / 导航模式 / 数据展示模式 / 反馈模式  │  │
│   └─────────────────────────────────────────────────────┘  │
│                            │                                │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                  页面模板层                          │  │
│   │          业务页面模板 / 场景化模板                  │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 设计系统与品牌的关系

| 层面 | 设计系统 | 品牌视觉 |
|------|----------|----------|
| 核心理念 | ✓ 遵循 | 品牌定义 |
| 色彩系统 | ✓ 扩展 | 品牌色板 |
| 字体系统 | ✓ 扩展 | 品牌字体 |
| 图形元素 | ✓ 适配 | 品牌图案 |
| 整体调性 | ✓ 保持一致 | 品牌调性 |

---

## 2. Design Token 设计

### Token 命名规范

```
┌─────────────────────────────────────────────────────────────┐
│                    Token 命名结构                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   命名格式: [类别]-[属性]-[状态]-[尺寸]                    │
│                                                             │
│   类别:                                                     │
│   ├── color                                               │
│   ├── typography                                          │
│   ├── spacing                                             │
│   ├── shadow                                              │
│   ├── border                                              │
│   └── motion                                              │
│                                                             │
│   示例:                                                     │
│   ├── color-primary-default                               │
│   ├── color-primary-hover                                 │
│   ├── color-primary-active                                │
│   ├── color-text-primary                                 │
│   ├── color-text-secondary                               │
│   ├── color-background-default                           │
│   ├── color-border-default                                │
│   ├── spacing-xs (4px)                                   │
│   ├── spacing-sm (8px)                                   │
│   ├── spacing-md (16px)                                  │
│   ├── spacing-lg (24px)                                  │
│   ├── spacing-xl (32px)                                  │
│   ├── font-size-heading-lg (32px)                        │
│   ├── font-size-heading-md (24px)                        │
│   ├── font-size-body (16px)                              │
│   └── font-size-caption (12px)                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 色彩 Token 体系

```
┌─────────────────────────────────────────────────────────────┐
│                    色彩 Token 层级                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   层级1: Primitive (原始值)                                │
│   ├── blue-50: #EFF6FF                                    │
│   ├── blue-100: #DBEAFE                                    │
│   ├── blue-500: #3B82F6                                    │
│   └── blue-600: #2563EB                                    │
│                                                             │
│   层级2: Semantic (语义化)                                 │
│   ├── color-brand-primary: {blue-600}                     │
│   ├── color-brand-secondary: {blue-500}                   │
│   ├── color-text-primary: {gray-900}                      │
│   ├── color-text-secondary: {gray-600}                     │
│   ├── color-background-default: {white}                    │
│   └── color-border-default: {gray-200}                     │
│                                                             │
│   层级3: Component (组件化)                                │
│   ├── button-primary-bg: {color-brand-primary}            │
│   ├── button-primary-text: {white}                        │
│   ├── input-border: {color-border-default}                │
│   └── link-color: {color-brand-primary}                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Typography Token

```css
/* 字体族 */
--font-family-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-family-mono: 'JetBrains Mono', monospace;

/* 字号 */
--font-size-xs: 12px;
--font-size-sm: 14px;
--font-size-base: 16px;
--font-size-lg: 18px;
--font-size-xl: 20px;
--font-size-2xl: 24px;
--font-size-3xl: 30px;
--font-size-4xl: 36px;

/* 字重 */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;

/* 行高 */
--line-height-tight: 1.25;
--line-height-normal: 1.5;
--line-height-relaxed: 1.625;

/* 字间距 */
--letter-spacing-tight: -0.025em;
--letter-spacing-normal: 0;
--letter-spacing-wide: 0.025em;
```

### Spacing Token

```css
/* 基于4px/8px网格 */
--spacing-0: 0px;
--spacing-1: 4px;
--spacing-2: 8px;
--spacing-3: 12px;
--spacing-4: 16px;
--spacing-5: 20px;
--spacing-6: 24px;
--spacing-8: 32px;
--spacing-10: 40px;
--spacing-12: 48px;
--spacing-16: 64px;
--spacing-20: 80px;

/* 语义化间距 */
--spacing-xs: var(--spacing-1);   /* 紧凑间距 */
--spacing-sm: var(--spacing-2);   /* 小间距 */
--spacing-md: var(--spacing-4);   /* 默认间距 */
--spacing-lg: var(--spacing-6);   /* 大间距 */
--spacing-xl: var(--spacing-8);   /* 特大间距 */
--spacing-2xl: var(--spacing-12); /* 超大间距 */
```

---

## 3. 组件设计规范

### 组件分类

| 类别 | 说明 | 示例 |
|------|------|------|
| 原子组件 | 最小可复用单元 | Button, Input, Icon |
| 分子组件 | 简单组件组合 | SearchBar, FormItem |
| 有机体 | 复杂业务组件 | DataTable, Form |
| 模板组件 | 页面级结构 | PageHeader, PageLayout |

### 组件规范文档模板

```
┌─────────────────────────────────────────────────────────────┐
│                    组件规范模板                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   组件名称: Button (按钮)                                   │
│   ───────────────────────────────────────────────────────  │
│                                                             │
│   1. 概述                                                   │
│      ├── 组件用途: 触发操作                                │
│      ├── 使用场景: 表单、对话框、页面操作                   │
│      └── 状态说明: 支持多种变体和尺寸                       │
│                                                             │
│   2. 变体 (Variants)                                       │
│      ├── Primary: 主要操作                                  │
│      ├── Secondary: 次要操作                                 │
│      ├── Ghost: 幽灵按钮                                    │
│      └── Danger: 危险操作                                   │
│                                                             │
│   3. 尺寸 (Sizes)                                          │
│      ├── Small (sm): 高度32px，字号14px                     │
│      ├── Medium (md): 高度40px，字号16px                    │
│      └── Large (lg): 高度48px，字号18px                    │
│                                                             │
│   4. 状态 (States)                                         │
│      ├── Default: 默认状态                                 │
│      ├── Hover: 悬停状态 (背景加深)                         │
│      ├── Active: 按下状态 (背景更深)                        │
│      ├── Focus: 聚焦状态 (边框高亮)                         │
│      ├── Disabled: 禁用状态 (透明度50%)                     │
│      └── Loading: 加载状态 (显示spinner)                    │
│                                                             │
│   5. 属性 (Props)                                          │
│      ├── variant: 'primary' | 'secondary' | 'ghost' | 'danger' │
│      ├── size: 'sm' | 'md' | 'lg'                         │
│      ├── disabled: boolean                                 │
│      ├── loading: boolean                                  │
│      ├── leftIcon: ReactNode                               │
│      ├── rightIcon: ReactNode                              │
│      └── ...                                               │
│                                                             │
│   6. 代码示例                                               │
│      ```tsx                                                │
│      <Button variant="primary" size="md">                  │
│        确认                                                  │
│      </Button>                                             │
│      ```                                                   │
│                                                             │
│   7. 设计与开发一致性                                       │
│      └── Sketch/Figma: Button Component                    │
│          代码: @ds/Button                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 组件状态规范

```
┌─────────────────────────────────────────────────────────────┐
│                    组件状态规范                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   所有组件必须支持的状态:                                    │
│                                                             │
│   状态        │ 视觉表现              │ 交互行为            │
│   ────────────┼──────────────────────┼─────────────────────  │
│   Default     │ 基础样式              │ 可交互              │
│   Hover       │ 视觉反馈              │ 指针变为pointer     │
│   Active      │ 按下反馈              │ 触发操作            │
│   Focus       │ 焦点指示              │ Tab键可聚焦        │
│   Disabled    │ 视觉降级              │ 不可交互            │
│   Loading     │ 加载指示              │ 禁用交互            │
│   Error       │ 错误状态              │ 显示错误信息        │
│                                                             │
│   状态优先级:                                              │
│   Disabled > Error > Loading > Focus > Hover > Default      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 组件库建设

### 组件库结构

```
src/
├── tokens/                 # Design Token
│   ├── colors.ts
│   ├── typography.ts
│   ├── spacing.ts
│   └── index.ts
│
├── foundations/           # 基础层
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.module.css
│   │   ├── Button.stories.tsx
│   │   └── Button.test.tsx
│   ├── Input/
│   ├── Select/
│   └── ...
│
├── patterns/              # 模式层
│   ├── Form/
│   ├── DataTable/
│   └── ...
│
├── templates/             # 模板层
│   ├── PageLayout/
│   └── ...
│
├── hooks/                 # Hooks
│   ├── useTheme.ts
│   └── ...
│
└── index.ts              # 导出入口
```

### 组件开发流程

```
┌─────────────────────────────────────────────────────────────┐
│                    组件开发流程                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. 需求分析                                               │
│   ├── 使用场景                                              │
│   ├── 变体需求                                              │
│   ├── 状态需求                                              │
│   └── 设计稿评审                                            │
│                                                             │
│   2. 设计阶段                                               │
│   ├── 设计稿制作                                            │
│   ├── 状态梳理                                              │
│   ├── 变体规划                                              │
│   └── 设计验收                                              │
│                                                             │
│   3. 开发阶段                                               │
│   ├── 技术方案设计                                          │
│   ├── 代码实现                                              │
│   ├── 样式开发                                              │
│   └── 代码评审                                              │
│                                                             │
│   4. 质量保证                                               │
│   ├── 单元测试                                              │
│   ├── 视觉还原                                              │
│   ├── 自动化截图                                            │
│   └── Accessibility审计                                    │
│                                                             │
│   5. 文档阶段                                               │
│   ├── API文档                                              │
│   ├── Storybook故事                                        │
│   ├── 使用指南                                              │
│   └── CHANGELOG                                            │
│                                                             │
│   6. 发布阶段                                               │
│   ├── 版本号管理                                            │
│   ├── NPM发布                                              │
│   └── 变更通知                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. 动效设计规范

### 动效 Token

```css
/* 过渡时长 */
--duration-instant: 0ms;
--duration-fast: 100ms;
--duration-normal: 200ms;
--duration-slow: 300ms;
--duration-slower: 500ms;

/* 缓动函数 */
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);

/* 常用组合 */
--transition-fast: var(--duration-fast) var(--ease-out);
--transition-normal: var(--duration-normal) var(--ease-out);
--transition-slow: var(--duration-slow) var(--ease-in-out);
```

### 动效场景规范

| 场景 | 时长 | 缓动 | 说明 |
|------|------|------|------|
| 微交互反馈 | 100-150ms | ease-out | 按钮hover、点击 |
| 状态切换 | 200-300ms | ease-out | 展开/收起 |
| 页面进入 | 300-400ms | ease-out | 元素出现 |
| 大范围移动 | 400-600ms | ease-in-out | 页面切换 |
| Loading | 循环 | linear | 持续动画 |

---

## 6. 图标系统

### 图标设计规范

| 规范 | 说明 |
|------|------|
| 基础网格 | 24×24px (标准) 或 20×20px (精简) |
| 线宽 | 1.5px 或 2px (统一) |
| 圆角 | 2px (统一) |
| 风格 | 线性/填充/双色 (三选一) |
| 命名 | kebab-case, 如 `arrow-right` |

### 图标命名规范

```
┌─────────────────────────────────────────────────────────────┐
│                    图标命名规范                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   格式: [类别]-[方向/状态]-[名称]                          │
│                                                             │
│   示例:                                                     │
│   ├── arrow-up                                            │
│   ├── arrow-down                                          │
│   ├── arrow-left                                          │
│   ├── arrow-right                                         │
│   ├── chevron-up                                          │
│   ├── check-circle                                        │
│   ├── warning-circle-filled                               │
│   ├── home-outlined                                       │
│   └── home-filled                                         │
│                                                             │
│   状态后缀:                                                │
│   ├── -outlined: 描边风格                                  │
│   ├── -filled: 实心风格                                    │
│   ├── -active: 激活状态                                    │
│   └── -disabled: 禁用状态                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. 响应式设计规范

### 断点系统

```css
/* 断点定义 */
--breakpoint-sm: 640px;   /* 手机横屏/大手机 */
--breakpoint-md: 768px;   /* 平板竖屏 */
--breakpoint-lg: 1024px;  /* 平板横屏/小桌面 */
--breakpoint-xl: 1280px;  /* 桌面 */
--breakpoint-2xl: 1536px; /* 大屏 */

/* 容器 */
--container-sm: 640px;
--container-md: 768px;
--container-lg: 1024px;
--container-xl: 1280px;
--container-2xl: 1536px;

/* 栅格 */
--grid-columns: 4;   /* 手机 */
--grid-columns-md: 8; /* 平板 */
--grid-columns-lg: 12; /* 桌面 */
--grid-gutter: 16px; /* 间距 */
```

### 响应式组件策略

| 策略 | 说明 | 示例 |
|------|------|------|
| 堆叠 | 移动端垂直排列 | 卡片列表 |
| 隐藏 | 小屏隐藏次要内容 | 侧边栏 |
| 缩放 | 按比例调整大小 | 表格、图表 |
| 切换 | 不同场景不同组件 | 导航→抽屉 |
| 自适应 | 内容自动适应宽度 | 文本、图片 |

---

## 8. Accessibility 规范

### WCAG 标准要点

| 级别 | 标准 | 要求 |
|------|------|------|
| A级 | 最低 | 可感知、可操作 |
| AA级 | 标准 | 对比度、内容缩放 |
| AAA级 | 最高 | 增强可读性、输入方式 |

### 可访问性检查清单

| 检查项 | 说明 | 验证方法 |
|--------|------|----------|
| 对比度 | 文字与背景≥4.5:1 | WCAG Contrast Checker |
| 焦点可见 | Tab键可聚焦，有视觉指示 | 手动测试 |
| 替代文本 | 图片有alt属性 | 代码审查 |
| 表单标签 | Input有label关联 | 代码审查 |
| 键盘操作 | 所有功能可键盘完成 | 手动测试 |
| ARIA标注 | 复杂组件有ARIA标签 | 辅助工具测试 |
| 色彩无关 | 不依赖颜色传达信息 | 灰度测试 |
| 动效控制 | 提供减少动效选项 | 系统设置 |

---

## 9. 文档与交付

### 设计系统文档结构

```
┌─────────────────────────────────────────────────────────────┐
│                    设计系统文档结构                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   📁 design-system-docs/                                    │
│   │                                                        │
│   ├── 📄 README.md                                         │
│   │                                                        │
│   ├── 📁 getting-started/                                   │
│   │   ├── introduction.md                                  │
│   │   ├── installation.md                                  │
│   │   └── contributing.md                                  │
│   │                                                        │
│   ├── 📁 foundations/                                       │
│   │   ├── colors.md                                       │
│   │   ├── typography.md                                   │
│   │   ├── spacing.md                                      │
│   │   ├── icons.md                                       │
│   │   └── motion.md                                       │
│   │                                                        │
│   ├── 📁 components/                                       │
│   │   ├── button.md                                       │
│   │   ├── input.md                                        │
│   │   ├── modal.md                                        │
│   │   └── ...                                             │
│   │                                                        │
│   ├── 📁 patterns/                                         │
│   │   ├── forms.md                                        │
│   │   ├── navigation.md                                    │
│   │   └── data-display.md                                 │
│   │                                                        │
│   └── 📁 resources/                                        │
│       ├── figma-libraries.md                              │
│       ├── code-snippets.md                                │
│       └── changelog.md                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Storybook 集成

| 组件 | Story 类型 |
|------|------------|
| Button | Playground, Variants, Sizes, States |
| Input | Default, WithLabel, WithError, Disabled |
| Modal | Basic, Confirmation, Form, Custom |
| Table | Basic, Sortable, Filterable, Pagination |

---

## 10. 团队协作流程

### 设计-开发协作

```
┌─────────────────────────────────────────────────────────────┐
│                    协作流程                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   设计侧                    开发侧                          │
│   ──────                    ──────                          │
│   创建设计稿                                                  │
│       │                                                        │
│       ▼                                                        │
│   组件设计 ──────────────────▶ 接收设计稿                    │
│       │                                                        │
│       ▼                                                        │
│   设计评审 ◀───────────────── 评审反馈                       │
│       │                                                        │
│       ▼                                                        │
│   标注移交 ──────────────────▶ 开始开发                      │
│       │                                                        │
│       ▼                                                        │
│   视觉验收 ◀───────────────── 开发完成                      │
│       │                                                        │
│       ▼                                                        │
│   文档完善                                                      │
│       │                                                        │
│       ▼                                                        │
│   发布上线                                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 版本管理规范

| 版本类型 | 规则 | 示例 |
|----------|------|------|
| Major | 破坏性变更 | 1.0.0 → 2.0.0 |
| Minor | 新增功能 | 1.0.0 → 1.1.0 |
| Patch | Bug修复 | 1.0.0 → 1.0.1 |

### CHANGELOG 规范

```
## [2.0.0] - 2024-01-15

### Breaking Changes
- Button 组件 `type` 属性变更为 `variant`
- Input 组件 `size` 属性可选值变化

### Added
- 新增 Card 组件
- 新增 Avatar 组件
- 新增 Tag 组件

### Fixed
- 修复 Modal 在移动端的滚动问题
- 修复 Button loading 状态点击问题

### Deprecated
- Input 组件 `status` 属性已废弃，使用 `error` 替代
```

---

## 11. 设计系统评估指标

### 效率指标

| 指标 | 计算方式 | 目标 |
|------|----------|------|
| 组件复用率 | 使用组件的新页面数 / 总新页面数 | > 80% |
| 设计还原度 | 符合规范的元素数 / 总元素数 | > 95% |
| 开发时间节省 | (原时间 - 现时间) / 原时间 | > 30% |

### 质量指标

| 指标 | 计算方式 | 目标 |
|------|----------|------|
| 一致性 | 用户反馈一致性问题数 | < 5/月 |
| Accessibility | WCAG AA 通过率 | 100% |
| Bug率 | 组件相关Bug数 / 总Bug数 | < 20% |

### 采用指标

| 指标 | 计算方式 | 目标 |
|------|----------|------|
| 产品线覆盖 | 使用设计系统的产品数 / 总产品数 | > 90% |
| 团队覆盖 | 使用设计系统的团队数 / 总团队数 | > 90% |

---

*此技能为设计系统建设提供系统性方法论，整合服务设计、品牌视觉、UI/UX设计等专项技能，形成完整的企业级设计能力体系。*
