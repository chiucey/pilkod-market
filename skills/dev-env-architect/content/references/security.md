---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3044022007f8aa29f61392daf423e8715fda5ca90702797db07327bebe3b554a52e9cb8e0220320fc5d02148520370821dadbae32a05b4dab8837a303e8919173c76d0d57c39
    ReservedCode2: 3045022100946a2ef2291054e55ff28c00f3aa9ce7d4b308cf6f7233fcb0a813bc2caa0ee802207cbb351542b844374f8b2c91f163442bab0ea9bbfa9d881f9d0d26125ef9e8db
---

# Security Scanning Reference

## Overview
Security scanning tools help identify vulnerabilities in code and dependencies, essential for DevSecOps practices <citation>191</citation>.

## Security Testing Types

### SAST (Static Application Security Testing)
- Analyzes source code without execution
- Runs in early development stages
- Finds coding flaws and vulnerabilities <citation>192</citation>

### DAST (Dynamic Application Security Testing)
- Tests running applications
- Simulates external attacks
- Finds runtime vulnerabilities <citation>200</citation>

### IAST (Interactive Application Security Testing)
- Combines SAST and DAST
- Runtime instrumentation
- Accurate vulnerability detection

## Dependency Scanning

### npm audit
```bash
# Basic audit
npm audit

# JSON output
npm audit --json > audit.json

# Fix vulnerabilities
npm audit fix

# Fix with specific level
npm audit fix --audit-level=moderate
```

### Snyk
```bash
# Install CLI
npm install -g snyk

# Authenticate
snyk auth

# Test for vulnerabilities
snyk test

# Monitor project
snyk monitor

# Fix vulnerabilities
snyk wizard
```

### npm-check-updates
```bash
# Check for outdated packages
ncu

# Upgrade packages
ncu -u

# Interactive upgrade
ncu -i
```

## SAST Tools

### ESLint Security
```javascript
// .eslintrc.js
module.exports = {
  plugins: ['security'],
  rules: {
    'security/detect-non-literal-fs-filename': 'error',
    'security/detect-unsafe-regex': 'error',
    'security/detect-possible-timing-attacks': 'warn',
    'security/detect-pseudoRandomBytes': 'warn',
  },
};
```

### SonarQube Integration
```yaml
# .github/workflows/sonarqube.yml
name: SonarQube

on:
  push:
    branches: [main]
  pull_request:

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: SonarSource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

      - uses: github/codeql-action/upload-scap@v2
```

### OWASP Dependency Check
```bash
# Install
docker pull owasp/dependency-check

# Scan
docker run --rm -v $(pwd):/src owasp/dependency-check --scan /src

# CLI install
brew install dependency-check

# Scan project
dependency-check --project "MyApp" --scan ./src
```

## Container Security

### Trivy
```bash
# Install
brew install trivy

# Scan image
trivy image myregistry/myapp:latest

# Scan filesystem
trivy fs --security-checks vuln,config /path/to/project

# Scan Kubernetes
trivy k8s --cluster-context my-cluster

# Output formats
trivy image --format json --output report.json myimage:latest
trivy image --format sarif --output report.sarif myimage:latest
```

### Docker Security Scanning
```dockerfile
# Use specific base image tags
FROM node:22-alpine:3.19

# Don't run as root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Use distroless images
FROM gcr.io/distroless/nodejs22-debian11

# Scan during build
RUN npm audit --audit-level=high
```

## API Security

### OAuth 2.0
```javascript
// JWT validation
const jwt = require('jsonwebtoken');

function validateToken(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    return res.status(401).json({ error: 'No token provided' });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

### Rate Limiting
```javascript
const rateLimit = require('express-rate-limit');

// General rate limit
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  message: 'Too many requests from this IP',
});

// Strict limit for auth
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
});

app.use('/api/', generalLimiter);
app.use('/api/auth/login', authLimiter);
```

## Input Validation

### Schema Validation
```javascript
const Joi = require('joi');

const userSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/).required(),
  age: Joi.number().integer().min(13).max(120),
});

function validateUser(data) {
  const { error, value } = userSchema.validate(data);
  if (error) {
    throw new Error(error.details[0].message);
  }
  return value;
}
```

### SQL Injection Prevention
```javascript
// Use parameterized queries
const query = 'SELECT * FROM users WHERE id = $1';
const result = await pool.query(query, [userId]);

// Avoid string concatenation
// BAD: `SELECT * FROM users WHERE id = ${userId}`
// GOOD: `SELECT * FROM users WHERE id = $1`
```

## CORS Configuration
```javascript
const cors = require('cors');

const corsOptions = {
  origin: function (origin, callback) {
    const allowedOrigins = ['https://example.com', 'https://app.example.com'];
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
};

app.use(cors(corsOptions));
```

## Helmet.js
```javascript
const helmet = require('helmet');

app.use(helmet());

// Configure specific headers
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'"],
    styleSrc: ["'self'", 'https://fonts.googleapis.com'],
    fontSrc: ["'self'", 'https://fonts.gstatic.com'],
    imgSrc: ["'self'", 'data:', 'https:'],
  },
}));

app.use(helmet.hsts({
  maxAge: 31536000,
  includeSubDomains: true,
}));
```

## Secrets Management

### Environment Variables
```bash
# Don't commit .env files
# .env.example (safe to commit)
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=your_api_key_here

# .env (add to .gitignore)
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
API_KEY=sk_live_xxxxxxxxxxxxx
JWT_SECRET=super_secret_jwt_key
```

### GitHub Secrets
```yaml
# GitHub Actions
- name: Deploy
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
    API_KEY: ${{ secrets.API_KEY }}
  run: npm run deploy
```

### AWS Secrets Manager
```javascript
const { SecretsManagerClient, GetSecretValueCommand } = require('@aws-sdk/client-secrets-manager');

const client = new SecretsManagerClient({ region: 'us-east-1' });

async function getSecret(secretName) {
  const command = new GetSecretValueCommand({ SecretId: secretName });
  const response = await client.send(command);
  return JSON.parse(response.SecretString);
}
```

## Common Vulnerabilities

### XSS Prevention
```javascript
// Sanitize HTML
const sanitizeHtml = require('sanitize-html');

function sanitizeInput(input) {
  return sanitizeHtml(input, {
    allowedTags: ['b', 'i', 'em', 'strong'],
    allowedAttributes: {},
  });
}

// Content Security Policy
app.use((req, res, next) => {
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  next();
});
```

### CSRF Protection
```javascript
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

// Apply to routes
app.post('/api/form', csrfProtection, (req, res) => {
  res.json({ success: true });
});

// Include CSRF token in forms
// <input type="hidden" name="_csrf" value="{{csrfToken}}">
```

## Security Headers
```javascript
// security-headers.js
const securityHeaders = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
};

app.use((req, res, next) => {
  Object.entries(securityHeaders).forEach(([key, value]) => {
    res.setHeader(key, value);
  });
  next();
});
```

## OWASP Top 10 (2021)
1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable Components
7. Auth Failures
8. Data Integrity Failures
9. Logging Failures
10. SSRF

## Vulnerability Scanning in CI

### GitHub Actions
```yaml
- name: Run Snyk
  uses: snyk/actions/node@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

- name: Run Trivy
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'
```

## Incident Response

### Logging
```javascript
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

// Never log sensitive data
logger.info('User logged in', { userId: user.id }); // Good
logger.info('User logged in', { user: user });     // Bad - may contain password
```

## Security Checklist

- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitize user input)
- [ ] CSRF protection on state-changing operations
- [ ] Rate limiting on public endpoints
- [ ] Secure headers configured
- [ ] Secrets in environment variables
- [ ] HTTPS enforced
- [ ] Dependency scanning in CI
- [ ] Container scanning
- [ ] Regular security updates
- [ ] Secure password hashing (bcrypt/argon2)
- [ ] JWT token expiration
- [ ] CORS configured correctly
- [ ] Logging security events

## Additional Resources
- OWASP: https://owasp.org/
- Snyk: https://snyk.io/
- SonarQube: https://sonarqube.org/
- Trivy: https://aquasecurity.github.io/trivy/
- Security Headers: https://securityheaders.com/
