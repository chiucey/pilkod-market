---
name: abp-blazor
description: ABP Blazor UI - Blazor components, CascadingAuthenticationState, Authorization, Services, Data Binding, Entity CRUD Components. Use when working with Blazor UI in ABP projects.
---

# ABP Blazor UI

> **Docs**: <https://docs.abp.io/en/latest/UI/Blazor/Overall>

## Project Structure

```
*.Blazor/
├── *.Blazor.csproj
├── Program.cs
├── _Imports.razor
├── App.razor
├── Pages/
│   └── Books/
│       └── Index.razor
├── Components/
│   ├── _Toolbar.razor
│   └── _Navbar.razor
└── Services/
    └── ProxyWrappers/
        └── Book.razor.cs
```

## App.razor

```razor
<CascadingAuthenticationState>
    <Router AppAssembly="@typeof(App).Assembly">
        <Found Context="routeData">
            <AuthorizeRouteView RouteData="@routeData" DefaultLayout="@typeof(MainLayout)">
                <NotAuthorized>
                    <RedirectToLogin />
                </NotAuthorized>
            </AuthorizeRouteView>
        </Found>
        <NotFound>
            <LayoutView Layout="@typeof(MainLayout)">
                <p>Sorry, there's nothing at this address.</p>
            </LayoutView>
        </NotFound>
    </Router>
</CascadingAuthenticationState>
```

## _Imports.razor

```razor
@using System.Net.Http
@using System.Net.Http.Json
@using Microsoft.AspNetCore.Authorization
@using Microsoft.AspNetCore.Components.Authorization
@using Microsoft.AspNetCore.Components.Forms
@using Microsoft.AspNetCore.Components.Routing
@using Microsoft.AspNetCore.Components.Web
@using Microsoft.AspNetCore.Components.Web.Virtualization
@using Microsoft.JSInterop
@using Volo.Abp.AspNetCore.Components.Web
@using Volo.Abp.BlazoriseUI
@using Volo.Abp.UI.Navigation
@using MyProject.Blazor.Pages
@using MyProject.Blazor.Components
@using MyProject.Blazor.Services
```

## Entity CRUD Component

### Create/Edit Modal

```razor
@* BookManagement.razor *@
@page "/books"
@using BookStore.Blazor.Components.BookManagement
@inherits BookManagementBase

<EntityCrudCard TEntity="BookDto"
                TGetListInput="GetBookListInput"
                TCreateUpdateInput="CreateUpdateBookDto"
                @ref="EntityCrudCard">
    <TableColumns>
        <TableColumn Text="@L["Name"]" Data="@context.Name" />
        <TableColumn Text="@L["Type"]" Data="@context.Type.ToString()" />
        <TableColumn Text="@L["Price"]" Data="@context.Price.ToString()" />
    </TableColumns>
</EntityCrudCard>
```

```csharp
// BookManagement.razor.cs
public class BookManagementBase : AbpCrudPage<
    IBookAppService,
    BookDto,
    Guid,
    GetBookListInput,
    CreateUpdateBookDto>
{
    protected override IBookAppService CrudService => BookAppService;

    [Inject]
    protected IBookAppService BookAppService { get; set; }
}
```

### Manual Implementation

```razor
@* Books.razor *@
@page "/books"
@using BookStore.Blazor.Components
@attribute [Authorize(BookStorePermissions.Books.Default)]

<h3>@L["Books"]</h3>

@* Data Grid *@
<DataGrid TItem="BookDto"
          Data="@Books"
          ReadData="@OnDataGridReadData"
          TotalItems="@TotalCount"
          ShowPager="true"
          PageSize="PageSize">
    <DataGridColumn TItem="BookDto" Field="@nameof(BookDto.Name)" Header="@L["Name"]" />
    <DataGridColumn TItem="BookDto" Field="@nameof(BookDto.Type)" Header="@L["Type"]" />
    <DataGridColumn TItem="BookDto" Field="@nameof(BookDto.Price)" Header="@L["Price"]">
        <DisplayTemplate>
            @context.Price.ToString("C")
        </DisplayContext>
    </DataGridColumn>
    <DataGridColumn TItem="BookDto" Field="@nameof(BookDto.Id)" Header="@L["Actions"]">
        <DisplayContext>
            <Buttons ieractions="DisplayContext.Value">
                <AuthorizeCell PermissionName="@BookStorePermissions.Books.Edit">
                    <Button Color="Color.Primary" Clicked="() => OpenEditModal(context.Value)">
                        @L["Edit"]
                    </Button>
                </AuthorizeCell>
                <AuthorizeCell PermissionName="@BookStorePermissions.Books.Delete">
                    <Button Color="Color.Danger" Clicked="() => DeleteEntity(context.Value)">
                        @L["Delete"]
                    </Button>
                </AuthorizeCell>
            </Buttons>
        </DisplayContext>
    </DataGridColumn>
</DataGrid>

@* Create Modal *@
<Button Color="Color.Primary" Clicked="OpenCreateModal">
    @L["NewBook"]
</Button>

<Modal @ref="CreateModal">
    <ModalContent IsCentered="true">
        <Form>
            <ModalHeader>
                <ModalTitle>@L["NewBook"]</ModalTitle>
                <CloseButton Clicked="CloseCreateModal" />
            </ModalHeader>
            <ModalBody>
                <Field>
                    <FieldLabel>@L["Name"]</FieldLabel>
                    <TextEdit @bind-Text="@NewBook.Name" />
                </Field>
                <Field>
                    <FieldLabel>@L["Price"]</FieldLabel>
                    <NumericEdit @bind-Value="@NewBook.Price" />
                </Field>
            </ModalBody>
            <ModalFooter>
                <Button Color="Color.Secondary" Clicked="CloseCreateModal">
                    @L["Cancel"]
                </Button>
                <Button Color="Color.Primary" Clicked="CreateEntity">
                    @L["Save"]
                </Button>
            </ModalFooter>
        </Form>
    </ModalContent>
</Modal>
```

```csharp
// Books.razor.cs
public partial class Books : AbpComponentBase
{
    protected IBookAppService BookAppService { get; set; }

    protected List<BookDto> Books;
    protected int TotalCount;
    protected int PageSize = 10;

    protected CreateUpdateBookDto NewBook = new();
    protected Guid EditingBookId;

    protected Modal CreateModal { get; set; }
    protected Modal EditModal { get; set; }

    protected override async Task OnInitializedAsync()
    {
        await GetBooksAsync();
    }

    protected async Task OnDataGridReadData(DataGridReadDataEventArgs<BookDto> e)
    {
        var input = new GetBookListInput
        {
            SkipCount = e.PageSize * (e.PageIndex - 1),
            MaxResultCount = e.PageSize,
            Sorting = e.Columns.Where(c => c.SortDirection != SortDirection.None)
                .Select(c => c.Field + (c.SortDirection == SortDirection.Descending ? " DESC" : ""))
                .JoinAsString(",")
        };

        var result = await BookAppService.GetListAsync(input);
        Books = result.Items.ToList();
        TotalCount = (int)result.TotalCount;
    }

    protected async Task CreateEntity()
    {
        await BookAppService.CreateAsync(NewBook);
        await CloseCreateModal();
        await GetBooksAsync();
    }

    protected async Task DeleteEntity(BookDto book)
    {
        await BookAppService.DeleteAsync(book.Id);
        await GetBooksAsync();
    }

    protected void OpenCreateModal()
    {
        NewBook = new CreateUpdateBookDto();
        CreateModal.Show();
    }

    protected Task CloseCreateModal()
    {
        return CreateModal.Hide();
    }
}
```

## Authorization in Blazor

### AuthorizeView

```razor
<AuthorizeView>
    <Authorized>
        <span>Hello, @context.User.Identity.Name!</span>
    </Authorized>
    <NotAuthorized>
        <span>You are not authorized.</span>
    </NotAuthorized>
</AuthorizeView>
```

### Permission Check

```razor
@if (await CanManageBooks())
{
    <Button Color="Color.Primary">Manage Books</Button>
}

@code {
    [Inject]
    protected IAuthorizationService AuthorizationService { get; set; }

    protected async Task<bool> CanManageBooks()
    {
        return await AuthorizationService.IsGrantedAsync(BookStorePermissions.Books.Manage);
    }
}
```

### AuthorizeCell Component

```razor
<AuthorizeCell PermissionName="BookStore.Books.Edit">
    <Button Color="Color.Primary" Clicked="() => Edit(context)">
        @L["Edit"]
    </Button>
</AuthorizeCell>
```

## Services

### Injecting Application Service

```csharp
// Books.razor.cs
public partial class Books : AbpComponentBase
{
    protected IBookAppService BookAppService { get; set; }

    [Inject]
    public NavigationManager NavigationManager { get; set; }

    [Inject]
    public IJSRuntime JSRuntime { get; set; }
}
```

### Using JSInterop

```csharp
protected override async Task OnAfterRenderAsync(bool firstRender)
{
    if (firstRender)
    {
        await JSRuntime.InvokeVoidAsync("myJsFunction");
    }
}
```

## Localization

```razor
@L["Books"]
@L["Name"]
@L["Price"]

@* With parameters *@
@L["WelcomeMessage", UserName]
```

## Toast Notifications

```csharp
@inject IToastService ToastService

protected async Task SaveAsync()
{
    await BookAppService.CreateAsync(Book);
    ToastService.Success("Book created successfully!");
}
```

## Best Practices

1. **Use `AbpComponentBase`** - Provides localization, authentication, and other services
2. **Use `OnParametersSet`** - For initialization that depends on parameters
3. **Dispose properly** - Implement `IDisposable` for cleanup
4. **Handle loading states** - Show loading indicators during async operations
5. **Use authorization** - Always check permissions for sensitive operations
6. **EntityCrudCard** - Use for standard CRUD operations
