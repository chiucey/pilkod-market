---
name: animal-island-ui-style
version: 1.0.0
author: guokaigdg
description: >
  为使用 animal-island-ui 组件库或复现其视觉风格提供完整设计指南。
  当用户需要：用动物森友会风格开发 React 页面或组件、使用 animal-island-ui
  库、构建温馨自然圆润可爱的 UI、或询问"动物森友会风格""animal island 风格"
  "圆润游戏风格 UI"时，必须使用此 skill。提供安装方法、设计原则、
  组件 API、Design Token 及从零实现指南。
---

# Animal Island UI Style

受《集合啦！动物森友会》启发的 React + TypeScript UI 组件库设计风格指南。

**安装：**
```bash
npm install animal-island-ui
```

**快速上手：**
```tsx
import { Button, Card, Switch, Modal, Input, Time, Phone } from 'animal-island-ui';
```

> 详细 Design Tokens 见 `references/tokens.md`
> 完整组件 API 见 `references/components.md`

---

## 设计语言核心（必须理解）

### 1. 游戏按键立体感 — 最重要特征

所有可交互元素用底部厚阴影模拟任天堂手柄的 3D 按压效果：

```css
/* 默认：底部厚阴影 */
box-shadow: 0 5px 0 0 #bdaea0;

/* Hover：元素上浮，阴影加深 */
transform: translateY(-1px);
box-shadow: 0 6px 0 0 #bdaea0;

/* Active：元素下压，阴影缩短 */
transform: translateY(2px);
box-shadow: 0 1px 0 0 #bdaea0;
```

输入框用 `box-shadow: 0 3px 0 0 #d4c9b4`，Switch 手柄用 `transform: translateY(-2px)` 保持悬浮感。

---

### 2. 色彩系统 — 温暖大地色 + 薄荷青绿

```
主色：    #19c8b9（薄荷青绿）  hover: #3dd4c6  active: #11a89b
文字：    #794f27（棕色）       次级: #9f927d   禁用: #c4b89e
背景：    rgb(247,243,223)（奶油米白）
边框：    #c4b89e
焦点高亮：#ffcc00（游戏黄，非蓝色）
选中菜单：#B7C6E5
```

---

### 3. 形态 — 圆润 pill 形 + 有机不规则

- **按钮 / 输入框**：`border-radius: 50px`（pill 胶囊形）
- **卡片**：`border-radius: 20px`
- **标题卡**：非对称圆角 `40px 35px 45px 38px / 38px 45px 35px 40px`
- **弹窗**：SVG clip-path blob 轮廓（有机不规则形状）

```jsx
// Modal 内嵌 SVG 裁剪路径
<svg style={{ position:'absolute', width:0, height:0 }} aria-hidden>
  <clipPath id="animal-modal-clip" clipPathUnits="objectBoundingBox">
    <path d="M0.501,0.005 L0.501,0.005 L0.523,0.005 L0.549,0.006
      C0.704,0.01,0.796,0.017,0.825,0.027 L0.827,0.028 C0.872,0.045,
      0.939,0.044,0.978,0.17 C1,0.254,1,0.365,0.99,0.505 L0.988,0.513
      C0.979,0.558,0.971,0.598,0.965,0.633 C0.956,0.689,0.979,0.77,
      0.964,0.865 C0.953,0.928,0.921,0.966,0.869,0.979 C0.821,0.986,
      0.773,0.992,0.726,0.995 L0.712,0.996 L0.694,0.997 C0.648,1,
      0.586,1,0.507,1 L0.501,1 L0.464,1 C0.385,1,0.325,0.998,0.283,
      0.995 C0.234,0.992,0.184,0.987,0.133,0.979 C0.081,0.966,0.05,
      0.928,0.039,0.865 C0.023,0.77,0.047,0.689,0.037,0.633
      C0.031,0.595,0.023,0.552,0.013,0.505 C-0.006,0.365,-0.002,0.254,
      0.024,0.17 C0.064,0.045,0.13,0.045,0.174,0.028 L0.175,0.028
      C0.204,0.017,0.303,0.009,0.474,0.005 L0.501,0.005" />
  </clipPath>
</svg>
```

---

### 4. 字体 / 动效 / 边框

```css
/* 字体：圆体，字重 600+ */
font-family: Nunito, 'Zen Maru Gothic', -apple-system, 'PingFang SC', sans-serif;

/* 过渡：统一缓动曲线 */
transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

/* 边框：2~2.5px，棕灰色 */
border: 2px solid #c4b89e;
```

---

## 常用组件示例

```tsx
// Button — 游戏按键风格，5种类型 3种尺寸
<Button type="primary">开始冒险</Button>
<Button type="default" size="large">探索</Button>
<Button type="dashed" danger>危险</Button>
<Button loading ghost type="primary">加载中</Button>

// Input — pill 形，焦点黄色高亮
<Input placeholder="搜索岛民..." allowClear prefix="🌿" />
<Input status="error" size="large" />

// Switch — 自然绿开关，带立体手柄
<Switch defaultChecked checkedChildren="开" unCheckedChildren="关" />

// Card — 13 种 NookPhone 主题色
<Card color="app-blue">蓝色</Card>
<Card type="title" color="app-yellow">标题卡</Card>

// Modal — blob 有机外形，ESC 可关闭
<Modal open={open} title="欢迎来到无人岛" onClose={close} onOk={ok}>
  内容
</Modal>

// Collapse — 叶片装饰折叠面板
<Collapse question="问题" answer="答案" defaultExpanded />

// 特色组件
<Cursor><App /></Cursor>   {/* 游戏风格光标 */}
<Time />                   {/* 实时时钟 */}
<Phone />                  {/* NookPhone 手机 UI */}
<Divider />                {/* 装饰分割线 */}
```

---

## 从零实现规则（不使用组件库）

粘贴此 CSS 变量作为起点：

```css
:root {
  --animal-primary:  #19c8b9;
  --animal-text:     #794f27;
  --animal-bg:       rgb(247, 243, 223);
  --animal-border:   #c4b89e;
  --animal-radius:   18px;
  --animal-font:     Nunito, 'Zen Maru Gothic', sans-serif;
  --animal-focus:    #ffcc00;
  --animal-shadow:   0 5px 0 0 #bdaea0;
}
```

**7 条设计铁律：**

1. 颜色只用大地棕色系 + 薄荷青绿，禁止纯黑 / 冷灰
2. 圆角最小 12px，按钮 / 输入框用 50px pill 形
3. 所有可点击元素必须有底部厚阴影，hover 上浮，active 下压
4. 字体用 Nunito 圆体，字重 600 起步
5. 动效过渡 0.15~0.35s，缓动 `cubic-bezier(0.4, 0, 0.2, 1)`
6. 焦点高亮用 `#ffcc00` 黄色，不用蓝色
7. 禁止：直角矩形、纯黑文字、冷蓝色交互、完全扁平无阴影

---

## 新组件开发规范

```
src/components/MyComponent/
├── MyComponent.tsx          # 组件逻辑，末尾必须设置 displayName
├── myComponent.module.less  # CSS Modules，自动注入全局 Less 变量
└── index.ts                 # 导出
```

Less 文件直接使用 Design Token 变量（由 vite.config additionalData 注入）：

```less
.btn {
  border-radius: @border-radius-base;
  color: @text-color;
  border: @border-width solid @border-color;
  transition: all @motion-duration-base @motion-ease;
  box-shadow: 0 5px 0 0 #bdaea0;

  &:hover { transform: translateY(-1px); box-shadow: 0 6px 0 0 #bdaea0; }
  &:active { transform: translateY(2px); box-shadow: 0 1px 0 0 #bdaea0; }
}
```

CSS Modules scoped 类名格式：`animal-[local]-[hash:base64:5]`
