---
name: codex-cli-runtime
description: 在 Pilkod 中委派诊断、计划、研究或实现任务给本机 Codex 时使用；负责选择 Codex MCP 调用方式和安全边界。
---

# Codex Runtime

通过本插件的 `codex-local` MCP Server 调用 Codex。Pilkod 是协调者，不要把 Claude Code 专属的 `codex-companion.mjs`、Bash 转发器或 hooks 搬到这里。

## CLI 兼容性

- 插件检查 `codex --help` 的命令列表。仍提供 `mcp-server` 的版本继续使用原生 MCP；移除该入口且提供 `app-server` 的版本使用插件内置协议适配，工具名仍为 `codex` 和 `codex-reply`。
- 新路径使用 Codex app-server 的实验性协议；版本升级后若协议不兼容，应报告原始错误，不自动重发任务或切换入口。
- Windows 新路径通过系统 Windows PowerShell 建立独立 Job Object 管理进程生命周期；环境策略禁止 PowerShell、类型编译或 Job 分配时停止启动，不绕过系统策略。
- app-server 路径的新任务默认 `sandbox: "read-only"`、`approval-policy: "never"`，顶层安全参数优先于 `config`。需要写入时明确传 `workspace-write`；模型、provider 和 reasoning effort 继续由 Codex 配置解析。
- app-server 路径不提供交互审批或问答界面。需要人工批准、额外权限或用户输入时停止并报错；不得替用户批准，也不得自动改用更宽松的 sandbox。引导用户在 Codex 交互界面处理。
- 保存返回的 `threadId`，续聊只传该 ID 和增量 prompt。同一 MCP 进程内显式继承首轮权限及 `config`、指令覆盖；插件重连后未知线程按只读、禁止审批恢复，逐次配置覆盖需要通过新任务重新提供，需要继续写入时创建明确授权的新任务。取消或超时会停止当前调用，不会回滚已经发生的文件改动；重试前先检查现场。

## 调用规则

- 使用 `codex` 工具处理新的任务；使用 `codex-reply` 继续已有 thread。
- 只发送一次清晰的任务；不要把多个无关目标混进一次调用。
- 不要显式传 `model`，除非用户明确指定且确认该模型对当前 Codex provider 可用；默认让 Codex 使用 `~/.codex/config.toml` 的模型、provider 和 reasoning effort。
- 对 review、诊断、研究任务使用 `sandbox: "read-only"` 和 `approval-policy: "never"`。
- 对明确授权的实现任务使用 `sandbox: "workspace-write"`，并在 prompt 中限定文件范围。
- 不要使用 `danger-full-access`，除非用户明确要求且理解其影响。
- 不要让 Codex 再次委派回 Pilkod，避免循环。

## 任务类型

- 审查当前 git 改动：优先让 Codex检查 diff，不要修改文件。
- 诊断失败：要求收集证据、定位根因，并给出最小安全下一步。
- 实现修复：明确允许修改，要求完成后检查 diff 和测试。
- 后续任务：使用 `codex-reply`，只发送增量指令，不重复整段上下文。

## 失败处理

如果 Codex 返回认证、provider、模型或 MCP 错误，保留原始错误，先检查 `codex login status` 和 `~/.codex/config.toml`，不要猜测替代模型或把任务伪装成已完成。
