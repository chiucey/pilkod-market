# 来源与适配

## 上游

- 项目：[TencentCloudBase/CloudBase-AI-Toolkit](https://github.com/TencentCloudBase/CloudBase-AI-Toolkit)
- 固定提交：`f3a15e810cc68a8a090655b0c0760bcd2d014c40`
- 来源目录：`plugin/cloudbase`，参考其中 `.codex-plugin/plugin.json`，上游插件版本 `0.2.0`。
- 复制内容：31 个 Skills 及其参考文件、`assets/logo.png`；保留仓库 MIT 许可证。
- 原作者：Tencent CloudBase。MiniMax Code 适配仅调整宿主打包和使用指引，不代表 Tencent 对该适配包作出认证。
- MCP：官方 npm 包 `@cloudbase/cloudbase-mcp@2.34.4`，运行时由 npx 下载；包内未复制 MCP 二进制。npm integrity 和复制前的上游文件 SHA-256 记录于 `upstream-source.json`。

## 适配内容

- 新增 MiniMax Plugin V1 manifest 和显式 stdio MCP 配置；固定 MCP 版本。
- `skills/cloudbase/SKILL.md`：加入 MCode 入口、包内 Skill 路径及工具名称说明，替换其他 IDE 的安装入口。
- `skills/cloudbase/references/mcp-setup.md`、`tooling-fallback.md`：改为 MCode 插件发现、设备码授权、依赖排查和可选 CLI 降级指引；说明上游授权准备环境的行为及现有进程环境范围。
- `skills/cloudbase-cli/references/core.md`：将 MCP 配置前置步骤指向 MCode 指引。
- 其他上游 Skill 和参考文件保留原文；未复制上游 Hooks 或宿主专用 commands/agents。

MiniMax 插件版本独立为 `0.1.0`。来源记录用于后续升级比对，不用于宣称尚未执行的登录、部署或跨平台验收。
