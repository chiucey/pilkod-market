---
name: reverse-engineer-anything
description: 使用 REA 逆向分析原生二进制、.NET、JavaScript/Electron、应用包、Android、固件及明确请求的运行行为；用于追踪功能、比较版本、反编译和基于证据重建。不用于已有完整源码仓库的普通代码阅读。
---

# REA 逆向分析

本插件由 Inside 适配 MiniMax Code，使用 morluto/rea 的 MIT 开源工作流与固定发布版 rea-agents@6.4.0。上游版权见插件根目录 LICENSE。

## MiniMax Code 接入约定

插件已声明名为 rea 的 stdio MCP，禁止为此重复运行 `rea setup`、`rea mcp add` 或修改其他 Agent、全局 MCP、权限和配置。安装本插件不代表已安装原生分析器。Node.js 要求为 22.x >=22.19、24.x >=24.11 或 >=26；首次启动通过 npx 下载固定版本。原生分析另需现有 Hopper、Ghidra 或 IDA，Android 等能力按指南检查额外依赖，不承诺所有平台可用。

先读取 [上游完整工作流](UPSTREAM.md)，再按目标只读所需参考。UPSTREAM.md 与 references 保留英文原文及证据契约；其中跨客户端安装建议仅为上游参考，以本节的 MiniMax Code 接入约定为准。按用户当前语言回复，代码标识和工具名不翻译。

MCP 已可用时直接使用其实际工具名和 schema，不要每次重复 doctor。工具未加载时检查本插件启用状态及宿主诊断；若任务允许使用终端，可用 `npx -y rea-agents@6.4.0 mcp doctor --json` 区分启动、目录和版本问题。诊断失败需如实报告，不能靠切换 latest 或擅自改宿主配置绕过。

## 工作流

1. 确定用户提供的目标路径、应用和问题；不能从无关报告或附近文件擅自选择目标。普通源码分析使用仓库工具。
2. ASAR/已提取 JS/Electron 目录使用 `analyze_javascript_application`；.NET 使用 `inspect_managed_artifact`；APK 使用 `inspect_android_package`；原生二进制使用 `open_binary` 后聚焦函数与引用。iOS IPA 先用 `open_binary`、`inspect_artifact` 获取包清单，再将证据交给 `project_apple_application_graph` 查看扩展、框架和可执行文件候选，用 `inspect_plist` 核实声明；需要时提取并分析可用的 Mach-O。包结构分析不等于完整反编译，不能承诺恢复加密代码。Android 方法反编译需要另配 JADX MCP JAR 与 Java 17+。其他目标按上游路由表处理，以当前工具 schema 和会话可用性为准。
3. 大型 JS 应用先请求 `detail: "summary"`，保留 `parent_evidence_id`，用 `inspect_analysis_view` 分页，再按返回 node_id 追踪功能。不重复运行相同分析来获取截断输出。
4. 静态分析优先。运行时启动、附加进程、浏览器场景、设备操作或文件提取只在用户要求范围内进行，遵守宿主权限；不得将分析扩展到无关应用、凭证或数据。内置浏览器任务遵循宿主 Browser 规则，REA 不用于绕过它们。
5. 引用 Evidence ID、位置和哈希，区分观察、推断及未知；静态结果不是执行证据。需要重建时使用正常开发工具实现并测试，不宣称恢复了完整原始源码。
6. 汇总已回答和未回答的问题、依赖及覆盖边界；完成后关闭自己打开的原生分析会话。

## 按需参考

- JS/Electron、功能追踪、版本比较：[javascript-applications](references/javascript-applications.md)
- 原生、.NET、应用包与资源：[native-and-artifacts](references/native-and-artifacts.md)
- Android：[android-applications](references/android-applications.md)
- 运行时观察：[runtime-observation](references/runtime-observation.md)
- 证据分页与验证：[evidence-workflows](references/evidence-workflows.md)
- 连接与引擎故障：[connection-and-recovery](references/connection-and-recovery.md)
