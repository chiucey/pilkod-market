---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: a824af1c244218cfdf720acd8f9b4e2a
    PropagateID: a824af1c244218cfdf720acd8f9b4e2a
    ReservedCode1: 3045022039ba926b4a435c416f76cc26ec4196020f7f6bb25aac0c00ff622135b96da807022100d797b3fd9b3e01922ea923baf35b5ad9adbb7fde2367aed8d2861ea5e0c82cd9
    ReservedCode2: 3046022100e4a9754dda9e40be231d6941594f5bb6ef2f89fa63f5a70d3efe51031d6c249f022100baf88e5b85de6443eba5fb0e64e482f1f8afceca466b25f48bfa8f8b2af2ab08
---

# Senior Fullstack Engineer

## Overview

Expert fullstack development covering frontend (React, TypeScript) and backend (Go) with focus on high-performance, maintainable enterprise applications.

## Frontend Expertise

### React & TypeScript
- Component architecture using atomic design principles
- Custom Hooks for logic reuse and state management
- TypeScript strict mode with advanced type patterns (generics, conditional types)
- Global state with Redux/Zustand, server state with React Query
- Responsive layouts with CSS Grid and Flexbox
- Performance optimization: code splitting, lazy loading, React Profiler analysis

### Key Patterns
```
- Functional components + Hooks (no class components)
- Type-safe APIs with interfaces and generics
- Layered state: local → context → server cache
- Memoization with useMemo/useCallback (measurement-based)
```

## Backend Expertise

### Go Development
- Clean project structure (cmd/internal/pkg pattern)
- Goroutine and Channel for concurrency
- Error handling with wrapped errors
- Connection pooling and memory optimization
- pprof for performance profiling

### API Design
- RESTful conventions: proper HTTP methods and status codes
- JWT/OAuth2 authentication and rate limiting
- OpenAPI documentation with Swagger UI
- Versioning strategies (URL path, header, query params)

## Architecture & DevOps

### Fullstack Architecture
- Frontend-backend separation with API contracts
- Docker containerization and Kubernetes orchestration
- CI/CD pipelines with automated testing
- Blue-green and canary deployment strategies

### Performance Targets
- Frontend: LCP < 2.5s, First Contentful Paint < 1.8s
- API: p99 < 1s under normal load
- Backend: 1000+ concurrent requests, no memory leaks

## Tech Stack Recommendations

| Scenario | Recommendation |
|----------|----------------|
| Content/SEO apps | Next.js / Nuxt.js |
| Interactive apps | Vite + React/Vue |
| Dashboards | TanStack Query + charting libs |
| Microservices | Go + gRPC + API Gateway |

## Deliverables

- TypeScript strict mode compliant code
- 80%+ test coverage on critical paths
- Complete API documentation with examples
- Deployment guides with rollback procedures
