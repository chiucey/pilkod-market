---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100f8dec8f2fb310797133dba67d8e02943db9fd029c16bdb237ce3afa8554b4e9e022100d16a4db25df84e0db770f6fcd5a50527edc3a8a0c21d2cbdec8fc4d307962aad
    ReservedCode2: 3046022100c6230a96d1058d6dfa3bec2b3d1a546693f19865a3586dcaf04f83e6483a8404022100f6a0d6d05f76842fb2bfc41aa100b2226e88e194d2288377dd0acf487a4756e2
---

# ArkTS 语言快速参考

## 基础类型

```typescript
// 基本类型
let name: string = 'HarmonyOS'
let version: number = 5.0
let isActive: boolean = true
let list: number[] = [1, 2, 3]
let tuple: [string, number] = ['version', 5.0]

// 枚举
enum Color { Red, Green, Blue }
let selected: Color = Color.Red

// 接口
interface User {
  name: string
  age: number
  email?: string  // 可选属性
}

// 类型别名
type ID = string | number
```

## 函数

```typescript
// 函数声明
function greet(name: string): string {
  return `Hello, ${name}`
}

// 箭头函数
const add = (a: number, b: number): number => a + b

// 可选参数
function log(message: string, level?: string): void {
  console.log(`${level ?? 'INFO'}: ${message}`)
}

// 默认参数
function connect(host: string = 'localhost', port: number = 8080): void {
  console.log(`Connecting to ${host}:${port}`)
}
```

## 类

```typescript
class Person {
  name: string
  private age: number
  protected email: string

  constructor(name: string, age: number, email: string) {
    this.name = name
    this.age = age
    this.email = email
  }

  introduce(): string {
    return `I'm ${this.name}, ${this.age} years old`
  }
}

class Developer extends Person {
  skills: string[]

  constructor(name: string, age: number, email: string, skills: string[]) {
    super(name, age, email)
    this.skills = skills
  }

  override introduce(): string {
    return `${super.introduce()}. Skills: ${this.skills.join(', ')}`
  }
}
```

## 装饰器

### 组件装饰器

```typescript
// 页面入口装饰器
@Entry
@Component
struct HomePage {
  // 组件内容
}

// 组件定义装饰器
@Component
struct MyComponent {
  // 组件内容
}

// 动态构造内容装饰器（用于自定义弹窗等）
@Builder
struct CustomBuilder() {
  Text('Custom Content')
}

// 预览器装饰器
@Preview
@Component
struct PreviewExample {
  build() {
    Text('Preview')
  }
}
```

### 状态装饰器

```typescript
@Component
struct Counter {
  // 组件内状态 - 最基础的状态管理
  @State count: number = 0

  // 父组件单向传递
  @Prop title: string

  // 双向数据绑定
  @Link userInput: string

  // 应用于类实例的状态观察
  @State myData: MyData = new MyData()

  build() {
    Column() {
      Text(`Count: ${this.count}`)
      Button('Increment')
        .onClick(() => {
          this.count++
        })
    }
  }
}

// 对象观察装饰器
@Observed
class MyData {
  value: string = ''
}
```

### 资源引用装饰器

```typescript
// 应用资源
Text($r('app.string.title'))

// 媒体资源
Image($r('app.media.icon'))

// 原始文件
Text($rawfile('data.txt'))
```

## 生命周期

### 应用生命周期

```typescript
// entry/src/main/ets/Application.ets
import UIAbility from '@ohos.app.ability.UIAbility'

export default class MyAbility extends UIAbility {
  onCreate(want, launchParam) {
    // 应用创建时调用
  }

  onDestroy() {
    // 应用销毁时调用
  }

  onWindowStageCreate(windowStage) {
    // 窗口创建时调用
  }

  onWindowStageDestroy() {
    // 窗口销毁时调用
  }
}
```

### 组件生命周期

```typescript
@Component
struct LifecycleDemo {
  aboutToAppear() {
    // 组件即将显示
  }

  aboutToDisappear() {
    // 组件即将销毁
  }

  build() {
    Text('Lifecycle Demo')
  }
}
```

## 异步处理

```typescript
// Promise
function fetchData(): Promise<string> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve('Data loaded')
    }, 1000)
  })
}

// async/await
async function loadData(): Promise<void> {
  try {
    let result = await fetchData()
    console.log(result)
  } catch (error) {
    console.error('Error:', error)
  }
}
```

## 模块导入

```typescript
// 导入系统模块
import prompt from '@ohos.prompt'
import http from '@ohos.net.http'

// 导入应用内模块
import { Utils } from '../utils/Utils'

// 导入自定义组件
import { Header } from './components/Header'
