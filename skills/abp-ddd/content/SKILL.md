---
name: abp-ddd
description: ABP DDD (Domain Driven Design) - AggregateRoot, Entity, ValueObject, IRepository, Domain Service, Specification pattern. Use when creating entities, defining aggregate roots, implementing domain services, or working in Domain layer of ABP projects.
---

# ABP Domain Driven Design

> **Docs**: <https://abp.io/docs/latest/framework/architecture/ddd>

## Aggregate Root

Aggregate Root is the main entity that controls the aggregate.

```csharp
// BookStore.Domain/Books/Book.cs
public class Book : AuditedAggregateRoot<Guid>
{
    public string Name { get; private set; }
    public BookType Type { get; private set; }
    public DateTime PublishDate { get; private set; }
    public float Price { get; private set; }

    // Private constructor for ORM
    private Book() { }

    public Book(Guid id, string name, BookType type, DateTime publishDate, float price)
        : base(id)
    {
        Name = Check.NotNullOrWhiteSpace(name, nameof(name));
        Type = type;
        PublishDate = publishDate;
        Price = price;
    }

    // Domain methods
    public void SetName(string name)
    {
        Name = Check.NotNullOrWhiteSpace(name, nameof(name));
    }

    public void SetPrice(float price)
    {
        Price = Check.Range(price, nameof(price), 0, float.MaxValue);
    }
}
```

## Entity

Entities have unique identity and can be referenced by Aggregate Root.

```csharp
// BookStore.Domain/Books/BookReview.cs
public class BookReview : Entity<Guid>
{
    public Guid BookId { get; set; }
    public string Title { get; set; }
    public string Content { get; set; }
    public int Rating { get; set; } // 1-5

    public override object[] GetKeys()
    {
        return new object[] { Id };
    }
}
```

## Value Object

Value Objects are immutable and compared by their values.

```csharp
// BookStore.Domain/Books/Address.cs
public class Address : ValueObject
{
    public string Street { get; }
    public string City { get; }
    public string Country { get; }
    public string ZipCode { get; }

    public Address(string street, string city, string country, string zipCode)
    {
        Street = street;
        City = city;
        Country = country;
        ZipCode = zipCode;
    }

    protected override IEnumerable<object> GetAtomicValues()
    {
        yield return Street;
        yield return City;
        yield return Country;
        yield return ZipCode;
    }
}
```

## Repository Interface

Define repository in Domain layer, implement in Infrastructure layer.

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

    Task<Book> FindByNameAsync(string name);
}
```

## Domain Service

Domain services handle operations that don't belong to a single entity.

```csharp
// BookStore.Domain/Books/BookManager.cs
public class BookManager : DomainService
{
    private readonly IBookRepository _bookRepository;

    public BookManager(IBookRepository bookRepository)
    {
        _bookRepository = bookRepository;
    }

    public async Task<Book> CreateAsync(
        string name,
        BookType type,
        DateTime publishDate,
        float price)
    {
        // Check for duplicate name
        var existingBook = await _bookRepository.FindByNameAsync(name);
        if (existingBook != null)
        {
            throw new BusinessException("BookStore:BookNameAlreadyExists")
                .WithData("name", name);
        }

        return new Book(
            GuidGenerator.Create(),
            name,
            type,
            publishDate,
            price
        );
    }

    public async Task SetPriceAsync(Book book, float price)
    {
        if (price < 0)
        {
            throw new BusinessException("BookStore:PriceCannotBeNegative");
        }

        book.SetPrice(price);
    }
}
```

## Specification Pattern

Specifications are used to define reusable query logic.

```csharp
// BookStore.Domain/Books/Specifications/BookByTypeSpec.cs
public class BookByTypeSpec : Specification<Book>, ISingleResultSpecification<Book>
{
    public BookType Type { get; }

    public BookByTypeSpec(BookType type)
    {
        Type = type;
    }

    public override Expression<Func<Book, bool>> ToExpression()
    {
        return book => book.Type == Type;
    }
}

// Usage
var spec = new BookByTypeSpec(BookType.ScienceFiction);
var books = await _bookRepository.GetListAsync(spec);
```

## Enumeration

```csharp
// BookStore.Domain.Shared/Books/BookType.cs
public enum BookType : byte
{
    Undefined = 0,
    Adventure = 1,
    Biography = 2,
    Dystopia = 3,
    ScienceFiction = 4,
    Fantasy = 5
}
```

## Best Practices

1. **Aggregate Root controls access** - All changes to aggregate entities go through aggregate root
2. **Repository per Aggregate** - Only aggregate roots have repositories
3. **Domain Service for cross-entity operations** - Use domain services when operation spans multiple aggregates
4. **Value Objects for fixed concepts** - Use value objects for things like Address, Money, Email
5. **Domain events for side effects** - Publish domain events for state changes
6. **Private setters** - Use private setters with public methods for controlled mutation

## Domain Layer Project Structure

```
*.Domain/
├── Books/
│   ├── Book.cs              # Aggregate Root
│   ├── BookReview.cs        # Entity (child)
│   ├── Address.cs           # Value Object
│   ├── IBookRepository.cs   # Repository interface
│   ├── BookManager.cs       # Domain Service
│   └── Specifications/      # Specifications
├── Authors/
│   └── Author.cs
├── *.Domain.csproj
└── DomainModule.cs
```
