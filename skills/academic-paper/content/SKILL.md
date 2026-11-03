---
name: academic-paper
description: 学术论文全流程管理 - 包含阅读笔记、写作辅助、文献综述、论文评审、批量整理、翻译润色、LaTeX辅助、图表规范、代码复现、投稿转换、演讲准备、学术档案、自动论文写作、质量自查
license: MIT
compatibility: opencode
metadata:
  domain: academic
  type: comprehensive
  version: 2.0
---

## Overview

覆盖学术论文全生命周期的所有场景。参考资源位于 skill 目录下的 `reference/`（常用缩写表）和 `templates/`（可直接使用的笔记/审稿/回复模板）。

**调用方式：** 说出你想做的任务 + "用 academic-paper 技能"。
**示例：** "用 academic-paper 帮我精读这篇论文" / "用 academic-paper 写一段文献综述"

## 通用规则

- 保留完整引用信息：作者 / 标题 / 年份 / venue / DOI / arXiv ID / PDF 链接
- 不确定的信息标注 [待确认] 并说明原因
- 注意区分不同学科的写作惯例（CS 重实验、数学重证明、社科重方法论）
- 输出优先 Markdown，可按需转 LaTeX

---

## 1. 论文阅读与笔记

### 1.1 笔记类型速查

| 类型 | 何时用 | 输出长度 | 产出物 |
|------|--------|----------|--------|
| 速读 | 筛论文、追新文献 | 3-5 条要点 | 决定是否精读 |
| 精读 | 核心论文深度理解 | 完整笔记 | 结构化笔记 |
| 批判 | 审稿 / 反驳 / 写 Related Work | 分析为主 | 优缺点评估 |
| 演示 | 组会 / 论文汇报 | 含 slide 大纲 | 汇报材料 |

### 1.2 精读输出结构

调用精读时，按以下结构输出：

```markdown
## [标题]

**作者**： · **年份**： · **Venue**：
**DOI**： · **arXiv**：
**代码**：[官方](链接) · [非官方](链接)
**关键词**：

### 研究问题
- 问题陈述 · 重要性 · 现有不足

### 方法
- 核心思路 → 架构 → 与 prior work 区别

### 实验
- 数据集 / 指标 / 基线 / 主结果（表格） / Ablation / 可视化

### 结论与贡献
- 主要发现（2-3 点）

### 批判分析
- 局限 · 实验充分性 · 结论支撑 · 遗漏实验

### 启发
- 对自己工作的启示 · 可借鉴思路 · Follow-up 方向

### 关键引用
- 前置阅读 · 重要相关工作
```

### 1.3 阅读清单管理

```markdown
## 阅读清单

| 论文 | 状态 | 优先级 | 笔记 | 标签 |
|------|------|--------|------|------|
| xxx | 待读/在读/完成 | P0/P1/P2 | link | tag |
```

### 1.4 速读判断准则

当需要判断一篇论文是否值得精读时，重点回答：
1. 问题是否与我的研究相关？
2. 方法是否有新意？
3. 结果是否显著优于 prior work？
4. 代码是否开源？
5. 如果是，进入精读；否则记录速读笔记即可。

---

## 2. 论文写作辅助

### 2.1 章节写作指南

| 章节 | 要点 | 常见错误 |
|------|------|----------|
| Title | 10-15 词，含关键词，承诺贡献 | 太泛 / 太长 / 无信息量 |
| Abstract | 背景→问题→方法→结果→影响，各 1-2 句 | 缺少结果数值 / 太啰嗦 |
| Intro | 漏斗结构：大背景→小问题→gap→本文方案→贡献列表 | Related Work 混入 Intro |
| Related Work | 按主题分类，段末对比本文 | 流水账 / 只列不评 |
| Method | 问题形式化→框架图→模块详述→训练细节 | 缺整体图 / 缺实现细节 |
| Experiment | 设置→数据集→基线→主表→分析→Ablation→可视化 | 缺消融 / 基线不公平 |
| Conclusion | 贡献总结 + 局限 + 未来工作 | 重复 Abstract / 无局限 |

### 2.2 学术短语速查

**引出问题：**
- Despite recent progress, ... remains challenging.
- Existing approaches primarily focus on ..., but little attention has been paid to ...

**描述贡献：**
- We propose a novel framework that ...
- The core idea is to ...
- Different from previous methods, our approach ...

**报告结果：**
- As shown in Table X, our method achieves ...
- Compared to baselines, our approach yields consistent improvements of ...

**总结收尾：**
- In this paper, we presented ...
- Our results demonstrate that ...

### 2.3 Abstract 模板（按需二选一）

**偏方法版：**
```
[背景]. However, [局限]. We propose [方法名] — a [类别] that [核心思路].
Specifically, we [设计1] and [设计2]. On [数据集], our method achieves [指标],
outperforming [基线] by [幅值].
```

**偏结果版：**
```
[问题] is critical for [场景]. While [现有方法] have shown promise, they suffer from
[具体问题]. We present [方法名], which addresses this by [策略]. On [数据集], our
approach obtains [结果1] and [结果2], establishing SOTA.
```

### 2.4 Cover Letter / 回复信

Cover Letter 模板和审稿回复信模板见 skill 目录下的 `templates/response-letter.md`。

### 2.5 语言润色速查

| 原句问题 | 替换方案 |
|----------|----------|
| is used to | serves to |
| is able to | can |
| In order to | To |
| It is worth noting that | （直接陈述） |
| very / really / quite | substantial / significant / 具体数值 |
| a lot of | many / numerous / substantial |
| 连续被动语态 | 交替主动被动 |
| 连续相同句式 | 长短句交替，每 3 句换结构 |

**时态规则：** Abstract 现在时 → Method 过去时 → Conclusion 现在时

---

## 3. 文献综述

### 3.1 综述工作流

```
检索 → 筛选（含纳入/排除标准） → 提取（PICO） → 质量评估 → 综合
```

### 3.2 对比表格式

```markdown
| 论文 | 年份 | 方法类别 | 核心思路 | 数据集 | 关键指标 | 代码 | 优缺点 |
|------|------|----------|----------|--------|----------|------|--------|
| [1] | 2025 | CNN | ... | ... | 90.1 | ✅ | ... |
```

### 3.3 研究空白矩阵

```markdown
| 维度 | 已有大量 | 少量探索 | 空白 |
|------|----------|----------|------|
| 场景 A | ✅ | | ❌ 本文目标 |
| 场景 B | | ✅ | |
```

### 3.4 综述段落输出要求

- 按主题组织，非逐篇列举
- 每段标注对应引用
- 段末点明与本文关系

---

## 4. 论文评审

### 4.1 18 项检查

| 类别 | 检查项 |
|------|--------|
| 问题定义 | 问题是否明确？Motivation 是否充分？ |
| 方法 | 创新性？可复现性？合理性？ |
| 实验 | 数据集？基线公平性？指标？显著性？Ablation？Error analysis？ |
| 写作 | 结构清晰？图表自包含？引用充分？ |
| 伦理 | 声明（如需）？ |
| 可复现 | 代码开源？超参数报告？随机种子固定？ |

### 4.2 评审格式

```markdown
## Summary
2-3 句概括 + 总体评价

## Major Issues
### Issue 1: [标题] [High/Medium]
- 问题 · 修改建议

## Minor Issues
### Issue 1: ...

## Suggestions
1. ...

## Rating
Strong Accept / Accept / Weak Accept / Borderline / Weak Reject / Reject
Confidence: High / Medium / Low
```

完整审稿模板见 `templates/review-template.md`。

### 4.3 Venue 评审侧重

| Venue | 侧重 | 页数 |
|-------|------|------|
| 顶会 (CVPR/NeurIPS/ICML) | 创新 + 实验充分 | 8 页 + 补充 |
| 顶刊 (TPAMI/IJCV) | 完整 + 理论深度 | 不限 |
| 中档会议 | 扎实即可 | 按模板 |
| Workshop | 想法新颖 | 4-6 页 |

---

## 5. 批量整理

### 5.1 PDF 元数据提取

扫描时提取：标题 / 作者 / 年份 / DOI / arXiv ID / 页数 / 代码链接

### 5.2 分类维度

- 按年份：2024 / 2025 / 2026
- 按会议：CVPR / NeurIPS / ICML / ICLR / AAAI / IJCAI / ACL / EMNLP ...
- 按主题：用户自定义
- 按状态：已读 / 在读 / 待读

缩写参考：`reference/venue-abbreviations.md`

### 5.3 重命名格式

```
年份-Venue简称-第一作者姓-关键词.pdf
示例：2025-CVPR-Zhang-DiffusionTransformer.pdf
```

### 5.4 BibTeX 条目生成

```bibtex
@inproceedings{zhang2025diffusion,
  title     = {Diffusion Transformer for ...},
  author    = {Zhang, San and Li, Si and Wang, Wu},
  booktitle = {Proceedings of ...},
  year      = {2025},
}
```

### 5.5 文献总表

```markdown
| # | 标题 | 一作 | 年份 | Venue | 标签 | 代码 | 笔记 |
|---|------|------|------|-------|------|------|------|
| 1 | ... | ... | 2025 | CVPR | det | ✅ | link |
```

---

## 6. 论文翻译 & 双语对照

### 6.1 原则
- 中英互译，术语一致
- 长句拆短，被动主动合理转换
- 公式 / 编号 / 专有名词不翻
- 引用格式不变

### 6.2 输出格式

```markdown
## Title
EN: ...
CN: ...

## Abstract
EN: ...
CN: ...
```

### 6.3 术语表

```markdown
| EN | CN | 说明 |
|----|----|------|
| attention | 注意力 | |
```

---

## 7. LaTeX 辅助

### 7.1 格式检查清单
- [ ] `\cite{}` 是否有对应 bib 条目
- [ ] `\ref{}` 是否有对应 `\label{}`
- [ ] `\begin{}` / `\end{}` 成对
- [ ] 特殊字符已转义：`_ & % $ # { } ~ ^`
- [ ] 图片路径正确
- [ ] 页数在限制内
- [ ] 补充材料已分离

### 7.2 常用片段

```latex
% 算法
\begin{algorithm}[t]
\caption{...}
\begin{algorithmic}
\State ...
\end{algorithmic}
\end{algorithm}

% 定理
\begin{theorem}\label{thm:conv}
...\end{theorem}

% 三线表
\begin{table}[t]
\centering\caption{...}\label{tab:res}
\begin{tabular}{lcc}\toprule
...\\\midrule
...\\\bottomrule
\end{tabular}\end{table}
```

### 7.3 推荐宏包

| 用途 | 宏包 |
|------|------|
| 表格 | booktabs, tabularx, multirow |
| 图片 | graphicx, subcaption, tikz |
| 算法 | algorithm, algorithmicx |
| 定理 | amsthm, ntheorem |
| 引用 | natbib, biblatex |
| 交叉引用 | hyperref, cleveref |

---

## 8. 图表规范

| 图表类型 | 要求 |
|----------|------|
| Figure 1 | 系统框架图，含输入/输出/模块/数据流 |
| Figure 2+ | 核心模块细节 |
| 可视化 | 定性对比，标注差异 |
| Table | booktabs 三线表，最佳加粗，对齐规范 |

配色优先考虑色盲友好（ColorBrewer），字体 ≥ 8pt。

| 工具 | 适用 |
|------|------|
| draw.io / TikZ | 框图 |
| matplotlib / seaborn | 数据图 |
| Illustrator / Inkscape | 示意图 |

---

## 9. 代码 & 可复现性

### 9.1 检查项
- README（环境 + 运行）
- requirements.yml / requirements.txt
- 预训练权重 / 下载脚本
- 训练 / 测试分离
- 随机种子固定
- 结果可复现（提供 log）

### 9.2 复现报告

```markdown
## 复现报告
论文：[标题]
环境：GPU / CUDA / PyTorch
| 指标 | 论文 | 复现 | 偏差 |
|------|------|------|------|
| Acc | 95.2 | 94.8 | -0.4 |
复现：完全 / 部分 / 失败
难度：容易 / 中等 / 困难
```

---

## 10. 投稿 & 格式转换

### 10.1 投稿检查
- [ ] 模板符合目标 venue
- [ ] 页数达标
- [ ] 匿名化（双盲：去作者名 / 致谢 / 机构）
- [ ] 补充材料已上传
- [ ] 代码链接已附
- [ ] 伦理 / IRB 声明（如需）
- [ ] Conflict of interest 声明
- [ ] 作者贡献声明

### 10.2 格式转换场景

| 转换 | 要点 |
|------|------|
| arXiv → 会议 | 压缩页数，突出贡献，补充实验 |
| 会议 → 期刊 | 扩展 30%+ 新内容 |
| 中文 → 英文 | 完整翻译，调风格 |
| NeurIPS ↔ CVPR | 参考文献格式 + 版面 |

---

## 11. 演讲准备

### 11.1 Slide 结构

| Slide | 内容 |
|-------|------|
| 1 | 标题 + 作者 + 单位 |
| 2 | 问题 + 动机（配例子） |
| 3 | 现有方法不足 |
| 4 | 核心 insight（一张图） |
| 5-6 | 方法细节 |
| 7 | 实验对比表 |
| 8 | Ablation / 可视化 |
| 9 | 结论 + 贡献 |
| 10 | Q&A |

### 11.2 原则
- 1 slide = 1 个信息
- 图 > 表 > 文字
- 1 slide ≈ 45-60 秒
- 准备 30s / 1min / 5min 三个 pitch 版本
- 预判 Q&A 并准备回答

---

## 12. 学术档案

### 12.1 CV 结构

```markdown
## 个人信息
## 教育背景
## 研究方向
## 发表论文（按年份倒序）
1. [作者], "[标题]", *Venue*, 年份.
## 学术服务
- 审稿：CVPR 2025, NeurIPS 2025
## 荣誉奖项
## 技能
```

### 12.2 论文列表

```markdown
## 2025
- **[标题]** \
  作者 \
  *Venue* 年份 \
  [PDF] [Code] [DOI]
```

---

## 13. 全流程自动论文写作

根据你提供的材料（实验结果、笔记、代码、想法、参考文献）自动生成完整论文。

**核心能力：** 实验日志→论文 | 零散笔记→论文 | 草稿优化 | 中译英 | 会议→期刊扩展

**工作模式：** 逐章生成，每写完一章停下等你反馈。可随时要求修改/重写/调整。

### 13.1 支持输入

| 输入 | 说明 |
|------|------|
| 实验结果 | 表格/数值 → 方法 + 实验章节 |
| 思路笔记 | 零散 idea → 完整论文 |
| 代码仓库 | 分析逻辑 → 方法描述 |
| 现有草稿 | 润色 / 改写 / 扩充 / 压缩 |
| 中文内容 | 翻译 → 英文论文 |
| 文献列表 | → Related Work + 引言 |
| 会议版本 | → 期刊扩展（+30% 新内容） |

### 13.2 写作流程

```
Phase 1: 需求分析
  ├─ 确认输入 + 目标 venue（页数/格式）
  ├─ 确认是否双盲匿名
  └─ 输出：大纲 + 各章节要点

Phase 2: 逐章写作（每章等你反馈）
  ├─ Title + Abstract
  ├─ Introduction
  ├─ Related Work
  ├─ Method
  ├─ Experiments
  └─ Conclusion

Phase 3: 整体优化
  ├─ 上下文一致性检查
  ├─ 引用完整性检查
  ├─ 图表引用检查
  └─ 语言润色

Phase 4: 格式输出（Markdown / LaTeX / BibTeX）
```

### 13.3 逐章写作规范

#### Title
10-15 词，含核心贡献关键词。一次生成 3-5 候选，标注推荐。

模板：`[方法名]: [核心思路] for [任务]` / `[任务] via [方法]`

#### Abstract
**严格 150-250 词：**
```
[1-2 句背景] However, [1 句局限].
We propose [方法名], which [1-2 句核心思路].
Experiments on [数据集] show our method achieves [指标], outperforming [基线] by [幅值].
Code at [链接].
```
生成两个版本：偏方法版 / 偏结果版。

#### Introduction
**漏斗结构（6 段）：**
```
P1: 大背景 + 重要性（引用综述）
P2: 现有成就（引用相关工作）
P3: 现有不足 + 关键挑战（gap）
P4: 本文方案概述（核心 insight）
P5: 贡献列表（numbered list, 3 条）
P6: 路线图（Section 2–6）
```

#### Related Work
主题式组织，禁止流水账。每主题一段，段末对比本文。尾段总结 gap。

#### Method
```
Problem Formulation → Framework Overview（对应 Figure 1）
→ Module 1 → Module 2 → ... → Training Details
```
每个公式后跟文字解释，关键组件说明动机。

#### Experiments
```
Setup（数据集/实现/指标/基线）
→ Main Results（主表，先趋势再逐行）
→ Ablation Studies
→ Analysis（可视化/开销/失败案例）
```
每个发现跟一句"Why this happens?"分析。

#### Conclusion
```
P1: 贡献 + 关键结果（2-3 句）
P2: 局限性（1-2 句）
P3: 未来工作（1-2 句）
```
不与 Abstract 重复。

### 13.4 多轮迭代命令

写作过程中随时说：

| 命令 | 效果 |
|------|------|
| "继续" / "OK" | 确认当前章节，写下一章 |
| "修改：[意见]" | 重写当前章节 |
| "重写" | 从头重写 |
| "压缩到 X 句" | 缩短 |
| "扩写到 X 段" | 扩展 |
| "加引用：[信息]" | 加入引用 |
| "跳过这章" | 跳到下一章 |
| "回到 [章节]" | 返回修改已完成章节 |
| "生成 LaTeX" | 输出 LaTeX 版本 |
| "检查引用" | 完整性 + 格式 |

### 13.5 输出格式

| Venue | 模板 | 限制 |
|-------|------|------|
| CVPR | cvpr_style.sty | 8 页 + ref |
| NeurIPS | neurips_2025.sty | 8 页 + ref |
| ICML | icml_2025.sty | 8 页 + ref |
| ICLR | iclr_2025.sty | 9 页 + ref |
| AAAI | aaai.sty | 7 页 + ref |
| IJCAI | ijcai_25.sty | 7 页 + ref |
| TPAMI | IEEEtran.cls | 不限 |
| Elsevier | elsarticle.cls | 不限 |

### 13.6 Prompt 模板

**从零开始：**
```
用 academic-paper 技能帮我写篇论文。
研究方向：[方向]
核心 idea：[一句话]
实验结果：[关键结果]
目标 venue：[名称]
```

**从实验结果：**
```
以下是我的实验结果：[表格/数据]
任务描述：[说明]
基线对比：[基线 + 结果]
请写成论文初稿。
```

**从草稿优化：**
```
帮我润色这篇论文。
当前草稿：[内容]
主要问题：[描述]
目标 venue：[名称]
```

### 13.7 协作原则
- 我负责生成和优化，你负责把关和决策
- factual claim 需要你确认
- 实验数据需要你提供
- 整体 story 方向由你把控
- 我会主动提问理清模糊之处

---

## 14. 论文质量自查

写作完成后自动运行检查，也可单独调用自查。

### 14.1 内容检查
- [ ] 贡献列表明确且可验证
- [ ] 每个 claim 有对应实验支持
- [ ] 所有图表在正文中被引用
- [ ] 所有引用在正文中被引用
- [ ] 术语全文一致
- [ ] 无矛盾和冗余

### 14.2 格式检查
- [ ] 页数在限制内
- [ ] 匿名化完全
- [ ] 参考文献格式统一
- [ ] 图表编号连续
- [ ] 公式编号连续
- [ ] 单位符号正确

### 14.3 语言检查
- [ ] 时态一致（Abstract 现在→Method 过去→Conclusion 现在）
- [ ] 无 dangling modifier
- [ ] 无不必要的主语从句
- [ ] 非过度使用被动语态
- [ ] 无 run-on sentence
- [ ] 长短句交替，无连续 3+ 相同句式
- [ ] 无模糊词（very, really, quite, a lot of）
