# 组件 API 完整参考

> 本文件由 SKILL.md 引用，包含所有组件的完整 Props 定义与使用示例。

---

## Button

```tsx
import { Button } from 'animal-island-ui';

type ButtonType = 'primary' | 'default' | 'dashed' | 'text' | 'link';
type ButtonSize = 'small' | 'middle' | 'large';

interface ButtonProps {
  type?:     ButtonType;       // 默认 'default'
  size?:     ButtonSize;       // 默认 'middle'
  danger?:   boolean;          // 危险状态（红色）
  ghost?:    boolean;          // 幽灵按钮（透明背景）
  block?:    boolean;          // 撑满父容器宽度
  loading?:  boolean;          // 加载中（显示斜纹动画，禁用点击）
  disabled?: boolean;
  icon?:     React.ReactNode;  // 左侧图标
  htmlType?: 'submit' | 'reset' | 'button';
  children?: React.ReactNode;
}
```

**样式特征：**
- `border-radius: 50px`（pill 形）
- primary：`background:#f8f8f0; color:#794f27; box-shadow:0 5px 0 0 #bdaea0`
- loading：repeating-linear-gradient 斜纹滚动动画
- hover：`translateY(-1px)` + 阴影加深；active：`translateY(2px)` + 阴影缩短

```tsx
<Button type="primary">开始冒险</Button>
<Button type="default" size="large" icon={<LeafIcon />}>探索</Button>
<Button type="dashed" danger>危险操作</Button>
<Button type="primary" loading>保存中</Button>
<Button ghost type="primary">幽灵按钮</Button>
<Button block type="default">块级按钮</Button>
```

---

## Input

```tsx
import { Input } from 'animal-island-ui';

type InputSize = 'small' | 'middle' | 'large';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  size?:       InputSize;
  prefix?:     React.ReactNode;  // 左侧内容（图标/文字）
  suffix?:     React.ReactNode;  // 右侧内容
  allowClear?: boolean;          // 显示清除按钮
  status?:     'error' | 'warning';
  onClear?:    () => void;
}
```

**样式特征：**
- `border-radius: 50px; border: 2.5px solid #c4b89e; box-shadow: 0 3px 0 0 #d4c9b4`
- 焦点：`border-color: #ffcc00; box-shadow: 0 3px 0 0 #e0b800, 0 0 0 3px rgba(255,204,0,0.15)`
- 背景：`rgb(247, 243, 223)`

```tsx
<Input placeholder="搜索岛民..." />
<Input size="large" prefix="🌿" suffix="🍃" allowClear />
<Input status="error" placeholder="错误状态" />
<Input status="warning" />
<Input disabled placeholder="禁用" />
```

---

## Switch

```tsx
import { Switch } from 'animal-island-ui';

type SwitchSize = 'default' | 'small';

interface SwitchProps {
  checked?:          boolean;           // 受控
  defaultChecked?:   boolean;           // 非受控初始值
  size?:             SwitchSize;
  disabled?:         boolean;
  loading?:          boolean;           // 加载中旋转图标
  checkedChildren?:  React.ReactNode;   // 开启时文字
  unCheckedChildren?: React.ReactNode;  // 关闭时文字
  onChange?:         (checked: boolean) => void;
}
```

**样式特征：**
- 关闭：`background:#d4c9b4; border:2.5px solid #c4b89e`
- 开启：`background:#86d67a; border-color:#6fba2c`
- 手柄：`background:rgb(247,243,223); border-radius:50%; box-shadow:0 3px 0 0 #bdaea0; transform:translateY(-2px)`
- 焦点：`outline: 2px solid #ffcc00`

```tsx
<Switch defaultChecked checkedChildren="开" unCheckedChildren="关" />
<Switch size="small" />
<Switch loading />
<Switch disabled />
```

---

## Card

```tsx
import { Card } from 'animal-island-ui';

type CardType  = 'default' | 'title';
type CardColor = 'default' | 'app-pink' | 'purple' | 'app-blue' | 'app-yellow'
               | 'app-orange' | 'app-teal' | 'app-green' | 'app-red'
               | 'lime-green' | 'yellow-green' | 'brown' | 'warm-peach-pink';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  type?:     CardType;   // 默认 'default'
  color?:    CardColor;  // 默认 'default'（奶油色）
  children?: React.ReactNode;
}
```

**样式特征：**
- default：`border-radius:20px; background:rgb(247,243,223); color:#725d42`
- title：`border-radius:40px 35px 45px 38px / 38px 45px 35px 40px`（有机形状）
- hover：`translateY(-4px); box-shadow:0 8px 24px rgba(114,93,66,0.15)`

```tsx
<Card>默认奶油色卡片</Card>
<Card color="app-blue">蓝色主题</Card>
<Card color="app-yellow">黄色主题</Card>
<Card type="title" color="app-pink">有机形状标题卡</Card>
```

---

## Collapse

```tsx
import { Collapse } from 'animal-island-ui';

interface CollapseProps {
  question:        React.ReactNode;  // 问题/标题
  answer:          React.ReactNode;  // 答案/内容
  defaultExpanded?: boolean;         // 默认展开
  disabled?:        boolean;
}
```

**样式特征：**
- 背景：`@bg-color`，展开时渐变 `bg-color → bg-color-secondary`
- 图标：圆形青绿主色背景，展开时旋转 180°
- 叶片 SVG 装饰，展开时旋转 45°
- 展开动画：`grid-template-rows: 0fr → 1fr`（无 JS 高度计算）

```tsx
<Collapse
  question="什么是动物森友会？"
  answer="这是任天堂出品的模拟经营游戏，于 2020 年发售。"
  defaultExpanded
/>
<Collapse question="如何安装？" answer={<code>npm install animal-island-ui</code>} />
<Collapse question="禁用项" answer="内容" disabled />
```

---

## Modal

```tsx
import { Modal } from 'animal-island-ui';

interface ModalProps {
  open:           boolean;
  title?:         React.ReactNode;
  width?:         number | string;   // 默认 520
  maskClosable?:  boolean;           // 默认 true，点击遮罩关闭
  closable?:      boolean;           // 默认 true
  footer?:        React.ReactNode | null;  // null = 不显示底部
  onClose?:       () => void;
  onOk?:          () => void;
  children?:      React.ReactNode;
  className?:     string;
}
```

**样式特征：**
- 通过 `createPortal` 挂载到 `document.body`
- 内容区使用 SVG `clip-path: url(#animal-modal-clip)` 实现有机 blob 外形
- 背景：`rgb(247,243,223)`；内边距：`48px`
- 标题：`font-size:28px; font-weight:700; color:rgba(114,93,66,1)`
- ESC 键关闭，打开时禁止 body 滚动
- 动画：`animal-zoom-in`（scale 0.92 → 1）

```tsx
const [open, setOpen] = useState(false);

<Modal
  open={open}
  title="欢迎来到无人岛"
  onClose={() => setOpen(false)}
  onOk={() => { handleOk(); setOpen(false); }}
>
  <p>你好，旅行者！</p>
</Modal>

// 自定义底部
<Modal open={open} footer={<Button type="primary">知道了</Button>} onClose={close}>
  内容
</Modal>

// 无底部
<Modal open={open} footer={null} onClose={close}>
  纯内容展示
</Modal>
```

---

## Cursor

```tsx
import { Cursor } from 'animal-island-ui';

interface CursorProps {
  children: React.ReactNode;
}
```

将子元素区域替换为游戏风格的自定义光标（使用 `cursor-icon.png`）。通常包裹整个应用根节点：

```tsx
// main.tsx / App.tsx
<Cursor>
  <App />
</Cursor>
```

---

## Time

```tsx
import { Time } from 'animal-island-ui';

interface TimeProps {
  // 暂无外部 Props，组件内部每秒自动刷新
}
```

实时时钟，显示格式：`星期X  M月D日  HH:MM`，内部复用 `<Cursor>` 包裹。

```tsx
<Time />
```

---

## Phone

```tsx
import { Phone } from 'animal-island-ui';

interface PhoneProps {
  // 暂无外部 Props
}
```

模拟动森 NookPhone 手机界面，包含：
- 实时时钟
- 9 个 App 图标网格（全为内置 SVG）
- 小红点通知徽标

```tsx
<Phone />
```

---

## Divider

```tsx
import { Divider } from 'animal-island-ui';

interface DividerProps {
  className?: string;
  style?:     React.CSSProperties;
}
```

带图片装饰的分割线，使用内置 `divider_line.png`：

```tsx
<Divider />
<Divider style={{ margin: '24px 0' }} />
```
