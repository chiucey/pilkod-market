# 在 Pilkod 中使用 Cloudflare

本文为 Pilkod 适配说明。先确认当前任务需要哪种操作，再使用对应的已发现工具。

## 连接与工具

1. 从官方市场安装后，在插件详情的 Cloudflare App 中点击连接，完成浏览器授权。连接完成后，以当前工具清单为准。
2. 使用 Cloudflare provider 的 docs 查询文档、search 查找 API，再通过 execute 执行所需 API。
   工具名以实际发现结果为准，通常为 connector__cloudflare__docs/search/execute。
   不假定上游的 cloudflare-api 名称或其他宿主的工具前缀可用。
3. 资源写入只使用用户已授权的操作和权限。403 可能是当前资源 scope 不足，检查具体错误，
   不要把每个 403 都当成凭证过期。确需增加权限时引导用户重新连接并在 Cloudflare 确认。
4. 工具缺失时检查 App 连接和当前能力清单。编写代码、阅读本地参考资料仍可继续；
   不用自建直连 MCP、读取浏览器/CLI 凭证或索取聊天中的 token 来替代连接流程。

## 项目与账户

读取当前项目的 wrangler.jsonc、wrangler.json 或 wrangler.toml，以及 package.json 中的
构建和部署脚本，明确 account_id、Worker 名、env、zone 和资源绑定。新项目中缺少这些信息时，
先读取账户清单并让用户选择必要目标。多账户时显式传 account_id，不默认选择第一项。
Cloudflare MCP 在远程运行，不能直接读取本机路径；路径字符串不等于上传文件。

## Wrangler

Cloudflare App 授权与 Wrangler CLI 授权相互独立。通过 App 连接不会自动登录本机 CLI，
服务端也不会向模型或 CLI 返回明文 token。查询和适合的 API 操作优先使用已连接 App。

确需本地构建、开发或 Wrangler 部署时，优先复用项目现有依赖、锁文件和 scripts，
使用项目包管理器的 exec（例如 pnpm exec wrangler 或 npm exec -- wrangler）。本文及上游
示例中的 wrangler 命令都应通过该项目执行方式运行；先检查已安装版本和 --help。
只有需要且项目未安装时才加入开发依赖，不自动全局安装或升级已有版本。
部署前用 whoami 核对 CLI 身份；若 CLI 未登录，在用户需要该操作时执行 wrangler login
并由用户完成浏览器授权。纯本地构建/类型生成不要求先连接云账户。

执行部署前确认目标项目、账户和环境，并先完成适用的本地校验或 deploy --dry-run。
MCP execute 代码应返回必要结果，遵循实际 schema 与上传格式；不要把构建目录绝对路径当作
远程服务器能访问的文件。对过大产物选择已支持的上传/CLI 工作流，并报告真实部署结果。

## 其他 Skills

包内保留 cloudflare、wrangler、agents-sdk、durable-objects、sandbox-sdk、
workers-best-practices、building-ai-agent-on-cloudflare、building-mcp-server-on-cloudflare。
从插件注册的 Skill 入口加载，参考资料相对当前 Skill 文件解析。
生成你自己的 MCP server 后，它是独立服务，需要独立测试和连接；Cloudflare App 只连接
官方 Cloudflare API MCP。web-perf 未包含在此包，页面性能审计需使用可用的 Chrome DevTools 插件。
上游 API/CLI 示例作为起点，执行前优先核对当前官方文档、项目依赖和工具 schema。
