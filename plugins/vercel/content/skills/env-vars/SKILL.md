---
name: env-vars
description: 管理已选定 Vercel 项目的 Development、Preview、Production 环境变量，检查变量缺失、分支作用域、CLI 拉取和更新。仅在 Vercel 环境配置任务中使用；普通 .env 编辑、模型密钥配置或其他平台变量管理不触发。
---

# Vercel 环境变量

> Pilkod 根据 vercel/vercel-plugin v0.54.1 的 env-vars 与 env 指引改写；收窄触发范围，增加秘密保护、版本相关拉取行为和写入确认。来源与许可见包根 THIRD-PARTY-NOTICES.md。

先读取 [操作约定](../../references/operations.md)，确认团队、项目、应用目录以及 CLI 参数支持。

## 只读检查

1. 从代码引用和不含秘密的变量模板提取期望变量名，按任务范围检查；读取敏感文件仍由宿主权限控制。
2. 使用 `vercel env ls <environment>` 查看目标作用域，Preview 还要核实对应分支。只报告变量名、环境、存在/缺失状态，不输出值。
3. 区分构建时变量、运行时变量和会进入浏览器的公开变量。`NEXT_PUBLIC_`、`VITE_` 等公开前缀中不得放密钥、私有数据库凭据。
4. 没有权限或 Secret 值不可读取时标为不可确认，不把它推断为变量不存在。

## 拉取到本地

`vercel env pull <file>` 用于普通本地工具；`vercel pull` 则提供 `vercel build/dev` 使用的项目设置与环境。选择与用户目标对应的一种。

拉取前确认目标环境和 Preview 分支。默认只考虑 Development，本地调试不自动获取生产数据凭据。下载生产或 Preview 配置需要明确授权。

- 列明目标路径及是否已存在；检查 Git ignore 和 tracked 状态。路径被 Git 跟踪或无法保证秘密不会进入提交时，先解决文件保护问题。
- **文件合并/覆盖行为随 CLI 版本变化。** 当前官方文档描述保留部分本地独有变量，但不能据此假定旧版也安全；先查安装版本帮助/文档。
- 优先拉取到目标项目内新的、受保护且被忽略的文件，核对变量名后再决定如何替换既有文件。写入或覆盖前说明影响并确认；不默认加 `--yes` 覆盖。
- 检查宿主用户可读写权限，避免组用户/其他用户访问秘密文件。临时秘密文件按宿主允许的安全方式管理，不写入插件包或任务报告。
- Secret 可能不可回读或只得到占位符，拉取成功不代表所有凭据可用。保留独立 Development 值，不把生产 Secret 复制到调试环境。
- 不通过 `source`、`eval` 或拼接 shell 的方式执行 `.env` 内容。

## 添加、更新和删除

先说明团队、项目、变量名、目标环境、可选 Preview 分支和影响，取得针对变更的确认，再检查相应 `--help`。

```text
vercel env add <name> <environment> [gitbranch]
vercel env update <name> <environment> [gitbranch]
vercel env rm <name> <environment> [gitbranch]
```

这些是命令形态，执行时必须使用当前 CLI 支持的非交互形式。不可省略环境以隐式影响所有环境；批量修改逐项列出作用域。

秘密值由用户通过 Dashboard、可信终端或已授权的安全输入源提供。支持 stdin 时直接从受保护文件/秘密管理器传入，不先在 Agent 输出中读取，不使用带明文秘密的 `echo`、`--value` 或 `--token`，不让用户把秘密粘贴进聊天。shell 重定向方式按当前平台选择。

只有明确受授权且支持的非交互输入可用时才执行；需要交互输入但宿主无法接管时，交给用户在可信终端完成。不要为了自动化降低 Secret 类型或平台策略。

## 生效与交付

修改后只回读变量名、类型和环境。远端变量修改通常需要新部署才生效，说明这一点，但不要未经确认继续部署。输出已变更键名、作用域、需要用户完成的操作和未验证内容。

## 官方资料

- [环境变量](https://vercel.com/docs/environment-variables)
- [env 与拉取行为](https://vercel.com/docs/cli/env)
- [pull](https://vercel.com/docs/cli/pull)
- [Secret 与环境策略](https://vercel.com/docs/environment-variables/sensitive-environment-variables)
