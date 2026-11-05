---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e2c338ae2cce89f07a9aa60ab8f24fd3
    PropagateID: e2c338ae2cce89f07a9aa60ab8f24fd3
    ReservedCode1: 30450221008238c83770cae0f694572491ab51d8f4c6ab682b317cb33eca6946522a3c506a02205fdabc0f8c34b6b720ad5c801ea6540351b63577c6a8461506aa711354ed3b77
    ReservedCode2: 304502205be9172aae0e14f1ccc255cb043b7599b891371dcfe93b4447dbe0f17778b798022100b0112d97992ea321c9488512b571c9292557aa6c3422f8b2ed599c406642733e
description: AI Agent Skills 锻造工具。当用户要求创建新技能、提升 SKILL.md 质量、重构已有技能、生成生产级 Agent Skill、批量制作 Skills、修正低质量 Skill、分析 Skill 架构，或需要 SKILL.md + scripts + references 完整包时使用。触发短语包括："生成一个xxx Skill"、"帮我创建一个xxx的技能"、"用 skillforge"、"我的 Skill 质量不好"、"帮我优化这个 Skill"、"需要批量制作 Skills"、"创建 Agent Skill"。
name: skillforge
---

# SkillForge - AI Agent Skills 锻造炉

用 AI 自动锻造生产级 Agent Skills 的完整工作流引擎。

## 核心能力

| 功能 | 说明 |
| --- | --- |
| 7步生成引擎 | 从零创建符合最佳实践的完整 Skill |
| 3步修正引擎 | 诊断并优化已有 Skill |
| 10维度质量审计 | 格式、触发、边界、示例、文档等全方位评估 |
| 完整 Skill 包 | 输出 SKILL.md + scripts/ + references/ |
| ZIP 打包 | 一键生成可分发的 .skill 文件 |

## 工作模式

### 模式一：创建新 Skill（7步生成）

当用户要求创建新技能时，使用以下流程：

#### Step 1: 需求深度挖掘

分析 5 个维度：
1. **定位分析** - Skill 的核心角色和职责边界
2. **触发边界** - 何时应触发，何时不应触发
3. **使用场景** - 典型和边缘用例
4. **知识缺口** - 需要用户提供哪些专业知识
5. **竞品分析** - 是否存在类似 Skill，分析差异化

输出：结构化需求文档

#### Step 2: 架构决策引擎

做出 5 大决策：
1. **结构模式** - 简单线性 vs 分支决策 vs 迭代循环
2. **自由度级别** - 严格约束 vs 灵活适配
3. **资源规划** - 需要哪些 tools、references、templates
4. **披露策略** - 透明推理 vs 简洁响应
5. **质量保证** - 验证点和回退策略

输出：架构决策文档

#### Step 3: 元数据精炼

为 SKILL.md 准备：
- 3 个候选 description
- 每个候选的自评打分（触发准确性、边界清晰度、简洁性）
- 选择最优 description 作为最终触发器

输出：精炼的 frontmatter

#### Step 4: SKILL.md 主体生成

遵循以下规范：
- Frontmatter 必须是第一行（YAML 块）
- 必须包含 name 和 description
- description 必须包含触发短语
- 文件结构：Frontmatter → 概述 → 核心逻辑 → 工具定义 → 示例
- 150-450 行指令主体
- 使用祈使句、面向任务的指令
- 具体示例替代模糊描述

输出：符合规范的 SKILL.md

#### Step 5: 质量审计

10 维度评分：

| 维度 | 权重 | 检查项 |
| --- | --- | --- |
| 格式规范 | 15% | YAML frontmatter、markdown 结构 |
| 触发质量 | 15% | description 触发准确性、边界清晰 |
| 边界定义 | 15% | 触发/不触发场景明确 |
| 指令质量 | 15% | 清晰、可执行、无歧义 |
| 示例质量 | 10% | 现实、多样、覆盖边缘 |
| 工具定义 | 10% | 完整、必要、合理 |
| 文档完善 | 5% | README、结构化注释 |
| 错误处理 | 5% | 边界情况、优雅降级 |
| 可维护性 | 5% | 模块化、清晰命名 |
| 安全性 | 5% | 无注入风险、无敏感泄露 |

评分 < 70% 时自动修复低分项

输出：评分报告 + 修复后的 SKILL.md

#### Step 6: 配套资源生成

根据需要生成：
- `scripts/` - 自动化脚本（Python/Bash）
- `references/` - 参考文档、模式库
- `templates/` - 输出模板
- `_meta.json` - Skill 元数据（id, version）

输出：完整 Skill 包结构

#### Step 7: 最终组装与交付

验证清单：
- [ ] 格式验证 - YAML 语法、markdown 结构
- [ ] 内容验证 - 触发器、指令、示例完整性
- [ ] 最佳实践验证 - 10 维度评分 >= 80%
- [ ] 打包验证 - ZIP 可正常解压

输出：可分发的 Skill 包

### 模式二：修正已有 Skill（3步优化）

当用户上传或粘贴已有 Skill 进行优化时：

#### Step 1: 问题诊断

对照最佳实践逐项检查：
- Frontmatter 格式和触发质量
- 指令清晰度和可执行性
- 边界定义完整性
- 示例覆盖度
- 工具定义合理性

输出：诊断报告 + 问题列表 + 当前评分

#### Step 2: SKILL.md 重写

保留原始意图，按最佳实践重写：
- 优化 frontmatter description
- 精炼指令主体
- 补充缺失边界定义
- 增强示例覆盖

输出：重写后的完整 SKILL.md

#### Step 3: 质量审计

验证重写质量：
- 新评分必须优于原版
- 10 维度评分 >= 80%
- 确认保留原有意图

输出：对比报告 + 优化后的 Skill

## 输出格式

最终交付：

```
skill-name/
├── SKILL.md           # 技能入口
├── _meta.json         # {"id": "xxx", "version": "1.0.0"}
├── scripts/          # 自动化脚本（可选）
├── references/       # 参考文档（可选）
└── templates/        # 输出模板（可选）
```

## 质量门槛

- Frontmatter 必须在第一行
- 必填字段：name、description
- description 必须包含触发短语
- 10 维度评分 >= 80%
- ZIP 可正常解压

## 示例对话

**用户**: "帮我用 skillforge 创建一个 code-reviewer Skill"

**执行**: 7步生成流程 → 输出完整 Skill 包

**用户**: "我的这个 Skill 质量不好，帮我优化"

**执行**: 3步修正流程 → 输出优化后的 Skill

**用户**: "需要批量制作 5 个自动化测试相关的 Skills"

**执行**: 循环调用 7步生成 → 批量输出 Skill 包
