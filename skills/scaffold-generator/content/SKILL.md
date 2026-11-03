---
name: scaffold-generator
description: Generates software project scaffolding. Use when users request creating new projects, initializing project structures, generating code templates, quickly setting up project skeletons, or creating basic programming language structures. Trigger phrases include: "create project", "generate framework", "initialize project", "setup project", "new project", "project structure".
---

# Scaffold Generator - Software Project Framework Generator

## Skill Overview

This skill is used to quickly generate basic framework structures for software development projects. It supports multiple mainstream programming languages, frameworks, and project types to help developers quickly start new projects.

## Supported Project Types

### Programming Languages
- **Python**: Django, Flask, FastAPI, CLI tools, Data science projects
- **JavaScript/TypeScript**: Node.js, React, Vue, Angular, Express
- **Java**: Spring Boot, Maven multi-module, Gradle projects
- **Go**: Gin, Echo, Standard CLI projects
- **Rust**: Cargo projects, WASM
- **C#/.NET**: ASP.NET Core, Console applications, Class libraries
- **Ruby**: Rails, Sinatra
- **PHP**: Laravel, Symfony

### Project Types
- Web backend API services
- Web frontend applications
- Command-line tools (CLI)
- Libraries/SDKs
- Microservices
- Full-stack applications
- Mobile backend
- Data processing pipelines

## Workflow

### Step 1: Collect Project Requirements

Use interactive forms to collect the following information:

1. **Project Name** (Required)
   - Use kebab-case format (auto-converted)

2. **Programming Language** (Required)
   - Select from the supported list above

3. **Framework/Project Type** (Required)
   - Display corresponding framework options based on language

4. **Additional Features** (Multiple Selection)
   - Database integration
   - Authentication & Authorization
   - API documentation
   - Unit testing
   - Docker support
   - CI/CD configuration
   - Environment configuration management
   - Logging system
   - Caching layer
   - Message queue

5. **Output Directory**
   - Default: current working directory
   - Can specify absolute or relative paths

### Step 2: Generate Project Structure

Based on collected information, generate the following standard structure:

```
project-name/
├── README.md                 # Project documentation
├── LICENSE                   # Open source license
├── .gitignore               # Git ignore configuration
├── package.json             # Dependency config (JS/TS)
├── pyproject.toml           # Python project config
├── pom.xml / build.gradle   # Java build config
├── docker-compose.yml       # Docker orchestration config
├── .env.example             # Environment variables example
├── src/                     # Source code directory
│   ├── main/               # Main code
│   ├── test/               # Test code
│   └── config/             # Configuration files
├── docs/                    # Documentation directory
├── scripts/                 # Scripts directory
├── tests/                   # Test directory
└── config/                  # Configuration directory
```

### Step 3: Generate Core Files

Generate the following core files based on project type:

#### Configuration Files
- **package.json / setup.py / pom.xml / go.mod**: Dependency management
- **tsconfig.json / pyproject.toml**: Language configuration
- **.eslintrc / .prettierrc**: Code style configuration
- **jest.config.js / pytest.ini**: Test configuration

#### Entry Files
- **index.ts / main.py / main.go / Program.cs**: Application entry point
- **app.js / app.py**: Application main module

#### Configuration Management
- **config.ts / config.py**: Configuration management module
- **.env.example**: Environment variables example
- **config.yaml / settings.json**: Configuration file templates

#### Authentication & Authorization
- **auth.ts / auth.py**: Authentication module
- **middleware/auth.ts**: Authentication middleware
- **models/user.ts**: User model

#### Database
- **models/*.ts**: Data models
- **database.ts / db.ts**: Database connection
- **migrations/**: Database migration files
- **seeds/**: Data seed files

#### API Related
- **routes/*.ts**: Route definitions
- **controllers/*.ts**: Controllers
- **services/*.ts**: Business logic layer
- **swagger.yaml / openapi.json**: API documentation

#### Testing
- **__tests__/**: Test files
- **fixtures/**: Test data
- **setup.ts**: Test configuration

#### DevOps
- **Dockerfile**: Containerization configuration
- **docker-compose.yml**: Multi-container orchestration
- **.github/workflows/**: GitHub Actions configuration
- **.gitlab-ci.yml**: GitLab CI configuration

### Step 4: Generate Sample Code

Generate runnable sample code based on selected framework and features:

1. **Basic Application Structure**
   - Minimal runnable application example
   - Basic CRUD operations example

2. **Configuration Examples**
   - Database connection configuration
   - Environment variables usage example

3. **Middleware Examples**
   - Authentication middleware
   - Logging middleware
   - Error handling middleware

4. **Test Examples**
   - Unit test examples
   - Integration test examples

### Step 5: Output Completion Report

Generate a completion report with the following information:

```
Project framework generation complete!

Project Name: {project-name}
Tech Stack: {language} + {framework}
Output Path: {output-path}

Generated Files:
   - Configuration files (n)
   - Source code files (n)
   - Test files (n)
   - Documentation files (n)
   - DevOps files (n)

Quick Start:
   1. cd {project-name}
   2. Install dependencies: {install-command}
   3. Configure environment variables
   4. Run project: {run-command}

Recommended Next Steps:
   - Read README.md for project structure
   - Configure database connection
   - Write business logic code
   - Write unit tests
```

## Output Specifications

### File Naming Conventions
- Source code files: Use standard naming conventions for the project language
- Configuration files: Use dot-prefix format (`.env`, `.gitignore`)
- Test files: Use `*.test.*` or `*_test.*` format

### Code Style
- Follow official style guides for each language
- Use consistent indentation and formatting across the project
- Include appropriate comments

### Documentation Requirements
- README.md must include:
  - Project introduction
  - Quick start guide
  - Project structure description
  - Development guide
  - Deployment instructions

## Usage Examples

### Example 1: Create Python FastAPI Project

**User Input**: "Create a FastAPI project named user-api with user authentication and database integration"

**Generated Results**:
- Complete project structure
- Authentication module included
- Database models and connection configuration
- CRUD API examples
- Swagger documentation configuration

### Example 2: Create React TypeScript Project

**User Input**: "Initialize a React + TypeScript project called dashboard-frontend"

**Generated Results**:
- Complete React project structure
- TypeScript configuration
- Component directory structure
- Route configuration
- State management configuration

### Example 3: Create Go Microservice Project

**User Input**: "Generate a Go microservice framework called order-service with Docker support"

**Generated Results**:
- Gin framework project structure
- Layered architecture (handler/service/repository)
- Dockerfile and docker-compose.yml
- Makefile
- Health check endpoint

## Quality Assurance

### Pre-Generation Validation
- Check if a project with the same name already exists in target directory
- Validate directory path validity
- Check available disk space

### Post-Generation Validation
- Confirm all files have been created
- Verify file completeness
- Check dependency configuration syntax

### Error Handling
- Directory creation failed: Prompt and ask for new path
- Insufficient permissions: Prompt with suggested solutions
- Insufficient disk space: Show required and available space
