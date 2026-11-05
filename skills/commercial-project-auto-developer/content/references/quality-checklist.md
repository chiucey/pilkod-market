# Quality Assurance Checklist

## Pre-Development Checklist

- [ ] Requirements documented and approved
- [ ] Architecture design reviewed
- [ ] Technology stack finalized
- [ ] Security requirements identified
- [ ] Performance requirements defined
- [ ] Scalability requirements assessed

## Code Quality Checklist

### General
- [ ] Code follows style guide
- [ ] No hardcoded secrets
- [ ] No TODO/FIXME in production code
- [ ] Consistent naming conventions
- [ ] Proper indentation and formatting
- [ ] No commented-out code

### Functions/Methods
- [ ] All public methods documented
- [ ] Proper error handling
- [ ] Input validation
- [ ] Output sanitization
- [ ] Return type documented
- [ ] Side effects documented

### Classes
- [ ] Single responsibility
- [ ] Proper abstraction
- [ ] Dependencies injected
- [ ] Immutable where possible
- [ ] Thread-safe if shared

### Database
- [ ] Parameterized queries only
- [ ] Proper indexes created
- [ ] Transactions used correctly
- [ ] Connection pooling configured
- [ ] Migration scripts reviewed

## Security Checklist

### Authentication
- [ ] Strong password hashing (bcrypt/argon2)
- [ ] Password policy enforced
- [ ] JWT tokens properly validated
- [ ] Refresh token rotation
- [ ] Session timeout configured
- [ ] Account lockout after failures

### Authorization
- [ ] RBAC implemented
- [ ] Permission checks on all protected routes
- [ ] Resource ownership verified
- [ ] Principle of least privilege

### Input Validation
- [ ] All inputs validated
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] CSRF tokens implemented
- [ ] Rate limiting applied
- [ ] File upload validated

### Data Protection
- [ ] Sensitive data encrypted
- [ ] HTTPS enforced
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Secrets in environment variables

## Testing Checklist

### Unit Tests
- [ ] Core business logic tested
- [ ] Edge cases covered
- [ ] Error scenarios tested
- [ ] Mocking appropriate
- [ ] Coverage >= 80%

### Integration Tests
- [ ] API endpoints tested
- [ ] Database operations tested
- [ ] External services mocked
- [ ] Authentication tested
- [ ] Error handling tested

### E2E Tests
- [ ] Critical user flows tested
- [ ] Login/logout tested
- [ ] Data creation tested
- [ ] Navigation tested
- [ ] Error states tested

## Performance Checklist

- [ ] Database queries optimized
- [ ] Indexes created for queries
- [ ] Caching implemented
- [ ] Lazy loading used
- [ ] Pagination implemented
- [ ] Compression enabled
- [ ] CDN for static assets
- [ ] Async processing for heavy tasks

## Documentation Checklist

### Code Documentation
- [ ] README complete
- [ ] API documentation complete
- [ ] Inline comments for complex logic
- [ ] CHANGELOG maintained

### User Documentation
- [ ] Setup guide
- [ ] Usage guide
- [ ] Troubleshooting section
- [ ] FAQ section

### Deployment Documentation
- [ ] Environment setup
- [ ] Deployment steps
- [ ] Monitoring guide
- [ ] Rollback procedure

## Deployment Checklist

- [ ] Environment variables documented
- [ ] Health check endpoint
- [ ] Graceful shutdown
- [ ] Backup strategy
- [ ] Rollback plan
- [ ] Monitoring configured
- [ ] Alerts set up

## Post-Deployment Checklist

- [ ] Smoke tests passed
- [ ] Performance benchmarks met
- [ ] Error rates normal
- [ ] Logs monitored
- [ ] Rollback plan ready
