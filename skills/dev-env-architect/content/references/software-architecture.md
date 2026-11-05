---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402200cb669b095f1157f06e3c117683357fe056ad81766c6bbc07f5b2eada76131e902205480dcfcd6e4e295c0a14d3158d7eb9be2ec0775a117bbd945fb0801ddd2d264
    ReservedCode2: 304502202232bb261adb48c11e61257792c7df55fd9396753a7c6109c96f8faaef74c4ea022100f96d375c824e896764a067b8f0b5db5eee81d29d48cdd4bba1a102cdca4fabaf
---

# Software Architecture Reference

## Overview
Modern software architecture patterns help build scalable, maintainable applications. Key trends include AI/ML integration, cloud-native technologies, and microservices <citation>11</citation>.

## Architecture Patterns

### Monolithic Architecture
- Single deployable unit
- All components in one codebase
- Simple deployment
- Easier debugging initially
- Scaling requires full replication

### Microservices Architecture
- Services communicate via APIs
- Independent deployment and scaling
- Technology flexibility
- Complexity in orchestration
- Requires DevOps maturity <citation>174</citation>

### Event-Driven Architecture
- Services emit and consume events
- Loose coupling
- Asynchronous communication
- Event sourcing
- CQRS pattern

### Serverless Architecture
- Functions as a service (FaaS)
- Automatic scaling
- Pay-per-use pricing
- Cold start latency
- Stateless functions

## Layered Architecture

### Clean Architecture Layers
```
┌─────────────────────────────┐
│     Presentation Layer      │
│   (Controllers, Views)      │
├─────────────────────────────┤
│     Application Layer       │
│      (Use Cases)            │
├─────────────────────────────┤
│       Domain Layer          │
│   (Entities, Business)      │
├─────────────────────────────┤
│    Infrastructure Layer      │
│  (Database, External APIs)  │
└─────────────────────────────┘
```

### Project Structure (Node.js)
```
src/
├── controllers/     # Route handlers
├── services/       # Business logic
├── models/         # Data models
├── repositories/   # Data access
├── middleware/     # Express middleware
├── utils/          # Helpers
├── config/         # Configuration
├── types/          # TypeScript types
└── index.js        # Entry point
```

## Node.js Architecture Best Practices

### Separation of Concerns
```javascript
// controllers/userController.js
const userController = {
  async create(req, res, next) {
    try {
      const { name, email } = req.body;
      const user = await userService.create({ name, email });
      res.status(201).json(user);
    } catch (error) {
      next(error);
    }
  },
};

// services/userService.js
class UserService {
  constructor(userRepository, emailService) {
    this.userRepository = userRepository;
    this.emailService = emailService;
  }

  async create(data) {
    const existingUser = await this.userRepository.findByEmail(data.email);
    if (existingUser) {
      throw new Error('User already exists');
    }
    const user = await this.userRepository.create(data);
    await this.emailService.sendWelcome(user);
    return user;
  }
}
```

### Dependency Injection
```javascript
// Using a DI container
class Container {
  constructor() {
    this.services = new Map();
  }

  register(name, factory) {
    this.services.set(name, factory);
  }

  get(name) {
    const service = this.services.get(name);
    return service(this);
  }
}

const container = new Container();
container.register('db', () => new Database());
container.register('userRepository', (c) => new UserRepository(c.get('db')));
container.register('userService', (c) => new UserService(c.get('userRepository')));
```

### Error Handling
```javascript
// custom error class
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

// error handler middleware
const errorHandler = (err, req, res, next) => {
  err.statusCode = err.statusCode || 500;
  err.status = err.status || 'error';

  if (process.env.NODE_ENV === 'development') {
    res.status(err.statusCode).json({
      status: err.status,
      error: err,
      message: err.message,
      stack: err.stack,
    });
  } else {
    if (err.isOperational) {
      res.status(err.statusCode).json({
        status: err.status,
        message: err.message,
      });
    } else {
      console.error('ERROR:', err);
      res.status(500).json({
        status: 'error',
        message: 'Something went wrong',
      });
    }
  }
};
```

## API Design Patterns

### REST API Design
```javascript
// Express routes
const express = require('express');
const router = express.Router();

// GET /users - List users
router.get('/', userController.list);

// GET /users/:id - Get user
router.get('/:id', userController.get);

// POST /users - Create user
router.post('/', validate(createUserSchema), userController.create);

// PUT /users/:id - Update user
router.put('/:id', validate(updateUserSchema), userController.update);

// DELETE /users/:id - Delete user
router.delete('/:id', userController.delete);

module.exports = router;
```

### API Versioning
```javascript
// Option 1: URL path
router.use('/v1', v1Routes);
router.use('/v2', v2Routes);

// Option 2: Header
app.use((req, res, next) => {
  const version = req.headers['accept-version'] || '1.0';
  req.apiVersion = version;
  next();
});

// Option 3: Query parameter
router.get('/users', (req, res) => {
  const version = req.query.v || '1';
  // Handle different versions
});
```

### GraphQL Schema
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  publishedAt: DateTime
}

type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
  postsByUser(userId: ID!): [Post!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User
  deleteUser(id: ID!): Boolean!
}

input CreateUserInput {
  name: String!
  email: String!
}
```

## Database Design Patterns

### Repository Pattern
```javascript
class UserRepository {
  constructor(model) {
    this.model = model;
  }

  async findById(id) {
    return this.model.findById(id);
  }

  async findByEmail(email) {
    return this.model.findOne({ email });
  }

  async create(data) {
    const user = new this.model(data);
    return user.save();
  }

  async update(id, data) {
    return this.model.findByIdAndUpdate(id, data, { new: true });
  }

  async delete(id) {
    return this.model.findByIdAndDelete(id);
  }

  async findAll(query = {}) {
    return this.model.find(query);
  }
}
```

### Data Access Object (DAO)
```javascript
class UserDAO {
  constructor(db) {
    this.db = db;
  }

  async findById(id) {
    const result = await this.db.query(
      'SELECT * FROM users WHERE id = $1',
      [id]
    );
    return result.rows[0];
  }

  async create(user) {
    const { name, email } = user;
    const result = await this.db.query(
      'INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *',
      [name, email]
    );
    return result.rows[0];
  }
}
```

## Caching Patterns

### Cache-Aside
```javascript
class CacheService {
  constructor(redis, ttl = 3600) {
    this.redis = redis;
    this.ttl = ttl;
  }

  async getOrSet(key, fetchFn) {
    const cached = await this.redis.get(key);
    if (cached) {
      return JSON.parse(cached);
    }

    const data = await fetchFn();
    await this.redis.setex(key, this.ttl, JSON.stringify(data));
    return data;
  }
}

// Usage
const user = await cache.getOrSet(
  `user:${userId}`,
  () => userRepository.findById(userId)
);
```

### Write-Through Cache
```javascript
async createUser(userData) {
  const user = await userRepository.create(userData);
  await cache.set(`user:${user.id}`, JSON.stringify(user));
  return user;
}

async updateUser(id, data) {
  const user = await userRepository.update(id, data);
  await cache.set(`user:${id}`, JSON.stringify(user));
  return user;
}
```

## Circuit Breaker Pattern
```javascript
class CircuitBreaker {
  constructor(fn, options = {}) {
    this.fn = fn;
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 30000;
    this.state = 'CLOSED';
    this.failures = 0;
    this.lastFailureTime = null;
  }

  async call(...args) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.resetTimeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit is OPEN');
      }
    }

    try {
      const result = await this.fn(...args);
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failures = 0;
    this.state = 'CLOSED';
  }

  onFailure() {
    this.failures++;
    this.lastFailureTime = Date.now();
    if (this.failures >= this.failureThreshold) {
      this.state = 'OPEN';
    }
  }
}
```

## Message Queue Patterns

### Producer-Consumer
```javascript
// Producer
class OrderService {
  constructor(queue) {
    this.queue = queue;
  }

  async createOrder(orderData) {
    const order = await this.orderRepository.create(orderData);
    await this.queue.send('order.created', {
      orderId: order.id,
      userId: order.userId,
      total: order.total,
    });
    return order;
  }
}

// Consumer
class OrderProcessor {
  async process(message) {
    const { orderId, userId } = message;
    // Process order
    console.log(`Processing order ${orderId}`);
    // Update inventory, send notifications, etc.
  }
}
```

## Logging & Observability

### Structured Logging
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'my-app' },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      ),
    }),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

// Usage
logger.info('User created', { userId: user.id, email: user.email });
logger.error('Database error', { error: err.message, stack: err.stack });
```

### Request Tracing
```javascript
const { trace, context, propagation } = require('@opentelemetry/api');

function tracingMiddleware(req, res, next) {
  const span = tracer.startSpan(`${req.method} ${req.path}`);

  context.with(trace.setSpan(context.active(), span), () => {
    res.on('finish', () => {
      span.setStatus({ code: res.statusCode >= 400 ? 1 : 0 });
      span.end();
    });
    next();
  });
}
```

## Performance Patterns

### Connection Pooling
```javascript
const { Pool } = require('pg');

const pool = new Pool({
  max: 20,                    // Maximum pool size
  idleTimeoutMillis: 30000,   // Close idle connections after 30s
  connectionTimeoutMillis: 2000, // Return error after 2s
});

// Use with async/await
const result = await pool.query('SELECT * FROM users');
```

### Batch Processing
```javascript
async function processInBatches(items, batchSize = 100) {
  const results = [];
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(
      batch.map(item => processItem(item))
    );
    results.push(...batchResults);
    console.log(`Processed ${Math.min(i + batchSize, items.length)}/${items.length}`);
  }
  return results;
}
```

## Security Patterns

### Input Validation
```javascript
const Joi = require('joi');

const createUserSchema = Joi.object({
  name: Joi.string().min(2).max(100).required(),
  email: Joi.string().email().required(),
  password: Joi.string()
    .min(8)
    .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
    .required(),
  age: Joi.number().integer().min(13).max(120),
});

function validate(schema) {
  return (req, res, next) => {
    const { error } = schema.validate(req.body, { abortEarly: false });
    if (error) {
      return res.status(400).json({
        error: 'Validation failed',
        details: error.details.map(d => d.message),
      });
    }
    next();
  };
}
```

## Scalability Patterns

### Horizontal Scaling
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Rate Limiting
```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api', limiter);
```

## Architecture Decision Records (ADR)

### Template
```markdown
# ADR 1: Use PostgreSQL for Primary Database

## Status
Accepted

## Context
We need to choose a primary database for our application.

## Decision
We will use PostgreSQL as our primary relational database.

## Consequences
### Positive
- ACID compliance
- Rich feature set
- Strong community

### Negative
- Requires database administration
- More expensive than managed services initially

## Alternatives Considered
- MySQL: Less feature-rich
- MongoDB: Not suitable for relational data
```

## Additional Resources
- Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- 12-Factor App: https://12factor.net/
- Microservices Patterns: https://microservices.io/patterns/index.html
