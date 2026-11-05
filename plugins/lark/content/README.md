# 飞书

Pilkod 国内官方 Marketplace Plugin，版本 `0.1.4`，分类 `Office`，仅向 Desktop 分发。包含下方固定上游 commit 的全部 28 个 `lark-*` Skills 和一个同步 `SessionStart` Hook；没有 MCP 或 App/Connector 声明。

## 使用

在 Pilkod 中新建任务，例如：

- 查看我今天的飞书日程和未完成任务。
- 阅读这份飞书文档并总结重点。
- 把这周的会议纪要整理成一份周报。

PATH 和独立二进制安装目录中都找不到 `lark-cli` 时，Hook 会把本插件的安装说明加入模型上下文。模型在需要执行飞书任务时通过普通终端工具安装并验证 CLI，再继续原任务。Hook 自身只查本地可执行文件路径，不下载、不安装、不登录，也不处理用户凭据。

Hook 在当前 PATH 找到可执行文件时不输出提醒。若只在 `~/.minimax/bin/lark-cli`（Windows 为 `%USERPROFILE%\.minimax\bin\lark-cli.exe`）找到独立二进制，则把绝对路径提供给模型，后续直接复用；不检查插件数据目录。应用配置和飞书授权按官方共享技能继续，需要用户完成对应浏览器交互。

## 本地测试重点

1. 本机 CLI 已在 PATH：飞书任务应复用它，不重复安装。
2. CLI 不在 Hook PATH，但在终端 PATH：模型应以实际终端结果为准。
3. CLI 完全缺失：提醒应引导安装，并在安装成功后继续原任务。
4. 没有 Node/npm：按固定版本的独立二进制下载说明安装，并校验 SHA-256。新会话即使 PATH 未变，也应识别该安装路径并引导复用。
5. 用户目录或 Plugin 路径含空格：提醒与命令路径仍应正确。
6. 验证配置和授权：不能把 CLI 已安装当作已经登录；未授权时展示官方授权链接与二维码。
7. Windows：验证 `commandWindows`、PowerShell 检测和独立二进制安装路径。

如果独立二进制安装目录中没有 CLI，可以通过缩小该次进程的 PATH 模拟缺失场景，无需卸载 PATH 中现有的 CLI。模拟测试只会输出提醒，不会安装。

## 来源与适配

上游：[larksuite/cli](https://github.com/larksuite/cli)，commit `30e95091fff14f9c5589eece2d66fce2d0065f48`，配套 CLI `1.0.93`。完整来源与图标记录见 [upstream.json](upstream.json)，上游许可证见 [LICENSE](LICENSE)。

28 个官方技能目录及其资源完整复制；仅在 `lark-shared/SKILL.md` 和其更新提示 reference 中增加 Pilkod 的安装与更新说明。另将 `lark-slides` 旧路径下内容为 Markdown 的 `iconpark-index.json` 替换为它指向的真实 JSON 索引，保留旧路径兼容性。导入时另清理了上游文件的行尾空白和末尾空行，Markdown 硬换行保留原语义；除此之外，业务技能内容保持上游原样。安装详情见 [CLI 准备说明](skills/lark-shared/references/minimax-code-cli-setup.md)。

图标原样采用[飞书开放平台](https://open.feishu.cn/)页面引用的[标准飞书 PNG 图标](https://lf-package-cn.feishucdn.com/obj/feishu-static/lark/open/website/share-logo.png)，尺寸为 700×700。来源和 SHA-256 记录在 `upstream.json`。

分发范围由国内仓库 `.pilkod-plugin/marketplace.json` 中的 `deliveryTargets: ["desktop"]` 声明。插件 manifest 不包含端分发字段。安装策略沿用默认的用户自主安装，不设为默认安装插件。
