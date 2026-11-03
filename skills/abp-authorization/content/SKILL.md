---
name: abp-authorization
description: ABP Permission System - PermissionDefinitionProvider, [Authorize] attribute, CheckPolicyAsync, IsGrantedAsync, ICurrentUser, IPermissionManager, multi-tenancy side. Use when working with permissions, authorization, role-based access, or security in ABP projects.
---

# ABP Authorization

> **Docs**: <https://abp.io/docs/latest/framework/fundamentals/authorization>

## Permission Definition

Define permissions in `*.Application.Contracts` project:

```csharp
// BookStore.Application.Contracts/Books/BookStorePermissions.cs
public static class BookStorePermissions
{
    public const string GroupName = "BookStore";

    public static class Books
    {
        public const string Default = GroupName + ".Books";
        public const string Create = Default + ".Create";
        public const string Edit = Default + ".Edit";
        public const string Delete = Default + ".Delete";
        public const string Export = Default + ".Export";
    }

    public static class Authors
    {
        public const string Default = GroupName + ".Authors";
        public const string Create = Default + ".Create";
        public const string Manage = Default + ".Manage";
    }
}
```

## Permission Definition Provider

```csharp
// BookStore.Domain/Books/BookStorePermissionDefinitionProvider.cs
public class BookStorePermissionDefinitionProvider : PermissionDefinitionProvider
{
    public override void Define(IPermissionDefinitionContext context)
    {
        var bookStoreGroup = context.AddGroup(
            BookStorePermissions.GroupName,
            L("Permission:BookStore"));

        // Books permissions
        var booksPermission = bookStoreGroup.AddPermission(
            BookStorePermissions.Books.Default,
            L("Permission:Books"));

        booksPermission.AddChild(
            BookStorePermissions.Books.Create,
            L("Permission:Books.Create"));

        booksPermission.AddChild(
            BookStorePermissions.Books.Edit,
            L("Permission:Books.Edit"));

        booksPermission.AddChild(
            BookStorePermissions.Books.Delete,
            L("Permission:Books.Delete"));

        booksPermission.AddChild(
            BookStorePermissions.Books.Export,
            L("Permission:Books.Export"));

        // Authors permissions
        var authorsPermission = bookStoreGroup.AddPermission(
            BookStorePermissions.Authors.Default,
            L("Permission:Authors"));

        authorsPermission.AddChild(BookStorePermissions.Authors.Create);
        authorsPermission.AddChild(BookStorePermissions.Authors.Manage);
    }

    private static LocalizableString L(string name)
    {
        return LocalizableString.Create<BookStoreResource>(name);
    }
}
```

## Using Permissions

### Declarative (Attribute)

```csharp
[Authorize(BookStorePermissions.Books.Create)]
public virtual async Task<BookDto> CreateAsync(CreateUpdateBookDto input)
{
    // Only users with Books.Create permission can execute
}

[Authorize(BookStorePermissions.Books.Default)]
public class BookAppService : ApplicationService
{
    // All methods require at least Default permission
}
```

### Multiple Permissions (OR)

```csharp
[Authorize(BookStorePermissions.Books.Create, BookStorePermissions.Books.Edit)]
public async Task<BookDto> CreateOrEditAsync(CreateUpdateBookDto input)
{
    // User needs Create OR Edit permission
}
```

### Programmatic Check

```csharp
public class BookAppService : ApplicationService
{
    public async Task DoSomethingAsync()
    {
        // Check and throw if not granted
        await CheckPolicyAsync(BookStorePermissions.Books.Edit);

        // Or check without throwing
        if (await AuthorizationService.IsGrantedAsync(BookStorePermissions.Books.Delete))
        {
            // Has permission
        }
    }
}
```

### Allow Anonymous Access

```csharp
[AllowAnonymous]
public virtual async Task<BookDto> GetPublicBookAsync(Guid id)
{
    // No authentication required
}
```

## Current User

Access authenticated user info via `CurrentUser` property:

```csharp
public class BookAppService : ApplicationService
{
    public async Task DoSomethingAsync()
    {
        // CurrentUser is available from base class
        var userId = CurrentUser.Id;
        var userName = CurrentUser.UserName;
        var email = CurrentUser.Email;
        var isAuthenticated = CurrentUser.IsAuthenticated;
        var roles = CurrentUser.Roles;
        var tenantId = CurrentUser.TenantId;
    }
}

// In other services, inject ICurrentUser
public class MyService : ITransientDependency
{
    private readonly ICurrentUser _currentUser;

    public MyService(ICurrentUser currentUser)
    {
        _currentUser = currentUser;
    }
}
```

### Ownership Validation

```csharp
public async Task UpdateMyBookAsync(Guid bookId, UpdateBookDto input)
{
    var book = await _bookRepository.GetAsync(bookId);

    if (book.CreatorId != CurrentUser.Id)
    {
        throw new AbpAuthorizationException("NotAuthorizedToUpdateBook");
    }

    // Update book...
}
```

## Multi-Tenancy Permissions

Control permission availability per tenant side:

```csharp
bookStoreGroup.AddPermission(
    BookStorePermissions.Books.Default,
    L("Permission:Books"),
    multiTenancySide: MultiTenancySides.Tenant // Only for tenants
);

// Options: Host, Tenant, or Both
```

## Feature-Dependent Permissions

Permissions can depend on features:

```csharp
booksPermission.RequireFeatures("BookStore.PremiumFeature");
```

## Permission Management

Grant/revoke permissions programmatically:

```csharp
public class PermissionAppService : ApplicationService
{
    private readonly IPermissionManager _permissionManager;

    public PermissionAppService(IPermissionManager permissionManager)
    {
        _permissionManager = permissionManager;
    }

    public async Task GrantPermissionToUserAsync(Guid userId, string permissionName)
    {
        await _permissionManager.SetForUserAsync(userId, permissionName, true);
    }

    public async Task GrantPermissionToRoleAsync(string roleName, string permissionName)
    {
        await _permissionManager.SetForRoleAsync(roleName, permissionName, true);
    }

    public async Task RevokeAllPermissionsAsync(Guid userId)
    {
        var permission = _permissionManager.Get("BookStore.Books.Default");
        await _permissionManager.SetForUserAsync(userId, permission.Name, false);
    }
}
```

## Permission with Claims

```csharp
public class BookStorePermissionDefinitionProvider : PermissionDefinitionProvider
{
    public override void Define(IPermissionDefinitionContext context)
    {
        var booksPermission = context.GetGroup(BookStorePermissions.GroupName)
            .AddPermission(BookStorePermissions.Books.Edit);

        // Add custom claims
        booksPermission.AddChild(BookStorePermissions.Books.Delete)
            .WithClaims("CanDelete", "true");
    }
}
```

## Security Best Practices

1. **Never trust client input** - Always validate on server side
2. **Use `CurrentUser`** - Don't pass user ID from client
3. **Validate ownership** - Check if user owns the resource
4. **Filter queries** - Always filter by current user when appropriate
5. **Don't expose sensitive data** - Omit sensitive fields from DTOs
6. **Principle of least privilege** - Only grant necessary permissions

## JavaScript Client Side

```javascript
// Check permission
if (abp.auth.isGranted('BookStore.Books.Create')) {
    // Show create button
}

// Get current user
var userId = abp.currentUser.id;
var userName = abp.currentUser.userName;

// Get claims
var email = abp.currentUser.email;
```
