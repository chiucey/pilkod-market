---
name: vercel-storage
description: 为 Vercel 项目选择、集成或排查 Blob、Edge Config 及已选定的 Marketplace 数据服务，覆盖上传访问控制、配置读取和数据库连接。仅在用户明确使用 Vercel 存储能力或已有 Vercel 存储集成时触发；保留既有数据库和供应商。
---

# Vercel 存储

> Pilkod 根据 vercel/vercel-plugin v0.54.1 的 vercel-storage 指引改写；增加供应商选择、资源费用、数据隔离及删除确认约束。来源与许可见包根 THIRD-PARTY-NOTICES.md。

先读取 [操作约定](../../references/operations.md)。代码分析无需创建云资源；账号操作前核实团队、项目和环境。

## 识别需求与现状

1. 读取依赖、现有数据访问层、变量名称与配置模板，先确认项目已有的对象存储、配置系统和数据库。不要输出连接串或 Secret 值。
2. 区分文件对象、动态配置和事务数据：Blob 用于文件对象；Edge Config 用于配置读取；需要查询、事务和约束的业务数据沿用或评估数据库。
3. 用户要求选型时，列出访问模式、区域、延迟、一致性、容量、保留周期、费用与迁移成本。Vercel Marketplace 服务可能由第三方提供，按当前供应商文档与账户套餐核实。
4. 不为使用 Vercel 自动替换既有数据库，也不假定历史 KV/Postgres 产品名称对应当前新建入口。安装 SDK 前检查仓库依赖与包管理器。

## Blob 文件

- 创建前确认公有/私有访问模式及当前 SDK、套餐支持。公有 URL 可泄露内容，随机文件名不构成鉴权；私有读取按受支持接口在服务端校验应用权限。
- 客户端上传凭证由服务端在鉴权后签发，限制用户、路径、大小、内容类型和有效期。不得把 `BLOB_READ_WRITE_TOKEN` 或等价管理凭据发到浏览器。
- 不信任客户端声明的 MIME 或文件名；按任务需要验证内容。处理覆盖、重名、异常和重复回调，敏感文件设置合适的缓存与下载策略。
- 删除、批量清理和更改可见性前列明确切对象/前缀、影响及可恢复性，单独确认；模糊匹配不能直接扩大删除范围。

## Edge Config 与数据库

- Edge Config 的读写路径、传播延迟与容量以当前文档为准，不能假定写入后所有区域立即一致。配置中只放用途明确的数据，敏感值继续使用受保护的环境变量或秘密服务。
- 数据库连接复用框架/驱动推荐模式，核实 pooling、区域和并发限制。读写超时与重试应匹配幂等性，不用无上限重试隐藏错误。
- Development、Preview、Production 隔离凭据及数据。检查 Preview 是否误连生产，不为了让构建通过而复制生产连接串。
- schema migration、数据导入/迁移和清理分别制定目标、备份/恢复措施、验证范围与确认步骤；不在部署或安装 SDK 的附带操作中执行。

## 资源变更与交付

新建存储、连接 Marketplace 服务、增加付费计划或修改访问策略前，说明供应商、团队、项目、环境、区域、计费及会新增的变量，取得明确确认。若 CLI 不支持可靠的非交互流程，交给用户在 Dashboard 完成，不猜测命令。

绑定或更新变量遵循 [环境变量指引](../env-vars/SKILL.md)；代码发布遵循 [部署流程](../deployments-cicd/SKILL.md)。检查复用相关测试或明确授权的非生产数据，不能默认在生产做写入/删除探测。

报告已选服务、权限与环境边界、实际资源标识、已做检查和费用/容量待确认项。未创建资源、未迁移数据或未进行真实读写时如实注明。

## 官方资料

- [Storage](https://vercel.com/docs/storage)
- [Blob](https://vercel.com/docs/vercel-blob)
- [Edge Config](https://vercel.com/docs/edge-config)
- [Marketplace](https://vercel.com/docs/marketplace)
