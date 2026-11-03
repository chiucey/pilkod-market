---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 3f999435e2d05c622178c1cdc3e0475a
    PropagateID: 3f999435e2d05c622178c1cdc3e0475a
    ReservedCode1: 30460221008ff5d1aa8869a18e881057234f4c794f0c570910cf514293facf9b930fca40f9022100aa4b82de6d2946806ed5cd7a787049a7bf145d2340219e8c7de4cf8e7d366680
    ReservedCode2: 304502210088813d5eae6d09544270cacf1f6c84cbb2179e578f913635587647bf196f971a02206e579a4354a5fb142437d2c4c4a63fe12c7b973851ba62dedcac5ca905380c0f
description: Anthropic官方PPT Skill。创建/编辑.pptx演示文稿，含markitdown读取/pptxgenjs创建/编辑模板/设计规范/视觉QA流程。需：markitdown/pptxgenjs/LibreOffice/Poppler。
github: https://github.com/anthropics/skills
license: Proprietary
name: pptx-skill
platforms:
    - Claude
    - OpenClaw
tags:
    - presentation
    - pptx
    - powerpoint
    - office
    - anthroic-official
---

# PPTX Skill · 演示文稿创建与编辑

## 快速对照

| 任务 | 工具 |
|------|------|
| 读取/提取文本 | `python -m markitdown presentation.pptx` |
| 编辑现有模板 | 解压→编辑→打包 |
| 从零创建 | pptxgenjs |

---

## 一、依赖安装

```bash
pip install "markitdown[pptx]" Pillow
npm install -g pptxgenjs
# 依赖：LibreOffice, Poppler（PDF转换）
```

---

## 二、读取内容

```bash
# 文本提取
python -m markitdown presentation.pptx

# 视觉缩略图
python scripts/thumbnail.py presentation.pptx

# 原始XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## 三、从零创建（pptxgenjs）

```javascript
const PptxGenJS = require('pptxgenjs');
let pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_16x9';
pptx.defineLayout({ name: 'CUSTOM', width: 10, height: 7.5 });
pptx.layout = 'CUSTOM';

// 配色方案（Midnight Executive示例）
const COLORS = {
  primary: '1E2761',  // 藏青
  secondary: 'CADCFC', // 冰蓝
  accent: 'FFFFFF',    // 白色
};

// 幻灯片
let slide = pptx.addSlide();
slide.addText('标题', {
  x: 0.5, y: 0.3, w: 9, h: 0.8,
  fontSize: 40, bold: true, color: COLORS.primary,
  fontFace: 'Georgia'
});
slide.addText('副标题或要点', {
  x: 0.5, y: 1.3, w: 9, h: 5,
  fontSize: 18, color: '333333',
  fontFace: 'Calibri'
});

pptx.writeFile({ fileName: 'output.pptx' });
```

---

## 四、设计规范

### 配色原则
- 一个主色占60-70%视觉权重，1-2个辅助色，1个尖锐强调色
- 不要所有颜色平分权重
- 深色背景用于标题+结尾页，浅色用于内容页（"三明治"结构）

### 字体搭配
| 标题字体 | 正文字体 |
|---------|---------|
| Georgia | Calibri |
| Trebuchet MS | Calibri |
| Palatino | Garamond |

### 字号标准
| 元素 | 字号 |
|------|------|
| 幻灯片标题 | 36-44pt bold |
| 小节标题 | 20-24pt bold |
| 正文 | 14-16pt |
| 注释 | 10-12pt muted |

### 禁止
- ❌ 纯文字幻灯片（无图片/图标/图表）
- ❌ 标题下加装饰线（AI生成的标志）
- ❌ 所有幻灯片同一布局
- ❌ 默认蓝色配色

---

## 五、视觉QA（必须！）

> ⚠️ **用Subagent做视觉检查**——你自己盯着代码看，会只看到你预期的东西，不是实际内容。

```bash
# 转图片
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide

# 用subagent检查：
# "检查这些幻灯片。查找：文字重叠/溢出/对比度低/残留占位符文字/间距不一致"
```

### 验证循环
1. 生成 → 转图 → 检查
2. 列出问题
3. 修复问题
4. **重新验证**（一次修复往往产生新问题）
5. 重复直到完整通过

---

## 六、排版规范

- 页边距：≥ 0.5"
- 内容块间距：0.3" - 0.5"
- 正文左对齐（不要居中）
- 每页需要视觉元素（图片/图标/图表/形状）

---

> 来源：https://github.com/anthropics/skills · Anthropic官方
