---
name: academic-research-suite
description: Full-stack academic research assistant - collaborative AI support from topic selection to publication. Use when users request academic research, literature review, paper writing, peer review, research workflow management, study planning, literature search, meta-analysis, academic polishing, or reviewer response. Supports IMRaD, systematic review, and meta-analysis structures.
---

# Academic Research Suite - 学术研究全栈工具包

> "学术写作不应该是孤军奋战" - 开源 AI 学术研究协作工具

## 核心哲学

本技能基于协作式多智能体架构，将学术研究视为团队协作而非孤独战斗。包含四大核心模块协同工作：

1. **深度研究** (Deep Research) - 13 智能体研究团队
2. **学术论文** (Academic Paper) - 12 智能体写作系统
3. **同行评审** (Paper Reviewer) - 多视角评审矩阵
4. **完整流程** (Pipeline) - 10 阶段端到端编排

## 工作流程

### 模式 1：深度研究 (Deep Research)

**适用场景**：用户需要开展研究、查找文献、进行系统评价或元分析

**7 种研究模式**：
| 模式 | 用途 | 触发关键词 |
|------|------|----------|
| `full` | 完整研究流程 | "全面研究"、"完整分析" |
| `quick` | 快速概览 | "快速了解"、"简要" |
| `systematic-review` | 系统评价 (PRISMA) | "系统评价"、"系统综述" |
| `socratic` | 苏格拉底式引导 | "引导研究"、"启发式" |
| `fact-check` | 事实核查 | "核查事实"、"验证" |
| `lit-review` | 文献综述 | "文献综述"、"literature review" |
| `review` | 评审式研究 | "评审"、"同行评审" |

**13 智能体团队**：
```
研究问题智能体 → 研究架构师 → 文献检索智能体 → 来源验证智能体
     ↓
综合智能体 → 报告撰写智能体 → 主编 → 魔鬼代言人
     ↓
伦理审查智能体 → 苏格拉底导师 → 偏倚风险智能体 → 元分析智能体 → 监控智能体
```

**执行流程**：
1. 使用 FINER 框架明确研究问题
2. 设计方法论架构
3. 系统性文献检索 (PRISMA)
4. 来源分级与掠夺性期刊检测
5. 跨来源综合分析
6. 生成 APA 7.0 报告
7. 主编评审 + 魔鬼代言人质疑
8. 伦理审查与 AI 披露验证
9. 偏倚风险评估 (RoB 2 / ROBINS-I)
10. 元分析 (效应量、异质性、森林图、GRADE)
11. 持续监控预警

### 模式 2：学术论文写作 (Academic Paper)

**适用场景**：用户需要撰写、修改、润色学术论文

**9 种写作模式**：
| 模式 | 用途 | 触发关键词 |
|------|------|----------|
| `full` | 完整论文写作 | "写论文"、"撰写论文" |
| `plan` | 章节规划 | "规划大纲"、"制定结构" |
| `revision` | 论文修改 | "修改论文"、"修订" |
| `revision-coach` | 修改教练 | "指导修改"、"回复审稿" |
| `format-convert` | 格式转换 | "转格式"、"LaTeX"、"Word" |
| `citation-check` | 引用检查 | "检查引用"、"citation" |
| `bilingual-abstract` | 双语摘要 | "中英文摘要"、"摘要翻译" |
| `writing-polish` | 写作润色 | "润色"、"polish" |
| `full-auto` | 全自动写作 | "一键写论文" |

**12 智能体写作团队**：
```
摄入智能体 → 文献策略师 → 结构架构师 → 论据构建智能体
     ↓
起草智能体 → 引用合规智能体 → 双语摘要智能体 → 同行评审智能体
     ↓
格式化智能体 → 苏格拉底导师 → 可视化智能体 → 修改教练智能体
```

**支持格式**：APA 7.0, IEEE, Chicago, MLA, Vancouver

**支持结构**：IMRaD, 主题综述, 理论分析, 案例研究, 政策简报, 会议论文

### 模式 3：同行评审 (Paper Reviewer)

**适用场景**：用户需要评审论文、模拟审稿意见、或准备回复审稿

**5 种评审模式**：
| 模式 | 用途 | 触发关键词 |
|------|------|----------|
| `full` | 完整评审 | "完整评审"、"全面审稿" |
| `quick` | 快速评审 | "快速审稿"、"简要评审" |
| `guided` | 引导式评审 | "引导审稿" |
| `methodology-focus` | 方法论聚焦 | "方法论评审"、"方法审查" |
| `re-review` | 复审 | "复审"、"再审" |

**评审智能体矩阵**：
```
主编 → 领域匹配、创新性、意义评估
方法论评审 → 研究设计、统计、可重复性
领域评审 → 文献覆盖、理论框架
视角评审 → 跨学科影响、实践价值
魔鬼代言人 → 核心论点质疑、逻辑谬误检测
编辑综合 → 共识分析、Rubric 评分
```

**评分决策映射**：
- ≥80 分：接受 (Accept)
- 65-79 分：小修 (Minor Revision)
- 50-64 分：大修 (Major Revision)
- <50 分：拒稿 (Reject)

### 模式 4：完整流程编排 (Pipeline)

**适用场景**：用户需要从零开始完成整个研究到发表流程

**10 阶段流程**：
```
阶段 1: 研究 (Deep Research)
    ↓
阶段 2: 写作 (Academic Paper)
    ↓
阶段 2.5: 诚信验证 (Integrity Check)
    ↓
阶段 3: 评审 (Paper Reviewer) × 2轮
    ↓ ← Socratic 修改教练
阶段 4: 修改 (Revision)
    ↓
阶段 4.5: 最终验证 (Final Integrity)
    ↓
阶段 5: 定稿 (Finalize: MD/DOCX/LaTeX → PDF)
    ↓
阶段 6: 流程总结 (Process Summary)
```

**关键特性**：
- 自适应检查点 (FULL/SLIM/MANDATORY)
- 100% 引用与数据验证
- 魔鬼代言人双重质疑
- Socratic 修改教练指导
- 6 维度协作质量评分

## 意图识别与路由

根据用户输入自动识别意图并路由到最合适的模式：

| 用户意图 | 推荐模式 |
|---------|---------|
| "我想研究 AI 对高等教育的影响" | Deep Research → full |
| "帮我写一篇关于 XX 的论文" | Academic Paper → full |
| "评审这篇论文" | Paper Reviewer → full |
| "帮我回复审稿意见" | Academic Paper → revision-coach |
| "做一个系统评价" | Deep Research → systematic-review |
| "引导我完成整个研究流程" | Pipeline → full |

## 苏格拉底引导模式

当用户请求引导式帮助时，采用苏格拉底方法：

1. **提问** - 通过开放式问题激发思考
2. **澄清** - 明确概念与假设
3. **挑战** - 质疑前提与逻辑
4. **收敛** - 综合观点形成结论

## 引用与诚信

- **强制 APA 7.0 格式** (默认)
- **WebSearch 审计追踪** - 所有引用必须可验证
- **反幻觉措施** - 五类幻觉分类与检测
- **AI 披露要求** - 必须说明 AI 使用情况

## 支持语言

- 中文 (简体/繁体)
- English
- 双语摘要 (中文 + 英文)
- 所有引导式交互支持任意语言

## 参考资源

详细文档位于 `references/` 目录：
- `agents.md` - 各智能体详细职责
- `modes.md` - 所有模式详细说明
- `prisma.md` - PRISMA 系统评价指南
- `citation_formats.md` - 引用格式规范
- `pipeline_checkpoints.md` - 检查点配置

## 原项目归属

本技能基于 [Academic Research Skills by Cheng-I Wu](https://github.com/Imbad0202/academic-research-skills) 开发，采用 CC BY-NC 4.0 许可证。
