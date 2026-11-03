# 框架技术参考

本文档详细列出所有支持的编程语言、框架及其对应的项目模板。

## Python

### FastAPI
- **特点**: 现代、快速（高性能）、异步API框架
- **适用场景**: RESTful API、微服务、高性能Web应用
- **核心依赖**: fastapi, uvicorn, pydantic, sqlalchemy
- **可选依赖**: alembic(迁移), pytest-asyncio(测试), black(格式化)
- **启动命令**: `uvicorn app.main:app --reload`

### Django
- **特点**: 全功能Web框架、内置ORM、管理后台
- **适用场景**: 全栈Web应用、内容管理系统、企业应用
- **核心依赖**: django, djangorestframework
- **可选依赖**: django-cors-headers, celery, redis
- **启动命令**: `python manage.py runserver`

### Flask
- **特点**: 轻量级、高度可扩展
- **适用场景**: 小型到中型Web应用、RESTful API、原型开发
- **核心依赖**: flask, flask-sqlalchemy, flask-migrate
- **可选依赖**: flask-jwt-extended, flask-cors, celery
- **启动命令**: `flask run` 或 `python app.py`

### CLI工具
- **框架选择**: Click, Typer, argparse
- **特点**: 命令行界面生成器
- **适用场景**: DevOps工具、数据处理CLI、代码生成器
- **打包工具**: PyInstaller, setuptools

## JavaScript/TypeScript

### Node.js + Express
- **特点**: 经典、轻量、灵活
- **适用场景**: RESTful API、传统Web后端、微服务
- **核心依赖**: express, dotenv, cors
- **可选依赖**: express-validator, helmet, morgan
- **启动命令**: `npm run dev`

### NestJS
- **特点**: 渐进式、面向对象、依赖注入
- **适用场景**: 企业级应用、微服务、可扩展应用
- **核心依赖**: @nestjs/core, @nestjs/common, @nestjs/platform-express
- **可选依赖**: @nestjs/typeorm, @nestjs/jwt, @nestjs/passport
- **启动命令**: `npm run start:dev`

### Next.js
- **特点**: React全栈框架、服务端渲染、静态生成
- **适用场景**: SSR应用、SSG网站、全栈Web应用
- **核心依赖**: next, react, react-dom
- **可选依赖**: @tanstack/react-query, next-auth, prisma
- **启动命令**: `npm run dev`

### React + TypeScript
- **特点**: 组件化、生态丰富、类型安全
- **适用场景**: SPA应用、移动端Web应用、复杂交互界面
- **核心依赖**: react, react-dom, typescript
- **UI框架选项**: Tailwind CSS, Material UI, Ant Design, Chakra UI
- **状态管理**: Zustand, Jotai, Redux Toolkit
- **路由**: React Router v6
- **启动命令**: `npm run dev`

### Vue 3 + TypeScript
- **特点**: 渐进式、易学易用、性能优异
- **适用场景**: SPA应用、企业级后台、轻量级应用
- **核心依赖**: vue, vue-router, pinia
- **UI框架选项**: Element Plus, Ant Design Vue, Naive UI
- **构建工具**: Vite
- **启动命令**: `npm run dev`

### Angular
- **特点**: 完整解决方案、TypeScript优先、企业级
- **适用场景**: 企业级应用、大型SPA、复杂业务系统
- **核心依赖**: @angular/core, @angular/common, @angular/router
- **启动命令**: `ng serve`

## Java

### Spring Boot
- **特点**: 全功能、生态完善、企业级
- **适用场景**: 企业级应用、微服务、分布式系统
- **核心依赖**: spring-boot-starter-web, spring-boot-starter-data-jpa
- **可选依赖**: spring-boot-starter-security, spring-boot-starter-validation
- **构建工具**: Maven, Gradle
- **启动命令**: `./mvnw spring-boot:run`

### Spring Boot + Gradle + Kotlin
- **特点**: 现代JVM语言、简洁语法
- **适用场景**: 新一代Spring开发、微服务
- **核心依赖**: spring-boot, kotlin, jpa

## Go

### Gin
- **特点**: 高性能、轻量、API友好
- **适用场景**: 微服务、高性能API、网关
- **核心依赖**: gin-gonic/gin, gorm
- **可选依赖**: jwt-go, go-redis, viper(配置)
- **启动命令**: `go run cmd/server/main.go`

### Echo
- **特点**: 高性能、低内存、简洁API
- **适用场景**: Web服务、RESTful API
- **核心依赖**: labstack/echo/v5

### 标准CLI
- **特点**: 无框架依赖、轻量
- **适用场景**: DevOps工具、代码生成器、数据处理CLI
- **核心库**: cobra, viper, bubbletea

## Rust

### Actix-web
- **特点**: 最高性能actor系统、类型安全
- **适用场景**: 高性能Web服务、微服务
- **核心依赖**: actix-web, actix-rt
- **可选依赖**: sqlx, diesel, serde

### Axum
- **特点**: 异步、类型安全、模块化
- **适用场景**: 现代异步Web服务
- **核心依赖**: axum, tower

### Cargo CLI
- **特点**: 标准Cargo项目
- **适用场景**: CLI工具、系统编程
- **核心库**: clap, anyhow, tokio

## C#/.NET

### ASP.NET Core Web API
- **特点**: 高性能、跨平台、现代
- **适用场景**: RESTful API、微服务、现代Web后端
- **核心依赖**: Microsoft.AspNetCore.App
- **启动命令**: `dotnet run`

### Blazor
- **特点**: .NET前端框架、组件化
- **适用场景**: .NET生态全栈应用

## Ruby

### Rails
- **特点**: 全功能约定优于配置
- **适用场景**: Web应用、原型到生产级
- **核心依赖**: rails
- **启动命令**: `rails server`

### Sinatra
- **特点**: 轻量、DSL风格
- **适用场景**: 小型API、微服务
- **核心依赖**: sinatra, sequel

## PHP

### Laravel
- **特点**: 全功能、优雅语法、庞大生态
- **适用场景**: 企业Web应用、内容管理系统
- **核心依赖**: laravel/framework
- **启动命令**: `php artisan serve`

### Symfony
- **特点**: 组件化、企业级
- **适用场景**: 大型企业应用
- **核心依赖**: symfony/framework-bundle

## 数据库选项

### 关系型数据库
- **PostgreSQL**: 推荐用于大多数应用、强大的JSON支持
- **MySQL**: 广泛使用、高兼容性
- **SQLite**: 轻量、开发环境友好

### NoSQL数据库
- **MongoDB**: 文档数据库、灵活模式
- **Redis**: 缓存、消息队列、Session存储
- **Cassandra**: 分布式、高可用

### ORM选项
| 语言 | ORM |
|------|-----|
| Python | SQLAlchemy, Django ORM, Tortoise ORM |
| JavaScript/TS | Prisma, TypeORM, Sequelize, Drizzle |
| Go | GORM, sqlx, ent |
| Java | Spring Data JPA, MyBatis |
| Rust | Diesel, SQLx, SeaORM |

## 认证方案

### JWT (JSON Web Token)
-  stateless认证
- 适用于分布式系统
- 库: jsonwebtoken(JS), PyJWT(Python), golang-jwt(Go)

### Session
- 服务端存储
- 适用于传统Web应用
- 库: express-session(JS), django-session(Python)

### OAuth 2.0
- 第三方登录
- 授权码流程
- 库: Passport.js, Laravel Socialite

### API Key
- 简单API认证
- 适用于内部服务或公开API

## DevOps 配置

### Docker 基础镜像推荐

| 语言 | 基础镜像 |
|------|----------|
| Node.js | node:20-alpine |
| Python | python:3.11-slim |
| Go | golang:1.21-alpine |
| Java | eclipse-temurin:21-jre-alpine |
| Rust | rust:1.73-alpine |
| .NET | mcr.microsoft.com/dotnet/sdk:8.0 |

### CI/CD 平台
- **GitHub Actions**: `.github/workflows/`
- **GitLab CI**: `.gitlab-ci.yml`
- **Jenkins**: `Jenkinsfile`

### 监控和日志
- **日志**: ELK Stack, Loki, CloudWatch
- **监控**: Prometheus + Grafana, DataDog
- **追踪**: Jaeger, Zipkin
