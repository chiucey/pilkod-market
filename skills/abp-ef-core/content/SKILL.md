---
name: abp-ef-core
description: ABP Entity Framework Core - DbContext, entity configuration, EfCoreRepository implementation, migrations (dotnet ef migrations add), data seeding. Use when working in EntityFrameworkCore projects, adding migrations, or implementing EF Core repositories.
---

# ABP Entity Framework Core

> **Docs**: <https://docs.abp.io/en/latest/Entity-Framework-Core>

## Never Do

| Don't | Do Instead |
| --- | --- |
| Skip `ConfigureByConvention()` | Always call it first |
| `AddDefaultRepositories(includeAllEntities: true)` | Use `AddDefaultRepositories()` only for aggregate roots |
| Inject `DbContext` in application/domain services | Use `IRepository` or custom repository interface |
| Use `DbContext` outside EF Core project | Access via `GetDbContextAsync()` inside repository only |

## DbContext Configuration

```csharp
// BookStore.EntityFrameworkCore/BookStoreDbContext.cs
[ConnectionStringName("Default")]
public class BookStoreDbContext : AbpDbContext<BookStoreDbContext>
{
    public DbSet<Book> Books { get; set; }
    public DbSet<Author> Authors { get; set; }
    public DbSet<BookReview> BookReviews { get; set; }

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
```

## Entity Configuration Extensions

```csharp
// BookStore.EntityFrameworkCore/BookStoreDbContextModelCreatingExtensions.cs
public static class BookStoreDbContextModelCreatingExtensions
{
    public static void ConfigureBookStore(this ModelBuilder builder)
    {
        Check.NotNull(builder, nameof(builder));

        builder.Entity<Book>(b =>
        {
            b.ToTable("Books", "bookstore");

            b.ConfigureByConvention();

            // Property configurations
            b.Property(x => x.Name).IsRequired().HasMaxLength(128);
            b.Property(x => x.Price).HasColumnType("decimal(18,2)");

            // Indexes
            b.HasIndex(x => x.Name);
            b.HasIndex(x => new { x.AuthorId, x.Type });

            // Relationships
            b.HasOne(x => x.Author)
                .WithMany(x => x.Books)
                .HasForeignKey(x => x.AuthorId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        builder.Entity<Author>(b =>
        {
            b.ToTable("Authors", "bookstore");
            b.ConfigureByConvention();

            b.Property(x => x.Name).IsRequired().HasMaxLength(256);
            b.Property(x => x.ShortBio).HasMaxLength(1000);
        });
    }
}
```

## DbContext Factory

```csharp
// BookStore.EntityFrameworkCore/BookStoreDbContextFactory.cs
public class BookStoreDbContextFactory : IDesignTimeDbContextFactory<BookStoreDbContext>
{
    public BookStoreDbContext CreateDbContext(string[] args)
    {
        var configuration = BuildConfiguration();
        var builder = new DbContextOptionsBuilder<BookStoreDbContext>();
        builder.UseSqlServer(configuration.GetConnectionString("Default"));
        return new BookStoreDbContext(builder.Options);
    }

    private static IConfigurationRoot BuildConfiguration()
    {
        var builder = new ConfigurationBuilder();
        builder.SetBasePath(Path.Combine(Directory.GetCurrentDirectory(), ".."));
        builder.AddJsonFile("appsettings.json");
        return builder.Build();
    }
}
```

## Repository Implementation

```csharp
// BookStore.EntityFrameworkCore/Books/EfCoreBookRepository.cs
public class EfCoreBookRepository : EfCoreRepository<BookStoreDbContext, Book>, IBookRepository
{
    public EfCoreBookRepository(IDbContextProvider<BookStoreDbContext> dbContextProvider)
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

    public async Task<List<Book>> GetListByAuthorAsync(Guid authorId, bool includeDetails = false)
    {
        var dbSet = await GetDbSetAsync();

        return await dbSet
            .IncludeDetails(includeDetails)
            .Where(b => b.AuthorId == authorId)
            .ToListAsync();
    }

    public override async Task<List<Book>> WithDetailsAsync()
    {
        return (await GetQueryableAsync())
            .Include(b => b.Author)
            .Include(b => b.Reviews)
            .ToList();
    }
}
```

## IncludeDetails Extension

```csharp
// BookStore.EntityFrameworkCore/Books/BookEfCoreQueryableExtensions.cs
public static class BookEfCoreQueryableExtensions
{
    public static IQueryable<Book> IncludeDetails(this IQueryable<Book> queryable, bool include = true)
    {
        if (!include)
        {
            return queryable;
        }

        return queryable
            .Include(b => b.Author)
            .Include(b => b.Reviews);
    }
}
```

## Module Configuration

```csharp
// BookStore.EntityFrameworkCore/BookStoreEntityFrameworkCoreModule.cs
[DependsOn(typeof(AbpEntityFrameworkCoreModule))]
public class BookStoreEntityFrameworkCoreModule : AbpModule
{
    public override void ConfigureServices(ServiceConfigurationContext context)
    {
        context.Services.AddAbpDbContext<BookStoreDbContext>(options =>
        {
            // Add default repositories for aggregate roots only (DDD best practice)
            options.AddDefaultRepositories();
        });

        Configure<AbpDbContextConfigurationOptions>(options =>
        {
            options.UseSqlServer();
        });
    }
}
```

## Migration Commands

```bash
# Navigate to EF Core project
cd src/MyProject.EntityFrameworkCore

# Add migration
dotnet ef migrations add MigrationName

# Apply migration (choose one):
dotnet run --project ../MyProject.DbMigrator # Recommended - also seeds data
dotnet ef database update # EF Core command only

# Remove last migration (if not applied)
dotnet ef migrations remove

# Generate SQL script
dotnet ef migrations script

# Generate script with migrations range
dotnet ef migrations script -o script.sql --from Migration1 --to Migration2
```

## Data Seeding

```csharp
// BookStore.Domain/Data/BookStoreDataSeederContributor.cs
public class BookStoreDataSeederContributor : IDataSeedContributor, ITransientDependency
{
    private readonly IRepository<Book, Guid> _bookRepository;
    private readonly IRepository<Author, Guid> _authorRepository;
    private readonly IGuidGenerator _guidGenerator;

    public BookStoreDataSeederContributor(
        IRepository<Book, Guid> bookRepository,
        IRepository<Author, Guid> authorRepository,
        IGuidGenerator guidGenerator)
    {
        _bookRepository = bookRepository;
        _authorRepository = authorRepository;
        _guidGenerator = guidGenerator;
    }

    public async Task SeedAsync(DataSeedContext context)
    {
        if (await _bookRepository.GetCountAsync() > 0)
        {
            return;
        }

        // Seed authors
        var author = new Author(_guidGenerator.Create(), "John Doe", "Fiction writer");
        await _authorRepository.InsertAsync(author, autoSave: true);

        // Seed books
        var book = new Book(
            _guidGenerator.Create(),
            "Sample Book",
            BookType.ScienceFiction,
            DateTime.Now,
            19.99f,
            author.Id
        );
        await _bookRepository.InsertAsync(book, autoSave: true);
    }
}
```

## Performance Tips

1. **Add explicit indexes** for frequently queried fields
2. **Use `AsNoTracking()`** for read-only queries
3. **Avoid N+1 queries** with `.Include()` or specifications
4. **Use `GetCancellationToken()`** in async methods
5. **Consider query splitting** for complex queries with multiple collections
