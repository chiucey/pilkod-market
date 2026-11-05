---
name: routing-middleware
description: 为 Vercel 项目配置和排查路由、redirect、rewrite、Routing Middleware，以及 Next.js 对应版本的 Middleware/Proxy。用于 Vercel 访问分流、鉴权前置、国际化和缓存相关路由问题；不接管与 Vercel 无关的通用中间件任务。
---

# Vercel 路由与 Middleware

> Pilkod 根据 vercel/vercel-plugin v0.54.1 的 routing-middleware 指引改写；增加框架版本识别、鉴权与缓存边界。来源与许可见包根 THIRD-PARTY-NOTICES.md。

先读取 [操作约定](../../references/operations.md)。代码排查先读配置；需要远端日志或发布时再核实项目与权限。

## 先画清请求路径

1. 检查框架版本、路由树、`vercel.json`、框架配置、Middleware/Proxy 文件和现有测试。区分 Vercel 平台 Routing Middleware、框架路由层和最终 Functions handler。
2. 按项目实际版本选用 `middleware.ts` 或 `proxy.ts`、运行时和配置 API；不要在旧版 Next.js 项目直接改名为 `proxy.ts`。升级或迁移应单独评估。
3. 按官方文档核实 headers、redirects、rewrites、文件系统路由及框架规则的优先级，写出问题请求经过的各层，避免依靠记忆叠加相互覆盖的规则。
4. 明确目标：改变地址用 redirect，保留客户端地址转发用 rewrite；仅修改响应头时优先使用现有静态配置。动态判断才引入 Middleware/Proxy。

## 安全实现

- matcher 收窄到需要处理的路径；按实际框架排除静态资源、图片、健康检查等例外。注意尾斜杠、locale、basePath 与重复重定向造成的循环。
- 对登录回跳、上游地址和自定义 host 做 allowlist/可信源校验，避免开放重定向及 SSRF；不把用户输入直接拼成转发目标。
- Middleware 可以做前置路由判断；受保护的数据读取和写入仍在最终服务端执行身份、权限和租户校验，不能仅依赖客户端 Cookie 存在。
- 不信任客户端传入的内部身份头。向下游传递必要信息前清理冲突头；不把 Cookie、Authorization 或私有请求头整体复制到公开响应。
- 按用户、租户、locale 等维度分流时，检查 CDN/框架缓存键与响应策略，避免将一个用户的私有响应缓存给其他人。外部 rewrite 还需核实凭据和敏感参数会发送到哪里。
- 在匹配广泛的热路径中避免慢查询、长任务和无上限外部请求。按实际运行时能力实现；需要后端业务逻辑时使用已有 handler。
- routing 配置、鉴权与缓存变更按风险验证；不要通过放宽 matcher、关闭鉴权或公开缓存来掩盖错误。

## 检查与交付

复用相关路由测试，覆盖此次改动涉及的正常路由、未授权、静态资源、循环及缓存隔离路径。只运行相关检查；远端访问只使用已授权地址，发布走 [部署流程](../deployments-cicd/SKILL.md)。

结果说明实际框架/版本、变更层、命中条件与例外、鉴权与缓存影响，以及本地和远端分别检查了什么。不要把配置可解析描述为线上流量已经按预期路由。

## 官方资料

- [Routing Middleware](https://vercel.com/docs/routing-middleware)
- [项目配置](https://vercel.com/docs/project-configuration)
- [Next.js Proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy)
- [Next.js Middleware v15](https://nextjs.org/docs/15/app/api-reference/file-conventions/middleware)
