# Cloudflare

在 Pilkod 中连接 Cloudflare，查询云资源，并结合 Workers、Wrangler、Agents SDK、D1、KV、R2 等参考指引开发应用。

## 开始使用

1. 从官方插件市场安装，在详情页连接 Cloudflare App，并在浏览器中确认所需权限。
2. 打开项目，说明目标；操作前确认项目账户、Worker 名和环境。
3. 工具或权限不足时按实际错误处理。连接成功不等于已授权所有资源写入。

包含 1 个 App、8 个 Skills，分类 Code。本地导入会忽略 App 引用，连接能力需通过官方市场安装使用。点击连接使用服务端管理的 OAuth。
详见[连接与使用指引](skills/cloudflare/references/minimax-connection.md)。

Wrangler CLI 有独立的安装与登录状态；需要其部署流程时按项目依赖执行。
本包不包含 Chrome DevTools；页面性能审计请使用相应插件。
上游技术资料保留原文，操作前核对当前文档和实际工具 schema。

来源、许可证和适配记录见 [CREDITS.md](CREDITS.md) 与 [upstream-source.json](upstream-source.json)。
