---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: dfd2c78a04291a8ff3b472e9f97bfadc
    PropagateID: dfd2c78a04291a8ff3b472e9f97bfadc
    ReservedCode1: 30450220433affa60c4286d29f5e2fe99c0c2870cb4bf317664c06eeed1ad46400767dc5022100c19d05154ec5578ad422cbcd923a7dbb7313eed06f1484f198c5f7ac9c16c044
    ReservedCode2: 304402200a0b6e2b7395c5611d57a89955fdcb189aa8bc91707a42534b75a737ccd9d582022071f8326958b70f6cdefd27c490291993e0ff63b514b9aa8c5edbd14f9ed7ca7b
---

# Vue 工程师面试准备示例

## Vue 第一面：核心原理与进阶特性

### 面试题示例（30题）

| 题号 | 模块 | 题目 | 考察点 |
|------|------|------|--------|
| 001 | 响应式原理 | Vue 2 响应式原理？Object.defineProperty 的缺陷？ | 响应式 |
| 002 | 响应式原理 | Vue 3 响应式原理？Proxy 的优势？ | 响应式 |
| 003 | 响应式原理 | ref 和 reactive 的区别？ | 响应式API |
| 004 | 响应式原理 | watch 和 watchEffect 的区别？ | 侦听器 |
| 005 | 虚拟DOM | 什么是虚拟DOM？为什么要用它？ | VDOM |
| 006 | 虚拟DOM | Vue 的 diff 算法？key 的作用？ | diff算法 |
| 007 | 虚拟DOM | patch 过程？子节点对比策略？ | VDOM更新 |
| 008 | 生命周期 | Vue 2 生命周期钩子？执行顺序？ | 生命周期 |
| 009 | 生命周期 | Vue 3 生命周期钩子？和 Vue 2 的对应关系？ | 生命周期 |
| 010 | 组件通信 | 父子组件通信方式？props/$emit？ | 组件通信 |
| 011 | 组件通信 | 兄弟组件、跨级组件通信？EventBus、Vuex？ | 组件通信 |
| 012 | 组件通信 | provide/inject 的用法？ | 依赖注入 |
| 013 | 插槽 | 插槽 vs 作用域插槽？默认插槽 vs 具名插槽？ | 插槽 |
| 014 | 插槽 | Vue 3 插槽变化？$slots vs $attrs？ | 插槽 |
| 015 | 指令 | 自定义指令？钩子函数？ | 指令系统 |
| 016 | 指令 | v-if vs v-show 的区别？ | 渲染控制 |
| 017 | 进阶特性 | keep-alive 的作用？include/exclude？ | 缓存 |
| 018 | 进阶特性 | 异步组件？defineAsyncComponent？ | 懒加载 |
| 019 | 进阶特性 | Teleport 组件的用途？ | 新特性 |
| 020 | 进阶特性 | Suspense 组件？ | 异步加载 |
| 021 | Composition API | setup 函数？ref vs reactive？ | 组合式API |
| 022 | Composition API | computed 和 watch？ | 响应式 |
| 023 | Composition API | watchEffect vs watch？ | 侦听 |
| 024 | Composition API | 什么是插件？如何编写 Vue 插件？ | 插件系统 |
| 025 | Vue Router | 路由守卫？beforeEach、beforeRouteEnter？ | 路由 |
| 026 | Vue Router | hash 模式和 history 模式的区别？ | 路由模式 |
| 027 | Vue Router | 路由懒加载？component vs components？ | 路由 |
| 028 | 状态管理 | Vuex vs Pinia？Pinia 的优势？ | 状态管理 |
| 029 | 性能优化 | Vue 项目性能优化手段？ | 性能优化 |
| 030 | 原理源码 | nextTick 原理？微任务队列？ | 异步更新 |

---

## Vue 第二面：架构设计与工程实践

### 设计题示例

**题目：设计一个中后台管理系统的通用组件库**

考察维度：
1. 组件设计原则（API 一致性、易用性）
2. 主题系统（CSS Variables、动态主题）
3. 表单组件设计（校验、联动）
4. 权限控制（指令、路由守卫）
5. 构建优化（Tree-shaking、按需加载）

---

## Vue 强化训练示例

### 强化训练 001：响应式原理深入

**目标**：从 ⚠️ 模糊 → 💪 熟练

**训练题**：
1. 为什么 Vue 2 无法检测数组下标变化？如何解决？
2. Vue.set/delete 的实现原理？
3. Vue 3 中 ref 和 reactive 的实现区别？
4. watchEffect 中访问响应式数据会收集依赖吗？
5. 如何手动实现一个简易的响应式系统？

---

## Vue 晋级评估标准

| 模块 | 精通要求 | 熟练要求 |
|------|---------|---------|
| 响应式原理 | 源码级理解 | 响应式特性 |
| 虚拟DOM | diff算法细节 | 更新机制 |
| 组件系统 | 通信模式、插槽 | 组件化 |
| Composition API | 逻辑复用、TS支持 | 组合式开发 |
| 工程实践 | 性能优化、构建 | 最佳实践 |
