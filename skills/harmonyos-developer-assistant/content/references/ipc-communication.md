---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100e31cef7d56b69bfed9423fba89885576cc3c799e6ff646b4e1b6a52025b8a4d4022100eb1d593b695503de260270485564e77ac4859a9785d3d2874cdf626eacb162be
    ReservedCode2: 304502210096b3f41338ce24d10f95bb6b292d5bd817f432d4e57ed5aee15e57426ef74a8d022073ac7c553b3f17d6fc1aca915fef7d78719ddec14566c3f41b71e8b86c2b38f0
---

# HarmonyOS 进程线程通信指南

## 公共事件（CommonEvent）

### 概述

公共事件服务（CES）为应用程序提供订阅、发布、退订公共事件的能力。

**事件类型**：
- **系统公共事件**：系统定义的事件，如 HAP 安装、更新、卸载
- **自定义公共事件**：应用自定义的事件

**发送方式**：
- 无序公共事件
- 有序公共事件
- 粘性公共事件

### 订阅公共事件

```typescript
import commonEvent from '@ohos.commonEvent';

// 创建订阅信息
let subscribeInfo = {
  events: ['event.name']  // 订阅的事件
};

// 创建订阅者
commonEvent.createSubscriber(subscribeInfo, (err, subscriber) => {
  if (err) {
    console.error(`Create subscriber failed: ${err}`);
    return;
  }

  // 订阅事件
  commonEvent.subscribe(subscriber, (err) => {
    if (err) {
      console.error(`Subscribe failed: ${err}`);
    } else {
      console.info('Subscribe success');
    }
  });

  // 处理事件
  subscriber.onReceiveEvent((err, data) => {
    if (err) {
      console.error(`Receive event failed: ${err}`);
      return;
    }
    console.info(`Event: ${data.event}`);
    console.info(`Bundle name: ${data.bundleName}`);
    console.info(`Data: ${data.data}`);
    console.info(`Parameters: ${JSON.stringify(data.parameters)}`);
  });
});
```

### 发布公共事件

```typescript
import commonEvent from '@ohos.commonEvent';

// 发布无序事件
commonEvent.publish('custom.event.name', (err) => {
  if (err) {
    console.error(`Publish failed: ${err}`);
  } else {
    console.info('Publish success');
  }
});

// 发布带参数的事件
let options = {
  code: 0,           // 事件代码
  data: 'event data' // 事件数据
};

commonEvent.publish('custom.event.name', options, (err) => {
  console.info('Publish with options');
});
```

### 发布有序事件

```typescript
import commonEvent from '@ohos.commonEvent';

let options = {
  code: 1,
  data: 'ordered event',
  ordered: true  // 有序事件
};

commonEvent.publish('ordered.event.name', options, (err) => {
  console.info('Ordered event published');
});

// 订阅有序事件时按优先级处理
let subscribeInfo = {
  events: ['ordered.event.name'],
  priority: 100  // 优先级
};
```

### 发布粘性事件

```typescript
import commonEvent from '@ohos.commonEvent';

let options = {
  code: 0,
  data: 'sticky event data',
  sticky: true  // 粘性事件
};

commonEvent.publish('sticky.event.name', options, (err) => {
  console.info('Sticky event published');
});
```

### 取消订阅

```typescript
import commonEvent from '@ohos.commonEvent';

commonEvent.unsubscribe(subscriber, (err) => {
  if (err) {
    console.error(`Unsubscribe failed: ${err}`);
  } else {
    console.info('Unsubscribe success');
  }
});
```

## 应用事件订阅（hiAppEvent）

### 订阅应用事件

```typescript
import { hiAppEvent, hilog } from '@kit.PerformanceAnalysisKit';

// 添加观察者
let holder = hiAppEvent.addWatcher({
  name: 'myWatcher',
  appEventFilters: [
    {
      domain: hiAppEvent.domain.OS,
      names: [hiAppEvent.event.APP_LAUNCH]
    }
  ],
  onReceive: (domain: string, appEventGroups: Array<hiAppEvent.AppEventGroup>) => {
    hilog.info(0x0000, 'testTag', `HiAppEvent onReceive: domain=${domain}`);

    for (const eventGroup of appEventGroups) {
      hilog.info(0x0000, 'testTag', `Event name: ${eventGroup.name}`);
      for (const event of eventGroup.args) {
        hilog.info(0x0000, 'testTag', `Event args: ${event.key}=${event.value}`);
      }
    }
  }
});

// 移除观察者
hiAppEvent.removeWatcher({ name: 'myWatcher' });
```

### 可订阅的事件

```typescript
// 应用生命周期事件
hiAppEvent.event.APP_LAUNCH        // 应用启动
hiAppEvent.event.APP_EXIT         // 应用退出
hiAppEvent.event.APP_CRASH        // 应用崩溃

// 资源泄漏事件
hiAppEvent.event.RESOURCE_LEAK     // 资源泄漏

// 用户行为事件
hiAppEvent.event.DISTRIBUTED_SERVICE_START
```

## 进程内通信

### 使用 AppStorage 共享数据

```typescript
// 主线程设置
import AppStorage from '@ohos.app.ability.AppStorage';

AppStorage.setOrCreate('sharedKey', 'sharedValue');

// 其他 Ability/Worker 读取
let value = AppStorage.get<string>('sharedKey');
```

### 使用 LocalStorage

```typescript
// 创建 LocalStorage 实例
let localStorage = new LocalStorage();

// 存储数据
localStorage.setOrCreate('key', 'value');

// 组件中使用
@Component
struct MyComponent {
  @StorageLink('key') linkValue: string = '';

  build() {
    Text(this.linkValue)
  }
}
```

### 组件间通信

```typescript
// 父子组件通信 - @Link
@Component
struct Child {
  @Link parentMessage: string;

  build() {
    Column() {
      Text(this.parentMessage)
        .onClick(() => {
          this.parentMessage = 'Updated by child';
        })
    }
  }
}

@Entry
@Component
struct Parent {
  @State message: string = 'Hello';

  build() {
    Column() {
      Child({ parentMessage: $message })
    }
  }
}
```

### EventHub 事件中心

```typescript
// 在 Ability 中使用 EventHub
import common from '@ohos.app.ability.common';

let context: common.UIAbilityContext = ...;

// 注册事件
context.eventHub.on('myEvent', (data: string) => {
  console.info(`Received: ${data}`);
});

// 触发事件
context.eventHub.emit('myEvent', 'event data');

// 取消注册
context.eventHub.off('myEvent');
```

## 常见使用场景

### 监听系统事件

```typescript
// 订阅屏幕亮灭事件
let screenEvents = [
  'usual.event.SCREEN_ON',    // 屏幕点亮
  'usual.event.SCREEN_OFF'    // 屏幕熄灭
];

// 订阅网络状态变化
let networkEvents = [
  'usual.event.CONNECTIVITY_CHANGE'  // 网络状态变化
];

commonEvent.subscribe({
  events: [...screenEvents, ...networkEvents]
}, subscriber, callback);
```

### 应用间通信

```typescript
// 发布自定义事件
commonEvent.publish('com.example.app.EVENT', {
  code: 100,
  data: JSON.stringify({ action: 'sync', timestamp: Date.now() })
}, (err) => {
  // 处理结果
});
```

## 注意事项

1. **权限申请**：订阅某些系统公共事件需要申请相应权限
2. **有序事件**：有序事件按优先级顺序执行
3. **粘性事件**：粘性事件会保留最新值，新订阅者可以立即获取
4. **资源释放**：取消订阅时及时释放资源
5. **性能考虑**：避免频繁发布订阅事件造成性能问题
