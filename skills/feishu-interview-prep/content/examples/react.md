---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
---

# React 工程师面试准备示例

## React 第一面：核心原理与Hooks

### 面试题示例（30题）

| 题号 | 模块 | 题目 | 考察点 |
|------|------|------|--------|
| 001 | 核心概念 | 虚拟DOM是什么？有什么优势？ | VDOM |
| 002 | 核心概念 | React 元素和组件的区别？ | JSX |
| 003 | 核心概念 | 什么是 Fiber？Fiber 架构解决了什么问题？ | Fiber |
| 004 | 核心概念 | React 的渲染流程？ reconciliation 过程？ | 渲染 |
| 005 | 生命周期 | React 16之前的生命周期？shouldComponentUpdate？ | 生命周期 |
| 006 | 生命周期 | React 16+的生命周期？getDerivedStateFromProps？ | 生命周期 |
| 007 | 生命周期 | 为什么 componentWillReceiveProps 被废弃？ | 生命周期 |
| 008 | Hooks | Hooks 的规则？什么是 Hooks 的调用顺序？ | Hooks规则 |
| 009 | Hooks | useState 的实现原理？ | Hooks |
| 010 | Hooks | useEffect 和 useLayoutEffect 的区别？ | 副作用 |
| 011 | Hooks | useCallback 和 useMemo 的区别？ | 优化 |
| 012 | Hooks | useRef 的用法？ref 的转发？ | Ref |
| 013 | Hooks | 自定义 Hooks 如何实现？ | 逻辑复用 |
| 014 | Hooks | useReducer 适合什么场景？ | 状态管理 |
| 015 | Hooks | useContext 的原理？ | Context |
| 016 | 状态管理 | Context 的原理？优缺点？ | 状态 |
| 017 | 状态管理 | Redux vs MobX vs Zustand？ | 状态管理 |
| 018 | 状态管理 | Redux 中间件机制？redux-thunk vs redux-saga？ | 中间件 |
| 019 | 性能优化 | React.memo 和 PureComponent 的区别？ | 优化 |
| 020 | 性能优化 | 如何避免不必要的渲染？React DevTools Profiler？ | 优化 |
| 021 | 性能优化 | 代码分割？React.lazy 和 Suspense？ | 优化 |
| 022 | 高级特性 | 什么是 Portals？使用场景？ | 高级特性 |
| 023 | 高级特性 | 什么是 Error Boundaries？如何实现？ | 错误处理 |
| 024 | 高级特性 | 什么是 Fragment？和数组的区别？ | JSX |
| 025 | 并发特性 | 什么是 Concurrent Mode？ | 并发 |
| 026 | 并发特性 | useTransition 和 useDeferredValue 的用途？ | 并发 |
| 027 | 并发特性 | 什么是 Suspense for Data Fetching？ | 并发 |
| 028 | 服务端渲染 | SSR vs SSG vs CSR？ | 渲染模式 |
| 029 | 服务端渲染 | Next.js 的渲染模式？getServerSideProps？ | SSR |
| 030 | 原理源码 | setState 是同步还是异步？批处理机制？ | 状态更新 |

---

## React 第二面：架构设计与工程实践

### 设计题示例

**题目：设计一个企业级中台应用架构**

考察维度：
1. 状态管理方案（全局状态、服务器状态）
2. 权限控制系统（路由权限、按钮权限）
3. 表单解决方案（动态表单、复杂校验）
4. 微前端架构（qiankun）
5. 性能监控和优化

---

## React 强化训练示例

### 强化训练 001：Hooks 原理深入

**目标**：从 ⚠️ 模糊 → 💪 熟练

**训练题**：
1. Hooks 为什么必须在组件顶层调用？
2. 如何自己实现一个 useState？
3. useEffect 的依赖数组为空和不传有什么区别？
4. React 如何追踪 Hooks 的调用顺序？
5. 什么是 Hooks 的"每次渲染"模型？

---

## React 晋级评估标准

| 模块 | 精通要求 | 熟练要求 |
|------|---------|---------|
| 核心原理 | Fiber架构、调和算法 | VDOM、渲染 |
| Hooks | 原理、自定义Hooks | 常用Hooks |
| 状态管理 | 状态管理方案选型 | Redux/Zustand |
| 性能优化 | 渲染优化、Bundle优化 | Profiler |
| 工程实践 | 架构设计、团队协作 | 最佳实践 |
