---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 44eb85803838528ece57b4b17ce76a14
    PropagateID: 44eb85803838528ece57b4b17ce76a14
    ReservedCode1: 30450220670897b339ea3932f283b9963720a440fe31ae12bea1543bca24bfd4206f10fa022100e026b2d1077c3f6185bebe39923c180082ea7c1497d2b737d492d9e53a1ba28a
    ReservedCode2: 3046022100989cc09e2f39a0eda72028e1f7745fbd12660c8606b644de78ed509fd0273fb3022100a8c1d1fc8c739c5fdbaf4419be2b616e6e03b5cc4db6b45beba18d3b61ea0d36
description: |-
    Skill 整合分析器。当用户要求对已安装的 skills 进行去重、整合、或发现功能重叠时触发。 使用场景：
      - "帮我扫描一下现有的 skills"
      - "有哪些技能可以整合"
      - "技能太多了，想清理一下"
      - "检查一下有没有重复的技能"
      - "帮我分析 skill 重叠"
      - "skill 整合"
    本技能扫描 /workspace/skills/ 目录下所有已安装的 skills， 按三层逻辑分析整合必要性，并生成可操作的报告供用户决策。
name: skill-integrator
---

# skill-integrator

扫描本地已安装 skills，分析整合机会，按三层逻辑输出报告。

## 三层整合逻辑

### L1 — 包含关系（建议直接删除）
A 包含 B（B 是 A 的子集，或 backup/旧版本）：
- A 的描述覆盖 B 的全部功能
- B 文件更少或内容更旧
- **操作**：直接删除 B，保留 A

### L2 — 重叠关系（用户决策是否融合）
A 和 B 有交叉但各自独立：
- 描述关键词重叠 ≥ 25%
- 技术栈有交集
- **操作**：输出重叠点和综合得分，用户决定是否融合成新技能

### L3 — 关联关系（提议评估）
A 和 B 功能分立，但主题/上下文相关：
- 同属一个工作流或话题领域
- 代码不重叠但使用者可能需要联动
- **操作**：输出融合同意提案，由用户判断是否执行

## 使用方式

### 方式一：直接运行扫描脚本
```bash
python3 /workspace/skills/skill-integrator/scanner.py
```

### 方式二：AI Agent 驱动
本技能被激活后，Agent 自动：
1. 读取 scanner.py 并执行
2. 解析 references/scan-report.json
3. 按三层逻辑向用户逐条呈现结果
4. 每条结果附带具体操作建议

## 输出文件

- **references/scan-report.json** — 结构化数据，包含：
  - `skills[]` — 所有 skill 的 profile（名称、描述、技术栈、文件数）
  - `l1_containment[]` — L1 包含关系
  - `l2_overlap[]` — L2 重叠关系
  - `l3_association[]` — L3 关联关系

## 扫描范围

默认扫描 `/workspace/skills/` 下所有子目录，读取每个 skill 的：
- `SKILL.md`（必须）— 触发词、描述
- `scripts/` — 技术实现细节
- `references/` — 关联文档

## 整合操作权限

本技能**只读不写**，所有删除/合并操作需用户明确确认后执行。
