# Modular Task Decomposition Guide

## Overview

Modular decomposition is the core principle of the commercial-project-auto-developer skill. It breaks down complex projects into manageable, independently executable modules.

## Decomposition Principles

### 1. Single Responsibility

Each module should have one clear purpose. Avoid mixing concerns:
- ❌ "User management and database operations"
- ✅ "User CRUD operations" + "Database connection management"

### 2. Clear Dependencies

Define explicit dependencies between modules:
```
T001 (Requirements)
    ↓
T002 (Architecture) ← depends on T001
    ↓
T003 (Database) ← depends on T002
    ↓
T004 (API) ← depends on T002, T003
```

### 3. Independent Execution

Each module should be executable independently (when dependencies are met):
- Clear input requirements
- Documented output format
- No hidden dependencies

## Standard Module Library

### Core Modules (Always Required)

| Module ID | Name | Description | Dependencies |
|-----------|------|-------------|--------------|
| T001 | Requirement Analysis | User needs, pain points, features | None |
| T002 | Architecture Design | System structure, patterns | T001 |
| T003 | Database Design | Schema, relationships | T002 |
| T004 | API Design | Interface definitions | T002, T003 |
| T005 | Backend Development | Server implementation | T004 |
| T006 | Frontend Development | Client implementation | T004 |
| T007 | Security | Hardening, scanning | T005, T006 |
| T008 | Testing | Verification, benchmarks | T007 |
| T009 | Deployment | Launch, monitoring | T008 |

### Optional Modules (As Needed)

| Module ID | Name | Description | Dependencies |
|-----------|------|-------------|--------------|
| T010 | Mobile App | iOS/Android development | T004 |
| T011 | Data Pipeline | ETL, analytics | T003 |
| T012 | DevOps | CI/CD, infrastructure | T009 |
| T013 | Documentation | User guides, API docs | T005, T006 |
| T014 | Training | Onboarding materials | T013 |

## Task Decomposition Template

```json
{
  "task_id": "T00X",
  "name": "Module Name",
  "phase": "development|testing|deployment",
  "priority": 1-10,
  "estimated_effort": "small|medium|large|xlarge",
  "dependencies": ["T001", "T002"],
  "inputs": {
    "required": ["input1", "input2"],
    "optional": ["input3"]
  },
  "outputs": {
    "primary": ["output1"],
    "secondary": ["output2", "output3"]
  },
  "subtasks": [
    {
      "id": "ST001",
      "name": "Subtask name",
      "action": "generate|implement|design|review|test",
      "tool": "optional-tool-name",
      "estimated_time": "minutes"
    }
  ],
  "acceptance_criteria": [
    "Criterion 1",
    "Criterion 2"
  ],
  "verification_method": "manual|automated|both"
}
```

## Decomposition Patterns

### Pattern 1: Layered Architecture

```
Presentation Layer (Frontend)
    ↓
Business Logic Layer (Services)
    ↓
Data Access Layer (Repositories)
    ↓
Data Layer (Database)
```

### Pattern 2: Service-Oriented

```
API Gateway
    ↓
┌─────┼─────┐
↓     ↓     ↓
User  Order  Payment
Service Service Service
↓     ↓     ↓
User  Order  Payment
DB    DB    DB
```

### Pattern 3: Microservices

```
Load Balancer
    ↓
┌─────────────────────────┐
│     Service Mesh        │
├─────┬─────┬─────┬──────┤
│Auth │User │Order│Payment│
├─────┴─────┴─────┴──────┤
│    Event Bus/Kafka      │
├─────────────────────────┤
│    Shared Data Store    │
└─────────────────────────┘
```

## Example Decomposition

### E-Commerce Platform

```json
{
  "project_name": "E-Commerce Platform",
  "modules": [
    {
      "task_id": "T001",
      "name": "E-Commerce Requirements",
      "subtasks": [
        {"name": "User registration flow", "action": "analyze"},
        {"name": "Product catalog management", "action": "analyze"},
        {"name": "Shopping cart logic", "action": "analyze"},
        {"name": "Checkout process", "action": "analyze"},
        {"name": "Order management", "action": "analyze"},
        {"name": "Payment integration", "action": "analyze"}
      ]
    },
    {
      "task_id": "T005",
      "name": "Backend Services",
      "subtasks": [
        {"name": "User service", "action": "implement"},
        {"name": "Product service", "action": "implement"},
        {"name": "Cart service", "action": "implement"},
        {"name": "Order service", "action": "implement"},
        {"name": "Payment gateway adapter", "action": "implement"},
        {"name": "Notification service", "action": "implement"}
      ]
    }
  ]
}
```

## Quality Checklist

For each decomposed module:

- [ ] Single, clear purpose
- [ ] Well-defined inputs
- [ ] Well-defined outputs
- [ ] Explicit dependencies
- [ ] Measurable acceptance criteria
- [ ] Appropriate granularity (not too coarse/fine)
- [ ] Can execute independently (when deps met)
