---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100f9f197faa9ea4d07fd9b7a83eea75494750a62fa3bca372b38aee3381f914496022100954eb4354ca376525098a76f5680baf3bf2bac11c7b559fa7f5bf84e83d34e74
    ReservedCode2: 30450221009b298cd37edc17dc5e5509c60d5150594f9793474d81ae9af731620e8d0213cb022031650e740515ac27fedd7771655620a1583946c3d569500dc3f5df7aff2ff0a8
---

# HarmonyOS 多线程并发开发指南

## 概述

ArkTS 提供两种并发能力：
- **异步并发**：Promise/async/await，适用于单次 I/O 任务
- **多线程并发**：TaskPool 和 Worker，适用于 CPU 密集型、I/O 密集型和同步任务

## TaskPool 任务池

### 基本使用

```typescript
import taskpool from '@kit.ArkTS';

// 定义并发函数（必须使用 @Concurrent 装饰器）
@Concurrent
function calculateSum(arr: number[]): number {
  return arr.reduce((sum, val) => sum + val, 0);
}

// 执行任务
async function executeTask() {
  let task = new taskpool.Task(calculateSum, [1, 2, 3, 4, 5]);
  let result = await taskpool.execute(task);
  console.info(`Result: ${result}`);
}
```

### 带返回值的任务

```typescript
@Concurrent
function fetchData(url: string): string {
  // 模拟网络请求
  return `Data from ${url}`;
}

async function main() {
  let task = new taskpool.Task(fetchData, 'https://api.example.com');
  let result = await taskpool.execute(task);
  console.info(`Result: ${result}`);
}
```

### 任务优先级

```typescript
import { taskpool, Priority } from '@kit.ArkTS';

// 高优先级任务
let highPriorityTask = new taskpool.Task(heavyTask, data, Priority.HIGH);

// 低优先级任务
let lowPriorityTask = new taskpool.Task(lightTask, data, Priority.LOW);
```

### 长时任务

```typescript
// 任务执行耗时不能超过 3 分钟（不包含 I/O 耗时）
@Concurrent
function longRunningTask(): string {
  // 长时间计算任务
  return 'completed';
}
```

### 任务取消

```typescript
async function cancelTaskDemo() {
  let task = new taskpool.Task(myTask, param);
  let taskId = taskpool.execute(task);

  // 取消任务
  taskpool.cancel(taskId);
}
```

## Worker 工作线程

### 创建 Worker

```typescript
// 主线程 - entry/src/main/ets/pages/Index.ets
import worker from '@kit.ArkTS';

// 创建 Worker 实例
const workerInstance = new worker.ThreadWorker(
  'entry/ets/workers/MyWorker.ets',
  { name: 'myWorker', resumeOnWorkerStart: true }
);

// 监听消息
workerInstance.onmessage = (message) => {
  console.info(`Received from worker: ${message}`);
};

// 监听错误
workerInstance.onerror = (error) => {
  console.error(`Worker error: ${error}`);
};

// 发送消息到 Worker
workerInstance.postMessage('Hello from main thread');

// 终止 Worker
workerInstance.terminate();
```

### Worker 文件

```typescript
// entry/src/main/ets/workers/MyWorker.ets
import worker from '@kit.ArkTS';

const parentPort = worker.parentPort;

parentPort.onmessage = (event) => {
  const data = event.data;
  console.info(`Worker received: ${data}`);

  // 处理任务
  let result = data * 2;

  // 发送结果回主线程
  parentPort.postMessage(result);
};
```

### 多 Worker 管理

```typescript
import { worker } from '@kit.ArkTS';

// 创建多个 Worker 实例
let workers: worker.ThreadWorker[] = [];
let workerCount = 3;

for (let i = 0; i < workerCount; i++) {
  let w = new worker.ThreadWorker('entry/ets/workers/Worker' + i + '.ets', {
    name: 'worker' + i
  });
  workers.push(w);
}

// 负载均衡分配任务
function dispatchTask(data: number) {
  let workerIndex = data % workerCount;
  workers[workerIndex].postMessage(data);
}
```

### registerGlobalCallObject 全局函数调用

```typescript
// 主线程
import { worker } from '@kit.ArkTS';

// 注册全局调用对象
worker.registerGlobalCallObject('myUtils', {
  getTimestamp: () => Date.now()
});

let myWorker = new worker.ThreadWorker('entry/ets/workers/Worker.ets');
myWorker.postMessage('call');
```

## Sendable 数据传递

### 基本类型

```typescript
// 基础类型自动支持 Sendable
let num: number = 10;
let str: string = 'hello';
let bool: boolean = true;
let arr: number[] = [1, 2, 3];
```

### 自定义 Sendable 类

```typescript
@Sendable
class MyData {
  name: string;
  value: number;

  constructor(name: string, value: number) {
    this.name = name;
    this.value = value;
  }
}

// 在任务间传递
@Concurrent
function processData(data: MyData): MyData {
  return new MyData(data.name + '_processed', data.value * 2);
}
```

### ArrayBuffer 传递

```typescript
@Concurrent
function processBuffer(buffer: ArrayBuffer): ArrayBuffer {
  let view = new Uint8Array(buffer);
  for (let i = 0; i < view.length; i++) {
    view[i] = view[i] % 256;
  }
  return buffer;
}

// 转移所有权（更快，但不保留原引用）
task.setTransferList([buffer]);
```

## 常见场景

### CPU 密集型任务

```typescript
// 图像处理
@Concurrent
function processImage(data: ArrayBuffer): ArrayBuffer {
  // 图像处理逻辑
  return processedData;
}

async function imageProcessing() {
  let task = new taskpool.Task(processImage, imageBuffer);
  let result = await taskpool.execute(task);
}
```

### I/O 密集型任务

```typescript
@Concurrent
function readLargeFile(path: string): string {
  // 文件读写操作
  return fileContent;
}

async function fileIO() {
  let task = new taskpool.Task(readLargeFile, '/data/file.txt');
  let content = await taskpool.execute(task);
}
```

### 任务依赖

```typescript
import { taskpool } from '@kit.ArkTS';

// 创建任务组
let task1 = new taskpool.Task(taskFunc1, param1);
let task2 = new taskpool.Task(taskFunc2, param2);

// 按顺序执行
await taskpool.execute(task1);
await taskpool.execute(task2);
```

## 注意事项

1. **UI 操作必须在主线程**：修改 UI 控件、更新视图等操作必须在 UI 线程中执行
2. **任务耗时限制**：TaskPool 任务执行耗时不能超过 3 分钟（不包含 I/O 耗时）
3. **避免导入 UI 相关模块**：子线程中不要导入 @Observed、AppStorage 等 UI 相关模块
4. **使用 @Concurrent 装饰器**：TaskPool 执行的任务函数必须使用此装饰器
5. **Sendable 数据**：跨线程传递复杂对象时，对象需符合 Sendable 协议
