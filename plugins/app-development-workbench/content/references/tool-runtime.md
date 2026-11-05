# 运行环境与工具发现

插件声明本地 stdio XcodeBuildMCP 2.7.0，启用 simulator、ui-automation、debugging、logging 工作流，关闭其 Sentry 遥测。MCP 程序通过 npx 获取，未捆绑 Xcode、Simulator、ETTrace 或原生二进制。版本升级必须重新验证并更新插件版本。

上游 2.7.0 文档的最低要求为 macOS 14.5、Xcode 16、Node.js 18；仍需核对用户当前工程 SDK、架构和 runtime。官方包采用 desktop 分发，该字段不等于 macOS 过滤。在 Windows/Linux 上原型和服务端技能可按环境使用，但不能声称本地 iOS 构建可运行。

## 前置检查

```bash
uname -s
node --version
xcode-select -p
xcodebuild -version
xcrun simctl list devices booted
```

没有 Xcode 时报告依赖缺失，不擅自切到别的工程。npx 下载需要网络；旧缓存损坏时保留错误证据，可用独立 npm cache 验证相同版本，不能清空整个用户缓存。

## MCP 路径

宿主会为 MCP 工具分配名字。先通过实际工具发现获取 list_sims、session defaults、build/run、UI 和日志能力及 schema，再调用对应工具；语义名不等于固定宿主前缀。配置存在但没有工具时检查 MCP 启动日志、依赖、工作流和宿主是否需重新启用/重启。

测试连接先 initialize → initialized → tools/list；再做只读的模拟器发现验证。此检查不代表构建或 UI 通过。不要把另一进程 tools/list 结果声称为 MiniMax 宿主内已加载。

## CLI 备选

MCP 暂不可调用时，在用户已授权的开发范围使用 CLI 完成可独立的检查，说明路径区别：

```bash
npx -y xcodebuildmcp@2.7.0 --help
npx -y xcodebuildmcp@2.7.0 tools
npx -y xcodebuildmcp@2.7.0 simulator --help
```

在执行具体命令前查看该工具 help。Apple CLI 可用于 xcodebuild/simctl 复现，但所有目标、输出目录和 Bundle ID 都来自本次发现。日志/调试的 CLI daemon 有独立状态，不与宿主 MCP 会话混用。

浏览器优先用户现有桌面浏览器。镜像需要真实可用的桥接，不能用静态截图冒充实时预览。SwiftUI 热更新受工程和工具支持范围限制，没有实测不承诺。

来源：[MCP mode](https://www.xcodebuildmcp.com/docs/mcp-mode)、[Configuration](https://www.xcodebuildmcp.com/docs/configuration)、[Privacy](https://www.xcodebuildmcp.com/docs/privacy)。
