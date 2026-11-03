---
name: abp-mvc
description: ABP MVC and Razor Pages UI - AbpPageModel, abp tag helpers (abp-card, abp-dynamic-form, abp-modal), JavaScript abp.ajax/abp.auth/abp.notify, DataTables integration. Use when working on MVC or Razor Pages UI in ABP projects.
---

# ABP MVC / Razor Pages UI

> **Docs**: <https://docs.abp.io/en/dev/ui>

## Razor Page Model

```csharp
// BookStore.Web/Pages/Books/Index.cshtml.cs
public class IndexModel : AbpPageModel
{
    private readonly IBookAppService _bookAppService;

    public List<BookDto> Books { get; set; }

    public IndexModel(IBookAppService bookAppService)
    {
        _bookAppService = bookAppService;
    }

    public async Task OnGetAsync()
    {
        var result = await _bookAppService.GetListAsync(
            new PagedAndSortedResultRequestDto());
        Books = result.Items.ToList();
    }
}
```

## Razor Page View

```cshtml
@page
@model BookStore.Web.Pages.Books.IndexModel
@{
}

<h2>@L["Books"]</h2>

<table id="BooksTable" class="table">
    <thead>
        <tr>
            <th>@L["Name"]</th>
            <th>@L["Type"]</th>
            <th>@L["Price"]</th>
            <th>@L["Actions"]</th>
        </tr>
    </thead>
    <tbody>
        @foreach (var book in Model.Books)
        {
            <tr>
                <td>@book.Name</td>
                <td>@L[$"BookType:{book.Type}"]</td>
                <td>@book.Price.ToString("C")</td>
                <td>
                    <a href="/Books/Edit/@book.Id" class="btn btn-sm btn-primary">
                        @L["Edit"]
                    </a>
                </td>
            </tr>
        }
    </tbody>
</table>
```

## ABP Tag Helpers

### Card

```cshtml
<abp-card>
    <abp-card-header>
        <abp-card-title>@L["Books"]</abp-card-title>
    </abp-card-header>
    <abp-card-body>
        <!-- Card content -->
    </abp-card-body>
    <abp-card-footer>
        Footer content
    </abp-card-footer>
</abp-card>
```

### Button

```cshtml
<abp-button button-type="Primary" icon="fa fa-save" text="@L["Save"]"></abp-button>

<abp-button button-type="Success" icon="fa fa-plus" text="@L["Create"]"
            onclick="location.href='/Books/Create'"></abp-button>

<abp-button button-type="Danger" icon="fa fa-trash"
            text="@L["Delete"]"></abp-button>
```

### Dynamic Form

```cshtml
<abp-dynamic-form abp-model="Book" submit-button="true">
    <abp-form-content />
</abp-dynamic-form>
```

### Modal

```cshtml
<abp-modal centered="true" size="Large" name="CreateModal" title="@L["NewBook"]">
    <abp-modal-body>
        <form id="CreateBookForm">
            <abp-input asp-for="Name" />
            <abp-select asp-for="Type" />
            <abp-input asp-for="Price" type="number" />
        </form>
    </abp-modal-body>
    <abp-modal-footer buttons-type="Close,Save"></abp-modal-footer>
</abp-modal>
```

### Data Table

```cshtml
<abp-table striped="true" hover="true" responsive="true">
    <thead>
        <tr>
            <th>@L["Name"]</th>
            <th>@L["Price"]</th>
        </tr>
    </thead>
    <tbody>
        @foreach (var book in Model.Books)
        {
            <tr>
                <td>@book.Name</td>
                <td>@book.Price</td>
            </tr>
        }
    </tbody>
</abp-table>
```

## Localization

```cshtml
@* In Razor views/pages *@
@L["Books"]
@L["Name"]
@L["Price"]

@* With parameters *@
@L["WelcomeMessage", Model.UserName]

@* Formatting *@
@L["BookCount", Model.BookCount]
```

## JavaScript API

```javascript
// Localization
var localization = abp.localization.getResource('BookStore');
var booksText = localization('Books');
var message = localization('WelcomeMessage', 'John');

// Authorization
if (abp.auth.isGranted('BookStore.Books.Create')) {
    $('#createButton').show();
}

// Settings
var maxCount = abp.setting.get('BookStore.MaxItemCount');

// Notifications
abp.notify.success('Book created successfully!');
abp.notify.error('An error occurred!');
abp.notify.warn('Please check your input.');

// Confirmation dialogs
abp.message.confirm('Are you sure you want to delete this book?')
    .then(function (confirmed) {
        if (confirmed) {
            bookService.delete(bookId);
        }
    });

// Alert
abp.message.success('Operation completed!');
abp.message.error('Something went wrong!');

// Ajax with automatic error handling
abp.ajax({
    url: '/api/app/book',
    type: 'POST',
    data: JSON.stringify(bookData)
}).then(function(result) {
    // Success
    abp.notify.success('Saved successfully!');
}).catch(function(error) {
    // Error is handled automatically
});
```

## DataTables Integration

```javascript
var dataTable = $('#BooksTable').DataTable(
    abp.libs.datatables.normalizeConfiguration({
        serverSide: true,
        paging: true,
        scrollX: true,
        autoWidth: false,
        ajax: abp.libs.datatables.createAjax(bookService.getList),
        columnDefs: [
            {
                title: l('Name'),
                data: 'name'
            },
            {
                title: l('Price'),
                data: 'price',
                render: function(data) {
                    return data.toFixed(2);
                }
            },
            {
                title: l('Actions'),
                rowAction: {
                    items: [
                        {
                            text: l('Edit'),
                            visible: abp.auth.isGranted('BookStore.Books.Edit'),
                            action: function(data) {
                                editModal.open({id: data.record.id});
                            }
                        },
                        {
                            text: l('Delete'),
                            visible: abp.auth.isGranted('BookStore.Books.Delete'),
                            confirmMessage: function(data) {
                                return l('BookDeletionConfirmationMessage', data.record.name);
                            },
                            action: function(data) {
                                bookService.delete(data.record.id)
                                    .then(function() {
                                        abp.notify.success(l('SuccessfullyDeleted'));
                                        dataTable.ajax.reload();
                                    });
                            }
                        }
                    ]
                }
            }
        ]
    })
);
```

## Modal Pages

### Create Modal

```cshtml
@* CreateModal.cshtml *@
@page
@using BookStore.Web.Pages.Books
@model CreateModalModel

@{
    <abp-modal>
        <abp-modal-header title="@L["NewBook"]"></abp-modal-header>
        <abp-modal-body>
            <form id="CreateBookForm" data-ajaxForm="true">
                <abp-input asp-for="Book.Name" />
                <abp-select asp-for="Book.Type" />
                <abp-input asp-for="Book.Price" />
            </form>
        </abp-modal-body>
        <abp-modal-footer buttons-type="Close,Save"></abp-modal-footer>
    </abp-modal>
}
```

```csharp
// CreateModal.cshtml.cs
public class CreateModalModel : BookStorePageModel
{
    [BindProperty]
    public CreateBookDto Book { get; set; }

    private readonly IBookAppService _bookAppService;

    public CreateModalModel(IBookAppService bookAppService)
    {
        _bookAppService = bookAppService;
    }

    public async Task<NoContentResult> OnPostAsync()
    {
        await _bookAppService.CreateAsync(Book);
        return NoContent();
    }
}
```

## Bundle & Minification

```csharp
// BookStoreWebModule.cs
Configure<AbpBundlingOptions>(options =>
{
    options.StyleBundles.Configure(StandardBundles.Styles.Global, bundle =>
    {
        bundle.AddFiles("/styles/my-styles.css");
    });

    options.ScriptBundles.Configure(StandardBundles.Scripts.Global, bundle =>
    {
        bundle.AddFiles("/scripts/my-script.js");
    });
});
```
