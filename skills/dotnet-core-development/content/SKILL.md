---
name: dotnet-core-development
description: 掌握 .NET Core/5+ 核心开发技能。当用户要求进行 .NET Core 基础开发、C# 新特性、依赖注入、配置管理、日志系统、或需要创建标准 .NET 项目结构时使用。
---

# .NET Core 开发技能

## 核心技能清单

| 技能项 | 熟练度 | 说明 |
|-------|-------|------|
| C# 新特性 | ⭐⭐⭐⭐⭐ | 8.0-12.0 新特性 |
| 依赖注入 | ⭐⭐⭐⭐⭐ | DI/IoC 容器 |
| 泛型 & 集合 | ⭐⭐⭐⭐⭐ | 泛型约束、集合操作 |
| 委托 & 事件 | ⭐⭐⭐⭐⭐ | 委托链、事件处理 |
| 表达式树 | ⭐⭐⭐⭐ | Expression Tree |
| 反射 & 特性 | ⭐⭐⭐⭐ | 运行时动态编程 |

## C# 新特性 (8.0-12.0)

### 模式匹配增强

```csharp
// 开关表达式
var result = shape switch
{
    Circle { Radius: var r } when r > 0 => $"Circle with radius {r}",
    Rectangle { Width: var w, Height: var h } => $"Rectangle {w}x{h}",
    _ => "Unknown shape"
};

// 属性模式
if (person is Person { Age: >= 18, Name: var name })
{
    Console.WriteLine($"Adult: {name}");
}

// 元组模式
string classify(int a, int b) => (a, b) switch
{
    (> 0, > 0) => "both positive",
    (< 0, < 0) => "both negative",
    _ => "mixed"
};
```

### 空值运算符

```csharp
// 空合并赋值
name ??= "Default";

// 可空引用类型
string? nullable = null;
string nonNullable = nullable ?? throw new ArgumentNullException();

// 条件表达式
var length = name?.Length ?? 0;

// 文件可为 null
public class Person
{
    public string? MiddleName { get; set; }
}
```

### 记录类型 (Record)

```csharp
// 基础记录
public record Person(string FirstName, string LastName);

// 可变记录
public record Person
{
    public string FirstName { get; set; }
    public string LastName { get; set; }
}

// with 表达式
var person2 = person1 with { LastName = "Smith" };

// 记录相等性
var p1 = new Person("John", "Doe");
var p2 = new Person("John", "Doe");
Console.WriteLine(p1 == p2); // True

// 记录继承
public record Student(string FirstName, string LastName, int Grade) 
    : Person(FirstName, LastName);
```

### 源生成器 (Source Generators)

```csharp
// 增量源生成器
[Generator]
public class AutoNotifyGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        context.RegisterPostInitializationOutput(ctx =>
            ctx.CreateOutputFile("generated.txt", "content"));
    }
}

// 属性示例
[AutoNotify]
public partial class Person
{
    [property: AutoNotify]
    private string? _name;
}
```

## 依赖注入 (DI)

### 服务注册

```csharp
public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        // 单例 - 整个应用生命周期只有一个实例
        services.AddSingleton<IProductService, ProductService>();
        
        // 瞬态 - 每次请求创建新实例
        services.AddTransient<ILogger, FileLogger>();
        
        // 作用域 - 每个请求创建一个实例
        services.AddScoped<IUserContext, UserContext>();
        
        // 带工厂的服务
        services.AddSingleton<IService>(sp => new Service());
        
        // 配置选项
        services.Configure<AppSettings>(
            Configuration.GetSection("AppSettings"));
        
        // 多接口注册
        services.AddSingleton<ICache, RedisCache>();
        services.AddSingleton<ICache>(sp => 
            new MemoryCache(sp.GetRequiredService<IMemoryCache>()));
    }
}
```

### 服务生命周期

```csharp
// IServiceProvider 使用
public class OrderService
{
    private readonly IServiceProvider _serviceProvider;

    public OrderService(IServiceProvider serviceProvider)
    {
        _serviceProvider = serviceProvider;
    }

    public void ProcessOrder()
    {
        // 创建新的作用域
        using var scope = _serviceProvider.CreateScope();
        var repository = scope.ServiceProvider
            .GetRequiredService<IOrderRepository>();
    }
}
```

### 泛型服务注册

```csharp
services.AddScoped(typeof(IRepository<>), typeof(Repository<>));

// 使用
public class OrderRepository :IRepository<Order>
{
    public Order GetById(int id) { /* ... */ }
}

services.AddScoped<IRepository<Order>, OrderRepository>();
```

## 泛型 & 集合

### 泛型约束

```csharp
// 基类约束
public class EntityValidator<T> where T : Entity
{
    public bool Validate(T entity) => entity.IsValid();
}

// 接口约束
public interface IRepository<T> where T : class
{
    Task<T> GetByIdAsync(int id);
}

// 构造函数约束
public class Factory<T> where T : new()
{
    public T Create() => new T();
}

// 多个约束
public class DataService<T, TRepository>
    where T : Entity
    where TRepository : IRepository<T>, new()
{
    public async Task<T> GetAndProcess(int id)
    {
        var repository = new TRepository();
        return await repository.GetByIdAsync(id);
    }
}
```

### 集合操作

```csharp
// Span<T> 性能优化
Span<int> numbers = stackalloc int[] { 1, 2, 3, 4, 5 };
var slice = numbers.Slice(1, 3);

// 索引和范围
var array = new[] { 1, 2, 3, 4, 5 };
var last = array[^1];      // 5
var slice = array[1..3];   // [2, 3]

// 列表模式匹配
var list = new List<int> { 1, 2, 3 };
if (list is [var first, .. var rest])
{
    Console.WriteLine($"{first}, {rest.Count}");
}
```

## 委托 & 事件

### 委托链

```csharp
// 多播委托
public delegate void ProgressHandler(int percent);

public class Process
{
    public event ProgressHandler OnProgress = delegate { };

    public void Execute()
    {
        OnProgress(25);
        OnProgress(50);
        OnProgress(100);
    }
}

// 添加和移除事件处理器
var process = new Process();
process.OnProgress += Console.WriteLine;
process.OnProgress += file.WriteLine;
process.OnProgress -= Console.WriteLine;
```

### Func & Action

```csharp
// Func<T, TResult> - 有返回值
Func<int, int, int> add = (a, b) => a + b;
Func<string> getDefault = () => "default";

// Action<T> - 无返回值
Action<string> log = Console.WriteLine;
Action<int, string> logWithLevel = (level, msg) => { };

// 闭包
var processors = new List<Action>();
for (int i = 0; i < 3; i++)
{
    int captured = i; // 捕获变量
    processors.Add(() => Console.WriteLine(captured));
}
```

## 表达式树 (Expression Tree)

```csharp
using System.Linq.Expressions;

// 编译表达式
Expression<Func<int, int, int>> expr = (a, b) => a + b;
var compiled = expr.Compile();
Console.WriteLine(compiled(2, 3)); // 5

// 构建表达式
var parameter = Expression.Parameter(typeof(int), "x");
var constant = Expression.Constant(10);
var body = Expression.Add(parameter, constant);
var lambda = Expression.Lambda<Func<int, int>>(body, parameter);

// 动态查询
public IQueryable<T> Where<T>(
    IQueryable<T> source, 
    string propertyName, 
    object value)
{
    var prop = Expression.PropertyOrField(
        Expression.Parameter(typeof(T)), propertyName);
    var constant = Expression.Constant(value);
    var equality = Expression.Equal(prop, constant);
    return source.Where(
        Expression.Lambda<Func<T, bool>>(equality, 
            Expression.Parameter(typeof(T))));
}
```

## 反射 & 特性

### 反射使用

```csharp
// 获取类型信息
var type = typeof(Order);
var properties = type.GetProperties();
var methods = type.GetMethods();

// 动态创建实例
var instance = Activator.CreateInstance(type);

// 调用方法
var method = type.GetMethod("Process");
method.Invoke(instance, null);

// 泛型类型
var genericType = typeof(List<>);
var specificType = genericType.MakeGenericType(typeof(string));
var list = Activator.CreateInstance(specificType);
```

### 自定义特性

```csharp
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class AuditAttribute : Attribute
{
    public string Description { get; set; }
}

[Audit(Description = "订单处理")]
public class OrderService
{
    [Audit(Description = "处理方法")]
    public void Process() { }
}

// 使用特性
public static class AuditHelper
{
    public static IEnumerable<MethodInfo> GetAuditedMethods(Type type)
    {
        return type.GetMethods()
            .Where(m => m.GetCustomAttribute<AuditAttribute>() != null);
    }
}
```

## 项目模板

### 标准项目结构

```
src/
├── MyApp.Core/           # 核心业务逻辑
│   ├── Entities/
│   ├── Interfaces/
│   ├── Services/
│   └── Extensions/
│
├── MyApp.Infrastructure/ # 基础设施
│   ├── Data/
│   ├── Caching/
│   ├── Logging/
│   └── ExternalServices/
│
├── MyApp.Api/            # Web API
│   ├── Controllers/
│   ├── Middleware/
│   ├── Filters/
│   └── Program.cs
│
└── MyApp.Tests/          # 测试项目
    ├── Unit/
    ├── Integration/
    └── Fixtures/
```
