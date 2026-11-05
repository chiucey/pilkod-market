# MCode 中的 MCP 与 CLI 降级

## 首选 MCP

本插件已打包 MCP 配置和全部 Skills。优先使用当前会话的 CloudBase MCP 工具，调用前读取实际 schema。工具未出现时，先检查 MCode 插件启用、连接状态和 Node/npm/npx 依赖，按 [mcp-setup.md](mcp-setup.md) 处理；不要运行其他 IDE 的插件安装命令。

## 可选 CLI

用户明确要求 CLI/CI，或 MCP 无法在当前会话恢复且 CLI 可以完成当前任务时：

1. 读取 `../../cloudbase-cli/SKILL.md` 和 `../../cloudbase-cli/references/core.md`，再按任务读取对应领域参考。
2. 检查 `tcb --version`。已有项目 CLI 依赖可继续使用；没有时先说明需要安装 `@cloudbase/cli`，选择当前项目或隔离目录的安装方式，避免默认全局安装。
3. 根据 CLI 文档执行登录。CLI 负责自己的授权；成功不代表当前 MCode MCP 连接或进程环境已更新。
4. 使用完整 envId，运行命令时指定当前项目目录，不依赖其他项目的默认环境。
5. 不使用 `tcb deploy` 通用快捷命令；使用参考文档中的云函数、托管、存储或 CloudRun 领域命令。

| 任务 | MCP 逻辑工具 | CLI 参考（相对 cloudbase-cli 目录） |
| --- | --- | --- |
| 管理账号登录 | `auth` | `references/core.md` |
| 环境查询或选择 | `envQuery`、`auth.set_env` | `references/core.md` |
| 云函数 | `queryFunctions`、`manageFunctions` | `references/functions.md` |
| Web 部署 | `manageApps`、`manageHosting` | `references/hosting.md` |
| CloudRun | `queryCloudRun`、`manageCloudRun` | `references/cloudrun.md` |
| 存储 | 当前 schema 中的存储工具 | `references/storage.md` |

MCP 和 CLI 都不能绕过用户的操作范围及变更确认。连续失败两次后报告具体错误，改用已验证可用的路径；不要反复重装或让用户提供 SecretId/SecretKey 来绕过授权。
