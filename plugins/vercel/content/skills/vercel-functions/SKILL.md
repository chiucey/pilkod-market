---
name: vercel-functions
description: 开发或排查部署在 Vercel 的 Functions，包括运行时选择、流式响应、后台任务、超时、冷启动和区域配置。已有 Vercel 项目或用户明确选择 Vercel Functions 时使用；不将普通 API、Agent 或模型调用迁移到 Vercel。
---

# Vercel Functions

> Pilkod 根据 vercel/vercel-plugin v0.54.1 的 vercel-functions 指引改写；保留框架和运行时选择，补充资源边界、数据保护和针对性验证。来源与许可见包根 THIRD-PARTY-NOTICES.md。

先读取 [操作约定](../../references/operations.md)。纯代码分析无需登录；涉及账号、日志或部署时再核实绑定与权限。

## 确定执行模型

1. 读取目标应用的依赖、锁文件、路由入口、运行时声明及 Vercel 配置，区分框架生成的 Functions、独立 API Functions 和 Routing Middleware。
2. 按安装版本检查 handler 签名、请求/响应类型、流式接口和配置位置。Node.js Functions 可支持流式响应；不要仅为流式需求切换到 Edge。
3. 保留当前运行时，核实依赖所需的 Node.js API、原生模块、文件系统和网络能力。只有明确需求及兼容性证据支持时才提出迁移，并说明影响和回退路径。
4. 区域、时长、内存、并发、负载大小和可用特性受运行时、项目设置与套餐影响。以当前官方文档和项目实际配置为准，不把通用示例数值当作项目配额。

## 实现与排障

- 鉴权和输入校验放在受信任的服务端边界。限制输入大小和上游请求时间；不把客户端传入的用户标识当作授权依据。
- 数据库客户端按依赖推荐方式复用连接，结合并发与连接池限制评估；不假定单次实例只处理一个请求，也不在共享内存保存跨请求的用户秘密。
- 临时文件和进程内状态只用于允许丢失的短期工作；持久化需求先检查现有存储设计，参考 [存储指引](../vercel-storage/SKILL.md)。
- 流式响应处理取消、异常和背压；响应头与错误状态在提交响应前确定。客户端断开、代理缓冲和最长执行时间仍需考虑。
- 使用框架或平台支持的响应后任务机制时，核实版本和生命周期。响应后任务仍有时间限制；需要持久执行、重试或排程的工作应评估现有队列/任务服务，不默认新增供应商。
- 超时先分解数据库、外部 HTTP、冷启动与应用计算耗时，再判断是否调整配置。增加 `maxDuration` 不能解决无限等待、连接泄漏或不可重试的副作用。
- 日志按 [CLI 指引](../vercel-cli/SKILL.md) 限定部署和时间窗口，脱敏后分析。写操作的重试需考虑幂等键和重复执行风险。

## 检查与交付

复用项目现有的相关构建、类型检查和行为测试；根据实际变更检查成功、异常、鉴权及取消等关键路径，不默认新增测试框架或整包测试。区分本地结果与 Vercel 运行结果；生产日志读取遵守权限，实际部署走 [部署确认流程](../deployments-cicd/SKILL.md)。

输出当前运行时与框架版本、定位依据、变更文件、已执行检查和仍需真实环境确认的限制。涉及区域或资源配置时说明成本与延迟影响。

## 官方资料

- [Functions](https://vercel.com/docs/functions)
- [运行时](https://vercel.com/docs/functions/runtimes)
- [限制](https://vercel.com/docs/functions/limitations)
- [流式响应](https://vercel.com/docs/functions/streaming-functions)
- [Fluid compute](https://vercel.com/docs/fluid-compute)
