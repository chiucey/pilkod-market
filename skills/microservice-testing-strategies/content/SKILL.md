---
name: microservice-testing-strategies
description: 微服务全栈测试策略技能。当用户讨论TDD、测试策略、微服务开发、单元测试、集成测试、组件测试、契约测试、端到端测试，或要求生成多层次测试用例时使用。引用自Martin Fowler的Microservice Testing文章。
---

# Microservice Testing Strategies

微服务测试策略技能，基于 [Martin Fowler - Testing Strategies in a Microservice Architecture](https://martinfowler.com/articles/microservice-testing/)。

## 核心原则

**TDD 不等于单元测试**。微服务架构引入网络边界后，测试策略需要重新审视。

## 测试金字塔

```
         ┌─────────────────────┐
         │   End-to-End Tests  │  ← 少量、慢、脆弱
         ├─────────────────────┤
         │ Component Tests     │  ← 中等数量
         │ Integration Tests   │
         ├─────────────────────┤
         │    Unit Tests       │  ← 大量、快速、易维护
         └─────────────────────┘
```

## 五层测试策略

### 1. Unit Tests（单元测试）

**定义**：测试最小可测试单元，验证其行为是否符合预期。

**两种风格**：
- **Sociable Unit Testing**：通过接口黑盒测试，观察状态变化
- **Solitary Unit Testing**：使用测试替身替换依赖

**应用场景**：
- 领域逻辑：使用真实领域对象测试复杂计算
- 管道代码：使用测试替身隔离外部依赖
- 协调逻辑：验证消息传递和响应

**关键洞察**：如果协调逻辑需要过多替身，通常表明应提取概念并独立测试。

---

### 2. Integration Tests（集成测试）

**定义**：验证组件间的通信路径和交互，检测接口缺陷。

**典型用例**：
- 验证与外部组件的交互（其他微服务、数据存储、缓存）
- 网关集成测试暴露协议级错误
- 持久化测试确保代码假设与数据存储匹配

**建议**：仅编写少量集成测试提供快速反馈，额外覆盖由单元测试和契约测试提供。

---

### 3. Component Tests（组件测试）

**定义**：将测试范围限制在系统的一部分，使用测试替身隔离被测代码。

**两种方式**：
- **进程内组件测试**：内存中实例化完整微服务，无网络开销
- **进程外组件测试**：针对独立进程部署的微服务执行

**暴露的内部资源**：
- 日志、功能开关、数据库命令、系统指标、健康检查、Ping资源

---

### 4. Contract Tests（契约测试）

**定义**：在外部服务边界验证其满足消费服务的契约。

**核心概念**：
- 契约 = 输入/输出数据结构 + 副作用 + 性能/并发特性
- 消费者驱动的契约（CDC）：各消费者形成不同契约

**工具**：Pact, Pacto, Janus

**好处**：
- 生产服务维护者了解变更对消费者的影响
- 支持使用并行变更方法安全进行API变更
- 新服务可由消费者驱动API设计

---

### 5. End-to-End Tests（端到端测试）

**定义**：验证系统满足外部需求并实现其目标，测试整个系统。

**两种方式**：
- **GUI驱动**：Selenium WebDriver等工具
- **Headless**：直接通过HTTP客户端操作微服务

**指南**：
1. **尽可能少写**：设定团队愿意等待的测试套件运行时间预算
2. **聚焦用户画像和旅程**：围绕用户画像和系统旅程建模
3. **明智选择端点**：必要时重新定义测试边界排除不稳定组件
4. **依赖IaC确保可重复性**：每次测试套件执行使用全新环境
5. **测试数据独立**：不依赖预存数据，使用公共/内部API构造实体

---

## 测试生成工作流

当进入TDD循环阶段时，自动生成以下维度的测试：

```
TDD Cycle:
  1. Write Unit Tests      → 单元测试
  2. Write Integration Tests → 边界和依赖测试
  3. Write Component Tests → 组件行为验证
  4. Write Contract Tests  → API契约验证（消费者视角）
  5. Write E2E Tests       → 关键用户旅程
```

## 参考

详细测试策略和示例见 `references/test-pyramid.md`。

## 引用来源

- [Martin Fowler - Testing Strategies in a Microservice Architecture](https://martinfowler.com/articles/microservice-testing/)
- Author: Toby Clemson
- Published: 18 November 2014
