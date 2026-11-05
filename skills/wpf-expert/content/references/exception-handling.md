# 异常处理最佳实践

## 1. 异常层次结构

```csharp
// 自定义异常层次
public abstract class ApplicationException : Exception
{
    public string Code { get; }
    public DateTime Timestamp { get; }

    protected ApplicationException(string code, string message)
        : base(message)
    {
        Code = code;
        Timestamp = DateTime.UtcNow;
    }
}

// 业务异常
public class BusinessException : ApplicationException
{
    public IDictionary<string, string[]> Details { get; }

    public BusinessException(
        string code,
        string message,
        IDictionary<string, string[]> details = null)
        : base(code, message)
    {
        Details = details;
    }
}

// 验证异常
public class ValidationException : ApplicationException
{
    public IEnumerable<ValidationError> Errors { get; }

    public ValidationException(
        IEnumerable<ValidationError> errors)
        : base("VALIDATION_ERROR", "验证失败")
    {
        Errors = errors;
    }
}

// 数据访问异常
public class DataAccessException : ApplicationException
{
    public string Sql { get; }
    public IDictionary<string, object> Parameters { get; }

    public DataAccessException(
        string message,
        Exception inner,
        string sql = null)
        : base("DATA_ACCESS_ERROR", message, inner)
    {
        Sql = sql;
    }
}

// 网络异常
public class NetworkException : ApplicationException
{
    public string Url { get; }
    public int? StatusCode { get; }
    public bool IsTimeout { get; }

    public NetworkException(
        string message,
        Exception inner,
        string url = null,
        int? statusCode = null,
        bool isTimeout = false)
        : base("NETWORK_ERROR", message, inner)
    {
        Url = url;
        StatusCode = statusCode;
        IsTimeout = isTimeout;
    }
}
```

## 2. 全局异常处理

### WPF App.xaml.cs
```csharp
public partial class App : Application
{
    private readonly IExceptionHandler _exceptionHandler;
    private readonly ILogService _logService;

    public App()
    {
        _exceptionHandler = new GlobalExceptionHandler(_logService);
    }

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        // UI 线程异常
        Current.DispatcherUnhandledException += OnDispatcherUnhandledException;

        // 非 UI 线程异常
        AppDomain.CurrentDomain.UnhandledException += OnUnhandledException;

        // Task 异常
        TaskScheduler.UnobservedTaskException += OnUnobservedTaskException;
    }

    private void OnDispatcherUnhandledException(
        object sender,
        DispatcherUnhandledExceptionEventArgs e)
    {
        _exceptionHandler.HandleUIException(
            e.Exception,
            "Dispatcher");

        e.Handled = true;
        ShowErrorDialog(e.Exception);
    }

    private void OnUnhandledException(
        object sender,
        UnhandledExceptionEventArgs e)
    {
        var exception = e.ExceptionObject as Exception;
        _exceptionHandler.HandleCriticalException(exception, e.IsTerminating);
    }

    private void OnUnobservedTaskException(
        object sender,
        UnobservedTaskExceptionEventArgs e)
    {
        _exceptionHandler.HandleTaskException(e.Exception);
        e.SetObserved();
    }
}
```

## 3. Polly 弹性策略

```csharp
public class ResiliencePolicies
{
    // 重试策略
    public static AsyncRetryPolicy<T> GetRetryPolicy<T>(
        int retryCount = 3,
        int delaySeconds = 2)
    {
        return Policy<T>
            .Handle<HttpRequestException>()
            .Or<NetworkException>(ex => !ex.IsTimeout)
            .WaitAndRetryAsync(
                retryCount,
                retryAttempt => TimeSpan.FromSeconds(
                    Math.Pow(delaySeconds, retryAttempt)),
                onRetry: (exception, timeSpan, retryCount, context) =>
                {
                    Log.Warning(
                        $"Retry {retryCount} after {timeSpan}s",
                        exception);
                });
    }

    // 熔断策略
    public static AsyncCircuitBreakerPolicy<T> GetCircuitBreakerPolicy<T>(
        int exceptionsAllowedBeforeBreaking = 5,
        int durationOfBreakSeconds = 60)
    {
        return Policy<T>
            .Handle<HttpRequestException>()
            .CircuitBreakerAsync(
                exceptionsAllowedBeforeBreaking,
                TimeSpan.FromSeconds(durationOfBreakSeconds),
                onBreak: (exception, duration) =>
                {
                    Log.Warning(
                        $"Circuit broken for {duration}",
                        exception);
                },
                onReset: () => Log.Info("Circuit reset"),
                onHalfOpen: () => Log.Info("Circuit half-open"));
    }

    // 超时策略
    public static Policy<T> GetTimeoutPolicy<T>(
        int timeoutSeconds = 30)
    {
        return Policy<T>
            .TimeoutAsync(
                TimeSpan.FromSeconds(timeoutSeconds),
                TimeoutStrategy.Optimistic);
    }

    // 降级策略
    public static AsyncPolicy<T> GetFallbackPolicy<T>(
        Func<T> fallbackValue)
    {
        return Policy<T>
            .Handle<Exception>()
            .FallbackAsync(
                fallbackValue(),
                onFallbackAsync: (exception) =>
                {
                    Log.Error($"Fallback triggered", exception);
                    return Task.CompletedTask;
                });
    }
}
```

## 4. 异常日志记录

```csharp
public interface IExceptionLogger
{
    Task LogExceptionAsync(Exception exception, ExceptionContext context);
}

public class ExceptionLogger : IExceptionLogger
{
    private readonly ILogService _logService;
    private readonly IExceptionFilter _filter;

    public async Task LogExceptionAsync(
        Exception exception,
        ExceptionContext context)
    {
        if (_filter.ShouldIgnore(exception))
            return;

        var logEntry = new ExceptionLogEntry
        {
            Id = Guid.NewGuid(),
            Type = exception.GetType().Name,
            Message = exception.Message,
            StackTrace = exception.StackTrace,
            Source = context.Source,
            Timestamp = DateTime.UtcNow,
            MachineName = Environment.MachineName,
            UserId = context.UserId,
            RequestId = context.RequestId,
            AdditionalData = context.AdditionalData
        };

        // 内部异常
        if (exception.InnerException != null)
        {
            logEntry.InnerException = new InnerExceptionInfo
            {
                Type = exception.InnerException.GetType().Name,
                Message = exception.InnerException.Message,
                StackTrace = exception.InnerException.StackTrace
            };
        }

        await _logService.LogAsync(logEntry);
    }
}
```

## 5. 统一响应结果

```csharp
public class Result<T>
{
    public bool IsSuccess { get; private set; }
    public bool IsFailure => !IsSuccess;
    public T Value { get; private set; }
    public string Code { get; private set; }
    public string Message { get; private set; }
    public IDictionary<string, string[]> Errors { get; private set; }

    public static Result<T> Success(T value)
    {
        return new Result<T>
        {
            IsSuccess = true,
            Value = value
        };
    }

    public static Result<T> Failure(string code, string message)
    {
        return new Result<T>
        {
            IsSuccess = false,
            Code = code,
            Message = message
        };
    }

    public static Result<T> ValidationFailure(
        IDictionary<string, string[]> errors)
    {
        return new Result<T>
        {
            IsSuccess = false,
            Code = "VALIDATION_ERROR",
            Errors = errors
        };
    }
}
```

## 6. 异常处理策略表

| 场景 | 推荐策略 | 实现方式 |
|------|----------|----------|
| 网络请求失败 | 重试 + 熔断 | Polly |
| 数据库连接超时 | 重试 + 超时 | Polly + 异步 |
| 并发冲突 | 乐观锁重试 | 版本号控制 |
| 资源不存在 | 快速失败 | 空值检查 |
| 服务不可用 | 降级返回 | 缓存备选 |
| 超时操作 | 超时策略 | CancellationToken |
| 未知异常 | 记录 + 告警 | 日志系统 |
