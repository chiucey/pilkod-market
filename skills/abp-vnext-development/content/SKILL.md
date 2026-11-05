---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9fe5d0916571eef6c491d450f989c014
    PropagateID: 9fe5d0916571eef6c491d450f989c014
    ReservedCode1: 30440220329375cf8c058a0eabc959f7bafd47caf0f8b3f29848f8a198ac84272b652aa702203ab7aed5438da6c51bbc97e515c14b52e556b313b0e5fa906a06cd2439b82d6e
    ReservedCode2: 304502205d7b563d5ae0047d5e1c0954b781b63e4b37b42cf21b69c240c43c6308fa6490022100e7c588429679165437a80cf088ec4eacf51155ddebbebbe45fa5b26d5dd63f80
description: ABP vNext 框架开发技能库。用于创建 ABP vNext 项目、开发分层架构（Domain/Application/Infrastructure）、实现应用服务和 DTO、设计实体和仓储、配置权限系统（PermissionDefinitionProvider/[Authorize]）、EF Core 数据库迁移（dotnet ef migrations）、编写集成测试（*TestBase/IDataSeedContributor）、ABP CLI 命令（generate-proxy/install-libs/new-module）、微服务架构、多租户配置、CMS Kit/Identity/SaaS 模块集成。
name: abp-vnext-development
---

# ABP vNext 开发技能库

> **官方文档**: <https://abp.io/docs/latest>

## 技能概述

ABP vNext 是一个基于 ASP.NET Core 的现代应用开发框架，遵循领域驱动设计（DDD）原则，提供模块化架构。本技能库帮助开发者快速掌握 ABP vNext 的核心概念和最佳实践。

## 核心能力

### 1. 项目脚手架与初始化

ABP vNext 提供命令行工具快速创建项目：

```bash
# 安装 ABP CLI
dotnet tool install -g Volo.Abp.Cli

# 创建新解决方案
abp new BookStore -t app -u mvc

# 创建模块
abp new Acme.BookStore.Domain.Shared -t module
```

**项目结构：**
```
BookStore/
├── src/
│   ├── BookStore.Domain/          # 领域层（实体、领域服务、接口）
│   ├── BookStore.Domain.Shared/   # 共享领域定义（枚举、常量）
│   ├── BookStore.Application/     # 应用层（应用服务、DTO）
│   ├── BookStore.Application.Contracts/  # 应用服务接口
│   ├── BookStore.EntityFrameworkCore/    # 基础设施层（EF Core 实现）
│   ├── BookStore.HttpApi/         # API 层（控制器）
│   └── BookStore.HttpApi.Host/    # API 主机（启动配置）
└── test/
    ├── BookStore.Domain.Tests/
    └── BookStore.Application.Tests/
```

### 2. 领域层开发（Domain Layer）

**创建实体：**

```csharp
// BookStore.Domain/Books/Book.cs
public class Book : AuditedAggregateRoot<Guid>
{
    public string Name { get; set; }
    public BookType Type { get; set; }
    public DateTime PublishDate { get; set; }
    public float Price { get; set; }

    // 私有构造函数用于 ORM
    private Book() { }

    public Book(Guid id, string name, BookType type, DateTime publishDate, float price)
        : base(id)
    {
        Name = Check.NotNullOrWhiteSpace(name, nameof(name));
        Type = type;
        PublishDate = publishDate;
        Price = price;
    }
}

// BookStore.Domain.Shared/Books/BookType.cs
public enum BookType : byte
{
    Undefined = 0,
    Adventure = 1,
    Biography = 2,
    Dystopia = 3,
    ScienceFiction = 4
}
```

**定义仓储接口：**

```csharp
// BookStore.Domain/Books/IBookRepository.cs
public interface IBookRepository : IRepository<Book, Guid>
{
    Task<List<Book>> GetListAsync(
        int skipCount,
        int maxResultCount,
        string sorting,
        string filter = null
    );
}
```

### 3. 应用层开发（Application Layer）

**创建 DTO：**

```csharp
// BookStore.Application.Contracts/Books/BookDto.cs
public class BookDto : ExtensibleFullAuditedEntityDto<Guid>
{
    public string Name { get; set; }
    public BookType Type { get; set; }
    public DateTime PublishDate { get; set; }
    public float Price { get; set; }
}

// BookStore.Application.Contracts/Books/CreateUpdateBookDto.cs
public class CreateUpdateBookDto : ExtensibleCreationAuditedEntityDto<Guid>
{
    [Required]
    [StringLength(128)]
    public string Name { get; set; }

    public BookType Type { get; set; }

    public DateTime PublishDate { get; set; }

    [Range(0, float.MaxValue)]
    public float Price { get; set; }
}
```

**实现应用服务：**

```csharp
// BookStore.Application/Books/BookAppService.cs
public class BookAppService : CrudAppService<
    Book,
    BookDto,
    Guid,
    PagedAndSortedResultRequestDto,
    CreateUpdateBookDto>,
    IBookAppService
{
    private readonly IBookRepository _bookRepository;

    public BookAppService(IRepository<Book, Guid> repository, IBookRepository bookRepository)
        : base(repository)
    {
        _bookRepository = bookRepository;
    }

    // 自定义业务逻辑
    public async Task<List<BookDto>> GetBooksByTypeAsync(BookType type)
    {
        var books = await _bookRepository.GetListAsync(
            0, 100, "Name",
            $"Type == {(int)type}"
        );

        return ObjectMapper.Map<List<Book>, List<BookDto>>(books);
    }
}

// BookStore.Application.Contracts/Books/IBookAppService.cs
public interface IBookAppService : ICrudAppService<
    BookDto,
    Guid,
    PagedAndSortedResultRequestDto,
    CreateUpdateBookDto>
{
    Task<List<BookDto>> GetBooksByTypeAsync(BookType type);
}
```

### 4. 权限系统

**定义权限：**

```csharp
// BookStore.Domain.Shared/Books/BookPermissions.cs
public static class BookPermissions
{
    public const string GroupName = "BookStore";

    public static class Books
    {
        public const string Default = GroupName + ".Books";
        public const string Create = Default + ".Create";
        public const string Update = Default + ".Update";
        public const string Delete = Default + ".Delete";
    }
}

// BookStore.Domain/Books/BookPermissionDefinitionProvider.cs
public class BookPermissionDefinitionProvider : PermissionDefinitionProvider
{
    public override void Define(IPermissionDefinitionContext context)
    {
        var bookGroup = context.AddGroup(BookPermissions.GroupName);

        var booksPermission = bookGroup.AddPermission(BookPermissions.Books.Default);
        booksPermission.AddChild(BookPermissions.Books.Create);
        booksPermission.AddChild(BookPermissions.Books.Update);
        booksPermission.AddChild(BookPermissions.Books.Delete);
    }
}
```

**应用权限到服务：**

```csharp
[Authorize(BookPermissions.Books.Create)]
public async Task<BookDto> CreateAsync(CreateUpdateBookDto input)
{
    // 实现...
}
```

### 5. 数据库配置

**EntityFrameworkCore 配置：**

```csharp
// BookStore.EntityFrameworkCore/BookStoreDbContext.cs
[ConnectionStringName("Default")]
public class BookStoreDbContext : AbpDbContext<BookStoreDbContext>
{
    public DbSet<Book> Books { get; set; }

    public BookStoreDbContext(DbContextOptions<BookStoreDbContext> options)
        : base(options)
    {
    }

    protected override void OnModelCreating(ModelBuilder builder)
    {
        base.OnModelCreating(builder);
        builder.ConfigureBookStore();
    }
}

// BookStore.EntityFrameworkCore/BookStoreDbContextModelCreatingExtensions.cs
public static class BookStoreDbContextModelCreatingExtensions
{
    public static void ConfigureBookStore(this ModelBuilder builder)
    {
        Check.NotNull(builder, nameof(builder));

        builder.Entity<Book>(b =>
        {
            b.ToTable("Books");
            b.ConfigureByConvention(); // 始终调用！自动配置审计、软删除等

            b.Property(x => x.Name).IsRequired().HasMaxLength(128);
            b.Property(x => x.Price).HasColumnType("decimal(18,2)");

            // 索引
            b.HasIndex(x => x.Name);

            // 关系
            b.HasOne(x => x.Author)
                .WithMany(x => x.Books)
                .HasForeignKey(x => x.AuthorId)
                .OnDelete(DeleteBehavior.Restrict);
        });
    }
}
```

**连接字符串配置：**

```json
// appsettings.json
{
  "ConnectionStrings": {
    "Default": "Server=localhost;Database=BookStoreDb;Trusted_Connection=True"
  }
}
```

**仓储实现：**

```csharp
public class BookRepository : EfCoreRepository<BookStoreDbContext, Book>, IBookRepository
{
    public BookRepository(IDbContextProvider<BookStoreDbContext> dbContextProvider)
        : base(dbContextProvider)
    {
    }

    public async Task<Book> FindByNameAsync(string name, bool includeDetails = true)
    {
        var dbSet = await GetDbSetAsync();
        return await dbSet
            .IncludeDetails(includeDetails)
            .FirstOrDefaultAsync(b => b.Name == name);
    }

    public override async Task<List<Book>> WithDetailsAsync()
    {
        return (await GetQueryableAsync()).Include(b => b.Reviews).ToList();
    }
}
```

#### EF Core 最佳实践

| 禁忌 | 正确做法 |
|------|----------|
| 跳过 `ConfigureByConvention()` | 始终首先调用此方法 |
| `AddDefaultRepositories(includeAllEntities: true)` | 仅对聚合根使用 `AddDefaultRepositories()` |
| 在应用/领域服务中注入 `DbContext` | 使用 `IRepository` 或自定义仓储接口 |
| 在 EF Core 项目外部直接使用 `DbContext` | 仅在仓储内部通过 `GetDbContextAsync()` 访问 |

**模块配置：**

```csharp
[DependsOn(typeof(AbpEntityFrameworkCoreModule))]
public class BookStoreEntityFrameworkCoreModule : AbpModule
{
    public override void ConfigureServices(ServiceConfigurationContext context)
    {
        context.Services.AddAbpDbContext<BookStoreDbContext>(options =>
        {
            // 仅对聚合根添加默认仓储（DDD 最佳实践）
            options.AddDefaultRepositories();
        });

        Configure<AbpDbContextConfigurationOptions>(options =>
        {
            options.UseSqlServer();
        });
    }
}
```

### 6. 模块依赖配置

```csharp
// BookStore.Domain/BookStoreDomainModule.cs
[DependsOn(
    typeof(AbpValidationModule),
    typeof(AbpDddDomainModule)
)]
public class BookStoreDomainModule : AbpModule
{
    public override void ConfigureServices(ServiceConfigurationContext context)
    {
        Configure<AbpAutoMapperOptions>(options =>
        {
            options.AddMaps<BookStoreApplicationModule>();
        });
    }
}

// BookStore.Application/BookStoreApplicationModule.cs
[DependsOn(
    typeof(BookStoreDomainModule),
    typeof(AbpApplicationModule)
)]
public class BookStoreApplicationModule : AbpModule
{
    public override void ConfigureServices(ServiceConfigurationContext context)
    {
        Configure<AbpAutoMapperOptions>(options =>
        {
            options.AddMaps<BookStoreApplicationModule>();
        });
    }
}
```

### 7. 测试策略

ABP 推荐集成测试而非单元测试，测试使用真实服务和 SQLite 内存数据库。

**测试项目结构：**

| 项目 | 用途 | 基类 |
|------|------|------|
| `*.Domain.Tests` | 领域逻辑、实体、领域服务 | `*DomainTestBase` |
| `*.Application.Tests` | 应用服务 | `*ApplicationTestBase` |
| `*.EntityFrameworkCore.Tests` | 仓储实现 | `*EntityFrameworkCoreTestBase` |

**应用服务测试：**

```csharp
public class BookAppService_Tests : BookStoreApplicationTestBase
{
    private readonly IBookAppService _bookAppService;

    public BookAppService_Tests()
    {
        _bookAppService = GetRequiredService<IBookAppService>();
    }

    [Fact]
    public async Task Should_Get_List_Of_Books()
    {
        // Act
        var result = await _bookAppService.GetListAsync(
            new PagedAndSortedResultRequestDto());

        // Assert
        result.TotalCount.ShouldBeGreaterThan(0);
        result.Items.ShouldContain(b => b.Name == "Test Book");
    }

    [Fact]
    public async Task Should_Create_Book()
    {
        // Arrange
        var input = new CreateBookDto
        {
            Name = "New Book",
            Price = 19.99m
        };

        // Act
        var result = await _bookAppService.CreateAsync(input);

        // Assert
        result.Id.ShouldNotBe(Guid.Empty);
        result.Name.ShouldBe("New Book");
    }

    [Fact]
    public async Task Should_Not_Create_Book_With_Invalid_Name()
    {
        // Arrange
        var input = new CreateBookDto
        {
            Name = "", // 无效
            Price = 10m
        };

        // Act & Assert
        await Should.ThrowAsync<AbpValidationException>(async () =>
        {
            await _bookAppService.CreateAsync(input);
        });
    }
}
```

**领域服务测试：**

```csharp
public class BookManager_Tests : BookStoreDomainTestBase
{
    private readonly BookManager _bookManager;

    public BookManager_Tests()
    {
        _bookManager = GetRequiredService<BookManager>();
    }

    [Fact]
    public async Task Should_Not_Allow_Duplicate_Book_Name()
    {
        // Arrange
        await _bookManager.CreateAsync("Existing Book", 10m);

        // Act & Assert
        var exception = await Should.ThrowAsync<BusinessException>(async () =>
        {
            await _bookManager.CreateAsync("Existing Book", 20m);
        });

        exception.Code.ShouldBe("BookStore:BookNameAlreadyExists");
    }
}
```

**测试命名约定：**

```csharp
// 模式: Should_ExpectedBehavior_When_Condition
public async Task Should_Create_Book_When_Input_Is_Valid()
public async Task Should_Throw_BusinessException_When_Name_Already_Exists()
public async Task Should_Return_Empty_List_When_No_Books_Exist()
```

**测试数据种子：**

```csharp
public class BookStoreTestDataSeedContributor : IDataSeedContributor, ITransientDependency
{
    public static readonly Guid TestBookId = Guid.Parse("...");

    private readonly IBookRepository _bookRepository;
    private readonly IGuidGenerator _guidGenerator;

    public async Task SeedAsync(DataSeedContext context)
    {
        await _bookRepository.InsertAsync(
            new Book(TestBookId, "Test Book", 19.99m, Guid.Empty),
            autoSave: true);
    }
}
```

**禁用授权：**

```csharp
public override void ConfigureServices(ServiceConfigurationContext context)
{
    context.Services.AddAlwaysAllowAuthorization();
}
```

**测试多租户：**

```csharp
[Fact]
public async Task Should_Filter_Books_By_Tenant()
{
    using (CurrentTenant.Change(TestData.TenantId))
    {
        var result = await _bookAppService.GetListAsync(new GetBookListDto());
        // 结果应按租户过滤
    }
}
```

### 8. ABP CLI 命令

```bash
# 安装 ABP CLI
dotnet tool install -g Volo.Abp.Cli

# 创建解决方案
abp new BookStore -t app -u mvc          # MVC Razor Pages
abp new BookStore -t app -u blazor        # Blazor
abp new BookStore -t app -u angular       # Angular
abp new BookStore -t microservice         # 微服务解决方案
abp new BookStore -t module               # 应用模块

# 生成客户端代理
abp generate-proxy -t ng                  # Angular（需运行后端）
abp generate-proxy -t csharp -u https://localhost:44300
abp generate-proxy -t js -u https://localhost:44300

# 安装客户端库
abp install-libs                          # MVC/Blazor Server

# 模块操作
abp new-module Acme.OrderManagement -t module:ddd
abp install-module Volo.Blogging
abp add-package Volo.Abp.Caching.StackExchangeRedis
abp add-package-ref Acme.BookStore.Domain

# 更新和清理
abp update                                # 更新所有 ABP 包
abp update --version 8.0.0               # 指定版本
abp clean                                 # 删除 bin/obj 文件夹

# ABP Suite CRUD 生成
abp suite generate --entity .suite/entities/Book.json -s ./Acme.BookStore.sln
```

## 最佳实践

1. **遵循 DDD 分层**：保持各层职责清晰，避免循环依赖
2. **使用 DTO 而非实体**：应用层与表现层通过 DTO 通信
3. **配置而非硬编码**：使用配置文件管理连接字符串、权限等
4. **编写单元测试**：确保核心业务逻辑的可靠性
5. **模块化开发**：相关功能封装为独立模块
6. **使用仓储模式**：抽象数据访问，便于测试

## 常见问题排查

| 问题 | 解决方案 |
|------|----------|
| 迁移失败 | 检查连接字符串，确认数据库服务运行 |
| 权限不生效 | 检查模块依赖顺序，确认权限定义已注册 |
| 自动映射失败 | 检查 Profile 配置，确保 DTO 与实体字段匹配 |
| 服务无法注入 | 检查模块依赖和接口实现 |

### 9. 微服务解决方案

ABP vNext 提供专门的微服务解决方案模板，内置 API 网关、服务间通信、分布式事件总线等基础设施。

```bash
# 创建微服务解决方案
abp new BookStore -t microservice

# 微服务项目结构
├── services/
│   ├── BookStore/
│   │   ├── BookStore.Domain/           # 领域层
│   │   ├── BookStore.Application/       # 应用层
│   │   ├── BookStore.EntityFrameworkCore/  # EF Core
│   │   └── BookStore.HttpApi/          # HTTP API
│   └── BookStoreAdministration/        # 管理服务
├── apps/
│   ├── backend/
│   │   ├── BookStore.HttpApi.Host/     # API 主机
│   │   └── BookStore.SwaggerHub/       # Swagger 聚合
│   └── angular/                        # Angular 前端
├── apigateways/
│   └── BookStore.Gateway/              # API 网关（Ocelot）
└── test/
```

**服务间通信：**

```csharp
// 使用分布式事件总线
public class BookCreatedEvent : EventData
{
    public Guid BookId { get; set; }
    public string BookName { get; set; }
}

// 发布事件
public class BookAppService : IBookAppService
{
    private readonly IDistributedEventBus _eventBus;

    public async Task<BookDto> CreateAsync(CreateUpdateBookDto input)
    {
        var book = await _bookRepository.InsertAsync(new Book(...));

        await _eventBus.PublishAsync(new BookCreatedEvent
        {
            BookId = book.Id,
            BookName = book.Name
        });

        return ObjectMapper.Map<Book, BookDto>(book);
    }
}

// 订阅事件
public class BookCreatedEventHandler :
    IDistributedEventHandler<BookCreatedEvent>
{
    public async Task HandleEventAsync(BookCreatedEvent eventData)
    {
        // 处理事件，如发送通知、更新缓存等
        Logger.LogInformation($"New book created: {eventData.BookName}");
    }
}
```

### 10. 应用模块体系

ABP vNext 提供丰富的预建应用模块，可直接集成到项目中。

#### 10.1 身份认证模块（Identity）

```csharp
// 配置 Identity 模块依赖
[DependsOn(
    typeof(AbpIdentityHttpApiModule),
    typeof(AbpIdentityApplicationModule)
)]
public class BookStoreApplicationModule : AbpModule
{
}

// 使用身份服务
public class UserService
{
    private readonly IIdentityUserAppService _identityUserService;

    public async Task AssignRoleAsync(Guid userId, string roleName)
    {
        await _identityUserService.SetRolesAsync(userId, new IdentityUserRollsDto
        {
            Rolls = new[] { roleName }
        });
    }
}
```

#### 10.2 SaaS 多租户模块

```csharp
// 多租户配置
[DependsOn(typeof(AbpSaaSApplicationModule))]
public class BookStoreApplicationModule : AbpModule
{
}

// 租户管理服务
public class TenantAppService : ITenantAppService
{
    public async Task<TenantDto> CreateAsync(CreateTenantDto input)
    {
        var tenant = await _tenantManager.CreateAsync(input.Name);
        await _tenantRepository.InsertAsync(tenant);
        return ObjectMapper.Map<Tenant, TenantDto>(tenant);
    }
}

// 在实体中启用多租户
public class Book : AuditedAggregateRoot<Guid>, IMultiTenant
{
    public Guid? TenantId { get; set; }
    // 其他属性...
}
```

#### 10.3 CMS Kit 内容管理模块

```csharp
// 配置 CMS Kit
[DependsOn(typeof(CmsKitApplicationModule))]
public class BookStoreApplicationModule : AbpModule
{
}

// 使用博客功能
public class BlogService : IBlogFeature
{
    private readonly IBlogPostRepository _blogPostRepository;

    public async Task<List<BlogPostDto>> GetRecentPostsAsync(int count)
    {
        return await _blogPostRepository.GetListAsync(
            0, count, "CreationTime DESC"
        );
    }
}
```

### 11. 基础设施服务

#### 11.1 BLOB 存储

支持多种存储提供者：内存、文件系统、数据库、Azure、阿里云、Minio、AWS S3、Google Cloud、Bunny.Net。

```csharp
// 定义 BLOBs 容器
public class BookStoreDbContext : AbpDbContext<BookStoreDbContext>
{
    protected override void OnModelCreating(ModelBuilderBuilder options)
    {
        options.Entity<BookCover>(b =>
        {
            b.ConfigureByConvention();
            b.ConfigureBlobStorage();
        });
    }
}

// 使用 BLOB 存储
public class BookCoverService
{
    private readonly IBlobContainer<BookCoverContainer> _blobContainer;

    public async Task<string> UploadCoverAsync(Guid bookId, Stream stream)
    {
        var fileName = $"{bookId}.jpg";
        await _blobContainer.SaveAsync(fileName, stream);
        return fileName;
    }
}

// 容器定义
public class BookCoverContainer : BlobContainerDefinition
{
    public BookCoverContainer() : base("BookCovers")
    {
        SetFileSizeLimit(5 * 1024 * 1024); // 5MB
        SetAllowedFormats(new[] { "image/jpeg", "image/png" });
    }
}
```

#### 11.2 后台作业

支持多种后台作业提供者：Hangfire、RabbitMQ、Quartz。

```csharp
// 定义后台作业
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

// 触发作业
public class OrderAppService : IOrderAppService
{
    private readonly IBackgroundJobManager _backgroundJobManager;

    public async Task CompleteOrderAsync(Guid orderId)
    {
        var order = await _orderRepository.GetAsync(orderId);
        order.Status = OrderStatus.Completed;

        // 发送确认邮件
        await _backgroundJobManager.EnqueueAsync(new SendEmailJobArgs
        {
            To = order.CustomerEmail,
            Subject = "Order Confirmed",
            Body = $"Your order {orderId} has been confirmed."
        });
    }
}
```

#### 11.3 事件总线

```csharp
// 本地事件
public class OrderPlacedEvent : EventData
{
    public Guid OrderId { get; set; }
    public decimal TotalAmount { get; set; }
}

// 发布本地事件
public class OrderAppService : IOrderAppService
{
    private readonly IEventBus _eventBus;

    public async Task<OrderDto> CreateOrderAsync(CreateOrderDto input)
    {
        var order = new Order(input.CustomerId, input.Items);
        await _orderRepository.InsertAsync(order);

        _eventBus.Publish(new OrderPlacedEvent
        {
            OrderId = order.Id,
            TotalAmount = order.TotalAmount
        });

        return ObjectMapper.Map<Order, OrderDto>(order);
    }
}

// 订阅事件
public class OrderPlacedEventHandler :
    ILocalEventHandler<OrderPlacedEvent>
{
    public async Task HandleEventAsync(OrderPlacedEvent eventData)
    {
        // 更新库存
        // 发送通知
        // 记录日志
    }
}
```

### 12. UI 主题系统

ABP vNext 提供可更换的主题系统。

#### 12.1 LeptonX Lite 主题

轻量级现代主题，开源免费。

```bash
# 安装 LeptonX Lite MVC 包
dotnet add package Volo.Abp.AspNetCore.Mvc.UI.Theme.LeptonXLite
```

```csharp
// 配置主题
Configure<AbpAspNetCoreMvcOptions>(options =>
{
    options.ConventionalControllers.Create(typeof(BookStoreApplicationModule).Assembly);
});

// 在 Module 中启用
[DependsOn(typeof(LeptonXLiteMvcModule))]
public class BookStoreModule : AbpModule
{
}
```

#### 12.2 自定义主题

```json
// appsettings.json
{
  "Theme": {
    "Name": "Basic",
    "Layout": "Application"
  }
}
```

### 13. 测试策略

#### 13.1 集成测试

```csharp
// BookStore.IntegrationTests/BookAppService_Tests.cs
public class BookAppService_Tests : BookStoreIntegrationTestBase
{
    private readonly IBookAppService _bookService;

    public BookAppService_Tests()
    {
        _bookService = GetRequiredService<IBookAppService>();
    }

    [Fact]
    public async Task Should_Create_Book_With_Valid_Data()
    {
        // Given
        var input = new CreateUpdateBookDto
        {
            Name = "Test Book",
            Type = BookType.ScienceFiction,
            PublishDate = DateTime.Now,
            Price = 100
        };

        // When
        var result = await _bookService.CreateAsync(input);

        // Then
        result.Id.ShouldNotBe(Guid.Empty);
        result.Name.ShouldBe("Test Book");

        // 验证数据库
        var dbBook = await UsingDbContextAsync(async db =>
            await db.Books.FirstOrDefaultAsync(b => b.Id == result.Id));
        dbBook.ShouldNotBeNull();
    }
}
```

#### 13.2 使用测试数据库

```csharp
// TestBase.cs
public abstract class BookStoreIntegrationTestBase :
    AbpIntegratedTest<BookStoreIntegrationTestModule>
{
    protected override SetAbpApplicationCreationOptions(
        AbpApplicationCreationOptions options)
    {
        options.UseTestDbContext();
    }

    protected override void SetAbpHostEnvironment(
        IHostEnvironment hostEnvironment)
    {
        hostEnvironment.EnvironmentName = "Test";
    }
}
```

### 14. 部署配置

#### 14.1 Docker 部署

```dockerfile
# src/BookStore.HttpApi.Host/Dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY bin/Release/net8.0/publish .
EXPOSE 80
ENTRYPOINT ["dotnet", "BookStore.HttpApi.Host.dll"]
```

```bash
# 构建 Docker 镜像
docker build -t bookstore-api:latest src/BookStore.HttpApi.Host

# 运行容器
docker run -d -p 8080:80 --name bookstore bookstore-api:latest
```

#### 14.2 Kubernetes 部署

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bookstore-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bookstore-api
  template:
    metadata:
      labels:
        app: bookstore-api
    spec:
      containers:
      - name: bookstore-api
        image: bookstore-api:latest
        ports:
        - containerPort: 80
        env:
        - name: ConnectionStrings__Default
          valueFrom:
            secretKeyRef:
              name: bookstore-secrets
              key: database-connection
```

### 15. 参考示例项目

| 项目 | 说明 | 源码 |
|------|------|------|
| EventHub | 完整的 DDD 参考应用，展示微服务架构 | [GitHub](https://github.com/abpframework/eventhub) |
| Easy CRM | 中型 CRM 应用，包含完整的业务逻辑 | [在线演示](http://easycrm.abp.io/) |
| Book Store | 基础 CRUD 教程应用 | [GitHub](https://github.com/abpframework/abp-samples/tree/master/BookStore-Mvc-EfCore) |
| ModularCRM | 模块化单体架构示例 | [GitHub](https://github.com/abpframework/abp-samples/tree/master/ModularCRM) |
| CMS Kit Demo | CMS Kit 模块演示 | [在线演示](https://cms-kit-demo.abpdemo.com/) |

## 常用命令速查

```bash
# ABP CLI 命令
abp help                          # 显示帮助
abp new <SolutionName>             # 创建新解决方案
abp update                         # 更新 ABP 相关包
abp add-module <ModuleName>        # 添加模块到解决方案

# 项目常用命令
dotnet restore                     # 还原依赖
dotnet build                       # 构建项目
dotnet test                        # 运行测试
dotnet ef migrations add <Name>    # 添加迁移
dotnet ef database update          # 应用迁移
dotnet run --project <ProjectPath> # 运行项目

# 创建不同类型的解决方案
abp new MyProject -t app -u mvc         # MVC Razor Pages
abp new MyProject -t app -u blazor     # Blazor
abp new MyProject -t app -u angular     # Angular
abp new MyProject -t microservice       # 微服务解决方案
abp new MyProject -t module             # 应用模块
```

## 高级主题

### 多租户配置

ABP vNext 内置多租户支持，只需简单配置即可启用。

```csharp
// 启用多租户数据过滤
public class Book : AuditedAggregateRoot<Guid>, IMultiTenant
{
    public Guid? TenantId { get; set; }
    public string Name { get; set; }
}

// 全局查询过滤器自动应用
// 所有查询自动过滤当前租户的数据
```

### 领域事件 vs 集成事件

```csharp
// 领域事件（同步，本地）
public class Order : AggregateRoot<Guid>
{
    public void AddItem(OrderItem item)
    {
        Items.Add(item);
        AddDomainEvent(new OrderItemAddedEvent(this, item));
    }
}

// 集成事件（异步，分布式）
public class OrderPlacedEvent : EventData
{
    public Guid OrderId { get; set; }
}

// 在应用层发布集成事件
public class OrderAppService
{
    private readonly IDistributedEventBus _eventBus;

    public async Task CreateOrderAsync(CreateOrderDto input)
    {
        var order = new Order(...);
        await _orderRepository.InsertAsync(order);

        await _eventBus.PublishAsync(new OrderPlacedEvent
        {
            OrderId = order.Id
        });
    }
}
```

### 数据过滤

```csharp
// 软删除过滤
public class Book : AuditedAggregateRoot<Guid>, ISoftDelete
{
    public bool IsDeleted { get; set; }
}

// 查询自动排除已删除记录
var books = await _bookRepository.GetListAsync();

// 禁用过滤（罕见场景）
using (_dataFilter.Disable<IMayHaveTenant>())
{
    var book = await _bookRepository.FindAsync(id);
}
```

## 参考资源

- [ABP 官方文档](https://abp.io/docs/latest)
- [ABP 框架源码](https://github.com/abpframework/abp)
- [ABP 社区](https://community.abp.io/)
- [ABP 示例项目](https://github.com/abpframework/abp-samples)
- [ABP 微服务模板文档](https://abp.io/docs/latest/solution-templates/microservice)
- [ Mastering ABP Framework](https://abp.io/books/mastering-abp-framework)
