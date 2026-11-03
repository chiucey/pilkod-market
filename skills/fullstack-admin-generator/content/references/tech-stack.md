# 技术栈详细说明

## 前端技术栈

### 核心框架
- **Vue 3.4+**: 使用 Composition API + `<script setup>` 语法
- **TypeScript 5.x**: 强类型支持
- **Vite 5.x**: 下一代前端构建工具

### 状态管理
- **Pinia**: Vue 3 官方推荐的状态管理库

### UI 框架
- **Ant Design Vue 4.x** 或 **Element Plus 2.x**: 企业级 UI 组件库
- **TailwindCSS 3.x**: 原子化 CSS 框架

### 其他依赖
- **Vue Router 4.x**: 路由管理
- **Axios**: HTTP 请求
- **Day.js**: 日期处理
- **ECharts**: 图表可视化

## 后端技术栈

### 核心框架
- **Spring Boot 3.2.5**: 基于 Spring 6.x
- **Java 17+**: LTS 版本

### 数据层
- **MyBatis-Plus 3.5.x**: MyBatis 增强工具
- **HikariCP**: 连接池

### 认证授权
- **Sa-Token 1.37.x**: 轻量级认证授权框架
  - 支持 Token 认证
  - 支持权限验证
  - 支持 OAuth2 / SSO

### 工具库
- **Lombok**: 简化代码
- **Hutool**: Java 工具库
- **MapStruct**: 对象映射

## 数据库

### MySQL 8.0
- 支持 JSON 类型
- 支持窗口函数
- 支持 CTE 递归查询

### Redis 7.x
- 缓存层
- Session 存储
- 分布式锁

## 项目结构

### 前端目录结构
```
frontend/
├── public/
├── src/
│   ├── api/           # API 接口
│   ├── assets/        # 静态资源
│   ├── components/    # 公共组件
│   ├── composables/   # 组合式函数
│   ├── directives/   # 自定义指令
│   ├── hooks/         # Hooks
│   ├── layouts/       # 布局组件
│   ├── plugins/       # 插件
│   ├── router/        # 路由配置
│   ├── store/         # 状态管理
│   ├── types/         # TypeScript 类型
│   ├── utils/         # 工具函数
│   ├── views/         # 页面组件
│   ├── App.vue
│   └── main.ts
├── .env
├── .env.production
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

### 后端目录结构
```
backend/
├── src/
│   └── main/
│       ├── java/com/example/
│       │   ├── config/        # 配置类
│       │   ├── controller/    # 控制器
│       │   ├── service/       # 服务层
│       │   ├── mapper/        # 数据访问层
│       │   ├── entity/        # 实体类
│       │   ├── dto/           # 数据传输对象
│       │   ├── vo/            # 视图对象
│       │   ├── common/        # 公共类
│       │   ├── exception/     # 异常处理
│       │   └── Application.java
│       └── resources/
│           ├── mapper/        # MyBatis XML
│           ├── application.yml
│           └── logback.xml
├── pom.xml
└── README.md
```
