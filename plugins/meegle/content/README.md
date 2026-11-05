# 飞书项目

Pilkod 国内官方 Marketplace Plugin，版本 `0.1.2`，分类 `Office`，仅向 Desktop 分发。包含官方 Meegle 的一个完整 Skill（27 个上游文件）与同步 `SessionStart` Hook，无 App/Connector 或 MCP 声明。分发范围由仓库 catalog 的 `deliveryTargets: ["desktop"]` 声明，不写入 manifest。

## 使用

- 查看我在飞书项目中本周的待办工作项。
- 查询飞书项目中这个需求的节点和排期。
- 统计飞书项目中团队本月的工作量。

本插件聚焦飞书项目（Meego/Meegle）的工作项、流程、排期、工时和视图；普通飞书任务/待办由 `lark-task` 处理。默认中文、国内 `project.feishu.cn`，已有 profile 或明确 host 优先，站点不匹配会停止而不改写配置。

## CLI 与授权

Hook 只检查 PATH 和 `~/.minimax/bin/meegle`（Windows：`%USERPROFILE%\.minimax\bin\meegle.exe`），不会联网、运行 CLI、下载、登录或处理凭据。缺失时向模型提供安装说明路径；终端 PATH 已有 CLI 则复用。

安装使用固定 CLI-only 命令 `npm install -g @lark-project/meegle@1.0.26`，不安装另一份全局 Skill。无 Node 时可从已验证的官方 npm 归档提取独立二进制并校验 SHA-256。两平台步骤与绝对路径复用见 [CLI 准备说明](skills/meegle/references/minimax-code-cli-setup.md)。插件 Hook 和独立二进制不依赖 Python；npm 入口要求 Node >=16。

Meegle 的认证独立于 lark。非 TTY 使用两阶段 device-code，由用户完成授权；`auth status` exit 2 网络异常不强迫重新登录。不读取、迁移或输出凭据。不自动创建 AI handoff 链接或修改用户偏好；明确请求的操作仍服从宿主授权边界。

## 来源与适配

- 官方仓库：[larksuite/meegle-cli](https://github.com/larksuite/meegle-cli)，固定 commit `e5ca19052b81cbba99c48ef0eab1f515552076e1`，配套 npm `1.0.26`。
- 完整复制 `skills/meegle` 与 [MIT LICENSE](LICENSE)。仅修改技能触发/宿主边界、auth guard、CLI 前置说明与 handoff 自动行为；其余业务参考保持上游内容。具体变更记录见 [upstream.json](upstream.json)。
- 图标原样采用[飞书项目官网](https://project.feishu.cn/)作为 icon、shortcut icon、og:image 引用的[官方 PNG](https://sf3-cn.feishucdn.com/obj/meego-static/front/static/20251121-114942.png)，不是通用飞书 Logo；SHA-256 已记录。
- Hook 遵循 `lark@0.1.4` 的 POSIX/PowerShell 本地检测约定，支持带空格路径与 JSON 转义。

## 验证范围

包 validator、引用闭包、图标完整解码和 POSIX Hook smoke 在仓库开发环境验证；独立二进制在 macOS arm64 验证 `--version` / `auth login --help`。Windows Hook 需要真实 Windows/PowerShell 运行验证；业务权限、真实 device-code 登录与服务端命令未使用用户账号测试。
