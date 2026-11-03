---
name: dotnet-orm-entity-framework
description: 掌握 .NET ORM 和 Entity Framework 开发技能。当用户要求进行数据库操作、Entity Framework 配置、LINQ 查询、迁移管理、或需要实现 Repository/Unit of Work 模式时使用。
---

# Entity Framework 开发技能

## 核心技能清单

| 技能项 | 熟练度 | 说明 |
|-------|-------|------|
| EF Core 基础 | ⭐⭐⭐⭐⭐ | DbContext、配置、查询 |
| LINQ 查询 | ⭐⭐⭐⭐⭐ | 表达式、延迟执行 |
| 迁移管理 | ⭐⭐⭐⭐⭐ | Add-Migration、Update-Database |
| 关系映射 | ⭐⭐⭐⭐⭐ | 一对多、多对多、继承 |
| 乐观/悲观锁 | ⭐⭐⭐⭐ | 并发控制 |
| 批量操作 | ⭐⭐⭐⭐ | BulkInsert、ExecuteSql |

## Entity Framework Core 基础

### DbContext 配置

```csharp
// 基础 DbContext
public class AppDbContext : DbContext
{
    public DbSet<Order> Orders { get; set; }
    public DbSet<Customer> Customers { get; set; }
    public DbSet<Product> Products { get; set; }

    protected override void OnConfiguring(
        DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder.UseSqlServer(
            "ConnectionString",
            options => options.EnableRetryOnFailure());
    }

    protected override void OnModelCreating(
        ModelBuilder modelBuilder)
    {
        // 配置实体
    }
}
```

### 连接字符串配置

```csharp
// Program.cs
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(
        builder.Configuration.GetConnectionString("Default"),
        sqlOptions =>
        {
            sqlOptions.EnableRetryOnFailure(
                maxRetryCount: 3,
                maxRetryDelay: TimeSpan.FromSeconds(10),
                errorNumbersToAdd: null);
            sqlOptions.CommandTimeout(30);
        }));

// 使用
public class OrderService
{
    private readonly AppDbContext _context;

    public OrderService(AppDbContext context)
    {
        _context = context;
    }
}
```

## LINQ 查询

### 基础查询

```csharp
// 查询所有
var orders = await _context.Orders.ToListAsync();

// 条件查询
var activeOrders = await _context.Orders
    .Where(o => o.Status == OrderStatus.Active)
    .Where(o => o.CreatedAt > DateTime.UtcNow.AddDays(-7))
    .ToListAsync();

// 延迟执行
var query = _context.Orders.Where(o => o.IsActive);
query = query.OrderBy(o => o.CreatedAt);
var results = await query.ToListAsync();
```

### 投影查询

```csharp
// 投影到 DTO
var orderDtos = await _context.Orders
    .Where(o => o.Id == orderId)
    .Select(o => new OrderDto
    {
        Id = o.Id,
        CustomerName = o.Customer.Name,
        TotalAmount = o.Items.Sum(i => i.Quantity * i.UnitPrice),
        ItemCount = o.Items.Count
    })
    .FirstOrDefaultAsync();

// 匿名对象
var results = await _context.Products
    .Select(p => new 
    {
        p.Name,
        p.Price,
        Category = p.Category.Name
    })
    .ToListAsync();
```

### 关联查询

```csharp
// Include 预加载
var order = await _context.Orders
    .Include(o => o.Customer)
    .Include(o => o.Items)
        .ThenInclude(i => i.Product)
    .FirstOrDefaultAsync(o => o.Id == id);

// ThenInclude 多层
var orders = await _context.Orders
    .Include(o => o.Customer)
        .ThenInclude(c => c.Address)
    .Where(o => o.Status == OrderStatus.Pending)
    .ToListAsync();

// 显式加载
var order = await _context.Orders.FindAsync(id);
if (!order.Customer.IsLoaded())
{
    await _context.Entry(order)
        .Reference(o => o.Customer)
        .LoadAsync();
}
```

### 聚合查询

```csharp
// 分组统计
var stats = await _context.Orders
    .GroupBy(o => o.Status)
    .Select(g => new
    {
        Status = g.Key,
        Count = g.Count(),
        TotalAmount = g.Sum(o => o.TotalAmount)
    })
    .ToListAsync();

// 分页
var page = 1;
var pageSize = 10;
var pagedOrders = await _context.Orders
    .OrderBy(o => o.CreatedAt)
    .Skip((page - 1) * pageSize)
    .Take(pageSize)
.ToListAsync();

// 数量统计
var count = await _context.Orders.CountAsync();
var pendingCount = await _context.Orders
    .CountAsync(o => o.Status == OrderStatus.Pending);
```

## 关系映射

### 一对多关系

```csharp
public class Order
{
    public int Id { get; set; }
    public int CustomerId { get; set; }
    public Customer Customer { get; set; }
    public List<OrderItem> Items { get; set; }
}

public class Customer
{
    public int Id { get; set; }
    public string Name { get; set; }
    public List<Order> Orders { get; set; }
}

// Fluent API 配置
modelBuilder.Entity<Order>()
    .HasOne(o => o.Customer)
    .WithMany(c => c.Orders)
    .HasForeignKey(o => o.CustomerId)
    .OnDelete(DeleteBehavior.Restrict);
```

### 多对多关系

```csharp
public class Student
{
    public int Id { get; set; }
    public string Name { get; set; }
    public List<Course> Courses { get; set; }
}

public class Course
{
    public int Id { get; set; }
    public string Name { get; set; }
    public List<Student> Students { get; set; }
}

// EF Core 自动创建联接表
modelBuilder.Entity<Student>()
    .HasMany(s => s.Courses)
    .WithMany(c => c.Students)
    .UsingEntity<Enrollment>(
        j => j.HasOne(e => e.Course).WithMany(c => c.Enrollments),
        j => j.HasOne(e => e.Student).WithMany(s => s.Enrollments),
        j => j.HasKey(e => new { e.StudentId, e.CourseId }));
```

### 继承映射

```csharp
// TPT (Table Per Type)
modelBuilder.Entity<Animal>().ToTable("Animals");
modelBuilder.Entity<Dog>().ToTable("Dogs");
modelBuilder.Entity<Cat>().ToTable("Cats");

// TPH (Table Per Hierarchy) - 默认
public abstract class Payment
{
    public int Id { get; set; }
    public decimal Amount { get; set; }
}

public class CreditCardPayment : Payment
{
    public string CardNumber { get; set; }
}

public class BankTransferPayment : Payment
{
    public string BankAccount { get; set; }
}

// TPC (Table Per Concrete)
modelBuilder.Entity<Dog>().ToTable("Dogs");
modelBuilder.Entity<Cat>().ToTable("Cats");
```

## 迁移管理

### 包管理器命令

```powershell
# 安装工具
dotnet tool install --global dotnet-ef

# 添加迁移
dotnet ef migrations add InitialCreate

# 添加命名迁移
dotnet ef migrations add AddOrderStatus -o Data/Migrations

# 更新数据库
dotnet ef database update

# 更新到指定版本
dotnet ef database update 20240101_AddOrderTable

# 生成脚本
dotnet ef migrations script -o migration.sql

# 移除上次迁移
dotnet ef migrations remove
```

### 迁移类结构

```csharp
public partial class InitialCreate : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.CreateTable(
            name: "Customers",
            columns: table => new
            {
                Id = table.Column<int>(type: "int", nullable: false)
                    .Annotation("SqlServer:Identity", "1, 1"),
                Name = table.Column<string>(type: "nvarchar(max)", nullable: false),
                Email = table.Column<string>(type: "nvarchar(max)", nullable: false)
            },
            constraints: table =>
            {
                table.PrimaryKey("PK_Customers", x => x.Id);
            });
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DropTable(name: "Customers");
    }
}
```

### 数据种子

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Customer>().HasData(
        new Customer { Id = 1, Name = "John", Email = "john@example.com" },
        new Customer { Id = 2, Name = "Jane", Email = "jane@example.com" }
    );

    modelBuilder.Entity<Product>().HasData(
        new { Id = 1, Name = "Product A", Price = 9.99m, CategoryId = 1 },
        new { Id = 2, Name = "Product B", Price = 19.99m, CategoryId = 1 }
    );
}
```

## 并发控制

### 乐观并发

```csharp
public class Order
{
    public int Id { get; set; }
    public decimal Total { get; set; }
    
    [ConcurrencyCheck]
    public byte[] RowVersion { get; set; }
}

// 配置
modelBuilder.Entity<Order>()
    .Property(o => o.RowVersion)
    .IsRowVersion();

// 使用
public async Task UpdateOrder(Order order)
{
    try
    {
        _context.Orders.Update(order);
        await _context.SaveChangesAsync();
    }
    catch (DbUpdateConcurrencyException ex)
    {
        // 处理并发冲突
        var entry = ex.Entries.Single();
        var currentValues = entry.CurrentValues;
        var dbValues = await entry.GetDatabaseValuesAsync();
        
        // 合并变更
        entry.OriginalValues.SetValues(dbValues);
        await _context.SaveChangesAsync();
    }
}
```

### 显式事务

```csharp
using var transaction = await _context.Database.BeginTransactionAsync();
try
{
    var order = new Order { CustomerId = 1 };
    _context.Orders.Add(order);
    await _context.SaveChangesAsync();

    var inventory = await _context.Inventory
        .FirstAsync(i => i.ProductId == productId);
    inventory.Quantity -= quantity;
    await _context.SaveChangesAsync();

    await transaction.CommitAsync();
}
catch (Exception)
{
    await transaction.RollbackAsync();
    throw;
}
```

## Repository & Unit of Work

### 泛型仓储

```csharp
public interface IRepository<T> where T : class
{
    Task<T> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    IQueryable<T> Query();
    Task AddAsync(T entity);
    void Update(T entity);
    void Delete(T entity);
}

public class Repository<T> : IRepository<T> where T : class
{
    protected readonly DbContext _context;
    protected readonly DbSet<T> _dbSet;

    public Repository(DbContext context)
    {
        _context = context;
        _dbSet = context.Set<T>();
    }

    public async Task<T> GetByIdAsync(int id) =>
        await _dbSet.FindAsync(id);

    public async Task<IEnumerable<T>> GetAllAsync() =>
        await _dbSet.ToListAsync();

    public IQueryable<T> Query() => _dbSet;

    public async Task AddAsync(T entity) =>
        await _dbSet.AddAsync(entity);

    public void Update(T entity) =>
        _dbSet.Update(entity);

    public void Delete(T entity) =>
        _dbSet.Remove(entity);
}
```

### Unit of Work

```csharp
public interface IUnitOfWork : IDisposable
{
    IRepository<Order> Orders { get; }
    IRepository<Customer> Customers { get; }
    Task<int> SaveChangesAsync();
}

public class UnitOfWork : IUnitOfWork
{
    private readonly AppDbContext _context;
    private IRepository<Order> _orders;
    private IRepository<Customer> _customers;

    public UnitOfWork(AppDbContext context)
    {
        _context = context;
    }

    public IRepository<Order> Orders =>
        _orders ??= new Repository<Order>(_context);

    public IRepository<Customer> Customers =>
        _customers ??= new Repository<Customer>(_context);

    public async Task<int> SaveChangesAsync() =>
        await _context.SaveChangesAsync();

    public void Dispose() => _context.Dispose();
}
```
