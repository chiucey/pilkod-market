# Vercel

由 Pilkod 维护的 Vercel 适配插件，通过按需加载的 Skills 和当前执行环境中的 Vercel CLI 支持应用开发、部署与排障。

## 安装与使用

在 Pilkod 桌面端或云端的插件市场安装并启用 Vercel，分发范围为 `desktop` 和 `cloud`。首版发布范围为 CN 测试市场，按用户选择安装（`USER_MANAGED`）。合入 `dev` 后可进行测试安装；生产市场需完成测试验收并单独晋级。

代码分析与实现指导可直接使用。查询账号资源或部署时，需要当前执行环境中可用的 Vercel CLI、用户授权且有目标项目权限的身份，以及目标项目的依赖环境。插件不会自动安装 CLI、登录账号、创建资源或发布应用；CLI 安装方式和版本由项目约定决定。

云端在当前沙箱的项目目录执行命令，独立检查 CLI、网络和凭据。桌面文件、绑定与登录状态不会自动同步。账号操作需要宿主实际支持的安全凭据注入或授权流程；条件不足时只进行代码指导，并交由用户在可信终端或 Dashboard 完成账号操作。

示例：

- 检查这个 Vercel 项目的部署状态和最近的错误日志。
- 把这个应用部署到 Vercel，先告诉我要发布到哪个项目和环境。
- 检查 Vercel Preview 环境缺少哪些变量，不要显示密钥值。

## 能力

| Skill | 工作范围 |
| --- | --- |
| `vercel-cli` | 项目核实、部署状态、构建与运行日志、CLI 排障 |
| `deployments-cicd` | 部署预检、Preview/Production、预构建、CI/CD、发布与回退确认 |
| `env-vars` | 环境变量名称与作用域检查、安全拉取和经确认的更新 |
| `vercel-functions` | Functions 运行时、流式响应、超时、资源与连接管理 |
| `routing-middleware` | 路由、redirect/rewrite、按版本适配 Middleware/Proxy |
| `vercel-storage` | Blob、Edge Config 和既有数据库/Marketplace 服务的集成指引 |

所有 Skills 共用 [操作约定](references/operations.md)。部署、环境变量写入、域名和资源变更在核实目标及影响后确认；日志和结果脱敏。已有框架、模型服务、数据库及发布方式保持不变，除非任务要求调整。

## 依赖与边界

- 包只包含 Skills、参考文档与图标，无自动 Hook、遥测、MCP、App、Host Binding 或后台脚本。
- Vercel CLI 的登录授权独立于插件安装；不依赖 Vercel MCP 的客户端资格或 OAuth 配置。
- CLI 参数、平台配额及 SDK API 按用户安装版本与当前官方文档核实。macOS、Windows 的命令形式遵循当前宿主 shell。
- 用户选择 Vercel 或任务明确涉及已有 Vercel 项目时触发；普通网站发布、创建 Agent、模型配置和通用 `.env` 编辑保留宿主原有工作流。
- 未接入上游 specialist agents、commands、自动上下文注入、eve 或 AI Gateway 默认选型；React 性能优化继续使用市场现有对应插件。

## 来源与维护

基于 `vercel/vercel-plugin` v0.54.1 固定提交精选、改写并适配 Pilkod Plugin V1。来源、修改范围与第三方归属见 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)，Apache-2.0 全文见 [LICENSE](LICENSE)。Vercel 名称和图标用于识别服务，本包由 Pilkod 适配维护。

后续升级先对照固定上游提交与当前官方文档，逐项审查能力、触发范围、权限及依赖变化，再增加包版本并通过市场校验。结构和打包检查覆盖静态契约，Desktop 实际安装、模型触发、账号授权与真实部署需独立验收。
