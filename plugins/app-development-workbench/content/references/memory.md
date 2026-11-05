# 内存采集与判定

只对用户授权的 App 进程采集。先由 Simulator 工具确认 UDID 与 Bundle ID，再在进程列表核对可执行文件路径和 PID；重启后 PID 必须重新确认。

以下是 Apple CLI 的显式示例，变量必须由本次真实发现填入。以当前系统 `leaks --help` / `man leaks` 核对支持项。

```bash
xcrun simctl spawn "$SIMULATOR_UDID" launchctl list
ps -p "$APP_PID" -o pid=,comm=
mkdir "$CAPTURE_DIR"
leaks --outputGraph="$CAPTURE_DIR/app.memgraph" "$APP_PID"
leaks "$CAPTURE_DIR/app.memgraph"
leaks --groupByType "$CAPTURE_DIR/app.memgraph"
leaks --traceTree="$OBJECT_ADDRESS" "$CAPTURE_DIR/app.memgraph"
```

CAPTURE_DIR 使用不存在的独立输出目录；leaks 非零退出码需要结合输出解释，不能一律当工具坏掉或一律当修复失败。若权限/进程类型不支持，改用已可用的 Xcode Memory Graph，说明采集方式，不关闭系统保护。

按类型检查应用对象，找到实际强持有路径，区分 process/session/account/view/request/task 生命周期。闭包捕获、任务未取消、observer/定时器、缓存键和 delegate 关系是排查线索，不能无引用证据就断言 retain cycle。

重复同一场景和次数，用相同等待条件复采。记录目标类型、数量、持有链、功能回归和仍存在的系统对象。内存峰值、泄漏个数和可达缓存不是同一个指标，不能只用文件大小宣称修复。

官方入口：[Gathering information about memory use](https://developer.apple.com/documentation/xcode/gathering-information-about-memory-use)、[Diagnosing memory, thread, and crash issues early](https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early)。
