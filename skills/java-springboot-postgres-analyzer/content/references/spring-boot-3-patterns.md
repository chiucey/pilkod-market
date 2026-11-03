# Spring Boot 3.x New Features and Design Patterns

## Java 17+ Features Application

### Record in DTOs

```java
// Traditional DTO class (verbose)
public class UserDTO {
    private Long id;
    private String name;
    private String email;

    public UserDTO() {}

    public UserDTO(Long id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }

    // getters, setters, equals, hashCode, toString...
}

// Spring Boot 3 Recommended: Use Record
public record UserDTO(Long id, String name, String email) {
    // Auto-generated: constructor, getters, equals, hashCode, toString
}
```

### Sealed Classes in Strategy Pattern

```java
public sealed interface PaymentStrategy
    permits CreditCardPayment, PayPalPayment, BankTransferPayment {
    PaymentResult process(BigDecimal amount);
}

public record CreditCardPayment(String cardNumber, String cvv)
    implements PaymentStrategy {
    @Override
    public PaymentResult process(BigDecimal amount) {
        // Credit card processing logic
    }
}

public non-sealed class PayPalPayment implements PaymentStrategy {
    // Can be extended
}
```

## Spring Boot 3 Core Improvements

### 1. Jakarta EE 10 / Servlet 6

```java
// Spring Boot 3 removes javax.* packages
import jakarta.servlet.http.HttpServletRequest;
import jakarta.persistence.*;
import jakarta.validation.*;
```

### 2. Improved Dependency Injection

```java
// Spring Boot 3: Constructor injection (recommended)
@Service
public class UserServiceImpl implements UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;

    public UserServiceImpl(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
}
```

### 3. Spring Security 6 Configuration

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));

        return http.build();
    }
}
```

### 4. RestClient (Replaces RestTemplate)

```java
@Service
public class ExternalApiService {

    private final RestClient restClient;

    public ExternalApiService(RestClient.Builder builder) {
        this.restClient = builder
            .baseUrl("https://api.example.com")
            .defaultHeader("Accept", "application/json")
            .build();
    }

    public UserResponse getUser(Long id) {
        return restClient.get()
            .uri("/users/{id}", id)
            .retrieve()
            .body(UserResponse.class);
    }
}
```

### 5. AOT Compilation Support

```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <configuration>
        <executable>true</executable>
    </configuration>
</plugin>
```

## Recommended Project Structure

```
com.example.myapp/
├── MyApplication.java           # Main application entry
├── config/                      # Configuration classes
│   ├── SecurityConfig.java
│   ├── OpenApiConfig.java
│   └── WebConfig.java
├── controller/                  # REST Controllers
│   └── v1/
│       └── UserController.java
├── service/                     # Business logic
│   ├── UserService.java         # Interface
│   └── impl/
│       └── UserServiceImpl.java # Implementation
├── repository/                  # Data access
│   └── UserRepository.java
├── domain/                      # Domain model
│   ├── entity/
│   │   └── User.java
│   ├── aggregate/
│   │   └── Order.java
│   └── vo/                      # Value Objects
│       └── EmailAddress.java
├── dto/                         # Data transfer objects
│   ├── request/
│   │   └── CreateUserRequest.java
│   └── response/
│       └── UserResponse.java
├── mapper/                      # MapStruct mappers
│   └── UserMapper.java
├── exception/                   # Exception handling
│   ├── GlobalExceptionHandler.java
│   └── ResourceNotFoundException.java
└── event/                       # Domain events
    └── UserCreatedEvent.java
```

## Common Design Patterns

### 1. Domain-Driven Design (DDD) Simplified

```java
@Entity
@Table(name = "orders")
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Embedded
    private OrderDetails details;

    @Enumerated(EnumType.STRING)
    private OrderStatus status;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
    private List<OrderItem> items = new ArrayList<>();

    // Domain methods
    public void addItem(Product product, int quantity) {
        OrderItem item = new OrderItem(product, quantity);
        items.add(item);
        item.setOrder(this);
    }

    public void place() {
        if (items.isEmpty()) {
            throw new IllegalStateException("Cannot place empty order");
        }
        this.status = OrderStatus.PLACED;
    }
}
```

### 2. Event Sourcing Simplified Pattern

```java
@Service
@RequiredArgsConstructor
@Transactional
public class OrderService {

    private final OrderRepository orderRepository;
    private final ApplicationEventPublisher eventPublisher;

    public void placeOrder(OrderCommand command) {
        Order order = Order.create(command.userId(), command.items());
        orderRepository.save(order);

        // Publish domain event
        eventPublisher.publishEvent(new OrderPlacedEvent(order.getId()));
    }
}
```

### 3. Specification Pattern (Complex Queries)

```java
public class OrderSpecifications {

    public static Specification<Order> hasStatus(OrderStatus status) {
        return (root, query, cb) ->
            cb.equal(root.get("status"), status);
    }

    public static Specification<Order> createdAfter(LocalDateTime date) {
        return (root, query, cb) ->
            cb.greaterThan(root.get("createdAt"), date);
    }

    public static Specification<Order> withTotalAmountAbove(BigDecimal amount) {
        return (root, query, cb) ->
            cb.greaterThan(root.get("totalAmount"), amount);
    }
}

// Usage
public interface OrderRepository extends JpaRepository<Order, Long>, JpaSpecificationExecutor<Order> {
}

@Service
public class OrderService {
    private final OrderRepository orderRepository;

    public Page<Order> searchOrders(OrderSearchCriteria criteria) {
        Specification<Order> spec = Specification
            .where(hasStatus(criteria.status()))
            .and(createdAfter(criteria.fromDate()))
            .and(withTotalAmountAbove(criteria.minAmount()));

        return orderRepository.findAll(spec, PageRequest.of(criteria.page(), criteria.size()));
    }
}
```

## Testing Best Practices

```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("Create user - Success")
    void createUser_Success() throws Exception {
        CreateUserRequest request = new CreateUserRequest(
            "John Doe",
            "john@example.com",
            "password123"
        );

        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.name").value("John Doe"))
            .andExpect(jsonPath("$.email").value("john@example.com"))
            .andExpect(jsonPath("$.id").exists());
    }

    @Test
    @DisplayName("Create user - Invalid email format")
    void createUser_InvalidEmail() throws Exception {
        CreateUserRequest request = new CreateUserRequest(
            "John Doe",
            "invalid-email",
            "password123"
        );

        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.errors.email").exists());
    }
}
```

```java
@UnitTest
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private EmailService emailService;

    @InjectMocks
    private UserServiceImpl userService;

    @Test
    void createUser_Success() {
        // Given
        CreateUserCommand command = new CreateUserCommand("John", "john@test.com");
        when(userRepository.existsByEmail(command.email())).thenReturn(false);
        when(userRepository.save(any(User.class))).thenAnswer(inv -> {
            User user = inv.getArgument(0);
            user.setId(1L);
            return user;
        });

        // When
        UserResult result = userService.createUser(command);

        // Then
        assertThat(result.name()).isEqualTo("John");
        verify(emailService).sendWelcomeEmail(any(User.class));
    }
}
```
