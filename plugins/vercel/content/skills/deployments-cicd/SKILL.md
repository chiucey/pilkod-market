---
name: deployments-cicd
description: 为用户已选择的 Vercel 项目执行部署预检、Preview 或 Production 发布、CI/CD 配置以及经确认的 promote/rollback。用户明确要求部署到 Vercel，或正在修改既有 Vercel 发布流程时使用；不接管其他平台或通用网站发布。
---

# Vercel 部署与 CI/CD

> Pilkod 根据 vercel/vercel-plugin v0.54.1 的 deployments-cicd、deploy 与 status 指引改写；补充首次生产部署、上传范围、确认和不确定结果处理。来源与许可见包根 THIRD-PARTY-NOTICES.md。

先读取 [操作约定](../../references/operations.md)，完成团队、项目、应用目录和 CLI 版本确认。

## 发布预检

1. 读取应用的构建脚本、锁文件、Vercel 配置和现有 CI。monorepo 明确目标 package 与 Dashboard 的 Root Directory；不为整个仓库擅自安装、构建或部署。
2. 检查工作区状态和 `.vercelignore` 等实际上传规则。CLI 源码部署使用本地文件，未提交改动也可能上传；Git 集成使用目标提交；`--prebuilt` 使用本地 `.vercel/output`。如存在未提交改动，说明不能仅用 HEAD 标识发布内容，不要求自动 commit。
3. 确定用户要发布的环境、绑定域名及部署保护。**Vercel 新项目首次部署会是 Production，即使未传 `--prod`；只有已有首次生产部署后才能按常规 Preview 规则判断。** 无法确认是否首次部署时停止，先核实；用户只同意 Preview 时不能擅自执行首次生产部署。
4. 检查构建和运行所需变量的名称与作用域，遵循 [环境变量指引](../env-vars/SKILL.md)。保持 Preview 与 Production 数据隔离。
5. 本地检查使用项目已有的相关命令；真实部署需用户授权，不能为了“测试插件”创建部署。

## 发布计划与确认

执行前列出团队、项目、应用目录、源码/预构建来源、实际环境、文件上传范围、可见性、生产域名影响和可能的资源费用。通过宿主确认工具获得此次发布的明确同意。`--yes` 仅解决 CLI 非交互问题，不是发布授权。

以下命令只在目标核实、帮助确认及用户确认之后使用：

| 目标 | 命令与限制 |
| --- | --- |
| 已有项目的 Preview | `vercel deploy`；仍需核实环境，不适用于未经同意的首次生产部署 |
| Production | `vercel deploy --prod`；明确生产域名影响 |
| 上传已构建产物 | `vercel deploy --prebuilt`，Production 加 `--prod`；产物环境必须与发布目标一致 |
| 暂不分配生产域名 | `vercel deploy --prod --skip-domain`；仍使用生产环境并可能访问生产数据 |

显式补充当前 CLI 支持的非交互及已确认的 scope 参数，避免隐式 link/create。不要自动添加 `--force`、`--public` 或禁用部署保护。

## 预构建与 CI

- 优先保持现有 Git 集成或 CI 方式；避免 Git 集成和自建 CI 对同一提交重复发布。
- 需要本地构建时，按目标环境执行 `vercel pull`、`vercel build` 和 `vercel deploy --prebuilt`。Preview 的分支变量必须在构建前拉取；生产构建与上传参数保持一致。
- `vercel pull` 会写入项目配置及环境文件；先按环境变量指引检查路径、敏感信息和覆盖影响。上传阶段增加分支元数据不能改变已烘焙进产物的变量。
- `--prebuilt` 有系统环境变量、框架和 Skew Protection 限制，使用前读对应版本文档；保留构建产物与源码来源记录。
- CI 凭据使用平台受保护的 Secret；`VERCEL_TOKEN` 不放命令参数或 YAML 明文。组织和项目标识明确配置，生产发布保留人工审批；不向不可信 fork/PR 暴露凭据。
- 只在用户要求范围内修改 pipeline，不关闭已有安全门禁。

## 发布结果与回退

从实际 CLI 输出提取 deployment URL/ID，随后 inspect 该部署并核对环境和域名。构建失败读构建日志，运行错误按 [CLI 日志指引](../vercel-cli/SKILL.md) 查询限定窗口；未 READY 时报告当前状态，不宣称发布成功。

超时或连接中断先查部署列表和目标状态，再判断是否需要重试。`promote`、`rollback` 会改变生产流量，先检查目标及当前版本语义，再单独确认具体操作；不把失败后的回滚视为默认授权，也不承诺 Preview 提升一定复用同一构建。

结果包括项目、部署 ID/URL、源码来源、实际环境、状态、已检查项目及未检查项。只有实际访问了页面/API 才报告对应业务检查结果；日志检查说明真实时间窗口。

## 官方资料

- [deploy](https://vercel.com/docs/cli/deploy)
- [首次部署与环境](https://vercel.com/docs/deployments/environments#first-deployment)
- [build](https://vercel.com/docs/cli/build)
- [promote](https://vercel.com/docs/cli/promote)
- [rollback](https://vercel.com/docs/cli/rollback)
