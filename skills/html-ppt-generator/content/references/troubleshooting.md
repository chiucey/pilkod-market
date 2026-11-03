---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100dd27b139f00f24a5f77fae2fc434237e3ca4e028d638bfc0783059b1dde4a27d02203c3ff980294648f0dcdcbd686f9c98b3de810f75d27eef8ed68b17234cd7c927
    ReservedCode2: 3046022100a7fe37981f57ef835cd37d33e6f64be12888bed3a66e3d4eea1ad6b12bdecac4022100fc7f47d375f0a2aaf025471afd0c03b42b057200df3b0a08d4ebd2403f220640
---

# 汇报人故障排除指南 · Troubleshooting for Presenters

> 本指南专为PPT汇报人编写，解决"代码看不懂、问题不会查"的困境。用通俗语言描述问题，用截图引导排查。

---

## 目录

1. [样式不显示怎么办](#1-样式不显示怎么办)
2. [图片不显示怎么办](#2-图片不显示怎么办)
3. [字体看起来怪怪的](#3-字体看起来怪怪的)
4. [动画效果不流畅](#4-动画效果不流畅)
5. [颜色和预期不一样](#5-颜色和预期不一样)
6. [打印出来效果差](#6-打印出来效果差)
7. [手机上显示不正常](#7-手机上显示不正常)
8. [常见术语解释](#8-常见术语解释)

---

## 1. 样式不显示怎么办

### 症状表现
- 标题变成了默认字体，不是预设的艺术字体
- 页面布局乱成一团，文字挤在一起
- 原本应该是红色的标题变成了黑色

### 快速排查（3步）

**Step 1: 检查文件名**

打开你的PPT文件，确认存在这两个文件：
```
你的项目/
├── index.html          ← PPT主文件
└── assets/
    └── template.html   ← 模板文件（必须存在！）
```

> **如果没有template.html？** 说明模板文件没有被复制进来。请从原始skill目录复制`assets/template.html`到你的项目`assets/`文件夹。

**Step 2: 检查路径引用**

在浏览器中打开index.html，按`F12`打开开发者工具，切换到`Console`（控制台）标签页。

如果看到类似下面的错误：
```
Failed to load resource: the server responded with a status of 404
```

说明模板文件路径不对。请检查index.html中是否有类似这样的代码：
```html
<link rel="stylesheet" href="assets/template.css">
```

改成：
```html
<link rel="stylesheet" href="assets/template.html">
```

**Step 3: 检查类名拼写**

开发者工具中，点击左上角的"选择元素"按钮（或者按`Ctrl+Shift+C`），然后点击页面中样式丢失的元素。

在右侧"Styles"面板中，检查是否有以下划线的样式：
- ~~删除线样式~~ = 这个CSS规则被忽略了
- 灰色文字 = CSS变量没有定义

---

## 2. 图片不显示怎么办

### 症状表现
- 图片位置显示一个破图图标
- 图片区域是空白
- 控制台显示404错误

### 快速排查

**Step 1: 检查图片文件位置**

确认图片文件在正确的文件夹中：
```
你的项目/
├── index.html
└── assets/
    ├── template.html
    ├── 图片1.png    ← 图片在这里
    └── 图片2.jpg
```

**Step 2: 检查路径写法**

HTML中的图片路径必须是**相对路径**，不能是绝对路径：

```html
<!-- ✅ 正确写法 -->
<img src="assets/图片.png" alt="">

<!-- ❌ 错误写法 -->
<img src="/assets/图片.png" alt="">   <!-- 开头的斜杠会出问题 -->
<img src="C:/Users/.../图片.png" alt="">  <!-- 绝对路径无法分享 -->
```

**Step 3: 检查文件名**

Windows系统文件名区分大小写！
- `图片.png` 和 `图片.PNG` 是不同的文件
- `logo.png` 和 `Logo.png` 也是不同的文件

---

## 3. 字体看起来怪怪的

### 症状表现
- 文字显示为宋体/微软雅黑，而不是预设的衬线字体
- 中英文混排时字体风格不统一
- 某些生僻字显示为方块

### 原因说明

HTML PPT依赖Google Fonts加载中文字体。如果网络无法访问Google（国内常见），字体加载会失败。

### 解决方案

**方案A: 使用系统自带字体（推荐）**

在template.html中，将字体回退设置为系统已有的字体：
```css
font-family: 'Noto Serif SC', 'Source Han Serif SC', 'SimSun', serif;
/*                              ↑                ↑        ↑
   Google字体(可能加载失败)    系统回退1       系统回退2  */
```

**方案B: 下载字体文件到本地**

1. 下载思源宋体、Noto Sans等字体文件（.ttf或.otf格式）
2. 放到`assets/fonts/`文件夹
3. 在HTML中引用本地字体：
```css
@font-face {
  font-family: 'MyChineseFont';
  src: url('assets/fonts/NotoSerifSC-Regular.otf');
}
```

---

## 4. 动画效果不流畅

### 症状表现
- 翻页时动画卡顿
- 元素出现时有明显的延迟
- 电脑风扇狂转

### 优化建议

**方法1: 减少动画元素**

删除不需要动画的元素上的`data-anim`属性：
```html
<!-- 有动画（逐级淡入） -->
<div data-anim>内容</div>

<!-- 无动画（直接显示） -->
<div>内容</div>
```

**方法2: 关闭浏览器硬件加速**

Chrome地址栏输入：`chrome://settings/`
找到"使用硬件加速模式"选项，关闭后刷新页面。

**方法3: 降低动画复杂度**

在template.html中调整动画参数：
```css
[data-anim] {
  animation-duration: 0.3s;  /* 原来是0.6s，改小更流畅 */
}
```

---

## 5. 颜色和预期不一样

### 症状表现
- 选了"政务庄重"主题，但颜色不是预期的中国红
- 深色模式下文字看不清楚
- 强调色不突出

### 快速修复

**Step 1: 确认主题色变量**

检查template.html中`:root`部分的变量定义：
```css
:root {
  --accent: #C41E3A;  /* 政务庄重主题应该是这个红色 */
  /* ... */
}
```

**Step 2: 清除浏览器缓存**

Ctrl+Shift+Delete（Windows）或 Cmd+Shift+Delete（Mac），清除缓存后刷新。

**Step 3: 检查是否有覆盖样式**

在开发者工具中搜索`--accent`，看是否有其他地方修改了这个值。

---

## 6. 打印出来效果差

### 症状表现
- 深色背景打印出来一片黑
- 某些元素被截断
- 页眉页脚位置不对

### 优化指南

**Step 1: 使用浅色背景**

深色主题（`data-theme="dark"`）不适合打印。在需要打印的页面，将背景改为白色：
```html
<section class="slide" data-theme="light">  <!-- 改成light -->
  ...
</section>
```

**Step 2: 调整打印设置**

浏览器打印设置中：
- 勾选"背景图形"（打印背景色）
- 选择"横向"（适合宽屏PPT）
- 边距选择"最小"

**Step 3: 添加打印样式（可选）**

在HTML中添加打印专用样式：
```css
@media print {
  .slide {
    page-break-after: always;
    height: auto;
  }
}
```

---

## 7. 手机上显示不正常

### 症状表现
- 内容溢出屏幕
- 文字太小无法阅读
- 图片变形

### 优化建议

HTML PPT是响应式设计的，但复杂布局在手机上会简化。

**建议1: 使用手机预览**

生成PPT后，用手机浏览器打开链接测试效果。

**建议2: 简化手机布局**

对于手机用户，可以隐藏某些复杂元素：
```css
@media (max-width: 768px) {
  .arch-verticals { display: none; }  /* 手机上隐藏三纵 */
}
```

**建议3: 建议使用电脑演示**

复杂政务汇报PPT，建议使用电脑或大屏幕投影展示，不适合手机浏览。

---

## 8. 常见术语解释

### CSS相关

| 术语 | 通俗解释 |
|------|----------|
| CSS变量 | 一个可以重复使用的"颜色/尺寸代号"，改一处全局生效 |
| 类名（Class） | HTML元素的"名字"，用来告诉CSS"这坨内容用什么样式" |
| 选择器 | CSS规则前面的`h1`、`.class`、`#id`等，用来指定对谁生效 |

### 文件相关

| 术语 | 通俗解释 |
|------|----------|
| index.html | PPT的主文件，双击打开就是这个 |
| template.html | 模板文件，包含所有样式定义 |
| 相对路径 | `assets/图片.png`这样的写法，相对于当前文件的位置 |
| 绝对路径 | `C:/Users/...`或`/Users/...`这样的写法，固定从根目录开始 |

### 浏览器相关

| 术语 | 通俗解释 |
|------|----------|
| 开发者工具 | 按F12打开的"后台"，可以看到代码和错误 |
| Console控制台 | 开发者工具里的一个标签，显示错误信息 |
| 404错误 | 服务器找不到这个文件，检查路径是否正确 |
| 缓存 | 浏览器保存的临时文件，有时需要清除才能看到更新 |

---

## 求助清单

如果以上方法都不能解决你的问题，准备以下信息求助：

1. **问题描述**：具体是哪个页面、哪个元素出问题了
2. **截图**：问题页面的截图
3. **错误信息**：开发者工具Console中的错误文字
4. **浏览器版本**：Chrome多少版本（地址栏输入`chrome://version`查看）

---

## 下一步

- 查看 [checklist.md](./checklist.md) 了解交付前的检查项
- 查看 [themes.md](./themes.md) 了解7套主题色的具体效果
- 查看 [layouts.md](./layouts.md) 了解18种页面布局

**祝你汇报顺利！**
