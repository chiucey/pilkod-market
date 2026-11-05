---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: d32d9f9aef0e4de35480ed917c83bc3d
    PropagateID: d32d9f9aef0e4de35480ed917c83bc3d
    ReservedCode1: 304502202e49ddf20bdf3155790c4f361362d74924a9ba65c7cdd76ff8f4db1736dd6af2022100e0cba797ff0f3e00e83203f3160d20f3d43cdbb3620bc7363b783ab5e053935f
    ReservedCode2: 304402205683dc70362755195b862b6b0a2bfca0d4a186896f66a1257c20af6054c7746302200210fbb02f6abc9e74ff3d1dc47cdfeacf79cc1f1bda51063960e200811e1cc8
description: Professional skill for building programming environments and designing software architecture. Use when users ask to set up development environments, configure Node.js/Git/Docker tools, design software architecture, implement CI/CD pipelines, or need guidance on modern development workflows. Trigger phrases include "setup development environment", "configure Node.js", "design software architecture", "build CI/CD pipeline", "docker environment", "monorepo setup".
name: dev-env-architect
---

# Development Environment & Architecture Builder

A comprehensive skill for setting up modern development environments and designing robust software architectures. This skill integrates best practices for Node.js development, version control, containerization, CI/CD pipelines, testing strategies, and cloud-native architectures.

## Core Capabilities

This skill provides expert guidance across multiple domains:

- **Environment Setup**: Node.js installation, version management, package managers
- **Version Control**: Git workflows, branching strategies, collaboration
- **Containerization**: Docker configuration, Dev Containers, orchestration
- **CI/CD**: Pipeline design, automation, deployment strategies
- **Testing**: Unit, integration, E2E testing frameworks
- **Security**: Vulnerability scanning, dependency auditing, secure coding
- **Architecture**: Microservices, monoliths, clean architecture patterns
- **Cloud Platforms**: AWS, Azure, GCP, serverless deployment

## Quick Reference

### Development Environment Checklist

```
[ ] Install Node.js (LTS v22.x recommended)
[ ] Configure package manager (npm/yarn/pnpm)
[ ] Setup Git with appropriate hooks
[ ] Configure IDE (VSCode/WebStorm)
[ ] Setup Docker for containerization
[ ] Implement CI/CD pipeline
[ ] Configure testing framework
[ ] Setup security scanning
[ ] Define architecture patterns
[ ] Document decisions (ADR)
```

### Essential Commands Reference

#### Node.js & npm

```bash
# Node.js version management
nvm install 22 && nvm use 22
node -v && npm -v

# Package management
npm install           # Install dependencies
npm ci               # Clean install from lock
pnpm install         # Fast, disk-efficient

# Global tools
npm install -g npm@latest
npm config set registry <registry-url>
```

#### Git Workflow

```bash
# Branch management
git checkout -b feature/your-feature
git add -p              # Interactive staging
git commit -m "feat(scope): description"

# Collaboration
git fetch upstream
git merge upstream/main
git push -u origin feature/your-feature

# GitHub Actions trigger
git push origin main    # CI runs automatically
```

#### Docker Operations

```bash
# Build and run
docker build -t myapp:latest .
docker run -d -p 3000:3000 myapp

# Docker Compose
docker compose up -d
docker compose logs -f
docker compose down -v
```

## Architecture Patterns

### Clean Architecture Structure

```
src/
├── controllers/     # HTTP handlers, route definitions
├── services/       # Business logic layer
├── repositories/    # Data access abstraction
├── models/         # Domain entities
├── middleware/     # Express middleware
├── config/         # Environment configuration
├── utils/          # Pure utility functions
└── index.js       # Application entry point
```

### Layered Responsibilities

| Layer | Responsibility | Dependencies |
|-------|---------------|--------------|
| Controllers | HTTP request/response | Services |
| Services | Business logic | Repositories, Domain |
| Repositories | Data access | Database clients |
| Models | Domain entities | None |

### API Design Principles

```javascript
// RESTful resource naming
GET    /api/users         # List users
GET    /api/users/:id     # Get single user
POST   /api/users         # Create user
PUT    /api/users/:id     # Update user
DELETE /api/users/:id     # Delete user

// Versioning strategy
/api/v1/users   # URL path versioning
/api/users?v=2  # Query parameter (alternative)
```

## Reference Files

This skill includes comprehensive reference files for detailed guidance:

| Reference | Description | When to Use |
|-----------|-------------|-------------|
| `references/nodejs.md` | Node.js setup, npm configuration, version management | Setting up Node.js environments |
| `references/git.md` | Git workflows, branching strategies, hooks | Version control configuration |
| `references/docker.md` | Container setup, Compose, Dev Containers | Containerization needs |
| `references/vscode.md` | IDE configuration, extensions, debugging | Development environment setup |
| `references/cicd.md` | CI/CD pipeline examples, GitHub Actions, GitLab CI | Automation and deployment |
| `references/testing.md` | Jest, Vitest, Cypress, Playwright | Testing strategy implementation |
| `references/security.md` | SAST/DAST tools, dependency scanning | Security hardening |
| `references/cloud-platforms.md` | AWS, Azure, GCP, Kubernetes | Cloud deployment |
| `references/software-architecture.md` | Architecture patterns, API design | System design decisions |
| `references/monorepo.md` | pnpm workspaces, Turborepo, Nx, Lerna | Multi-package projects |

## Workflow Orchestration

### Environment Setup Workflow

```
1. Assess Requirements
   ├── Identify technology stack
   ├── Define environment scope
   └── Check existing configurations

2. Install & Configure
   ├── Node.js version manager setup
   ├── Package manager installation
   ├── Git configuration
   └── IDE setup with extensions

3. Containerization (Optional)
   ├── Dockerfile creation
   ├── Docker Compose setup
   └── Dev Container configuration

4. Testing Infrastructure
   ├── Test framework selection
   ├── CI/CD pipeline setup
   └── Security scanning integration

5. Validation
   ├── Environment smoke tests
   ├── Dependency audit
   └── Performance baseline
```

### Architecture Design Workflow

```
1. Requirements Analysis
   ├── Functional requirements
   ├── Non-functional requirements
   └── Constraints identification

2. Architecture Selection
   ├── Monolith vs Microservices
   ├── Layered vs Clean Architecture
   └── Communication patterns

3. Component Design
   ├── Service boundaries
   ├── Data ownership
   └── API contracts

4. Implementation Planning
   ├── Technology choices
   ├── Team structure
   └── Migration strategy

5. Documentation
   ├── Architecture Decision Records
   ├── API documentation
   └── Runbooks
```

## Best Practices

### Environment Configuration

- Use `.env.example` for documentation, keep actual `.env` in `.gitignore`
- Leverage `nvm` or `fnm` for Node.js version management
- Prefer `pnpm` for monorepo projects (disk efficiency)
- Configure ESLint and Prettier early in project lifecycle

### Git Workflow

- Use Conventional Commits: `feat(scope): description`
- Protect main branch with required reviews
- Implement pre-commit hooks for linting and testing
- Keep feature branches short-lived (max 1-2 weeks)

### Docker Best Practices

- Use multi-stage builds for smaller images
- Run as non-root user in containers
- Leverage build cache with proper layer ordering
- Use specific version tags, avoid `latest`

### Security Checklist

- Run `npm audit` in CI pipeline
- Implement dependency pinning with lock files
- Use SAST tools (ESLint security plugin)
- Enable DAST scanning for running applications
- Configure security headers (CSP, HSTS, etc.)

## Troubleshooting Guide

### Common Issues & Solutions

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| `EACCES` permission error | npm global directory ownership | Configure npm prefix or use nvm |
| Docker build cache invalid | Incorrect layer ordering | Move `COPY package*.json` before `COPY .` |
| Git merge conflicts | Concurrent branch edits | Rebase before merge, communicate with team |
| CI pipeline timeout | Long-running tests | Optimize tests, use caching |
| Memory issues in Node | Memory leaks | Use `--max-old-space-size`, profile memory |

### Debugging Techniques

1. **Local Development**
   - Use VSCode debugger with breakpoints
   - Enable source maps for transpiled code
   - Use `console.log` sparingly, prefer structured logging

2. **Container Issues**
   - Check logs: `docker compose logs -f service-name`
   - Inspect container: `docker exec -it container sh`
   - Volume mounts: Verify paths are correct

3. **CI/CD Failures**
   - Re-run failed jobs after checking logs
   - Use artifact caching effectively
   - Implement proper error handling in scripts

## Integration Examples

### VSCode Dev Container Setup

```json
// .devcontainer/devcontainer.json
{
  "name": "Node.js Development",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:22",
  "forwardPorts": [3000],
  "postCreateCommand": "npm install",
  "customizations": {
    "vscode": {
      "extensions": ["dbaeumer.vscode-eslint"]
    }
  }
}
```

### GitHub Actions CI Pipeline

```yaml
name: CI Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm audit --audit-level=moderate
```

### Docker Multi-Stage Build

```dockerfile
# Build stage
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY --from=builder /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

## Additional Resources

- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [12-Factor App](https://12factor.net/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## Skill Metadata

| Attribute | Value |
|-----------|-------|
| Skill ID | dev-env-architect |
| Version | 1.0.0 |
| Category | Development Infrastructure |
| Tags | nodejs, git, docker, cicd, architecture, testing, security |
| Complexity | Expert |
| Update Frequency | Quarterly |

---

*This skill provides guidance based on industry best practices. Always adapt recommendations to your specific project requirements and organizational constraints.*
