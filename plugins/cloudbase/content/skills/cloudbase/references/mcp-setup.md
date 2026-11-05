# 在 MiniMax Code 使用 CloudBase MCP

## 安装与工具发现

本插件已经声明 `cloudbase-mcp`，由 MCode 通过 stdio 启动：

```text
npx -y @cloudbase/cloudbase-mcp@2.34.4
```

1. 在 MCode 插件管理中安装并启用「腾讯云 CloudBase」。
2. 从当前会话提供的工具列表或工具搜索中查找 CloudBase 工具，读取实际 schema。工具名可能带 MCode 生成的前缀；本文的 `auth`、`envQuery` 等是上游逻辑名。
3. 插件刚启用但当前会话未出现工具时，检查插件连接状态，再重新进入会话验证。不要仅凭安装成功宣称 MCP 已可用。
4. MCP 依赖 Node.js 与 npm/npx。首次启动需要网络和 npm 下载缓存空间；失败时报告具体的进程或下载错误。不要反复安装其他 IDE 的插件或改写其配置。

无需单独执行 `tcb login`，也无需运行 `npx plugins add`、`npx skills add` 或配置 mcporter。MCode 的插件连接成功与腾讯云账号授权完成是两个状态。

## 管理账号授权

当用户要求登录或使用需要授权的 CloudBase 管理能力时：

1. 调用 `auth(action="start_auth", authMode="device")`。如果用户指定国际站点或地域，依据当前 schema 传入对应字段；否则沿用服务默认值。
2. 返回 `AUTH_PENDING` 时，向用户展示 `verification_uri_complete`（或 `verification_uri`）及 `user_code`，等待用户在浏览器完成授权。不要要求用户把密钥或浏览器登录凭证粘贴到聊天或配置文件。
3. 按返回提示调用 `auth(action="status")` 获取进度；尊重轮询间隔、过期和取消状态。不得将 `AUTH_PENDING` 当成登录成功。
4. 凭证由官方 MCP 的授权组件保存和复用；MCode 插件包不复制、打印或手动注入这些凭证。

上游授权流程可能同时准备云开发服务；账号没有环境时可能尝试开通或创建免费环境。因此不要把 `auth(status)` 当作纯连接健康检查：只验证 MCP 连接时使用初始化和工具发现。用户只要求查看本地配置时，不触发授权准备流程。用户要求登录且尚无环境时，先说明这一行为，确认其也同意准备云开发环境后继续。

`auth` 是管理账号登录；应用用户的登录方式由 `queryAppAuth` / `manageAppAuth` 管理。不要混淆这两类授权。

## 确定当前项目环境

1. 从当前项目读取 `.cloudbase/project.json` 或 `cloudbaserc.json`，结合用户要求确认完整 envId。不得从用户主目录或另一个项目猜测环境。
2. 用户给出别名时，用 `envQuery(action="list", alias=..., aliasExact=true)` 解析完整 EnvId；没有唯一结果时先澄清。
3. 按工具 schema 显式传 envId；需要设置进程环境的工具，先调用 `auth(action="set_env", envId="完整环境ID")`，再核对目标环境。`set_env` 不等同于把环境持久化到当前项目配置。
4. 项目文件路径参数使用当前项目的绝对路径。只有用户要求绑定项目时才修改项目配置，保留原有字段，不写入账号凭证。
5. 当前接入沿用 MCode 现有 MCP 连接范围，不能把进程中的默认环境当成项目隔离保证。涉及不同环境的操作顺序执行；并发操作不同项目环境时，不能依赖 `set_env` 避免交叉影响。

## 故障与降级

- Node/npm/npx 缺失：报告依赖缺失，并按用户操作系统选择安装方式。插件启用本身不会安装 Node.js。
- 下载或进程启动失败：检查 MCode 连接错误、网络和 npm 可用性，避免重复创建同名 MCP。
- 授权等待、拒绝或过期：保持未登录状态，按用户意愿重试；不绕过授权。
- 当前会话没有工具：按 [tooling-fallback.md](tooling-fallback.md) 排查；CLI 仅是可选降级路径。
