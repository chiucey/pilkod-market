# JPA and PostgreSQL Best Practices Guide

## Entity Design Patterns

### 1. Base Entity Template

```java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @CreatedBy
    @Column(name = "created_by")
    private String createdBy;

    @LastModifiedBy
    @Column(name = "updated_by")
    private String updatedBy;

    @Version
    private Long version;

    // Getters
    public Long getId() { return id; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public String getCreatedBy() { return createdBy; }
    public String getUpdatedBy() { return updatedBy; }
    public Long getVersion() { return version; }
}
```

### 2. Auditing Configuration

```java
@Configuration
@EnableJpaAuditing
public class JpaAuditingConfig {

    @Bean
    public AuditorAware<String> auditorProvider() {
        return () -> Optional.ofNullable(SecurityContextHolder.getContext().getAuthentication())
            .map(Authentication::getName)
            .filter(name -> !name.equals("anonymousUser"))
            .or(() -> Optional.of("system"));
    }
}
```

## Relationship Mapping Best Practices

### 1. One-to-Many Relationship (Avoid N+1)

```java
@Entity
@Table(name = "categories")
public class Category extends BaseEntity {

    @Column(nullable = false)
    private String name;

    @Column(length = 1000)
    private String description;

    // Lazy loading + batch size optimization
    @OneToMany(mappedBy = "category", fetch = FetchType.LAZY)
    @BatchSize(size = 25)
    @OrderBy("name ASC")
    private List<Product> products = new ArrayList<>();
}
```

### 2. Many-to-Many Relationship (Explicit Join Table)

```java
@Entity
@Table(name = "users")
public class User extends BaseEntity {

    @Column(nullable = false)
    private String name;

    // Explicit join table definition
    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles = new HashSet<>();
}
```

### 3. Inheritance Mapping (TPC - Table Per Concrete Class)

```java
@Entity
@Inheritance(strategy = InheritanceType.TABLE_PER_CLASS)
public abstract class Payment extends BaseEntity {

    @Column(nullable = false)
    private BigDecimal amount;

    @Enumerated(EnumType.STRING)
    private PaymentStatus status;
}

@Entity
@Table(name = "credit_card_payments")
public class CreditCardPayment extends Payment {

    @Column(name = "card_number", length = 20)
    private String cardNumber;

    @Column(name = "expiry_date")
    private LocalDate expiryDate;
}

@Entity
@Table(name = "bank_transfer_payments")
public class BankTransferPayment extends Payment {

    @Column(name = "account_number")
    private String accountNumber;

    @Column(name = "bank_code")
    private String bankCode;
}
```

## Query Optimization

### 1. Dynamic Queries (Criteria API)

```java
@Repository
@RequiredArgsConstructor
public class ProductRepositoryImpl implements ProductRepositoryCustom {

    private final EntityManager em;

    @Override
    public Page<Product> search(ProductSearchCriteria criteria) {
        CriteriaBuilder cb = em.getCriteriaBuilder();
        CriteriaQuery<Product> query = cb.createQuery(Product.class);
        Root<Product> root = query.from(Product.class);

        List<Predicate> predicates = new ArrayList<>();

        if (criteria.name() != null) {
            predicates.add(cb.like(cb.lower(root.get("name")),
                "%" + criteria.name().toLowerCase() + "%"));
        }

        if (criteria.minPrice() != null) {
            predicates.add(cb.greaterThanOrEqualTo(root.get("price"),
                criteria.minPrice()));
        }

        if (criteria.categoryId() != null) {
            predicates.add(cb.equal(root.get("category").get("id"),
                criteria.categoryId()));
        }

        query.where(predicates.toArray(new Predicate[0]));

        if (criteria.sortBy() != null) {
            if (criteria.ascending()) {
                query.orderBy(cb.asc(root.get(criteria.sortBy())));
            } else {
                query.orderBy(cb.desc(root.get(criteria.sortBy())));
            }
        }

        TypedQuery<Product> typedQuery = em.createQuery(query);
        typedQuery.setFirstResult((int) criteria.page() * criteria.size());
        typedQuery.setMaxResults(criteria.size());

        // Count query
        CriteriaQuery<Long> countQuery = cb.createQuery(Long.class);
        countQuery.select(cb.count(countQuery.from(Product.class)));
        countQuery.where(predicates.toArray(new Predicate[0]));

        Long total = em.createQuery(countQuery).getSingleResult();

        return new PageImpl<>(typedQuery.getResultList(),
            PageRequest.of(criteria.page(), criteria.size()), total);
    }
}
```

### 2. Projection Queries

```java
// Interface projection
public interface ProductSummary {
    String getName();
    BigDecimal getPrice();
}

public interface ProductDetail {
    String getName();
    BigDecimal getPrice();
    @Value("#{target.category.name}")
    String getCategoryName();
}

// Repository methods
public interface ProductRepository extends JpaRepository<Product, Long> {

    List<ProductSummary> findProjectedByCategoryId(Long categoryId);

    @Query("SELECT p.name AS name, p.price AS price FROM Product p WHERE p.id = :id")
    Optional<ProductDetail> findDetailById(@Param("id") Long id);
}
```

### 3. Entity Graphs

```java
@Entity
@NamedEntityGraph(
    name = "Product.withCategory",
    attributeNodes = @NamedAttributeNode("category")
)
@EntityGraph(value = "Product.withCategory", type = EntityGraph.EntityGraphType.LOAD)
public class Product {
    // ...
}

// Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    @EntityGraph(attributePaths = {"category", "tags"})
    Optional<Product> findWithDetailsById(Long id);
}
```

## PostgreSQL-Specific Features

### 1. JSONB Columns

```java
@Entity
@Table(name = "orders")
public class Order extends BaseEntity {

    @Column(name = "metadata", columnDefinition = "jsonb")
    @Convert(converter = JsonbConverter.class)
    private Map<String, Object> metadata;

    @Column(name = "tags", columnDefinition = "text[]")
    @Convert(converter = StringArrayConverter.class)
    private String[] tags;
}

@Converter
public class JsonbConverter implements AttributeConverter<Map<String, Object>, String> {

    private static final ObjectMapper mapper = new ObjectMapper();

    @Override
    public String convertToDatabaseColumn(Map<String, Object> attribute) {
        try {
            return mapper.writeValueAsString(attribute);
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    public Map<String, Object> convertToEntityAttribute(String dbData) {
        try {
            return mapper.readValue(dbData, new TypeReference<>() {});
        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }
}
```

### 2. JSONB Queries

```java
@Query(value = """
    SELECT * FROM orders o
    WHERE o.metadata->>'source' = :source
    AND o.created_at > :since
    """, nativeQuery = true)
List<Order> findByMetadataSource(@Param("source") String source,
                                   @Param("since") LocalDateTime since);
```

### 3. Array Type Queries

```java
@Query(value = """
    SELECT * FROM products p
    WHERE p.tags && CAST(:tags AS text[])
    """, nativeQuery = true)
List<Product> findByAnyTag(@Param("tags") List<String> tags);
```

## Performance Optimization Checklist

### 1. Index Strategy

```java
@Entity
@Table(name = "products", indexes = {
    @Index(name = "idx_product_name", columnList = "name"),
    @Index(name = "idx_product_category_price", columnList = "category_id, price"),
    @Index(name = "idx_product_created", columnList = "created_at DESC")
})
public class Product {
    // ...
}
```

### 2. Batch Operations

```java
@Service
@RequiredArgsConstructor
public class ProductImportService {

    private final ProductRepository productRepository;
    private final EntityManager entityManager;

    @Transactional
    public void importProducts(List<ProductDTO> products) {
        int batchSize = 50;

        for (int i = 0; i < products.size(); i++) {
            Product product = mapper.toEntity(products.get(i));
            entityManager.persist(product);

            if (i > 0 && i % batchSize == 0) {
                entityManager.flush();
                entityManager.clear();
            }
        }

        entityManager.flush();
        entityManager.clear();
    }
}
```

### 3. Read Optimization

```java
// Read-only transaction optimization
@org.springframework.transaction.annotation.Transactional(readOnly = true)
public List<Product> getActiveProducts() {
    return productRepository.findByActiveTrue();
}

// Set flush mode in transaction
@Service
public class ReportingService {

    @Transactional(readOnly = true)
    public List<MonthlyReport> generateReport(LocalDate startDate) {
        return entityManager.unwrap(Session.class)
            .createStoredProcedureCall("generate_monthly_report")
            .setParameter("start_date", startDate)
            .getResultList();
    }
}
```

## Common Problem Solutions

### 1. LazyInitializationException

```java
// Solution 1: Use JOIN FETCH
@Query("SELECT p FROM Product p LEFT JOIN FETCH p.category WHERE p.id = :id")
Optional<Product> findByIdWithCategory(@Param("id") Long id);

// Solution 2: Use EntityGraph
@EntityGraph(attributePaths = {"category", "images"})
Optional<Product> findWithDetailsById(Long id);

// Solution 3: Use DTO projection
@Query("""
    SELECT new com.example.dto.ProductDTO(
        p.id, p.name, p.price, c.name
    )
    FROM Product p LEFT JOIN p.category c
    WHERE p.id = :id
    """)
Optional<ProductDTO> findDTOById(@Param("id") Long id);
```

### 2. Optimistic Lock Retry

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;

    @Retryable(
        retryFor = OptimisticLockingFailureException.class,
        maxAttempts = 3,
        backoff = @Backoff(delay = 100)
    )
    @Transactional
    public void processOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));

        order.process();
        orderRepository.save(order);
    }
}
```

### 3. Circular References (A->B->A)

```java
@Entity
public class Parent {

    @OneToMany(mappedBy = "parent", cascade = CascadeType.ALL)
    @JsonIgnoreProperties("parent")  // Break cycle
    private List<Child> children;
}

@Entity
public class Child {

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_id")
    @JsonIgnoreProperties({"children", "parent"})  // Break cycle
    private Parent parent;
}
```
