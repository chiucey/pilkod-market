# Java重构设计模式完全指南

## SOLID原则详解

### S - 单一职责原则（Single Responsibility Principle）

**定义**：一个类应该只有一个引起它变化的原因。

**违反信号**：
- 类名包含"Manager"、"Handler"、"Service"、"Util"等多重概念
- 类的实例变量有多个无关联的分组
- 修改类时经常需要同时修改多个职责

**示例**：
```java
// ❌ 违反SRP - User类承担多重职责
public class User {
    private String name;
    private String email;

    public void saveUser() { /* 数据库操作 */ }
    public void sendEmail() { /* 发送邮件 */ }
    public void generateReport() { /* 生成报表 */ }
    public void calculateStatistics() { /* 统计分析 */ }
}

// ✅ 遵循SRP - 职责分离
public class User {
    private String name;
    private String email;
}

@Repository
public class UserRepository {
    public void save(User user) { /* 数据库操作 */ }
    public Optional<User> findById(Long id) { /* 查询 */ }
}

@Service
public class EmailService {
    public void sendEmail(User user, String subject, String body) { /* 发送 */ }
}

@Service
public class ReportService {
    public Report generateUserReport(User user) { /* 生成报表 */ }
}

@Service
public class StatisticsService {
    public UserStatistics calculateStatistics(User user) { /* 统计 */ }
}
```

### O - 开闭原则（Open-Closed Principle）

**定义**：软件实体应该对扩展开放，对修改关闭。

**违反信号**：
- 添加新功能时需要修改现有类
- 存在大量条件语句处理不同类型
- 类型检查（instanceof）遍布代码

**示例**：
```java
// ❌ 违反OCP - 新增形状需要修改方法
public double calculateArea(String shapeType) {
    if ("circle".equals(shapeType)) {
        return Math.PI * radius * radius;
    } else if ("rectangle".equals(shapeType)) {
        return width * height;
    }
    throw new IllegalArgumentException("Unknown shape");
}

// ✅ 遵循OCP - 使用多态
public interface Shape {
    double calculateArea();
}

public record Circle(double radius) implements Shape {
    @Override
    public double calculateArea() {
        return Math.PI * radius * radius;
    }
}

public record Rectangle(double width, double height) implements Shape {
    @Override
    public double calculateArea() {
        return width * height;
    }
}

public class AreaCalculator {
    public double calculateArea(Shape shape) {
        return shape.calculateArea();
    }
}
```

### L - 里氏替换原则（Liskov Substitution Principle）

**定义**：子类必须能够替换其父类而不改变程序行为。

**违反信号**：
- 子类需要override父类方法并抛异常
- 子类override方法时做更严格的验证
- 子类的方法有副作用

**示例**：
```java
// ❌ 违反LSP - 正方形继承矩形
public class Rectangle {
    protected int width;
    protected int height;

    public void setWidth(int width) { this.width = width; }
    public void setHeight(int height) { this.height = height; }
    public int getArea() { return width * height; }
}

public class Square extends Rectangle {
    @Override
    public void setWidth(int width) {
        this.width = width;
        this.height = width; // 违反LSP！
    }

    @Override
    public void setHeight(int height) {
        this.width = height;
        this.height = height; // 违反LSP！
    }
}

// ✅ 遵循LSP - 使用接口
public interface Shape {
    int getArea();
}

public class Rectangle implements Shape {
    private final int width;
    private final int height;

    public Rectangle(int width, int height) {
        this.width = width;
        this.height = height;
    }

    @Override
    public int getArea() { return width * height; }
}

public class Square implements Shape {
    private final int side;

    public Square(int side) { this.side = side; }

    @Override
    public int getArea() { return side * side; }
}
```

### I - 接口隔离原则（Interface Segregation Principle）

**定义**：不应该强迫客户依赖它不使用的方法。

**违反信号**：
- 接口有大量方法
- 实现类需要实现不需要的方法
- 使用接口的地方经常只需要其中几个方法

**示例**：
```java
// ❌ 违反ISP - 一个大接口
public interface Machine {
    void print();
    void fax();
    void scan();
    void staple();
    void collate();
}

public class SimplePrinter implements Machine {
    @Override
    public void print() { /* 打印 */ }

    @Override
    public void fax() { throw new UnsupportedOperationException(); }
    @Override
    public void scan() { throw new UnsupportedOperationException(); }
    @Override
    public void staple() { throw new UnsupportedOperationException(); }
    @Override
    public void collate() { throw new UnsupportedOperationException(); }
}

// ✅ 遵循ISP - 拆分为多个小接口
public interface Printer { void print(); }
public interface FaxMachine { void fax(); }
public interface Scanner { void scan(); }
public interface Stapler { void staple(); }
public interface Collator { void collate(); }

public class SimplePrinter implements Printer {
    @Override
    public void print() { /* 打印 */ }
}

public class MultiFunctionPrinter implements Printer, FaxMachine, Scanner {
    @Override
    public void print() { /* 打印 */ }
    @Override
    public void fax() { /* 传真 */ }
    @Override
    public void scan() { /* 扫描 */ }
}
```

### D - 依赖倒置原则（Dependency Inversion Principle）

**定义**：高层模块不应该依赖低层模块，两者都应该依赖抽象。

**违反信号**：
- 直接new具体类
- 方法参数是具体类而非接口
- 静态工厂直接返回具体类

**示例**：
```java
// ❌ 违反DIP - 直接依赖具体实现
public class OrderService {
    private final MySQLOrderRepository repository = new MySQLOrderRepository();

    public void saveOrder(Order order) {
        repository.save(order);
    }
}

// ✅ 遵循DIP - 依赖抽象
public interface OrderRepository {
    void save(Order order);
    Optional<Order> findById(Long id);
    List<Order> findAll();
}

@Service
public class OrderService {
    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }

    public void saveOrder(Order order) {
        repository.save(order);
    }
}

@Repository
public class MySQLOrderRepository implements OrderRepository {
    @Override
    public void save(Order order) { /* MySQL保存 */ }
    @Override
    public Optional<Order> findById(Long id) { /* MySQL查询 */ }
    @Override
    public List<Order> findAll() { /* MySQL查询 */ }
}

@Repository
public class MongoOrderRepository implements OrderRepository {
    @Override
    public void save(Order order) { /* MongoDB保存 */ }
    @Override
    public Optional<Order> findById(Long id) { /* MongoDB查询 */ }
    @Override
    public List<Order> findAll() { /* MongoDB查询 */ }
}
```

## 常用重构模式

### 1. 提取方法（Extract Method）

**目的**：将长方法拆分为多个短方法

**适用场景**：
- 方法超过40行
- 方法有多个职责
- 代码块需要重复使用

**示例**：
```java
// 重构前
public void processOrder(Order order) {
    if (order == null) throw new IllegalArgumentException("订单不能为空");
    if (order.getItems().isEmpty()) throw new IllegalArgumentException("订单必须包含商品");
    for (OrderItem item : order.getItems()) {
        if (item.getQuantity() <= 0) throw new IllegalArgumentException("数量必须大于0");
    }
    double total = 0;
    for (OrderItem item : order.getItems()) {
        total += item.getPrice() * item.getQuantity();
    }
    if (total > 1000) total = total * 0.9;
    order.setTotal(total);
    orderRepository.save(order);
}

// 重构后
public void processOrder(Order order) {
    validateOrder(order);
    double total = calculateTotal(order);
    double discountedTotal = applyDiscount(total);
    saveOrder(order, discountedTotal);
}

private void validateOrder(Order order) {
    if (order == null) throw new IllegalArgumentException("订单不能为空");
    if (order.getItems().isEmpty()) throw new IllegalArgumentException("订单必须包含商品");
    order.getItems().forEach(this::validateOrderItem);
}

private void validateOrderItem(OrderItem item) {
    if (item.getQuantity() <= 0) throw new IllegalArgumentException("数量必须大于0");
}

private double calculateTotal(Order order) {
    return order.getItems().stream()
        .mapToDouble(item -> item.getPrice() * item.getQuantity())
        .sum();
}

private double applyDiscount(double total) {
    return total > 1000 ? total * 0.9 : total;
}

private void saveOrder(Order order, double total) {
    order.setTotal(total);
    orderRepository.save(order);
}
```

### 2. 提取类（Extract Class）

**目的**：将大类拆分为小类

**适用场景**：
- 类超过500行
- 类有多个职责
- 多个实例变量可以归为一组

### 3. 引入参数对象（Introduce Parameter Object）

**目的**：将相关参数封装为对象

**适用场景**：
- 方法参数超过3个
- 参数有内在关联
- 参数需要在多处传递

**示例**：
```java
// 重构前
public List<Report> generateReport(Date startDate, Date endDate,
    String department, String reportType, int pageSize) { }

// 重构后
public record ReportRequest(
    DateRange dateRange,
    String department,
    ReportType type,
    int pageSize
) { }

public List<Report> generateReport(ReportRequest request) { }
```

### 4. 策略模式（Strategy Pattern）

**目的**：替换复杂的条件语句

**适用场景**：
- 存在多种算法变体
- 需要在运行时选择算法
- 条件判断逻辑复杂

**示例**：
```java
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

### 5. 工厂模式（Factory Pattern）

**目的**：封装对象创建逻辑

**适用场景**：
- 对象创建逻辑复杂
- 需要统一创建入口
- 创建过程需要验证或配置

### 6. 观察者模式（Observer Pattern）

**目的**：解耦发布-订阅关系

**适用场景**：
- 一个对象变化需要通知多个对象
- 需要异步通知
- 需要动态订阅/退订

**示例**：
```java
public interface Observer<T> {
    void update(T event);
}

public class EventBus {
    private Map<Class<?>, List<Observer<?>>> observers = new HashMap<>();

    public <T> void subscribe(Class<T> eventType, Observer<T> observer) {
        observers.computeIfAbsent(eventType, k -> new ArrayList<>()).add(observer);
    }

    public <T> void publish(T event) {
        List<Observer<?>> list = observers.get(event.getClass());
        if (list != null) {
            for (Observer<?> observer : list) {
                ((Observer<T>) observer).update(event);
            }
        }
    }
}
```

### 7. 装饰器模式（Decorator Pattern）

**目的**：动态添加功能

**适用场景**：
- 需要在运行时添加功能
- 功能可以组合
- 继承会导致类爆炸

**示例**：
```java
public interface DataSource {
    void writeData(String data);
    String readData();
}

public abstract class DataSourceDecorator implements DataSource {
    protected DataSource wrappee;

    public DataSourceDecorator(DataSource wrappee) { this.wrappee = wrappee; }
}

public class EncryptionDecorator extends DataSourceDecorator {
    public EncryptionDecorator(DataSource wrappee) { super(wrappee); }

    @Override
    public void writeData(String data) {
        super.writeData(encrypt(data));
    }

    @Override
    public String readData() {
        return decrypt(super.readData());
    }

    private String encrypt(String data) { /* 加密逻辑 */ return data; }
    private String decrypt(String data) { /* 解密逻辑 */ return data; }
}

// 使用
DataSource dataSource = new FileDataSource("data.txt");
dataSource = new EncryptionDecorator(dataSource);
dataSource = new CompressionDecorator(dataSource);
```

## 代码味道（Code Smells）

### 需要重构的信号

1. **重复代码（Duplicated Code）**
   - 同一代码块出现在多个地方
   - **修复**：提取公共方法/类

2. **过长方法（Long Method）**
   - 方法行数超过40行
   - **修复**：分解为多个小方法

3. **过大类（Large Class）**
   - 类行数超过500行
   - **修复**：提取子类或协作类

4. **过长参数列表（Long Parameter List）**
   - 参数超过5个
   - **修复**：封装为参数对象

5. **过多注释（Comments）**
   - 需要注释解释的代码通常意味着代码本身不够清晰
   - **修复**：重构代码使其自解释

6. **霰弹式修改（Shotgun Surgery）**
   - 一个变化需要修改多个类
   - **修复**：移动方法或类到合适的模块

7. **依恋情节（Feature Envy）**
   - 一个类过多依赖另一个类的数据
   - **修复**：移动方法到合适的类

8. **switch语句（Switch Statements）**
   - 重复的switch语句
   - **修复**：多态或策略模式

9. **平行继承（Parallel Inheritance）**
   - 新增子类时需要新建其他子类
   - **修复**：合并继承层次

10. **冗余类（冗余类）**
    - 做的事太少
    - **修复**：内联或删除

11. **纯数据类（Data Class）**
    - 只有getter/setter
    - **修复**：将行为移入

12. **魔法数（Magic Numbers）**
    - 硬编码的数字/字符串
    - **修复**：使用常量或枚举

## 反模式识别

### 1. God Class（上帝类）

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

### 2. Callback Hell（回调地狱）

```java
// ❌ 嵌套过深
asyncOperation1(result1 -> {
    asyncOperation2(result2 -> {
        asyncOperation3(result3 -> { /* 继续嵌套... */ });
    });
});

// ✅ 重构：使用CompletableFuture
CompletableFuture.supplyAsync(this::operation1)
    .thenCompose(this::operation2)
    .thenCompose(this::operation3)
    .thenAccept(this::handleResult);
```

### 3. Primitive Obsession（原语偏执）

```java
// ❌ 过度使用基本类型
public void createUser(String name, String email, String phone,
    String address, String city, String zip) { }

// ✅ 重构：使用值对象
public void createUser(Name name, Email email, Phone phone, Address address) { }
```

### 4. Anemic Domain Model（贫血领域模型）

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

    public boolean isEmpty() { return items.isEmpty(); }
}
```

## 模式选择指南

| 问题 | 推荐模式 |
|------|----------|
| 需要创建对象但不确定具体类 | 工厂方法/抽象工厂 |
| 需要创建复杂对象 | 构建器 |
| 需要确保单一实例 | 单例 |
| 需要统一接口访问子系统 | 门面 |
| 需要动态添加功能 | 装饰器 |
| 需要控制访问 | 代理 |
| 需要处理不同算法变体 | 策略 |
| 需要将请求封装 | 命令 |
| 需要状态相关行为 | 状态 |
| 需要模板化流程 | 模板方法 |
| 需要处理对象层次 | 组合 |
| 需要一对多通知 | 观察者 |

## 现代Java特性应用

### record（Java 16+）

```java
// 替代传统的值对象类
public record UserDTO(Long id, String name, String email) {
    // 自动生成：equals(), hashCode(), toString()
    // 自动生成：getter方法（name(), email()）
}

// 带验证的record
public record Email(String value) {
    public Email {
        if (!value.contains("@")) {
            throw new IllegalArgumentException("Invalid email");
        }
    }
}
```

### sealed类（Java 17+）

```java
public sealed interface Shape permits Circle, Rectangle, Triangle {
    double area();
}

public record Circle(double radius) implements Shape {
    @Override
    public double area() { return Math.PI * radius * radius; }
}

public record Rectangle(double width, double height) implements Shape {
    @Override
    public double area() { return width * height; }
}

public non-sealed class Triangle implements Shape {
    // 可以被扩展
}
```

### switch表达式（Java 14+）

```java
// 旧式switch
int result = 0;
switch (day) {
    case MONDAY:
    case FRIDAY:
    case SUNDAY:
        result = 6;
        break;
    case TUESDAY:
        result = 7;
        break;
    default:
        result = 8;
}

// 新式switch表达式
int result = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> 6;
    case TUESDAY -> 7;
    default -> 8;
};
```
