---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8e974c922260a5f97ebf74f9e21fcea4
    PropagateID: 8e974c922260a5f97ebf74f9e21fcea4
    ReservedCode1: 3044022073ba5b110184e9043244e603afb3418d06e145d6de9eb10de0d7a0987fb48aed022003a008aadc93dbd32b8fe4271be796bca9eefe5ce1c5facc938c6dbaec149443
    ReservedCode2: 3045022018da9bffefddd7d5bc9e9f0a1615d894049a2ddbd04283192152060f2f45dcf70221009b936ab8224b958bf88a926332fedc1b9498820e7afe525864c6067a3d6e6959
---

# HarmonyOS Debug 调试专业技能指南

## 概述

HarmonyOS 提供了完善的稳定性治理框架和调试工具链，涵盖开发、调试、测试、上线及运维等完整生命周期。本文档介绍应用稳定性问题的检测、分析、优化和运维实践。

**核心调试能力**：
- 崩溃检测与定位（JsCrash/CppCrash）
- 内存泄漏检测与定位
- 应用冻屏（Freeze）检测
- 地址越界问题检测
- 性能分析工具链
- 应用异常处理

## 崩溃检测与定位

### 崩溃类型概述

| 进程类型 | 检测方式 | 定位工具 |
|---------|---------|---------|
| Native进程 | Tombstone + Debuggerd + Dropbox | Faultlogger |
| Java进程 | ART signal catcher + signal chain | - |
| JS进程 | Faultlogger | HiAppEvent |

### 使用 HiAppEvent 订阅崩溃事件

```typescript
import { hiAppEvent, hilog } from '@kit.PerformanceAnalysisKit';

const TAG = 'CrashMonitor';
const DOMAIN = 0xFF00;

// 添加观察者监听崩溃事件
let watcher = hiAppEvent.addWatcher({
  name: 'crashWatcher',
  appEventFilters: [
    {
      domain: hiAppEvent.domain.OS,
      names: [
        hiAppEvent.event.APP_CRASH,        // 应用崩溃
        hiAppEvent.event.APP_FREEZE,       // 应用冻屏
        hiAppEvent.event.CPP_CRASH         // Native崩溃
      ]
    }
  ],
  onReceive: (domain, appEventGroups) => {
    hilog.error(DOMAIN, TAG, `Crash detected - Domain: ${domain}`);

    for (const group of appEventGroups) {
      hilog.error(DOMAIN, TAG, `Event: ${group.name}`);
      for (const event of group.args) {
        hilog.error(DOMAIN, TAG, `  ${event.key} = ${event.value}`);
      }
    }
  }
});

// 移除观察者
hiAppEvent.removeWatcher({ name: 'crashWatcher' });
```

### 获取上次应用异常信息

```typescript
import hiAppEvent from '@ohos.hiviewdfx.hiAppEvent';

// 获取上一次应用崩溃信息
async function getLastAppException() {
  try {
    const crashInfo = await hiAppEvent.getLastAppExceptionInfo();
    if (crashInfo.error) {
      hilog.error(DOMAIN, TAG, `Error getting crash info: ${crashInfo.error.message}`);
      return;
    }

    hilog.info(DOMAIN, TAG, `Exception type: ${crashInfo.exception.type}`);
    hilog.info(DOMAIN, TAG, `Exception reason: ${crashInfo.exception.reason}`);
    hilog.info(DOMAIN, TAG, `Exception stack: ${crashInfo.exception.stack}`);
  } catch (err) {
    hilog.error(DOMAIN, TAG, `Failed to get crash info: ${JSON.stringify(err)}`);
  }
}

// 获取上一次应用卡死信息
async function getLastAppFreeze() {
  try {
    const freezeInfo = await hiAppEvent.getLastAppFreezeInfo();
    hilog.info(DOMAIN, TAG, `Freeze type: ${freezeInfo.freeze.type}`);
    hilog.info(DOMAIN, TAG, `Freeze reason: ${freezeInfo.freeze.reason}`);
  } catch (err) {
    hilog.error(DOMAIN, TAG, `Failed to get freeze info: ${JSON.stringify(err)}`);
  }
}
```

### 构造应用异常场景（仅用于测试）

```typescript
// 触发应用崩溃测试
function triggerAppCrash() {
  try {
    // 构造 APP_CRASH 场景
    const result: object = JSON.parse('');
  } catch (e) {
    // 3秒后应用退出
  }
}

// 触发应用冻屏测试
function triggerAppFreeze() {
  // 500ms后执行无限循环导致应用卡死
  setTimeout(() => {
    while (true) {}
  }, 500);
}
```

## 内存泄漏检测与定位

### 内存指标说明

| 指标 | 说明 | 异常特征 |
|-----|------|---------|
| PSS | 独占 + 共享库按比例分摊 | 突增可能刚加载大资源 |
| RSS | 独占 + 共享库全算 | 长期高位说明缓存未回收 |
| USS | 只看独占内存 | 台阶式上升不回退→泄漏 |

### 使用 Snapshot 检测内存泄漏

**操作步骤**：
1. 在 DevEco Studio 中创建 Snapshot 场景调优分析任务
2. 设置 Snapshot 泳道
3. 开始录制后观察 Memory 泳道的内存使用情况
4. 在需要定位的时刻启动一次快照

```typescript
// Snapshot 分析结果解读
interface SnapshotResult {
  Constructor: string;     // 构造器名称
  Distance: number;       // 从GC Root到对象的距离
  Shallow Size: number;   // 对象的实际大小
  Retained Size: number;   // 对象保留的内存大小
}
```

### ArkTS 内存泄漏常见原因

```typescript
// 1. 定时器未清除
@Entry
@Component
struct MemoryLeakDemo1 {
  timerId: number = 0;

  aboutToAppear() {
    // 错误：未保存timerId，组件销毁时无法清除
    setInterval(() => {
      console.info('Timer running');
    }, 1000);
  }

  // 正确做法：在 aboutToDisappear 中清除
  aboutToDisappear() {
    clearInterval(this.timerId);
  }
}

// 2. 事件监听器未解绑
@Entry
@Component
struct MemoryLeakDemo2 {
  private connection = new EventHub();

  aboutToAppear() {
    // 错误：未保存解绑函数
    this.connection.on('event', (data) => {
      console.info('Event received');
    });
  }

  // 正确做法：保存并调用off
  aboutToDisappear() {
    this.connection.off('event');
  }
}

// 3. 闭包引用导致内存无法释放
@Entry
@Component
struct MemoryLeakDemo3 {
  @State data: number[] = [];

  build() {
    Column() {
      List() {
        ForEach(this.data, (item: number) => {
          ListItem() {
            // 错误：闭包持有整个组件引用
            Button('Click')
              .onClick(() => {
                console.info(`Item: ${item}`);
              })
          }
        })
      }
    }
  }
}

// 4. 全局变量未清理
class GlobalCache {
  static cache: Map<string, object> = new Map();

  static add(key: string, value: object) {
    GlobalCache.cache.set(key, value);
  }

  // 正确做法：提供清理方法
  static clear() {
    GlobalCache.cache.clear();
  }
}
```

### 使用 HiDebug 获取内存信息

```typescript
import hidebug from '@kit.PerformanceAnalysisKit';

// 获取应用内存信息
async function getMemoryInfo() {
  try {
    const memInfo = hidebug.getMemoryUsage();
    hilog.info(DOMAIN, TAG, `PSS: ${memInfo.pss} KB`);
    hilog.info(DOMAIN, TAG, `RSS: ${memInfo.rss} KB`);
  } catch (err) {
    hilog.error(DOMAIN, TAG, `Failed to get memory info: ${JSON.stringify(err)}`);
  }
}

// 获取堆内存信息
async function getHeapMemoryInfo() {
  try {
    const heapInfo = hidebug.getHeapMemoryUsage();
    hilog.info(DOMAIN, TAG, `Total heap: ${heapInfo.total} KB`);
    hilog.info(DOMAIN, TAG, `Used heap: ${heapInfo.used} KB`);
    hilog.info(DOMAIN, TAG, `Free heap: ${heapInfo.free} KB`);
  } catch (err) {
    hilog.error(DOMAIN, TAG, `Failed to get heap info: ${JSON.stringify(err)}`);
  }
}
```

## 应用冻屏检测与定位

### 冻屏问题概述

应用冻屏（AppFreeze）指应用主线程被阻塞，导致界面无法响应用户操作。

**常见原因**：
- 主线程执行耗时操作
- 死循环或无限等待
- 大型同步计算
- 文件 I/O 阻塞

### 检测方法

```typescript
import hiAppEvent from '@ohos.hiviewdfx.hiAppEvent';

// 订阅应用冻屏事件
hiAppEvent.addWatcher({
  name: 'freezeWatcher',
  appEventFilters: [
    {
      domain: hiAppEvent.domain.OS,
      names: [hiAppEvent.event.APP_FREEZE]
    }
  ],
  onReceive: (domain, appEventGroups) => {
    hilog.error(DOMAIN, TAG, 'App freeze detected!');

    for (const group of appEventGroups) {
      hilog.error(DOMAIN, TAG, `Freeze info: ${JSON.stringify(group.args)}`);
    }
  }
});
```

### 定位分析方法

1. **Trace 日志分析**：使用 DevEco Studio 的 Frame Insight 工具
2. **主线程堆栈**：查看冻屏时的主线程调用栈
3. **代码审查**：检查主线程中的耗时操作

```typescript
// 在可能冻屏的代码段添加日志
hilog.info(DOMAIN, TAG, 'Start long operation');

// 执行耗时操作
await doLongOperation();

hilog.info(DOMAIN, TAG, 'End long operation');
```

## 地址越界问题检测

### 地址越界问题类型

| 问题类型 | 说明 |
|---------|------|
| Use After Free | 释放后使用 |
| Double Free | 重复释放 |
| Stack Overflow | 栈溢出 |
| Heap Overflow | 堆溢出 |

### 使用 HWAsan 检测（API 13+）

```typescript
// HWAsan 是推荐的地址越界检测工具
// 配置 build-profile.json5 启用 HWAsan
{
  "buildOption": {
    "nativeLibs": {
      "asan": true
    }
  }
}
```

### 地址越界定位流程

```
第一步：定界 - 是否为地址越界问题
  - 问题多次低概率持续发生？
  - 崩溃栈顶无规律？
  - 同一个崩溃栈顶源码无规律？
  → 满足以上条件可初步确认地址越界

第二步：高概率场景分析
  - 配合流水日志分析
  - 分析崩溃栈（报错原因）
  - 确定触发测试场景

第三步：测试复现
  - 使用 DevEco Testing 进行稳定性测试
  - 应用开启 HWAsan 检测

第四步：定位解决
  - 基于问题日志分析根因

第五步：进一步稳定性测试
  - 验证问题修复后的表现
```

## 性能分析工具链

### DevEco Studio Profiler 工具集

| 工具 | 用途 |
|-----|------|
| Launch Insight | 分析应用启动耗时 |
| Frame Insight | 分析卡顿和丢帧 |
| Time Insight | 识别CPU耗时热点代码 |
| Allocation Insight | 分析内存分配记录 |
| Snapshot Insight | 分析ArkTS对象分布差异 |
| CPU Insight | 分析CPU调度和线程状态 |

### Launch Insight - 启动耗时分析

```typescript
// 使用 Trace 记录启动过程
import trace from '@kit.PerformanceAnalysisKit';

// 标记启动阶段
trace.traceStart('app_launch', 'phase1');
await loadResources();
trace.traceEnd('app_launch', 'phase1');

trace.traceStart('app_launch', 'phase2');
await initializeData();
trace.traceEnd('app_launch', 'phase2');
```

### Frame Insight - 丢帧分析

```typescript
// 丢帧通常由以下原因导致：
// 1. UI 任务耗时过长
// 2. 主线程被阻塞
// 3. 频繁的状态更新触发重绘

// 优化建议
// - 使用 @Concurrent 装饰器将耗时操作移到 TaskPool
// - 减少 @State 变量更新频率
// - 使用懒加载和虚拟滚动处理长列表
```

### Time Insight - CPU 热点分析

```typescript
// 使用 HiDumper 获取 CPU 信息
// 命令行：hilog -b D -S app > cpu_log.txt
// 分析 cpu_log.txt 中的调用栈信息
```

## 应用异常处理最佳实践

### 全局异常捕获

```typescript
// 在 Application 中设置全局错误处理
import UIAbility from '@ohos.app.ability.UIAbility';

export default class MyAbility extends UIAbility {
  onCreate(want, launchParam) {
    // 设置应用级错误处理
    process.on('uncaughtException', (error) => {
      hilog.error(DOMAIN, TAG, `Uncaught exception: ${error.message}`);
      hilog.error(DOMAIN, TAG, `Stack: ${error.stack}`);
    });

    process.on('unhandledRejection', (reason, promise) => {
      hilog.error(DOMAIN, TAG, `Unhandled rejection at: ${promise}, reason: ${reason}`);
    });
  }
}
```

### 异步任务错误处理

```typescript
// Promise 错误处理
async function asyncTask() {
  try {
    const result = await mightFailAsyncOperation();
    return result;
  } catch (error) {
    hilog.error(DOMAIN, TAG, `Async error: ${error.message}`);
    // 恢复或通知用户
    return fallbackValue;
  }
}

// TaskPool 任务错误处理
import taskpool from '@kit.ArkTS';

@Concurrent
function mayThrowError(): number {
  if (someCondition) {
    throw new Error('Task failed');
  }
  return 42;
}

async function executeTask() {
  let task = new taskpool.Task(mayThrowError);
  try {
    let result = await taskpool.execute(task);
  } catch (error) {
    hilog.error(DOMAIN, TAG, `TaskPool error: ${error.message}`);
  }
}
```

### 稳定性测试场景检测

```typescript
import appManager from '@ohos.app.ability.appManager';

// 查询是否处于稳定性测试场景
appManager.isRunningInStabilityTest((err, isTest) => {
  if (err) {
    hilog.error(DOMAIN, TAG, `Error: ${JSON.stringify(err)}`);
    return;
  }

  if (isTest) {
    hilog.info(DOMAIN, TAG, 'Running in stability test mode');
    // 可以调整日志级别或启用额外检测
  }
});
```

## 日志系统使用

### hilog 日志级别

```typescript
import { hilog } from '@kit.PerformanceAnalysisKit';

const DOMAIN = 0xFF00;
const TAG = 'MyApp';

// 调试日志（开发环境）
hilog.debug(DOMAIN, TAG, 'Debug info: %{public}s', 'message');

// 信息日志
hilog.info(DOMAIN, TAG, 'Info: %{public}s', 'message');

// 警告日志
hilog.warn(DOMAIN, TAG, 'Warning: %{public}s', 'message');

// 错误日志
hilog.error(DOMAIN, TAG, 'Error: %{public}s', 'message');

// 致命错误日志
hilog.fatal(DOMAIN, TAG, 'Fatal: %{public}s', 'message');
```

### 日志格式化输出

```typescript
// 使用占位符格式化
hilog.info(DOMAIN, TAG, 'User %{public}s logged in at %{public}s',
  userName,
  new Date().toISOString()
);

// 输出 JSON 对象
const userData = { id: 1, name: 'John' };
hilog.info(DOMAIN, TAG, 'User data: %{public}s', JSON.stringify(userData));
```

## 常见问题排查

### 崩溃问题排查清单

| 步骤 | 检查项 |
|-----|--------|
| 1 | 查看崩溃日志中的错误码和堆栈 |
| 2 | 确认崩溃发生在哪个模块（JS/Native） |
| 3 | 分析崩溃前的应用行为 |
| 4 | 检查是否有内存异常 |
| 5 | 审查相关代码的异常处理 |

### 内存泄漏排查清单

| 步骤 | 检查项 |
|-----|--------|
| 1 | 使用 Snapshot 工具对比操作前后的内存 |
| 2 | 检查定时器是否正确清理 |
| 3 | 检查事件监听器是否正确解绑 |
| 4 | 检查静态变量和全局缓存 |
| 5 | 检查闭包引用 |
| 6 | 检查资源文件是否正确释放 |

### 冻屏问题排查清单

| 步骤 | 检查项 |
|-----|--------|
| 1 | 使用 Trace 分析主线程耗时 |
| 2 | 检查是否有同步 I/O 操作 |
| 3 | 检查是否有死循环 |
| 4 | 检查 TaskPool/Worker 使用是否正确 |
| 5 | 检查锁竞争情况 |

## 官方资源

- 稳定性概览：https://developer.huawei.com/consumer/cn/doc/best-practices/bpta-stability-overview
- 稳定性检测：https://developer.huawei.com/consumer/cn/doc/best-practices/bpta-stability-detection
- 稳定性分析：https://developer.huawei.com/consumer/cn/doc/best-practices/bpta-stability-analysis
- 稳定性优化：https://developer.huawei.com/consumer/cn/doc/best-practices/bpta-stability-opt
- 崩溃故障分析：https://developer.huawei.com/consumer/cn/forum/topic/0202153088009460397
- DevEco Testing：https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/deveco-testing-0000001729454893
