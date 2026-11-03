---
name: text-to-whiteboard
description: "Convert structured text (Markdown/notes/articles) into Excalidraw whiteboard diagrams. Creates flowcharts, comparison charts, classification cards, and knowledge maps with a professional 4-color design system. Use this skill when the user wants to visualize content as a whiteboard/diagram - including phrases like「做成白板」「转成白板」「可视化」「画成图」「做成流程图」「整理成图」「excalidraw」or needs to turn text into visual format for sharing/presentations. Do NOT use for: UML/ER diagrams, data charts (bar/line charts), Gantt charts, SVG generation, or file format conversion (PDF/Word/HTML)."
---

# Text to Whiteboard

将结构化文本转为精美的 Excalidraw 白板图。

---

## Quick Start

```
用户: "把这篇文章做成白板"
用户: "可视化这个流程"
用户: "转成知识图谱"
```

**默认行为**：使用 Jianing Fav 主题，无品牌水印，输出到 `~/Desktop/output.excalidraw`

---

## Two Modes

### Simple Mode（简洁模式）
**触发词**: `/simple`, "简洁版", "极简版", "演讲用", "演讲"

- 黑白文字为主，适合演讲/演示
- 仅用 Mist Blue/Pink 点缀
- 使用 `scripts/make_simple_board.py` 模板

### Full Visualization（完整可视化，默认）
- 四色多模块系统（蓝/绿/黄/玫瑰红）
- 专业图表（流程图、概念图、对比图）
- 使用 `scripts/make_board.py` 模板

### Mode Selection

| 条件 | 模式 |
|------|------|
| 内容 < 300 字 | Simple |
| 用户说"演讲"/"presentation" | Simple |
| 内容有 3+ 详细章节 | Full |
| 流程/对比/分类内容 | Full |
| 不确定 | Full（默认） |

---

## Interactive Flow

### 入口：选择模式

每次启动时，先问用户：

```
你想怎样开始？
1. 快捷模式 - 使用你的默认设置，直接生成
2. 按步骤来 - 首次体验推荐，一步步选择
```

---

### 快捷模式（Fast Mode）

使用用户保存的默认设置，直接生成：

| 设置项 | 有保存偏好 | 无保存偏好（回退）|
|--------|-----------|------------------|
| 可视化模式 | 用户保存的值 | `auto`（自动检测）|
| 配色主题 | 用户保存的值 | `Jianing Fav` |
| 品牌 | 用户保存的值 | `null`（无署名）|

**偏好文件**: `config/user_preferences.json`（首次使用可能不存在，会自动使用回退值）

**触发词**: "快捷", "快速", "直接做", "fast", "quick", "不要问"

---

### 按步骤模式（Step-by-Step）

#### Step 1: 获取内容

```
今天你想把什么内容做成白板？
- 粘贴文本/Markdown
- 告诉我文件路径
```

#### Step 2: 选择可视化模式

```
你想要哪种可视化风格？

1. 完整可视化 - 四色多模块，适合复杂内容、知识图谱
2. 简洁模式 - 黑白为主，适合演讲、演示
3. 让 AI 判断 - 根据内容自动选择
```

#### Step 3: 选择配色（仅当选择"完整可视化"或 AI 判断为完整可视化时）

```
选择配色方案：

1. 浏览预设主题 - 打开主题预览页，从 8 个主题中选择
2. 自定义风格 - 上传图片/VI文档，提取配色
3. 没想法 - 使用默认 Jianing Fav 主题
```

**预设主题**：
| # | 主题名 | 风格 |
|---|--------|------|
| 1 | Jianing Fav | 蓝/绿/黄/玫瑰四色（默认）|
| 2 | Professional Blue | 专业蓝色系 |
| 3 | Finance Graph | 绿红对比，适合数据 |
| 4 | Minimal Pitch | 黑白极简，适合路演 |
| 5 | Soft Pastel | 柔和粉彩，适合教育 |
| 6 | Paper & Ink | 米白+朱红，书香风格 |
| 7 | Vintage Editorial | 复古编辑风 |
| 8 | Dark Mode | 深色背景+亮色点缀 |

#### Step 4: 品牌（可选）

```
需要添加署名吗？
- 输入你的名字/品牌名
- 或跳过（无署名）
```

---

### 结束时：更新快捷模式默认值

生成完成后，询问：

```
白板已生成！✅

要不要保存这次的选择作为你的快捷模式默认值？
- 保存 - 下次选"快捷模式"时直接用这些设置
- 不保存 - 保持原来的默认值
```

**用户可保存的偏好**：
- 可视化模式：完整/简洁/自动检测
- 配色主题：选中的主题名称
- 品牌署名：用户的名字/品牌

---

### 用户偏好存储

用户保存的快捷模式偏好存放在：
```
config/user_preferences.json
```

格式：
```json
{
  "fast_mode_defaults": {
    "visualization_mode": "full",  // "full" | "simple" | "auto"
    "theme": "Jianing Fav",
    "branding": "by 小明"
  }
}
```

---

## Color System (Jianing Fav)

详细配色见 `config/themes.json`，核心规则：

| 模块 | 浅底 | 深字 |
|------|------|------|
| 蓝 | #DDE7ED | #3D6A82 |
| 绿 | #E2EDDF | #3A6B42 |
| 黄 | #F5F0DC | #7A6020 |
| 玫瑰 | #F2E8E6 | #8F3F3A |

**Canvas & Text**: `C0=#F4F7F9`, `INK=#1E2A30`, `GOLD=#B8882A`

**核心规则**:
1. 全浅色背景，深色只用于文字/线条
2. 卡片内不混色
3. 标题默认黑色，强化板块才用彩色
4. 3+ 卡片用多色，1-2 卡片用蓝色系
5. **画布背景必须为白色**: `viewBackgroundColor: "#FFFFFF"`

---

## Canvas Background

**必须设置**: `appState.viewBackgroundColor` = `"#FFFFFF"` (纯白)

不要使用 C0 或其他浅色作为画布背景。

---

## Diagram Types

| 内容类型 | 图表形式 |
|----------|----------|
| 步骤/流程 | 横向卡片 + 箭头 |
| 理论/分类 (3-4项) | 横向多色卡片 |
| 对比 (2组) | 左右双栏 + 中间箭头 |
| 模块列表 (4项) | 2x2 四色网格 |
| 要点/警告 | 全宽纵向卡片（交替底色）|
| 结语/强调 | 白底 + 金色文字 |

---

## Element Functions (Python)

```python
el_rect(x, y, w, h, bg, stroke, sw, r)   # 圆角矩形
el_text(x, y, text, size, color, w, align)  # 文字
el_arrow(x1, y1, x2, y2, color, sw)      # 箭头
el_line(x, y, w, color, sw)              # 水平分隔线
```

**Critical Notes**:
1. 文字颜色用 `strokeColor`，不是 `color`
2. 必须设置 `width` 和 `height`，否则截断
3. 垂直线用 `el_rect(x, y, 4, height, color, color, 0, 2)`，不用 `el_line`

---

## SOP

1. **解析内容** - 提取标题、章节、要点，删除过渡段落
2. **匹配图表** - 根据内容类型选择图表形式
3. **编写脚本** - 基于 `scripts/make_board.py` 或 `make_simple_board.py`
4. **运行输出** - `python3 script.py --output ~/Desktop/output.excalidraw`
5. **打开查看** - excalidraw.com → Menu → Open

---

## Gotchas

| 问题 | 原因 | 解决 |
|------|------|------|
| 中文引号报错 | `"` 与 Python 冲突 | 用 `「」` 或单独变量 |
| 文字不显示 | 用了 `color` 字段 | 用 `strokeColor` |
| 文字截断 | `width` 太小或估算不准 | 用 `estimate_text_width(text, size)` 函数 |
| 元素不渲染 | 缺少必需字段 | 复制模板完整结构 |
| 垂直线无效 | `el_line` 只支持水平 | 用 `el_rect` 代替 |
| 文字超出卡片 | 宽度估算不准或卡片太小 | 运行 `check_bounds()` 检查 |
| 画布背景不是白色 | `viewBackgroundColor` 设置错误 | 必须设为 `"#FFFFFF"` |
| 多行卡片不对齐 | 每行起始 x 或宽度不一致 | 运行 `check_alignment()` 检查，统一使用 `PAGE_X` 作为起始位置 |

---

## Text Width Estimation

中英文混排时，使用 `estimate_text_width()` 函数：

```python
def estimate_text_width(text, size):
    """估算文字渲染宽度，中英文混排友好"""
    width = 0
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 中文
            width += size * 0.95
        elif char.isupper():  # 大写英文
            width += size * 0.65
        else:  # 小写/数字/符号
            width += size * 0.45
    return max(int(width), 80)
```

---

## Bounds Checking (Required)

输出前**必须**运行边界检查：

```python
def check_bounds(elements):
    """检查文字是否超出卡片边界"""
    # 收集大卡片（排除装饰性细矩形）
    rects = [e for e in elements if e["type"] == "rectangle" and e["width"] > 100 and e["height"] > 40]
    # ... 检查逻辑
```

**使用方式**：在 `json.dump()` 之前调用 `check_bounds(elements)`

---

## Alignment Checking (Required)

检查多行卡片是否左右对齐：

```python
def check_alignment(elements, tolerance=8):
    """检查卡片是否左右对齐"""
    # 收集大卡片，按 y 坐标分组成行
    # 检查每行的左边界和右边界是否一致
    # tolerance=8px 容差
```

**使用方式**：在 `json.dump()` 之前调用 `check_alignment(elements)`

**对齐原则**：
- 同一页面多行卡片时，所有行的左边界应该对齐
- 所有行的右边界应该对齐
- 容差 8px（小于这个差距不报错）

---

## Branding

**位置选项**:
- 底部居中（默认）: `────── by Name ──────`
- 底部右侧: 角落小水印
- 顶部右侧: Logo/品牌名
- 隐藏: 不添加任何品牌标识

**格式**: 签名文字 + 手写字体 (fontFamily: 3) + 装饰线

---

## File Structure

```
text-to-whiteboard/
├── SKILL.md
├── config/themes.json      # 8 个预设主题配色
├── scripts/
│   ├── make_board.py       # 完整模式模板
│   └── make_simple_board.py # 简洁模式模板
├── assets/
│   └── themes_preview.html # 主题预览页
└── examples/
    └── input/              # 示例输入文件
```

---

## Output

- **格式**: `.excalidraw` JSON 文件 (10-100KB)
- **位置**: 默认 `~/Desktop/output.excalidraw`
- **打开**: excalidraw.com → Menu → Open → 选择文件

---

## Example Outputs

See `examples/outputs/` for reference images:

| Example | Style | Features |
|---------|-------|----------|
| [example-1-ai-recording-system.png](examples/outputs/example-1-ai-recording-system.png) | Full Visualization | 4-color modules, flow arrows, knowledge map |
| [example-2-brain-ceo.png](examples/outputs/example-2-brain-ceo.png) | Full Visualization | 4-color classification, layered hierarchy, section dividers |

**Design patterns shown:**
- 莫兰迪色系（蓝/绿/黄/玫瑰）区分不同模块
- 模块化卡片 + 圆角设计
- 浅底深字，对比清晰
- 分隔线/箭头引导阅读流
- 标题层级分明（大标题→板块标题→正文）

---

## Version

Current: 2.3.0
Updated: 2026-04-07

**v2.3.0 Changes**:
- Added `check_alignment()` for multi-row card alignment checking
- Updated Gotchas table with alignment issue

**v2.2.0 Changes**:
- Added `estimate_text_width()` for accurate Chinese/English text width
- Added `check_bounds()` function for boundary validation before output
- Enforced white canvas background (`#FFFFFF`)
- Updated Gotchas table with new common issues
