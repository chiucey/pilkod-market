---
name: dotnet-webapi-development
description: 掌握 .NET Web API 开发技能。当用户要求创建 RESTful API、设计 API 接口、处理 HTTP 请求响应、实现认证授权、配置 Swagger 文档时使用。
---

# Web API 开发技能

## 核心技能清单

| 技能项 | 熟练度 | 说明 |
|-------|-------|------|
| RESTful 设计 | ⭐⭐⭐⭐⭐ | REST 规范、HTTP 方法 |
| 控制器开发 | ⭐⭐⭐⭐⭐ | CRUD、路由、绑定 |
| 认证授权 | ⭐⭐⭐⭐⭐ | JWT、OAuth2、策略 |
| 请求验证 | ⭐⭐⭐⭐⭐ | Data Annotations、FluentValidation |
| 异常处理 | ⭐⭐⭐⭐⭐ | 全局异常、中间件 |
| OpenAPI/Swagger | ⭐⭐⭐⭐⭐ | 文档生成、测试 |

## RESTful API 设计

### 资源命名规范

```
# 正确示例
GET    /api/products              # 获取产品列表
GET    /api/products/{id}         # 获取单个产品
POST   /api/products              # 创建产品
PUT    /api/products/{id}         # 更新产品
PATCH  /api/products/{id}          # 部分更新
DELETE /api/products/{id}         # 删除产品

# 嵌套资源
GET    /api/orders/{orderId}/items     # 获取订单项
POST   /api/orders/{orderId}/items     # 添加订单项
DELETE /api/orders/{orderId}/items/{id} # 删除订单项

# 集合操作
GET    /api/products?page=1&pageSize=10
GET    /api/products?category=electronics
POST   /api/products/bulk          # 批量操作
```

### HTTP 状态码

| 状态码 | 含义 | 使用场景 |
|-------|-----|---------|
| 200 OK | 成功 | GET、PUT、PATCH 成功 |
| 201 Created | 已创建 | POST 创建成功 |
| 204 No Content | 无内容 | DELETE 成功 |
| 400 Bad Request | 请求错误 | 验证失败 |
| 401 Unauthorized | 未认证 | 缺少/无效认证 |
| 403 Forbidden | 无权限 | 无权访问资源 |
| 404 Not Found | 未找到 | 资源不存在 |
| 409 Conflict | 冲突 | 重复创建 |
| 422 Unprocessable | 无法处理 | 业务逻辑错误 |
| 500 Internal Error | 服务器错误 | 系统异常 |

## 控制器开发

### 基础控制器

```csharp
[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class ProductsController : ControllerBase
{
    private readonly IProductService _productService;
    private readonly IMapper _mapper;

    public ProductsController(
        IProductService productService,
        IMapper mapper)
    {
        _productService = productService;
        _mapper = mapper;
    }

    [HttpGet]
    [ProducesResponseType(typeof(PagedResult<ProductDto>), 200)]
    public async Task<ActionResult<PagedResult<ProductDto>>> GetProducts(
        [FromQuery] ProductQuery query)
    {
        var result = await _productService.GetProductsAsync(query);
        return Ok(result);
    }

    [HttpGet("{id:int}")]
    [ProducesResponseType(typeof(ProductDto), 200)]
    [ProducesResponseType(404)]
    public async Task<ActionResult<ProductDto>> GetProduct(int id)
    {
        var product = await _productService.GetByIdAsync(id);
        if (product == null)
            return NotFound();
        
        return Ok(_mapper.Map<ProductDto>(product));
    }

    [HttpPost]
    [ProducesResponseType(typeof(ProductDto), 201)]
    [ProducesResponseType(400)]
    public async Task<ActionResult<ProductDto>> CreateProduct(
        [FromBody] CreateProductCommand command)
    {
        var product = await _productService.CreateAsync(command);
        return CreatedAtAction(
            nameof(GetProduct),
            new { id = product.Id },
            _mapper.Map<ProductDto>(product));
    }

    [HttpPut("{id:int}")]
    [ProducesResponseType(204)]
    public async Task<IActionResult> UpdateProduct(
        int id,
        [FromBody] UpdateProductCommand command)
    {
        if (id != command.Id)
            return BadRequest();

        await _productService.UpdateAsync(command);
        return NoContent();
    }

    [HttpDelete("{id:int}")]
    [ProducesResponseType(204)]
    public async Task<IActionResult> DeleteProduct(int id)
    {
        await _productService.DeleteAsync(id);
        return NoContent();
    }
}
```

### 路由属性

```csharp
[Route("api/v1/[controller]")]
public class OrdersController : ControllerBase
{
    // 自定义路由
    [HttpGet("customer/{customerId:int}/orders")]
    public async Task<IActionResult> GetCustomerOrders(int customerId) { }

    // 路由约束
    [HttpGet("{id:guid}")]           // GUID
    [HttpGet("{status:alpha}")]      // 字母
    [HttpGet("{page:int:min(1)}")]   // 整数最小值

    // 可选参数
    [HttpGet("search")]
    public async Task<IActionResult> Search([FromQuery] string term = null) { }

    // 路由名称
    [HttpGet("{id:int}", Name = "GetProductById")]
    public async Task<IActionResult> GetById(int id) { }
}
```

### 模型绑定

```csharp
// FromQuery - 查询字符串
public async Task<IActionResult> Get(
    [FromQuery] string search,
    [FromQuery] int page = 1,
    [FromQuery] int pageSize = 10) { }

// FromBody - 请求体
public async Task<IActionResult> Create([FromBody] CreateDto dto) { }

// FromRoute - 路由参数
[HttpGet("{id:int}")]
public async Task<IActionResult> Get([FromRoute] int id) { }

// FromForm - 表单数据
public async Task<IActionResult> Upload([FromForm] IFormFile file) { }

// FromHeader - 请求头
public async Task<IActionResult> Get([FromHeader(Name = "X-Request-Id")] string requestId) { }

// 复合模型
public async Task<IActionResult> Create([FromForm] CreateOrderDto dto, 
                                         [FromForm] IFormFile attachment) { }
```

## 认证授权

### JWT 认证

```csharp
// Program.cs
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]))
};
    });

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy => 
        policy.RequireRole("Admin"));
    options.AddPolicy("MinimumAge", policy =>
        policy.RequireClaim("Age", "18", "21", "25"));
});

// 控制器使用
[Authorize]
[ApiController]
public class SecureController : ControllerBase
{
    [Authorize(Policy = "AdminOnly")]
    [HttpDelete("{id}")]
    public async Task<IActionResult> Delete(int id) { }

    [AllowAnonymous]
    [HttpGet("public")]
    public IActionResult Public() => Ok("Public data");
}
```

### JWT Token 生成

```csharp
public class TokenService
{
    private readonly IConfiguration _config;

    public string GenerateToken(User user)
    {
        var key = new SymmetricSecurityKey(
            Encoding.UTF8.GetBytes(_config["Jwt:Key"]));
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
            new Claim(JwtRegisteredClaimNames.Email, user.Email),
            new Claim(ClaimTypes.Role, user.Role),
            new Claim("Department", user.Department)
        };

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(30),
            signingCredentials: credentials);

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
```

### Claims 访问

```csharp
[HttpGet("profile")]
public async Task<IActionResult> GetProfile()
{
    var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
    var email = User.FindFirstValue(ClaimTypes.Email);
    var role = User.FindFirstValue(ClaimTypes.Role);

    var profile = await _userService.GetProfileAsync(userId);
    return Ok(profile);
}
```

## 请求验证

### Data Annotations

```csharp
public class CreateProductCommand
{
    [Required(ErrorMessage = "名称不能为空")]
    [StringLength(100, MinimumLength = 2)]
    public string Name { get; set; }

    [Required]
    [Range(0.01, 100000, ErrorMessage = "价格必须在 0.01 - 100000 之间")]
    public decimal Price { get; set; }

    [EmailAddress]
    public string Email { get; set; }

    [Url]
    public string Website { get; set; }

    [Phone]
    public string Phone { get; set; }

    [RegularExpression(@"^\d{4}-\d{4}$", 
        ErrorMessage = "格式必须为 1234-5678")]
    public string Code { get; set; }
}
```

### FluentValidation

```csharp
// 安装：FluentValidation.AspNetCore

public class CreateProductCommandValidator : 
    AbstractValidator<CreateProductCommand>
{
    public CreateProductCommandValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("名称不能为空")
            .Length(2, 100).WithMessage("名称长度 2-100")
            .MustAsync(async (name, cancellation) =>
                !await _productRepo.ExistsByNameAsync(name))
            .WithMessage("产品名称已存在");

        RuleFor(x => x.Price)
            .GreaterThan(0).WithMessage("价格必须大于 0")
            .LessThan(100000).WithMessage("价格不能超过 100000");

        RuleFor(x => x.CategoryId)
            .MustAsync(async (id, cancellation) =>
                await _categoryRepo.ExistsAsync(id))
            .WithMessage("分类不存在");
    }
}

// 注册
builder.Services.AddValidatorsFromAssemblyContaining<CreateProductCommandValidator>();

// 使用
[HttpPost]
public async Task<IActionResult> Create(
    [FromBody] CreateProductCommand command,
    IValidator<CreateProductCommand> validator)
{
    var result = await validator.ValidateAsync(command);
    if (!result.IsValid)
        return BadRequest(result.Errors.Select(e => e.ErrorMessage));

    var product = await _mediator.Send(command);
    return CreatedAtAction(nameof(Get), new { id = product.Id }, product);
}
```

## 全局异常处理

### 异常中间件

```csharp
public class ExceptionHandlingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ExceptionHandlingMiddleware> _logger;

    public ExceptionHandlingMiddleware(
        RequestDelegate next,
        ILogger<ExceptionHandlingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            await HandleExceptionAsync(context, ex);
        }
    }

    private async Task HandleExceptionAsync(HttpContext context, Exception ex)
    {
        _logger.LogError(ex, "Unhandled exception");

        var response = context.Response;
        response.ContentType = "application/json";

        var (statusCode, message) = ex switch
        {
            NotFoundException => (404, ex.Message),
            ValidationException => (400, ex.Message),
            UnauthorizedException => (401, ex.Message),
            ForbiddenException => (403, ex.Message),
            _ => (500, "An error occurred processing your request")
        };

        response.StatusCode = statusCode;
        await response.WriteAsJsonAsync(new ErrorResponse
        {
            StatusCode = statusCode,
            Message = message,
            TraceId = context.TraceIdentifier
        });
    }
}

public class ErrorResponse
{
    public int StatusCode { get; set; }
    public string Message { get; set; }
    public string TraceId { get; set; }
}
```

### ProblemDetails

```csharp
// ASP.NET Core 内置 ProblemDetails
builder.Services.AddProblemDetails();

public class CustomProblemDetailsMiddleware
{
    public static async Task HandleNotFound(HttpContext context)
    {
        context.Response.StatusCode = 404;
        await context.Response.WriteAsJsonAsync(new
        {
            type = "https://tools.ietf.org/html/rfc7231#section-6.5.4",
            title = "Not Found",
            status = 404,
            detail = "The requested resource was not found"
        });
    }
}
```

## OpenAPI / Swagger

### Swagger 配置

```csharp
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Product API",
        Version = "v1",
        Description = "Product management API",
        Contact = new OpenApiContact
        {
            Name = "API Support",
            Email = "support@example.com"
        }
    });

    // JWT 认证
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Name = "Authorization",
        Type = SecuritySchemeType.Http,
        Scheme = "bearer",
        BearerFormat = "JWT",
        In = ParameterLocation.Header,
        Description = "Enter JWT token"
    });

    options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });

    // XML 注释
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    options.IncludeXmlComments(xmlPath);
});
```

### XML 注释

```csharp
/// <summary>
/// Get a product by ID
/// </summary>
/// <param name="id">Product ID</param>
/// <returns>Product details</returns>
/// <response code="200">Returns the product</response>
/// <response code="404">If product not found</response>
[HttpGet("{id:int}")]
[ProducesResponseType(typeof(ProductDto), 200)]
[ProducesResponseType(404)]
public async Task<ActionResult<ProductDto>> GetProduct(int id)
{
    var product = await _productService.GetByIdAsync(id);
    if (product == null)
        return NotFound();
    return Ok(product);
}
```
