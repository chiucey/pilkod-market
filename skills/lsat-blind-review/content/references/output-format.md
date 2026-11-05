---
description: |
  Canonical output format for LSAT LR Blind Review workbooks. Reverse-engineered
  from the user-modified `LSAT_LR_Flaw_Q201-240_Blind_Review_解析_v1.docx`
  (2026-09-19) and used as the default style for every new workbook. Older
  reference files (`four-part-template.md`) carry a superset of typography
  notes; this file is the **applied** format that build scripts must produce.

  **Last updated 2026-09-28** — Part I (Question cards) 调整为两栏 + 9.5pt +
  行前后 3pt / 行间距 1.05 倍 + 每 2 题 column break（过长题单列）。Part II / III
  行距 1.00× + Helvetica 字体。

  **2026-09-28（用户偏好精简）** — Part II 8 段式精简为 4 段（合并 ①② 为 ①，
  去 ④ BR 预判 + 核查 / 来源行）；Part III 3 张表精简为 1 张（去 错选字母分布 +
  7 日训练清单）；Part II/III 字体切换为 Helvetica（sans-serif），与 Part I 的
  Arial + Times New Roman 形成跨 Part 视觉对比。

  **2026-09-28** — 新增 §3.1.bis 封面 PNG 章节（cover template 集成）。详见
  `references/cover-template.md` 与 `scripts/render_cover.py`。
allowed-tools:
  - Read
metadata:
  trigger: docx 输出格式 / 字体 / 行间距 / 表格样式
  source: 用户 2026-09-19 修改后的 `LSAT_LR_Flaw_Q201-240_Blind_Review_解析_v1.docx` (127,536 字节)
  single-source-of-truth: true
  last-update: 2026-09-23 Part I 两栏 + 9.5pt 板式更新
---

# LSAT LR Blind Review — Output Format (applied)

This is the canonical output format that every new Blind Review workbook must
follow. It was reverse-engineered from the user-edited
`LSAT_LR_Flaw_Q201-240_Blind_Review_解析_v1.docx` (127 KB) on 2026-09-19.
The 9 already-shipped deliverables keep their original formatting; this
specification applies to every build from this date onward.

## 1. 页面与节 (page & section)

| Setting | Value | Notes |
|---|---|---|
| 页面尺寸 | A4 (8.27" × 11.69", 即 7560310 × 10692130 EMU) | 与 9 份已交付 docx 一致 |
| 页边距 | L/R/T/B = 0.79" (≈ 2cm, 720090 EMU) | 紧凑便于单页放题 |
| Section 数 | 3 个 section (用 `<w:sectPr>` 节断) | Section 0 = Part I（**两栏**）；Section 1 = Part II（单栏）；Section 2 = Part III+来源说明（单栏） |
| Section 0 栏数 | **两栏** `<w:cols w:num="2" w:space="720" w:equalWidth="1"/>` | 仅 Part I 使用；栏间距 720 twips ≈ 0.5"；Part II/III 恢复单栏 |
| Footer | `Page <PAGE> / <NUMPAGES>` 居中（Arial 9pt 黑色） | `<PAGE>` / `<NUMPAGES>` 用 field codes 实现 |

## 2. 字体规则（user 长期偏好 + 2026-09 确认）

| 类别 | 字体 | 字号 | 字重 | 颜色 | 说明 |
|---|---|---|---|---|---|
| **标题行**（顶部单行 `LSAT LR · <Scope> · Blind Review Workbook v{n}`） | Arial | 16pt | bold | 黑色 | 全文仅一行，置于第 0 段 |
| **Part heading**（`Part I Blind Review` / `Part II · 错题速览表` / `Part III · 弱势报告`） | Arial | 16pt | bold | 黑色 | Part 切换之间用分页符 |
| **Part 子标题**（如 `Part II · 错题速览表（12 题）`） | Arial | 14pt | bold | 黑色 | 紧跟 Part heading |
| **Part III heading**（`Part III · 弱势报告`） | Arial | 15pt | bold | 黑色 | 比 Part I/II heading 略小 |
| **Card header**（`Flaw · Q{n} · {type}`） | Arial | **9.5pt** | bold | 黑色 | Part I 两栏 + 9.5pt；**格式**：`<Category> · Q{n} · {type}` —— Category 是题目分类（如 `Flaw` / `Strengthen` / `Principle`），不是 scope 名 |
| **Stimulus** | Times New Roman | **9.5pt** | regular | 黑色 | Part I 两栏 + 9.5pt；verbatim |
| **`Question {n}` 行** | Times New Roman | **9.5pt** | bold | 黑色 | Part I 两栏 + 9.5pt；原文 verbatim |
| **Stem** | Times New Roman | **9.5pt** | bold | 黑色 | Part I 两栏 + 9.5pt；原文 verbatim |
| **选项字母 `A. ` `B. ` 等** | Arial | **9.5pt** | bold | 黑色 | Part I 两栏 + 9.5pt；单个 run 起始 |
| **选项正文** | Times New Roman | **9.5pt** | regular | 黑色 | Part I 两栏 + 9.5pt；紧接选项字母 run |
| **Part II / III 速览表标题与单元格** | Helvetica | 10.5pt | regular | 黑色 | Part II/III 统一 Helvetica sans-serif，与 Part I 形成视觉对比 |
| **Part II 4 段式小标题**（`① 题型 + 任务` / `③ stimulus 拆解` / `⑤ 正确答案为何对` / `⑧ 可迁移 Takeaway`） | Helvetica | 10.5pt | bold | 黑色 | 精简后 4 段（合并 ①②，去 ④ BR 预判、核查、来源行） |
| **`【Stimulus 复盘】` 行** | Helvetica | 10.5pt | bold | 黑色 | 4 段式之前的 stimulus 副本 |
| **Part II / III 分析正文**（4 段式 body） | Helvetica | 10.5pt | regular | 黑色 | 中文用 CJK 宋体 / 仿宋；英文用 Helvetica |
| **Part III 4-6 条具体劣势标题**（`劣势 N · {bucket}：`） | Helvetica | 10.5pt | regular | 黑色 | 非 bold；用 ` · ` 分隔 |
| **Part III 表内文字**（速览表 + 题型分布表 + 错因标签频次表） | Helvetica | 10.5pt | regular | 黑色 | 仅 Part III 用 3 张表（去 7 日训练清单） |

**关键红线**：

- **英文正文 Times New Roman；英文标题 Arial；CJK 宋体 / 仿宋 / 楷体**（2026-09 user override，取代此前 Latin Aptos + CJK Microsoft YaHei 默认）。
- **Part II / III 全 Helvetica sans-serif**：用于 Part II 速览表 + 8 段式（现 4 段式）+ Part III 全表 + 标题 + prose body。Part I 保持 Arial + Times New Roman；跨 Part 字体差异是 2026-09-28 用户偏好的有意区分，不是 build 缺陷。
- **不用任何强调色**：禁止 `#1F4E79`（navy）/ `#DCE6F1`（light-blue shading）/ `#C0392B`（red）/ `#804000`（amber）等。正确项仅以加粗区分，不加底色。
- **不用 cover 封面**：不再使用单独的 cover 页（"盲测卡片 · 核对总表 · 分题解析 · 劣势报告" 这类副标题 / 元数据 / Part 概览 / 使用说明 全部移除）。
- **不加 `BR 自答表`**：默认 `BR_SELF_ANSWER_TABLE` 未导出 = OFF。
- **不写核查 / 来源行**（2026-09-28 用户偏好精简）：Part II 8 段式分析不输出 `核查：✓verified` 和 `来源：lsatlab ...` 行；网络核对结果只在 build 时由 verify_<scope>.py 校验，不进入 workbook 本身。
- **不写错选字母分布 / 7 日训练清单**（2026-09-28 用户偏好精简）：Part III 只保留 1 张速览表 + 1 张题型分布表 + 1 张错因标签频次表 = 3 张表（speed table 单独算 = docx 内共 4 张）。verify harness 应校验 `len(doc.tables) >= 4`。
- **8 段式精简为 4 段式**（2026-09-28）：保留 `① 题型 + 任务` / `③ stimulus 拆解 / 条件关系` / `⑤ 正确答案为何对` / `⑧ 可迁移 Takeaway`；去掉 `② 任务翻译`（合并入 ①）、`④ BR 预判`（合并入 ③）、`⑥ 你实际所选为何有吸引力又为何不对`（合并入 ⑤）、`⑦ 其余选项排除`（合并入 ⑤）。

## 3. 结构（single-file 4 part）

docx 由 4 部分组成，无独立封面，无来源说明单独成页（来源信息分布在每题 ⑤ 段后的 `来源：...` 行）：

### 3.1 顶部标题行 + 时间戳（第 0-1 段）

```
LSAT LR · <Scope> · Blind Review Workbook v{n}
Finished Time: 12:27p.m. Sep 19th (Sat), 2026
```

- 第 0 段（标题行）：`LSAT LR · <Scope> · Blind Review Workbook v{n}` —— **左对齐**，Arial 16pt bold 黑色
- 第 1 段（时间戳）：`Finished Time: {时间戳}` —— **右对齐**，Arial 9pt regular 黑色
- 时间戳格式：`{H:MM}{a.m./p.m.} {Mon} {D}{st|nd|rd|th} ({Weekday}), {YYYY}`
  - 例：`12:27p.m. Sep 19th (Sat), 2026`
  - 12 小时制，`p.m.` / `a.m.` 用小写 + 半角点（`.`）而非冒号
  - 月份用英文 3 字母缩写（Jan/Feb/.../Dec）
  - 日期带序数后缀（1st / 2nd / 3rd / 4th ... 23rd / 31st 等）
  - 星期用英文 3 字母缩写（Mon/Tue/.../Sun）放在圆括号内
  - 年份 4 位
- 例：`LSAT LR · Flaw Q201-240 · Blind Review Workbook v1` / `Finished Time: 12:27p.m. Sep 19th (Sat), 2026`
- `<Scope>` 示例：`Day1` / `Day2_Day3` / `PT107_Section1_Section3` / `Flaw_Q201-240`
- `v{n}` 遵循 `AGENTS.md` 的 `vx` 格式
- 时间戳取 **build script 运行时**的本地时间，不可在 build 之后伪造

### 3.1.bis 封面 PNG（2026-09-28 起所有新 workbook 适用）

每个 workbook 必须**同时**交付一张 cover PNG，并嵌入为 docx 第 1 页（默认行为，不再是可选）：

- 调用 `scripts/render_cover.py "<subtitle>" <out_path>.png [year]` 生成
- A4 2481×3508 @ 300 dpi
- 副标题格式与 workbook scope 对应（不含版本号），如：
  - `PrepTest 01 · Section 3 & 4` / `PrepTest 109 · Section 3` / `Day 1` / `Principle Identify · Section 3`
- 完整设计规范、红线、字体、调用示例见 `references/cover-template.md`

**嵌入为 docx 第 1 页**（默认行为）：用 `python-docx` 在 docx 第一段之前插入 cover PNG（`width=Cm(17.0)`），并加 `WD_BREAK.PAGE` 让原标题 + 时间戳进入第 2 页开头。**不**重写 4-Part 正文。完整步骤见 `references/cover-template.md` 与 `scripts/insert_cover.py`。

若用户明确说"不要封面"，可跳过嵌入；但推荐默认生成 + 嵌入。

### 3.2 Part I — Question cards（**仅用户的错题**；不含做对的题）

> **2026-09-19 偏好更新**：Part I 仅包含用户的**错题**（用户在该次练习中答错的题号）。原 9 份冻结 docx（Day1 / Day2_Day3 / Principle_Identify / PT107/PT108/PT109 / 跨Workbook_报告）以及 Flaw_Q201-240 v1（127 KB）**当时**采用"全部 40 题"模式——那些是历史模式，保留不动。**自 2026-09-19 起新生成的 workbook 一律改为"仅错题"模式**。
>
> **2026-09-23 板式更新**：Part I 改为 **两栏布局**，BR 题目全文（含选项）统一 **9.5pt**，行前后各 **3pt**，行间距 **1.05 倍**；每题后空两行；每 2 题后显式 column break，过长题可独占一列。原单栏 12pt 板式仅适用于 2026-09-23 之前生成的 workbook。

- 第 1 段：`Part I Blind Review` — Arial 16pt bold 黑色
- 第 2 段后：直接进入错题卡片
- **Section 0 栏设置**：`<w:cols w:num="2" w:space="720" w:equalWidth="1"/>`（Part II / III 恢复单栏）
- **每张卡片**（全部按 9.5pt / space_before 3pt / space_after 3pt / line_spacing 1.05 倍）：
  - **Card header**（第 1 行）：`<Category> · Q{n} · {type}` —— Arial **9.5pt** bold
  - **Stimulus**：1-N 段 verbatim，Times New Roman **9.5pt** regular
  - **`Question {n}` 行**：Times New Roman **9.5pt** bold
  - **Stem**：Times New Roman **9.5pt** bold
  - **A-E 选项**：每行一段；`A. ` 等字母部分用 Arial **9.5pt** bold，正文用 Times New Roman **9.5pt** regular
- **题末留白**：每张卡片写完后追加 **2 个空段**（`<w:p>` 内容空字符串，字号继承 9.5pt / 行距 1.2 / 段距 3pt）。
- **列断规则**（核心）：
  - 默认 **每列 2 题**：第 2 题写完后，追加 1 个含 `<w:br w:type="column"/>` 的空段（即"空两行 + column break"），下一题从下一列顶部开始。
  - **过长单题例外**：若单题渲染后估计超过单列容量（builder 实现时建议 **> 50 行 或 > 1500 字符**作为"过长"判定，可在实测后微调），则该题**单独占一列**；写完后追加 2 个空段 + column break，下一题进入新列；不凑满 2 题再换栏。
- **无答案 / 无提示 / 无 BR 自答表**（skill 硬规则）。
- **整张 Part I 在 section 0 内**（首尾用 `<w:sectPr>` 节断与 Part II 隔开；section 0 末的 `<w:sectPr>` 同时承载两栏设置）。

**示例**：用户做 Flaw Q201-240 共 40 题，错了 12 题（204/205/208/209/211/215/217/219/221/229/237/239）→ Part I 仅含这 12 张卡片，不含 Q201-203/206-207/210/212-214/216/218/220/222-228/230-236/238/240。Part II 速览表与 8 段式解析也只针对这 12 题。两栏布局下 12 张卡片 ≈ 3 页（每页 2 栏 × 2 题 ≈ 4 题 / 页），单列 9.5pt 留白充分。

### 3.3 Part II — 答案速览表 + 4 段式中文解析

> **2026-09-28 用户偏好精简**：原 8 段式精简为 4 段式（合并 ①② 为 ①，去 ④ BR 预判 / 核查 / 来源行 / ⑥ 你的选择为何有吸引力 / ⑦ 其余选项排除 合并入 ⑤）。Build script 直接出 final docx，**不**写入 核查 / 来源 行（这些元数据仅在 verify_<scope>.py 中校验，不进 workbook）。

- `Part II · 错题速览表`（Arial 16pt bold）→ 紧接着 `Part II · 错题速览表（12 题）`（Arial 14pt bold）
- **速览表**（13 行 × 6 列，Table Grid 样式 / 黑色细边框 / 无底色）：
  ```
  | 题号 | Section | 题型 | 正确答案 | 你的答案 | 错因标签 |
  | 204  | Flaw    | Flaw | **E**    | A        | 原则匹配 |
  | ...  | ...     | ...  | **...**  | ...      | ...       |
  ```
  - **Section 列**：填题目分类（如 `Flaw`），不是 scope 名（如 `Flaw_Q201-240`）
  - **正确答案列**：Helvetica 10.5pt **bold**（无底色）
  - 其余列：Helvetica 10.5pt regular
- `Part II · 12 错题 4 段式中文解析`（Arial 16pt bold）→ 紧接着 12 个错题各自一段
- **每题布局**（Helvetica 10.5pt regular for stimulus 复盘；Helvetica 10.5pt bold for 4-section 小标题）：
  1. **`Q{n} · {type}`** —— Helvetica 10.5pt bold（与 4 段式小标题同字号）
  2. **`【Stimulus 复盘】`** —— Helvetica 10.5pt bold；后接 stimulus 原文（Helvetica 10.5pt regular，**只出现一次**）
  3. `① 题型 + 任务` —— Helvetica 10.5pt bold + prose（合并原 ① 题型识别 + ② 任务翻译；Helvetica 10.5pt regular，1-3 行）
  4. `③ stimulus 拆解 / 条件关系` —— Helvetica 10.5pt bold + bullet-style 拆解（合并原 ④ BR 预判）
  5. `⑤ 正确答案为何对` —— Helvetica 10.5pt bold + prose 详述 gap 闭合（合并原 ⑥ 你的选择 + ⑦ 其余选项排除）
  6. `⑧ 可迁移 Takeaway` —— Helvetica 10.5pt bold + 中文规律一句；下方 `> {English standard formulation}` 用 Helvetica 10.5pt italic

- **整张 Part II 在 section 1 内**
- **不**写 `核查：✓verified` 与 `来源：lsatlab ... + 7sage ...` 行（2026-09-28 用户偏好精简）

### 3.4 Part III — 弱势报告

> **2026-09-28 用户偏好精简**：原 5 张子表精简为 2 张子表（去 错选字母分布 + 7 日训练清单）；其余 3 子节（题型分布 / 错因标签频次 / 4-6 条具体劣势）保留。
>
> **2026-09-28 用户偏好精简 2**：4-6 条具体劣势进一步压缩为单段 ≤3 句、无括号、合并 表征 + 训练动作为一行。具体表征 sub-paragraph 删除。

- `Part III · 弱势报告`（Arial 15pt bold）
- **3 个子节 + 2 张表**（docx 内 Part III 区域共 2 张表，加上 Part II 速览表共 3 张）：
  1. `1. 题型分布（12 错题）` —— Helvetica 10.5pt bold；下方 4×2 表（`题型` / `题数`）
  2. `2. 错因标签频次（12 错题）` —— Helvetica 10.5pt bold；下方 5×2 表（`错因标签` / `题数`）
  3. `3. 4-6 条具体劣势` —— Helvetica 10.5pt bold；下方 4 条具体劣势，每条单段：
     - **格式**：`劣势 N · {bucket}：`（Helvetica 10.5pt bold）+ 同一段延续 `表征 1 句。训练 1-2 句。`（Helvetica 10.5pt regular）
     - **硬约束**：每条 ≤3 句（表征 1 + 训练 ≤2）；不使用括号 `（）` 解释、不分多行 sub-paragraph；具体表征 sub-paragraph 删除
     - **错误示例**：
       ```
       劣势 1 · 方法识别：3 题错在方法识别——argument 的 inferential move 没先正向归纳，
       直接拿表面现象匹配选项；典型如 S3-Q9 把 'fines 当 ordinary expense' 当成 weaken
       （其实强化）。BR 训练动作：每题先写 1 行 'arguer actually did X'（cause/evidence/
       analogy 等），再扫选项。Weaken 题默认要给出 alternate explanation；Parallel 题先
       把 passage 写成 A/B/C 字母形式再对选项拆解。
       ```
       （4 句 + 2 处括号 + 3 行 sub-paragraph → 太啰嗦）
     - **正确示例**：
       ```
       劣势 1 · 方法识别：3 题错在没先正向归纳 argument 的 inferential move 就匹配选项。
       BR 时先写 1 行 'arguer actually did X' 再扫选项；Weaken 默认走 alternate
       explanation；Parallel 先拆 A/B/C 字母。
       ```
       （2 句 + 0 处括号 + 单段）

- **整张 Part III 在 section 2 内**
- **不**写 `错选字母分布` 表（2026-09-28 用户偏好精简）
- **不**写 `7 日优先级训练清单` 表 + 章节标题（2026-09-28 用户偏好精简）
- **不**写 `具体表征：` sub-paragraph（2026-09-28 用户偏好精简 2）

### 3.5 来源说明（不再单独成页 + 不在 8 段式后写入）

- workbook 内**不**出现 `核查：✓verified` 和 `来源：lsatlab ... + 7sage ...` 行（2026-09-28 用户偏好精简）。网络核对结果只在 `verify_<scope>.py` harness 中输出，不进入 workbook 本身。
- 不再设置独立的"来源说明"页或 Part。
- 来源站点固定为：`lsatlab` / `7Sage` / `LSAT Hacks` / `PowerScore Forum` / `Apollo` / `TestMaxPrep`。
- 不出现"未复制第三方解析"等元说明文本（Part III 4-6 条劣势 + `【Stimulus 复盘】` 已经把分析原创性体现出来）。

### 3.5.bis 封底 PNG（2026-09-28 起所有奇数页数 workbook 适用）

- **触发条件**：workbook 最终页数为**奇数**时（即 `cover + content` 总页数 mod 2 == 1），自动生成 A4 back cover PNG 并嵌入 docx 作为最后一页。
- **偶数页 workbook 不插入封底**（用户明确指定触发条件）。
- **强制字体 ≤9pt**（per 用户 2026-09-28 反馈，硬约束）：所有文字 Arial 9pt 或更小；标题 Arial Bold 9pt + 正文 Arial Regular 9pt。
- **封底内容**（全部英文）：
  - 顶部：R.Cap / LSAT PREP logo + 分隔线
  - ABOUT THIS WORKBOOK（4 段英文：WHAT THIS IS / METHODOLOGY / HOW TO USE / CAVEAT）
  - 版权块：`© [Year] J. Hu. All rights reserved. ...`
  - 底部 meta：`R.Cap · J. Hu · {year}`
- **总字数硬约束**：ABOUT THIS WORKBOOK 部分（4 段正文 + sub-section 标题 + 顶部 R.Cap / LSAT PREP）总 word count **≤350 词**。版权块与底部 meta 不计入。
- **设计风格**与 front cover 区分：封底**不**含浅灰弧形 swoosh 装饰；以功能区分前后封。
- 调用 `scripts/render_back_cover.py "<subtitle>" <out_path>.png [year]` 生成 PNG。
- 用 `scripts/insert_back_cover.py <docx> <png>` 检测页数后条件插入。
- 完整设计规范、字体规则、4 段默认英文内容、8 条硬约束见 `references/back-cover-template.md`。

## 4. 表格样式（Table Grid + 黑色细线，无底色）

| 元素 | 边框 | 底色 | 字体 | 备注 |
|---|---|---|---|---|
| 速览表（13×6） | 黑色 0.5pt 全部边框 | 白色（无底色） | Helvetica 10.5pt | 表头加粗黑；正确答案列加粗 |
| 题型分布（4×2）/ 错因标签频次（5×2） | 黑色 0.5pt | 白色 | Helvetica 10.5pt | 表头加粗黑 |

- **禁止**：浅蓝 `#DCE6F1` 底色 / 红色 `#C0392B` / 琥珀 `#804000` / navy `#1F4E79` 文字色。
- **不区分正误颜色**：正确项与错误项在视觉上不通过颜色区分，仅通过加粗区分。

## 5. 行间距 / 段间距

| 段落 | space_before | space_after | line_spacing |
|---|---|---|---|
| 标题行（第 0 段） | 0 | 12pt | 1.0 |
| Part heading | 0 | 18pt | 1.15 |
| Part 子标题 | 0 | 6pt | 1.15 |
| **Part I · Card header / Stimulus / Question N / Stem / 选项 A-E** | **3pt** | **3pt** | **1.05 倍** |
| **Part I · 题末空段（每张卡后 2 个）** | **3pt** | **3pt** | **1.05 倍** |
| **Part I · 列断空段（含 `<w:br w:type="column"/>`）** | **3pt** | **3pt** | **1.05 倍** |
| 【Stimulus 复盘】 | 6pt | 2pt | 1.00 |
| ①—⑤／(i)/(iii)/(v) 段式小标题 | 4pt | 0 | 1.00 |
| 段式 prose body | 0 | 4pt | 1.00 |
| ⑧ Takeaway 中文 | 0 | 4pt | 1.00 |
| Part III 子节标题 | 6pt | 2pt | 1.00 |
| 劣势 N · ... | 4pt | 0 | 1.00 |
| 具体表征 / 训练动作 prose | 0 | 6pt | 1.00 |

> **2026-09-28 更新**：Part I 全部段落统一 `space_before = space_after = 3pt / line_spacing = 1.05 倍`；Part II / III 走 `line_spacing = 1.00 倍`（更紧凑，且配 Helvetica sans-serif 让 prose 更易读）。Part I 题末 / 列断空段也走同一套 3pt / 1.05 倍，避免与卡片内段落视觉割裂。

## 6. 元素命名规范

- 顶部标题：`<scope> · Blind Review Workbook v{n}` 中 `<scope>` = Docx scope 简称（不含 `LSAT_LR_` 前缀与 `.docx` 后缀）
- Card header：`<Category> · Q{n} · {type}`：**Category 是题目分类**（Flaw / Method / Principle / Strengthen / Weaken / etc.），不是 scope
- Part II 速览表 Day 列：仅填 **Category**（如 `Flaw`），不填 scope
- 题型标识 `{type}`：英文题目类型，1-3 个单词（`Flaw` / `Flaw (EXCEPT)` / `Misunderstanding` / `Method` / `Principle` / `Parallel Flaw` / `Assumption` / etc.）

## 7. 与 9 份已交付 docx 的兼容性

- 9 份已冻结 docx（Day1 / Day2_Day3 v3 / Principle_Identify_Section3 / PT107_S1_S3 / PT108_S2 / PT109_S1/S3/S4 / 跨Workbook_报告）保留各自的原始格式。
- **2026-09-19 之前**生成的 workbook 适用"单栏 + 12pt"旧规格（仅本档生成）。
- **2026-09-19 至 2026-09-22**生成的 workbook 适用"单栏 + 12pt + 仅错题"规格。
- **2026-09-28 起**生成的 workbook 适用 **Part I 两栏 + 9.5pt + 3pt / 1.05 倍** + **Part II/III Helvetica 10.5pt / 1.00 倍 + 4 段式 + 3 张表（去 7 日训练清单 / 错选字母分布）** 新规格。9 份已冻结 docx 不重建。
- 已交付 docx 不可重建（skill 硬规则 #4）。

## 8. 核查标签 `✓verified` / `~` / `?` 的使用

- `✓verified`：≥ 1 个公开 prep 站点（lsatlab / 7Sage / LSAT Hacks / PowerScore / Apollo / TestMaxPrep）确认答案正确
- `~`：仅单源旁证或结构性镜像，未达双源标准
- `?`：未核实，纯逻辑推导
- 速览表中**只用 `✓verified` 一种标签**（用户的 Flaw Q201-240 docx 12 题全部双源已核实）
- 实际生成时若 12 题中存在 `~` 或 `?`，应**如实标注**，不升级为 `✓verified`

## 9. 相关文档

- `references/four-part-template.md` — 旧版 4 段式模板（保留作为 typography 参考；本文件已**取代**其中关于字体 / 颜色的硬性规定）
- `references/mistakes-history.md` — 历史 v2 mis-map 教训；含 2026-09 字体 / 颜色 override 记录
- `references/verification-checklist.md` — verification harness 11 项检查清单
- `references/weakness-mapping.md` — 4 个底层能力桶 + 错因标签词汇
- `references/terminology-preferences.md` — LSAT 术语固定译法（在 lsat-prep-tutor skill 下）
