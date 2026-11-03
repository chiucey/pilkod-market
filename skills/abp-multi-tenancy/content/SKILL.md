---
name: abp-multi-tenancy
description: ABP Multi-Tenancy - IMultiTenant, CurrentTenant, TenantResolver, Data Filtering, Tenant Management. Use when implementing multi-tenant features, tenant isolation, or SaaS applications in ABP.
---

# ABP Multi-Tenancy

> **Docs**: <https://abp.io/docs/latest/framework/fundamentals/multi-tenancy>

## Overview

ABP has built-in multi-tenancy support with automatic data filtering based on the current tenant.

## Enable Multi-Tenancy

```csharp
// Host side - typically enabled by default
// Tenant side - inherit from tenant settings
```

## IMultiTenant Interface

```csharp
public class Book : AuditedAggregateRoot<Guid>, IMultiTenant
{
    public Guid? TenantId { get; set; }

    public string Name { get; set; }
    public float Price { get; set; }

    // Navigation property
    [ForeignKey(nameof(TenantId))]
    public virtual Tenant Tenant { get; set; }
}
```

## Current Tenant

### Access Current Tenant

```csharp
public class BookAppService : ApplicationService
{
    public async Task DoSomethingAsync()
    {
        // Current tenant ID
        var tenantId = CurrentTenant.Id;

        // Current tenant name
        var tenantName = CurrentTenant.Name;

        // Check if current user is host
        var isHost = CurrentTenant.Id == null;
    }
}
```

### Change Tenant Temporarily

```csharp
public class MyService : ApplicationService
{
    public async Task ProcessForTenantAsync(Guid targetTenantId)
    {
        using (CurrentTenant.Change(targetTenantId, "Target Tenant Name"))
        {
            // All operations here use the target tenant
            var books = await _bookRepository.GetListAsync();
        }

        // After using block, returns to original tenant
    }
}
```

## Data Filtering

ABP automatically filters data based on `TenantId`:

```csharp
// Query is automatically filtered by current tenant
var books = await _bookRepository.GetListAsync();

// Generates: WHERE TenantId = 'current-tenant-id'
```

### Disable Filtering

```csharp
public class MyService : ApplicationService
{
    public async Task GetGlobalBooksAsync()
    {
        using (CurrentTenant.Change(null))
        {
            // Query all books across all tenants
            var books = await _bookRepository.GetListAsync();
        }
    }
}
```

## Tenant Resolution

ABP resolves tenant from multiple sources:

### Order of Resolution

1. **Claim** - `abp.TenantId` claim in JWT token
2. **Query String** - `__tenant` query string parameter
3. **Header** - `__tenant` header
4. **Cookie** - `Abp.TenantId` cookie

### Configuration

```csharp
// Configure tenant resolution
public override void ConfigureServices(ServiceConfigurationContext context)
{
    Configure<AbpTenantResolveOptions>(options =>
    {
        options.AddTenantResolver(new ClaimTenantResolver());
        options.AddTenantResolver(new QueryStringTenantResolver());
    });
}
```

## Tenant Management

### Create Tenant

```csharp
public class TenantAppService : ApplicationService
{
    private readonly TenantManager _tenantManager;

    public TenantAppService(TenantManager tenantManager)
    {
        _tenantManager = tenantManager;
    }

    public async Task<TenantDto> CreateAsync(CreateTenantDto input)
    {
        var tenant = await _tenantManager.CreateAsync(input.Name);

        if (!input.AdminEmail.IsNullOrWhiteSpace())
        {
            await _tenantManager.CreateAdminAsync(
                tenant.Id,
                input.AdminEmail,
                input.AdminPassword
            );
        }

        await CurrentUnitOfWork.SaveChangesAsync();

        return ObjectMapper.Map<Tenant, TenantDto>(tenant);
    }
}
```

### Switch Tenant

```csharp
public class TenantSwitchService : ApplicationService
{
    public async Task SwitchToTenantAsync(Guid tenantId)
    {
        var tenant = await TenantManager.FindByIdAsync(tenantId);
        if (tenant == null)
        {
            throw new UserFriendlyException("Tenant not found");
        }

        using (CurrentTenant.Change(tenant.Id, tenant.Name))
        {
            // Perform operations in tenant context
        }
    }
}
```

## Connection Strings

### Per-Tenant Connection Strings

```csharp
// Set connection string for tenant
public class TenantAppService : ApplicationService
{
    private readonly ITenantRepository _tenantRepository;

    public async Task SetConnectionStringAsync(Guid tenantId, string connectionString)
    {
        var tenant = await _tenantRepository.GetAsync(tenantId);
        tenant.SetConnectionString(connectionString);
        await _tenantRepository.UpdateAsync(tenant);
    }
}
```

### Resolve Connection String

```csharp
// DefaultDbContext: uses IConnectionStringResolver
public class MyProjectDbContext : AbpDbContext<MyProjectDbContext>
{
    // Uses current tenant's connection string by default
}

public class GlobalDbContext : AbpDbContext<GlobalDbContext>
{
    public GlobalDbContext(DbContextOptions<GlobalDbContext> options)
        : base(options)
    {
    }

    protected override bool IsMultiTenantFilterEnabled()
    {
        return false; // Host-level database
    }
}
```

## Authorization

### Host vs Tenant Permissions

```csharp
public class BookStorePermissionDefinitionProvider : PermissionDefinitionProvider
{
    public override void Define(IPermissionDefinitionContext context)
    {
        var hostGroup = context.AddGroup("BookStore.Host");
        hostGroup.AddPermission("BookStore.Host.Manage");

        var tenantGroup = context.AddGroup("BookStore.Tenant");
        tenantGroup.AddPermission("BookStore.Tenant.Manage")
            .MultiTenancySide(MultiTenancySides.Tenant);
    }
}
```

### Permission Options

```csharp
MultiTenancySides.Host      // Only available to host
MultiTenancySides.Tenant    // Only available to tenants
MultiTenancySides.Both       // Available to both (default)
```

## Multi-Tenant Entities

### Base Classes

```csharp
// Multi-tenant entity
public class Book : AuditedAggregateRoot<Guid>, IMultiTenant
{
    public Guid? TenantId { get; set; }
    public string Name { get; set; }
}

// Host-only entity (no filtering)
public class TenantSetting : Entity<Guid>, IMayHaveTenant
{
    public Guid? TenantId { get; set; } // May be null = host setting
    public string Name { get; set; }
}

// Always tenant entity (throws if not in tenant context)
public class TenantBook : AuditedAggregateRoot<Guid>, IMultiTenant
{
    public Guid TenantId { get; set; } // Non-nullable
}
```

## Testing Multi-Tenancy

```csharp
public class BookAppService_Tests : BookStoreApplicationTestBase
{
    [Fact]
    public async Task Should_Filter_Books_By_Tenant()
    {
        // Arrange
        var tenant1Books = await _bookRepository.GetListAsync();
        using (CurrentTenant.Change(TestData.Tenant1Id))
        {
            var tenant2Books = await _bookRepository.GetListAsync();

            // Assert
            tenant1Books.ShouldNotBeEquivalent(tenant2Books);
        }
    }

    [Fact]
    public async Task Should_Get_All_Books_When_Switched_To_Host()
    {
        using (CurrentTenant.Change(null)) // Switch to host
        {
            var allBooks = await _bookRepository.GetListAsync();
            allBooks.Count.ShouldBeGreaterThan(0);
        }
    }
}
```

## Data Seeding Per Tenant

```csharp
public class TenantDataSeeder : IDataSeedContributor, ITransientDependency
{
    public async Task SeedAsync(DataSeedContext context)
    {
        var tenantId = context.TenantId;

        if (tenantId == null)
        {
            // Host-level data
            await SeedHostDataAsync();
        }
        else
        {
            // Tenant-specific data
            await SeedTenantDataAsync(tenantId.Value);
        }
    }
}
```

## Best Practices

1. **Always include TenantId** in multi-tenant entities
2. **Use `IMultiTenant` base interface** for automatic filtering
3. **Be careful with cross-tenant operations** - Use `CurrentTenant.Change()`
4. **Separate host and tenant data** - Use different databases or schemas
5. **Test with multiple tenants** - Ensure proper isolation
6. **Handle tenant resolution failures** - Return 404 or redirect
