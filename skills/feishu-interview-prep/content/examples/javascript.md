---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 958080d615bbfd30fec6f72bebfb8db8
    PropagateID: 958080d615bbfd30fec6f72bebfb8db8
    ReservedCode1: 304502205f69eacd71627afc20c7d6133949650c8195857f1f050b03e4421aa4f98ad63f0221009081bc0ddc01b4304b04130928f7e4ce08ef331b4550e29799c1ec28c5edee96
    ReservedCode2: 3046022100d056451466daaee2863ff6e35654a77a304ff2161dad272568d722dbd0be3470022100f7845d6f581b7c8b90c1c851120b0d3c1d97909f19ee1881ae072f0fdee4cf8e
---

# JavaScript/前端工程师面试准备示例

## JS 第一面：基础知识与技术深度

### 面试题示例（30题）

| 题号 | 模块 | 题目 | 考察点 |
|------|------|------|--------|
| 001 | 类型系统 | JavaScript 有哪些数据类型？typeof 的结果？ | 类型判断 |
| 002 | 类型系统 | == 和 === 的区别？类型转换规则？ | 隐式转换 |
| 003 | 类型系统 | 什么是 BigInt？什么场景使用？ | 大数 |
| 004 | 作用域 | var、let、const 的区别？ | 变量提升 |
| 005 | 作用域 | 什么是闭包？闭包的应用场景？ | 闭包 |
| 006 | 原型链 | 原型链的查找机制？instanceof 原理？ | 原型 |
| 007 | 原型链 | new 的实现过程？手写 new？ | 构造函数 |
| 008 | 继承 | 原型继承、构造函数继承、组合继承的区别？ | 继承方式 |
| 009 | 异步 | 什么是 Promise？Promise 解决了什么问题？ | 异步编程 |
| 010 | 异步 | async/await 的原理？Generator 协程？ | 异步语法 |
| 011 | 异步 | Promise.all、Promise.race 的区别？ | Promise API |
| 012 | 异步 | setTimeout 和 setImmediate 的区别？ | 事件循环 |
| 013 | 事件循环 | 浏览器事件循环？宏任务和微任务？ | 事件循环 |
| 014 | 事件循环 | Node.js 事件循环和浏览器区别？ | 事件循环 |
| 015 | this | this 的指向规则？call、apply、bind？ | this |
| 016 | 执行上下文 | 什么是执行上下文？作用域链？ | 运行环境 |
| 017 | 垃圾回收 | V8 垃圾回收算法？新生代和老年代？ | GC |
| 018 | 垃圾回收 | 什么是内存泄漏？哪些操作会导致？ | 内存管理 |
| 019 | 函子 | 什么是函子（Functor）？ | 函数式 |
| 020 | 函子 | 什么是 Monad？Promise 算 Monad 吗？ | 函数式 |
| 021 | 手写实现 | 手写防抖和节流？ | 手写能力 |
| 022 | 手写实现 | 深拷贝和浅拷贝？JSON.parse 的坑？ | 手写能力 |
| 023 | 手写实现 | 实现一个简易的 EventEmitter？ | 手写能力 |
| 024 | 手写实现 | 实现 Promise？ | 手写能力 |
| 025 | Vue | Vue 响应式原理？Object.defineProperty？ | 框架原理 |
| 026 | Vue | Vue 3 响应式原理？Proxy 的优势？ | 框架原理 |
| 027 | Vue | Vue 的 diff 算法？key 的作用？ | 虚拟DOM |
| 028 | React | React Hooks 的规则？useEffect 依赖？ | Hooks |
| 029 | React | React Fiber 架构？时间切片？ | 架构 |
| 030 | 浏览器 | 浏览器渲染过程？重排和重绘？ | 浏览器原理 |

---

## JS 第二面：系统设计与工程能力

### 设计题示例

**题目：设计一个前端监控 SDK**

考察维度：
1. 数据采集（错误、性能、行为）
2. 数据上报（节流、离线队列）
3. 源码定位（sourcemap）
4. 告警规则
5. 数据可视化

---

## JS 强化训练示例

### 强化训练 001：事件循环

**目标**：从 ⚠️ 模糊 → 💪 熟练

**训练题**：
1. 写出以下代码的输出顺序：
```javascript
console.log('1');
setTimeout(() => console.log('2'));
Promise.resolve().then(() => console.log('3'));
queueMicrotask(() => console.log('4'));
```
2. 为什么 Promise.then 是微任务而 setTimeout 是宏任务？
3. Node.js 中 process.nextTick 和 setImmediate 的区别？
4. 如何让代码按特定顺序执行？
5. 实现一个遵循 Promise/A+ 规范的 MiniPromise？

---

## JS 晋级评估标准

| 模块 | 精通要求 | 熟练要求 |
|------|---------|---------|
| 基础语法 | 深入原理 | 熟练使用 |
| 异步编程 | Promise 原理、手写实现 | async/await、并发控制 |
| 框架原理 | 源码级理解 | 响应式、虚拟DOM |
| 工程能力 | 性能优化、架构设计 | 构建工具、团队协作 |
| 前端工程化 | 工具链设计 | Webpack、Vite |
