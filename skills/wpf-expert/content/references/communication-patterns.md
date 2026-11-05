# 通讯模式详解

## 1. HTTP 客户端

### HttpClient 封装
```csharp
public interface IHttpClient
{
    Task<Result<T>> GetAsync<T>(string url,
        Dictionary<string, string> headers = null);
    Task<Result<TResponse>> PostAsync<TRequest, TResponse>(
        string url, TRequest data);
    Task<Result<T>> DeleteAsync<T>(string url);
}

public class HttpClientService : IHttpClient
{
    private readonly HttpClient _httpClient;
    private readonly ISerializer _serializer;
    private readonly ILogger _logger;

    public HttpClientService(
        HttpClient httpClient,
        ISerializer serializer,
        ILogger logger)
    {
        _httpClient = httpClient;
        _serializer = serializer;
        _logger = logger;
    }

    public async Task<Result<T>> GetAsync<T>(
        string url,
        Dictionary<string, string> headers = null)
    {
        try
        {
            using var request = new HttpRequestMessage(
                HttpMethod.Get, url);

            if (headers != null)
            {
                foreach (var header in headers)
                {
                    request.Headers.Add(header.Key, header.Value);
                }
            }

            var response = await _httpClient.SendAsync(request);
            return await HandleResponseAsync<T>(response);
        }
        catch (Exception ex)
        {
            _logger.Error($"GET request failed: {url}", ex);
            return Result<T>.Failure("NETWORK_ERROR", ex.Message);
        }
    }

    public async Task<Result<TResponse>> PostAsync<TRequest, TResponse>(
        string url, TRequest data)
    {
        try
        {
            var json = _serializer.Serialize(data);
            using var content = new StringContent(
                json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(url, content);
            return await HandleResponseAsync<TResponse>(response);
        }
        catch (Exception ex)
        {
            _logger.Error($"POST request failed: {url}", ex);
            return Result<TResponse>.Failure("NETWORK_ERROR", ex.Message);
        }
    }

    private async Task<Result<T>> HandleResponseAsync<T>(
        HttpResponseMessage response)
    {
        var content = await response.Content.ReadAsStringAsync();

        if (response.IsSuccessStatusCode)
        {
            var result = _serializer.Deserialize<T>(content);
            return Result<T>.Success(result);
        }

        return Result<T>.Failure(
            $"HTTP_{response.StatusCode}",
            $"Request failed: {response.ReasonPhrase}");
    }
}
```

### Refit 接口驱动
```csharp
// 定义 API 接口
public interface IGitHubApi
{
    [Get("/users/{userId}")]
    Task<User> GetUserAsync(string userId);

    [Get("/repos")]
    Task<List<Repository>> GetRepositoriesAsync(
        [Query] string sort = "updated");

    [Post("/repos")]
    Task<Repository> CreateRepositoryAsync(
        [Body] CreateRepositoryRequest request);
}

// 配置 Refit
public static class RefitConfiguration
{
    public static IServiceCollection AddRefitClients(
        this IServiceCollection services)
    {
        services
            .AddRefitClient<IGitHubApi>()
            .ConfigureHttpClient(c =>
            {
                c.BaseAddress = new Uri("https://api.github.com");
                c.DefaultRequestHeaders.Add("Accept", "application/json");
            })
            .AddPolicyHandler(GetRetryPolicy())
            .AddPolicyHandler(GetCircuitBreakerPolicy());

        return services;
    }

    private static IAsyncPolicy<HttpResponseMessage> GetRetryPolicy()
    {
        return HttpPolicyExtensions
            .HandleTransientHttpError()
            .WaitAndRetryAsync(3, retryAttempt =>
                TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)));
    }

    private static IAsyncPolicy<HttpResponseMessage> GetCircuitBreakerPolicy()
    {
        return HttpPolicyExtensions
            .HandleTransientHttpError()
            .CircuitBreakerAsync(5, TimeSpan.FromMinutes(1));
    }
}
```

## 2. SignalR 实时通讯

### Hub 实现
```csharp
public class NotificationHub : Hub
{
    private readonly INotificationService _notificationService;
    private readonly IUserTracker _userTracker;

    public NotificationHub(
        INotificationService notificationService,
        IUserTracker userTracker)
    {
        _notificationService = notificationService;
        _userTracker = userTracker;
    }

    public override async Task OnConnectedAsync()
    {
        await base.OnConnectedAsync();
        await _userTracker.UserConnected(Context.ConnectionId);
    }

    public override async Task OnDisconnectedAsync(Exception exception)
    {
        await _userTracker.UserDisconnected(Context.ConnectionId);
        await base.OnDisconnectedAsync(exception);
    }

    // 加入特定组
    public async Task JoinGroup(string groupName)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, groupName);
    }

    public async Task LeaveGroup(string groupName)
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, groupName);
    }

    // 发送消息到组
    public async Task SendToGroup(string groupName, string message)
    {
        await Clients.Group(groupName).SendAsync("ReceiveMessage", message);
    }
}
```

### WPF 客户端
```csharp
public interface ISignalRClient
{
    event EventHandler<NotificationEventArgs> NotificationReceived;
    event EventHandler<ConnectionStateChangedEventArgs> StateChanged;
    Task ConnectAsync();
    Task DisconnectAsync();
    Task SendMessageAsync(string message);
}

public class SignalRClient : ISignalRClient, IDisposable
{
    private HubConnection _connection;
    private readonly ILogger _logger;

    public SignalRClient(ILogger logger)
    {
        _logger = logger;
    }

    public event EventHandler<NotificationEventArgs> NotificationReceived;
    public event EventHandler<ConnectionStateChangedEventArgs> StateChanged;

    public async Task ConnectAsync()
    {
        _connection = new HubConnectionBuilder()
            .WithUrl("https://api.example.com/notificationHub")
            .WithAutomaticReconnect(new[] {
                TimeSpan.Zero,
                TimeSpan.FromSeconds(2),
                TimeSpan.FromSeconds(5),
                TimeSpan.FromSeconds(10)
            })
            .ConfigureLogging(logging =>
            {
                logging.AddConsole();
            })
            .Build();

        RegisterHandlers();

        _connection.Closed += OnConnectionClosed;
        _connection.Reconnecting += OnReconnecting;
        _connection.Reconnected += OnReconnected;

        await _connection.StartAsync();
    }

    private void RegisterHandlers()
    {
        _connection.On<string>("ReceiveNotification", (message) =>
        {
            NotificationReceived?.Invoke(this,
                new NotificationEventArgs(message));
        });

        _connection.On<string, string>("ReceiveMessage",
            (user, message) =>
            {
                NotificationReceived?.Invoke(this,
                    new NotificationEventArgs($"{user}: {message}"));
            });
    }

    public async Task SendMessageAsync(string message)
    {
        if (_connection.State != HubConnectionState.Connected)
            throw new InvalidOperationException("Not connected");

        await _connection.InvokeAsync("SendMessage", message);
    }

    private Task OnConnectionClosed(Exception ex)
    {
        _logger.Warning($"Connection closed: {ex?.Message}");
        StateChanged?.Invoke(this,
            new ConnectionStateChangedEventArgs(
                HubConnectionState.Disconnected));
        return Task.CompletedTask;
    }

    public void Dispose()
    {
        _connection?.DisposeAsync().AsTask().Wait();
    }
}
```

## 3. MQTT 物联网通讯

```csharp
public interface IMqttService
{
    event EventHandler<MqttMessageReceivedEventArgs> MessageReceived;
    Task ConnectAsync();
    Task PublishAsync(string topic, string payload);
    Task SubscribeAsync(string topic);
    Task UnsubscribeAsync(string topic);
}

public class MqttService : IMqttService, IDisposable
{
    private IMqttClient _client;
    private readonly MqttClientOptions _options;
    private readonly ILogger _logger;

    public event EventHandler<MqttMessageReceivedEventArgs> MessageReceived;

    public MqttService(string broker, string clientId)
    {
        var factory = new MqttFactory();

        _options = new MqttClientOptionsBuilder()
            .WithTcpServer(broker)
            .WithClientId(clientId)
            .WithCredentials("username", "password")
            .WithCleanSession()
            .WithProtocolVersion(MQTTnet.Formatter.MqttProtocolVersion.V500)
            .Build();

        _client = factory.CreateMqttClient();
    }

    public async Task ConnectAsync()
    {
        _client.ApplicationMessageReceivedAsync += OnMessageReceived;

        await _client.ConnectAsync(_options);

        _logger.Info("MQTT connected");
    }

    public async Task PublishAsync(string topic, string payload)
    {
        var message = new MqttApplicationMessageBuilder()
            .WithTopic(topic)
            .WithPayload(payload)
            .WithQualityOfServiceLevel(MQTTnet.Protocol.MqttQualityOfServiceLevel.AtLeastOnce)
            .Build();

        await _client.PublishAsync(message);
    }

    public async Task SubscribeAsync(string topic)
    {
        await _client.SubscribeAsync(new MqttTopicFilterBuilder()
            .WithTopic(topic)
            .Build());

        _logger.Info($"Subscribed to {topic}");
    }

    private Task OnMessageReceived(MqttApplicationMessageReceivedEventArgs e)
    {
        var payload = Encoding.UTF8.GetString(e.ApplicationMessage.PayloadSegment);

        MessageReceived?.Invoke(this,
            new MqttMessageReceivedEventArgs(
                e.ApplicationMessage.Topic,
                payload));

        return Task.CompletedTask;
    }

    public void Dispose()
    {
        _client?.Dispose();
    }
}
```

## 4. gRPC 服务调用

### Protobuf 定义
```protobuf
syntax = "proto3";

package user;

service UserService {
    rpc GetUser(GetUserRequest) returns (UserResponse);
    rpc ListUsers(ListUsersRequest) returns (stream UserResponse);
    rpc CreateUser(CreateUserRequest) returns (UserResponse);
    rpc DeleteUser(DeleteUserRequest) returns (Empty);
}

message GetUserRequest {
    int32 id = 1;
}

message UserResponse {
    int32 id = 1;
    string name = 2;
    string email = 3;
    bool is_active = 4;
}

message ListUsersRequest {
    int32 page = 1;
    int32 page_size = 2;
}

message CreateUserRequest {
    string name = 1;
    string email = 2;
}

message DeleteUserRequest {
    int32 id = 1;
}

message Empty {}
```

### 客户端实现
```csharp
public interface IUserGrpcService
{
    Task<User> GetUserAsync(int id);
    IAsyncEnumerable<User> ListUsersAsync(int page, int pageSize);
    Task<User> CreateUserAsync(string name, string email);
}

public class UserGrpcService : IUserGrpcService
{
    private readonly UserService.UserServiceClient _client;
    private readonly ILogger _logger;

    public UserGrpcService(
        UserService.UserServiceClient client,
        ILogger logger)
    {
        _client = client;
        _logger = logger;
    }

    public async Task<User> GetUserAsync(int id)
    {
        try
        {
            var response = await _client.GetUserAsync(
                new GetUserRequest { Id = id });

            return new User
            {
                Id = response.Id,
                Name = response.Name,
                Email = response.Email
            };
        }
        catch (Grpc.Core.RpcException ex)
        {
            _logger.Error($"gRPC call failed: {ex.Status}");
            throw;
        }
    }

    public async IAsyncEnumerable<User> ListUsersAsync(
        int page, int pageSize)
    {
        using var call = _client.ListUsers(new ListUsersRequest
        {
            Page = page,
            PageSize = pageSize
        });

        await foreach (var user in call.ResponseStream.ReadAllAsync())
        {
            yield return new User
            {
                Id = user.Id,
                Name = user.Name,
                Email = user.Email
            };
        }
    }
}
```

## 5. 通讯策略选择

| 场景 | 推荐协议 | 原因 |
|------|----------|------|
| REST API | HTTP/REST | 通用、标准、易调试 |
| 实时推送 | SignalR/WebSocket | 双向通讯、自动重连 |
| 物联网 | MQTT | 轻量级、低带宽、订阅发布 |
| 高性能服务调用 | gRPC | 二进制协议、类型安全 |
| 消息队列 | RabbitMQ/Azure Service Bus | 异步、解耦、可靠性 |
| 实时流 | WebSocket/SignalR | 低延迟、双向流 |
