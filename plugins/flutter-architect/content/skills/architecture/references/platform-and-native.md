# 平台与原生集成

## 一、平台差异清单

### Android
- 构建：AGP / Gradle 版本与 Flutter 版本绑定，升级要一起看。
- Kotlin、权限（运行时）、后台限制、电池优化。
- 推送通道、厂商通道适配。
- 包体积、启动速度、minSdk（3.47 默认 24；低于 23 直接报错，低于 24 告警）。
- 多 dex：minSdk 21+ 由 AGP 原生支持，通常无需额外配置。
- 16 KB page size：面向 Android 15+（targetSdk 35+）需保证原生库 16 KB 对齐，Play 已按此要求审核。
- targetSdk 合规：跟随 Play 年度截止日期，提前一个版本适配。
- ABI split、签名（v2/v3）、应用商店合规。

### iOS
- Xcode、Swift/Objective-C、entitlements、provisioning profile。
- App Transport Security、后台模式、推送。
- Privacy Manifest 与权限用途描述（被拒高频原因）。
- Swift Package Manager：自 3.44 起默认用于 iOS/macOS 原生依赖。
- CocoaPods：进入维护模式，registry 2026-12-02 起只读，仅作过渡；新项目不要再以 CocoaPods 为默认方案。
- App Store 审核：账号删除、隐私、支付合规。

### Web
- 渲染：CanvasKit（默认）与 Skwasm（`flutter build web --wasm`）；HTML renderer 已在 3.29 移除，`--web-renderer` 不再是选型项。
- 首屏体积、bundle 拆分、SEO（Flutter Web 天生弱，静态内容考虑 Jaspr 等方案）。
- 路由策略（path vs hash）、浏览器兼容、可访问性、PWA。
- Wasm 构建需核对第三方包兼容性。

### Desktop
- 窗口管理、多窗口、系统托盘、快捷键、鼠标与滚轮事件。
- 文件路径与权限、本地存储、安装包与签名分发、自动更新。
- 各平台特性差异大（macOS 沙盒、Windows 注册表、Linux 桌面环境）。

## 二、原生集成方式

| 方式 | 用途 | 注意 |
|---|---|---|
| MethodChannel | 一次性调用 | 手写容易漂移，需统一封装 |
| EventChannel | 原生事件流 | 注意取消订阅与线程 |
| BasicMessageChannel | 双向消息、编解码定制 | 性能敏感场景 |
| Pigeon | 类型安全生成 | 推荐用于新代码 |
| FFI | C/C++ 库 | 需处理内存生命周期、线程 |
| JNI | 调用 Java/Kotlin | 包体积与启动成本 |
| 原生模块嵌入 | 混合栈、插件 | 与原生团队约定生命周期 |

架构师要判断：
- 用现成插件还是自研？自研的维护成本与平台覆盖谁承担？
- 插件是否影响包体积、启动、稳定性？
- 能否降级、能否开关、能否自动化测试？

## 三、插件选型评估

1. 是否仍在维护（近 12 个月发布、issue 有响应）。
2. 平台覆盖是否满足目标（含桌面与 Web）。
3. 是否带原生代码；带的话看构建复杂度与 NDK/依赖。
4. 许可证是否合规。
5. 是否可隔离：通过接口包装，避免业务直接依赖其类型。
6. 是否有可接受的降级方案。

## 四、混合栈

- 明确 Flutter 页面与原生页面的边界与路由交接。
- 引擎复用 vs 多引擎：多引擎成本高（内存、插件重复初始化），优先单引擎多 View。
- 生命周期同步：原生页面销毁时 Flutter View 要正确释放。
- 状态传递：使用明确协议（序列化数据），不要共享可变对象。
- 降级：Flutter 页面加载失败要有原生兜底。

## 五、权限与隐私

- 权限最小化，申请时机与业务动作绑定，不在启动时批量申请。
- 被拒后的引导路径必须有。
- 隐私清单、SDK 数据采集说明、用户可撤回授权。
- 国内合规：个人信息保护法、最小必要、第三方 SDK 清单、应用商店上架要求。
- 日志与埋点脱敏：禁止上报设备唯一标识、通讯录、地理位置等敏感数据，除非业务必要且已获授权。
