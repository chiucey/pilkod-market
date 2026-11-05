---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 1158c52ec56dc962b471fdfedad19cea
    PropagateID: 1158c52ec56dc962b471fdfedad19cea
    ReservedCode1: 3046022100d83bab70c3156ea25d203b1d186909e66f81165ae067a82383112f1fb685b40b02210088933aa2e818d5b40656f1aeffe76b49bfc677b2a4f037bf4d24c031e6afde13
    ReservedCode2: 304402202a551e991751dedcf7550a2e88604bc6fa7849a79f10a931de5812cf9c1d346202203f5313e69d4b90d2b64dd8b9db2346aead0f83643c974b60b983c36d85b400e7
---

# HarmonyOS 崩溃定位与性能分析指南

## 性能分析工具（hiAppEvent）

### 应用事件订阅

```typescript
import { hiAppEvent, hilog } from '@kit.PerformanceAnalysisKit';

// 添加事件观察者
let holder = hiAppEvent.addWatcher({
  name: 'performanceWatcher',
  appEventFilters: [
    {
      domain: hiAppEvent.domain.OS,
      names: [
        hiAppEvent.event.APP_LAUNCH,
        hiAppEvent.event.APP_EXIT,
        hiAppEvent.event.APP_CRASH
      ]
    }
  ],
  onReceive: (domain: string, appEventGroups: Array<hiAppEvent.AppEventGroup>) => {
    hilog.info(0x0000, 'perfTag', `Domain: ${domain}`);

    for (const group of appEventGroups) {
      hilog.info(0x0000, 'perfTag', `Event: ${group.name}`);

      for (const event of group.args) {
        hilog.info(0x0000, 'perfTag', `Key: ${event.key}, Value: ${event.value}`);
      }
    }
  }
});

// 移除观察者
hiAppEvent.removeWatcher({ name: 'performanceWatcher' });
```

### 订阅崩溃事件

```typescript
import { hiAppEvent, hilog } from '@kit.PerformanceAnalysisKit';

hiAppEvent.addWatcher({
  name: 'crashWatcher',
  appEventFilters: [
    {
      domain: hiAppEvent.domain.OS,
      names: [hiAppEvent.event.APP_CRASH]
    }
  ],
  onReceive: (domain: string, appEventGroups: Array<hiAppEvent.AppEventGroup>) => {
    for (const group of appEventGroups) {
      hilog.error(0x0000, 'crashTag', `App crashed: ${group.name}`);

      // 获取崩溃详情
      for (const event of group.args) {
        hilog.error(0x0000, 'crashTag',
          `Crash info - ${event.key}: ${event.value}`);
      }
    }
  }
});
```

## 日志系统（hilog）

### 基本使用

```typescript
import hilog from '@ohos.hilog';

const DOMAIN = 0x0001;
const TAG = 'MyApp';

// 输出不同级别日志
hilog.debug(DOMAIN, TAG, 'Debug message: %{public}s', 'details');
hilog.info(DOMAIN, TAG, 'Info message: %{public}s', 'details');
hilog.warn(DOMAIN, TAG, 'Warning message: %{public}s', 'details');
hilog.error(DOMAIN, TAG, 'Error message: %{public}s', 'details');
hilog.fatal(DOMAIN, TAG, 'Fatal message: %{public}s', 'details');
```

### 格式化输出

```typescript
// 支持格式化占位符
hilog.info(DOMAIN, TAG, 'User %{public}s logged in at %{public}s',
  'John', new Date().toISOString());

hilog.info(DOMAIN, TAG, 'Count: %{public}d, Price: %{public}f',
  10, 99.99);

// 使用隐私标签
hilog.info(DOMAIN, TAG, 'Sensitive data: %{private}s', 'secret'); // 不输出
hilog.info(DOMAIN, TAG, 'Public data: %{public}s', 'visible');   // 输出
```

### 日志配置

```typescript
// 在 module.json5 中配置
{
  "app": {
    "bundleName": "com.example.app",
    "vendor": "example",
    "versionCode": 100000,
    "versionName": "1.0.0",
    "icon": "$media:app_icon",
    "label": "$string:app_name"
  }
}
```

## DevEco Studio 调试

### 断点调试

1. 在代码行号左侧点击设置断点
2. 使用 Debug 模式启动应用
3. 在 Debug 面板查看变量值
4. 使用 Step Over/Into/Out 控制执行流程

### Logcat 面板

```
# 过滤特定标签
hilog -s -p 0x0001 MyApp

# 查看错误日志
hilog -s -p 0xFF

# 导出日志
hilog -r > /path/to/log.txt
```

## 常见崩溃类型

### 空指针异常

```typescript
// 检查对象是否存在
if (obj !== null && obj !== undefined) {
  obj.method();
}

// 使用可选链
let value = obj?.property?.nested;
```

### 数组越界

```typescript
// 检查索引
if (index >= 0 && index < array.length) {
  let item = array[index];
}

// 使用安全方法
let item = array.at(index);  // 返回 undefined 而非报错
```

### 类型转换错误

```typescript
// 使用类型保护
if (value instanceof String) {
  let str = value as string;
}

// 使用类型断言
let str = value as string;
```

### 异步操作错误

```typescript
// 使用 try-catch
async function safeAsync() {
  try {
    await riskyOperation();
  } catch (err) {
    hilog.error(DOMAIN, TAG, `Async error: ${err}`);
  }
}
```

## 性能分析

### 主线程监控

```typescript
import { hiAppEvent } from '@kit.PerformanceAnalysisKit';

// 监控主线程耗时操作
@Concurrent
function heavyTask() {
  // 耗时操作
}
```

### 内存泄漏检测

```typescript
import { hiAppEvent, hilog } from '@kit.PerformanceAnalysisKit';

// 订阅资源泄漏事件
hiAppEvent.addWatcher({
  name: 'leakWatcher',
  appEventFilters: [
    {
      domain: hiAppEvent.domain.OS,
      names: [hiAppEvent.event.RESOURCE_LEAK]
    }
  ],
  onReceive: (domain: string, appEventGroups: Array<hiAppEvent.AppEventGroup>) => {
    for (const group of appEventGroups) {
      hilog.warn(0x0000, 'leakTag', `Resource leak detected: ${group.name}`);

      for (const event of group.args) {
        hilog.warn(0x0000, 'leakTag',
          `Leak info - ${event.key}: ${event.value}`);
      }
    }
  }
});
```

### UI 渲染性能

```typescript
// 避免在 build() 中执行耗时操作
@Entry
@Component
struct PerformanceDemo {
  @State data: string = '';

  aboutToAppear() {
    // 耗时操作应在生命周期方法中执行
    this.loadData();
  }

  build() {
    // build() 中只执行 UI 相关操作
    Text(this.data)
  }
}
```

## 崩溃日志分析

### 日志级别

| 级别 | 说明 | 使用场景 |
|------|------|----------|
| DEBUG | 调试信息 | 开发阶段 |
| INFO | 一般信息 | 运行时状态 |
| WARN | 警告信息 | 潜在问题 |
| ERROR | 错误信息 | 需要处理的问题 |
| FATAL | 致命错误 | 应用崩溃 |

### 日志格式

```
[Time] [Level] [Domain:Tag] [Message]
2024-01-15 10:30:45.123 ERROR 0x0001:MyApp App crashed: TypeError
```

## 调试技巧

### 使用 try-catch 包裹关键代码

```typescript
try {
  riskyOperation();
} catch (err) {
  hilog.error(DOMAIN, TAG, 'Operation failed: %{public}s',
    (err as Error).message);
}
```

### 添加调试日志

```typescript
hilog.info(DOMAIN, TAG, 'Entering function: %{public}s', 'myFunction');
hilog.info(DOMAIN, TAG, 'Variable state: %{public}s', JSON.stringify(state));
hilog.info(DOMAIN, TAG, 'Exiting function: %{public}s', 'myFunction');
```

### 使用条件断点

```typescript
// 当特定条件满足时触发断点
if (variable === specificValue) {
  debugger;  // 条件断点
}
```

## 常见问题排查

### 应用启动白屏

1. 检查 aboutToAppear 和 onWindowStageCreate 是否耗时过长
2. 检查资源文件是否加载正确
3. 使用性能分析工具定位瓶颈

### 界面卡顿

1. 检查是否有耗时操作在主线程执行
2. 检查列表渲染是否使用了懒加载
3. 检查动画是否过于复杂

### 内存占用高

1. 检查是否有未释放的资源
2. 检查图片是否过大
3. 检查是否存在内存泄漏

## DevEco Testing 性能测试

```typescript
// 使用 DevEco Testing 进行性能测试
import test from '@ohos.application.test';

// 性能测试用例
test.it('performance_test', 0, async (done) => {
  let startTime = Date.now();

  // 执行测试操作
  await performOperation();

  let endTime = Date.now();
  let duration = endTime - startTime;

  // 验证性能指标
  expect(duration).assertLess(1000);  // 应小于 1 秒
  done();
});
```
