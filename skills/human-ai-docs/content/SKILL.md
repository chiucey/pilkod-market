---
name: human-ai-docs
description: This skill should be used when users want to organize and maintain their engineering project documentation with a dual-layer system - one for AI context (CLAUDE.md) and one for human readers (README.md). It triggers when users mention "梳理项目", "整理文档", "初始化工程", "organize project", "init project docs", or need to create/maintain AI-collaborative documentation for software projects.
version: 1.0.0
triggers:
  - "梳理项目"
  - "整理文档"
  - "初始化工程"
  - "organize project"
  - "init project docs"
  - "create project docs"
  - "更新工程文档"
  - "update project docs"
---

# Human-AI-Docs Skill

## Description

Human-AI-Docs maintains a **dual-layer documentation system** for software engineering projects:

1. **README.md (Human Layer)**: Natural language guide for human developers
2. **CLAUDE.md (AI Layer)**: Structured context for AI assistants with @import syntax
3. **docs/ (Technical Layer)**: Detailed technical documentation

This skill helps teams create consistent, maintainable project documentation that serves both human understanding and AI assistance.

## When to Use This Skill

Use this skill when:
- User wants to organize/initialize project documentation
- User mentions keywords: "梳理项目", "整理文档", "初始化工程"
- User needs to create dual-layer documentation (human + AI)
- User asks to update existing project documentation
- User wants to set up AI-collaborative project structure

## Core Philosophy

### Dual Documentation Design

| Layer | File | Audience | Style |
|-------|------|----------|-------|
| Human | README.md | Developers, Stakeholders | Natural language, Getting Started |
| AI | CLAUDE.md | AI Assistants | Structured, Task-oriented, @import |
| Technical | docs/*.md | Deep Reference | Detailed, Complete |

### Key Principles

1. **Separation of Concerns**: Human and AI documentation serve different purposes
2. **Task-Oriented**: Organize by "how to complete tasks" not by knowledge domains
3. **Minimal AI Context**: Keep CLAUDE.md lean (<100 lines) using @import
4. **Incremental Updates**: User describes changes, AI updates documentation

## Core Workflow

### Phase 1: Project Analysis

1. **Detect Project Type**
   - Scan project structure (package.json, requirements.txt, Cargo.toml, etc.)
   - Identify main directories (src/, lib/, api/, services/, etc.)
   - Determine tech stack

2. **Ask Key Questions**
   ```
   请描述项目的主要功能:
   - 这是什么类型的项目？(Web应用/库/工具/服务)
   - 主要使用的技术栈？
   - 核心模块有哪些？
   - 典型的开发工作流是什么？
   ```

### Phase 2: Documentation Generation

**Generate Three Layers:**

1. **README.md (Human Layer)**
   - Project overview and purpose
   - Quick start guide
   - Installation instructions
   - Common workflows
   - Contribution guidelines

2. **CLAUDE.md (AI Layer)**
   - Project structure summary
   - Task-oriented operation index
   - Tech stack reference
   - Build and test commands
   - Keep <100 lines with @import for details

3. **docs/ (Technical Layer)**
   - docs/architecture.md - Architecture design
   - docs/workflows.md - Development workflows
   - docs/api.md - API documentation (if applicable)
   - docs/testing.md - Testing guide

### Phase 3: Operation Index

Create a task-oriented index table in CLAUDE.md:

```markdown
## 操作索引表

| 操作指令 | 详细文档 | 触发词 |
|----------|----------|--------|
| 添加新API | @docs/api-workflow.md | "添加接口", "new API" |
| 运行测试 | @docs/testing.md | "测试", "run tests" |
| 部署应用 | @docs/deployment.md | "部署", "deploy" |
```

## @import Mechanism

Use `@path/to/file.md` syntax to reference detailed documentation:

```markdown
## 技术栈详解
@docs/tech-stack.md

## 架构概览
@docs/architecture.md
```

**Benefits:**
- Keep CLAUDE.md lean (<100 lines)
- Detailed content in docs/ files
- Easy to maintain and update

## File Structure

Generated project structure:

```
project-root/
├── README.md                    # Human user guide
├── CLAUDE.md                    # AI context (<100 lines)
├── docs/                        # Technical details
│   ├── architecture.md         # Architecture design
│   ├── workflows.md            # Development workflows
│   ├── tech-stack.md          # Technology stack
│   ├── api.md                 # API documentation
│   └── testing.md             # Testing guide
└── .ai-docs/                   # Documentation state
    └── doc-state.log.md       # Update history log
```

## Incremental Update Process

### When to Update

- New feature added
- Architecture change
- Tech stack update
- Workflow modification

### Update Workflow

```
用户: "我刚加了用户认证功能"
AI: "请描述主要变更：
      1. 新增了什么模块？
      2. 修改了哪些现有文件？
      3. 对文档的影响？"

用户: "添加了 auth/ 模块，包含登录注册"
AI: [分析影响]
    → 需要创建: docs/auth.md
    → 需要更新: docs/architecture.md
    → 需要更新: CLAUDE.md 操作索引表

AI: "确认更新以上文档？[Y/n]"
用户: Y
AI: [执行更新]
```

## Doc State Log

Track documentation updates in `.ai-docs/doc-state.log.md`:

```markdown
# Doc State Log

## [2026-03-27] UPDATE
- **Changes**: Added auth module
- **Files**:
  - docs/auth.md (created)
  - docs/architecture.md (updated)
  - CLAUDE.md (updated)
```

## Examples

See @references/usage-example.md for complete workflow demonstration.

## Templates

Configuration templates available:
- @templates/README-template.md
- @templates/CLAUDE-template.md

## Best Practices

1. **Keep CLAUDE.md Lean**: Use @import for details, main file <100 lines
2. **Task-Oriented Index**: Organize by operations, not by components
3. **Human-Readable README**: Focus on onboarding and quick start
4. **Detailed docs/**: Comprehensive technical reference
5. **Regular Updates**: Update docs when code changes
