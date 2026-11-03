# Project Scaffold Template

## Project: {{project_name}}

### Basic Information

| Field | Value |
|-------|-------|
| Project Name | {{project_name}} |
| Project Type | {{project_type}} |
| Industry | {{industry}} |
| Technology Stack | {{tech_stack}} |
| Created Date | {{created_date}} |
| Version | {{version}} |

## Directory Structure

```
{{project_name}}/
├── src/
│   ├── backend/                 # Backend source code
│   │   ├── api/                 # API layer
│   │   ├── core/                # Core business logic
│   │   ├── models/              # Data models
│   │   ├── services/            # Service layer
│   │   ├── utils/               # Utilities
│   │   └── main.py              # Application entry
│   ├── frontend/               # Frontend source code
│   │   ├── components/          # Reusable components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom hooks
│   │   ├── stores/              # State management
│   │   ├── services/            # API services
│   │   └── App.tsx              # Root component
│   └── shared/                  # Shared code
│       ├── types/               # Type definitions
│       └── constants/           # Constants
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # E2E tests
├── config/
│   ├── development.yaml
│   ├── staging.yaml
│   └── production.yaml
├── scripts/
│   ├── deploy.sh
│   ├── migrate.sh
│   └── seed.sh
├── docs/
│   ├── api/
│   ├── architecture/
│   └── guides/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── package.json
├── pyproject.toml
└── README.md
```

## Technology Stack

### Backend
- Language: {{backend_language}}
- Framework: {{backend_framework}}
- ORM: {{orm}}
- Database: {{database}}
- Cache: {{cache}}

### Frontend
- Framework: {{frontend_framework}}
- UI Library: {{ui_library}}
- State Management: {{state_management}}
- Build Tool: {{build_tool}}

### Infrastructure
- Container: Docker
- CI/CD: {{cicd}}
- Cloud: {{cloud_provider}}
- Monitoring: {{monitoring}}

## Configuration Files

### Backend Configuration (config.yaml)
```yaml
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: true

database:
  type: "postgresql"
  host: "localhost"
  port: 5432
  name: "{{project_name}}"
  pool_size: 20

cache:
  type: "redis"
  host: "localhost"
  port: 6379
  ttl: 3600

security:
  jwt_secret: "${JWT_SECRET}"
  jwt_expiry: 86400
  bcrypt_rounds: 12
```

### Frontend Configuration
```typescript
// src/config/index.ts
export const config = {
  apiUrl: process.env.VITE_API_URL || 'http://localhost:8000',
  environment: process.env.NODE_ENV || 'development',
  features: {
    enableAnalytics: true,
    enableDebug: false,
  },
};
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/register | User registration |
| POST | /api/v1/auth/login | User login |
| POST | /api/v1/auth/refresh | Refresh token |
| POST | /api/v1/auth/logout | User logout |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/users | List users |
| GET | /api/v1/users/:id | Get user by ID |
| PUT | /api/v1/users/:id | Update user |
| DELETE | /api/v1/users/:id | Delete user |

## Testing Strategy

### Unit Tests
- Coverage: >= 80%
- Tools: Jest, Pytest
- Focus: Business logic, utilities

### Integration Tests
- API endpoints
- Database operations
- External services

### E2E Tests
- Critical user flows
- Tools: Playwright, Cypress

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```
# Required
DATABASE_URL=postgresql://user:pass@host:5432/dbname
JWT_SECRET=your-secret-key

# Optional
REDIS_URL=redis://localhost:6379
SENTRY_DSN=https://example@sentry.io/project
```

## Next Steps

1. [ ] Initialize project structure
2. [ ] Configure database migrations
3. [ ] Implement authentication
4. [ ] Build core features
5. [ ] Write tests
6. [ ] Configure CI/CD
7. [ ] Deploy to staging
8. [ ] Deploy to production
