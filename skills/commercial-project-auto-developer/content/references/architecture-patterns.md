# Architecture Patterns Guide

## Common Patterns

### 1. Layered Architecture

```
┌─────────────────────────┐
│     Presentation        │
│    (Controllers, UI)    │
├─────────────────────────┤
│     Application         │
│    (Use Cases, Services)│
├─────────────────────────┤
│       Domain           │
│   (Entities, Logic)     │
├─────────────────────────┤
│    Infrastructure       │
│ (DB, External Services) │
└─────────────────────────┘
```

**Best for:** Standard business applications, CRUD-heavy systems

### 2. Microservices Architecture

```
┌────────────────────────────────────────────┐
│              API Gateway                   │
├──────────┬──────────┬──────────┬─────────┤
│  User    │  Order   │ Payment  │ Product │
│ Service  │ Service  │ Service  │ Service │
├──────────┴──────────┴──────────┴─────────┤
│           Message Queue (Kafka)           │
├─────────────────────────────────────────┤
│              Data Store                  │
└─────────────────────────────────────────┘
```

**Best for:** Large-scale systems, multiple teams, scaling requirements

### 3. Event-Driven Architecture

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Producer │────>│  Event   │────>│ Consumer │
│          │     │  Broker  │     │          │
└──────────┘     └──────────┘     └──────────┘
     │                                  │
     └──────────── Event Bus ◄─────────┘
```

**Best for:** Real-time systems, loosely coupled components

### 4. CQRS (Command Query Responsibility Segregation)

```
┌─────────────┐         ┌─────────────┐
│  Commands   │         │   Queries   │
│   (Write)  │         │   (Read)    │
└──────┬──────┘         └──────┬──────┘
       │                       │
       v                       v
┌─────────────┐         ┌─────────────┐
│ Write DB    │         │  Read DB   │
│ (Primary)   │───────> │ (Optimized)│
└─────────────┘ Sync    └─────────────┘
```

**Best for:** High read/write ratios, complex domain models

### 5. Hexagonal Architecture (Ports & Adapters)

```
                    ┌─────────────────┐
                    │    Application  │
                    │     Core        │
                    │   (Domain)      │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
    │ Primary │         │ Ports   │         │Secondary│
    │ Adapter │         │(Interface│         │ Adapter │
    │ (API)   │         │         │         │ (DB)    │
    └─────────┘         └─────────┘         └─────────┘
```

**Best for:** Testable, maintainable, framework-agnostic code

## Design Patterns by Category

### Creational Patterns

| Pattern | Use Case | Implementation |
|---------|----------|----------------|
| Singleton | Database connection | Instance cached, thread-safe |
| Factory | Object creation | Abstract factory for DB types |
| Builder | Complex objects | Query builders, request builders |
| Prototype | Object cloning | Cache warmed from template |

### Structural Patterns

| Pattern | Use Case | Implementation |
|---------|----------|----------------|
| Adapter | Legacy integration | API wrapper classes |
| Decorator | Logging, caching | Middleware pattern |
| Facade | Simplified API | Service layer |
| Proxy | Access control | Auth middleware |

### Behavioral Patterns

| Pattern | Use Case | Implementation |
|---------|----------|----------------|
| Strategy | Multiple algorithms | Configurable validators |
| Observer | Event handling | Event listeners |
| Command | Undo/redo | Action classes |
| State | Workflows | State machines |

## Database Patterns

### Repository Pattern
```python
class UserRepository:
    """Abstract data access for users"""

    def find_by_id(self, id: str) -> Optional[User]:
        pass

    def find_by_email(self, email: str) -> Optional[User]:
        pass

    def save(self, user: User) -> User:
        pass

    def delete(self, id: str) -> None:
        pass
```

### Unit of Work Pattern
```python
class UnitOfWork:
    """Transaction management"""

    def __enter__(self):
        self.users = UserRepository()
        self.orders = OrderRepository()
        return self

    def commit(self):
        # Commit transaction
        pass

    def rollback(self):
        # Rollback transaction
        pass
```

### CQRS Pattern
```python
# Command side
class CreateUserCommand:
    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name

# Query side
class UserQueryHandler:
    def get_user_summary(self, user_id):
        # Optimized read query
        return self.read_db.query(UserSummary).get(user_id)
```

## API Patterns

### RESTful Design
```
GET    /users          - List users
GET    /users/:id      - Get user
POST   /users          - Create user
PUT    /users/:id      - Update user
DELETE /users/:id      - Delete user
```

### Versioning Strategy
```
/api/v1/users
/api/v2/users
```

### Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "next": "/users?page=2",
    "prev": null
  }
}
```

## Security Patterns

### Zero Trust
- Never trust, always verify
- Least privilege access
- Micro-segmentation

### Defense in Depth
```
┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
│ WAF │──>│ IDS │──>│ Auth│──>│ App │
└─────┘   └─────┘   └─────┘   └─────┘
```

### Circuit Breaker
```python
@circuit_breaker(failure_threshold=5, timeout=30)
def call_external_service():
    return external_api.request()
```

## Scalability Patterns

### Database Scaling
- Read replicas
- Sharding
- Partitioning
- Connection pooling

### Caching Strategy
```
┌──────┐    ┌──────┐    ┌──────┐
│ L1   │───>│ L2   │───>│ L3   │
│Memory│    │ Redis│    │ DB   │
└──────┘    └──────┘    └──────┘
```

### Load Balancing
- Round robin
- Least connections
- IP hashing
- Health checks

## Selection Guide

| Requirement | Recommended Pattern |
|-------------|---------------------|
| Simple CRUD app | Layered |
| Multiple teams | Microservices |
| Real-time updates | Event-driven |
| High read volume | CQRS |
| Complex business logic | Hexagonal |
| Distributed transactions | Saga |
