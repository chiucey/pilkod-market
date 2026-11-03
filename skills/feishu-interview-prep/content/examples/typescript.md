---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
---

# TypeScript 工程师面试准备示例

## TypeScript 第一面：类型系统与工程实践

### 面试题示例（30题）

| 题号 | 模块 | 题目 | 考察点 |
|------|------|------|--------|
| 001 | 类型基础 | TypeScript 和 JavaScript 的区别？ | 类型系统 |
| 002 | 类型基础 | type 和 interface 的区别？何时使用？ | 类型定义 |
| 003 | 类型基础 | 什么是泛型？泛型的应用场景？ | 泛型 |
| 004 | 类型基础 | any vs unknown vs never 的区别？ | 类型安全 |
| 005 | 类型基础 | TypeScript 的类型推断机制？ | 类型推断 |
| 006 | 联合类型 | 联合类型和交叉类型的区别？ | 类型组合 |
| 007 | 联合类型 | 可辨识联合类型（Discriminated Unions）？ | 类型设计 |
| 008 | 映射类型 | 什么是映射类型（Mapped Types）？ | 类型转换 |
| 009 | 映射类型 | Partial、Required、Readonly 实现原理？ | 内置工具类型 |
| 010 | 条件类型 | 什么是条件类型？infer 关键字？ | 高级类型 |
| 011 | 装饰器 | TypeScript 装饰器语法？和 JavaScript 装饰器区别？ | 元编程 |
| 012 | 模块系统 | ES Module 和 CommonJS 的区别？ | 模块化 |
| 013 | 命名空间 | namespace vs module？ | 代码组织 |
| 014 | 声明文件 | 什么是 .d.ts 声明文件？ | 类型声明 |
| 015 | 编译配置 | tsconfig.json 常用配置项？ | 编译选项 |
| 016 | 类型守卫 | 什么是类型守卫？typeof、instanceof、in？ | 类型收窄 |
| 017 | 类型守卫 | 自定义类型守卫如何实现？ | 类型收窄 |
| 018 | 枚举 | enum 和 const enum 的区别？ | 枚举 |
| 019 | 枚举 | 字符串枚举和数字枚举？ | 枚举 |
| 020 | 类 | public、private、protected、readonly 修饰符？ | 访问控制 |
| 021 | 类 | 抽象类和接口的区别？ | 面向对象 |
| 022 | 类 | 什么是 Mixin？如何实现？ | 多继承 |
| 023 | 函数 | 函数重载如何实现？ | 函数 |
| 024 | 函数 | 可选参数和默认参数？ | 函数 |
| 025 | 异步 | Promise、async/await 在 TypeScript 中的类型？ | 异步类型 |
| 026 | React | React + TypeScript 最佳实践？ | 框架集成 |
| 027 | Vue | Vue 3 + TypeScript 组件类型？ | 框架集成 |
| 028 | 类型体操 | 实现一个 DeepPartial 类型？ | 类型操作 |
| 029 | 类型体操 | 实现一个 RequiredKeys 类型？ | 类型操作 |
| 030 | 编译检查 | strict 模式有哪些检查？ | 类型检查 |

---

## TypeScript 第二面：工程化与架构

### 设计题示例

**题目：设计一个 TypeScript 组件库**

考察维度：
1. 类型设计（Props、Events、Slots）
2. 主题系统（CSS Variables、Theme Provider）
3. 组件 API 一致性设计
4. Tree-shaking 优化
5. 文档和示例生成

---

## TypeScript 强化训练示例

### 强化训练 001：高级类型操作

**目标**：从 ⚠️ 模糊 → 💪 熟练

**训练题**：
1. 如何实现一个只包含特定类型键的 Pick？
2. 什么是模板字面量类型？
3. 实现一个分布式条件类型？
4. 如何在类型层面区分数组和元组？
5. infer 关键字的高级用法？

---

## TypeScript 晋级评估标准

| 模块 | 精通要求 | 熟练要求 |
|------|---------|---------|
| 类型系统 | 类型推断原理、类型操作 | 熟练使用 |
| 泛型 | 约束、通配符、高阶类型 | 泛型设计 |
| 工程实践 | 类型守卫、类型守卫链 | 类型安全 |
| 框架集成 | React/Vue 类型绑定 | 组件类型 |
| 类型体操 | 复杂类型实现 | 工具类型 |
