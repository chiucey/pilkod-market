# Design Tokens 完整参考

> 本文件由 SKILL.md 引用，包含完整的设计变量定义。
> 项目使用 Less 变量 + CSS Custom Properties 双层体系。

---

## Less 变量（源码层，`src/styles/variables.less`）

```less
// ===== 主色 =====
@primary-color:        #19c8b9;
@primary-color-hover:  #3dd4c6;
@primary-color-active: #11a89b;
@primary-color-bg:     #e6f9f6;

// ===== 状态色 =====
@success-color:        #6fba2c;
@success-color-hover:  #85cc45;
@success-color-active: #5a9e1e;

@warning-color:        #f5c31c;
@warning-color-hover:  #f7d04a;
@warning-color-active: #dba90e;

@error-color:          #e05a5a;
@error-color-hover:    #e87878;
@error-color-active:   #c94444;

// ===== 文字 =====
@text-color:           #794f27;
@text-color-secondary: #9f927d;
@text-color-disabled:  #c4b89e;

// ===== 边框 =====
@border-color:         #9f927d;
@border-color-hover:   #827157;

// ===== 背景 =====
@bg-color:             #f8f8f0;
@bg-color-secondary:   #f0e8d8;
@bg-color-disabled:    #f0ece2;
// 内容区实际值：rgb(247, 243, 223)

// ===== 字体 =====
@font-family: Nunito, 'Zen Maru Gothic', -apple-system,
  'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
@font-size-sm:   12px;
@font-size-base: 14px;
@font-size-lg:   16px;
@line-height-base: 1.5715;

// ===== 间距 =====
@spacing-xs: 4px;
@spacing-sm: 8px;
@spacing-md: 12px;
@spacing-lg: 16px;
@spacing-xl: 24px;

// ===== 圆角 =====
@border-radius-sm:   12px;
@border-radius-base: 18px;
@border-radius-lg:   24px;
@border-width:       2px;

// ===== 阴影 =====
@shadow-sm:   0 2px  4px  0 rgba(61, 52, 40, 0.06);
@shadow-base: 0 3px  10px 0 rgba(61, 52, 40, 0.10);
@shadow-lg:   0 8px  24px 0 rgba(61, 52, 40, 0.14);

// ===== 动效 =====
@motion-duration-fast: 0.15s;
@motion-duration-base: 0.25s;
@motion-duration-slow: 0.35s;
@motion-ease: cubic-bezier(0.4, 0, 0.2, 1);

// ===== 高度 =====
@height-sm:   32px;
@height-base: 40px;
@height-lg:   48px;
```

---

## CSS Custom Properties（运行时，`:root`）

所有 Less 变量均映射为 `--animal-*` CSS 变量，可在任意 CSS 中使用：

```css
var(--animal-primary-color)        /* #19c8b9 */
var(--animal-text-color)           /* #794f27 */
var(--animal-bg-color)             /* #f8f8f0 */
var(--animal-border-color)         /* #9f927d */
var(--animal-border-radius-base)   /* 18px */
var(--animal-shadow-base)          /* 0 3px 10px 0 rgba(...) */
var(--animal-motion-duration-base) /* 0.25s */
var(--animal-motion-ease)          /* cubic-bezier(0.4,0,0.2,1) */
var(--animal-font-family)          /* Nunito, ... */
var(--animal-spacing-xl)           /* 24px */
var(--animal-height-base)          /* 40px */
```

---

## NookPhone 调色板（Card color 变体）

| color prop | 背景色 | 文字色 | 用途 |
|---|---|---|---|
| `default` | `rgb(247,243,223)` | `#725d42` | 默认奶油色 |
| `app-pink` | `#f8a6b2` | `#fff` | 粉色应用 |
| `purple` | `#b77dee` | `#fff` | 紫色 |
| `app-blue` | `#889df0` | `#fff` | 蓝色应用 |
| `app-yellow` | `#f7cd67` | `#725d42` | 黄色应用 |
| `app-orange` | `#e59266` | `#fff` | 橙色应用 |
| `app-teal` | `#82d5bb` | `#fff` | 青色应用 |
| `app-green` | `#8ac68a` | `#fff` | 绿色应用 |
| `app-red` | `#fc736d` | `#fff` | 红色应用 |
| `lime-green` | `#d1da49` | `#3d5a1a` | 青柠绿 |
| `yellow-green` | `#ecdf52` | `#725d42` | 黄绿色 |
| `brown` | `#9a835a` | `#fff` | 棕色 |
| `warm-peach-pink` | `#e18c6f` | `#fff` | 暖桃粉 |

---

## 特殊色值（非 Token，硬编码于组件）

| 用途 | 色值 |
|---|---|
| 焦点高亮（Input/Switch） | `#ffcc00` |
| 焦点阴影色 | `#e0b800` |
| 侧边栏选中背景 | `#B7C6E5` |
| 侧边栏 hover 背景 | `#d6dff0` |
| 按钮底部阴影色 | `#bdaea0` |
| 输入框底部阴影色 | `#d4c9b4` |
| Switch 开启阴影色 | `#5a9e1e` |
| 弹窗/卡片内容背景 | `rgb(247, 243, 223)` |
| 弹窗文字色 | `rgb(128, 115, 89)` / `#8a7b66` |
