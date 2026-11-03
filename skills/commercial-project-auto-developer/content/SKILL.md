---
name: commercial-project-auto-developer
description: "Super commercial-grade project automatic development AI skill. Use when users request to develop a complete commercial project from scratch, need full-stack development automation, want automated requirement analysis and decomposition, require code generation with commercial standards, or need deployment-ready project delivery. Triggers: develop project, commercial project, full-stack development, automated development, project development, build a project, develop an application, create a system, start new project, want to build"
---

# Commercial Project Auto-Developer

A super commercial-grade AI skill that automates the entire project development lifecycle from requirement analysis to deployment, with intelligent plan presentation and user confirmation workflow.

## Core Workflow Overview

```
User Request
    ↓
Phase 0: Requirement Understanding (Confirmation Required)
    ↓
Phase 1: Project Analysis & Planning (Confirmation Required)
    ↓
Phase 2: Intelligent Execution
    ↓
Phase 3: Quality Assurance & Delivery
```

---

## Phase 0: Requirement Understanding

**CRITICAL: This phase MUST be executed before any development work begins.**

### Step 0.1: Requirement Collection

When user submits a project request, automatically collect and clarify:

1. **Project Type**: Web App / Mobile App / Desktop App / Backend API / Data Platform / Full-Stack
2. **Industry Domain**: E-commerce / Finance / Healthcare / Education / Social / Enterprise / Other
3. **Core Functionality**: What problem does it solve?
4. **Target Users**: Who will use it?
5. **Scale Requirements**: Users / Transactions / Data volume expectations
6. **Technology Preferences**: Specific stack requirements (or open to recommendations)

### Step 0.2: Present Understanding & Confirm

Present the understood requirements back to user using GenUI form:

```xml
<genui-form-wizard title="Confirm Project Requirements" action-id="confirm_requirements">
<genui-form-page title="Step 1: Project Type (Single Selection)">
<genui-radio-group name="projectType">
<genui-radio value="web">Web Application</genui-radio>
<genui-radio value="mobile">Mobile Application</genui-radio>
<genui-radio value="desktop">Desktop Application</genui-radio>
<genui-radio value="backend">Backend API Service</genui-radio>
<genui-radio value="fullstack">Full-Stack Application</genui-radio>
<genui-radio value="dataplatform">Data Platform</genui-radio>
</genui-radio-group>
<genui-input selection-mode="radio" name="projectTypeNote" placeholder="Any specific requirements? (optional)"></genui-input>
</genui-form-page>
<genui-form-page title="Step 2: Industry & Scale (Single Selection)">
<genui-radio-group name="industry">
<genui-radio value="ecommerce">E-commerce</genui-radio>
<genui-radio value="finance">Finance / Fintech</genui-radio>
<genui-radio value="healthcare">Healthcare</genui-radio>
<genui-radio value="education">Education / EdTech</genui-radio>
<genui-radio value="social">Social / Community</genui-radio>
<genui-radio value="enterprise">Enterprise / B2B</genui-radio>
<genui-radio value="other">Other</genui-radio>
</genui-radio-group>
<genui-input selection-mode="radio" name="expectedScale" placeholder="Expected users/transactions? (optional)"></genui-input>
</genui-form-page>
<genui-form-page title="Step 3: Tech Stack (Multiple Selection)">
<genui-checkbox-group name="techStack">
<genui-checkbox value="python">Python (FastAPI/Django)</genui-checkbox>
<genui-checkbox value="javascript">JavaScript/TypeScript (Node.js)</genui-checkbox>
<genui-checkbox value="react">React/Vue/Angular</genui-checkbox>
<genui-checkbox value="java">Java/Kotlin</genui-checkbox>
<genui-checkbox value="go">Go</genui-checkbox>
<genui-checkbox value="rust">Rust</genui-checkbox>
<genui-checkbox value="dotnet">.NET / C#</genui-checkbox>
<genui-checkbox value="open">Open to recommendations</genui-checkbox>
</genui-checkbox-group>
<genui-input selection-mode="checkbox" name="databasePrefs" placeholder="Database preferences? (optional)"></genui-input>
</genui-form-page>
<genui-form-page title="Step 4: Confirm & Proceed">
<genui-radio-group name="proceed">
<genui-radio value="confirm">Yes, proceed with these requirements</genui-radio>
<genui-radio value="modify">I need to modify some requirements</genui-radio>
<genui-radio value="detailed">Give me detailed planning first</genui-radio>
</genui-radio-group>
<genui-input selection-mode="radio" name="additionalNotes" placeholder="Any additional requirements or notes? (optional)"></genui-input>
</genui-form-page>
</genui-form-wizard>
```

**WAIT for user response before proceeding to Phase 1.**

---

## Phase 1: Project Analysis & Planning

### Step 1.1: Project Type Recognition

Analyze and identify:
- Application type (Web/Desktop/Mobile/Backend/Data Platform)
- Industry domain (E-commerce/Finance/Healthcare/Education)
- Technology stack preferences (Language/Framework/Database)
- Complexity assessment (Simple/Medium/Complex/Enterprise)

### Step 1.2: Generate Recommended Plan

Generate multiple project plan options based on requirements:

#### Option A: Standard Full-Stack
- Frontend: React/Vue + TypeScript
- Backend: Node.js + Express/FastAPI
- Database: PostgreSQL + Redis
- Deployment: Docker + CI/CD

#### Option B: Modern Stack
- Frontend: Next.js/Remix (Full-stack framework)
- Backend: Integrated (same repo)
- Database: PostgreSQL + Prisma
- Deployment: Vercel/Netlify + Docker

#### Option C: Enterprise Grade
- Frontend: React + Redux Toolkit
- Backend: Java/Kotlin (Spring Boot)
- Database: PostgreSQL + MongoDB
- Infrastructure: Kubernetes + Istio
- Additional: Message Queue, CDN, etc.

#### Option D: Lightweight/MVP
- Frontend: Vue/React (minimal)
- Backend: Node.js + Express
- Database: SQLite/PostgreSQL
- Deployment: Single Docker container

### Step 1.3: Present Plan Options with GenUI

```xml
<genui-form-wizard title="Select Project Plan" action-id="select_plan">
<genui-form-page title="Step 1: Choose Architecture Pattern">
<genui-radio-group name="architecture">
<genui-radio value="standard">Standard Full-Stack</genui-radio>
<genui-radio value="modern">Modern Full-Stack (Next.js)</genui-radio>
<genui-radio value="enterprise">Enterprise Grade</genui-radio>
<genui-radio value="lightweight">Lightweight / MVP</genui-radio>
<genui-radio value="custom">Custom Configuration</genui-radio>
</genui-radio-group>
<genui-input selection-mode="radio" name="architectureReason" placeholder="Why this choice? (optional)"></genui-input>
</genui-form-page>
<genui-form-page title="Step 2: Core Modules Selection (Multiple Selection)">
<genui-checkbox-group name="modules">
<genui-checkbox value="auth">User Authentication & Authorization</genui-checkbox>
<genui-checkbox value="user_mgmt">User Management (CRUD)</genui-checkbox>
<genui-checkbox value="data_mgmt">Data Management</genui-checkbox>
<genui-checkbox value="file_upload">File Upload & Storage</genui-checkbox>
<genui-checkbox value="notifications">Notifications (Email/Push/SMS)</genui-checkbox>
<genui-checkbox value="payments">Payment Integration</genui-checkbox>
<genui-checkbox value="analytics">Analytics & Reporting</genui-checkbox>
<genui-checkbox value="api">RESTful API</genui-checkbox>
<genui-checkbox value="realtime">Real-time Features</genui-checkbox>
<genui-checkbox value="search">Search Functionality</genui-checkbox>
</genui-checkbox-group>
<genui-input selection-mode="checkbox" name="otherModules" placeholder="Other modules needed? (optional)"></genui-input>
</genui-form-page>
<genui-form-page title="Step 3: Quality & DevOps Options (Multiple Selection)">
<genui-checkbox-group name="devops">
<genui-checkbox value="ci_cd">CI/CD Pipeline</genui-checkbox>
<genui-checkbox value="testing">Unit & Integration Testing</genui-checkbox>
<genui-checkbox value="docker">Docker Containerization</genui-checkbox>
<genui-checkbox value="monitoring">Monitoring & Logging</genui-checkbox>
<genui-checkbox value="security">Security Scanning</genui-checkbox>
<genui-checkbox value="docs">Auto-generated Documentation</genui-checkbox>
<genui-checkbox value="db_migration">Database Migrations</genui-checkbox>
<genui-checkbox value="cdn">CDN Configuration</genui-checkbox>
</genui-checkbox-group>
<genui-input selection-mode="checkbox" name="devopsNotes" placeholder="DevOps requirements? (optional)"></genui-input>
</genui-form-page>
<genui-form-page title="Step 4: Final Confirmation">
<genui-radio-group name="finalConfirm">
<genui-radio value="proceed">Start development with these settings</genui-radio>
<genui-radio value="review">Review detailed plan first</genui-radio>
<genui-radio value="modify">I need to adjust something</genui-radio>
</genui-radio-group>
<genui-input selection-mode="radio" name="finalNotes" placeholder="Any final adjustments? (optional)"></genui-input>
</genui-form-page>
</genui-form-wizard>
```

### Step 1.4: Present Detailed Execution Plan

After user selects options, present the complete execution plan:

```xml
<genui-step-collapse title="Complete Project Execution Plan">
<genui-step-collapse-item label="Phase 1: Requirements & Planning" key="phase1">
<genui-li-item>Requirement Analysis & PRD Document</genui-li-item>
<genui-li-item>Project Type & Architecture Selection</genui-li-item>
<genui-li-item>Technology Stack Finalization</genui-li-item>
<genui-li-item>Module Decomposition & Dependencies</genui-li-item>
</genui-step-collapse-item>
<genui-step-collapse-item label="Phase 2: Backend Development" key="phase2">
<genui-li-item>Database Schema Design & SQL Generation</genui-li-item>
<genui-li-item>API Design & OpenAPI Documentation</genui-li-item>
<genui-li-item>Project Scaffold & Core Structure</genui-li-item>
<genui-li-item>Authentication & Authorization System</genui-li-item>
<genui-li-item>Core Business Logic Implementation</genui-li-item>
<genui-li-item>API Endpoints Implementation</genui-li-item>
<genui-li-item>Unit Tests for Backend</genui-li-item>
</genui-step-collapse-item>
<genui-step-collapse-item label="Phase 3: Frontend Development" key="phase3">
<genui-li-item>UI Component Library Setup</genui-li-item>
<genui-li-item>State Management Configuration</genui-li-item>
<genui-li-item>Page Layouts & Routing</genui-li-item>
<genui-li-item>API Integration Layer</genui-li-item>
<genui-li-item>Core Feature Implementation</genui-li-item>
<genui-li-item>Responsive Design Implementation</genui-li-item>
</genui-step-collapse-item>
<genui-step-collapse-item label="Phase 4: Security & Quality" key="phase4">
<genui-li-item>Security Code Review</genui-li-item>
<genui-li-item>Vulnerability Scanning & Fixes</genui-li-item>
<genui-li-item>Integration Testing</genui-li-item>
<genui-li-item>Performance Benchmarking</genui-li-item>
<genui-li-item>Code Quality Audit</genui-li-item>
</genui-step-collapse-item>
<genui-step-collapse-item label="Phase 5: Deployment & Delivery" key="phase5">
<genui-li-item>Docker Configuration</genui-li-item>
<genui-li-item>CI/CD Pipeline Setup</genui-li-item>
<genui-li-item>Deployment Scripts</genui-li-item>
<genui-li-item>Complete Documentation</genui-li-item>
<genui-li-item>Production Deployment</genui-li-item>
</genui-step-collapse-item>
</genui-step-collapse>

**Project:** [User's Project Name]
**Architecture:** [Selected Architecture]
**Modules:** [Selected Modules]
**Est. Duration:** [Estimated based on complexity]

**Deliverables:**
- Complete source code with commercial-grade quality
- PRD document
- API documentation
- Database schema
- Deployment configuration
- Test suites

**Please confirm to start development, or request modifications.**
```

---

## Phase 2: Intelligent Execution & Code Generation

**ONLY execute after user confirmation in Phase 1.**

For each task, follow this execution flow:

### Step 2.1: Resource Check

```
IF tool EXISTS → Execute tool
ELSE IF template EXISTS → Generate from template
ELSE → Enter intelligent generation flow
```

### Step 2.2: Intelligent Generation Flow

1. Analyze task requirements in detail
2. Search for relevant knowledge (if needed)
3. Generate complete code/document
4. Self-review against checklist
5. Present intermediate results for review (for complex tasks)

### Step 2.3: Self-Review Checklist

- [ ] Code completeness check (100% implementation, no TODOs)
- [ ] Error handling check (all failure scenarios handled)
- [ ] Comment completeness check (all public methods documented)
- [ ] Commercial-grade standards check
- [ ] Security compliance check (OWASP Top 10)
- [ ] Performance considerations (indexes, caching, async)
- [ ] Type safety (TypeScript types, Python type hints)

### Step 2.4: Intermediate Review (for complex tasks)

For major deliverables, present to user for review before proceeding:

```xml
<genui-form-wizard title="Review Deliverable" action-id="review_deliverable">
<genui-form-page title="Deliverable Review">
<genui-radio-group name="reviewDecision">
<genui-radio value="approve">Approved - Continue to next phase</genui-radio>
<genui-radio value="revise">Needs revision (specify below)</genui-radio>
<genui-radio value="pause">Pause for discussion</genui-radio>
</genui-radio-group>
<genui-input selection-mode="radio" name="revisionNotes" placeholder="Specify any revisions needed (if any)..."></genui-input>
</genui-form-page>
</genui-form-wizard>
```

---

## Phase 3: Quality Assurance & Delivery

### Step 3.1: Code Quality Check

- Run static analysis tools (ESLint, Pylint, etc.)
- Fix identified issues
- Verify code style compliance
- Check for code smells

### Step 3.2: Security Check

- OWASP Top 10 vulnerability scanning
- SQL injection protection verification
- XSS protection verification
- Authentication/Authorization verification
- Dependency audit (no vulnerable packages)

### Step 3.3: Test Verification

- Unit test execution (>= 80% coverage target)
- Integration test execution
- API endpoint testing
- UI smoke testing

### Step 3.4: Final Delivery

```xml
<genui-form-wizard title="Project Delivery" action-id="final_delivery">
<genui-form-page title="Final Review & Next Steps">
<genui-radio-group name="deliveryAction">
<genui-radio value="deploy">Deploy to production now</genui-radio>
<genui-radio value="staging">Deploy to staging first</genui-radio>
<genui-radio value="package">Package for manual deployment</genui-radio>
</genui-radio-group>
<genui-input selection-mode="radio" name="deploymentTarget" placeholder="Deployment target or notes (optional)"></genui-input>
</genui-form-page>
</genui-form-wizard>
```

### Deliverable Organization

- Complete source code repository
- Product Requirements Document (PRD)
- API Documentation (Swagger/OpenAPI)
- Database Schema Documentation
- Architecture Documentation
- Deployment Guide
- User Guide
- Developer Guide

---

## Execution Principles

### Principle 1: Confirm Before Execute (CHANGED)

```
RECEIVE request → UNDERSTAND requirements → PRESENT plan → GET confirmation → EXECUTE
```

**CRITICAL**: Never begin development without user confirmation of:
1. Project requirements (Phase 0)
2. Architecture and modules (Phase 1)
3. Detailed execution plan (Phase 1.4)

Only ask for clarification when requirements are ambiguous or insufficient.

### Principle 2: User Choice & Options

Always present multiple options when possible:
- At least 2-3 architecture choices
- Module selection options
- Technology stack alternatives
- Quality/DevOps options

Use GenUI forms for structured input and selection.

### Principle 3: Transparent Progress

Keep user informed:
- Show current phase and progress
- Present intermediate results for review
- Report any issues or blockers
- Explain decisions and trade-offs

### Principle 4: Modular Decomposition

Any project must be decomposed into:
- Requirement Analysis
- Architecture Design
- Database Design
- API Design
- Backend Development
- Frontend Development
- Testing
- Deployment

Each module continues to decompose into independently executable micro-tasks with clear inputs, outputs, and dependencies.

### Principle 5: Self-Evolution

**Trigger conditions for search learning:**
- Using unfamiliar technology stack specified by user
- Encountering unknown frameworks, libraries, tools
- Need to implement complex algorithms or business logic
- Need to comply with specific industry standards
- Performance-critical code
- Security-sensitive operations

**Search content:**
- Official documentation
- Best practices
- Example code
- Common issues and solutions
- Industry-specific compliance requirements

### Principle 6: Commercial-Grade Quality

Every output must meet commercial standards:
- Complete error handling at all layers
- Comprehensive logging for debugging
- Full documentation (comments, README, API docs)
- Security by design (OWASP compliance)
- Performance optimized (indexes, caching, async)
- Type safety (where applicable)

---

## Tool Invocation Priority

### Priority 1: Analysis Tools

| Task | Tools |
|------|-------|
| Requirement Analysis | `app_requirement_analyzer.py`, `user_requirement_interview.py` |
| Implicit Requirements | `implicit_requirement_miner.py` |
| Architecture Design | `architecture_diagram_generator.py`, `tech_risk_assessor.py` |
| Risk Assessment | `risk_assessment.py`, `decision_matrix.py` |
| Project Planning | `dev_effort_estimator.py`, `priority_sorting.py` |
| Document Generation | `multi_role_document_generator.py`, `rtm_builder.py` |

### Priority 2: Knowledge Base

| Phase | Path |
|-------|------|
| Requirement Analysis | `knowledge_base/01-requirement-analysis/` |
| Architecture Design | `knowledge_base/02-architecture-design/` |
| Development | `knowledge_base/03-development-quality/` |
| Deployment | `knowledge_base/04-deployment-ops/` |
| Security | `knowledge_base/05-security-vulnerability/` |

### Priority 3: Templates

| Type | Path |
|------|------|
| PRD Template | `templates/prd-template.md` |
| Architecture Doc | `templates/architecture-template.md` |
| API Spec | `templates/api-spec-template.md` |
| Test Template | `templates/test-template.md` |
| README Template | `templates/readme-template.md` |

### Priority 4: Intelligent Search & Generation

When no tool/template applies, search for:
- Latest official documentation
- Best practices guides
- Working code examples
- Common patterns and anti-patterns
- Industry-specific requirements

---

## Code Generation Standards

### Universal Standards

#### 1. File Header

```python
"""
Module: [Module Name]
Purpose: [Brief description of module responsibilities]
Author: MiniMax Agent
Created: YYYY-MM-DD
Version: 1.0.0
License: MIT
Dependencies: [Key dependencies]
"""

import standard_library
import third_party_packages
from local_modules import something
```

#### 2. Class Definition

```python
class ClassName:
    """
    Class description with purpose and responsibilities.

    This class handles [specific responsibility] by providing
    methods for [operations supported].

    Attributes:
        attr1: Description of class attribute
        attr2: Description of class attribute

    Example:
        >>> service = ClassName(config)
        >>> result = service.process(data)
    """

    def __init__(self, param1: Type1, param2: Type2) -> None:
        """
        Initialize the class with required dependencies.

        Args:
            param1: Description of parameter 1
            param2: Description of parameter 2

        Raises:
            ValueError: When parameter validation fails
            ConnectionError: When database connection fails
        """
        self.param1 = param1
        self.param2 = param2
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configure and return logger instance with structured format."""
        logger = logging.getLogger(self.__class__.__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def method_name(self, param: Type) -> ReturnType:
        """
        Method description explaining what it does.

        Args:
            param: Parameter description

        Returns:
            Description of return value

        Raises:
            CustomException: When specific error condition occurs
        """
        try:
            # Input validation
            self._validate_input(param)

            # Core logic
            result = self._process_data(param)

            # Logging for audit
            self.logger.info(f"Successfully processed: {param}")

            return result
        except SpecificException as e:
            self.logger.error(f"Specific error occurred: {e}")
            raise CustomException("User-friendly error message") from e
        except Exception as e:
            self.logger.exception(f"Unexpected error in method_name")
            raise
```

#### 3. Error Handling Pattern

```python
try:
    # Operation that may fail
    result = risky_operation()
    return result
except SpecificException as e:
    logger.error(f"Expected error context: {e}")
    raise CustomError("Actionable error message") from e
except Exception as e:
    logger.exception("Unexpected error occurred in operation")
    raise
finally:
    # Resource cleanup (always executed)
    if resource:
        resource.release()
```

#### 4. Configuration Management

```python
import json
from pathlib import Path
from typing import Any, Optional
import yaml
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration with validation."""
    host: str = Field(default="localhost")
    port: int = Field(default=5432, ge=1, le=65535)
    name: str = Field(..., min_length=1)
    pool_size: int = Field(default=10, ge=1, le=100)
    ssl_mode: str = Field(default="prefer")


class ConfigManager:
    """Centralized configuration management with environment override."""

    def __init__(self, config_path: str = "config.yaml") -> None:
        self.config_path = Path(config_path)
        self._config: dict = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file with environment override."""
        if self.config_path.exists():
            suffix = self.config_path.suffix.lower()
            if suffix in ('.yaml', '.yml'):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
            elif suffix == '.json':
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
        else:
            self._config = self._get_default_config()

        # Environment variable overrides
        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        import os
        env_mappings = {
            'DB_HOST': ('database', 'host'),
            'DB_PORT': ('database', 'port'),
            'DB_NAME': ('database', 'name'),
            'LOG_LEVEL': ('logging', 'level'),
        }
        for env_var, (section, key) in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                if section not in self._config:
                    self._config[section] = {}
                self._config[section][key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
```

### Language-Specific Standards

#### Python Web (FastAPI)

```python
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from contextlib import asynccontextmanager
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    logger.info("Starting application...")
    try:
        await initialize_database()
        await initialize_cache()
        await initialize_services()
        logger.info("Application startup complete")
    except Exception as e:
        logger.exception("Failed to start application")
        raise
    yield
    # Shutdown
    logger.info("Shutting down application...")
    await cleanup_services()
    await cleanup_database()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Project API",
    description="Commercial-grade API service with comprehensive error handling",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],  # Specify exact origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# Request/Response Models
class UserCreateRequest(BaseModel):
    """Request model for user creation."""
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)

    @validator('email')
    def validate_email(cls, v):
        return v.lower().strip()

    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower().strip()

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v


class UserResponse(BaseModel):
    """Response model for user data."""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    created_at: datetime
    is_active: bool = True


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = True
    data: Optional[Any] = None
    message: str = ""
    errors: Optional[List[dict]] = None
    pagination: Optional[dict] = None


@app.post("/api/v1/users", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    background_tasks: BackgroundTasks
) -> APIResponse:
    """
    Create a new user account.

    Args:
        request: Validated user creation data

    Returns:
        Standardized API response with user data

    Raises:
        HTTPException: 400 if validation fails, 409 if email/username exists
    """
    try:
        # Check for existing user
        existing = await user_service.find_by_email(request.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Create user
        user = await user_service.create(request.dict())

        # Background task for welcome email
        background_tasks.add_task(send_welcome_email, user.email)

        logger.info(f"User created: {user.id}")

        return APIResponse(
            success=True,
            data=UserResponse.from_orm(user).dict(),
            message="User created successfully"
        )

    except HTTPException:
        raise
    except BusinessException as e:
        logger.warning(f"Business error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Unexpected error creating user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

#### TypeScript (Node.js)

```typescript
/**
 * Module: UserService
 * Purpose: User management and authentication
 * Author: MiniMax Agent
 * Version: 1.0.0
 */

import { Router, Request, Response, NextFunction } from 'express';
import { body, param, validationResult, ValidationChain } from 'express-validator';
import Joi from 'joi';
import winston from 'winston';
import { v4 as uuidv4 } from 'uuid';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// Validation Schemas
const userSchema = Joi.object({
  email: Joi.string().email().required().lowercase().trim(),
  username: Joi.string().alphanum().min(3).max(50).required().lowercase().trim(),
  password: Joi.string().min(8).max(128).required()
    .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/),
  fullName: Joi.string().max(255).optional()
});

// Interfaces
interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  message?: string;
  errors?: ValidationError[];
  pagination?: PaginationInfo;
}

interface ValidationError {
  field: string;
  message: string;
}

interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

interface User {
  id: string;
  email: string;
  username: string;
  fullName?: string;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

abstract class BaseController {
  protected logger: winston.Logger;

  constructor() {
    this.logger = logger;
  }

  protected handleValidation(req: Request): void {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      const formattedErrors: ValidationError[] = errors.array().map(err => ({
        field: 'path' in err ? err.path : 'unknown',
        message: err.msg
      }));
      throw new ValidationException('Validation failed', formattedErrors);
    }
  }

  protected successResponse<T>(
    res: Response,
    data: T,
    message = 'Success',
    statusCode = 200,
    pagination?: PaginationInfo
  ): void {
    const response: ApiResponse<T> = {
      success: true,
      data,
      message,
      ...(pagination && { pagination })
    };
    res.status(statusCode).json(response);
  }

  protected errorResponse(
    res: Response,
    statusCode: number,
    message: string,
    errors?: ValidationError[]
  ): void {
    const response: ApiResponse = {
      success: false,
      message,
      errors
    };
    res.status(statusCode).json(response);
  }
}

class ValidationException extends Error {
  public statusCode: number;
  public errors?: ValidationError[];

  constructor(message: string, errors?: ValidationError[]) {
    super(message);
    this.statusCode = 400;
    this.errors = errors;
  }
}

export class UserController extends BaseController {
  private userService: UserService;

  constructor(userService: UserService) {
    super();
    this.userService = userService;
  }

  /**
   * Create new user account
   * POST /api/v1/users
   */
  public createUser = async (
    req: Request,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      // Validate request body
      const { error, value } = userSchema.validate(req.body);
      if (error) {
        throw new ValidationException('Validation failed', [{
          field: error.details[0].path.join('.'),
          message: error.details[0].message
        }]);
      }

      // Check for existing user
      const existingUser = await this.userService.findByEmail(value.email);
      if (existingUser) {
        res.status(409).json({
          success: false,
          message: 'Email already registered'
        });
        return;
      }

      // Create user
      const user = await this.userService.create(value);

      this.logger.info(`User created: ${user.id}`);
      this.successResponse(res, this.mapToResponse(user), 'User created successfully', 201);
    } catch (error) {
      this.logger.error('Error creating user', { error });
      next(error);
    }
  };

  /**
   * Get user by ID
   * GET /api/v1/users/:id
   */
  public getUser = async (
    req: Request,
    res: Response,
    next: NextFunction
  ): Promise<void> => {
    try {
      const { id } = req.params;

      const user = await this.userService.findById(id);
      if (!user) {
        res.status(404).json({
          success: false,
          message: 'User not found'
        });
        return;
      }

      this.successResponse(res, this.mapToResponse(user));
    } catch (error) {
      this.logger.error('Error getting user', { error });
      next(error);
    }
  };

  private mapToResponse(user: User): Partial<User> {
    const { password, ...safeUser } = user;
    return safeUser;
  }
}
```

#### Database Schema (PostgreSQL)

```sql
-- ============================================================================
-- Database Schema: Commercial Project
-- Author: MiniMax Agent
-- Created: YYYY-MM-DD
-- Version: 1.0.0
-- Description: Complete database schema with audit trails and indexes
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- Enum Types
-- ----------------------------------------------------------------------------
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'deleted');
CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled');
CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed', 'refunded');

-- ----------------------------------------------------------------------------
-- Users Table
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    avatar_url TEXT,
    status user_status NOT NULL DEFAULT 'active',
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES users(id),
    last_login_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_username_format CHECK (username ~* '^[a-z0-9_]{3,100}$')
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
CREATE INDEX idx_users_email_trgm ON users USING gin (email gin_trgm_ops);

-- ----------------------------------------------------------------------------
-- Audit Log Table
-- ----------------------------------------------------------------------------
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL,
    old_data JSONB,
    new_data JSONB,
    user_id UUID REFERENCES users(id),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_table ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- ----------------------------------------------------------------------------
-- Audit Trigger Function
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, record_id, action, new_data, user_id)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, to_jsonb(NEW), current_setting('app.current_user_id', true)::UUID);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_data, new_data, user_id)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, to_jsonb(OLD), to_jsonb(NEW), current_setting('app.current_user_id', true)::UUID);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_data, user_id)
        VALUES (TG_TABLE_NAME, OLD.id, TG_OP, to_jsonb(OLD), current_setting('app.current_user_id', true)::UUID);
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER audit_users_changes
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger();
```

---

## Project Structure Template

```
project-name/
├── src/
│   ├── backend/
│   │   ├── api/
│   │   │   ├── controllers/      # Route handlers
│   │   │   ├── middleware/       # Auth, logging, error handling
│   │   │   ├── routes/           # Route definitions
│   │   │   ├── validators/       # Request validation
│   │   │   └── docs/             # API documentation
│   │   ├── core/
│   │   │   ├── config/           # Configuration management
│   │   │   ├── database/         # DB connection, migrations
│   │   │   ├── exceptions/       # Custom exceptions
│   │   │   ├── logging/          # Logging setup
│   │   │   └── utils/            # Utility functions
│   │   ├── models/               # Data models/entities
│   │   ├── services/             # Business logic
│   │   ├── repositories/         # Data access layer
│   │   ├── events/               # Event handlers
│   │   ├── jobs/                 # Background jobs
│   │   └── main.py               # Application entry
│   ├── frontend/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── common/          # Generic components
│   │   │   └── features/         # Feature-specific components
│   │   ├── pages/               # Page components
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   └── settings/
│   │   ├── hooks/               # Custom React hooks
│   │   ├── stores/              # State management (Redux/Zustand)
│   │   ├── services/            # API client layer
│   │   ├── utils/               # Utility functions
│   │   ├── types/               # TypeScript type definitions
│   │   ├── constants/           # App constants
│   │   ├── styles/              # Global styles
│   │   └── App.tsx              # Root component
│   └── shared/
│       ├── types/               # Shared type definitions
│       ├── constants/            # Shared constants
│       ├── validators/           # Shared validation schemas
│       └── utils/                # Shared utilities
├── tests/
│   ├── unit/
│   │   ├── backend/             # Backend unit tests
│   │   └── frontend/            # Frontend unit tests
│   ├── integration/             # Integration tests
│   ├── e2e/                     # End-to-end tests
│   └── fixtures/                # Test fixtures
├── config/
│   ├── development.yaml
│   ├── staging.yaml
│   ├── production.yaml
│   └── docker-compose.yml
├── scripts/
│   ├── setup.sh                 # Initial setup script
│   ├── deploy.sh                 # Deployment script
│   ├── migrate.sh               # Database migrations
│   ├── seed.sh                  # Database seeding
│   └── backup.sh                # Backup script
├── docs/
│   ├── api/                     # API documentation
│   ├── architecture/           # Architecture diagrams
│   ├── deployment/              # Deployment guides
│   └── guides/                  # User/developer guides
├── .env.example                 # Environment template
├── .env.local                   # Local environment
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker compose
├── .dockerignore
├── .gitignore
├── package.json                 # Node dependencies
├── pyproject.toml               # Python dependencies
├── tsconfig.json                # TypeScript config
├── eslint.config.js             # ESLint config
├── prettier.config.js           # Prettier config
├── jest.config.js               # Jest config
├── pytest.ini                   # Pytest config
├── README.md                    # Project README
├── CONTRIBUTING.md              # Contributing guidelines
├── LICENSE                      # License file
└── CHANGELOG.md                 # Version changelog
```

---

## Quality Gates

### Gate 1: Code Quality

- [ ] All code passes linting (ESLint/Pylint/Flake8)
- [ ] No critical or high severity static analysis warnings
- [ ] Code coverage >= 80%
- [ ] No TODO/FIXME comments in production code
- [ ] No hardcoded secrets or credentials
- [ ] Consistent code style throughout

### Gate 2: Security

- [ ] No OWASP Top 10 vulnerabilities
- [ ] All dependencies have no known vulnerabilities (npm audit, pip-audit)
- [ ] SQL injection protected (parameterized queries)
- [ ] XSS protection (input sanitization, output encoding)
- [ ] CSRF protection (tokens, SameSite cookies)
- [ ] Authentication and authorization verified
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] Sensitive data encrypted at rest

### Gate 3: Testing

- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass
- [ ] API tests pass (all endpoints)
- [ ] UI tests pass (critical flows)
- [ ] Performance benchmarks met
- [ ] Load testing passed (expected concurrency)

### Gate 4: Documentation

- [ ] README complete with setup instructions
- [ ] API documentation complete (OpenAPI/Swagger)
- [ ] Architecture documentation complete
- [ ] Deployment guide complete
- [ ] Contribution guidelines present
- [ ] License file present

### Gate 5: Deployment

- [ ] Docker image builds successfully
- [ ] All environment variables documented
- [ ] Health check endpoint responds
- [ ] Rollback plan documented
- [ ] Monitoring/alerting configured
- [ ] Backup strategy documented

---

## Search & Learning Protocol

### Trigger Conditions

Always trigger search learning when:

1. User specifies unfamiliar technology stack
2. Encountering unknown frameworks/libraries/tools
3. Implementing complex algorithms
4. Industry-specific requirements (HIPAA, GDPR, PCI-DSS)
5. Performance-critical code paths
6. Security-sensitive operations

### Search Strategy

```
1. Identify knowledge gap
   ↓
2. Formulate search query (3-5 keywords + version/year)
   ↓
3. Execute parallel searches:
   - Official documentation
   - Best practices guides
   - Stack Overflow solutions
   - GitHub examples
   ↓
4. Extract information from top 5-10 results
   ↓
5. Apply best practices to current task
   ↓
6. Document learned patterns
   ↓
7. Generate code with confidence
```

### Knowledge Application

- Apply official best practices
- Use working code examples from reputable sources
- Follow established design patterns
- Consider security implications
- Optimize for performance
- Include error handling

---

## Deliverable Standards

### Code Deliverables

- Clean, readable, maintainable code
- Comprehensive inline comments (public methods required)
- Type hints (Python) / TypeScript types
- Error handling at all layers
- Logging for debugging and audit
- Unit tests with >= 80% coverage
- No placeholder/TODO comments in final delivery

### Document Deliverables

- Clear structure with table of contents
- Step-by-step instructions
- Code examples (copy-paste ready)
- Screenshots (where applicable)
- Troubleshooting section
- FAQ section

### Configuration Deliverables

- Environment-specific configs
- Default values with documentation
- Secrets management guide
- Security recommendations
- Example .env file

---

## Output Format

When delivering completed project:

```
================================================================================
PROJECT DELIVERY REPORT
================================================================================

Project: [Project Name]
Status: COMPLETED
Completion Date: [Date]

SUMMARY
-------
[Brief description of what was delivered]

ARCHITECTURE
------------
[Selected architecture pattern]
[Technology stack overview]

DELIVERABLES
------------
[✓] Complete source code
[✓] PRD Document
[✓] API Documentation
[✓] Database Schema
[✓] Deployment Configuration
[✓] Test Suites
[✓] Developer Guide

QUALITY VERIFICATION
-------------------
[✓] Code Quality: All linting passed
[✓] Security: OWASP Top 10 verified
[✓] Testing: 85% coverage achieved
[✓] Documentation: Complete

NEXT STEPS
----------
1. Review the generated documentation
2. Set up environment variables
3. Run database migrations
4. Start development/staging server
5. Configure CI/CD pipeline
6. Deploy to production

================================================================================
```

---

## Advanced Features

### Multi-Tenant Support

When requested, include:
- Tenant isolation strategies
- Shared vs dedicated resources
- Tenant-specific configurations
- Cross-tenant data access controls

### Microservices Architecture

When scaling is required:
- Service decomposition patterns
- Inter-service communication
- API Gateway configuration
- Service mesh setup
- Distributed tracing

### Real-time Features

When real-time is needed:
- WebSocket implementation
- Server-Sent Events
- Message queue integration
- Presence indicators
- Notification systems

### API Versioning Strategy

- URL path versioning (/api/v1/)
- Header versioning
- Deprecation policies
- Migration guides

### Caching Strategy

- Application-level caching
- Database query caching
- CDN configuration
- Cache invalidation patterns

---

## Edge Cases & Error Handling

### Network Failures
- Retry with exponential backoff
- Circuit breaker pattern
- Graceful degradation

### Data Consistency
- Optimistic vs pessimistic locking
- Transaction management
- Eventual consistency handling

### Rate Limiting
- Per-user limits
- Global limits
- Response headers (X-RateLimit-*)

### File Upload
- Size limits
- Type validation
- Virus scanning
- Storage strategy

---

This skill provides end-to-end commercial-grade project development with user confirmation at every critical stage to ensure delivered results match user expectations.
