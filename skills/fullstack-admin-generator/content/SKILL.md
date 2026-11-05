---
name: fullstack-admin-generator
description: 快速生成全栈管理后台项目脚手架。当用户要求创建后台管理系统、生成前后端项目结构、初始化 Vue3 + Spring Boot 项目、或需要一键生成管理后台模板时使用。
---

# 全栈管理后台项目生成器

一键生成基于 Soybean Admin (Vue3) + Spring Boot 的管理后台项目脚手架。

## 技术栈

| 层级 | 技术选型 |
|------|----------|
| 前端 | Vue 3 + TypeScript + Vite + Pinia + Vue Router |
| 后端 | Spring Boot 3.2.5 + MyBatis-Plus + Sa-Token |
| 数据库 | MySQL 8.0 + Redis |
| 部署 | Docker + Docker Compose |

## 工作流程

### 1. 创建项目结构

```
project-name/
├── frontend/           # 前端项目 (Soybean Admin)
├── backend/            # 后端项目 (Spring Boot)
├── db/                 # 数据库脚本
└── docker-compose.yml  # 容器编排
```

### 2. 生成前端项目配置

生成内容：
- `package.json` - 依赖配置
- `vite.config.ts` - Vite 配置
- `tsconfig.json` - TypeScript 配置
- `src/` - 源码目录结构
- `.env` - 环境变量

### 3. 生成后端项目配置

生成内容：
- `pom.xml` - Maven 依赖
- `application.yml` - 应用配置
- `src/main/java/` - Java 源码结构
- `src/main/resources/` - 资源配置

### 4. 生成数据库脚本

生成内容：
- `init.sql` - 建表脚本
- `data.sql` - 初始数据
- Redis 配置

## 使用方式

用户可通过以下方式指定项目信息：
- **交互式**: 使用 GenUI 表单收集项目名称、包名、数据库配置
- **参数式**: 直接传入项目配置参数

## 输出产物

1. 完整的前端项目脚手架（可直接 `npm install && npm run dev`）
2. 完整的后端项目脚手架（可直接导入 IDE 运行）
3. Docker 部署配置
4. 数据库初始化脚本
