---
name: abp-infrastructure
description: ABP Infrastructure Services - BLOB Storing, Background Jobs, Distributed Event Bus, Caching, Email/SMS sending, Text Templating. Use when implementing infrastructure features like file storage, background processing, or notifications in ABP projects.
---

# ABP Infrastructure Services

> **Docs**: <https://abp.io/docs/latest/infrastructure>

## BLOB Storing

### Configuration

```csharp
// Use database as blob storage
[DependsOn(typeof(AbpBlobStoringDatabaseModule))]
public class MyModule : AbpModule
{
    public override void ConfigureServices(ServiceConfigurationContext context)
    {
        Configure<AbpBlobStoringOptions>(options =>
        {
            options.Containers.AddDefaultAzureContainer(
                connectionString: "DefaultEndpointsProtocol=https;...",
                containerName: "myblobs"
            );
        });
    }
}
```

### Define BLOBs Container

```csharp
// In DbContext
public class MyDbContext : AbpDbContext
{
    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder);

        builder.Entity<BookCover>(b =>
        {
            b.ConfigureByConvention();
            b.ConfigureBlobStorage();
        });
    }
}

// Container definition
public class BookCoverContainer : BlobContainerDefinition
{
    public BookCoverContainer() : base("BookCovers")
    {
        SetFileSizeLimit(5 * 1024 * 1024); // 5MB
        SetAllowedFormats(new[] { "image/jpeg", "image/png", "image/gif" });
    }
}
```

### Save BLOB

```csharp
public class BookAppService : ApplicationService
{
    private readonly IBlobContainer<BookCoverContainer> _blobContainer;

    public BookAppService(IBlobContainer<BookCoverContainer> blobContainer)
    {
        _blobContainer = blobContainer;
    }

    public async Task<string> UploadCoverAsync(Guid bookId, Stream stream)
    {
        var fileName = $"{bookId}.jpg";
        await _blobContainer.SaveAsync(fileName, stream, overrideExisting: true);
        return fileName;
    }

    public async Task<byte[]> GetCoverAsync(Guid bookId)
    {
        var fileName = $"{bookId}.jpg";
        return await _blobContainer.GetAllBytesAsync(fileName);
    }

    public async Task DeleteCoverAsync(Guid bookId)
    {
        var fileName = $"{bookId}.jpg";
        await _blobContainer.DeleteAsync(fileName);
    }
}
```

### BLOB Storage Providers

| Provider | NuGet Package |
| --- | --- |
| Database | `Volo.Abp.BlobStoring.Database` |
| File System | Built-in |
| Azure Blob Storage | `Volo.Abp.BlobStoring.Azure` |
| AWS S3 | `Volo.Abp.BlobStoring.Aws` |
| Aliyun OSS | `Volo.Abp.BlobStoring.Aliyun` |
| MinIO | `Volo.Abp.BlobStoring.Minio` |
| Google Cloud Storage | `Volo.Abp.BlobStoring.GoogleCloud` |

## Background Jobs

### Define Job

```csharp
// Simple background job
public class SendEmailJob : AsyncBackgroundJob<SendEmailJobArgs>, ITransientDependency
{
    private readonly IEmailSender _emailSender;

    public SendEmailJob(IEmailSender emailSender)
    {
        _emailSender = emailSender;
    }

    public override async Task ExecuteAsync(SendEmailJobArgs args)
    {
        await _emailSender.SendAsync(
            args.To,
            args.Subject,
            args.Body
        );
    }
}

public class SendEmailJobArgs
{
    public string To { get; set; }
    public string Subject { get; set; }
    public string Body { get; set; }
}
```

### Enqueue Job

```csharp
public class OrderAppService : ApplicationService
{
    private readonly IBackgroundJobManager _backgroundJobManager;

    public OrderAppService(IBackgroundJobManager backgroundJobManager)
    {
        _backgroundJobManager = backgroundJobManager;
    }

    public async Task CompleteOrderAsync(Guid orderId)
    {
        var order = await _orderRepository.GetAsync(orderId);

        await _backgroundJobManager.EnqueueAsync<SendEmailJob, SendEmailJobArgs>(
            new SendEmailJobArgs
            {
                To = order.CustomerEmail,
                Subject = "Order Confirmed",
                Body = $"Your order {orderId} has been confirmed."
            },
            delay: TimeSpan.FromMinutes(5) // Optional delay
        );
    }
}
```

### Background Job Providers

| Provider | Configuration |
| --- | --- |
| Hangfire | `UseHangfire()` |
| RabbitMQ | `UseRabbitMQ()` |
| Quartz | `UseQuartz()` |

## Distributed Event Bus

### Publish Event

```csharp
public class OrderAppService : ApplicationService
{
    private readonly IDistributedEventBus _eventBus;

    public OrderAppService(IDistributedEventBus eventBus)
    {
        _eventBus = eventBus;
    }

    public async Task CreateOrderAsync(CreateOrderDto input)
    {
        var order = new Order(input.CustomerId);
        await _orderRepository.InsertAsync(order);

        await _eventBus.PublishAsync(new OrderCreatedEto
        {
            OrderId = order.Id,
            CustomerId = order.CustomerId,
            TotalAmount = order.TotalAmount
        });
    }
}
```

### Subscribe Event

```csharp
public class OrderCreatedEventHandler :
    IDistributedEventHandler<OrderCreatedEto>
{
    private readonly ILogger<OrderCreatedEventHandler> _logger;

    public OrderCreatedEventHandler(ILogger<OrderCreatedEventHandler> logger)
    {
        _logger = logger;
    }

    public async Task HandleEventAsync(OrderCreatedEto eventData)
    {
        _logger.LogInformation($"Order created: {eventData.OrderId}");

        // Send notification, update inventory, etc.
    }
}
```

## Caching

### Configure Cache

```csharp
public override void ConfigureServices(ServiceConfigurationContext context)
{
    Configure<AbpDistributedCacheOptions>(options =>
    {
        options.KeyPrefix = "MyApp:";
        options.GlobalCacheEntryOptions = new DistributedCacheEntryOptions
        {
            AbsoluteExpiration = TimeSpan.FromMinutes(30)
        };
    });
}
```

### Use Cache

```csharp
public class BookAppService : ApplicationService
{
    private readonly IDistributedCache<BookCacheItem> _cache;

    public BookAppService(IDistributedCache<BookCacheItem> cache)
    {
        _cache = cache;
    }

    public async Task<BookDto> GetBookAsync(Guid id)
    {
        var cacheKey = $"book:{id}";

        return await _cache.GetOrAddAsync(
            cacheKey,
            async () =>
            {
                var book = await _bookRepository.GetAsync(id);
                return ObjectMapper.Map<Book, BookDto>(book);
            },
            () => new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(30)
            }
        );
    }
}

public class BookCacheItem
{
    public Guid Id { get; set; }
    public string Name { get; set; }
}
```

## Email Sending

### Configuration

```csharp
public override void ConfigureServices(ServiceConfigurationContext context)
{
    Configure<AbpEmailingOptions>(options =>
    {
        options.DefaultFromAddress = "noreply@myapp.com";
        options.DefaultFromDisplayName = "My Application";
    });

    Configure<EmailSenderOptions>(options =>
    {
        options.Host = "smtp.example.com";
        options.Port = 587;
        options.UserName = "username";
        options.Password = "password";
        options.EnableSsl = true;
    });
}
```

### Send Email

```csharp
public class NotificationService : ApplicationService
{
    private readonly IEmailSender _emailSender;

    public NotificationService(IEmailSender emailSender)
    {
        _emailSender = emailSender;
    }

    public async Task SendWelcomeEmailAsync(string email, string name)
    {
        await _emailSender.SendAsync(
            to: email,
            subject: "Welcome to MyApp",
            body: $"Hello {name}, welcome to our application!"
        );
    }
}
```

## SMS Sending

### Configuration

```csharp
public override void ConfigureServices(ServiceConfigurationContext context)
{
    Configure<AbpSmsOptions>(options =>
    {
        options.AddTwilio(
            accountSId: "your-account-sid",
            authToken: "your-auth-token",
            from: "+1234567890"
        );
    });
}
```

### Send SMS

```csharp
public class SmsService : ApplicationService
{
    private readonly ISmsSender _smsSender;

    public SmsService(ISmsSender smsSender)
    {
        _smsSender = smsSender;
    }

    public async Task SendVerificationCodeAsync(string phoneNumber, string code)
    {
        await _smsSender.SendAsync(
            phoneNumber,
            $"Your verification code is: {code}"
        );
    }
}
```

## Text Templating

### Define Template

```csharp
public class OrderConfirmationTemplate : ITemplateContentProvider
{
    public string Template => "Dear {{CustomerName}},\n\n" +
        "Your order #{{OrderNumber}} has been confirmed.\n" +
        "Total: {{TotalAmount}}";
}
```

### Render Template

```csharp
public class OrderService : ApplicationService
{
    private readonly ITemplateRenderer _templateRenderer;

    public OrderService(ITemplateRenderer templateRenderer)
    {
        _templateRenderer = templateRenderer;
    }

    public async Task SendOrderConfirmationAsync(Order order)
    {
        var content = await _templateRenderer.RenderAsync<OrderConfirmationTemplate>(
            new
            {
                CustomerName = order.CustomerName,
                OrderNumber = order.OrderNumber,
                TotalAmount = order.TotalAmount.ToString("C")
            }
        );

        await _emailSender.SendAsync(order.Email, "Order Confirmed", content);
    }
}
```

## Best Practices

1. **Use BLOB storage for files** - Don't store files in database
2. **Background jobs for long operations** - Don't block HTTP requests
3. **Cache frequently accessed data** - Reduce database load
4. **Use distributed events for cross-service communication** - Eventual consistency
5. **Configure retry policies** - Handle transient failures
6. **Monitor infrastructure services** - Health checks and logging
