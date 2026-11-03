# GitLab 插件

由 Pilkod 维护，支持 Desktop 与 Cloud，用于处理已接入 GitLab 实例中的代码、Issue、MR 和已有 CI 日志。

## 安装与连接

在官方插件市场安装并启用本插件，使用连接入口填写实例地址和个人访问令牌。

在宿主连接表单填写 GitLab 站点地址（例如 `https://gitlab.com`）或完整 API 地址（例如 `https://gitlab.com/api/v4`）和对应实例的 PAT，保留自建实例的路径和端口。实例必须已接入且远程服务可达；仅用户电脑可访问的内网不保证可用。
提交代码、MR 和评论需要 PAT 的 `api` 权限及相应项目角色，受保护分支仍遵守实例规则。更换实例通过重新连接完成；每个用户当前保留一个 GitLab 连接。

## 可以完成的任务

工作流程见 [GitLab 工作流](skills/gitlab-workflow/SKILL.md)。使用本插件无需另装 CLI 或本地 MCP 服务。

- 读取 Issue、MR 和代码，通过连接工具提交修复到新分支、创建或更新 MR，并确认远端提交和 MR 内容。
- 按请求添加评论并读回，分析已有 pipeline/job 的失败日志。

代码提交不会自动执行本地测试。具备可用工作区时执行相关测试，否则报告未测试。连接不会自动为终端的 git clone/push 配置身份。具体操作由用户当前请求、连接权限和实时可用工具决定；仅分析时不发评论。写入前核对目标与参数，写后回读；结果未知时先查询是否已生效，再决定重试。

## 图标来源

- 官方品牌页面：https://about.gitlab.com/press/press-kit/
- 原始下载：https://about.gitlab.com/images/press/gitlab-logo-500-rgb.png
- 资源：`官方 Logomark PNG`
- 取得日期：2026-09-15。`icon.png` 为官方 PNG 原字节，未重绘、转换或裁剪；无 darkIcon。

品牌标记版权与商标归其各自权利人，使用时遵循上述官方品牌说明。
