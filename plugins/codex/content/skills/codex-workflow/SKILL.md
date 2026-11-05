---
name: codex-workflow
description: 使用本机 OpenAI Codex 进行只读代码审查、对抗式设计审查或明确授权的修复任务时使用。触发词包括“让 Codex 审查”“Codex review”“对抗式审查”“让 Codex 修复”。
---

# Codex Workflow

在 Pilkod 中通过 `codex-local` MCP Server 调用本机 Codex。Pilkod 始终负责理解需求、协调结果和最终决策；Codex 是被委派的独立审查者或执行者。

## 模型与 Provider

- 默认不要向 `codex` 工具传 `model`；让 Codex 使用本机配置（默认 `~/.codex/config.toml`）中的模型、provider 和 reasoning effort。
- Pilkod 自身的模型名不能直接当作 Codex 模型名。不要自动填入未经当前 Codex provider 验证的模型值。
- 只有用户明确指定模型，并且确认当前 Codex provider 支持时，才传入 `model`；本插件代理原样转发该参数。
- 未指定模型时省略 `model`，由 Codex 自己解析默认配置。
- 需要说明实际使用的模型或 provider 时，以本次运行返回的信息为准；没有可核对的信息时说明尚未确认。

## 路由规则

### 普通只读审查

用户要求检查当前改动、寻找 bug、审查安全性或验证实现时：

- 调用 Codex 的 `codex` 工具；
- 明确要求只读，不修改文件、不创建提交；
- 让 Codex 优先报告 `file:line`、严重性、影响和最小修复建议；
- 完成后由 Pilkod 独立核对关键发现。

### 对抗式审查

用户要求挑战设计、寻找隐藏假设或检查高风险变更时：

- 调用 `codex` 工具；
- 在任务中加入“对抗式审查”以及具体关注点；
- 重点要求检查失败模式、并发、权限、数据丢失、回滚和可观测性；
- 仍然保持只读，不让 Codex 修改工作区。

### 修复或实现任务

只有用户明确允许修改时，才委派可写任务：

- 明确告诉 Codex 可以修改哪些文件和允许的范围；
- 默认不要执行 `git commit`、`git push`、发布或删除不可恢复数据；
- 要求先检查现状，再实施最小改动，最后运行相关测试；
- 返回后必须检查真实 `git diff`、测试输出和工作区状态。

## 安全边界

- 不要让 Pilkod、Codex 和其他 Agent 同时修改同一批文件。
- 不要让 Codex 再次委派回 Pilkod，避免循环调用。
- 不要把 API key、登录令牌或其他秘密写入 Codex prompt、日志或文件。
- review 默认只读；“修复”“实现”“改代码”才允许进入可写路径。
- Codex 的文字结论不是事实证明；关键结论必须结合源码、diff 和测试验证。
- 大型任务优先让 Codex 返回结构化审查结果，避免把无关完整文件内容复制进 prompt。

## 结果处理

收到 Codex 结果后，Pilkod 应：

1. 区分事实、推断和建议；
2. 打开相关文件核对行号与上下文；
3. 对可操作问题给出优先级；
4. 如果发生了修改，检查 `git diff` 和测试；
5. 向用户明确说明 Codex 做了什么、没有做什么，以及仍未验证的内容。
