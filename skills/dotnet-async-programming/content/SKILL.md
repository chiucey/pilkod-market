---
name: dotnet-async-programming
description: 掌握 .NET 异步编程技能。当用户要求进行异步编程、async/await、Task 并行、取消令牌、通道通信、或优化异步性能时使用。
---

# 异步编程技能

## 核心技能清单

| 技能项 | 熟练度 | 说明 |
|-------|-------|------|
| async/await | ⭐⭐⭐⭐⭐ | 异步语法基础 |
| Task 并行 | ⭐⭐⭐⭐⭐ | WhenAll、WhenAny |
| CancellationToken | ⭐⭐⭐⭐⭐ | 取消控制 |
| Channel | ⭐⭐⭐⭐⭐ | 生产者/消费者 |
| ValueTask | ⭐⭐⭐⭐ | 避免分配 |
| 异常处理 | ⭐⭐⭐⭐⭐ | AggregateException |

## async/await 基础

### 基础模式

```csharp
// 异步方法签名
public async Task<Result> ProcessOrderAsync(int orderId, CancellationToken ct)
{
    // 异步等待
    var order = await _orderRepo.GetByIdAsync(orderId, ct);
    
    // 同步转异步
    await Task.Run(() => ComputeExpensiveValue());
    
    // 返回结果
    return Result.Success(order);
}

// 无返回值的异步
public async Task SendEmailAsync(string to, string subject)
{
    await _emailService.SendAsync(to, subject);
    _logger.LogInformation("Email sent to {To}", to);
}

// 异步属性（C# 8.0+）
public class Product
{
    public string Name { get; set; }
    
    public async Task<string> GetDescriptionAsync()
    {
        return await _productService.GetDescriptionAsync(Name);
    }
}
```

### 避免的常见错误

```csharp
// ❌ 错误：使用 .Result 阻塞
public Order GetOrder(int id)
{
    return _orderRepo.GetByIdAsync(id).Result;  // 死锁风险！
}

// ✅ 正确：使用 await
public async Task<Order> GetOrderAsync(int id)
{
    return await _orderRepo.GetByIdAsync(id);
}

// ❌ 错误：返回 void（无法等待）
public void ProcessAsync()
{
    await _service.ProcessAsync();  // 不好的做法
}

// ✅ 正确：返回 Task
public async Task ProcessAsync()
{
    await _service.ProcessAsync();
}

// ❌ 错误：在构造或初始化器中 await
public class Service
{
    private readonly Product _product = await GetProductAsync();  // 编译错误
}

// ✅ 正确：使用异步初始化
public class Service
{
    private Product? _product;
    
    public async Task InitializeAsync()
    {
        _product = await GetProductAsync();
    }
}
```

## Task 并行

### WhenAll & WhenAny

```csharp
// 并行执行多个任务
public async Task<DashboardData> GetDashboardAsync(int userId)
{
    var userTask = _userService.GetUserAsync(userId);
    var ordersTask = _orderService.GetRecentOrdersAsync(userId);
    var statsTask = _statsService.GetUserStatsAsync(userId);

    await Task.WhenAll(userTask, ordersTask, statsTask);

    return new DashboardData
    {
        User = userTask.Result,
        Orders = ordersTask.Result,
        Stats = statsTask.Result
    };
}

// 等待第一个完成
public async Task<SearchResult> SearchMultiSourceAsync(string query)
{
    var sources = new[]
    {
        SearchWebAsync(query),
        SearchImagesAsync(query),
        SearchVideosAsync(query)
    };

    while (sources.Any())
    {
        var completed = await Task.WhenAny(sources);
        var result = await completed;
        
        if (result.HasResults)
            return result;
        
        sources = sources.Where(s => s != completed).ToArray();
    }

    return SearchResult.Empty;
}

// 全部完成或超时
public async Task<T[]> ExecuteWithTimeoutAsync<T>(
    IEnumerable<Task<T>> tasks,
    TimeSpan timeout)
{
    var timeoutTask = Task.Delay(timeout);
    var allTasks = Task.WhenAll(tasks);
    
    var completed = await Task.WhenAny(allTasks, timeoutTask);
    
    if (completed == timeoutTask)
        throw new TimeoutException("Operation timed out");
    
    return await allTasks;
}
```

### 并行 LINQ

```csharp
// PLINQ - 并行 LINQ
public async Task<List<AnalysisResult>> AnalyzeAllOrdersAsync(
    IEnumerable<Order> orders)
{
    return await Task.Run(() =>
        orders
            .AsParallel()
            .WithDegreeOfParallelism(4)
            .Select(o => AnalyzeOrder(o))
            .ToList());
}

// 分区处理
public async Task ProcessBatchesAsync<T>(
    IEnumerable<T> items,
    Func<T, Task> processor,
    int batchSize = 100)
{
    var batches = items.Chunk(batchSize);
    
    await Parallel.ForEachAsync(batches, 
        new ParallelOptions { MaxDegreeOfParallelism = 4 },
        async (batch, ct) =>
        {
            await Task.WhenAll(batch.Select(item => processor(item)));
        });
}

// 并行聚合
public async Task<Statistics> CalculateStatisticsAsync(
    IEnumerable<double> values)
{
    var valuesArray = values.ToArray();
    
    return await Task.Run(() =>
    {
        var mean = valuesArray.AsParallel().Average();
        var stdDev = Math.Sqrt(
            valuesArray.AsParallel()
                .Select(v => Math.Pow(v - mean, 2))
                .Average());
        
        return new Statistics { Mean = mean, StdDev = stdDev };
    });
}
```

## CancellationToken

### 取消模式

```csharp
// 接收取消令牌
public async Task<IEnumerable<Order>> GetOrdersAsync(
    int customerId,
    CancellationToken cancellationToken = default)
{
    // 检查取消请求
    cancellationToken.ThrowIfCancellationRequested();
    
    var orders = await _context.Orders
        .Where(o => o.CustomerId == customerId)
        .ToListAsync(cancellationToken);  // 传递给 EF Core
    
    cancellationToken.ThrowIfCancellationRequested();
    
    return orders;
}

// 链接取消令牌
public async Task DoWorkAsync(CancellationToken externalToken)
{
    using var cts = CancellationTokenSource.CreateLinkedTokenSource(externalToken);
    cts.CancelAfter(TimeSpan.FromSeconds(30));  // 30秒超时
    
    try
    {
        await LongRunningOperationAsync(cts.Token);
    }
    catch (OperationCanceledException) when (externalToken.IsCancellationRequested)
    {
        Console.WriteLine("External cancellation requested");
    }
    catch (OperationCanceledException) when (cts.Token.IsCancellationRequested)
    {
        Console.WriteLine("Timeout cancellation");
    }
}

// 禁止取消传播
public async Task DoWorkSafelyAsync(CancellationToken cancellationToken)
{
    try
    {
        await ProcessAsync(CancellationToken.None);  // 忽略取消
    }
    catch when (cancellationToken.IsCancellationRequested)
    {
        // 处理取消
    }
}
```

### 后台服务取消

```csharp
public class BackgroundProcessor : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Background processor starting");
        
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ProcessQueueAsync(stoppingToken);
                await Task.Delay(TimeSpan.FromSeconds(1), stoppingToken);
            }
            catch (OperationCanceledException)
            {
                _logger.LogInformation("Background processor stopping");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in background processor");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Graceful shutdown initiated");
        await base.StopAsync(cancellationToken);
        _logger.LogInformation("Background processor stopped");
    }
}
```

## Channel

### 生产者/消费者

```csharp
// 创建通道
public class OrderQueue
{
    private readonly Channel<Order> _channel;

    public OrderQueue()
    {
        _channel = Channel.CreateUnbounded<Order>(
            new UnboundedChannelOptions
            {
                SingleReader = true,  // 单消费者
                SingleWriter = false  // 多生产者
            });
    }

    public ValueTask EnqueueAsync(Order order)
    {
        return _channel.Writer.WriteAsync(order);
    }

    public IAsyncEnumerable<Order> DequeueAllAsync(
        CancellationToken cancellationToken)
    {
        return _channel.Reader.ReadAllAsync(cancellationToken);
    }
}

// 消费者
public class OrderProcessor
{
    private readonly OrderQueue _queue;

    public async Task ProcessOrdersAsync(CancellationToken cancellationToken)
    {
        await foreach (var order in _queue.DequeueAllAsync(cancellationToken))
        {
            try
            {
                await ProcessOrderAsync(order);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to process order {OrderId}", order.Id);
            }
        }
    }
}

// 生产者
public class OrderController : ControllerBase
{
    private readonly OrderQueue _queue;

    [HttpPost]
    public async Task<IActionResult> CreateOrder(Order order)
    {
        await _queue.EnqueueAsync(order);
        return Accepted();
    }
}
```

### 背压控制

```csharp
// 有界通道（背压）
public class BoundedOrderQueue
{
    private readonly Channel<Order> _channel;

    public BoundedOrderQueue(int capacity)
    {
        _channel = Channel.CreateBounded<Order>(
            new BoundedChannelOptions(capacity)
            {
                FullMode = BoundedChannelFullMode.Wait  // 满时等待
            });
    }

    // 尝试写入（满时立即返回）
    public bool TryEnqueue(Order order)
    {
        return _channel.Writer.TryWrite(order);
    }

    // 异步等待写入（满时等待空间）
    public async Task<bool> WaitToEnqueueAsync(Order order, 
        CancellationToken cancellationToken)
    {
        return await _channel.Writer.WaitToWriteAsync(cancellationToken);
    }
}
```

## ValueTask

### 何时使用

```csharp
// ✅ 适合 ValueTask 的场景：同步快速完成
public ValueTask<bool> ExistsAsync(int id)
{
    return _cache.Contains(id) 
        ? new ValueTask<bool>(true)
        : new ValueTask<bool>(_repo.ExistsAsync(id));
}

// ❌ 不适合 ValueTask 的场景
public ValueTask<Customer> GetCustomerAsync(int id)  // 总是异步
{
    return _repo.GetCustomerAsync(id);
}

// ✅ 总是异步时使用 Task
public Task<Customer> GetCustomerAsync(int id)
{
    return _repo.GetCustomerAsync(id);
}
```

### IValueTaskSource

```csharp
public class AsyncLazy<T>
{
    private readonly Func<T> _factory;
    private readonly Func<Task<T>> _taskFactory;
    private ConfiguredValueTaskAwaitable<T>.ConfiguredValueTaskAwaiter _awaiter;
    private bool _isValueCreated;
    private T _value = default!;
    private Exception? _exception;

    public AsyncLazy(Func<T> factory)
    {
        _factory = factory;
        _taskFactory = () => Task.Run(factory);
    }

    public T Value => _isValueCreated ? _value : _factory();
}
```

## 异常处理

### 异常聚合

```csharp
// 收集多个任务的异常
public async Task ProcessAllAsync(IEnumerable<Order> orders)
{
    var exceptions = new List<Exception>();
    var tasks = orders.Select(async order =>
    {
        try
        {
            await ProcessOrderAsync(order);
        }
        catch (Exception ex)
        {
            exceptions.Add(new InvalidOperationException(
                $"Failed to process order {order.Id}", ex));
        }
    });

    await Task.WhenAll(tasks);

    if (exceptions.Any())
        throw new AggregateException("Some orders failed", exceptions);
}

// 继续处理错误任务
public async Task<IDictionary<Order, Exception>> 
    ProcessWithErrorsAsync(IEnumerable<Order> orders)
{
    var results = new ConcurrentDictionary<Order, Exception>();
    var tasks = orders.Select(async order =>
    {
        try
        {
            await ProcessOrderAsync(order);
        }
        catch (Exception ex)
        {
            results.TryAdd(order, ex);
        }
    });

    await Task.WhenAll(tasks);
    return results;
}
```

### 重试模式

```csharp
public static class RetryHelper
{
    public static async Task<T> RetryAsync<T>(
        Func<Task<T>> operation,
        int maxRetries = 3,
        TimeSpan? delay = null)
    {
        delay ??= TimeSpan.FromSeconds(1);
        
        for (int i = 0; i <= maxRetries; i++)
        {
            try
            {
                return await operation();
            }
            catch (Exception ex) when (i < maxRetries)
            {
                _logger.LogWarning(ex, "Retry {Retry} of {Max}", i + 1, maxRetries);
                await Task.Delay(delay.Value * (i + 1));
            }
        }
        
        return await operation(); // 最后一次不捕获
    }
}

// Polly 集成
public async Task<T> ExecuteWithPolicyAsync<T>(
    Func<Task<T>> operation,
    ResiliencePipeline<T> pipeline)
{
    return await pipeline.ExecuteAsync(operation);
}

// 配置重试策略
var retryPolicy = Policy
    .Handle<HttpRequestException>()
    .OrResult(r => !r.IsSuccessStatusCode)
    .WaitAndRetryAsync(
        3,
        retryAttempt => TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));
```

### 异步 using

```csharp
// 异步资源释放
public class AsyncDisposableService : IAsyncDisposable
{
    private readonly HttpClient _httpClient;

    public async ValueTask DisposeAsync()
    {
        await _httpClient.DisposeAsync();
    }
}

// await using
public async Task ProcessAsync()
{
    await using var service = new AsyncDisposableService();
    await service.DoWorkAsync();
}
```
