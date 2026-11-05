---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 0624120028d71b4fe62520ec6c22d6fa
    PropagateID: 0624120028d71b4fe62520ec6c22d6fa
    ReservedCode1: 3044022012b5f31848c14a57cc4154ed6df121bfa82f970c97f4ecba59b9966fe762dd9502207e57b3c1e8dc5f8c110622f058acdf17ffe018aff1a050dff60a0ca48e8ee938
    ReservedCode2: 3046022100a6938924fb2c681eda957cfd9ac40b840efc166b8830ae9d693d2cb8d6c24dc60221008b91ed0e1a42892d6e281b6b67b9e0c5367f6454320139f215c1a3fe3d081879
description: Software testing expert skill for writing, running, and managing unit tests, integration tests, and end-to-end tests in TypeScript, Python, and Swift. Supports browser-based UI functional testing, customer-uploaded test case execution, and generates Word document test reports with image support. Can use user-provided templates or create professional test reports based on test case results. Use when users ask to write test cases, run tests, manage test suites, execute automated testing, perform UI functional testing, upload test cases for execution, or generate test reports.
name: software-testing-expert
---

# Software Testing Expert Skill

## Overview

A comprehensive software testing expert skill that supports multiple programming languages and testing frameworks. This skill enables writing, running, and managing unit tests, integration tests, end-to-end tests, browser-based UI functional tests, customer-uploaded test case execution, and generating professional Word document test reports with image support.

## Supported Languages and Frameworks

### TypeScript/JavaScript
- **Unit Testing**: Jest, Vitest
- **Integration Testing**: Supertest, testing-library
- **E2E Testing**: Playwright, Cypress, Puppeteer
- **UI Component Testing**: testing-library/react, testing-library/vue

### Python
- **Unit Testing**: pytest, unittest, doctest
- **Integration Testing**: pytest-asyncio, requests
- **E2E Testing**: Playwright (Python), Selenium
- **API Testing**: httpx, aiohttp

### Swift
- **Unit Testing**: XCTest
- **UI Testing**: XCTest UI Testing
- **Integration Testing**: XCUITest

## Core Capabilities

### 1. Unit Testing
- Create comprehensive unit tests with proper mocking
- Setup and teardown management
- Parameterized tests
- Code coverage analysis
- Mock and stub creation

### 2. Integration Testing
- Database integration testing
- API integration testing
- Service integration testing
- Configuration management

### 3. End-to-End (E2E) Testing
- Full workflow testing
- User journey simulation
- Multi-page application testing
- Session and state management

### 4. Browser-Based UI Testing
- Cross-browser testing (Chrome, Firefox, Safari, Edge)
- Element interaction (click, type, select)
- Form submission testing
- Navigation and routing
- Screenshot capture
- Video recording of test runs
- Accessibility testing (a11y)

### 5. Word Document Test Report Generation
- Generate professional Word test reports
- Support for embedded images and screenshots
- Test case-based report structure
- User-provided template support
- Customizable report sections:
  - Test summary
  - Test case results (passed/failed/blocked)
  - Screenshots for failures
  - Execution logs
  - Defect tracking
- Export to DOCX format

## Uploaded Test Case Features

### Supported Test Case Formats
- **Excel (.xlsx, .xls)**: Test case management tools export (Zephyr, TestRail, qTest)
- **CSV (.csv)**: Comma-separated test case data
- **JSON (.json)**: Structured test case definitions
- **YAML (.yaml, .yml)**: Human-readable test case format
- **XML (.xml)**: Standard test case interchange formats

### Test Case Upload Workflow
1. Receive uploaded test case file from customer
2. Parse and validate test case format
3. Extract test case information:
   - Test case ID
   - Title
   - Description
   - Preconditions
   - Test steps
   - Expected results
   - Priority/Severity
   - Test data
4. Generate automated test scripts from test cases
5. Execute tests against target application
6. Capture results and screenshots
7. Generate standard test report

### Automated Test Generation
When test cases are uploaded:
- Convert manual test steps to automated test scripts
- Support multiple output frameworks (Playwright, Selenium, pytest)
- Map test case fields to test framework structure
- Generate executable test code with proper assertions
- Handle test data parameterization

### Test Case Parser Examples

#### Excel Format
| TC_ID | Title | Preconditions | Step 1 | Step 2 | Step 3 | Expected Result | Priority |
|-------|-------|---------------|--------|--------|--------|-----------------|----------|
| TC-001 | Login Test | User registered | Enter username | Enter password | Click login | Redirect to dashboard | High |

#### JSON Format
```json
{
  "testCases": [
    {
      "id": "TC-001",
      "title": "User Login Validation",
      "priority": "High",
      "preconditions": ["User registered in system"],
      "steps": [
        {"step": 1, "action": "Navigate to login page", "expected": "Login form displayed"},
        {"step": 2, "action": "Enter valid username", "expected": "Username field populated"},
        {"step": 3, "action": "Enter valid password", "expected": "Password field populated"},
        {"step": 4, "action": "Click login button", "expected": "Redirect to dashboard"}
      ]
    }
  ]
}
```

## Test Report Features

### Report Structure
```
Test Report
├── Executive Summary
│   ├── Total Test Cases
│   ├── Pass Rate
│   ├── Test Duration
│   └── Risk Assessment
├── Test Environment
│   ├── System Configuration
│   ├── Test Data
│   └── Prerequisites
├── Test Case Results
│   ├── Passed Test Cases
│   ├── Failed Test Cases
│   └── Blocked Test Cases
├── Defect Summary
├── Attachments
│   └── Screenshots
└── Recommendations
```

### Image Support
- Embed screenshots directly in reports
- Support for multiple image formats (PNG, JPG, BMP)
- Automatic image resizing for document compatibility
- Figure captions and numbering
- Inline and standalone image placement

### Template Support
When user provides a test report template:
1. Parse template structure and formatting
2. Extract placeholder markers
3. Populate data following template layout
4. Preserve original styling and branding
5. Generate final document matching template format

## Test Case Management

### Test Case Structure
```yaml
test_case_id: TC-001
title: User Login Validation
priority: High
preconditions:
  - User registered in system
  - Browser opened to login page
test_steps:
  - Enter valid username
  - Enter valid password
  - Click login button
expected_result: User redirected to dashboard
```

### Test Case Execution
- Execute individual test cases
- Batch execution of test suites
- Parallel test execution where supported
- Capture screenshots on failure
- Generate execution logs

## Testing Workflow

### 1. Upload Phase
- Receive test case file upload
- Validate file format and structure
- Parse test case content
- Handle encoding issues
- Report parsing errors if any

### 2. Generation Phase
- Convert test cases to automated scripts
- Select appropriate framework (Playwright/Selenium/pytest)
- Parameterize test data
- Generate test suite structure
- Create configuration files

### 3. Execution Phase
- Run individual tests
- Run test suites
- Generate coverage reports
- Capture test results
- Take screenshots for UI tests
- Log all execution details

### 4. Reporting Phase
- Generate test reports
- Analyze failures
- Embed screenshots
- Provide recommendations
- Export to Word document
- Match template format if provided

## Best Practices

### Test Organization
```
tests/
├── unit/
│   ├── components/
│   ├── services/
│   └── utils/
├── integration/
│   ├── api/
│   └── database/
├── e2e/
│   ├── flows/
│   └── pages/
├── cases/
│   └── test_cases.yaml
├── uploaded/
│   └── customer_test_cases.xlsx
└── fixtures/
```

### Test Naming Conventions
- Use descriptive names: `shouldReturnUserWhenValidIdProvided`
- Follow pattern: `describe`/`it` or `test`/`expect`
- Group related tests

### Assertion Strategies
- Use specific assertions
- Include meaningful error messages
- Test both positive and negative cases
- Cover edge cases

### Report Generation Best Practices
- Include clear section headers
- Use tables for structured data
- Embed relevant screenshots
- Provide actionable recommendations
- Include version and timestamp

## Tool Usage

### For TypeScript Projects
- Use `mcp__matrix__bash` to run test commands
- Support for npm/yarn scripts
- Integration with CI/CD pipelines

### For Python Projects
- Use `mcp__matrix__bash` to run pytest commands
- Support for virtual environments
- Coverage report generation

### For Swift Projects
- Use `mcp__matrix__bash` to run xcodebuild
- Support for simulators
- Test report generation

### For Browser Testing
- Use `mcp__matrix__bash` for Playwright/Cypress CLI
- Support for headless mode
- Parallel test execution
- Screenshot capture

### For Word Report Generation
- Use `minimax-docx` skill for Word document creation
- Embed images using proper Word XML structure
- Support template-based generation
- Export to standard DOCX format

### For Test Case Upload Processing
- Use `minimax-xlsx` skill for Excel file parsing
- Support CSV parsing with pandas
- JSON/YAML parsing with native libraries
- Generate test automation code dynamically

## Implementation Examples

### Uploaded Test Case to Playwright Script

**Input (Uploaded Test Case - Excel/JSON):**
```json
{
  "id": "TC-001",
  "title": "User Login Validation",
  "priority": "High",
  "preconditions": ["User registered in system"],
  "steps": [
    {"step": 1, "action": "Navigate to /login", "expected": "Login page loads"},
    {"step": 2, "action": "Fill email field with 'user@test.com'", "expected": "Email entered"},
    {"step": 3, "action": "Fill password field with 'password123'", "expected": "Password entered"},
    {"step": 4, "action": "Click submit button", "expected": "Redirect to /dashboard"}
  ]
}
```

**Generated Playwright Test:**
```typescript
import { test, expect } from '@playwright/test';

test('TC-001: User Login Validation', async ({ page }) => {
  // Preconditions: User registered in system

  // Step 1: Navigate to /login
  await page.goto('/login');
  await expect(page).toHaveTitle(/Login/);

  // Step 2: Fill email field with 'user@test.com'
  await page.fill('input[name="email"]', 'user@test.com');

  // Step 3: Fill password field with 'password123'
  await page.fill('input[name="password"]', 'password123');

  // Step 4: Click submit button
  await page.click('button[type="submit"]');

  // Expected: Redirect to /dashboard
  await expect(page).toHaveURL('/dashboard');
});
```

### TypeScript (Jest)
```typescript
describe('UserService', () => {
  let userService: UserService;
  let mockRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepository = {
      findById: jest.fn(),
      create: jest.fn(),
    };
    userService = new UserService(mockRepository);
  });

  it('should return user when valid ID is provided', async () => {
    const mockUser = { id: '1', name: 'Test User' };
    mockRepository.findById.mockResolvedValue(mockUser);

    const result = await userService.getUser('1');

    expect(result).toEqual(mockUser);
    expect(mockRepository.findById).toHaveBeenCalledWith('1');
  });
});
```

### Python (pytest)
```python
import pytest
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository

@pytest.fixture
def mock_repository():
    return Mock(spec=UserRepository)

@pytest.fixture
def user_service(mock_repository):
    return UserService(mock_repository)

def test_get_user_returns_user_when_valid_id(user_service, mock_repository):
    mock_user = {"id": "1", "name": "Test User"}
    mock_repository.find_by_id.return_value = mock_user

    result = user_service.get_user("1")

    assert result == mock_user
    mock_repository.find_by_id.assert_called_once_with("1")
```

### Swift (XCTest)
```swift
import XCTest
@testable import MyApp

class UserServiceTests: XCTestCase {
    var userService: UserService!
    var mockRepository: MockUserRepository!

    override func setUp() {
        super.setUp()
        mockRepository = MockUserRepository()
        userService = UserService(repository: mockRepository)
    }

    func testGetUser_ReturnsUser_WhenValidIdProvided() {
        let mockUser = User(id: "1", name: "Test User")
        mockRepository.findByIdReturnValue = mockUser

        let result = userService.getUser(id: "1")

        XCTAssertEqual(result?.id, "1")
        XCTAssertEqual(result?.name, "Test User")
    }
}
```

## Standard Test Report Format

### Report Content Structure
```markdown
# Software Test Report

**Project**: Example Application
**Test Date**: 2026-03-27
**Tester**: Automated System
**Version**: 1.0.0
**Test Source**: Uploaded Test Cases

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Test Cases | 50 |
| Passed | 45 |
| Failed | 3 |
| Blocked | 2 |
| Pass Rate | 90% |

## Test Case Results

### TC-001: User Login
- **Status**: PASSED
- **Steps Executed**: 5/5
- **Duration**: 2.5s
- **Screenshot**: [embedded]

### TC-002: Payment Processing
- **Status**: FAILED
- **Steps Executed**: 3/8
- **Duration**: 5.2s
- **Error**: Card declined unexpectedly
- **Screenshot**: [embedded failure screenshot]

## Attachments

Figure 1: Login Success Screenshot
Figure 2: Payment Failure Screenshot
```

## Integration with Development Workflow

### Test-Driven Development (TDD)
1. Write failing test first
2. Implement minimum code to pass
3. Refactor while maintaining tests

### Continuous Integration
- Automated test execution
- Coverage thresholds
- Performance benchmarks
- Security scanning
- Automatic report generation

### Code Review Integration
- Test coverage requirements
- Best practices enforcement
- Documentation verification

## Deliverables

When invoked, this skill will provide:
1. Comprehensive test suites
2. Test case definitions (YAML/JSON)
3. **Automated test scripts from uploaded test cases**
4. Test documentation
5. Coverage reports
6. **Word document test reports** with embedded screenshots
7. **Standard test report generation from test case execution**
8. CI/CD integration scripts
9. Best practices guide
