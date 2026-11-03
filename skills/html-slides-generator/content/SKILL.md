---
name: html-slides-generator
description: 创建精美的零依赖、动画丰富的 HTML 幻灯片演示文稿。当用户想要构建演示文稿、将 PPT/PPTX 转换为网页格式、创建演讲幻灯片、制作 pitch deck 或需要网页版幻灯片时使用。帮助非设计师通过视觉探索而非抽象描述来发现美学风格。
---

# HTML Slides Generator

创建零依赖、动画丰富的 HTML 演示文稿，可在任何浏览器中运行。

## 核心原则

1. **零依赖** — 单个 HTML 文件，内联 CSS/JS。无需 npm，无需构建工具。
2. **展示而非描述** — 生成视觉预览，而非抽象选择。用户通过实际看到来发现需求。
3. **独特设计** — 避免通用"AI 风格"。每个演示文稿都应感觉是量身定制的。
4. **视口适配（非协商性）** — 每个幻灯片必须精确适配 100vh。幻灯片内禁止滚动。内容溢出？拆分为多个幻灯片。

## 设计美学

避免通用"AI 风格"输出，专注于：

- **排版**：选择美观、独特、有趣的字体。避免 Arial、Inter 等通用字体。
- **色彩与主题**：坚持统一的审美。使用 CSS 变量保证一致性。醒目色彩搭配锐利强调色。
- **动效**：使用动画实现效果和微交互。优先使用纯 CSS 方案。
- **背景**：创造氛围和深度，而非默认纯色。叠加 CSS 渐变，使用几何图案。

**避免的通用模式**：
- Inter、Roboto、Arial 等常见字体
- 白色背景上的紫色渐变
- 居中一切、通用英雄区域

---

## 模式检测（第 0 阶段）

确定用户需求：

- **模式 A：从头创建** — Go to Phase 1
- **模式 B：PPT 转换** — 转换 .pptx 文件，Go to Phase 4
- **模式 C：增强改进** — 改进现有 HTML 演示文稿，读取理解后增强

### 模式 C：修改规则

增强现有演示文稿时，风险最大的是视口适配：

1. **添加内容前**：计算现有元素，检查内容密度限制
2. **添加图片**：必须设置 `max-height: min(50vh, 400px)`。如果幻灯片已满内容，先拆分
3. **添加文本**：每页最多 4-6 个要点。超出限制？拆分为续页
4. **修改后验证**：`.slide` 有 `overflow: hidden`，新元素使用 `clamp()`，图片有视口相对 max-height
5. **主动重组**：如果修改会导致溢出，自动拆分内容并告知用户

---

## 阶段 1：内容收集（新建演示文稿）

### Step 1.1：关键信息收集

使用 `genui-form-wizard` 一次性收集所有信息：

**页面 1 - 用途（单选）**：
- Pitch deck（融资路演）
- Teaching-Tutorial（教学教程）
- Conference talk（会议演讲）
- Internal presentation（内部演示）

**页面 2 - 长度（单选）**：
- 简短 5-10 页
- 中等 10-20 页
- 较长 20+ 页

**页面 3 - 内容状态（单选）**：
- 所有内容已准备
- 粗略笔记
- 仅主题/想法

**页面 4 - 内联编辑（单选）**：
- "是（推荐）" — 可在浏览器中直接编辑文本，自动保存到 localStorage
- "否" — 仅生成演示文稿，文件更小

**页面 5 - 图片（多选）**：
- 有图片（用户稍后提供）
- 无图片（使用 CSS 生成视觉元素）

### Step 1.2：图片评估（如提供图片）

如果用户提供了图片文件夹：

1. **扫描** — 列出所有图片文件
2. **查看** — 使用 `mcp__matrix__images_understand` 分析每张图片
3. **评估** — 判断：展示内容、是否可用、代表什么概念、主导色彩
4. **共同设计大纲** — 结合文本和图片设计幻灯片结构
5. **确认** — 展示幻灯片大纲供用户确认

---

## 阶段 2：风格发现

### Step 2.0：选择路径

**选项 A："给我看选项"（推荐）** — 基于心情生成 3 个预览
**选项 B："我知道我要什么"** — 直接从预设列表选择

### Step 2.1：心情选择（引导式发现）

**单选心情（最多 2 项）**：
- Impressed/Confident — 专业、可信赖
- Excited/Energized — 创新、大胆
- Calm/Focused — 清晰、专注
- Inspired/Moved — 情感、打动人心

### Step 2.2：生成 3 个风格预览

基于心情，从 [STYLE_PRESETS.md](references/style-presets.md) 选择 3 个独特的预设，生成 3 个单页 HTML 预览。

| 心情 | 建议预设 |
| --- | --- |
| Impressed/Confident | Bold Signal, Electric Studio, Dark Botanical |
| Excited/Energized | Creative Voltage, Neon Cyber, Split Pastel |
| Calm/Focused | Notebook Tabs, Paper & Ink, Swiss Modern |
| Inspired/Moved | Dark Botanical, Vintage Editorial, Pastel Geometry |

预览要求：
- 单页 HTML，约 50-100 行
- 展示一个动画标题幻灯片
- 包含排版、色彩、动画和整体美学

### Step 2.3：用户选择

让用户选择最喜欢的预览，或选择"混搭元素"。

---

## 阶段 3：生成演示文稿

使用阶段 1 的内容和阶段 2 选定的风格生成完整演示文稿。

### 生成要求

- 单个自包含 HTML 文件，所有 CSS/JS 内联
- 读取并包含 [viewport-base.css](references/viewport-base.css) 完整内容
- 每个幻灯片为 `<section class="slide">`
- 使用 CSS scroll snap 导航
- 使用 CSS keyframes 生成所有动画
- 构建完成后部署或提供给用户

### 幻灯片内容密度限制

| 幻灯片类型 | 最大内容 |
| --- | --- |
| 标题幻灯片 | 1 标题 + 1 副标题 + 可选标语 |
| 内容幻灯片 | 1 标题 + 4-6 要点 或 1 标题 + 2 段落 |
| 特性网格 | 1 标题 + 最多 6 张卡片 |
| 代码幻灯片 | 1 标题 + 8-10 行代码 |
| 引言幻灯片 | 1 引言（最多 3 行）+ 署名 |
| 图片幻灯片 | 1 标题 + 1 图片（最大 60vh） |

**内容超出限制？拆分为多个幻灯片。永不堆砌，永不滚动。**

### 必需 JavaScript 功能

每个演示文稿必须包含：

1. **SlidePresentation 类**：
   - 键盘导航（方向键、空格、Page Up/Down）
   - 触摸/滑动支持
   - 鼠标滚轮导航
   - 进度条更新
   - 导航点

2. **Intersection Observer** — 滚动触发动画，添加 `.visible` 类

3. **可选增强**（匹配选定风格）：
   - 自定义光标轨迹
   - 粒子背景（canvas）
   - 视差效果
   - 悬停 3D 倾斜
   - 磁性按钮
   - 计数器动画

4. **内联编辑**（仅当用户在阶段 1 选择"是"时）：
   - 编辑切换按钮
   - 自动保存到 localStorage
   - 导出/保存文件功能

---

## 阶段 4：PPT 转换

### 依赖要求

需要 Python 环境安装 `python-pptx` 和 `Pillow`：
```bash
pip install python-pptx Pillow
```

### 转换流程

1. **读取 PPT 文件** — 提取所有文本、图片和备注
2. **展示提取内容** — 供用户确认
3. **风格选择** — 让用户选择视觉风格
4. **生成 HTML** — 使用原始素材创建网页演示文稿

### 图片处理

| 情况 | 处理方式 |
| --- | --- |
| 方形 Logo | 圆形裁剪 `crop_circle()` |
| 图片 > 1MB | 缩放到 `max_dim=1200` |
| 宽高比错误 | 手动裁剪 |

---

## 输出交付

生成完成后：

1. **测试验证** — 确保所有幻灯片正确显示
2. **部署**（如适用）— 使用 `deploy` 工具发布
3. **提供文件** — 将 HTML 文件交付给用户

---

## 引用文件

- [viewport-base.css](references/viewport-base.css) — 必须在每个演示文稿中包含的强制 CSS
- [style-presets.md](references/style-presets.md) — 10 种精选视觉风格预设
- [html-template.md](references/html-template.md) — HTML 架构和 JS 功能参考
- [animation-patterns.md](references/animation-patterns.md) — 动画效果参考

