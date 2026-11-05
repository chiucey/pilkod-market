---
name: dotnet-microservices
description: 掌握 .NET 微服务架构开发技能。当用户要求进行微服务设计、服务间通信、API Gateway 配置、服务发现、容器化部署、或需要实现分布式系统时使用。
---

# 微服务架构开发技能

## 核心技能清单

| 技能项 | 熟练度 | 说明 |
|-------|-------|------|
| 服务拆分 | ⭐⭐⭐⭐⭐ | 限界上下文、领域划分 |
| 容器化 | ⭐⭐⭐⭐⭐ | Docker、Kubernetes |
| 服务通信 | ⭐⭐⭐⭐⭐ | REST、gRPC、消息 |
| API Gateway | ⭐⭐⭐⭐⭐ | Ocelot、YARP |
| 服务发现 | ⭐⭐⭐⭐ | Consul、Eureka |
| 分布式追踪 | ⭐⭐⭐⭐ | OpenTelemetry、Jaeger |

## 服务拆分原则

### 限界上下文

```
┌──────────────────────────────────────────────────────────────────┐
│                        电商系统                                    │
├─────────────────┬──────────────────┬─────────────────────────────┤
│    订单服务      │     库存服务       │        支付服务              │
│   Order Service │  Inventory Svc   │      Payment Service         │
├─────────────────┼──────────────────┼─────────────────────────────┤
│ - Order         │ - Product        │ - Payment                   │
│ - OrderItem    │ - Inventory       │ - Refund                    │
│ - Customer     │ - Warehouse       │ - Transaction               │
│ - Address      │ - StockLevel      │ - Merchant                  │
├─────────────────┼──────────────────┼─────────────────────────────┤
│ Order Db        │ Inventory Db      │ Payment Db                  │
└─────────────────┴──────────────────┴─────────────────────────────┘
```

### 领域划分示例

```csharp
// 每个微服务独立的领域模型
namespace OrderService.Domain;

public class Order : AggregateRoot
{
    public Guid Id { get; private set; }
    public Guid CustomerId { get; private set; }
    public OrderStatus Status { get; private set; }
    public List<OrderItem> Items { get; private set; }
    public Money Total { get; private set; }

    // 订单服务独有的业务逻辑
    public void AddItem(Product product, int quantity) { }
    public void Confirm() { }
    public void Cancel() { }
}
```

## Docker 容器化

### Dockerfile

```dockerfile
# 基础镜像
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

# 构建镜像
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["src/OrderService/OrderService.csproj", "OrderService/"]
RUN dotnet restore "OrderService/OrderService.csproj"
COPY . .
WORKDIR "/src/OrderService"
RUN dotnet build "OrderService.csproj" -c Release -o /app/build

# 发布镜像
FROM build AS publish
RUN dotnet publish "OrderService.csproj" -c Release -o /app/publish

# 运行镜像
FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "OrderService.dll"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  order-service:
    build:
      context: .
      dockerfile: src/OrderService/Dockerfile
    ports:
      - "5001:80"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__Default=Server=sqlserver;Database=Orders;User=sa;Password=StrongPassword
      - ServiceBus__ConnectionString=${SERVICE_BUS_CONNECTION}
    depends_on:
      - sqlserver
      - rabbitmq
    networks:
      - microservice-network

  inventory-service:
    build:
      context: .
      dockerfile: src/InventoryService/Dockerfile
    ports:
      - "5002:80"
    networks:
      - microservice-network

  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=StrongPassword
    volumes:
      - sqlserver-data:/var/opt/mssql
    networks:
      - microservice-network

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - microservice-network

volumes:
  sqlserver-data:

networks:
  microservice-network:
    driver: bridge
```

## 服务通信

### REST通信

```csharp
// 使用 HttpClientFactory
public class OrderService
{
    private readonly HttpClient _httpClient;

    public OrderService(IHttpClientFactory httpClientFactory)
    {
        _httpClient = httpClientFactory.CreateClient("InventoryService");
    }

    public async Task<bool> CheckInventoryAsync(Guid productId, int quantity)
    {
        var response = await _httpClient.GetAsync(
            $"/api/inventory/{productId}/check?quantity={quantity}");
        return response.IsSuccessStatusCode;
    }
}

// Program.cs 配置
builder.Services.AddHttpClient("InventoryService", client =>
{
    client.BaseAddress = new Uri("http://inventory-service");
    client.Timeout = TimeSpan.FromSeconds(10);
});
```

### gRPC 通信

```protobuf
// inventory.proto
syntax = "proto3";

option csharp_namespace = "OrderService.gRPC";

package inventory;

service InventoryService {
    rpc CheckStock (StockRequest) returns (StockResponse);
    rpc ReserveStock (ReserveRequest) returns (ReserveResponse);
}

message StockRequest {
    string product_id = 1;
    int32 quantity = 2;
}

message StockResponse {
    bool available = 1;
    int32 available_quantity = 2;
}

message ReserveRequest {
    string product_id = 1;
    int32 quantity = 2;
    string order_id = 3;
}

message ReserveResponse {
    bool success = 1;
    string message = 2;
}
```

```csharp
// gRPC 客户端
public class InventoryGrpcService
{
    private readonly InventoryService.InventoryServiceClient _client;

    public InventoryGrpcService(GrpcChannel channel)
    {
        _client = new InventoryService.InventoryServiceClient(channel);
    }

    public async Task<bool> CheckStockAsync(string productId, int quantity)
    {
        var response = await _client.CheckStockAsync(
            new StockRequest
            {
                ProductId = productId,
                Quantity = quantity
            });
        return response.Available;
    }
}
```

### 消息队列通信

```csharp
// 发布消息
public class OrderCreatedEventHandler : IEventHandler<OrderCreatedEvent>
{
    private readonly IMessagePublisher _publisher;

    public async Task HandleAsync(OrderCreatedEvent @event)
    {
        await _publisher.PublishAsync("orders.created", new
        {
            OrderId = @event.OrderId,
            CustomerId = @event.CustomerId,
            TotalAmount = @event.TotalAmount
        });
    }
}

// 订阅消息
public class InventoryEventHandler : IMessageHandler
{
    [Subscribe(Queue = "orders.created")]
    public async Task HandleOrderCreated(dynamic message)
    {
        var orderId = message.OrderId;
        // 处理订单创建事件
    }
}
```

## API Gateway

### YARP 配置

```csharp
// Program.cs
builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));

// appsettings.json
{
  "ReverseProxy": {
    "Routes": {
      "order-route": {
        "ClusterId": "order-cluster",
        "Match": {
          "Path": "/api/orders/{**catch-all}"
        },
        "Transforms": [
          { "PathPattern": "/{**catch-all}" }
        ]
      },
      "inventory-route": {
        "ClusterId": "inventory-cluster",
        "Match": {
          "Path": "/api/inventory/{**catch-all}"
        }
      }
    },
    "Clusters": {
      "order-cluster": {
        "Destinations": {
          "order-service-1": {
            "Address": "http://order-service:80"
          }
        }
      },
      "inventory-cluster": {
        "Destinations": {
          "inventory-service-1": {
            "Address": "http://inventory-service:80"
          }
        }
      }
    }
  }
}
```

### Ocelot 配置

```json
{
  "Routes": [
    {
      "DownstreamPathTemplate": "/api/orders/{everything}",
      "DownstreamScheme": "http",
      "DownstreamHostAndPorts": [
        { "Host": "order-service", "Port": 80 }
      ],
      "UpstreamPathTemplate": "/orders/{everything}",
      "UpstreamHttpMethod": ["GET", "POST", "PUT", "DELETE"],
      "AuthenticationOptions": {
        "AuthenticationProviderKey": "Bearer",
        "AllowedScopes": ["order.read", "order.write"]
      },
      "RateLimitOptions": {
        "ClientWhitelist": [],
        "EnableRateLimiting": true,
        "Period": "1s",
        "PeriodTimespan": 1,
        "Limit": 100
      }
    }
  ],
  "GlobalConfiguration": {
    "BaseUrl": "https://api.example.com",
    "RateLimitOptions": {
      "QuotaExceededMessage": "API 访问频率超限"
    }
  }
}
```

## 服务发现

### Consul 集成

```csharp
// Program.cs
builder.Services.AddConsulServiceDiscovery(options =>
{
    options.HostName = "consul";
    options.Port = 8500;
    options.DiscoveryOptions = new ConsulServiceDiscoveryOptions
    {
        PreferIpAddress = true,
        DrainConnectionInterval = TimeSpan.FromSeconds(5)
    };
});

// 注册服务
builder.Services.RegisterServiceDiscovery(options =>
{
    options.ServiceName = "order-service";
    options.Port = 80;
    options.Address = Dns.GetHostEntry(Dns.GetHostName())
        .AddressList.FirstOrDefault()?.ToString();
});
```

### 负载均衡

```csharp
// HttpClientFactory 负载均衡
builder.Services.AddHttpClient("InventoryService")
    .UseDubboLoadBalancer(options =>
    {
        options.LoadBalancerType = LoadBalancerType.RoundRobin;
    });

// gRPC 负载均衡
var channel = GrpcChannel.ForAddress(
    "http://inventory-cluster",
    new GrpcChannelOptions
    {
        LoadBalancingChannelCredentials = ChannelCredentials.Create(
            new SslCredentials(),
            new[]
            {
                new ChannelOption(
                    "lb_config",
                    JsonSerializer.Serialize(new
                    {
                        targets = new[]
                        {
                            new { ip = "inventory-1:80" },
                            new { ip = "inventory-2:80" }
                        }
                    }))
            })
    });
```

## 分布式追踪

### OpenTelemetry 配置

```csharp
// Program.cs
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing =>
    {
        tracing
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddEntityFrameworkCoreInstrumentation()
            .AddSource("OrderService")
            .AddJaegerExporter(options =>
            {
                options.AgentHost = "jaeger";
                options.AgentPort = 6831;
            });
    });
```

### 追踪传播

```csharp
// 创建带追踪的 HttpClient
public class TracingHttpHandler : DelegatingHandler
{
    private readonly ActivitySource _activitySource;

    public TracingHttpHandler(ActivitySource activitySource)
    {
        _activitySource = activitySource;
    }

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        using var activity = _activitySource.StartActivity(
            "HTTP " + request.Method.Method);
        
        activity?.SetTag("http.url", request.RequestUri);
        activity?.SetTag("http.method", request.Method.Method);

        var response = await base.SendAsync(request, cancellationToken);

        activity?.SetTag("http.status_code", (int)response.StatusCode);
        return response;
    }
}
```

## Saga 模式

### 编排 Saga

```csharp
public class OrderSagaOrchestrator
{
    private readonly IMessagePublisher _publisher;

    public async Task ExecuteOrderSaga(CreateOrderCommand command)
    {
        // 1. 创建订单
        var orderId = Guid.NewGuid();
        await _publisher.PublishAsync("order.created", new { OrderId = orderId });

        // 2. 预留库存
        var inventoryReserved = await WaitForResponse<bool>(
            "inventory.reserved", orderId);
        
        if (!inventoryReserved)
        {
            await _publisher.PublishAsync("order.cancelled", 
                new { OrderId = orderId, Reason = "Insufficient inventory" });
            return;
        }

        // 3. 处理支付
        await _publisher.PublishAsync("payment.processing", new { OrderId = orderId });
        var paymentProcessed = await WaitForResponse<bool>(
            "payment.processed", orderId);

        if (!paymentProcessed)
        {
            // 补偿库存
            await _publisher.PublishAsync("inventory.release", new { OrderId = orderId });
            await _publisher.PublishAsync("order.cancelled", 
                new { OrderId = orderId, Reason = "Payment failed" });
            return;
        }

        // 4. 完成订单
        await _publisher.PublishAsync("order.completed", new { OrderId = orderId });
    }
}
```

## 健康检查

```csharp
// 配置健康检查
builder.Services.AddHealthChecks()
    .AddSqlServer(connectionString, name: "sqlserver")
    .AddRedis(redisConnectionString, name: "redis")
    .AddRabbitMQ(rabbitConnectionString, name: "rabbitmq")
    .AddUrlGroup(new Uri("http://inventory-service/health"), 
        name: "inventory-service");

// 健康检查端点
app.MapHealthChecks("/health", new Microsoft.AspNetCore.Diagnostics.HealthChecks
{
    Predicate = check => check.Tags.Contains("ready")
});

app.MapHealthChecks("/health/live", new Microsoft.AspNetCore.Diagnostics.HealthChecks
{
    Predicate = _ => false // 仅检查应用是否存活
});
```
