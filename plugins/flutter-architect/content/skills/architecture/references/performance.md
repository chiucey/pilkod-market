# 性能

## 一、先建基线

| 指标 | 参考口径 |
|---|---|
| 帧预算 | 60Hz → 16.7ms/帧；120Hz → 8.3ms/帧（UI 与 Raster 各自计算） |
| 卡顿率 | jank 帧占比与掉帧分布，不要只看平均 FPS |
| 启动 | 冷启动首帧时间、engine 初始化耗时、首屏可交互时间 |
| 内存 | 峰值 RSS、图片解码占用、退出页面后的回落幅度 |
| 包体积 | 下载包/安装包体积、单 ABI 体积、资源占比 |

没有基线就下结论，等于猜。优化前后必须给对比数据与采集方法。

## 二、渲染管线

Build → Layout → Paint → Composite，每帧由 vsync 驱动。UI 线程做 Dart 侧的 build/layout/paint，Raster 线程做栅格化与合成。

常见归因：
- UI 线程超预算：build 过重、layout 过深、同步计算、状态作用域过大。
- Raster 线程超预算：保存层（saveLayer）、大阴影、模糊、裁剪、图片解码、过度绘制。

## 三、Impeller（当前默认引擎）

现状（不要凭旧印象）：
- iOS：唯一渲染引擎，无法切回 Skia。
- Android：API 29+ 默认开启，低版本或 Vulkan 不可用时回退旧 OpenGL。
- macOS / Linux / Windows：自 3.47 起默认。
- Web：仍是 Skia/CanvasKit 与 Skwasm。

影响：
- shader 运行时编译导致的首次卡顿问题在 Impeller 下语义变化，旧方案（shader warmup）不能直接照搬。
- 排查时用 `flutter run --no-enable-impeller` 做 A/B；上线包可在 AndroidManifest 关闭。
- 遇到渲染差异/性能问题，报 issue 时附 trace 与设备信息。

## 四、启动优化

阶段拆解：原生启动 → engine 初始化 → Dart main → 首帧 → 首屏数据 → 可交互。

手段：
- 延迟初始化：非首屏 SDK、插件、数据库在首屏后初始化。
- 异步初始化：避免 main 内同步 IO（读配置、解密、初始化日志）。
- 减少首屏请求数量，首屏数据走本地缓存兜底。
- 骨架屏/占位图，先出骨架再填数据。
- 图片预加载与尺寸匹配，禁止首屏加载超大图。
- 减少插件初始化耗时：检查每个插件的 setup 成本。

测量：`flutter run --profile --trace-startup`、启动埋点分段打点、Android/iOS 原生启动工具配合看。

## 五、列表性能

- 用 `ListView.builder` / `SliverList`，禁止一次性生成全部 item。
- 固定高度用 `itemExtent` / `prototypeItem`，减少布局计算。
- item 内避免重复创建昂贵对象；常量 Widget 用 `const`。
- 滚动整体重绘时考虑 `RepaintBoundary`（不要无脑全包，会增内存）。
- 图片按显示尺寸解码，用 `cacheWidth/cacheHeight` 或服务端裁剪。
- 避免透明叠加、昂贵 clip、大阴影、嵌套滚动。
- 分页加载 + 合理预取范围；数据未变时不要触发整表重建。

## 六、内存

- 图片是首要杀手：解码尺寸、缓存上限、列表复用。
- 页面退出后释放：AnimationController、StreamSubscription、Timer、FocusNode、TextEditingController、原生监听。
- TabView / PageView 的 keepAlive 策略要显式决定，不要默认全留。
- isolate 与 native 侧内存单独观测，Dart 侧看不到全部。
- 泄漏排查：DevTools Memory + 快照对比（持续增长且不复用）。

## 七、包体积

- 体积归因：`flutter build appbundle --analyze-size --target-platform android-arm64`（多 ABI 会直接报错，必须指定单一 target-platform）。
- 注意：`--analyze-size` 与 `--split-debug-info` 不能同时使用，需要拆成两条流水线。
- tree shaking 默认开启；确认没有动态字符串反射式调用破坏裁剪。
- 图标字体裁剪、图片压缩与格式选择（webp/avif）。
- ABI split / App Bundle 按设备下发。
- 插件裁剪：审计只用到一个方法的重量级 SDK。
- deferred components：Android/Web 可用，iOS 不支持，慎用。
- 资源分级：非首屏资源延迟打包或远端下发。
- 无用资源与重复资源清理，检查 assets 是否被打进多个变体。

## 八、工具

- Flutter DevTools：Performance、CPU Profiler、Memory、Widget Inspector、Timeline。
- `flutter run --profile --trace-to-file` / `--trace-startup`。
- PerformanceOverlay、`dart:developer` Timeline 打点。
- Android Studio Profiler、Xcode Instruments、Perfetto。
- 线上：崩溃/卡顿/AFK 监控（Sentry、Crashlytics、自研 APM）。

## 九、排查流程

1. 定位阶段：启动 / 首屏 / 滚动 / 动画 / 页面切换 / 后台恢复。
2. 量化现象：帧率、掉帧时刻、耗时区间、内存曲线。
3. 采集：profile 模式录制 trace，不要用 debug 模式下结论。
4. 归因：UI 还是 Raster；build/layout/paint 哪一段；是否单点慢函数。
5. 验证：改一处测一次，前后数据对比。
6. 回归防护：加性能埋点或基准测试，避免复发。

常见误判：debug 模式下的性能数据、模拟器数据、只测首屏不测反复进出、用平均 FPS 掩盖尖峰卡顿。
