# MVVM 架构模式

## 1. ViewModel 基类

```csharp
public abstract class ViewModelBase : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler PropertyChanged;

    protected virtual void OnPropertyChanged(
        [CallerMemberName] string propertyName = null)
    {
        PropertyChanged?.Invoke(
            this,
            new PropertyChangedEventArgs(propertyName));
    }

    protected bool SetProperty<T>(
        ref T field,
        T value,
        [CallerMemberName] string propertyName = null)
    {
        if (EqualityComparer<T>.Default.Equals(field, value))
            return false;

        field = value;
        OnPropertyChanged(propertyName);
        return true;
    }
}

public abstract class ViewModelBase<T> : ViewModelBase
{
    protected T _model;

    public T Model
    {
        get => _model;
        set => SetProperty(ref _model, value);
    }
}
```

## 2. RelayCommand 实现

```csharp
public class RelayCommand : ICommand
{
    private readonly Action<object> _execute;
    private readonly Predicate<object> _canExecute;

    public RelayCommand(
        Action<object> execute,
        Predicate<object> canExecute = null)
    {
        _execute = execute ?? throw new ArgumentNullException(nameof(execute));
        _canExecute = canExecute;
    }

    public event EventHandler CanExecuteChanged
    {
        add => CommandManager.RequerySuggested += value;
        remove => CommandManager.RequerySuggested -= value;
    }

    public bool CanExecute(object parameter)
    {
        return _canExecute?.Invoke(parameter) ?? true;
    }

    public void Execute(object parameter)
    {
        _execute(parameter);
    }

    public void RaiseCanExecuteChanged()
    {
        CommandManager.InvalidateRequerySuggested();
    }
}

public class AsyncRelayCommand : ICommand
{
    private readonly Func<object, Task> _execute;
    private readonly Predicate<object> _canExecute;
    private bool _isExecuting;

    public AsyncRelayCommand(
        Func<object, Task> execute,
        Predicate<object> canExecute = null)
    {
        _execute = execute ?? throw new ArgumentNullException(nameof(execute));
        _canExecute = canExecute;
    }

    public event EventHandler CanExecuteChanged
    {
        add => CommandManager.RequerySuggested += value;
        remove => CommandManager.RequerySuggested -= value;
    }

    public bool CanExecute(object parameter)
    {
        return !_isExecuting && (_canExecute?.Invoke(parameter) ?? true);
    }

    public async void Execute(object parameter)
    {
        if (!CanExecute(parameter))
            return;

        try
        {
            _isExecuting = true;
            RaiseCanExecuteChanged();
            await _execute(parameter);
        }
        finally
        {
            _isExecuting = false;
            RaiseCanExecuteChanged();
        }
    }

    public void RaiseCanExecuteChanged()
    {
        CommandManager.InvalidateRequerySuggested();
    }
}
```

## 3. 依赖注入配置

```csharp
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddApplicationServices(
        this IServiceCollection services)
    {
        // 注册服务
        services.AddSingleton<IUserService, UserService>();
        services.AddScoped<IOrderService, OrderService>();
        services.AddTransient<IProductRepository, ProductRepository>();

        // 注册 ViewModel
        services.AddTransient<MainViewModel>();
        services.AddTransient<UserListViewModel>();
        services.AddTransient<UserDetailViewModel>();

        // 注册消息总线
        services.AddSingleton<IMessenger, Messenger>();
        services.AddSingleton<IEventAggregator, EventAggregator>();

        return services;
    }
}
```

## 4. 消息总线

```csharp
// 消息基类
public abstract class Message
{
    public DateTime Timestamp { get; } = DateTime.UtcNow;
    public string SenderId { get; set; }
}

// 示例消息
public class UserSelectedMessage : Message
{
    public int UserId { get; }
    public User User { get; }

    public UserSelectedMessage(int userId, User user)
    {
        UserId = userId;
        User = user;
    }
}

public class NavigationMessage : Message
{
    public Type ViewModelType { get; }
    public IDictionary<string, object> Parameters { get; }

    public NavigationMessage(Type viewModelType,
        IDictionary<string, object> parameters = null)
    {
        ViewModelType = viewModelType;
        Parameters = parameters;
    }
}

// Messenger 实现
public interface IMessenger
{
    void Register<TMessage>(
        object recipient,
        Action<TMessage> action)
        where TMessage : Message;

    void Unregister<TMessage>(object recipient)
        where TMessage : Message;

    void Send<TMessage>(TMessage message)
        where TMessage : Message;

    void UnregisterAll(object recipient);
}
```

## 5. Dialog Service

```csharp
public interface IDialogService
{
    Task<bool> ShowConfirmationAsync(
        string title,
        string message);

    Task ShowErrorAsync(string message);

    Task<string> ShowInputAsync(
        string title,
        string message,
        string defaultValue = null);

    Task<T> ShowDialogAsync<T>(object viewModel)
        where T : class;
}

public class DialogService : IDialogService
{
    public async Task<bool> ShowConfirmationAsync(
        string title,
        string message)
    {
        var result = MessageBox.Show(
            message,
            title,
            MessageBoxButton.YesNo,
            MessageBoxImage.Question);

        return result == MessageBoxResult.Yes;
    }

    public async Task ShowErrorAsync(string message)
    {
        MessageBox.Show(
            message,
            "错误",
            MessageBoxButton.OK,
            MessageBoxImage.Error);
    }

    public async Task<string> ShowInputAsync(
        string title,
        string message,
        string defaultValue = null)
    {
        // 实现输入对话框
        throw new NotImplementedException();
    }

    public async Task<T> ShowDialogAsync<T>(object viewModel)
        where T : class
    {
        // 实现通用对话框
        throw new NotImplementedException();
    }
}
```

## 6. ViewModel 生命周期

```csharp
public interface IViewModelLifeCycle
{
    Task InitializeAsync(IDictionary<string, object> parameters);
    Task LoadedAsync();
    Task UnloadedAsync();
    Task ClosingAsync();
}

public abstract class ViewModelLifeCycleBase : ViewModelBase, IViewModelLifeCycle
{
    public virtual Task InitializeAsync(
        IDictionary<string, object> parameters)
    {
        return Task.CompletedTask;
    }

    public virtual Task LoadedAsync()
    {
        return Task.CompletedTask;
    }

    public virtual Task UnloadedAsync()
    {
        return Task.CompletedTask;
    }

    public virtual Task ClosingAsync()
    {
        return Task.CompletedTask;
    }
}
```

## 7. 完整示例

```csharp
public class UserListViewModel : ViewModelLifeCycleBase
{
    private readonly IUserService _userService;
    private readonly IMessenger _messenger;
    private readonly IDialogService _dialogService;

    private ObservableCollection<UserViewModel> _users;
    private UserViewModel _selectedUser;
    private bool _isLoading;
    private string _searchText;

    public UserListViewModel(
        IUserService userService,
        IMessenger messenger,
        IDialogService dialogService)
    {
        _userService = userService;
        _messenger = messenger;
        _dialogService = dialogService;

        Users = new ObservableCollection<UserViewModel>();
        LoadUsersCommand = new AsyncRelayCommand(LoadUsersAsync);
        DeleteUserCommand = new AsyncRelayCommand(DeleteUserAsync, _ => SelectedUser != null);
        AddUserCommand = new RelayCommand(_ => AddUser());
        RefreshCommand = new AsyncRelayCommand(_ => LoadUsersAsync());

        // 监听消息
        _messenger.Register<UserCreatedMessage>(this, OnUserCreated);
    }

    public ObservableCollection<UserViewModel> Users
    {
        get => _users;
        set => SetProperty(ref _users, value);
    }

    public UserViewModel SelectedUser
    {
        get => _selectedUser;
        set
        {
            if (SetProperty(ref _selectedUser, value))
            {
                _messenger.Send(new UserSelectedMessage(value?.Id, value?.Model));
            }
        }
    }

    public bool IsLoading
    {
        get => _isLoading;
        set => SetProperty(ref _isLoading, value);
    }

    public string SearchText
    {
        get => _searchText;
        set
        {
            if (SetProperty(ref _searchText, value))
            {
                FilterUsers();
            }
        }
    }

    public ICommand LoadUsersCommand { get; }
    public ICommand DeleteUserCommand { get; }
    public ICommand AddUserCommand { get; }
    public ICommand RefreshCommand { get; }

    public override async Task InitializeAsync(
        IDictionary<string, object> parameters)
    {
        await LoadUsersAsync();
    }

    private async Task LoadUsersAsync(object parameter = null)
    {
        try
        {
            IsLoading = true;
            var users = await _userService.GetAllUsersAsync();

            Users.Clear();
            foreach (var user in users)
            {
                Users.Add(new UserViewModel(user));
            }
        }
        catch (Exception ex)
        {
            await _dialogService.ShowErrorAsync($"加载失败: {ex.Message}");
        }
        finally
        {
            IsLoading = false;
        }
    }

    private async Task DeleteUserAsync(object parameter = null)
    {
        if (SelectedUser == null) return;

        var confirmed = await _dialogService.ShowConfirmationAsync(
            "确认删除",
            $"确定要删除用户 {SelectedUser.Name} 吗？");

        if (confirmed)
        {
            await _userService.DeleteUserAsync(SelectedUser.Id);
            Users.Remove(SelectedUser);
        }
    }

    private void AddUser()
    {
        _messenger.Send(new NavigationMessage(typeof(UserDetailViewModel)));
    }

    private void FilterUsers()
    {
        // 实现过滤逻辑
    }

    private void OnUserCreated(UserCreatedMessage message)
    {
        // 刷新列表
        _ = LoadUsersAsync();
    }

    public override void UnregisterAll(object recipient)
    {
        _messenger.Unregister<UserCreatedMessage>(this);
        base.UnregisterAll(recipient);
    }
}
```
