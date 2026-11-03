---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 024fd916bc3480eb91723bf437d8a4b4
    PropagateID: 024fd916bc3480eb91723bf437d8a4b4
    ReservedCode1: 3045022100a8ab5ced263b9a78adbad1621ec593616ec0910564cdc91a1dd2c94ff837e30102205f041eca5eee823e9248fc51fc66cf00cadb73e06d21d053e869624a9b36b1d9
    ReservedCode2: 3044022019b69d9549e8a88ab7ec1fda925d0684bbf3fe4cd1dd981529d72d7a76560b580220435a1f49ba6959dff7ed5b32ea6b4e168f9cc1f138dfd51c23e2a61e0cd68fc4
description: B端软件销售案例信息图生成。将销售案例文档（案例背景、产品资料、客户资料）提炼为5大维度，生成3D蓝色科技风格信息图。适用场景：（1）完成软件平台/解决方案销售后，（2）需要制作案例宣传素材给销售部门，（3）提供案例文档后自动生成双版信息图供选择。核心流程：读取材料→提炼结构化内容→生成文案文档（用户可编辑）→同时生成深蓝/浅蓝双版图片。
name: b2b-sales-case-infographic
---

# B端软件销售案例信息图生成

将案例内容提炼为结构化文案，生成**深蓝 + 浅蓝双版**信息图，供销售部门宣传使用。

## 核心变更说明

- ✅ 每个模块顶部显示：数字编号 + 小标题（01 客户类型 / 02 客户特点 / 03 用户痛点 / 04 产品价值 / 05 可复制经验）
- ✅ 小标题字号明显小于数字，内容文字居主视觉区
- ✅ 不显示页脚数据来源文字
- ✅ 文案先生成 `.md` 文档供用户核验/修改，再出图
- ✅ 同时输出深蓝版 + 浅蓝版两个配色版本供选择

---

## 输入要求

用户提供以下材料（越多越精准）：
1. **案例背景文档**（.docx/.md/.txt）— 客户类型、行业、规模
2. **产品信息文档**（.docx/.md/.txt）— 所售软件/解决方案介绍
3. **客户/用户资料**（可选）— 痛点、需求补充
4. **参考Logo**（.png）— 放在 `assets/` 目录，生成时用 `--ref` 引用

**最低要求**：至少提供案例背景 + 产品信息。

---

## 信息提炼框架

| 编号 | 维度 | 提取要点 |
|------|------|---------|
| 01 | 客户类型 | 行业、规模、企业性质 |
| 02 | 客户特点 | 市场地位、业务模式、数字化成熟度 |
| 03 | 用户痛点 | 具体业务场景中的困难，忠实原文 |
| 04 | 产品价值 | 具体功能 → 具体效果，一一对应 |
| 05 | 可复制经验 | 成功要素、实施方法论、行业通用性 |

---

## 工作流程

### Step 1: 读取材料

按以下优先级读取：
1. 用户直接粘贴的内容 → `source-case.md`
2. 工作空间中的案例文档 → `source-case.md`
3. `assets/` 中的图片 → 记录路径备用

### Step 2: 提炼结构化内容

按5维度框架提炼，**完全忠实原文，不添加信息**：
- 保留原文关键词和业务术语
- 数字需脱敏的标注 `[数据已脱敏]`
- 客户名称需保密的，用"某头部城商行"类表述

### Step 3: 生成文案文档 → `case-draft.md` ⚠️

将结构化内容写入 `infographic/case-draft-{YYYYMMDD}.md`，格式如下：

```markdown
# 【案例文案草稿】{案例名称}
> 请核验以下文案内容，如有修改请直接编辑本文档，然后告知「确认出图」

## 01
[客户类型内容，2-4行]

## 02
[客户特点内容，2-4行]

## 03
[用户痛点内容，3-5条，每条一行]

## 04
[产品价值内容，3-5条，每条格式：功能 → 效果]

## 05
[可复制经验内容，2-4条]
```

**⚠️ 重要**：出图前必须先生成此文案文档，直接回复给用户，等待用户确认或修改后，再进入Step 4。

**用户可操作**：
- 直接在回复中修改文字内容
- 或告知「直接出图」跳过修改

### Step 4: 生成双版信息图

用户确认文案后，**同时生成两个配色版本**，供用户选择：

#### 深蓝版（Deep Blue）
- 背景：`#0D1B2A` 深海军蓝
- 主色：`#0A84FF` 科技蓝
- 辅助：`#00D4FF` 激光青 + `#E8F4FF` 冰白
- 氛围：深邃、稳重、信赖

#### 浅蓝版（Light Blue）
- 背景：`#E8F4FF` 冰白 + `#0A84FF` 浅蓝渐变
- 主色：`#0066CC` 标准蓝
- 辅助：`#00D4FF` 激光青 + `#0D1B2A` 深蓝
- 氛围：明亮、清新、专业

#### Prompt 结构（两个版本均带模块小标题，无页脚）

```
A professional B2B software sales case infographic, 3D holographic blue tech style.
[VERSION A - DEEP BLUE: Dark navy bg #0D1B2A, tech-blue #0A84FF, laser-cyan #00D4FF accents]
[VERSION B - LIGHT BLUE: Ice-white #E8F4FF bg, standard-blue #0066CC, deep-navy #0D1B2A text]

Five clean modules stacked vertically in bento-grid layout.
Each module: module label (e.g. "01 客户类型") at top, large glowing 3D number, content below.
NO page footer or attribution text anywhere.

Module 01 客户类型: [用户确认的01内容]
Module 02 客户特点: [用户确认的02内容]
Module 03 用户痛点: [用户确认的03内容]
Module 04 产品价值: [用户确认的04内容]
Module 05 可复制经验: [用户确认的05内容]

Header: Main title at top, subtitle below, glowing blue divider line.

3D icon style: floating holographic panels with blue edge glow, translucent glass,
slight perspective tilt. Blueprint grid background, coordinate markers.
Professional sans-serif typography, high contrast, sharp corporate tech aesthetic.
--ar 9:16
```

### Step 5: 输出交付

```
infographic/
├── case-draft-{YYYYMMDD}.md       ← 文案草稿（供用户编辑）
├── case-deep-blue-{YYYYMMDD}.png ← 深蓝版
└── case-light-blue-{YYYYMMDD}.png ← 浅蓝版
```

---

## 输出规格

| 项目 | 规格 |
|------|------|
| 布局 | 五模块竖向堆叠（bento-grid） |
| 尺寸 | 竖版 9:16（默认）/ 横版 16:9 / 方版 1:1 |
| 模块标识 | 仅数字 01–05，无中文标题 |
| 文字语言 | 跟随用户提供材料语言 |

---

## 参考文件

- `references/styles/3d-blue-tech.md` — 深蓝版配色完整规范
- `references/styles/3d-light-blue.md` — 浅蓝版配色完整规范
- `references/layouts/bento-grid.md` — 五模块布局规范
- `references/case-content-template.md` — 内容提取模板
