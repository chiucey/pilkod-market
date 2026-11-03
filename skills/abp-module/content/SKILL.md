---
name: abp-module
description: ABP Module Development - Module dependencies, Plug-In modules, Module extension, Module Communication. Use when creating reusable modules or extending ABP framework modules.
---

# ABP Module Development

> **Docs**: <https://abp.io/docs/latest/framework/fundamentals/modularity>

## Module Structure

```
Acme.BookStore/
├── src/
│   ├── Acme.BookStore.Domain/
│   │   ├── DomainModule.cs
│   │   └── ...
│   ├── Acme.BookStore.Application/
│   ├── Acme.BookStore.HttpApi/
│   ├── Acme.BookStore.EntityFrameworkCore/
│   └── Acme.BookStore.HttpApi.Host/
└── test/
```

## Module Classes

### Domain Module

```csharp
// Acme.BookStore.Domain/AcmeBookStoreDomainModule.cs
[DependsOn(
    typeof(AbpDddDomainModule),
    typeof(AbpValidationModule)
)]
public class AcmeBookStoreDomainModule : AbpModule
{
    public override void ConfigureServices(ServiceConfigurationContext context)
    {
        Configure<AbpAutoMapperOptions>(options =>
        {
            options.AddProfile<AcmeBookStoreDomainMappingProfile>();
        });

        Configure<AbpMultiTenancyOptions>(options =>
        {
            options.IsEnabled = true;
        });
    }
}
```

### Application Module

```csharp
// Acme.BookStore.Application/AcmeBookStoreApplicationModule.cs
[DependsOn(
    typeof(AcmeBookStoreDomainModule),
    typeof(AbpAspNetCoreMvcModule),
    typeof(AbpAutofacModule)
)]
public class AcmeBookStoreApplicationModule : AbpModule
{
    public override void ConfigureServices(ServiceConfigurationContext context)
    {
        Configure<AbpAutoMapperOptions>(options =>
        {
            options.AddProfile<AcmeBookStoreApplicationMapperProfile>();
        });

        Configure<AbpPermissionOptions>(options =>
        {
            options.DefinitionProviders.Add<BookStorePermissionDefinitionProvider>();
        });
    }
}
```

### HTTP API Module

```csharp
// Acme.BookStore.HttpApi/AcmeBookStoreHttpApiModule.cs
[DependsOn(
    typeof(AcmeBookStoreApplicationModule)
)]
public class AcmeBookStoreHttpApiModule : AbpModule
{
    public override void ConfigureServices(ServiceConfigurationContext context)
    {
        Configure<AbpApiDescriptionModelOptions>(options =>
        {
            options.SoonAddDefaultFlavors(ApiVersionDescriptionGroupProvider.DefaultGroupName);
        });
    }
}
```

### Entity Framework Module

```csharp
// Acme.BookStore.EntityFrameworkCore/AcmeBookStoreEntityFrameworkCoreModule.cs
[DependsOn(
    typeof(AcmeBookStoreDomainModule),
    typeof(AbpEntityFrameworkCoreModule)
)]
public class AcmeBookStoreEntityFrameworkCoreModule : AbpModule
{
    public override void ConfigureServices(ServiceConfigurationContext context)
    {
        context.Services.AddAbpDbContext<BookStoreDbContext>(options =>
        {
            options.AddDefaultRepositories();
        });

        Configure<AbpDbContextOptions>(options =>
        {
            options.Configure<BookStoreDbContext>();
        });
    }
}
```

## Module Dependencies

### Adding Dependencies

```csharp
[DependsOn(typeof(AbpAspNetCoreMvcModule))]
[DependsOn(typeof(AbpIdentityApplicationModule))]  // Add Identity module
[DependsOn(typeof(CmsKitApplicationModule))]         // Add CMS Kit module
public class MyModule : AbpModule
{
}
```

### Dependency Order

```
MyModule
    ├── Dependency1
    │   └── Dependency2
    │       └── Dependency3
    └── Dependency4
```

ABP initializes from bottom to top.

## Module Options

### Configure Module

```csharp
public override void ConfigureServices(ServiceConfigurationContext context)
{
    // Configure options
    Configure<BookStoreOptions>(options =>
    {
        options.MaxBookCount = 100;
        options.DefaultBookType = BookType.Undefined;
    });

    // Add configuration
    Configuration.Modules.AbpMvc().ModelBindingParameters
        .Add("BookType", typeof(BookType));
}
```

## Plug-In Modules

Load modules dynamically at runtime.

### Enable Plug-In

```csharp
public override void ConfigureServices(ServiceConfigurationContext context)
{
    Configure<AbpModuleDiscoveryOptions>(options =>
    {
        options.AddAssemblyFiles = true;
    });
}
```

### Module.json

```json
{
  "module": {
    "name": "Acme.HelloWorld",
    "assembly": "Acme.HelloWorld.dll",
    "dependsOn": [
      "Acme.BookStore.Application"
    ]
  }
}
```

## Module Extension

Extend existing modules with additional functionality.

### Extend Entity

```csharp
public class MyBookExtension : EntityExtension
{
    public override void MapEntity(EntityModelBuilder context)
    {
        var book = context.Entity<Book>();
        book.AddProperty("CustomField", typeof(string));
    }
}
```

### Extend Permission

```csharp
public class MyPermissionContributor : PermissionDefinitionProvider
{
    public override void Define(IPermissionDefinitionContext context)
    {
        var bookPermissions = context.GetPermission("BookStore.Books");
        bookPermissions.AddChild("BookStore.Books.CustomPermission");
    }
}
```

## Module Communication

### Via Dependency Injection

```csharp
// Module A exposes service
public interface IModuleAService
{
    Task<string> GetDataAsync();
}

// Module B depends on Module A
public class ModuleBService
{
    private readonly IModuleAService _moduleAService;

    public ModuleBService(IModuleAService moduleAService)
    {
        _moduleAService = moduleAService;
    }
}
```

### Via Domain Events

```csharp
// Publish event in Module A
public class ModuleAAppService : ApplicationService
{
    private readonly IEventBus _eventBus;

    public async Task DoSomethingAsync()
    {
        await _eventBus.PublishAsync(new DataChangedEvent { Data = "..." });
    }
}

// Subscribe in Module B
public class ModuleBDataChangedHandler :
    ILocalEventHandler<DataChangedEvent>
{
    public Task HandleEventAsync(DataChangedEvent eventData)
    {
        // Handle event from Module A
    }
}
```

### Via Configuration

```csharp
// Module A sets configuration
Configure<BookStoreOptions>(options =>
{
    options.MyCustomSetting = "value";
});

// Module B reads configuration
Configure<BookStoreOptions>(options =>
{
    var value = options.MyCustomSetting;
});
```

## Startup Template

### Create Module

```bash
abp new-module Acme.ProductManagement -t module:ddd
```

### Add to Solution

```bash
# Create new solution with the module
abp new Acme.BookStore -t app -m Acme.ProductManagement

# Add existing module to solution
abp add-module Acme.ProductManagement
```

## Best Practices

1. **Follow DDD structure** - Domain, Application, Infrastructure layers
2. **Define clear dependencies** - Minimize dependencies between modules
3. **Use interfaces** - Define interfaces in Contracts layer
4. **Avoid circular dependencies** - Use events for loose coupling
5. **Version your modules** - Semantic versioning for compatibility
6. **Document dependencies** - Specify required modules and versions
7. **Test independently** - Each module should be testable standalone
