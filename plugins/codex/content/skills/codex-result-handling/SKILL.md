---
name: codex-result-handling
description: 在 Pilkod 收到 Codex 结果后使用；负责保留证据边界、按严重性呈现发现并阻止未经确认的自动修复。
---

# Codex Result Handling

收到 Codex 输出后：

- 保留 Codex 的 verdict、summary、findings 和 next steps 结构。
- review 结果按严重性排序，优先呈现可复现且可操作的发现。
- 文件路径和行号按 Codex 原样保留，并结合源码上下文核对。
- 明确区分 observed fact、inference、uncertainty 和 follow-up question。
- 如果没有发现，明确写出“未发现问题”，并简短说明残余风险。
- 如果 Codex 修改了文件，明确说明已修改，并列出实际 touched files。
- 如果 Codex 没有成功启动、输出不完整或返回 malformed output，不要生成替代答案；报告最有用的错误信息并停止。
- 如果 Codex 报告需要认证或 setup，指导用户检查 `codex login status`，不要自行编造认证流程。

## Review 的硬边界

展示 review findings 后停止，不要自动修改任何代码。必须先让用户明确选择要修复的具体问题，之后才能触碰文件；即使修复看起来显而易见也一样。

## 修改任务

如果用户已经明确授权修复：

1. 核对 Codex 报告和真实 diff；
2. 检查 touched files 是否在授权范围内；
3. 运行与改动相关的测试；
4. 报告修改、验证和残余风险。
