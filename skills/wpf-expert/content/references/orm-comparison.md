# ORM 框架对比详解

## 1. Entity Framework Core

### 核心特性
```csharp
// Code First 模式
public class User
{
    public int Id { get; set; }
    public string Name { get; set; }
    public DateTime CreatedAt { get; set; }
    public ICollection<Order> Orders { get; set; }
}

public class ApplicationDbContext : DbContext
{
    public DbSet<User> Users { get; set; }

    protected override void OnConfiguring(
        DbContextOptionsBuilder optionsBuilder)
    {
        optionsBuilder.UseSqlServer(
            "ConnectionString",
            options => options.EnableRetryOnFailure());
    }
}
```

### 查询示例
```csharp
// 异步查询
var users = await _context.Users
    .Where(u => u.IsActive)
    .Include(u => u.Orders)
    .OrderByDescending(u => u.CreatedAt)
    .Skip(page * pageSize)
    .Take(pageSize)
    .ToListAsync();

// 批量操作
await _context.Users.AddRangeAsync(newUsers);
await _context.SaveChangesAsync();

// 追踪查询 vs 无追踪查询
var tracked = await _context.Users.FindAsync(id);
var readOnly = await _context.Users
    .AsNoTracking()
    .FirstOrDefaultAsync(u => u.Id == id);
```

## 2. Dapper

### 核心特性
```csharp
// 查询扩展方法
var user = await _connection
    .QueryFirstOrDefaultAsync<User>(
        "SELECT * FROM Users WHERE Id = @Id",
        new { Id = userId });

var users = await _connection
    .QueryAsync<User, Order, User>(
        @"SELECT u.*, o.* FROM Users u
          INNER JOIN Orders o ON u.Id = o.UserId
          WHERE u.IsActive = 1",
        (user, order) => { user.Order = order; return user; },
        splitOn: "Id");
```

### 批量操作
```csharp
// BulkCopy 实现
using var bulkCopy = new SqlBulkCopy(connection);
bulkCopy.DestinationTableName = "Users";
bulkCopy.BatchSize = 1000;

var table = new DataTable();
table.Columns.Add("Name", typeof(string));
// 填充数据...

await bulkCopy.WriteToServerAsync(table);
```

## 3. MyBatis.NET

### XML 配置
```xml
<!-- UserMapper.xml -->
<mapper namespace="UserMapper">
    <select id="FindById" resultType="User">
        SELECT * FROM Users WHERE Id = #{id}
    </select>

    <select id="FindActiveUsers" resultType="User">
        SELECT * FROM Users
        WHERE IsActive = 1
        ORDER BY CreatedAt DESC
    </select>

    <insert id="Insert" parameterType="User">
        INSERT INTO Users (Name, Email, CreatedAt)
        VALUES (#{name}, #{email}, #{createdAt})
        <selectKey keyProperty="id" resultType="int"
                   order="AFTER">
            SELECT LAST_INSERT_ID()
        </selectKey>
    </insert>

    <update id="Update" parameterType="User">
        UPDATE Users
        SET Name = #{name}, Email = #{email}
        WHERE Id = #{id}
    </update>
</mapper>
```

## 4. NHibernate

### 配置与映射
```csharp
// Fluent NHibernate 映射
public class UserMap : ClassMap<User>
{
    public UserMap()
    {
        Table("Users");
        Id(u => u.Id).GeneratedBy.Identity();
        Map(u => u.Name).Not.Nullable();
        Map(u => u.Email).Unique();
        HasMany(u => u.Orders)
            .Cascade.AllDeleteOrphan();
    }
}

// 查询示例
var users = session.QueryOver<User>()
    .Where(u => u.IsActive == true)
    .JoinQueryOver(u => u.Orders)
    .Where(o => o.Status == OrderStatus.Pending)
    .List();
```

## 5. PetaPoco

### 轻量级使用
```csharp
// 简单查询
var user = db.SingleOrDefault<User>(
    "SELECT * FROM Users WHERE Id = @0", id);

// 分页查询
var page = db.Page<User>(
    page: 1,
    pagesize: 10,
    sql: "SELECT * FROM Users WHERE IsActive = 1");
```

## ORM 选择决策树

```
开始
  │
  ├─ 是否需要复杂关联映射？
  │   ├─ 是 → EF Core / NHibernate
  │   └─ 否 → 继续
  │
  ├─ 是否追求极致性能？
  │   ├─ 是 → Dapper / ADO.NET
  │   └─ 否 → 继续
  │
  ├─ SQL 管理偏好？
  │   ├─ XML 配置 → MyBatis.NET
  │   ├─ 纯 SQL → Dapper
  │   └─ 全 ORM → EF Core / NHibernate
  │   │
  └─ 项目规模？
      ├─ 小型 → PetaPoco / Dapper
      ├─ 中型 → EF Core
      └─ 大型 → NHibernate / EF Core
```

## 性能对比

| 操作 | ADO.NET | Dapper | EF Core | NHibernate |
|------|---------|--------|---------|------------|
| 简单查询 | 100% | 95% | 70% | 65% |
| 复杂关联 | 100% | 90% | 60% | 55% |
| 批量插入 | 100% | 85% | 50% | 45% |
| 开发效率 | 低 | 中 | 高 | 高 |
| SQL 控制 | 完全 | 完全 | 部分 | 部分 |
