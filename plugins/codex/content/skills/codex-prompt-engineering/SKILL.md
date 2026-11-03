---
name: codex-prompt-engineering
description: 需要为 Codex 编写诊断、审查、研究或实现 prompt 时使用；通过紧凑的 XML contract 提高结果稳定性，不强行覆盖本机模型配置。
---

# Codex Prompt Engineering

像操作员一样给 Codex 写 prompt，而不是泛泛地邀请它协作。保持 compact、block-structured，并明确任务、输出契约、完成策略和验证要求。

## 默认结构

```xml
<task>
说明具体任务、仓库或失败上下文，以及期望的最终状态。
</task>

<structured_output_contract>
说明精确输出形状、排序和简洁程度。
</structured_output_contract>

<verification_loop>
完成前根据需求、变更文件和工具输出验证结果；检查失败时修正后再结束。
</verification_loop>
```

## 按任务增加约束

- 调试或实现：加入 `completeness_contract`、`verification_loop` 和 `missing_context_gating`。
- review 或 adversarial review：加入 `grounding_rules`、`structured_output_contract` 和 `dig_deeper_nudge`。
- 研究或推荐：加入 `research_mode` 和 `citation_rules`。
- 可写任务：加入 `action_safety`，限制范围并避免无关重构。

## 重要规则

- 一次 Codex run 只做一个清晰任务。
- 告诉 Codex 什么叫完成，不要让它猜。
- 缺少会影响正确性、安全性或不可逆操作的信息时才停止提问。
- review 要求事实有证据；推断必须标注为推断。
- 先改善 prompt contract，不要靠强行提高 reasoning effort 解决问题。
- 不要默认传 `model`；让本机 Codex 配置决定 provider 和模型。

## 可复用区块

完整区块、任务模板和反模式见本 Skill 目录下的 `references/`：

- `prompt-blocks.md`
- `codex-prompt-recipes.md`
- `codex-prompt-antipatterns.md`
