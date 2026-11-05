# 腾讯云 CloudBase

为 MiniMax Code Desktop 提供 CloudBase 数据库、云函数、云存储、应用认证、托管和云托管的开发与管理能力。

## 接入方式

沿用 CloudBase 官方 Codex 插件的 MCP + Skills 组合：一个本地 stdio MCP，31 个领域 Skills。包使用 MiniMax Plugin V1 格式，分发到国内 Desktop 插件目录，版本为 `0.1.0`。

- MCP：`npx -y @cloudbase/cloudbase-mcp@2.34.4`，固定发布版本。
- Skills：取自官方 Toolkit 固定提交，包含本地引用的完整参考文档。
- 登录：由 MCP `auth` 的设备码流程完成，无需预先配置 CLI login。
- 运行依赖：可从 Desktop 进程 PATH 找到 Node.js 和 npm/npx；首次启动需访问 npm 下载包。

在 MCode 中启用插件后，可以说「帮我登录 CloudBase，并选择这个项目的云开发环境」。根据返回的验证链接与设备码完成登录，然后确认项目的完整 envId。具体步骤见 [使用指引](skills/cloudbase/references/mcp-setup.md)。

## 接入范围

本包复用 MCode 现有插件和 MCP 运行机制。未加入上游 Claude/Cursor Hooks、宿主专属 commands/agents、CLI 前置登录或 MCode runtime 改造。

插件连接成功只表示 MCP 可用，不等于腾讯云授权完成。上游登录流程可能准备云开发服务或免费环境，操作前按使用指引确认范围。

当前没有新增按项目隔离 MCP 进程的能力。环境操作需核对并显式指定 envId，需要文件路径时使用项目绝对路径；进程默认环境不能充当项目绑定或并发隔离。`auth.set_env` 不保证将 envId 写入项目配置。

首次接入仅声明 `desktop`，云端分发和不同操作系统的真实登录、部署验收不包含在本次包验证中。

## 来源与升级

见 [CREDITS.md](CREDITS.md)、[upstream-source.json](upstream-source.json) 和 [LICENSE](LICENSE)。升级时同时核对 MCP 工具 schema 与 Skills，更新固定版本、来源记录和本插件版本，再运行市场校验、打包 dry-run 与 MCP 初始化/工具发现验证。
