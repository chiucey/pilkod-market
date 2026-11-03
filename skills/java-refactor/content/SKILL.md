---
name: java-refactor
description: Java代码重构专家技能。当用户要求重构Java代码、优化代码结构、改善代码质量、提升可读性可维护性时使用。触发短语包括"重构Java代码"、"优化Java代码"、"改善代码质量"、"Java代码审查与重构"、"成为Java重构专家"。
---

# Java代码重构专家技能

## 专业定位

作为Java重构专家，本技能提供**企业级代码重构服务**，确保在保持100%功能兼容性的前提下，实现代码质量的质的提升。

### 核心能力矩阵

| 维度 | 承诺标准 |
|------|----------|
| **功能保持** | 100%功能一致，所有边界条件、异常行为保持不变 |
| **可读性** | 符合Java编码规范，命名见名知意，方法职责单一 |
| **可维护性** | 消除重复，降低耦合，提高内聚 |
| **可扩展性** | 遵循SOLID原则，支持新功能无缝接入 |
| **性能** | 不引入性能退化，保持或优化执行效率 |
| **安全性** | 消除安全漏洞，遵循安全编码最佳实践 |

## 重构金标准

### 1. 功能完整性验证

重构前后必须满足：

```
✅ 输入输出契约完全一致
✅ 边界条件处理完全一致
✅ 异常抛出类型和消息一致
✅ 日志输出行为一致
✅ 线程安全特性一致
✅ 资源管理行为一致
```

### 2. 代码质量度量标准

| 指标 | 警告阈值 | 重构阈值 |
|------|----------|----------|
| 方法行数 | >30行 | >40行 |
| 类行数 | >400行 | >500行 |
| 方法参数 | >3个 | >5个 |
| 圈复杂度 | >8 | >10 |
| 嵌套深度 | >3层 | >4层 |
| 注释占比 | <10% | <5% |

### 3. Java编码规范（强制）

#### 命名规范
```java
// ✅ 正确示例
public class UserAccountService { }
public interface PaymentGateway { }
private static final int MAX_RETRY_COUNT = 3;
private List<User> activeUsers;
public Optional<User> findUserById(Long id) { }
public Stream<Order> getOrdersByStatus(OrderStatus status) { }

// ❌ 错误示例
public class UserService { }  // 模糊不清
public class uSvc { }        // 缩写不当
private int x, y, z;         // 无意义命名
public User get(id) { }      // 参数无命名
```

#### 现代Java特性最佳实践

```java
// ✅ 使用Optional处理空值
public Optional<User> findById(Long id) {
    return Optional.ofNullable(userRepository.findOne(id));
}

// ❌ 避免null检查链
public User findById(Long id) {
    User u = userRepository.findOne(id);
    if (u != null) {
        if (u.getProfile() != null) {
            return u;
        }
    }
    return null;
}

// ✅ 使用Stream API
public List<String> getActiveUserEmails() {
    return users.stream()
        .filter(User::isActive)
        .map(User::getEmail)
        .collect(Collectors.toList());
}

// ❌ 避免冗余循环
public List<String> getActiveUserEmails() {
    List<String> emails = new ArrayList<>();
    for (User user : users) {
        if (user.isActive()) {
            emails.add(user.getEmail());
        }
    }
    return emails;
}

// ✅ 使用try-with-resources
try (Connection conn = dataSource.getConnection();
     PreparedStatement stmt = conn.prepareStatement(sql)) {
    // 使用资源
} catch (SQLException e) {
    // 处理异常
}

// ❌ 避免手动资源管理
Connection conn = null;
PreparedStatement stmt = null;
try {
    conn = dataSource.getConnection();
    stmt = conn.prepareStatement(sql);
} finally {
    if (stmt != null) stmt.close();
    if (conn != null) conn.close();
}

// ✅ 使用record（Java 16+）
public record UserDTO(Long id, String name, String email) { }

// ✅ 使用sealed类（Java 17+）
public sealed interface Shape permits Circle, Rectangle { }
public record Circle(double radius) implements Shape { }
public record Rectangle(double width, double height) implements Shape { }
```

## 重构技术大全

### 初级重构（代码级）

#### 1. 提取方法（Extract Method）
```java
// 重构前
public void processOrder(Order order) {
    // 复杂验证逻辑
    if (order.getCustomer() == null) throw new IllegalArgumentException("...");
    if (order.getItems().isEmpty()) throw new IllegalArgumentException("...");
    for (OrderItem item : order.getItems()) {
        validateItem(item);
    }
    // 计算逻辑
    double subtotal = 0;
    for (OrderItem item : order.getItems()) {
        subtotal += item.getPrice() * item.getQuantity();
    }
    // 更多逻辑...
}

// 重构后
public void processOrder(Order order) {
    validateOrder(order);
    double subtotal = calculateSubtotal(order);
    double discount = calculateDiscount(subtotal);
    OrderResult result = buildOrderResult(order, subtotal, discount);
    persistOrder(result);
}
```

#### 2. 提取类（Extract Class）
```java
// 重构前 - Person类承担过多职责
public class Person {
    private String firstName;
    private String lastName;
    private String street;
    private String city;
    private String zipCode;
    private String phoneNumber;

    public String getFullName() { return firstName + " " + lastName; }
    public String getAddress() { return street + ", " + city + " " + zipCode; }
}

// 重构后 - 职责分离
public class Person {
    private Name name;
    private ContactInfo contactInfo;

    public String getFullName() { return name.getFullName(); }
    public String getAddress() { return contactInfo.getFormattedAddress(); }
}

public record Name(String firstName, String lastName) {
    public String getFullName() { return firstName + " " + lastName; }
}

public record ContactInfo(Address address, PhoneNumber phone) {
    public String getFormattedAddress() {
        return address.getFormatted();
    }
}
```

#### 3. 参数对象（Introduce Parameter Object）
```java
// 重构前
public List<Report> generateReport(Date startDate, Date endDate,
    String department, String reportType, int pageSize,
    boolean includeArchived, String sortBy) {
    // 实现
}

// 重构后
public record ReportRequest(
    DateRange dateRange,
    String department,
    ReportType type,
    int pageSize,
    boolean includeArchived,
    SortField sortBy
) { }

public List<Report> generateReport(ReportRequest request) {
    // 实现 - 更清晰，扩展性更好
}
```

### 中级重构（结构级）

#### 4. 策略模式（Strategy Pattern）
```java
// 重构前 - 复杂的条件判断
public double calculateShipping(ShippingInfo info) {
    if ("STANDARD".equals(info.getMethod())) {
        if (info.getWeight() < 1) return 5.0;
        else if (info.getWeight() < 5) return 10.0;
        else return 20.0;
    } else if ("EXPRESS".equals(info.getMethod())) {
        if (info.getWeight() < 1) return 15.0;
        else if (info.getWeight() < 5) return 30.0;
        else return 60.0;
    }
    throw new UnsupportedOperationException("Unknown shipping method");
}

// 重构后 - 策略模式
public interface ShippingStrategy {
    double calculate(double weight);
    boolean supports(ShippingMethod method);
}

@Service
public class ShippingCalculator {
    private final List<ShippingStrategy> strategies;

    public double calculate(ShippingInfo info) {
        return strategies.stream()
            .filter(s -> s.supports(info.getMethod()))
            .findFirst()
            .orElseThrow(() -> new UnsupportedOperationException(...))
            .calculate(info.getWeight());
    }
}

@Component
public class StandardShipping implements ShippingStrategy {
    @Override
    public double calculate(double weight) {
        return switch ((int)(weight / 5)) {
            case 0 -> 5.0;
            case 1, 2, 3 -> 10.0 + (weight - 5) * 2;
            default -> 20.0 + (weight - 20) * 3;
        };
    }
    @Override
    public boolean supports(ShippingMethod method) {
        return method == ShippingMethod.STANDARD;
    }
}
```

#### 5. 命令模式（Command Pattern）
```java
// 重构前 - 操作分散
public class ActionHandler {
    public void handle(String actionType, Object payload) {
        switch (actionType) {
            case "CREATE": handleCreate(payload); break;
            case "UPDATE": handleUpdate(payload); break;
            case "DELETE": handleDelete(payload); break;
            case "APPROVE": handleApprove(payload); break;
        }
    }
}

// 重构后 - 命令模式
public interface Command {
    Object execute(Object payload);
    boolean supports(String actionType);
}

@Service
public class ActionHandler {
    private final Map<String, Command> commandRegistry;

    public void handle(String actionType, Object payload) {
        Command command = commandRegistry.get(actionType);
        if (command == null) {
            throw new UnsupportedOperationException("Unknown action: " + actionType);
        }
        command.execute(payload);
    }
}

@Component
public class CreateCommand implements Command {
    @Override
    public Object execute(Object payload) {
        return createdEntity;
    }
    @Override
    public boolean supports(String actionType) {
        return "CREATE".equals(actionType);
    }
}
```

#### 6. 模板方法模式（Template Method）
```java
// 重构前 - 算法步骤混合
public void processPayment(Payment payment) {
    if (!validatePayment(payment)) throw new ValidationException(...);
    if (!deductAmount(payment.getAccount(), payment.getAmount())) {
        throw new InsufficientFundsException(...);
    }
    saveTransaction(payment);
    sendNotification(payment);
}

// 重构后 - 模板方法
public abstract class PaymentProcessor {
    public final void processPayment(Payment payment) {
        validate(payment);
        executePayment(payment);
        recordTransaction(payment);
        notifyCustomer(payment);
        onComplete(payment);
    }

    protected abstract void validate(Payment payment);
    protected abstract void executePayment(Payment payment);

    protected void recordTransaction(Payment payment) {
        transactionLog.save(payment);
    }

    protected void notifyCustomer(Payment payment) {
        notificationService.send(payment.getCustomerId(), "Payment processed");
    }

    protected void onComplete(Payment payment) { }
}

public class CreditCardProcessor extends PaymentProcessor {
    @Override
    protected void validate(Payment payment) {
        if (!creditCardValidator.isValid(payment.getCard())) {
            throw new ValidationException("Invalid card");
        }
    }

    @Override
    protected void executePayment(Payment payment) {
        paymentGateway.charge(payment.getCard(), payment.getAmount());
    }
}
```

### 高级重构（架构级）

#### 7. 依赖注入重构
```java
// 重构前 - 硬依赖
public class OrderService {
    private final EmailService emailService = new EmailService();
    private final PaymentGateway paymentGateway = new PaymentGateway();

    public void placeOrder(Order order) {
        // 业务逻辑
    }
}

// 重构后 - 依赖注入
@Service
public class OrderService {
    private final EmailService emailService;
    private final PaymentGateway paymentGateway;

    public OrderService(
            EmailService emailService,
            @Qualifier("stripePaymentGateway") PaymentGateway paymentGateway) {
        this.emailService = emailService;
        this.paymentGateway = paymentGateway;
    }
}
```

#### 8. 构建器模式（Builder Pattern）
```java
// 重构前 - Telescoping Constructor
public class Email {
    private String to;
    private String from;
    private String subject;
    private String body;
    private List<String> cc;
    private Priority priority;

    public Email(String to) { this.to = to; }
    public Email(String to, String from) { this.to = to; this.from = from; }
    public Email(String to, String from, String subject) { /* ... */ }
}

// 重构后 - Builder模式
public class Email {
    private final String to;
    private final String from;
    private final String subject;
    private final List<String> cc;
    private final Priority priority;

    private Email(Builder builder) {
        this.to = builder.to;
        this.from = builder.from;
        this.subject = builder.subject;
        this.cc = builder.cc;
        this.priority = builder.priority;
    }

    public static Builder builder() { return new Builder(); }

    public static class Builder {
        private String to;
        private String from = "default@example.com";
        private String subject = "";
        private List<String> cc = new ArrayList<>();
        private Priority priority = Priority.NORMAL;

        public Builder to(String to) { this.to = to; return this; }
        public Builder from(String from) { this.from = from; return this; }
        public Builder cc(String... cc) { this.cc = Arrays.asList(cc); return this; }
        public Email build() {
            if (to == null || to.isBlank()) {
                throw new IllegalStateException("Recipient is required");
            }
            return new Email(this);
        }
    }
}

// 使用
Email email = Email.builder()
    .to("recipient@example.com")
    .subject("Hello")
    .priority(Priority.HIGH)
    .build();
```

## 代码味道识别与修复

### 必须重构的代码味道

| 代码味道 | 识别特征 | 修复方案 |
|----------|----------|----------|
| **重复代码** | 代码块相同或高度相似 | 提取公共方法/类 |
| **过长方法** | >40行 | 分解为多个小方法 |
| **过大类** | >500行 | 提取子类或协作类 |
| **过长参数** | >5个参数 | 封装为参数对象 |
| **霰弹修改** | 改一处需改多处 | 移动方法或类 |
| **依恋情节** | 过度使用其他类数据 | 移动方法到合适的类 |
| **switch语句** | 重复的switch | 多态或策略模式 |
| **平行继承** | 新增子类需新建其他 | 合并继承层次 |
| **冗余类** | 做的事太少 | 内联或删除 |
| **纯数据类** | 只有getter/setter | 行为移入 |
| **魔法数** | 硬编码数字/字符串 | 使用常量/枚举 |
| **过深嵌套** | >4层if/循环 | 提取方法/卫语句 |

### 反模式识别与修复

#### 反模式1: God Class（上帝类）
```java
// ❌ 一个类做所有事情
public class SystemManager {
    public void doEverything() { /* 10000行代码 */ }
}

// ✅ 重构：分离职责
public class UserManager { }
public class OrderManager { }
public class InventoryManager { }
```

#### 反模式2: Callback Hell（回调地狱）
```java
// ❌ 嵌套过深
asyncOperation1(result1 -> {
    asyncOperation2(result2 -> {
        asyncOperation3(result3 -> {
            // 继续嵌套...
        });
    });
});

// ✅ 重构：使用CompletableFuture
CompletableFuture
    .supplyAsync(this::operation1)
    .thenCompose(this::operation2)
    .thenCompose(this::operation3)
    .thenAccept(this::handleResult);
```

#### 反模式3: Primitive Obsession（原语偏执）
```java
// ❌ 过度使用基本类型
public void createUser(String name, String email, String phone,
    String address, String city, String zip) { }

// ✅ 重构：使用值对象
public void createUser(Name name, Email email, Phone phone, Address address) { }
```

#### 反模式4: Anemic Domain Model（贫血领域模型）
```java
// ❌ 只有getter/setter
public class Order {
    private Long id;
    private List<OrderItem> items;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> items) { this.items = items; }
}

// ✅ 重构：添加领域行为
public class Order {
    private Long id;
    private List<OrderItem> items = new ArrayList<>();

    public Money calculateTotal() {
        return items.stream()
            .map(OrderItem::getSubtotal)
            .reduce(Money.ZERO, Money::add);
    }

    public void addItem(OrderItem item) {
        item.setOrder(this);
        this.items.add(item);
    }

    public boolean isEmpty() {
        return items.isEmpty();
    }
}
```

## 专业重构工作流

### 阶段1：代码诊断

```
1.1 静态分析
    - 运行SonarQube/Checkstyle/PMD
    - 识别圈复杂度、重复代码、代码规范问题

1.2 动态分析
    - 识别热点代码
    - 分析调用链和依赖关系

1.3 问题分类
    - 按严重程度分级（Blocker/Critical/Major/Minor）
    - 按重构难度分级（简单/中等/复杂/架构级）
```

### 阶段2：重构规划

```
2.1 制定重构顺序
    - 优先处理高风险、低复杂度的重构
    - 识别重构依赖关系
    - 确定安全边际

2.2 建立基线
    - 现有测试用例收集
    - 建立基准测试
    - 确定可接受的性能波动范围

2.3 回滚计划
    - Git分支策略
    - 增量部署计划
```

### 阶段3：执行重构

```
3.1 单步执行
    - 每次只做一个重构操作
    - 保持代码在可工作状态

3.2 持续验证
    - 本地运行单元测试
    - 运行静态分析
    - 验证代码覆盖率

3.3 提交管理
    - 原子提交（一个重构操作一个commit）
    - 详细的commit message
```

### 阶段4：质量保证

```
4.1 测试验证
    - 所有测试用例通过
    - 新增边界测试
    - 性能回归测试

4.2 代码审查
    - 对比重构前后
    - 检查SOLID原则
    - 验证设计模式应用

4.3 文档更新
    - 更新API文档
    - 更新架构图
```

## 专业输出格式

### 重构报告模板

```markdown
# Java代码重构报告

## 项目信息
- 项目名称：[名称]
- 重构日期：[日期]
- 重构范围：[文件/模块列表]

## 诊断结果

### 代码质量现状
| 指标 | 重构前 | 重构后 | 改善 |
|------|--------|--------|------|
| 代码行数 | X | Y | Z% |
| 类数量 | X | Y | Z% |
| 平均方法长度 | X | Y | Z% |
| 圈复杂度 | X | Y | Z% |
| 重复代码率 | X% | Y% | Z% |

### 问题清单
| ID | 问题 | 严重性 | 位置 | 修复方案 |
|----|------|--------|------|----------|
| 1 | 过长方法 | Major | X.java:45 | 提取方法 |
| 2 | 重复代码 | Critical | Y.java:100 | 提取公共方法 |

## 重构详情

### [ID-001] 方法提取重构
**文件**: `OrderService.java`
**位置**: 第45-120行

**变更前**:
```java
// 120行的processOrder方法
```

**变更后**:
```java
public void processOrder(Order order) {
    validateOrder(order);
    calculateTotals(order);
    applyDiscounts(order);
    persistOrder(order);
}
```

**改善效果**:
- 方法行数: 120行 → 5行
- 圈复杂度: 15 → 2
- 可读性: 显著提升

## 验证结果

### 测试通过率
- 单元测试: 100% (150/150)
- 集成测试: 100% (45/45)
- 覆盖率: 85% → 88%

### 性能基准
- 响应时间: 基准内
- 内存使用: 无显著变化

## 后续建议

### 短期（1-2周）
- [ ] 补充缺失的单元测试
- [ ] 添加关键方法的JavaDoc

### 中期（1-2月）
- [ ] 引入领域驱动设计(DDD)
- [ ] 考虑微服务拆分
```

## 质量保证清单

### 重构前必查
- [ ] 理解业务逻辑和影响范围
- [ ] 所有测试用例通过
- [ ] 建立代码快照/分支
- [ ] 制定回滚方案

### 重构中必查
- [ ] 每次重构后运行测试
- [ ] 保持代码可编译状态
- [ ] 记录每个变更点
- [ ] 遵循原子提交原则

### 重构后必查
- [ ] 所有测试通过
- [ ] 性能无退化
- [ ] 消除所有警告
- [ ] 更新相关文档
- [ ] 代码审查通过
