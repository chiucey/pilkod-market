---
name: prototype-iter
description: |
  基于参考图做移动端 ToB 工作台原型的局部迭代（增/删/改字段、组件、区块、提示文案）。
  强约束：颜色、字体、组件样式、栅格、间距严格保持与参考图一致。
  默认方案：HTML+CSS 代码生成（推荐，pixel-perfect）。
  备选方案：image_synthesize 图生图（用于概念稿/草图，不保证像素级一致）。
  触发：用户提供一张或多张参考图（PNG/JPG）并描述要改什么，例如"在第 X 个表单后加一个备注字段"、"把查询按钮从蓝色改成实心圆角"等。
  不适用：自由创意生成、整页重做、跨视觉体系（不同 App 风格）改版。
---

# Prototype Iter — 局部微调型原型迭代

## 核心理念

**不重绘，只改用户指定的部分。** 其他区域必须与参考图视觉完全一致：颜色、字号、圆角、间距、组件样式、栅格、状态栏、导航栏都按参考图克隆。

**首选方案**：HTML + CSS 代码生成（`write` 工具）。代码即真理——CSS 锁死颜色/字体/间距，HTML 结构锁死元素位置。可以做到像素级一致，且改版只需改几行代码。

**备选方案**：`image_synthesize` 图生图。优势是出图快、不需要写代码；劣势是每次跑都有随机性，无法保证像素级一致（出现 6 个区块变 5 个、标题冒出"NEW"、画布比例偏移等问题）。

---

## 工作流

### Step 1. 接收输入
- 用户上传**至少一张**参考图（PNG/JPG）
- 用户用自然语言描述**修改点**（必填）

> 修改点描述必须包含三要素：位置 + 对象 + 动作
> - ✅ "在'业务受理信息'区块下方新增一个'宽带增值产品'折叠区块，样式与其他折叠区块一致"
> - ✅ "把'附加套餐'Tab 文字改为'增值产品'"
> - ❌ "加个字段"（太模糊，模型/AI 会自由发挥）

如果用户描述太模糊，反问一次要求补全这三要素，不要自己脑补。

### Step 2. 选择方案

**默认走 HTML 方案**（除非用户明确说"用图生图"或"快速出图"）：

| 方案 | 适用场景 | 质量 | 速度 |
|------|---------|------|------|
| **HTML+CSS 代码生成（推荐）** | 追求像素级一致、改版频繁 | 100% | 几分钟写代码，秒级出图 |
| **image_synthesize 图生图** | 概念稿、不需要改版迭代 | 85% 相似 | 几秒一张，但要反复抽卡 |

### Step 3. 加载设计规范
从本 skill 的 `references/design-spec.md` 读取规范。**绝对不能漏。**

### Step 4. 实现

#### 方案 A：HTML 代码生成
参考 `references/html-template.html`，按以下步骤：
1. 复制模板为基础
2. 替换内容（区块标题、字段标签等）
3. 应用修改（新增区块、改 Tab 文字等）
4. 用 `website_deploy` 部署到公网链接给用户预览

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    :root {
      --primary-blue: #3B7CFF;
      --primary-blue-dark: #1A5FE0;
      --danger-red: #E53935;
      --bg-page: #F5F7FA;
      --bg-card: #FFFFFF;
      --border-light: #ECECEC;
      --text-primary: #333333;
      --text-placeholder: #B5B5B5;
    }
    /* ... 详见 references/design-spec.md 第三节"组件 HTML 实现" ... */
  </style>
</head>
<body>
  <div class="phone"><!-- 状态栏 + 导航 + 区块 --></div>
</body>
</html>
```

#### 方案 B：image_synthesize 图生图
详见下文"图生图 Prompt 模板"。

### Step 5. 验证与迭代
- HTML 方案：浏览器打开看效果，根据反馈改 CSS
- 图生图：对比生成图与参考图，按"失败模式与处理"调 prompt

### Step 6. 沉淀经验（方案 B：自动问）
每次改版完成且用户满意后，**主动问一次**：
> "这次改版有 [N] 个新经验值得沉淀到 skill（参数/易错点/新组件），要沉淀吗？"

如果用户说"沉淀"，把这次的新经验追加到 `references/design-spec.md`：
- 新的设计 token 或 CSS 变量 → 加到第 1 节
- 新的组件样式 → 加到第 3 节（每个组件都有 HTML+CSS 实现）
- 用户纠正的"易错点" → 加到第 6 节

不打断用户但保留选择权——如果改版很小或重复已知模式，不主动问。

---

## HTML 方案工作流（推荐）

### 基础结构
1. 创建 `/workspace/prototype-iter/html-output/<page>.html`
2. 在 HTML 里使用 `:root` CSS 变量定义设计 token
3. 使用 `.phone` 容器（390px 宽）模拟移动端
4. 用 `website_deploy` 部署到公网链接

### 关键 HTML 模式

**折叠区块（关键 - 很多原型会做错）**：
```html
<!-- 折叠状态：只显示标题区，无 section-content -->
<div class="section collapsed">
  <div class="section-title">
    <div class="text">区块标题</div>
    <svg class="arrow"><!-- 上箭头 ∨ 表示"展开"，旋转 180° 表示"折叠" --></svg>
  </div>
</div>

<!-- 展开状态：显示标题区 + section-content -->
<div class="section expanded">
  <div class="section-title">...</div>
  <div class="section-content">
    <!-- 字段行 -->
  </div>
</div>
```

**注意**：原图里所有 6 个区块标题右侧都是**向上箭头（∧）**——即使折叠状态的"我的附加套餐"等也是向上箭头，**不是向下箭头**。这是这个 App 的视觉约定。

**字段行（注意：很多字段是"纯文字 + 1px 灰线"，不是 input）**：
```html
<!-- 有 input 的字段（仅证件类型/促销员/推荐人 等少量字段） -->
<div class="field-row">
  <div class="label"><span class="required">*</span>字段名：</div>
  <div class="value-wrap">
    <input type="text" placeholder="...">
  </div>
</div>

<!-- 无 input 的字段（证件号码/姓名等） -->
<div class="field-row">
  <div class="label"><span class="required">*</span>字段名：</div>
  <div class="value-wrap"></div>
</div>

<!-- 带搜索图标的字段（促销员/推荐人） -->
<div class="field-row">
  <div class="label">字段名：</div>
  <div class="value-wrap">
    <span class="placeholder-text">请点击右侧图片进行查询</span>
    <svg class="search-icon"><!-- 圆圈+斜把手 --></svg>
  </div>
</div>
```

**搜索区（关键 - 不用 input）**：
```html
<div class="search-area">
  <div class="input-line">
    <div class="placeholder">请输入服务号码或宽带账号</div>
    <div class="line"></div>
  </div>
  <div class="query-line">
    <div class="input-line">
      <div class="placeholder">请输入服务密码或宽带密码</div>
      <div class="line"></div>
    </div>
    <button class="query-btn">查询</button>
  </div>
</div>
```

**mini-select 选择器（圆角椭圆）**：
```html
<div class="mini-select">
  <span>请选择</span>
  <span class="arrow-down">⌄</span>
</div>
```

**搜索图标 SVG**：
```html
<svg viewBox="0 0 24 24" fill="none" stroke="#3B7CFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="10" cy="10" r="6"/>
  <line x1="20" y1="20" x2="14.5" y2="14.5"/>
</svg>
```

---

## 图生图方案 Prompt 模板（备选）

> ⚠️ 图生图方案已知问题：每次跑结果有随机性，可能出现"区块被省略"、"画布比例偏移"、"标题文字变形"、"冒出未要求文字"等问题。**关键场景（必须像素级一致）请用 HTML 方案。**

### 基础模板
```
保持参考图的视觉风格完全不变：
- 主色蓝 #3B7CFF（导航栏、主按钮、勾选）
- 浅灰区块背景 #F5F7FA
- 主文字 #333333，次文字 #999999
- 思源黑体/无衬线字体
- 区块标题左侧 3-4px 蓝色竖线
- 圆角按钮 4-6px，输入框 4px
- 状态栏+蓝色导航栏+白色内容区

【仅修改】
- 在 <具体位置> 的 <原对象> 后/前/中，<具体动作> 一个 <新对象>
- 新对象的样式与同区域其他同类对象一致

【严格禁止】
- 任何颜色、字体、间距的变化
- 添加未要求的新元素
- 改变现有文字内容（除显式要求改的）
- 改变现有组件位置
- 画布比例变化（保持原图比例）
- 省略参考图中的任何区块
- 在空白字段添加占位符
- 在区块标题末尾添加"NEW"等额外文字

参考图：<参考图描述>
```

---

## 常见修改场景速查

| 场景 | HTML 方案实现 | 图生图 prompt 描述 |
|------|--------------|-------------------|
| 新增折叠区块 | 复制 `<div class="section collapsed">` 模板 | "在 X 区块下方新增一个'Y'折叠区块，标题区样式完全一致" |
| 新增字段 | 在对应区块的 section-content 里加 field-row | "在 X 区块的 Z 字段后新增一个字段，标签'W'，占位符'...'" |
| 改 Tab 文字 | 改 `<div class="tab">` 里的文字 | "把第 N 个 Tab 文字从'A'改为'B'" |
| 改区块顺序 | HTML 里调整 `<div class="section">` 的位置 | 需重跑图生图（不推荐） |
| 字段改必填 | 在 label 里加 `<span class="required">*</span>` | "在 X 字段标签前加红色星号" |
| 改 placeholder | 改 input 的 placeholder 属性 | prompt 写明新占位符 |
| 改图标（emoji→SVG） | 替换为 SVG 代码 | prompt 写"使用蓝色描边圆形搜索图标" |

---

## 失败模式与处理

### HTML 方案的常见错误

| 失败现象 | 原因 | 处理 |
|----------|------|------|
| 折叠区块出现了"暂无附加套餐"等占位文字 | AI 误以为空字段需要提示 | **删除 section-content**，只保留 section-title |
| 字段被做成 input 框 | AI 误以为所有字段都是输入 | **只有少量字段有 input**（证件类型、促销员、推荐人），其他字段 value-wrap 为空 |
| 搜索区出现 input 框 | AI 误以为"输入"必须用 input | **搜索区用纯文字 + 1px 灰线**，不用 input |
| 字段之间没有分割线 | 漏了 border-bottom | 加 `border-bottom: 1px solid var(--border-light)` |
| 区块之间没有分割线 | 漏了 section border | 加 `border-bottom: 1px solid #D8DCE0` 到 .section |
| 字段 label 右对齐 | 默认三栏错位 | 三栏字段的 label **全部左对齐**，给数值预留空间 |
| 搜索图标用 emoji 🔍 | 偷懒 | 用 SVG 圆圈+斜把手，颜色主色蓝 |

### 图生图方案的常见错误

| 失败现象 | 原因 | 处理 |
|----------|------|------|
| 整体颜色偏移 | 模型没锁住规范 | 在 prompt 开头重复规范 + 加 "use the EXACT same color palette" |
| 出现参考图没有的元素 | 模型自由发挥 | 加 "do not introduce any new visual elements" |
| 修改点位置偏离 | 位置描述太模糊 | 用 "Y 轴约 X% 位置" + 区块名双定位 |
| 中文字变形/错误 | 图生图对中文不稳 | 改用 HTML 方案 |
| 字号/间距变化 | 模型理解偏差 | 加 "all typography, spacing, padding MUST remain identical" |
| 圆角/边框变化 | 组件细节漂移 | 加 "all corners, borders, shadows must be pixel-identical" |
| **画布比例偏移** | aspect_ratio 参数错 | 不传 aspect_ratio，让模型保持原图比例 |
| **某个区块被省略** | 模型对"保留"的理解有随机性 | 列出所有区块的完整清单（带序号），禁止合并/省略 |
| **画布被裁剪** | 输出分辨率不够 | 提高 resolution 到 2K，不传 aspect_ratio |
| **冒出"NEW"等额外文字** | 模型自作主张 | 强调"标题文字必须一字不差"、"禁止添加任何额外文字" |

---

## 边界

**不要做的事**：
- 不要让模型做整页重做（局部微调）
- 不要让模型跨视觉体系（不要拿这张图生成"小红书"风格）
- 不要在没有参考图的情况下工作
- 不要试图用图生图做精确的中文渲染（用 HTML 方案）

**输出规范**：
- HTML 方案：用 `website_deploy` 部署到公网链接
- 图生图方案：用 `<deliver-assets>` 包裹图片
- 改版响应：HTML 方案秒级出图，图生图方案需抽卡
