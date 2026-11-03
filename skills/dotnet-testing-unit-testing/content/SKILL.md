---
name: dotnet-testing-unit-testing
description: 掌握 .NET 单元测试和集成测试技能。当用户要求编写单元测试、使用 xUnit/NUnit/MSTest、Mock 对象、测试覆盖率、或进行 TDD 开发时使用。
---

# 单元测试与集成测试技能

## 核心技能清单

| 技能项 | 熟练度 | 说明 |
|-------|-------|------|
| xUnit/NUnit | ⭐⭐⭐⭐⭐ | 测试框架 |
| Moq/FakeItEasy | ⭐⭐⭐⭐⭐ | Mock 框架 |
| FluentAssertions | ⭐⭐⭐⭐⭐ | 断言库 |
| 集成测试 | ⭐⭐⭐⭐ | WebApplicationFactory |
| 测试覆盖率 | ⭐⭐⭐⭐ | Coverlet |
| TDD 实践 | ⭐⭐⭐⭐ | 测试驱动开发 |

## xUnit 测试框架

### 基础结构

```csharp
public class OrderServiceTests
{
    [Fact]
    public void CalculateTotal_WithValidItems_ReturnsCorrectTotal()
    {
        // Arrange
        var service = new OrderService();
        var items = new List<OrderItem>
        {
            new OrderItem { Price = 10.00m, Quantity = 2 },
            new OrderItem { Price = 5.00m, Quantity = 3 }
        };

        // Act
        var total = service.CalculateTotal(items);

        // Assert
        Assert.Equal(35.00m, total);
    }

    [Theory]
    [InlineData(100, 10, 90)]
    [InlineData(50, 5, 45)]
    [InlineData(200, 0, 200)]
    public void ApplyDiscount_ReturnsCorrectAmount(
        decimal original, decimal discountPercent, decimal expected)
    {
        // Arrange
        var service = new OrderService();

        // Act
        var result = service.ApplyDiscount(original, discountPercent);

        // Assert
        Assert.Equal(expected, result);
    }
}
```

### 测试类组织

```csharp
public class OrderServiceTests : IDisposable
{
    private readonly OrderService _service;
    private readonly Mock<IOrderRepository> _mockRepo;
    private readonly Mock<IEmailService> _mockEmail;

    public OrderServiceTests()
    {
        _mockRepo = new Mock<IOrderRepository>();
        _mockEmail = new Mock<IEmailService>();
        _service = new OrderService(_mockRepo.Object, _mockEmail.Object);
    }

    public void Dispose()
    {
        // 清理资源
    }

    [Fact]
    public async Task CreateOrderAsync_SavesOrderAndSendsEmail()
    {
        // Arrange
        var command = new CreateOrderCommand { CustomerId = 1 };
        _mockRepo.Setup(r => r.AddAsync(It.IsAny<Order>()))
            .ReturnsAsync((Order o) => o);

        // Act
        var result = await _service.CreateOrderAsync(command);

        // Assert
        _mockRepo.Verify(r => r.AddAsync(It.IsAny<Order>()), Times.Once);
        _mockEmail.Verify(e => e.SendOrderConfirmation(
            It.IsAny<int>(), It.IsAny<string>()), Times.Once);
    }
}
```

### 特性标签

```csharp
public class AdvancedTests
{
    // 跳过测试
    [Fact(Skip = "等待数据库修复")]
    public void LongRunningTest() { }

    // 特性测试
    [Fact]
    [Trait("Category", "Integration")]
    [Trait("Priority", "High")]
    public void IntegrationTest() { }

    // 动态数据
    [Theory]
    [MemberData(nameof(TestData))]
    public void TestWithMemberData(string input, int expected) { }

    public static IEnumerable<object[]> TestData =>
        new List<object[]>
        {
            new object[] { "test1", 1 },
            new object[] { "test2", 2 }
        };

    // 类数据
    [Theory]
    [ClassData(typeof(CalculatorTestData))]
    public void TestWithClassData(int a, int b, int expected) { }
}

public class CalculatorTestData : IEnumerable<object[]>
{
    public IEnumerator<object[]> GetEnumerator()
    {
        yield return new object[] { 1, 2, 3 };
        yield return new object[] { 0, 0, 0 };
        yield return new object[] { -1, 1, 0 };
    }

    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}
```

## Moq 框架

### 基础 Mock

```csharp
public class MockBasicsTests
{
    [Fact]
    public void GetOrder_WhenExists_ReturnsOrder()
    {
        // Arrange
        var mockRepo = new Mock<IOrderRepository>();
        mockRepo.Setup(r => r.GetByIdAsync(1))
            .ReturnsAsync(new Order { Id = 1, Total = 100m });

        var service = new OrderService(mockRepo.Object);

        // Act
        var result = service.GetOrder(1);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(100m, result.Total);
    }

    [Fact]
    public void GetOrder_WhenNotExists_ReturnsNull()
    {
        // Arrange
        var mockRepo = new Mock<IOrderRepository>();
        mockRepo.Setup(r => r.GetByIdAsync(It.IsAny<int>()))
            .ReturnsAsync((Order?)null);

        var service = new OrderService(mockRepo.Object);

        // Act
        var result = service.GetOrder(999);

        // Assert
        Assert.Null(result);
    }
}
```

### 参数匹配

```csharp
[Fact]
public void ProcessOrder_WithValidCustomer_ProcessesSuccessfully()
{
    // Arrange
    var mockRepo = new Mock<IOrderRepository>();
    
    mockRepo.Setup(r => r.GetByCustomerIdAsync(It.IsAny<int>()))
        .ReturnsAsync(new List<Order>());

    // 特定值匹配
    mockRepo.Setup(r => r.GetByIdAsync(1))
        .ReturnsAsync(new Order { Id = 1 });

    // 范围匹配
    mockRepo.Setup(r => r.GetByIdAsync(
        It.Is<int>(id => id > 0 && id < 1000)))
        .ReturnsAsync(new Order());

    // 正则匹配
    mockRepo.Setup(r => r.GetByEmailAsync(
        It.IsRegex(@".+@example\.com")))
        .ReturnsAsync(new Customer());

    // 参数回调
    var capturedOrder = (Order?)null;
    mockRepo.Setup(r => r.AddAsync(It.IsAny<Order>()))
        .Callback<Order>(o => capturedOrder = o)
        .ReturnsAsync((Order o) => o);

    // Act
    var service = new OrderService(mockRepo.Object);
    service.ProcessOrder(1);

    // Assert
    Assert.NotNull(capturedOrder);
    Assert.Equal(OrderStatus.Processed, capturedOrder.Status);
}
```

### 验证调用

```csharp
[Fact]
public void CreateOrder_SendsEmailConfirmation()
{
    // Arrange
    var mockRepo = new Mock<IOrderRepository>();
    var mockEmail = new Mock<IEmailService>();
    
    mockRepo.Setup(r => r.AddAsync(It.IsAny<Order>()))
        .ReturnsAsync((Order o) => o);

    var service = new OrderService(mockRepo.Object, mockEmail.Object);

    // Act
    service.CreateOrder(new CreateOrderCommand { CustomerId = 1 });

    // Assert - 验证调用次数
    mockEmail.Verify(e => e.SendOrderConfirmation(
        It.IsAny<int>(), It.IsAny<string>()), Times.Once);

    // 验证调用顺序
    var inOrder = Mock.Get(mockEmail).InOrder(() =>
    {
        mockEmail.Object.SendOrderConfirmation(It.IsAny<int>(), It.IsAny<string>());
        mockEmail.Object.SendAdminNotification(It.IsAny<int>());
    });
}

[Fact]
public void UpdateOrder_NeverSendsEmail_WhenStatusUnchanged()
{
    // Arrange
    var mockEmail = new Mock<IEmailService>();
    var mockRepo = new Mock<IOrderRepository>();

    // Act
    var service = new OrderService(mockRepo.Object, mockEmail.Object);
    service.UpdateOrderStatus(1, OrderStatus.Pending);

    // Assert - 验证从未调用
    mockEmail.Verify(e => e.SendStatusChangeNotification(
        It.IsAny<int>(), It.IsAny<OrderStatus>()), Times.Never);
}
```

## FluentAssertions

### 基础断言

```csharp
using FluentAssertions;

[Fact]
public void Order_TotalCalculation_IsCorrect()
{
    // Arrange
    var order = new Order
    {
        Items = new List<OrderItem>
        {
            new() { Price = 10.00m, Quantity = 2 },
            new() { Price = 5.00m, Quantity = 3 }
        }
    };

    // Act
    var total = order.Total;

    // Assert
    total.Should().Be(35.00m);
    total.Should().BeGreaterThan(0);
    total.Should().BeLessThan(100);
}

[Fact]
public void CreateCustomer_WithInvalidEmail_ThrowsException()
{
    // Arrange & Act
    var act = () => new Customer("John", "invalid-email");

    // Assert
    act.Should().Throw<ValidationException>()
        .WithMessage("*valid email*");
}

[Fact]
public void GetOrders_ForExistingCustomer_ReturnsOrders()
{
    // Arrange
    var customerId = 1;
    _mockRepo.Setup(r => r.GetByCustomerIdAsync(customerId))
        .ReturnsAsync(new List<Order>
        {
            new() { Id = 1, Total = 100 },
            new() { Id = 2, Total = 200 }
        });

    // Act
    var orders = _service.GetCustomerOrders(customerId);

    // Assert
    orders.Should().HaveCount(2);
    orders.Should().Contain(o => o.Total == 100);
    orders.Should().BeInAscendingOrder(o => o.Total);
}
```

### 对象集合断言

```csharp
[Fact]
public void GetProducts_ReturnsExpectedProducts()
{
    // Arrange
    var expectedProducts = new[]
    {
        new Product { Id = 1, Name = "Product A", Price = 10 },
        new Product { Id = 2, Name = "Product B", Price = 20 }
    };

    _mockRepo.Setup(r => r.GetAllAsync())
        .ReturnsAsync(expectedProducts);

    // Act
    var products = _service.GetProducts();

    // Assert
    products.Should().BeEquivalentTo(expectedProducts, options => options
        .Excluding(p => p.CreatedAt)
        .IncludingNestedObjects());
}

[Fact]
public void ProcessOrders_WithMixedResults_GroupsCorrectly()
{
    // Arrange
    var orders = new List<Order>
    {
        new() { Status = OrderStatus.Pending, Total = 100 },
        new() { Status = OrderStatus.Completed, Total = 200 },
        new() { Status = OrderStatus.Pending, Total = 50 },
        new() { Status = OrderStatus.Cancelled, Total = 75 }
    };

    // Act
    var grouped = _service.GroupByStatus(orders);

    // Assert
    grouped.Should().ContainKey(OrderStatus.Pending);
    grouped[OrderStatus.Pending].Should().HaveCount(2);
    grouped[OrderStatus.Pending].Sum(o => o.Total).Should().Be(150);
}
```

## 集成测试

### WebApplicationFactory

```csharp
public class CustomWebApplicationFactory : 
    WebApplicationFactory<Program>
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            // 移除 DbContext
            var descriptor = services.SingleOrDefault(
                d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));
            if (descriptor != null)
                services.Remove(descriptor);

            // 添加测试数据库
            services.AddDbContext<AppDbContext>(options =>
            {
                options.UseInMemoryDatabase("TestDb");
            });
        });
    }
}

public class IntegrationTests : IClassFixture<CustomWebApplicationFactory>
{
    private readonly CustomWebApplicationFactory _factory;
    private readonly HttpClient _client;

    public IntegrationTests(CustomWebApplicationFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetProducts_ReturnsSuccessAndCorrectContentType()
    {
        // Act
        var response = await _client.GetAsync("/api/products");

        // Assert
        response.EnsureSuccessStatusCode();
        response.Content.Headers.ContentType.MediaType
            .Should().Be("application/json");
    }

    [Fact]
    public async Task CreateProduct_WithValidData_ReturnsCreated()
    {
        // Arrange
        var newProduct = new
        {
            Name = "Test Product",
            Price = 99.99m,
            CategoryId = 1
        };

        // Act
        var response = await _client.PostAsJsonAsync(
            "/api/products", newProduct);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        
        var createdProduct = await response.Content
            .ReadFromJsonAsync<ProductDto>();
        createdProduct.Should().NotBeNull();
        createdProduct!.Name.Should().Be("Test Product");
    }
}
```

### Authenticated Tests

```csharp
public class AuthenticatedTests : IClassFixture<CustomWebApplicationFactory>
{
    private readonly CustomWebApplicationFactory _factory;
    private readonly HttpClient _client;

    public AuthenticatedTests(CustomWebApplicationFactory factory)
    {
        _factory = factory;
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetOrders_WithoutAuth_ReturnsUnauthorized()
    {
        var response = await _client.GetAsync("/api/orders");
        response.StatusCode.Should().Be(HttpStatusCode.Unauthorized);
    }

    [Fact]
    public async Task GetOrders_WithValidToken_ReturnsOrders()
    {
        // Arrange - 获取 token
        var token = await GetAuthToken();
        _client.DefaultRequestHeaders.Authorization = 
            new AuthenticationHeaderValue("Bearer", token);

        // Act
        var response = await _client.GetAsync("/api/orders");

        // Assert
        response.EnsureSuccessStatusCode();
        var orders = await response.Content
            .ReadFromJsonAsync<List<OrderDto>>();
        orders.Should().NotBeNull();
    }
}
```

## 测试覆盖率

### Coverlet 配置

```xml
<!-- UnitTests.csproj -->
<ItemGroup>
    <PackageReference Include="coverlet.collector" Version="6.0" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2" />
</ItemGroup>

<PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IncludeCoverageHistogram>true</IncludeCoverageHistogram>
    <CoverageOutputFormat>opencover</CoverageOutputFormat>
</PropertyGroup>
```

### 运行覆盖率

```bash
# 运行测试并生成覆盖率
dotnet test --collect:"XPlat Code Coverage"

# 生成报告
dotnet tool install --global dotnet-reportgenerator-globaltool
reportgenerator -reports:./TestResults/*/coverage.cobertura.xml \
    -targetdir:./coverage -reporttypes:Html

# 查看详细报告
# 打开 coverage/index.html
```

### 覆盖率目标

| 模块 | 最低覆盖率 |
|-----|-----------|
| 业务逻辑 | 80% |
| 核心服务 | 90% |
| 工具类 | 70% |
| 控制器 | 60% |
| 整体项目 | 70% |

## TDD 开发流程

### 红-绿-重构

```csharp
// 1. 红 - 编写失败的测试
[Fact]
public void Add_TwoNumbers_ReturnsSum()
{
    var calculator = new Calculator();
    
    // 这会编译失败 - Calculator 还不存在
    var result = calculator.Add(2, 3);
    
    result.Should().Be(5);
}

// 2. 绿 - 最简单实现通过测试
public class Calculator
{
    public int Add(int a, int b) => 5; // 硬编码通过
}

// 3. 重构 - 改进实现
public class Calculator
{
    public int Add(int a, int b) => a + b; // 真正实现
}
```

### 典型 TDD 流程

```csharp
// 步骤 1: 明确需求
// 需求: 计算订单总价，支持折扣

// 步骤 2: 编写测试
[Fact]
public void CalculateTotal_WithDiscount_ReturnsDiscountedTotal()
{
    var calculator = new OrderCalculator();
    var items = new List<OrderItem>
    {
        new() { Price = 100, Quantity = 1 }
    };

    var total = calculator.CalculateTotal(items, discountPercent: 10);

    total.Should().Be(90);
}

[Fact]
public void CalculateTotal_WithInvalidDiscount_ThrowsException()
{
    var calculator = new OrderCalculator();
    var items = new List<OrderItem>
    {
        new() { Price = 100, Quantity = 1 }
    };

    var act = () => calculator.CalculateTotal(items, discountPercent: 150);

    act.Should().Throw<ArgumentOutOfRangeException>();
}

// 步骤 3: 实现功能
public class OrderCalculator
{
    public decimal CalculateTotal(
        IEnumerable<OrderItem> items, 
        decimal discountPercent = 0)
    {
        if (discountPercent < 0 || discountPercent > 100)
            throw new ArgumentOutOfRangeException(nameof(discountPercent));

        var subtotal = items.Sum(i => i.Price * i.Quantity);
        var discount = subtotal * discountPercent / 100;
        return subtotal - discount;
    }
}
```
