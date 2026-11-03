---
name: paper-infographic
description: 将论文内容转化为一张高信息密度的学术信息图，7个模块讲清楚研究问题、方法、实验、结果、贡献与局限。适用于知识传播、论文解读与内容平台发布。
metadata:
  version: 1.0.0
  openclaw:
    emoji: 📊
    requires: {}
---

# 论文一图拆解信息图生成器

将复杂论文压缩为一张高密度学术信息图，帮助快速讲清研究问题、方法、实验、结果与价值。

---

## 触发条件

用户发送论文标题/链接/摘要，要求生成"论文解读图"、"信息图"、"一张图讲清楚"、"论文速读图"、"小红书论文图"时激活。

---

## 工作流程

### 第 1 步：收集论文信息

**必须先向用户询问：**

1. **论文标题 / 链接 / 摘要** — 要拆解哪篇论文？
2. **目标读者** — 给谁看？（普通读者 / AI 从业者 / 学生 / 内容平台用户）
3. **侧重点偏好** —
   - 研究问题讲清楚
   - 方法结构讲清楚
   - 实验结果讲清楚
   - 贡献与启发讲清楚
   - 小红书传播风格

> ⚠️ 等待用户提供信息后，再进入下一步。

---

### 第 2 步：提取论文核心信息

从论文中提取以下内容：

- 论文标题、发表时间、作者/机构
- 研究背景 / 核心痛点
- 方法框架 / 核心创新
- 实验设置 / 数据集 / 对比方法
- 关键结果指标（提升幅度）
- 主要贡献与局限性
- 一句话总结与启发

---

### 第 3 步：提炼价值

筛选标准：

- **核心性** — 是否是理解论文必须知道的信息？
- **可压缩** — 是否适合在单张图内表达？
- **可比较** — 是否有指标/对比支撑？
- **可传播** — 能否让读者快速判断论文价值？
- **可启发** — 能否帮助理解趋势或应用？

---

### 第 4 步：7 模块结构

信息图必须包含以下 7 个模块：

| 模块 | 内容 |
|------|------|
| 模块 1【论文速览】 | 标题、年份、机构/作者、关键词、研究方向 |
| 模块 2【核心问题】 | 解决什么问题？为什么重要？传统方法卡在哪？ |
| 模块 3【方法结构】 | 核心流程 + 关键创新，用通俗语言解释 |
| 模块 4【实验设计】 | 数据集、基线方法、评价指标、实验任务 |
| 模块 5【关键结果】 | 核心指标、提升幅度、最强证明实验 |
| 模块 6【贡献边界】 | 主要贡献、适用前提、局限性、误读警示 |
| 模块 7【一句话带走】 | 最值得记住的结论 + 适合谁看 + 启发 |

---

### 第 5 步：生成图片

使用 `image_synthesize` 工具，Prompt 结构如下：

```
Create a high-density academic infographic poster for Xiaohongshu about a research paper titled「[论文标题]」.

=== CRITICAL STYLE REQUIREMENTS (MUST FOLLOW EXACTLY) ===

【OVERALL VISUAL CONCEPT】
- A one-page research paper breakdown infographic.
- The poster should feel like a clean academic insight board, not a marketing poster.
- High information density with 6-7 clearly separated modules.
- Designed to help readers understand the paper's problem, method, experiments, results, contributions, and limitations at a glance.
- Strong editorial hierarchy, clear reading flow, and compact academic structure.

【COLOR SYSTEM】
- Background: soft off-white / light warm gray paper tone.
- Primary structure color: deep navy or charcoal black.
- Secondary information color: cool gray.
- Highlight color: orange-red for key conclusions, top results, or critical insights.
- Optional accent: muted blue for method diagrams or structured labels.

【LAYOUT & STRUCTURE】
- Portrait ratio: 3:4, optimized for Xiaohongshu.
- Top area should contain the paper title, year, keywords, and paper identity tags.
- Middle area should include 5-6 structured modules with clear borders or content zones.
- Bottom area can include a summary / takeaway / recommendation block.
- The reading flow should be highly structured and editorial, like a visual abstract plus a paper reading note.
- Avoid overly decorative composition; prioritize clarity and density.

【GRAPHIC ELEMENTS】
- Use academic infographic language:
  - paper title block
  - keyword tags
  - method flow arrows
  - model structure boxes
  - comparison tables
  - result metric cards
  - benchmark labels
  - contribution / limitation callout boxes
  - summary strip
- Graphics must support understanding, not decoration.
- No scrapbook objects, no cartoon icons, no pop-art style.

【MODULE REQUIREMENTS】
- Module 1: Paper Snapshot → title, year, authors, keywords, domain
- Module 2: Core Problem → research question and why it matters
- Module 3: Method Structure → simplified method or model flow
- Module 4: Experiment Setup → datasets, baselines, metrics, tasks
- Module 5: Key Results → main findings and improvement highlights
- Module 6: Contribution Boundary → contributions, assumptions, limitations
- Module 7: One-Line Takeaway → fast summary and who should care

【TYPOGRAPHY STYLE】
- Bold, modern sans-serif Chinese typography
- Strong title hierarchy with compact sublabels
- Dense but readable academic text blocks
- Numbers, metric values, and benchmark improvements should stand out clearly
- English terms can appear only as technical labels when necessary

【WHAT TO AVOID】
- No cute, cartoonish, or playful style
- No torn paper, stickers, clips, or hand-drawn journal textures
- No overly futuristic dashboard overload
- No retro pop-art palette
- No excessive empty space
- No vague generic summaries without concrete technical content

【CONTENT FOR THIS IMAGE】
Main Title: [论文标题]
Sub Title: [用一句话说明图的用途]

Module Allocation:
- Module 1 [Paper Snapshot]: [论文速览内容]
- Module 2 [Core Problem]: [核心问题内容]
- Module 3 [Method Structure]: [方法结构内容]
- Module 4 [Experiment Setup]: [实验设计内容]
- Module 5 [Key Results]: [关键结果内容]
- Module 6 [Contribution Boundary]: [贡献边界内容]
- Module 7 [One-Line Takeaway]: [一句话带走内容]

Illustration / Diagram Elements to include:
1. [方法流程图元素]
2. [实验对比元素]
3. [结果指标高亮元素]
4. [总结洞察元素]
```

**输出参数：**
- `aspect_ratio`: "3:4"
- `resolution`: "2K"
- `output_file`: `/workspace/paper_infographic_[论文简称].png`

---

### 第 6 步：返回结果

图片生成后：
1. 说明每个模块的核心内容
2. 提示用户可以调整的方向（换配色、加数据、改风格等）
3. 询问是否需要生成其他论文

---

## 输出模板

生成完毕后，按以下格式返回给用户：

```
📊 论文信息图已完成！

【论文】[论文标题]
【模块结构】
  ① 论文速览 | ② 核心问题 | ③ 方法结构
  ④ 实验设计 | ⑤ 关键结果 | ⑥ 贡献边界 | ⑦ 一句话带走

【生成图片】
[图片文件]

【各模块核心内容】
- ① [速览核心]
- ② [问题核心]
- ③ [方法核心]
- ④ [实验核心]
- ⑤ [结果核心]
- ⑥ [边界核心]
- ⑦ [带走核心]

---
调整方向：配色 / 数据精度 / 文字量 / 图解风格
```