---
name: to-pptx
description: 将文本、文件、对话内容转换为PPT演示文稿。支持5种页面类型（封面、目录、分隔页、内容页、总结页），支持模板风格继承和多种创意布局。触发词：生成PPT、制作PPT、Word转PPT、Excel转PPT、PDF转PPT、内容转PPT、to-pptx、转PPT、生成演示文稿、帮我做PPT、创建PPT。
---

# PPTX Generator - PPT生成与编辑技能

## 概述

本技能提供完整的PPT生成和编辑能力，支持：

1. **新增PPT**：根据内容生成指定页数的演示文稿
2. **编辑PPT**：修改指定页面，其他页面保持不变
3. **多格式输入**：支持文字、Excel、PPT、Word、PDF等文件
4. **模板继承**：可选继承用户提供的PPT模板风格
5. **页面类型**：封面、目录、分隔页、内容页、总结页

## Quick Reference

| 任务 | 方法 |
|------|------|
| 新增PPT | 分析内容 → 提取要点 → 选择页面类型 → 生成指定页数 |
| 编辑PPT | 定位目标页 → 修改内容 → 保持其他页面不变 |
| 内容提取 | 文字直接分析 / 文件使用对应工具提取 |
| 模板继承 | 提取模板颜色 → 映射到主题键 → 继承风格生成 |

| 属性 | 值 |
|------|-----|
| **尺寸** | 10" x 5.625" (LAYOUT_16x9) |
| **颜色** | 6位hex无# (如 `"FF0000"`) |
| **中文字体** | Microsoft YaHei |
| **英文字体** | Arial / Georgia / Calibri |
| **页码位置** | x: 9.3", y: 5.1" |

---

## 意图识别

### 场景判断

当用户请求PPT相关操作时，首先判断意图：

| 意图 | 关键词 | 处理方式 |
|------|--------|----------|
| **新增PPT** | "生成PPT"、"制作PPT"、"新建PPT"、"帮我做一个PPT" | 进入新增流程 |
| **编辑PPT** | "编辑PPT"、"修改PPT"、"调整PPT"、"重新设计第X页" | 进入编辑流程 |
| **仅修改某页** | "第X页"、"改一下第3页"、"重新设计第5页" | 定位目标页，仅修改指定页 |

### 新增PPT流程

```
1. 理解内容 → 2. 提取核心要点 → 3. 选择页面类型 → 4. 规划页数 → 5. 生成PPT
```

### 编辑PPT流程

```
1. 定位目标页 → 2. 分析修改需求 → 3. 仅修改指定页 → 4. 保持其他页不变
```

---

## 内容提取

### 支持的文件格式

| 格式 | 工具/方法 |
|------|----------|
| 纯文字 | 直接分析对话内容 |
| Word (.docx) | `python -m markitdown file.docx` |
| PPT (.pptx) | `python -m markitdown file.pptx` |
| Excel (.xlsx) | openpyxl 读取数据 |
| PDF (.pdf) | `mcp__matrix__extract_pdfs_full_content` |
| 图片 | OCR文字识别 (如需要) |

### 提取策略

1. **结构识别**：识别标题、段落、列表、表格
2. **要点提取**：归纳3-5个核心信息点
3. **层次梳理**：主标题 → 子主题 → 支持细节
4. **数据识别**：表格数据、图表信息、关键数字

详见：[Content Extraction Guide](references/content-extraction.md)

---

## 页面类型

### 5种页面类型

| 类型 | 用途 | 必需元素 |
|------|------|----------|
| **封面** | 开场、主题引入 | 大标题、副标题、日期/机构 |
| **目录** | 内容导航 | 章节列表、页码指引 |
| **分隔页** | 章节过渡 | 章节编号、章节标题 |
| **内容页** | 核心信息展示 | 标题、要点/图表/数据 |
| **总结页** | 收尾、强化记忆 | 关键要点回顾、CTA |

### 选择建议

| 场景 | 推荐页面组合 |
|------|-------------|
| 简单汇报 | 封面 + 内容页(1-N) + 总结页 |
| 正式演讲 | 封面 + 目录 + 分隔页 + 内容页 + 总结页 |
| 培训教程 | 封面 + 目录 + (分隔页 + 内容页) x N + 总结页 |
| 方案展示 | 封面 + 目录 + 内容页(多) + 总结页 |

### 页面生成规则

- 封面：第1页，无页码徽章
- 目录：第2页（如有），带页码
- 分隔页：章节开始页，带页码
- 内容页：核心信息页，带页码
- 总结页：最后一页，带页码

详见：[Slide Types Guide](references/slide-types.md)

---

## 模板风格继承

### 关键原则（必须执行）

> **⚠️ 当用户传入模板文件时，必须先提取模板配色，再生成PPT。禁止忽略模板或使用默认配色。**

### 流程

```
用户提供模板 → 提取颜色/字体/布局 → 映射到主题键 → 内容填充 → 生成PPT
```

### 模板提取步骤

**第一步：解压PPTX文件**
```bash
unzip -o "模板.pptx" -d temp_template_extracted/
```

**第二步：读取主题配色（优先）**
读取 `ppt/theme/theme1.xml`，解析 `<a:clrScheme>` 标签：
- `dk2` → 主标题色 → `primary`
- `accent1` → 强调色 → `accent`
- `lt2` → 背景色 → `bg`

**第三步：读取实际幻灯片配色**
读取 `ppt/slides/slide*.xml`，提取 `a:srgbClr val="XXXXXX"` 中的颜色值：
- 找最大色块颜色作为背景 `bg`
- 找标题颜色作为主色 `primary`
- 找装饰/边框颜色作为辅助色 `secondary`

**第四步：映射到主题键**
```javascript
const theme = {
  primary: extractedPrimary,   // 主色调
  secondary: extractedSecondary, // 辅助色
  accent: extractedAccent,     // 强调色
  light: extractedLight,       // 浅色装饰
  bg: extractedBg              // 背景色
};
```

### 完整提取示例

```bash
# 1. 解压
unzip -o "template.pptx" -d temp_template/

# 2. 查看主题文件获取配色方案
cat temp_template/ppt/theme/theme1.xml | grep -o 'srgbClr val="[0-9A-Fa-f]*"' | head -20

# 3. 分析实际使用的颜色
grep -oh '[0-9A-Fa-f]\{6\}' temp_template/ppt/slides/*.xml | sort | uniq -c | sort -rn | head -10
```

### 无模板时

使用设计系统预设配色，从18套方案中选择适合主题的配色。

详见：[Content Extraction Guide](references/content-extraction.md)

---

## Theme Object Contract

主题对象必须包含这些**精确键名**：

| 键 | 用途 | 示例 |
|-----|------|------|
| `theme.primary` | 标题/深色文字 | `"22223b"` |
| `theme.secondary` | 正文/次要文字 | `"4a4e69"` |
| `theme.accent` | 强调/装饰色 | `"9a8c98"` |
| `theme.light` | 浅色装饰 | `"c9ada7"` |
| `theme.bg` | 背景色 | `"f2e9e4"` |

---

## 页码徽章

除封面外，所有页面**必须**包含页码徽章：

- **位置**: x: 9.3", y: 5.1"
- **格式**: 当前页码（如 `3` 或 `03`）
- **样式**: 与主题配色协调

```javascript
// 圆形徽章
slide.addShape(pres.shapes.OVAL, {
  x: 9.3, y: 5.1, w: 0.4, h: 0.4,
  fill: { color: theme.accent }
});
slide.addText("3", {
  x: 9.3, y: 5.1, w: 0.4, h: 0.4,
  fontSize: 12, fontFace: "Arial",
  color: "FFFFFF", bold: true,
  align: "center", valign: "middle"
});
```

---

## 幻灯片文件格式

每张幻灯片是一个独立的JS模块：

```javascript
// slide-01.js (封面)
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'cover',    // cover | toc | divider | content | summary
  index: 1,
  title: '演示文稿标题'
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 封面内容...

  return slide;
}

module.exports = { createSlide, slideConfig };
```

---

## 编辑现有PPT

当用户要求修改指定页面时：

1. **定位目标**：识别要修改的页面编号
2. **分析需求**：理解该页需要修改的内容
3. **仅修改目标页**：其他页面保持不变
4. **重新打包**：生成更新后的PPT

详见：[Edit Workflow Guide](references/edit-workflow.md)

---

## 输出结构

```
slides/
├── slide-01.js      # 第1页（封面）
├── slide-02.js      # 第2页（目录）
├── slide-03.js      # 第3页（内容）
├── ...
├── imgs/            # 图片资源
├── output/          # 最终输出
│   └── presentation.pptx
└── compile.js       # 编译脚本
```

---

## 依赖项

- `pip install "markitdown[pptx]"` — 文本提取
- `npm install pptxgenjs` — PPT生成
- `pip install openpyxl` — Excel读取

---

## 参考文档

| 文件 | 内容 |
|------|------|
| [slide-types.md](references/slide-types.md) | 5种页面类型详细指南 |
| [content-extraction.md](references/content-extraction.md) | 多格式内容提取 |
| [edit-workflow.md](references/edit-workflow.md) | PPT编辑工作流 |
| [design-system.md](references/design-system.md) | 配色方案和字体 |
| [pptxgenjs.md](references/pptxgenjs.md) | PptxGenJS API |
| [creative-layouts.md](references/creative-layouts.md) | 创意布局设计指南 |
