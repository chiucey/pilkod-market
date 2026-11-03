---
name: ios-simulator-debug
description: 用于发现 iOS 工程和模拟器、构建安装启动、UI 操作与日志定位。优先使用 XcodeBuildMCP 的实际工具 schema，必要时用 Apple CLI 复现。
---

# 模拟器构建与运行调试


先读 [工具与环境](../../references/tool-runtime.md)。macOS、Xcode 与 Simulator 是外部依赖；包安装成功不证明环境可运行。

## 明确目标再执行
1. 发现 project/workspace、scheme、Debug 配置和部署目标；优先复用已经启动且适合本工程的模拟器，记录 UDID 和 runtime。
2. 用户已要求运行应用且没有合适 Booted 设备时，可启动已有匹配设备；删除、抹除、卸载或切换用户数据需要对应明确范围，不为构建失败随便重置模拟器。
3. 通过宿主实际工具列表找到会话默认、build/run、UI 和日志工具，读取输入 schema，再设置 workspace 或 project（不混填）、scheme 与 simulatorId。不硬编码 Codex 的工具命名空间。
4. 构建完成后核对生成 App 的 Bundle ID，并安装、启动。已经有正确构建且只需启动时不要无意义重编。
5. 读取实际 UI/截图证实正确 App 已前台启动，再开始交互。构建退出码 0 只证明本次编译步骤。

## 复现与证据
操作前读取当前 UI，优先 accessibility identifier/label；坐标只在确实无法定位时使用，布局变化后重读。按最小步骤执行，记录触发、实际结果与预期。

需要日志时先开启当前 Bundle ID 的采集，执行一次复现，再停止并保存相关区间。对错误先关联具体请求或视图状态，再改根因；对敏感日志脱敏，不把令牌或用户照片放进交付包。

构建失败读取首个有效编译/链接错误；依赖失败确认版本与缓存完整性，UI 不可点击先查层级/遮挡/状态。仅在证据支持时尝试工具的 xcodebuild 备选模式，不反复撞同一命令。

## 浏览器预览边界
正常原生 App 仍在 Simulator 中运行。宿主有已验证镜像工具时可附加镜像；没有则使用 Simulator UI 和截图，不声称浏览器已接入。SwiftUI #Preview/PreviewProvider 仅在已验证的工具链中运行，不能承诺任意工程浏览器热更新。使用用户现有桌面浏览器，不另起无头浏览器。

交付工程/scheme/UDID/版本、复现步骤、相关截图与日志、修复和复测结果。性能或内存问题进入对应调查技能，不能从日志无错误推断无卡顿或无泄漏。
