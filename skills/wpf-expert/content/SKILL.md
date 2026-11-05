---
name: wpf-expert
description: |
  WPF 项目和 C# 开发专家。当用户要求开发 WPF 应用程序、设计 MVVM 架构、实现复杂 UI 界面、集成各种 UI 库（Material Design、MahApps、HandyControl）、处理 HTTP/gRPC/SignalR/MQTT 通讯、使用 Entity Framework/Dapper/MyBatis 操作数据库、编写高质量 C# 代码、进行软件自检诊断、异常处理、或者需要 .NET 技术栈的任意开发帮助时使用此技能。
---

# WPF 与 C# 专家技能

## 专业领域

### 1. WPF 核心技术

- **XAML 精通**: 数据绑定、命令、资源字典、样式、模板、触发器
- **MVVM 架构**: 模式实现、依赖注入、消息总线（Messenger/EventAggregator）
- **高级控件**: 自定义控件、ItemsControl、VirtualizingStackPanel
- **动画系统**: 故事板、时间线、第三方动画库
- **性能优化**: 虚拟化、延迟加载、UI 线程管理

### 2. UI 库集成

| 库名称 | 特点 | 适用场景 |
|--------|------|----------|
| MaterialDesignInXAML | Material Design 规范 | 现代企业应用 |
| MahApps.Metro | Metro/Fluent 风格 | Windows 10+ 桌面应用 |
| HandyControl | 丰富的组件库 | 快速开发 |
| Avalonia | 跨平台 WPF | Linux/macOS 支持 |
| Extended.Wpf.Toolkit | 专业控件集 | 高级表单/图表 |
| ControlzEx | Metro 控件库 | 现代化 Windows 应用 |

### 3. 通讯库专家

```
HTTP 通讯:
├── HttpClient (System.Net.Http)
├── RestSharp / Flurl
├── Refit (接口驱动 HTTP)
└── Polly (重试/熔断)

实时通讯:
├── SignalR (WebSocket/SSE)
├── WebSocketSharp / Fleck
├── MQTT (M2MqttX)
└── gRPC (Protobuf)

数据序列化:
├── System.Text.Json
├── Newtonsoft.Json
├── Protobuf-net
└── MessagePack-CSharp
```

### 4. ORM 框架支持（多库支持）

| ORM 框架 | 特点 | 适用场景 | 性能 |
|----------|------|----------|------|
| **Entity Framework Core** | 完整 ORM、功能丰富 | 企业级应用 | 中等 |
| **Dapper** | 轻量级、高性能、微 ORM | 高并发场景 | 极高 |
| **MyBatis.NET** | XML 配置、SQL 分离 | 复杂 SQL 项目 | 高 |
| **NHibernate** | 企业级、全功能 ORM | 大型企业系统 | 中等 |
| **ADO.NET** | 底层控制 | 极致性能需求 | 极高 |
| **PetaPoco** | 轻量级、简单易用 | 中小型项目 | 高 |

### 5. 数据库技术

```sql
数据库类型:
├── SQL Server / Azure SQL
├── PostgreSQL / MySQL / MariaDB
├── SQLite (嵌入式)
├── Redis (缓存)
└── MongoDB (NoSQL)

查询优化:
├── 分页查询 (Skip/Take, Offset/Fetch)
├── 批量操作 (BulkCopy, Batch Insert)
├── 事务管理 (TransactionScope, BeginTransaction)
└── 连接池配置
```

### 6. C# 语言精通

- **现代 C# 特性**: 记录类型、模式匹配、源生成器、异步流
- **LINQ 高级用法**: 表达式树、延迟执行、自定义扩展
- **委托与事件**: 事件聚合器、弱引用事件
- **泛型约束**: 协变/逆变、泛型方法
- **内存管理**: Span、Memory、内存池
- **源生成器**: 代码自动化、DI 容器生成

## 工作流程

### 任务分类处理

#### 1. 架构设计任务
1. 分析业务需求
2. 推荐技术栈组合
3. 提供分层架构方案
4. 编写核心代码模板

#### 2. 编码实现任务
1. 遵循企业编码规范
2. 应用设计模式
3. 编写可测试代码
4. 添加 XML 文档注释

#### 3. 问题诊断任务
1. 复现问题场景
2. 分析根本原因
3. 提供解决方案
4. 预防性建议

### 软件自检流程

```
┌─────────────────────────────────────────────────────────────┐
│                    软件健康度自检系统                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 编译诊断                                                │
│     ├── 依赖项检查 (NuGet 包版本兼容性)                        │
│     ├── 编译警告分析 (警告即错误原则)                           │
│     ├── 类型安全验证                                          │
│     └── 资源泄漏检测                                          │
│                                                             │
│  2. 运行时诊断                                              │
│     ├── 内存泄漏检测 (dotMemory,ANTS)                        │
│     ├── CPU 使用率分析                                        │
│     ├── 线程死锁检测                                          │
│     ├── UI 响应性检测                                         │
│     └── 异常日志分析                                          │
│                                                             │
│  3. 性能诊断                                                │
│     ├── 启动时间分析                                          │
│     ├── 内存占用分析                                          │
│     ├── 数据库查询性能 (SQL Profiler)                         │
│     ├── 网络请求延迟                                          │
│     └── 渲染性能监控                                          │
│                                                             │
│  4. 安全诊断                                                │
│     ├── 依赖项漏洞扫描 (OWASP)                                │
│     ├── 敏感信息检测                                          │
│     ├── XAML 安全审查                                         │
│     └── 权限配置检查                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 异常处理体系

```csharp
// 多层异常处理策略
public class GlobalExceptionHandler
{
    // 1. UI 层异常处理
    public void HandleUIException(Exception ex, string source)
    {
        // WPF DispatcherUnhandledException
        // 记录异常日志
        // 用户友好错误提示
        // 可选：发送异常报告
    }

    // 2. 业务层异常处理
    public Result<T> HandleBusinessException<T>(Func<T> operation)
    {
        try
        {
            return Result<T>.Success(operation());
        }
        catch (BusinessException ex)
        {
            return Result<T>.Failure(ex.Code, ex.Message);
        }
        catch (ValidationException ex)
        {
            return Result<T>.Failure("VALIDATION_ERROR", ex.Errors);
        }
    }

    // 3. 数据层异常处理
    public async Task<Result<T>> HandleDataException<T>(
        Func<Task<T>> operation,
        int maxRetries = 3)
    {
        for (int i = 0; i < maxRetries; i++)
        {
            try
            {
                return Result<T>.Success(await operation());
            }
            catch (SqlException ex) when (IsTransient(ex))
            {
                await Task.Delay(GetRetryDelay(i));
                continue;
            }
            catch (DbUpdateException ex)
            {
                throw new DataPersistenceException(
                    "数据库操作失败", ex);
            }
        }
    }

    // 4. 网络层异常处理
    public async Task<Result<T>> HandleNetworkException<T>(
        Func<Task<T>> operation)
    {
        try
        {
            return Result<T>.Success(await operation());
        }
        catch (HttpRequestException ex)
        {
            throw new NetworkException(
                "网络请求失败", ex);
        }
        catch (TaskCanceledException ex) when (ex.CancellationToken.IsCancellationRequested)
        {
            throw new NetworkException(
                "请求超时", ex);
        }
        catch (WebSocketException ex)
        {
            throw new WebSocketException(
                "WebSocket 连接失败", ex);
        }
    }
}
```

### 异常分类与处理策略

| 异常类型 | 触发场景 | 处理策略 | 示例 |
|----------|----------|----------|------|
| **ValidationException** | 数据验证失败 | 返回验证错误列表 | 输入格式错误 |
| **BusinessException** | 业务规则违反 | 业务告警、记录 | 余额不足 |
| **DataAccessException** | 数据库操作失败 | 重试、降级 | 连接超时 |
| **NetworkException** | 网络通讯失败 | 重试、离线缓存 | API 不可用 |
| **SecurityException** | 安全策略违反 | 审计、告警 | 未授权访问 |
| **ConcurrencyException** | 并发冲突 | 乐观锁重试 | 版本冲突 |
| **TimeoutException** | 操作超时 | 重试、超时提示 | 数据库查询超时 |
| **ResourceNotFoundException** | 资源不存在 | 404 处理 | 数据未找到 |

## 输出质量标准

- 所有代码示例通过编译检查
- 提供完整的可运行示例
- 包含必要的错误处理
- 添加代码审查清单
- 注明版本兼容性

## 参考资源

详见 `references/` 目录下的详细文档：
- `orm-comparison.md` - ORM 框架对比详解
- `mvvm-patterns.md` - MVVM 架构模式
- `exception-handling.md` - 异常处理最佳实践
- `performance-optimization.md` - 性能优化指南
- `communication-patterns.md` - 通讯模式详解
