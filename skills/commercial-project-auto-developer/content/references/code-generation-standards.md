# Code Generation Standards Reference

## Universal Standards

### File Header Comment
Every source file should have a header comment:

```python
"""
Module Name

Description of module purpose and responsibilities.

Author: AI Developer
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
Version: 1.0.0
License: MIT
"""
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `UserService`, `PaymentProcessor` |
| Functions | snake_case | `get_user_by_id`, `process_payment` |
| Constants | UPPER_SNAKE | `MAX_RETRY_COUNT`, `API_TIMEOUT` |
| Variables | snake_case | `user_data`, `total_amount` |
| Private Members | _prefix | `_internal_cache` |
| Files | snake_case | `user_service.py`, `payment_processor.py` |
| Database Tables | snake_case | `user_accounts`, `order_items` |
| API Endpoints | kebab-case | `/api/v1/user-profiles` |

### Documentation Standards

#### Functions/Methods
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    Brief description of what the function does.

    More detailed description if needed, explaining the
    behavior and any important considerations.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
        RuntimeError: When operation fails

    Examples:
        >>> result = function_name("test", 42)
        >>> print(result)
        expected_output
    """
```

#### Classes
```python
class ClassName:
    """
    Brief description of the class.

    More detailed description explaining the class's
    purpose, usage, and important notes.

    Attributes:
        attr1: Description of class attribute
        attr2: Description of class attribute
    """

    def __init__(self, param1: Type1, param2: Type2):
        """
        Initialize the class.

        Args:
            param1: Description
            param2: Description
        """
        self.attr1 = param1
        self.attr2 = param2
```

## Error Handling Patterns

### Standard Try-Except Pattern
```python
try:
    result = operation_that_may_fail()
    return result
except SpecificException as e:
    logger.error(f"Expected error: {e}")
    raise CustomError("User message") from e
except Exception as e:
    logger.exception("Unexpected error occurred")
    raise
```

### Context Manager Pattern
```python
with get_resource() as resource:
    resource.use()
    # Cleanup is automatic
```

### Retry Pattern
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def unreliable_operation():
    # Operation with potential transient failures
    pass
```

## Logging Standards

### Log Levels
| Level | Usage |
|-------|-------|
| DEBUG | Detailed debugging information |
| INFO | General operational events |
| WARNING | Potential issues, recoverable errors |
| ERROR | Serious problems, failed operations |
| CRITICAL | System failures, shutdown required |

### Structured Logging
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "user_action",
    user_id=user_id,
    action="login",
    ip_address=request.ip,
    success=True,
    duration_ms=150
)
```

### Logging Anti-Patterns
- ❌ `log.error("Error: " + str(e))`
- ❌ `log.debug("Debug message")` in production
- ❌ Logging sensitive data (passwords, tokens)
- ❌ Not logging exceptions with traceback

## Configuration Management

### Environment Variables
```python
import os
from typing import Optional

class Config:
    """Application configuration from environment."""

    @classmethod
    def get_database_url(cls) -> str:
        return os.getenv("DATABASE_URL", "sqlite:///default.db")

    @classmethod
    def get_log_level(cls) -> str:
        return os.getenv("LOG_LEVEL", "INFO").upper()

    @classmethod
    def is_production(cls) -> bool:
        return os.getenv("ENVIRONMENT") == "production"
```

### Secrets Management
```python
# DO NOT hardcode secrets
# WRONG:
API_KEY = "sk-1234567890abcdef"

# CORRECT:
import os
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable required")
```

## Security Standards

### Input Validation
```python
from pydantic import BaseModel, Field, validator

class UserInput(BaseModel):
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(..., ge=0, le=150)

    @validator('email')
    def validate_email(cls, v):
        v = v.lower().strip()
        if not v:
            raise ValueError('Email cannot be empty')
        return v
```

### SQL Injection Prevention
```python
# WRONG:
query = f"SELECT * FROM users WHERE id = {user_id}"

# CORRECT:
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

### XSS Prevention
```javascript
// In templates, always escape
// WRONG:
<div>{userContent}</div>

// CORRECT:
<div>{escapeHtml(userContent)}</div>

// Or use framework's automatic escaping
```

## Testing Standards

### Test Structure
```python
import pytest

class TestUserService:
    """Tests for UserService"""

    @pytest.fixture
    def service(self):
        """Create service instance for testing"""
        return UserService(mock_repository)

    @pytest.fixture
    def sample_user(self):
        """Create sample user data"""
        return User(id=1, email="test@example.com", name="Test")

    def test_create_user_success(self, service, sample_user):
        """Test successful user creation"""
        result = service.create(sample_user)
        assert result.id is not None
        assert result.email == "test@example.com"

    def test_create_user_duplicate_email(self, service, sample_user):
        """Test handling of duplicate email"""
        service.create(sample_user)
        with pytest.raises(DuplicateEmailError):
            service.create(sample_user)

    @pytest.mark.parametrize("email,expected", [
        ("test@example.com", True),
        ("invalid", False),
        ("", False),
    ])
    def test_email_validation(self, email, expected):
        """Test email validation edge cases"""
        result = validate_email(email)
        assert result == expected
```

### Test Naming
- `test_<unit>_<scenario>_<expected>`
- Examples:
  - `test_user_create_success`
  - `test_user_create_duplicate_email_raises_error`
  - `test_payment_process_valid_card_succeeds`

## Performance Standards

### Database Optimization
```sql
-- Use indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id, created_at DESC);

-- Avoid SELECT *
SELECT id, email, name FROM users WHERE active = true;

-- Use pagination
SELECT * FROM products LIMIT 20 OFFSET 40;
```

### Caching Strategy
```python
from functools import lru_cache
from redis import Redis

redis = Redis()

def get_user_cached(user_id: int) -> User:
    cache_key = f"user:{user_id}"

    # Try cache first
    cached = redis.get(cache_key)
    if cached:
        return deserialize_user(cached)

    # Fetch from database
    user = database.get_user(user_id)

    # Cache for future requests
    redis.setex(cache_key, 3600, serialize_user(user))

    return user
```

### Async Patterns
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def fetch_user_data(user_id: int) -> dict:
    """Fetch user data from multiple sources concurrently"""
    async with asyncio.TaskGroup() as tg:
        basic_task = tg.create_task(fetch_basic_info(user_id))
        activity_task = tg.create_task(fetch_activity(user_id))
        preferences_task = tg.create_task(fetch_preferences(user_id))

    return {
        "basic": basic_task.result(),
        "activity": activity_task.result(),
        "preferences": preferences_task.result(),
    }
```

## Code Review Checklist

Before submitting code for review:

- [ ] Code follows naming conventions
- [ ] All functions have docstrings
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] No hardcoded secrets
- [ ] Input validation implemented
- [ ] SQL queries use parameterized statements
- [ ] Tests cover happy path and edge cases
- [ ] No TODO/FIXME comments left
- [ ] Code is self-documenting
- [ ] Performance considerations addressed
- [ ] Security implications reviewed
