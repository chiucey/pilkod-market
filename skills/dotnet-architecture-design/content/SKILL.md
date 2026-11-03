---
name: dotnet-architecture-design
description: 掌握.NET应用架构设计能力。当用户要求进行系统设计、架构决策、技术选型、代码分层、使用SOLID原则、设计模式（创建型/结构型/行为型/架构型）、DDD领域驱动设计、CQRS模式、或讨论Clean Architecture分层时使用。
---

# .NET 架构设计能力

## 架构设计原则

### SOLID 原则深入实践

- **单一职责(SRP)**：类的单一职责判断、模块边界设计
- **开闭原则(OCP)**：扩展方式、装饰器模式应用
- **里氏替换(LSP)**：继承层次设计、协变逆变
- **接口隔离(ISP)**：接口粒度、职责分离
- **依赖反转(DIP)**：依赖注入、控制反转

### 设计模式精通

| 模式类别 | 核心模式 | 应用场景 |
|---------|---------|---------|
| 创建型 | Factory, Builder, Singleton | 对象创建复杂场景 |
| 结构型 | Adapter, Decorator, Facade, Proxy | 遗留系统适配、扩展功能 |
| 行为型 | Strategy, Observer, Command, Mediator | 业务规则切换、事件处理 |
| 架构型 | CQRS, Event Sourcing, Repository | 复杂业务、审计需求 |

## 分层架构设计

### 经典分层架构

| 架构类型 | 分层结构 | 适用场景 |
|---------|---------|---------|
| 经典三层 | UI层 / Business层 / DataAccess层 | 简单业务系统 |
| DDD分层 | Domain层 / Application层 / Infrastructure层 / UI层 | 复杂业务域 |
| 六边形架构 | 端口与适配器分离 | 高度可测试性需求 |
| 洋葱架构 | 核心业务 / Ports / Adapters | 业务逻辑与技术解耦 |

## 核心技能清单

| 技能项 | 熟练度 | 说明 |
|-------|-------|------|
| SOLID Principles | ⭐⭐⭐⭐⭐ | 面向对象设计原则 |
| Design Patterns | ⭐⭐⭐⭐⭐ | 常用23种设计模式 |
| DDD领域驱动设计 | ⭐⭐⭐⭐ | 限界上下文、聚合根、领域事件 |
| Clean Architecture | ⭐⭐⭐⭐ | 清晰架构分层 |
| CQRS模式 | ⭐⭐⭐⭐ | 命令查询分离 |
| Event Sourcing | ⭐⭐⭐⭐ | 事件溯源模式 |
| Repository Pattern | ⭐⭐⭐⭐ | 仓储模式实现 |
| Unit of Work | ⭐⭐⭐⭐ | 工作单元模式 |

## 技术选型能力

### 数据存储选型

| 场景 | 推荐方案 | 决策依据 |
|-----|---------|---------|
| 强一致性事务 | 关系型数据库 (SQL Server/PostgreSQL) | ACID 特性 |
| 高并发读写 | NoSQL (MongoDB/Cassandra) + 缓存 | 水平扩展能力 |
| 复杂查询 | 关系型 + 读写分离 | SQL 表达能力 |
| CQRS分离 | 命令端写数据库 + 查询端读模型 | 读写职责分离 |

### 通信模式选型

| 通信类型 | 技术方案 | 适用场景 |
|---------|---------|---------|
| 同步通信 | REST API, gRPC | 请求-响应模式 |
| 异步通信 | RabbitMQ, Azure Service Bus, Kafka | 解耦、削峰 |
| 双工通信 | SignalR, WebSocket | 实时推送需求 |
| 事件驱动 | Event Bus, Domain Events | 微服务间协作 |

### 缓存层设计

```
多级缓存策略：
┌─────────────────────────────────────────┐
│            Client Cache                 │
│         (Browser/APP Cache)             │
└─────────────────┬───────────────────────┘
                  │ Miss
┌─────────────────▼───────────────────────┐
│            CDN Cache                     │
│        (Static Content Only)             │
└─────────────────┬───────────────────────┘
                  │ Miss
┌─────────────────▼───────────────────────┐
│          Distributed Cache               │
│        (Redis/Memory Cache)             │
└─────────────────┬───────────────────────┘
                  │ Miss
┌─────────────────▼───────────────────────┐
│          Database / Data Source          │
└─────────────────────────────────────────┘
```

## 项目结构模板

### DDD 分层结构示例

```
src/
├── Domain/
│   ├── Entities/
│   ├── ValueObjects/
│   ├── Aggregates/
│   ├── Events/
│   ├── Repositories/
│   └── Services/
├── Application/
│   ├── Commands/
│   ├── Queries/
│   ├── DTOs/
│   ├── Interfaces/
│   └── Services/
├── Infrastructure/
│   ├── Persistence/
│   ├── Caching/
│   ├── Messaging/
│   └── ExternalServices/
└── Presentation/
    ├── Controllers/
    ├── Middleware/
    └── Filters/
```

### CQRS 架构示例

```
Application/
├── Commands/
│   ├── CreateOrderCommand
│   ├── UpdateOrderCommand
│   └── DeleteOrderCommand
├── Queries/
│   ├── GetOrderByIdQuery
│   └── GetOrdersByCustomerQuery
├── CommandHandlers/
│   └── OrderCommandHandler
└── QueryHandlers/
    └── OrderQueryHandler
```

## 设计模式应用指南

### 创建型模式场景

- **Singleton**：配置管理、日志服务、连接池
- **Factory Method**：跨平台UI组件、数据库连接
- **Builder**：复杂对象构建（SQL查询、HTTP请求）
- **Abstract Factory**：多数据源切换、主题系统

### 结构型模式场景

- **Adapter**：遗留系统集成、第三方库封装
- **Decorator**：日志增强、缓存包装、事务装饰
- **Facade**：复杂子系统简化、Service层封装
- **Proxy**：远程调用保护、延迟加载

### 行为型模式场景

- **Strategy**：支付方式选择、排序算法切换
- **Observer**：事件通知、UI绑定、分布式事件
- **Command**：撤销/重做、批处理队列
- **Mediator**：微服务间协调、UI组件通信

## 架构决策记录模板

当进行架构决策时，应记录：

```markdown
## ADR-XXX: [决策标题]

### 状态
[提议/接受/已废弃/已替代]

### 背景
[描述需要解决的问题]

### 决策
[描述采取的方案]

### 后果
- 正面影响：...
- 负面影响：...
- 风险缓解：...
```

## 常见架构问题解决方案

| 问题 | 症状 | 解决方案 |
|-----|-----|---------|
| 领域逻辑泄露 | Service层过胖 | 领域事件、Specification模式 |
| 循环依赖 | 编译错误 | 依赖倒置、事件驱动 |
| 性能瓶颈 | 数据库过载 | CQRS、读写分离、缓存 |
| 一致性冲突 | 数据不一致 | Saga模式、最终一致性 |
| 测试困难 | 耦合度过高 | 依赖注入、Mock框架 |

## 参考资源

详细的设计模式和架构模式示例见 `references/` 目录：
- `solid-principles.md` - SOLID 原则详解
- `design-patterns.md` - 设计模式实现示例
- `cqrs-pattern.md` - CQRS 完整实现指南
- `ddd-fundamentals.md` - DDD 核心概念
