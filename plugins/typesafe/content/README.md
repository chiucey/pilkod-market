# TypeSafe / Jev

将 TypeSafe 官方 `typesafe-ai` Skill 封装为 MiniMax Plugin V1，帮助 Agent 使用 Jev / System One
设计和实现结构化判断。支持 Desktop 与 Cloud，由用户按需安装。

## 使用

安装并启用插件后，向 Agent 提出具体需求，例如“用 TypeSafe Jev 实现客服工单分类与路由，
将不确定结果交给人工处理”。运行时 Skill 名称为 `typesafe:typesafe-ai`。

Skill 指导 Agent 查阅最新官方文档，选择 Choice、Score 或 Noul，设计输入和问题，组合判断，
并在实际业务数据上验证结果。上游 Skill 原文保持不变。

## 依赖与边界

- 包内只有一个 Skill，没有 App、MCP server、Hook 或安装脚本；安装本身不调用 Jev API。
- 读取最新文档需要访问 `https://docs.typesafe.ai/`；无法联网时，上游指引要求说明限制，
  使用可用本地文档或 SDK 类型，不编造版本相关细节。
- 实际运行生成的集成代码需要用户自己的 TypeSafe 访问权限和 API key，并按所选官方 SDK
  配置运行环境。API 调用可能产生费用，提交的判断内容会发送给 TypeSafe。
- 通过目标应用的环境变量或服务端凭证管理配置 API key，不写入插件、源码或对话；Web 应用
  的凭证保留在服务端。
- 插件不自动安装 SDK、不配置凭证，也不替换 MiniMax Code 的主模型、权限系统或压缩流程。

来源版本、许可证与图标出处见 [ATTRIBUTION.md](ATTRIBUTION.md)。
