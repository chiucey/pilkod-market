---
name: vercel-cli
description: 使用 Vercel CLI 查询已选定 Vercel 项目的状态、部署和日志，处理项目绑定、CLI 配置及 Vercel 平台命令。仅在用户明确选择 Vercel 或任务涉及已有 Vercel 项目时使用；普通网站发布、创建本机 Agent 和通用开发任务不触发。
---

# Vercel CLI 与日志排障

> Pilkod 根据 vercel/vercel-plugin v0.54.1 的 vercel-cli 与 status 指引重新组织；修改了触发范围、账号边界和检查流程。来源与许可见包根 THIRD-PARTY-NOTICES.md。

先读取 [操作约定](../../references/operations.md)，完成 CLI 可用性、团队及项目确认。

## 选择工作流

| 用户目标 | 接下来读取 |
| --- | --- |
| 部署、CI/CD、promote、rollback | [deployments-cicd](../deployments-cicd/SKILL.md) |
| 环境变量查询、拉取或修改 | [env-vars](../env-vars/SKILL.md) |
| 函数实现、运行时错误、超时 | [vercel-functions](../vercel-functions/SKILL.md) |
| rewrite、redirect、Middleware、Proxy | [routing-middleware](../routing-middleware/SKILL.md) |
| Blob 或数据库接入 | [vercel-storage](../vercel-storage/SKILL.md) |

只读取与本次任务直接有关的指引。读取其他文件时相对当前 Skill 文件解析路径；shell 命令在用户项目中执行。

## 查询状态

先检查相应子命令帮助，再选择最小查询：

```bash
vercel list
vercel inspect <deployment-url-or-id>
vercel env ls <environment>
```

将列表中的部署与团队、项目、目标环境和用户提供的 URL/ID/提交对应起来。没有匹配结果时说明查询范围，不把其他分支最近的部署当成目标。环境变量列表只报告名称和作用域。

## 排查部署与运行错误

1. 确定是构建失败、运行错误、访问保护还是请求路由问题。
2. 构建失败：检查该部署状态，当前版本支持时使用 `vercel inspect <deployment-url-or-id> --logs` 读取构建日志。
3. 运行错误：使用明确 deployment 和时间窗口查询有限日志。当前 CLI 支持时：

   ```bash
   vercel logs --deployment <deployment-id> --level error --since 1h --limit 50
   ```

4. CLI 参数以实际安装版本帮助为准。优先一次性查询；不默认使用 `--follow`，避免任务永久等待。需要实时日志时明确持续时间和停止条件。
5. 结合错误时间、部署 ID、请求 ID、路由和代码定位第一个有证据的失败点，再提出最小修复。
6. 受保护部署优先使用用户已有授权以及当前版本的 `vercel curl` 能力；不得为了检查而关闭部署保护。浏览器检查使用宿主浏览器工具及其认证流程。

空日志只能说明指定时间和过滤条件下未发现记录，不能推出“没有故障”或“运行正常”。网络失败、账号权限问题与应用代码失败分别报告。

## 输出

简洁列出：目标项目/环境、部署状态、查询窗口、关键证据、定位结论、下一步。秘密和个人数据在展示前脱敏。若未访问业务页面或接口，明确说明业务功能尚未检查。

## 官方资料

- [CLI](https://vercel.com/docs/cli)
- [inspect](https://vercel.com/docs/cli/inspect)
- [logs](https://vercel.com/docs/cli/logs)
- [项目绑定](https://vercel.com/docs/cli/project-linking)
