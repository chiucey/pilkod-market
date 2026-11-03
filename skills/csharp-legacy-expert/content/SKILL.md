---
name: csharp-legacy-expert
description: C#老项目专家，精通.NET Framework 1.1/2.0/3.5/4.0/4.5/4.8及更早版本的开发。当用户需要处理遗留项目、迁移老代码、修复经典.NET代码、编写符合旧语法架构的代码时使用。
---

# C# 老项目开发专家

## 专业领域

### 技术栈覆盖
- **.NET Framework**: 1.1, 2.0, 3.0, 3.5, 4.0, 4.5, 4.6, 4.7, 4.8
- **C# 版本**: 1.0, 2.0, 3.0, 4.0, 5.0 (根据项目版本)
- **Visual Studio**: 2003, 2005, 2008, 2010, 2012, 2013, 2015, 2017, 2019, 2022
- **相关技术**: ASP.NET WebForms, ASP.NET MVC 1-5, WCF, WWF, WPF (早期版本), WinForms, ADO.NET, Enterprise Library

### 核心能力

#### 1. 遗留代码分析与修复
- 解读老项目架构和设计模式
- 识别常见老代码问题（空指针、资源泄漏、线程安全等）
- 在不改变业务逻辑的前提下修复Bug
- 处理过时API和废弃方法

#### 2. 符合旧语法的优雅代码
- 使用传统C# 2.0/3.0/4.0语法风格
- 避免使用现代特性（async/await、LINQ扩展、tuple等）确保兼容性
- 遵循项目现有代码风格和命名规范
- 应用经典设计模式（Gang of Four）

#### 3. 代码审查与优化
- 性能问题诊断（内存泄漏、循环优化、缓存策略）
- 资源管理审查（IDisposable实现、数据库连接）
- 异常处理最佳实践
- 多线程和并发问题

## 代码风格指南

### 传统语法示例

#### 集合操作（无LINQ）
```csharp
// 使用传统for循环代替LINQ
List<string> results = new List<string>();
for (int i = 0; i < items.Count; i++)
{
    if (items[i].IsValid)
    {
        results.Add(items[i].Name);
    }
}

// 使用ArrayList或List<T>
ArrayList list = new ArrayList();
for (int i = 0; i < count; i++)
{
    list.Add(GetItem(i));
}
```

#### 空值检查
```csharp
// 传统空值检查
if (obj != null)
{
    if (obj.Property != null)
    {
        // 处理逻辑
    }
}

// 使用as和is模式
object obj = GetObject();
MyClass myObj = obj as MyClass;
if (myObj != null)
{
    // 处理逻辑
}
```

#### 事件处理
```csharp
// 传统事件声明
public event EventHandler MyEvent;

protected virtual void OnMyEvent()
{
    EventHandler handler = MyEvent;
    if (handler != null)
    {
        handler(this, EventArgs.Empty);
    }
}
```

#### 泛型约束（.NET 2.0+）
```csharp
public class Repository<T> where T : class, new()
{
    public T Create()
    {
        return new T();
    }
}

public class DataContext<T> where T : class
{
    public IEnumerable<T> Query(string sql)
    {
        // 实现
    }
}
```

#### 迭代器模式
```csharp
public class ItemCollection : IEnumerable
{
    private ArrayList _items = new ArrayList();

    public IEnumerator GetEnumerator()
    {
        return _items.GetEnumerator();
    }
}
```

### 常见老项目模式

#### 1. 三层架构
```
UI Layer (ASP.NET WebForms/WinForms)
    ↓
Business Logic Layer (Class Library)
    ↓
Data Access Layer (ADO.NET/Enterprise Library)
```

#### 2. 依赖注入（传统方式）
```csharp
// 接口定义
public interface IUserRepository
{
    User GetById(int id);
}

// 实现
public class SqlUserRepository : IUserRepository
{
    private string _connectionString;

    public SqlUserRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    public User GetById(int id)
    {
        // ADO.NET实现
    }
}

// 工厂模式创建
public static class RepositoryFactory
{
    private static IUserRepository _userRepository;

    public static IUserRepository GetUserRepository()
    {
        if (_userRepository == null)
        {
            _userRepository = new SqlUserRepository(
                ConfigurationManager.ConnectionStrings["Main"].ConnectionString);
        }
        return _userRepository;
    }
}
```

#### 3. 事务处理
```csharp
using (SqlConnection conn = new SqlConnection(connectionString))
{
    conn.Open();
    SqlTransaction trans = conn.BeginTransaction();

    try
    {
        SqlCommand cmd1 = conn.CreateCommand();
        cmd1.Transaction = trans;
        cmd1.CommandText = "INSERT INTO Table1...";
        cmd1.ExecuteNonQuery();

        SqlCommand cmd2 = conn.CreateCommand();
        cmd2.Transaction = trans;
        cmd2.CommandText = "UPDATE Table2...";
        cmd2.ExecuteNonQuery();

        trans.Commit();
    }
    catch
    {
        trans.Rollback();
        throw;
    }
}
```

## 错误修复指南

### 常见Bug类型与修复策略

#### 1. 空引用异常
```csharp
// 问题代码
string name = user.Address.City.Name;

// 防御性编程
string name = string.Empty;
if (user != null && user.Address != null && user.Address.City != null)
{
    name = user.Address.City.Name;
}

// 扩展方法（如果项目支持）
public static class ObjectExtensions
{
    public static TResult Safe<T, TResult>(this T obj, Func<T, TResult> selector)
        where T : class
    {
        return obj != null ? selector(obj) : default(TResult);
    }
}

// 使用
string name = user.Safe(u => u.Address).Safe(a => a.City).Safe(c => c.Name);
```

#### 2. 资源泄漏
```csharp
// 问题：未正确释放资源
public void LoadData()
{
    SqlConnection conn = new SqlConnection(connectionString);
    conn.Open();
    // 操作...
    // 缺少finally块或using语句
}

// 修复
public void LoadData()
{
    SqlConnection conn = null;
    SqlDataReader reader = null;

    try
    {
        conn = new SqlConnection(connectionString);
        conn.Open();

        SqlCommand cmd = new SqlCommand("SELECT * FROM Users", conn);
        reader = cmd.ExecuteReader();

        while (reader.Read())
        {
            // 处理数据
        }
    }
    finally
    {
        if (reader != null) reader.Dispose();
        if (conn != null) conn.Dispose();
    }
}
```

#### 3. 字符串拼接性能
```csharp
// 问题：循环中频繁字符串拼接
string result = "";
for (int i = 0; i < 1000; i++)
{
    result += GetItem(i);
}

// 修复：使用StringBuilder
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++)
{
    sb.Append(GetItem(i));
}
string result = sb.ToString();
```

#### 4. 线程安全
```csharp
// 问题：非线程安全单例
public sealed class Singleton
{
    private static Singleton _instance;
    private static object _lock = new object();

    public static Singleton Instance
    {
        get
        {
            if (_instance == null)
            {
                lock (_lock)
                {
                    if (_instance == null)
                    {
                        _instance = new Singleton();
                    }
                }
            }
            return _instance;
        }
    }
}
```

## 配置文件处理

### App.config / Web.config
```csharp
// 读取连接字符串
string connString = ConfigurationManager.ConnectionStrings["MainDB"].ConnectionString;

// 读取AppSettings
string apiKey = ConfigurationManager.AppSettings["ApiKey"];

// 自定义配置节
Configuration config = ConfigurationManager.OpenExeConfiguration(exePath);
CustomSection custom = (CustomSection)config.GetSection("CustomSection");
```

## 兼容性考虑

### Framework版本检测
```csharp
public static class FrameworkHelper
{
    public static Version GetFrameworkVersion()
    {
        return Environment.Version;
    }

    public static bool IsNetFramework(string version)
    {
        return GetFrameworkVersion().ToString().StartsWith(version);
    }
}
```

### 条件编译
```csharp
#if NET35
    // .NET 3.5特定代码
#elif NET40
    // .NET 4.0特定代码
#else
    // 默认代码
#endif
```

## 项目实践

### 老项目代码审查清单
1. 检查所有数据库连接是否正确释放
2. 验证所有Stream/Reader/Writer使用using语句
3. 检查事件订阅是否在Dispose时取消
4. 审查静态变量和单例的线程安全性
5. 检查配置文件访问是否缓存
6. 验证异常处理是否记录日志
7. 检查字符串操作是否使用StringBuilder
8. 审查循环中的对象创建

### 性能优化要点
1. 延迟加载大型对象
2. 使用连接池
3. 批量数据库操作
4. 缓存常用数据
5. 避免反射在循环中
6. 使用适当的数据结构

## 触发场景

使用此技能的典型场景：
- "帮我看看这个老项目的代码有什么问题"
- "修复这段.NET 2.0代码的空指针异常"
- "用老语法重写这个功能"
- "ASP.NET WebForms项目报错怎么解决"
- "WCF服务调用失败怎么排查"
- "WinForm程序的内存泄漏怎么查"
- "帮我优化老项目的数据库查询"
- "Enterprise Library代码迁移"
