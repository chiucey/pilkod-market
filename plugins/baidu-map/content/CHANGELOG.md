# Changelog

本项目版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## 1.2.0

### 变更

- 移除 `skills/bmap-cli/scripts/ensure-cli.sh` 安装脚本。Plugin 不再负责下载或安装 `bmap-cli`，改为直接检查 `BMAP_CLI` 环境变量或 PATH；未找到时输出提示并以退出码 2 停止。
- `bmap-cli` Skill 描述从「安装或定位」改为「定位已安装的」，`openclaw.requiresBins` 元数据一并移除。
- 版本升至 1.2.0。

## 1.1.0

### 变更

- 四个 Skill 改为并列自动发现，不再把 `bmap-cli` 设计成 plugin 入口或总分诊器。
- `bmap-cli` 只负责定位 CLI、登录、AK / SK、样式、配额、消费量和账户资源管理；业务 Skill 仅在缺少凭据时按需调用它。
- `baidu-ai-map` 明确为直接地理结果的默认路径，判断标准从”问题复杂度”改为”用户要答案还是代码”。
- `baidu-map-jsapi-gl` 与 `baidu-map-webapi` 分别收紧为浏览器前端和服务端代码任务，避免抢占普通地点、路线和天气请求。
- Skill 与文档 MCP 改为流程和事实的互补关系：本地 reference 处理常用模式，精确、缺失、版本相关或最新事实查询官方 MCP。
- 将 Agent Plan 接口细节下沉到按需加载的 reference，并压缩 WebAPI 主 Skill；四个 `SKILL.md` 均保持合理大小，避免加载时被截断。
- 移除校验器尚未接受的可选 `compatibility` frontmatter；运行依赖继续由 Skill 正文、README 与扁平 `metadata` 表达。
- README 增加面向接收方的完整安装步骤，并明确自然语言是正常入口，显式 `$skill` / `mcp://` 仅用于调试。

## 1.0.0

首个 Agent Plugins 1.0.0 版本。由原先散落在 `~/.agents/skills/` 下的四个独立
skill 加一份手工写入的 MCP 配置，重构为单一可移植 plugin 包。

### 新增

- `plugin.json`：符合 Agent Plugins 1.0.0 的闭合 manifest。
- `mcp.json`：以 stdio 传输声明 `baidu-maps-docs`。
- `bin/docs-mcp-proxy.mjs`：stdio ↔ Streamable HTTP 代理。上游
  `docs.map.baidu.com/mcp/` 用 `?ak=` 查询参数鉴权，而规范禁止在远程 MCP 的
  `url` / `headers` 中做占位符展开或内嵌凭据（§7.2.1），因此该端点无法直接以
  `streamable-http` 声明。代理在运行时从 `BAIDU_MAPS_DOCS_AK` / `BMAP_AK` 或本地
  `bmap-cli` 登录态解析 AK，凭据不落入包内任何文件。

### 修复

- `baidu-map-jsapi-gl`：frontmatter `name` 原为 `bmap-jsapi-gl`，与父目录名不一致，
  严格客户端会跳过该 skill。已改为 `baidu-map-jsapi-gl`。
- 全部四个 skill：`metadata` 原为嵌套对象（`openclaw.requires.env` 等），而 Agent
  Skills 规范只允许 string→string 扁平映射。已扁平化为 `openclaw.primaryEnv` 等
  键，环境依赖改用规范定义的 `compatibility` 字段表述。
- `baidu-ai-map`：原指向不存在的 `bmap-cli auth get-token`（CLI v1.0.1 无 `auth`
  子命令）。已改为 `ap list` 取 `data.api_key`，并补上「先查后建」约束——
  `ap create` 是重置语义，会立即作废账号在用的所有 SK。
- `baidu-map-webapi`：`recipes/` 并入 `references/recipes/`（规范只约定 `scripts/`
  `references/` `assets/`），并修正 25 处因移动而失效的相对引用。
- 凭据注入问题修复。

### 变更

- **单包双路径**：轻量路径（Agent Plan，仅需登录态、零 AK）与完整路径（写代码，需
  对应端 AK）合并在同一 plugin 中，不做拆分。`bmap-cli` skill 新增「能力分诊」一节
  作为唯一分流点；`baidu-ai-map` 与 `baidu-map-webapi` 各自声明边界，互相禁止替代。
  轻量路径明确禁止触发 `ak list` / AK 创建 / 询问 AK 类型——否则一个零配置请求会
  退化成申请凭据的对话。
- `bmap-cli` skill 移除「阶段一：环境准备」中的 `skills install` 与 `mcp install`
  步骤。plugin 安装器已负责 skills 分发与 MCP 注册，skill 再执行一遍会产生双份
  副本与版本漂移。
- 新增凭据输出纪律：`ap list` 输出含明文 SK，禁止整段回显。
- 移除原 `chmod 600 <mcp_config_path>` 补救步骤——AK 不再写入客户端 MCP 配置文件。
