# 来源与适配

- 上游：[openai/plugins](https://github.com/openai/plugins/tree/1dc195897af4161d039b80d8471ec0a10c9bbc89/plugins/cloudflare)，固定提交 `1dc195897af4161d039b80d8471ec0a10c9bbc89`，插件版本 0.1.2。
- 复制 8 个 Skills 及其参考文件和 Cloudflare 原始 PNG 图标；web-perf、commands、Codex manifest 与直连 MCP 配置未纳入包。
- MiniMax 包版本独立为 0.1.0。原始技术内容来自 Cloudflare；MiniMax Code 负责本包格式及宿主指引适配，不代表上游认证。
- 上游 manifest 声明 MIT；cloudflare、wrangler、agents-sdk 目录分别附带 Apache-2.0 的 LICENSE.txt，已原样保留这些文件及原有声明，不把所有文件重新标成单一许可证。修改后的文件通过适配段落及下列清单标识。
- 新增原生 manifest、App 引用、连接指引和中/英文产品说明。服务端的 OAuth/MCP 配置由独立 Apollo 配置管理，包内无 token 或 client_id。
- 原文件 SHA-256、复制路径及是否修改见 upstream-source.json，供后续升级核对。

## 修改的上游文件

- `skills/agents-sdk/SKILL.md`
- `skills/building-ai-agent-on-cloudflare/SKILL.md`
- `skills/building-mcp-server-on-cloudflare/SKILL.md`
- `skills/building-mcp-server-on-cloudflare/references/examples.md`
- `skills/building-mcp-server-on-cloudflare/references/oauth-setup.md`
- `skills/building-mcp-server-on-cloudflare/references/troubleshooting.md`
- `skills/cloudflare/SKILL.md`
- `skills/durable-objects/SKILL.md`
- `skills/sandbox-sdk/SKILL.md`
- `skills/workers-best-practices/SKILL.md`
- `skills/wrangler/SKILL.md`


## 格式整理

以下文件仅移除上游残留的行尾空白或补齐末尾换行：

- `skills/durable-objects/references/workers.md`
- `skills/durable-objects/references/testing.md`
- `skills/durable-objects/references/rules.md`
- `skills/cloudflare/references/snippets/api.md`
- `skills/cloudflare/references/snippets/configuration.md`
- `skills/cloudflare/references/agents-sdk/README.md`
- `skills/cloudflare/references/argo-smart-routing/api.md`
- `skills/cloudflare/references/argo-smart-routing/configuration.md`
- `skills/cloudflare/references/observability/api.md`
- `skills/cloudflare/references/observability/configuration.md`
- `skills/cloudflare/references/turnstile/api.md`
- `skills/cloudflare/references/turnstile/configuration.md`
- `skills/cloudflare/references/waf/api.md`
- `skills/cloudflare/references/waf/README.md`
- `skills/cloudflare/references/waf/patterns.md`
- `skills/cloudflare/references/waf/configuration.md`
- `skills/cloudflare/references/bindings/api.md`
- `skills/cloudflare/references/bindings/patterns.md`
- `skills/cloudflare/references/bindings/configuration.md`
