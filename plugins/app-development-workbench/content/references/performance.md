# 性能调查的可执行路径

## 常规 Instruments 路径

用当前 `xcrun xctrace list templates` 确认可用模板，选择 Time Profiler / SwiftUI 等与问题对应的采样；从 Xcode 或 xctrace 对真实 App 采集。不同工具版本参数可能变化，执行前查看 `xcrun xctrace help record`。明确录制的是启动还是固定运行时交互，开始/停止点必须一致。保留 trace 原件以及所用 App/dSYM。

## ETTrace 兼容路径

这是可选外部依赖，不随插件捆绑。读取 [ETTrace 官方仓库](https://github.com/EmergeTools/ETTrace) 的目标版本说明，确认 runner 与 App framework 兼容。原参考流程以 v1.1.0 processed nodes 格式为基线，其他格式需重新核实，不强行当同格式处理。

1. 创建本次独立目录，在变更前保存 App target 配置差异。
2. 通过已批准的安装方式准备 runner；将匹配版本的 Simulator ETTrace framework 临时链接到实际被测 App target，不能只加到测试 target。
3. 构建并安装该包，确认启动日志出现 Starting ETTrace。固定端口要求同一时间只有一个被采集的 instrumented App。
4. 用 dwarfdump 核对实际可执行文件与各 app-owned 动态 framework 的 UUID 和 dSYM，缺关键符号先修复。
5. 进入独立目录，通过支持交互的终端运行 ettrace。启动采样使用 --launch，运行中采样从稳定页面开始；根据实际版本 help 填入 --simulator、--dsyms 等参数。
6. 立即将本次新生成的 output_<thread>.json 保存到新 run 目录。不要混入上轮输出，不把 viewer 的 output.json 或 emerge-output 原始文件当成已处理火焰图。
7. 检查实际顶层 nodes、name、duration、children 结构和符号摘要，再分析 inclusive/self 比重。未知 schema、非有限数值、缺失关键字段或应用主要栈未符号化时停止量化结论。
8. 修复后按同一环境与操作复采。恢复临时 framework/配置，仅撤销本次 patch，核对正常 App 再次可构建。

## 报告口径

列场景、版本、采集方式、线程、符号完整性、重复次数、主要应用调用栈与证据。inclusive 包含后代，自耗时只含该帧；重叠 inclusive 不能直接求和当总耗时。不同设备、网络、数据量和 Debug/Release 不能直接比较百分比。

源码检查仅用于候选原因，具体结论需要 trace 支持。优化观察范围、图片解码、计算位置或布局前后都要核验功能保持。

官方参考：[Improving your app’s performance](https://developer.apple.com/documentation/xcode/improving-your-app-s-performance)、[Understanding and improving SwiftUI performance](https://developer.apple.com/documentation/swiftui/understanding-and-improving-swiftui-performance)。
