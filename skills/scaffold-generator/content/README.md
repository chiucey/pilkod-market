# Scaffold Generator - 软件开发框架生成器

## 概述

Scaffold Generator 是一个用于快速生成软件开发项目基本框架的 AI 技能。它能够帮助开发者快速启动新项目，避免从头开始配置项目结构的繁琐工作。

## 功能特点

- **多语言支持**: Python, JavaScript/TypeScript, Java, Go, Rust, C#, Ruby, PHP 等
- **多框架支持**: FastAPI, Django, Flask, Express, NestJS, Gin, Spring Boot 等
- **模块化选择**: 数据库、认证、API文档、Docker、CI/CD 等
- **标准化结构**: 遵循各语言和框架的最佳实践
- **可扩展模板**: 支持自定义模板和配置

## 快速开始

### 基本用法

当您需要创建新项目时，只需向 AI 描述您的需求：

```
创建一个名为 user-api 的 FastAPI 项目，包含用户认证和数据库集成
```

或使用更简洁的方式：

```
初始化一个 Python FastAPI 项目
```

### 交互式配置

技能会引导您完成以下配置步骤：

1. 项目名称
2. 编程语言选择
3. 框架/项目类型
4. 附加功能（可选）
   - 数据库集成
   - 认证授权
   - API文档
   - 单元测试
   - Docker支持
   - CI/CD配置

## 支持的技术栈

### 编程语言

| 语言 | 框架选项 |
|------|----------|
| Python | FastAPI, Django, Flask, CLI工具 |
| JavaScript/TypeScript | Express, NestJS, Next.js, React, Vue, Angular |
| Java | Spring Boot, Maven/Gradle项目 |
| Go | Gin, Echo, 标准CLI |
| Rust | Actix-web, Axum, Cargo CLI |
| C#/.NET | ASP.NET Core, Console应用 |
| Ruby | Rails, Sinatra |
| PHP | Laravel, Symfony |

### 数据库选项

- **关系型**: PostgreSQL, MySQL, SQLite
- **NoSQL**: MongoDB, Redis, Cassandra

### DevOps工具

- Docker & Docker Compose
- GitHub Actions
- GitLab CI
- Kubernetes配置

## 生成的项目结构

```
project-name/
├── README.md
├── LICENSE
├── .gitignore
├── package.json / pyproject.toml / go.mod
├── docker-compose.yml
├── .env.example
├── src/
│   ├── main/
│   ├── test/
│   └── config/
├── docs/
├── scripts/
├── tests/
└── config/
```

## 目录结构

```
scaffold-generator/
├── SKILL.md                    # 技能主定义文件
├── _meta.json                  # 技能元数据
├── README.md                   # 本文档
├── references/                 # 参考文档
│   ├── templates.md           # 项目模板参考
│   └── frameworks.md          # 框架技术参考
└── assets/                     # 模板资源
    ├── Dockerfile-template
    ├── docker-compose-template
    ├── github-actions-template
    └── env-example-template
```

## 参考文档

- [项目模板参考](references/templates.md) - 详细的项目结构模板
- [框架技术参考](references/frameworks.md) - 支持的框架和技术栈详情

## 资源文件

- `Dockerfile-template` - Docker容器化配置模板
- `docker-compose-template` - Docker Compose编排模板
- `github-actions-template` - GitHub Actions CI/CD模板
- `env-example-template` - 环境变量配置模板

## 使用示例

### 示例 1: 创建 Python FastAPI 项目

**输入**:
```
创建一个叫 user-service 的 FastAPI 项目，包含 JWT 认证和 PostgreSQL 数据库
```

**输出**:
- 完整的 FastAPI 项目结构
- JWT 认证模块
- SQLAlchemy 模型和数据库连接
- CRUD API 示例
- Swagger 文档配置
- Docker 支持

### 示例 2: 创建 React TypeScript 项目

**输入**:
```
初始化一个叫 dashboard-app 的 React + TypeScript 项目，使用 Tailwind CSS
```

**输出**:
- Vite + React + TypeScript 项目
- Tailwind CSS 配置
- 组件目录结构
- 路由配置
- API 服务层示例

### 示例 3: 创建 Go 微服务

**输入**:
```
生成一个叫 order-service 的 Go 微服务，需要 gRPC 和 Docker 支持
```

**输出**:
- Gin/标准 HTTP 框架项目
- 分层架构 (handler/service/repository)
- Protocol Buffers 定义
- Dockerfile 和 docker-compose.yml
- Makefile 构建脚本

## 最佳实践

1. **命名规范**: 使用 kebab-case 作为项目名称
2. **版本控制**: 生成后立即初始化 Git 仓库
3. **环境配置**: 复制 `.env.example` 为 `.env`，不要提交敏感信息
4. **依赖管理**: 使用锁文件 (package-lock.json, poetry.lock, go.sum)
5. **文档维护**: 保持 README.md 更新，记录重要的配置和命令

## 常见问题

### Q: 生成的项目可以直接运行吗？
A: 是的，生成的项目包含最小可运行的应用示例和必要的配置。

### Q: 如何添加额外的功能？
A: 您可以手动添加所需的功能，或在生成时说明需求，技能会尽可能包含相关配置。

### Q: 支持自定义模板吗？
A: 当前版本使用内置模板，自定义模板功能正在规划中。

## 许可证

本项目遵循 MIT 许可证。

## 更新日志

### v1.0.0 (2026-04-14)
- 初始版本发布
- 支持 8 种编程语言
- 支持 15+ 框架
- 包含 Docker 和 CI/CD 配置模板
