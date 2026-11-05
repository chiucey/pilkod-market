---
name: java-springboot-postgres-analyzer
description: Analyzes, understands, and modifies Java 17+ Spring Boot 3+ PostgreSQL projects. Use when users want to analyze project structure, understand business logic, modify code, provide optimization suggestions, debug issues, or refactor Spring Boot applications.
---

# Java Spring Boot PostgreSQL Project Analyzer Skill

## Core Capabilities

This skill focuses on deep analysis of Java 17 + Spring Boot 3 + PostgreSQL technology stack projects with the following core capabilities:

1. **Project Structure Analysis** - Identify standard Spring Boot 3 project architecture
2. **Code Component Analysis** - Parse Controller, Service, Repository, Entity, DTO components
3. **Business Logic Understanding** - Analyze data flow, business rules, and API design
4. **Database Mapping** - Understand JPA/Hibernate entity to PostgreSQL table relationships
5. **Modification Suggestions** - Provide actionable code modification solutions

## Workflow

### Step 1: Project Scan and Understanding

Start with a comprehensive project scan:

```
Scan Priority:
1. pom.xml / build.gradle - Confirm dependencies and technology stack versions
2. application.yml / application.properties - Configuration analysis
3. Main application class (@SpringBootApplication) - Entry point location
4. Package structure - Standard layered architecture identification
```

**Key Checkpoints:**
- Spring Boot 3.x feature usage (Jakarta EE 9+, Records, Sealed Classes)
- JPA/Hibernate entity to database Schema mapping
- RESTful API design patterns
- Transaction management and security configuration

### Step 2: Business Logic Analysis

Perform targeted analysis based on user requirements:

**Controller Layer Analysis:**
- REST endpoint mapping (@GetMapping, @PostMapping, etc.)
- Request/Response data structures (DTO/Records usage)
- Parameter validation (Jakarta Validation)

**Service Layer Analysis:**
- Business logic implementation
- Transaction boundary definition
- Exception handling patterns

**Repository Layer Analysis:**
- JPA query methods
- Custom SQL queries
- Database operation optimization

**Entity Layer Analysis:**
- Entity relationship mapping (@OneToMany, @ManyToMany, etc.)
- Database constraint definitions
- Audit fields (@CreatedDate, @LastModifiedDate)

### Step 3: Modification Plan Generation

Based on analysis results, provide specific modification suggestions:

1. **Clear modification scope** - Point out files and specific locations to modify
2. **Provide complete code** - Give copy-paste ready code snippets
3. **Explain impact scope** - Describe modifications impact on other components
4. **Recommend best practices** - Suggest Spring Boot 3/JDK 17 best practices

## Trigger Conditions

This skill activates when users make requests like:

- "Analyze this Spring Boot project"
- "Modify the business logic of XX feature"
- "What's wrong with this code"
- "How to optimize XX module"
- "Add XX feature to the project"
- "Explain this project architecture"
- "Help me debug XX issue"
- "Refactor XX code"

## Technology Stack Baseline

This skill is based on the following technology stack versions:

| Component | Minimum Version | Recommended Version |
|-----------|-----------------|---------------------|
| Java | 17 | 21 LTS |
| Spring Boot | 3.0 | 3.2+ |
| PostgreSQL | 13 | 15+ |
| Hibernate | 6.x | 6.4+ |
| Jakarta EE | 9+ | 10 |

## Reference Documents

Detailed technical references and best practice guides are located in the `references/` directory:

- `spring-boot-3-patterns.md` - Spring Boot 3 new features and design patterns
- `jpa-postgres-guide.md` - JPA and PostgreSQL best practices
- `common-patterns.md` - Common business scenario code patterns

## Output Format

After skill execution, output results in the following format:

```
## Analysis Report

### Project Overview
[Project structure and technology stack overview]

### Analysis for Your Requirements
[Targeted analysis of the described feature/issue]

### Modification Suggestions

#### File: [Path]
**Current Code:**
```java
[current code snippet]
```

**Recommended Change:**
```java
[modified code snippet]
```

**Explanation:** [reason for change and impact]

### Implementation Steps
1. [specific action steps]
2. ...
```

## Limitations

This skill does not cover:
- Frontend code modifications (React/Vue, etc.)
- Non-Spring ecosystem Java projects
- Detailed analysis of Spring Boot 2.x or below projects
- Specific SQL optimization for database performance tuning
