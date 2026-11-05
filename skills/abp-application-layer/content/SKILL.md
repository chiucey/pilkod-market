---
name: abp-application-layer
description: ABP Application Layer - Application Service, DTO (Data Transfer Object), CrudAppService, AutoMapper, Object Mapping. Use when implementing application services, creating DTOs, or working in Application layer of ABP projects.
---

# ABP Application Layer

> **Docs**: <https://abp.io/docs/latest/framework/architecture/ddd/application-layer>

## DTO Classes

### Entity DTO

```csharp
// BookStore.Application.Contracts/Books/BookDto.cs
public class BookDto : AuditedEntityDto<Guid>
{
    public string Name { get; set; }
    public BookType Type { get; set; }
    public DateTime PublishDate { get; set; }
    public float Price { get; set; }
    public Guid AuthorId { get; set; }
    public string AuthorName { get; set; }
}
```

### Creation DTO

```csharp
// BookStore.Application.Contracts/Books/CreateUpdateBookDto.cs
public class CreateUpdateBookDto : AuditedEntityDto<Guid?>
{
    [Required]
    [StringLength(128)]
    public string Name { get; set; }

    public BookType Type { get; set; }

    public DateTime PublishDate { get; set; }

    [Range(0, float.MaxValue)]
    public float Price { get; set; }

    public Guid AuthorId { get; set; }
}
```

### List DTO (Paged)

```csharp
// BookStore.Application.Contracts/Books/BookListDto.cs
public class BookListDto : EntityDto<Guid>
{
    public string Name { get; set; }
    public BookType Type { get; set; }
    public float Price { get; set; }
    public bool IsAvailable { get; set; }
}
```

### Custom Query DTO

```csharp
public class GetBookListInput : PagedAndSortedResultRequestDto, IShouldNormalize
{
    public string Filter { get; set; }

    public Guid? AuthorId { get; set; }

    public BookType? Type { get; set; }

    public void Normalize()
    {
        if (string.IsNullOrEmpty(Sorting))
        {
            Sorting = "Name";
        }
    }
}
```

## Application Service Interface

```csharp
// BookStore.Application.Contracts/Books/IBookAppService.cs
public interface IBookAppService :
    ICrudAppService<        // Implements standard CRUD
        BookDto,            // Output DTO
        Guid,               // Primary key type
        GetBookListInput,   // List request DTO
        CreateUpdateBookDto // Create/Update DTO
    >
{
    // Custom methods beyond CRUD
    Task<List<BookDto>> GetBooksByAuthorAsync(Guid authorId);
    Task<BookDto> GetBookWithDetailsAsync(Guid id);
    Task<int> GetBookCountAsync();
}
```

## Application Service Implementation

```csharp
// BookStore.Application/Books/BookAppService.cs
public class BookAppService :
    CrudAppService<Book, BookDto, Guid, GetBookListInput, CreateUpdateBookDto>,
    IBookAppService
{
    private readonly IBookRepository _bookRepository;
    private readonly BookManager _bookManager;

    public BookAppService(
        IRepository<Book, Guid> repository,
        IBookRepository bookRepository,
        BookManager bookManager)
        : base(repository)
    {
        _bookRepository = bookRepository;
        _bookManager = bookManager;
    }

    // Override base methods for custom logic
    public override async Task<BookDto> CreateAsync(CreateUpdateBookDto input)
    {
        await _bookManager.CheckNameAsync(input.Name);

        var book = await _bookManager.CreateAsync(
            input.Name,
            input.Type,
            input.PublishDate,
            input.Price,
            input.AuthorId
        );

        await _bookRepository.InsertAsync(book);

        return ObjectMapper.Map<Book, BookDto>(book);
    }

    // Custom method
    public async Task<List<BookDto>> GetBooksByAuthorAsync(Guid authorId)
    {
        var books = await _bookRepository.GetListByAuthorAsync(authorId);
        return ObjectMapper.Map<List<Book>, List<BookDto>>(books);
    }

    // Query with specification
    protected override async Task<IQueryable<Book>> CreateFilteredQueryAsync(GetBookListInput input)
    {
        return (await _bookRepository.GetQueryableAsync())
            .WhereIf(!input.Filter.IsNullOrWhiteSpace(), b => b.Name.Contains(input.Filter))
            .WhereIf(input.AuthorId.HasValue, b => b.AuthorId == input.AuthorId)
            .WhereIf(input.Type.HasValue, b => b.Type == input.Type);
    }
}
```

## AutoMapper Configuration

```csharp
// BookStore.Application/Books/BookMapperProfile.cs
public class BookMapperProfile : Profile
{
    public BookMapperProfile()
    {
        // Entity to DTO
        CreateMap<Book, BookDto>();
        CreateMap<Book, BookListDto>();

        // DTO to Entity
        CreateMap<CreateUpdateBookDto, Book>();
    }
}

// BookStore.Application/BookStoreApplicationModule.cs
[DependsOn(typeof(AbpAutoMapperModule))]
public class BookStoreApplicationModule : AbpModule
{
    public override void ConfigureServices(ServiceConfigurationContext context)
    {
        Configure<AbpAutoMapperOptions>(options =>
        {
            options.AddMaps<BookStoreApplicationModule>();
            // Or add specific profiles
            // options.AddProfile<BookMapperProfile>();
        });
    }
}
```

## Unit of Work

ABP uses Unit of Work pattern automatically. Configure per method:

```csharp
public class BookAppService : ApplicationService
{
    [UnitOfWork] // Default: read-write
    public async Task CreateWithUowAsync(CreateUpdateBookDto input)
    {
        // Changes are committed at the end
    }

    [UnitOfWork(isTransactional: false)] // Read-only
    public async Task<BookDto> GetBookReadOnlyAsync(Guid id)
    {
        return await Repository.FirstOrDefaultAsync(id);
    }
}
```

## Application Layer Project Structure

```
*.Application/
├── Books/
│   ├── BookAppService.cs         # Implementation
│   └── BookMapperProfile.cs      # AutoMapper profile
├── Authors/
│   └── AuthorAppService.cs
├── *.Application.csproj
└── ApplicationModule.cs

*.Application.Contracts/
├── Books/
│   ├── IBookAppService.cs        # Interface
│   ├── BookDto.cs                # Output DTO
│   ├── BookListDto.cs            # List DTO
│   └── CreateUpdateBookDto.cs     # Input DTO
├── Authors/
│   └── IAuthorAppService.cs
└── *.Application.Contracts.csproj
```

## Best Practices

1. **DTOs are input/output contracts** - Never expose entities directly to presentation layer
2. **Application service is transaction boundary** - Each method typically runs in one transaction
3. **Use `ObjectMapper` consistently** - Don't manually map unless necessary
4. **Validate input in DTO** - Use data annotations for basic validation
5. **Return appropriate DTOs** - Don't return full entity for lists, use specialized list DTOs
6. **Async suffix** - All async methods should end with `Async`
