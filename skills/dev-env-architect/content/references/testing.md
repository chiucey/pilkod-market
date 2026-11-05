---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402202f8af71eda766645d83b715944117d0a389d2f45d8f5c0f7aa9d01055aad70d9022040533fb10cc52ab5e7f346f858b47e829f88034974199a237937ed1cba4c0ec0
    ReservedCode2: 3045022100afe6a2c066ee530265395d5aa3067e249b0f8569f2670fea30474626c80b4256022047e5d56932d727b43dc11ad251ff7146f40f29befbb3ef487ff9534b87cf1348
---

# Testing Framework Reference

## Overview
Testing is crucial for software quality. Modern JavaScript testing includes unit testing, integration testing, and end-to-end testing <citation>229</citation>.

## Testing Framework Comparison

| Framework | Type | Best For | Pros | Cons |
|-----------|------|----------|------|------|
| Jest | Unit/Integration | React apps | Zero-config, snapshot testing | Slower for large projects |
| Vitest | Unit/Integration | Vite projects | Fast, Vite-native | Newer ecosystem |
| Cypress | E2E | Web apps | Great DX, time travel | Single browser |
| Playwright | E2E | Cross-browser | Multi-browser, parallelism | Steeper learning curve |
| Mocha | Unit | Flexibility | Highly customizable | Requires setup |

## Jest

### Configuration
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.test.js',
    '!src/**/__tests__/**'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  moduleFileExtensions: ['js', 'json'],
  transform: {
    '^.+\\.js$': 'babel-jest'
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testTimeout: 10000,
  verbose: true
};
```

### Basic Test
```javascript
// sum.test.js
const sum = require('./sum');

describe('sum', () => {
  test('adds two numbers', () => {
    expect(sum(1, 2)).toBe(3);
  });

  test('handles negative numbers', () => {
    expect(sum(-1, -2)).toBe(-3);
  });

  test('throws on invalid input', () => {
    expect(() => sum('a', 1)).toThrow();
  });
});
```

### Matchers
```javascript
// Common matchers
expect(value).toBe(expected);           // ===
expect(value).toEqual(expected);       // deep equality
expect(value).toBeNull();              // null
expect(value).toBeUndefined();          // undefined
expect(value).toBeTruthy();            // true, 1, 'string'
expect(value).toBeFalsy();             // false, 0, ''
expect(value).toBeGreaterThan(n);      // >
expect(value).toBeLessThan(n);         // <
expect(array).toContain(item);         // includes
expect(string).toMatch(/regex/);       // regex match
expect(fn).toThrow();                  // throws error
expect(obj).toHaveProperty('key');     // has property
```

### Async Testing
```javascript
test('fetches data', async () => {
  const data = await fetchData();
  expect(data).toHaveLength(5);
});

test('handles error', async () => {
  await expect(fetchData()).rejects.toThrow('Network error');
});

test('mocking', async () => {
  const mockFn = jest.fn().mockResolvedValue(42);
  const result = await mockFn();
  expect(mockFn).toHaveBeenCalledTimes(1);
  expect(result).toBe(42);
});
```

### Mocking
```javascript
// Mock module
jest.mock('./api', () => ({
  fetchData: jest.fn()
}));

// Mock function
const mockFn = jest.fn();
mockFn.mockReturnValue(10);
mockFn.mockResolvedValue(20);
mockFn.mockImplementation((a, b) => a + b);

// Spy
const obj = { method: () => 42 };
jest.spyOn(obj, 'method').mockReturnValue(10);
```

## Vitest

### Configuration
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      reporter: ['text', 'json', 'html'],
    },
  },
});
```

### Basic Test
```javascript
// sum.test.js
import { describe, it, expect } from 'vitest';
import { sum } from './sum';

describe('sum', () => {
  it('adds two numbers', () => {
    expect(sum(1, 2)).toBe(3);
  });
});
```

## Cypress

### Configuration
```javascript
// cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
  },
});
```

### E2E Test
```javascript
// cypress/e2e/login.cy.js
describe('Login', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('shows login form', () => {
    cy.get('form').should('be.visible');
    cy.get('input[name="email"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');
  });

  it('logs in successfully', () => {
    cy.get('input[name="email"]').type('user@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
  });

  it('shows error on invalid login', () => {
    cy.get('input[name="email"]').type('invalid@example.com');
    cy.get('input[name="password"]').type('wrong');
    cy.get('button[type="submit"]').click();
    cy.get('.error').should('contain', 'Invalid credentials');
  });
});
```

### Commands
```javascript
// Custom commands
Cypress.Commands.add('login', (email, password) => {
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="password"]').type(password);
  cy.get('button[type="submit"]').click();
});

// Usage
cy.login('user@example.com', 'password123');
```

## Playwright

### Configuration
```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
```

### E2E Test
```javascript
// tests/login.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Login', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('shows login form', async ({ page }) => {
    await expect(page.locator('form')).toBeVisible();
    await expect(page.locator('input[name="email"]')).toBeVisible();
  });

  test('logs in successfully', async ({ page }) => {
    await page.fill('input[name="email"]', 'user@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });
});
```

### API Testing
```javascript
test('API test with Playwright', async ({ request }) => {
  const response = await request.get('https://api.example.com/users');
  expect(response.ok()).toBeTruthy();
  expect(response.status()).toBe(200);
  const body = await response.json();
  expect(body).toHaveProperty('data');
});
```

## Testing Strategy

### Test Pyramid
```
        /\
       /  \
      / E2E\      Few, slow, expensive
     /      \
    /Integration\  Some, medium speed
   /          \
  /   Unit      \ Many, fast, cheap
 /              \
------------------
```

### What to Test

#### Unit Tests
- Pure functions
- Business logic
- Utility functions
- Edge cases

#### Integration Tests
- API endpoints
- Database operations
- Service interactions
- Authentication flows

#### E2E Tests
- Critical user paths
- Checkout flows
- Login/registration
- High-value features

## Mock Data

### Faker.js
```javascript
const { faker } = require('@faker-js/faker');

const user = {
  id: faker.string.uuid(),
  name: faker.person.fullName(),
  email: faker.internet.email(),
  avatar: faker.image.avatar(),
  address: {
    street: faker.location.streetAddress(),
    city: faker.location.city(),
    country: faker.location.country(),
  },
  company: faker.company.name(),
  createdAt: faker.date.past(),
};
```

## Code Coverage

### Istanbul (Jest)
```bash
npm test -- --coverage --coverageReporters=text --coverageReporters=lcov
```

### Coverage Thresholds
```javascript
// jest.config.js
module.exports = {
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
```

## Test Runners

### npm Scripts
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --runInBand --coverage",
    "cypress:open": "cypress open",
    "cypress:run": "cypress run",
    "playwright:test": "playwright test"
  }
}
```

## CI Integration

### GitHub Actions
```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        cache: 'npm'
    - run: npm ci
    - run: npm test -- --coverage
      env:
        CI: true
    - uses: codecov/codecov-action@v3
      with:
        files: ./coverage/lcov.info
```

## Best Practices

### Writing Good Tests
1. Test behavior, not implementation
2. Use descriptive names: `shouldLoginWithValidCredentials`
3. Arrange-Act-Assert pattern
4. One assertion per test (when practical)
5. Keep tests independent
6. Use data-testid for UI elements

### Test Structure
```javascript
describe('Component/Feature', () => {
  describe('when condition', () => {
    it('should do something', () => {
      // Arrange
      const input = { ... };

      // Act
      const result = doSomething(input);

      // Assert
      expect(result).toEqual(expected);
    });
  });

  describe('when error condition', () => {
    it('should handle error gracefully', () => {
      // ...
    });
  });
});
```

## Additional Resources
- Jest Docs: https://jestjs.io/docs/getting-started
- Vitest Docs: https://vitest.dev/
- Cypress Docs: https://docs.cypress.io/
- Playwright Docs: https://playwright.dev/docs/intro
- Testing Library: https://testing-library.com/
