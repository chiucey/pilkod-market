---
name: dotnet-performance-optimization
description: 掌握 .NET 性能优化技能。当用户要求进行性能分析、内存优化、数据库优化、缓存策略、响应时间优化、或使用诊断工具时使用。
---

# 性能优化技能

## 核心技能清单

| 技能项 | 熟练度 | 说明 |
|-------|-------|------|
| 性能分析 | ⭐⭐⭐⭐⭐ | dotnet-trace、PerfView |
| 内存管理 | ⭐⭐⭐⭐⭐ | GC 调优、内存泄漏 |
| 并行编程 | ⭐⭐⭐⭐⭐ | Task、Parallel |
| 数据库优化 | ⭐⭐⭐⭐⭐ | 索引、查询优化 |
| 缓存策略 | ⭐⭐⭐⭐⭐ | 多级缓存、本地/分布式 |
| Benchmark | ⭐⭐⭐⭐⭐ | BenchmarkDotNet |

## 性能分析工具

### dotnet-trace

```bash
# 安装工具
dotnet tool install --global dotnet-trace

# 收集性能数据
dotnet-trace collect -p <pid> --providers Microsoft-Windows-DotNETRuntime

# 收集指定时长
dotnet-trace collect -p <pid> --duration 00:00:30 --output trace.nettrace

# 分析文件
dotnet-trace convert trace.nettrace --format speedscope
```

### PerfView

```csharp
// 添加诊断代码
using System.Diagnostics.Tracing;

[EventSource(Name = "MyApp-Performance")]
public class PerformanceEventSource : EventSource
{
    public static readonly PerformanceEventSource Log = 
        new PerformanceEventSource();

    public void RequestStart(string path)
    {
        WriteEvent(1, path);
    }

    public void RequestStop(string path, long elapsedMs)
    {
        WriteEvent(2, path, elapsedMs);
    }
}

// 使用
public class HomeController : Controller
{
    public IActionResult Index()
    {
        PerformanceEventSource.Log.RequestStart("/Home/Index");
        try
        {
            var data = _service.GetData();
            return View(data);
        }
        finally
        {
            PerformanceEventSource.Log.RequestStop("/Home/Index", stopwatch.ElapsedMilliseconds);
        }
    }
}
```

## 内存管理

### GC 调优

```csharp
// Program.cs 配置
public class Program
{
    public static void Main(string[] args)
    {
        // 服务器 GC 模式
        GCSettings.LatencyMode = GCLatencyMode.SustainedLowLatency;
        
        // 禁用 GC 延迟模式（高性能场景）
        // GCSettings.LatencyMode = GCLatencyMode.NoGCRegion;
        
        CreateHostBuilder(args).Build().Run();
    }
}

// 强制垃圾回收（谨慎使用）
public class MemoryIntensiveService
{
    public void ProcessLargeData()
    {
        try
        {
            // 处理大数据
        }
        finally
        {
            // 完成后请求 GC
            GC.Collect(2, GCCollectionMode.Optimized);
        }
    }
}

// 弱引用
public class CacheService
{
    private readonly WeakReference<Dictionary<int, object>> _cache;

    public CacheService()
    {
        _cache = new WeakReference<Dictionary<int, object>>(
            new Dictionary<int, object>());
    }

    public object GetOrCreate(int key, Func<object> factory)
    {
        if (_cache.TryGetTarget(out var cache) && cache.TryGetValue(key, out var value))
        {
            return value;
        }

        var newValue = factory();
        if (_cache.TryGetTarget(out cache))
        {
            cache[key] = newValue;
        }
        return newValue;
    }
}
```

### 内存泄漏检测

```csharp
// 使用 MemoryDump 分析
// dotnet-dump collect -p <pid>
// dotnet-dump analyze

// 常见泄漏场景
public class LeakyService
{
    private readonly List<Action> _callbacks = new();

    // 泄漏：事件未注销
    public void Subscribe(Event aggregator)
    {
        aggregator.OnEvent += () => Console.WriteLine("Event");
    }

    // 修复：使用弱事件
    public void SubscribeSafe(Event aggregator)
    {
        WeakEventManager<EventArgs>.AddHandler(
            aggregator, "OnEvent", OnEventHandler);
    }
}
```

## 并行编程

### Task 优化

```csharp
// 异步并行
public async Task<List<OrderDto>> GetOrdersAsync(List<int> customerIds)
{
    var orders = await Task.WhenAll(
        customerIds.Select(id => _orderRepo.GetByCustomerIdAsync(id)));
    
    return orders.SelectMany(o => o).ToList();
}

// 限制并发数
public async Task ProcessItemsThrottled<T>(
    IEnumerable<T> items,
    Func<T, Task> processor,
    int maxConcurrency = 10)
{
    using var semaphore = new SemaphoreSlim(maxConcurrency);
    
    var tasks = items.Select(async item =>
    {
        await semaphore.WaitAsync();
        try
        {
            await processor(item);
        }
        finally
        {
            semaphore.Release();
        }
    });

    await Task.WhenAll(tasks);
}

// ValueTask 优化（避免分配）
public ValueTask<Customer> GetCustomerAsync(int id)
{
    if (_cache.TryGetValue(id, out var customer))
        return new ValueTask<Customer>(customer);
    
    return new ValueTask<Customer>(_cache.GetOrCreateAsync(id));
}
```

### Channel 并行

```csharp
public class BackgroundTaskQueue
{
    private readonly Channel<Func<CancellationToken, ValueTask>> _queue;

    public BackgroundTaskQueue()
    {
        _queue = Channel.CreateUnbounded<Func<CancellationToken, ValueTask>>(
            new UnboundedChannelOptions { SingleReader = true });
    }

    public async ValueTask QueueAsync(
        Func<CancellationToken, ValueTask> workItem)
    {
        await _queue.Writer.WriteAsync(workItem);
    }

    public async ValueTask DequeueAsync(
        CancellationToken cancellationToken)
    {
        await foreach (var workItem in _queue.Reader
            .ReadAllAsync(cancellationToken))
        {
            await workItem(cancellationToken);
        }
    }
}
```

## 数据库优化

### 索引优化

```csharp
// EF Core 索引配置
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        // 单列索引
        builder.HasIndex(o => o.CustomerId);

        // 复合索引
        builder.HasIndex(o => new { o.CustomerId, o.CreatedAt });

        // 唯一索引
        builder.HasIndex(o => o.OrderNumber).IsUnique();

// 覆盖索引（包含列）
        builder.HasIndex(o => o.Status)
            .HasFilter("Status = 'Pending'")
            .IncludeProperties(o => new { o.TotalAmount, o.CreatedAt });
    }
}

// SQL 优化提示
var orders = await _context.Orders
    .FromSqlRaw("SELECT * FROM Orders WITH (NOLOCK) WHERE CustomerId = {0}", customerId)
    .Include(o => o.Items)
    .ToListAsync();
```

### 查询优化

```csharp
// 分页优化
public async Task<PagedResult<Order>> GetOrdersAsync(int page, int pageSize)
{
    // 避免 OFFSET 大偏移量
    var lastId = (page - 1) * pageSize;
    
    return await _context.Orders
        .Where(o => o.Id > lastId)
        .OrderBy(o => o.Id)
        .Take(pageSize)
        .Select(o => new Order
        {
            Id = o.Id,
            CustomerId = o.CustomerId,
            // 只选择需要的列
        })
        .ToListAsync();
}

// 批量操作
public async Task BulkInsertAsync(IEnumerable<Order> orders)
{
    await _context.BulkInsertAsync(orders, options =>
    {
        options.BatchSize = 1000;
        options.InsertKeepIdentity = false;
    });
}

// 避免 N+1
var orders = await _context.Orders
    .Include(o => o.Customer)  // 预加载
    .Include(o => o.Items)
        .ThenInclude(i => i.Product)  // 多层预加载
    .Where(o => o.Status == OrderStatus.Pending)
    .ToListAsync();
```

## 缓存策略

### 多级缓存

```csharp
public class MultiLevelCache
{
    private readonly IMemoryCache _memoryCache;
    private readonly IDistributedCache _distributedCache;
    private readonly ICacheInvalidator _invalidator;

    public async Task<T?> GetOrCreateAsync<T>(
        string key,
        Func<Task<T>> factory,
        TimeSpan? memoryExpiration = null,
        TimeSpan? distributedExpiration = null)
    {
        // 1. 检查本地内存
        if (_memoryCache.TryGetValue(key, out T? value))
            return value;

        // 2. 检查分布式缓存
        var cached = await _distributedCache.GetStringAsync(key);
        if (cached != null)
        {
            value = JsonSerializer.Deserialize<T>(cached);
            _memoryCache.Set(key, value, memoryExpiration ?? TimeSpan.FromMinutes(5));
            return value;
        }

        // 3. 执行获取
        value = await factory();
        if (value != null)
        {
            var serialized = JsonSerializer.Serialize(value);
            await _distributedCache.SetStringAsync(key, serialized, 
                new DistributedCacheEntryOptions
                {
                    AbsoluteExpirationRelativeToNow = distributedExpiration
                });
            _memoryCache.Set(key, value, memoryExpiration ?? TimeSpan.FromMinutes(5));
        }

        return value;
    }
}
```

### 缓存失效策略

```csharp
// 写时失效
public async Task UpdateProductAsync(Product product)
{
    await _productRepo.UpdateAsync(product);
    
    // 失效缓存
    await _cache.RemoveAsync($"product:{product.Id}");
    await _cache.RemoveByPatternAsync("products:*");
}

// 延迟失效
public async Task<T> GetOrSetAsync<T>(string key, Func<Task<T>> factory)
{
    var value = await _cache.GetAsync<T>(key);
    if (value != null)
        return value;

    value = await factory();
    await _cache.SetAsync(key, value, TimeSpan.FromMinutes(30));
    
    // 安排延迟删除
    _scheduler.Schedule(() => _cache.RemoveAsync(key), 
        TimeSpan.FromMinutes(5));

    return value;
}
```

## BenchmarkDotNet

### 基准测试

```csharp
[SimpleJob(RuntimeMoniker.Net80)]
[SimpleJob(RuntimeMoniker.NetFramework48)]
[MemoryDiagnoser]
[RankColumn]
[HtmlReport]
public class StringComparisonBenchmark
{
    private string _string1 = "Hello World";
    private string _string2 = "hello world";

    [Benchmark(Baseline = true)]
    public bool StringEquals() =>
        _string1.Equals(_string2);

    [Benchmark]
    public bool StringEqualsIgnoreCase() =>
        _string1.Equals(_string2, StringComparison.OrdinalIgnoreCase);

    [Benchmark]
    public bool StringCompareOrdinalIgnoreCase() =>
        string.Compare(_string1, _string2, 
            StringComparison.OrdinalIgnoreCase) == 0;

    [Benchmark]
    public bool StringToLower() =>
        _string1.ToLower() == _string2.ToLower();

    [Benchmark]
    public bool SpanCompareTo() =>
        _string1.AsSpan().CompareTo(
            _string2.AsSpan(), StringComparison.OrdinalIgnoreCase) == 0;
}
```

### 运行基准测试

```bash
# 发布构建
dotnet build -c Release

# 运行基准测试
dotnet run --project .\BenchmarkDotNet\BenchmarkDotNet.csproj

# 只运行指定测试
dotnet run --filter "*StringEquals*"
```

### 结果解读

```
|              Method |      Mean |     Error |    StdDev |    Median |  Gen 0 | Allocated |
|-------------------- |----------:|----------:|----------:|----------:|-------:|----------:|
|        StringEquals |  89.34 ns |  1.234 ns |  1.154 ns |  89.05 ns | 0.0076 |      48 B |
| StringEqualsIgnoreCase | 102.45 ns |  1.892 ns |  1.771 ns | 102.18 ns | 0.0076 |      48 B |
| StringCompareOrdinalIgnoreCase |  56.78 ns |  0.923 ns |  0.864 ns |  56.62 ns | 0.0076 |      48 B |
```

## 响应时间优化

### 预热和预加载

```csharp
public class ApplicationWarmup : IHostedService
{
    private readonly IServiceProvider _services;

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        using var scope = _services.CreateScope();
        
        // 预加载常用数据
        var cache = scope.ServiceProvider.GetRequiredService<IMemoryCache>();
        
        await cache.GetOrCreateAsync("categories", 
            async entry =>
            {
                var repo = scope.ServiceProvider
                    .GetRequiredService<ICategoryRepository>();
                entry.SlidingExpiration = TimeSpan.FromHours(1);
                return await repo.GetAllAsync();
            });
    }
}
```

### 响应压缩

```csharp
// Program.cs
builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<GzipCompressionProvider>();
    options.Providers.Add<BrotliCompressionProvider>();
});

builder.Services.Configure<GzipCompressionProviderOptions>(options =>
{
    options.Level = CompressionLevel.Fastest;
});

app.UseResponseCompression();

// 减少响应大小
[ApiController]
public class ProductsController : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<IEnumerable<ProductSummaryDto>>> GetProducts()
    {
        // 返回摘要而非完整数据
        return Ok(_products.Select(p => new ProductSummaryDto
        {
            Id = p.Id,
            Name = p.Name
        }));
    }
}
```
