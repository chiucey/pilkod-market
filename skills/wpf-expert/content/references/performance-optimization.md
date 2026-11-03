# 性能优化指南

## 1. XAML 性能优化

### 虚拟化
```xml
<!-- 列表虚拟化 -->
<ListView VirtualizingStackPanel.IsVirtualizing="True"
          VirtualizingStackPanel.VirtualizationMode="Recycling"
          ScrollViewer.IsDeferredScrollingEnabled="True">
    <ListView.ItemsPanel>
        <ItemsPanelTemplate>
            <VirtualizingStackPanel />
        </ItemsPanelTemplate>
    </ListView.ItemsPanel>
</ListView>

<!-- 数据模板选择器延迟加载 -->
<DataTemplate x:Key="DeferredDataTemplate">
    <ContentControl Content="{Binding}"
                     ContentTemplate="{StaticResource HeavyTemplate}"
                     ContentTemplateSelector="{StaticResource TemplateSelector}"
                     ContentSource="Content"
                     Loaded="ContentControl_Loaded"/>
</DataTemplate>
```

### 资源字典优化
```xml
<!-- 使用 ResourceDictionary.Source 动态加载 -->
<ResourceDictionary>
    <ResourceDictionary.MergedDictionaries>
        <ResourceDictionary Source="Themes/Base.xaml"/>
        <ResourceDictionary Source="Themes/Controls.xaml"/>
        <ResourceDictionary Source="Themes/Icons.xaml"/>
    </ResourceDictionary.MergedDictionaries>
</ResourceDictionary>

<!-- 避免在资源字典中使用值转换器实例 -->
<ResourceDictionary xmlns:converters="clr-namespace:App.Converters">
    <converters:BoolToVisibilityConverter x:Key="BoolToVisibility"/>
</ResourceDictionary>
```

## 2. 绑定性能

```csharp
// 延迟绑定更新
public class DebounceBehavior : Behavior<TextBox>
{
    public static readonly DependencyProperty DelayProperty =
        DependencyProperty.Register(
            nameof(Delay),
            typeof(int),
            typeof(DebounceBehavior),
            new PropertyMetadata(300));

    public int Delay
    {
        get => (int)GetValue(DelayProperty);
        set => SetValue(DelayProperty, value);
    }

    private IDisposable _subscription;

    protected override void OnAttached()
    {
        base.OnAttached();
        var textChanged = Observable
            .FromEventPattern<TextChangedEventArgs>(
                h => AssociatedObject.TextChanged += h,
                h => AssociatedObject.TextChanged -= h)
            .Throttle(TimeSpan.FromMilliseconds(Delay))
            .ObserveOnDispatcher();

        _subscription = textChanged.Subscribe(_ => UpdateSource());
    }

    private void UpdateSource()
    {
        var binding = AssociatedObject.GetBindingExpression(TextBox.TextProperty);
        binding?.UpdateSource();
    }

    protected override void OnDetaching()
    {
        _subscription?.Dispose();
        base.OnDetaching();
    }
}
```

## 3. UI 线程优化

```csharp
public class DispatcherHelper
{
    // 异步调用到 UI 线程
    public static async Task<T> InvokeAsync<T>(Func<T> func)
    {
        if (Application.Current.Dispatcher.CheckAccess())
        {
            return func();
        }

        return await Application.Current.Dispatcher.InvokeAsync(func);
    }

    public static async Task InvokeAsync(Action action)
    {
        if (Application.Current.Dispatcher.CheckAccess())
        {
            action();
            return;
        }

        await Application.Current.Dispatcher.InvokeAsync(action);
    }

    // 批量更新
    public static void BeginBatchUpdate()
    {
        var window = Application.Current.MainWindow;
        if (window != null)
        {
            // 禁用渲染
            RenderCapability.Tier = 0;
        }
    }

    public static void EndBatchUpdate()
    {
        var window = Application.Current.MainWindow;
        if (window != null)
        {
            RenderCapability.Tier = 2;
            // 强制重绘
            window.InvalidateVisual();
        }
    }
}
```

## 4. 内存优化

```csharp
public class MemoryDiagnostics
{
    private long _baselineMemory;

    public void CaptureBaseline()
    {
        GC.Collect();
        GC.WaitForPendingFinalizers();
        GC.Collect();
        _baselineMemory = GC.GetTotalMemory(true);
    }

    public MemoryReport GetReport()
    {
        GC.Collect();
        GC.WaitForPendingFinalizers();
        GC.Collect();

        var currentMemory = GC.GetTotalMemory(false);

        return new MemoryReport
        {
            BaselineMemory = _baselineMemory,
            CurrentMemory = currentMemory,
            MemoryIncrease = currentMemory - _baselineMemory,
            Generation0Collections = GC.CollectionCount(0),
            Generation1Collections = GC.CollectionCount(1),
            Generation2Collections = GC.CollectionCount(2),
            TotalAvailableMemory = GC.GetGCMemoryInfo().TotalAvailableMemoryBytes
        };
    }

    public bool HasMemoryLeak()
    {
        var report = GetReport();
        // 检测内存增长超过 50MB
        return report.MemoryIncrease > 50 * 1024 * 1024;
    }
}

public class WeakEventManager<TEventSource, TEventArgs>
    where TEventArgs : EventArgs
{
    private readonly List<WeakReference> _handlers = new();
    private readonly object _lock = new();

    public void AddHandler(EventHandler<TEventArgs> handler)
    {
        lock (_lock)
        {
            _handlers.Add(new WeakReference(handler));
        }
    }

    public void RemoveHandler(EventHandler<TEventArgs> handler)
    {
        lock (_lock)
        {
            _handlers.RemoveAll(wr =>
                !wr.IsAlive || ReferenceEquals(wr.Target, handler));
        }
    }

    public void Raise(object sender, TEventArgs args)
    {
        List<WeakReference> toRemove = new();

        lock (_lock)
        {
            foreach (var weakRef in _handlers)
            {
                if (weakRef.IsAlive)
                {
                    ((EventHandler<TEventArgs>)weakRef.Target)(sender, args);
                }
                else
                {
                    toRemove.Add(weakRef);
                }
            }

            foreach (var wr in toRemove)
            {
                _handlers.Remove(wr);
            }
        }
    }
}
```

## 5. 数据库查询优化

```csharp
public class QueryOptimizer
{
    // 分页查询
    public async Task<PagedResult<T>> GetPagedAsync<T>(
        IQueryable<T> query,
        int page,
        int pageSize)
    {
        var totalCount = await query.CountAsync();

        var items = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync();

        return new PagedResult<T>
        {
            Items = items,
            Page = page,
            PageSize = pageSize,
            TotalCount = totalCount,
            TotalPages = (int)Math.Ceiling(totalCount / (double)pageSize)
        };
    }

    // 批量查询优化
    public async Task<List<T>> BatchQueryAsync<T>(
        IEnumerable<int> ids,
        Func<int[], Task<List<T>>> batchFunc,
        int batchSize = 100)
    {
        var results = new List<T>();
        var batches = ids.Chunk(batchSize);

        foreach (var batch in batches)
        {
            var batchResults = await batchFunc(batch.ToArray());
            results.AddRange(batchResults);
        }

        return results;
    }

    // 查询超时配置
    public static void ConfigureQueryTimeout(
        DbContext context,
        int seconds = 30)
    {
        context.Database
            .SqlQuery<int>($"SET LOCK_TIMEOUT {seconds * 1000}");

        context.Database
            .SqlQuery<int>($"SET QUERY_GOVERNOR_COST_LIMIT {seconds}");
    }
}
```

## 6. 启动性能优化

```xml
<!-- App.xaml 启动优化 -->
<Application Startup="Application_Startup">
    <Application.Resources>
        <ResourceDictionary>
            <!-- 延迟加载非关键资源 -->
        </ResourceDictionary>
    </Application.Resources>
</Application>
```

```csharp
public partial class App : Application
{
    private readonly Stopwatch _startupTimer = new();

    private async void Application_Startup(object sender, StartupEventArgs e)
    {
        _startupTimer.Start();

        // 预热核心组件
        await WarmupAsync();

        // 显示启动窗口
        var splash = new SplashScreen("splash.png");
        splash.Show(true);

        await InitializeServicesAsync();

        // 创建主窗口
        var mainWindow = new MainWindow();
        MainWindow = mainWindow;

        // 延迟加载模块
        _ = Task.Run(() => LoadModulesAsync());

        mainWindow.Show();
        splash.Close(TimeSpan.Zero);

        _startupTimer.Stop();
        Log.Info($"Application started in {_startupTimer.ElapsedMilliseconds}ms");
    }

    private async Task WarmupAsync()
    {
        // 预热 JIT
        var types = new[]
        {
            typeof(MainViewModel),
            typeof(ViewModelBase<>),
            typeof(RelayCommand)
        };

        foreach (var type in types)
        {
            _ = RuntimeHelpers.GetUninitializedObject(type);
        }

        await Task.CompletedTask;
    }
}
```

## 7. 性能监控

```csharp
public class PerformanceMonitor
{
    private readonly Dictionary<string, PerformanceCounter> _counters;
    private readonly ILogService _log;

    public PerformanceMonitor(ILogService log)
    {
        _log = log;
        _counters = new Dictionary<string, PerformanceCounter>();

        InitializeCounters();
    }

    private void InitializeCounters()
    {
        if (!PerformanceCounterCategory.Exists("WPF Application"))
        {
            CounterCreationDataCollection counters = new();
            counters.Add(new CounterCreationData(
                "UI Response Time",
                "Average UI response time in ms",
                PerformanceCounterType.AverageTimer));

            CounterCreationData[] arr = new CounterCreationData[counters.Count];
            counters.CopyTo(arr, 0);
            PerformanceCounterCategory.Create(
                "WPF Application",
                "WPF Application Performance",
                arr);
        }
    }

    public IDisposable Measure(string operationName)
    {
        return new PerformanceGuard(operationName, this, _log);
    }

    private class PerformanceGuard : IDisposable
    {
        private readonly string _operationName;
        private readonly PerformanceMonitor _monitor;
        private readonly Stopwatch _stopwatch;

        public PerformanceGuard(
            string operationName,
            PerformanceMonitor monitor,
            ILogService log)
        {
            _operationName = operationName;
            _monitor = monitor;
            _stopwatch = Stopwatch.StartNew();
        }

        public void Dispose()
        {
            _stopwatch.Stop();
            var elapsed = _stopwatch.ElapsedMilliseconds;

            if (elapsed > 100) // 慢操作告警
            {
                _monitor._log.Warning(
                    $"Slow operation: {_operationName} took {elapsed}ms");
            }
        }
    }
}
```
