---
name: abp-microservice
description: ABP Microservice architecture - API Gateway, Distributed Event Bus, Service-to-Service communication, Microservice Solution Template. Use when designing or working with microservice architecture in ABP projects.
---

# ABP Microservice Architecture

> **Docs**: <https://abp.io/docs/latest/solution-templates/microservice>

## Microservice Solution Structure

```
MyProject/
├── services/
│   ├── MyProject/
│   │   ├── MyProject.Domain/
│   │   ├── MyProject.Application/
│   │   ├── MyProject.EntityFrameworkCore/
│   │   └── MyProject.HttpApi/
│   ├── MyProjectAdministration/
│   │   └── ...
│   └── Identity/
│       └── ...
├── apps/
│   ├── backend/
│   │   ├── MyProject.HttpApi.Host/
│   │   └── MyProject.SwaggerHub/
│   └── angular/
│       └── ...
├── apigateways/
│   └── MyProject.Gateway/
│       └── ...
├── dbmigrator/
│   └── MyProject.DbMigrator/
└── test/
    └── ...
```

## Create Microservice Solution

```bash
abp new MyProject -t microservice

# With specific options
abp new MyProject -t microservice -u angular
```

## API Gateway

### Configuration

```csharp
// apps/apigateways/MyProject.Gateway/Program.cs
app.UseOcelot().Wait();
```

### Route Configuration

```json
// apps/apigateways/MyProject.Gateway/ocelot.json
{
  "Routes": [
    {
      "DownstreamPathTemplate": "/api/my-project/books",
      "DownstreamScheme": "https",
      "DownstreamHostAndPorts": [
        {
          "Host": "myproject-api",
          "Port": 443
        }
      ],
      "UpstreamPathTemplate": "/api/books",
      "UpstreamHttpMethod": [ "Get", "Post", "Put", "Delete" ],
      "AuthenticationOptions": {
        "AuthenticationProviderKey": "Bearer"
      }
    }
  ]
}
```

## Distributed Event Bus

### Define Event

```csharp
// MyProject.Domain/Books/Events/BookCreatedEvent.cs
public class BookCreatedEvent : EventData
{
    public Guid BookId { get; set; }
    public string BookName { get; set; }
    public decimal Price { get; set; }

    public BookCreatedEvent(Guid bookId, string bookName, decimal price)
    {
        BookId = bookId;
        BookName = bookName;
        Price = price;
    }
}
```

### Publish Event

```csharp
// MyProject.Application/Books/BookAppService.cs
public class BookAppService : ApplicationService, IBookAppService
{
    private readonly IDistributedEventBus _eventBus;

    public BookAppService(IDistributedEventBus eventBus)
    {
        _eventBus = eventBus;
    }

    public async Task<BookDto> CreateAsync(CreateBookDto input)
    {
        var book = new Book(
            GuidGenerator.Create(),
            input.Name,
            input.Price
        );

        await _bookRepository.InsertAsync(book);

        // Publish distributed event
        await _eventBus.PublishAsync(new BookCreatedEvent(
            book.Id,
            book.Name,
            book.Price
        ));

        return ObjectMapper.Map<Book, BookDto>(book);
    }
}
```

### Subscribe to Event

```csharp
// MyProject.Application/Books/BookCreatedEventHandler.cs
public class BookCreatedEventHandler :
    IDistributedEventHandler<BookCreatedEvent>
{
    private readonly ILogger<BookCreatedEventHandler> _logger;

    public BookCreatedEventHandler(ILogger<BookCreatedEventHandler> logger)
    {
        _logger = logger;
    }

    public Task HandleEventAsync(BookCreatedEvent eventData)
    {
        _logger.LogInformation(
            "Book created: {BookId} - {BookName}",
            eventData.BookId,
            eventData.BookName
        );

        // Notify external systems, update cache, etc.
        return Task.CompletedTask;
    }
}
```

## Service-to-Service Communication

### HTTP Client

```csharp
// Define HTTP client in module
public override void ConfigureServices(ServiceConfigurationContext context)
{
    context.Services.AddHttpClient<BookCatalogHttpClient>();
}

// Inject and use
public class BookAppService : ApplicationService
{
    private readonly BookCatalogHttpClient _catalogClient;

    public BookAppService(BookCatalogHttpClient catalogClient)
    {
        _catalogClient = catalogClient;
    }

    public async Task SyncBookAsync(Guid bookId)
    {
        var catalogInfo = await _catalogClient.GetBookInfoAsync(bookId);
        // Process catalog info
    }
}
```

### Typed HTTP Client

```csharp
// MyProject.HttpApi.Client/BookCatalogHttpClient.cs
public class BookCatalogHttpClient
{
    private readonly HttpClient _httpClient;

    public BookCatalogHttpClient(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<CatalogBookDto> GetBookInfoAsync(Guid bookId)
    {
        var response = await _httpClient.GetAsync($"/api/catalog/books/{bookId}");
        return await response.Content.ReadFromJsonAsync<CatalogBookDto>();
    }
}
```

## Database Per Service

```csharp
// Each service has its own DbContext
// MyProject.EntityFrameworkCore/MyProjectDbContext.cs
[ConnectionStringName("MyProject")]
public class MyProjectDbContext : AbpDbContext<MyProjectDbContext>
{
    // Service-specific DbSets
    public DbSet<Book> Books { get; set; }
}
```

## Authentication in Microservices

```csharp
// Each service validates JWT tokens
public class MyProjectHttpApiHostModule : AbpModule
{
    public override void ConfigureServices(ServiceConfigurationContext context)
    {
        Configure<AbpAuthenticationOptions>(options =>
        {
            options.TokenRules.Add(AnonymousPermissionRule); // Allow anonymous endpoints
        });
    }
}
```

## Health Checks

```csharp
// MyProject.HttpApi.Host/Program.cs
app.UseHealthChecks("/health", new Microsoft.AspNetCore.Diagnostics.HealthChecks.HealthCheckOptions
{
    ResponseWriter = async (context, report) =>
    {
        context.Response.ContentType = "application/json";
        await context.Response.WriteAsync(JsonSerializer.Serialize(new
        {
            status = report.Status.ToString(),
            checks = report.Entries.Select(e => new
            {
                name = e.Key,
                status = e.Value.Status.ToString()
            })
        }));
    }
});
```

## Docker Deployment

```dockerfile
# services/MyProject/MyProject.HttpApi.Host/Dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY bin/Release/net8.0/publish .
EXPOSE 80
ENTRYPOINT ["dotnet", "MyProject.HttpApi.Host.dll"]
```

```yaml
# docker-compose.yml
services:
  myproject-api:
    build: ./services/MyProject/MyProject.HttpApi.Host
    ports:
      - "5000:80"
    environment:
      - ConnectionStrings__Default=Server=db;Database=MyProject;User=sa;Password=...
    depends_on:
      - db

  identity-api:
    build: ./services/Identity/MyProject.Identity.HttpApi.Host
    ports:
      - "5001:80"
```

## Kubernetes Deployment

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myproject-api
spec:
  selector:
    app: myproject-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myproject-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myproject-api
  template:
    metadata:
      labels:
        app: myproject-api
    spec:
      containers:
        - name: myproject-api
          image: myproject-api:latest
          ports:
            - containerPort: 80
```

## Best Practices

1. **Database per service** - Each service owns its data
2. **Async communication** - Use events for eventual consistency
3. **API Gateway** - Single entry point for clients
4. **Health checks** - Monitor service health
5. **Resilience** - Implement retry and circuit breaker patterns
6. **CI/CD** - Automate builds and deployments
