# Agent Skills 平台技术架构设计

---

## 1. 架构设计原则

### 1.1 设计理念

本平台采用**云原生微服务架构**，遵循以下核心原则：

| 原则 | 描述 | 实践 |
|------|------|------|
| 高可用 | 系统持续稳定运行 | 多AZ部署、自动故障转移 |
| 可扩展 | 平滑应对业务增长 | 水平扩展、服务解耦 |
| 可观测 | 全方位系统监控 | 日志、指标、链路追踪 |
| 安全性 | 端到端安全保障 | 零信任架构、多层防护 |
| 开发者友好 | 降低接入成本 | 完善SDK、API文档 |

### 1.2 技术选型总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端层                                  │
├─────────────────────────────────────────────────────────────────┤
│  Web应用 (React 18 + TypeScript + Ant Design)                    │
│  移动App (React Native / Flutter)                                │
│  小程序 (Taro)                                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        网关层                                    │
├─────────────────────────────────────────────────────────────────┤
│  Kong API Gateway                                                │
│  • 请求路由/负载均衡                                             │
│  • 认证授权/限流熔断                                             │
│  • 日志记录/监控上报                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        服务层 (Kubernetes)                      │
├──────────────┬──────────────┬──────────────┬──────────────┬─────┤
│   用户服务   │   技能服务   │   订单服务   │   支付服务   │ ... │
│  User Service│  Skill Service│ Order Service│Payment Service│     │
└──────────────┴──────────────┴──────────────┴──────────────┴─────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据层                                    │
├──────────────┬──────────────┬──────────────┬──────────────┬─────┤
│   PostgreSQL │    Redis     │  Elasticsearch│    OSS       │ ... │
│   主数据库    │  缓存/会话    │  全文检索     │  文件存储     │     │
└──────────────┴──────────────┴──────────────┴──────────────┴─────┘
```

---

## 2. 系统架构设计

### 2.1 整体架构图

```
                            ┌─────────────────┐
                            │   CDN (全球)    │
                            │  静态资源加速   │
                            └────────┬────────┘
                                     │
                            ┌────────▼────────┐
                            │  负载均衡器      │
                            │  (SLB/Alb)      │
                            └────────┬────────┘
                                     │
                            ┌────────▼────────┐
                            │   API Gateway   │
                            │  (Kong/Nginx)   │
                            └────────┬────────┘
                                     │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────▼───────┐             ┌───────▼───────┐             ┌───────▼───────┐
│   前台Web     │             │   移动App     │             │   管理后台    │
│   (SSR/CSR)   │             │   (API调用)   │             │   (SPA)       │
└───────────────┘             └───────────────┘             └───────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
           ┌─────────▼─────────┐ ┌────▼────┐ ┌────────▼────────┐
           │   用户服务集群    │ │技能服务  │ │   订单服务集群   │
           │  (3 Pods)        │ │ 集群     │ │   (3 Pods)     │
           └─────────┬─────────┘ └────┬────┘ └────────┬────────┘
                     │                │               │
           ┌─────────┴────────────────┴───────────────┴────────┐
           │                    │                             │
    ┌──────▼──────┐     ┌───────▼──────┐             ┌─────────▼──────┐
    │  PostgreSQL │     │   Redis      │             │ Elasticsearch  │
    │  主从集群   │     │  Cluster     │             │  Search Cluster│
    └─────────────┘     └─────────────┘             └────────────────┘
```

### 2.2 核心服务设计

#### 2.2.1 用户服务 (User Service)

**职责**：用户注册、登录、认证、权限管理

**技术栈**：

- 框架：Spring Boot 3.x / NestJS
- 认证：JWT + Redis Session
- 缓存：Redis Cluster

**核心接口**：

```
POST   /api/v1/auth/register        # 用户注册
POST   /api/v1/auth/login           # 用户登录
POST   /api/v1/auth/logout          # 登出
POST   /api/v1/auth/refresh         # 刷新Token
GET    /api/v1/users/me             # 获取当前用户信息
PUT    /api/v1/users/me             # 更新用户信息
POST   /api/v1/users/verify         # 实名认证
```

**数据模型**：

```typescript
interface User {
  id: string;              // UUID
  email: string;           // 邮箱（唯一）
  phone?: string;          // 手机号
  passwordHash: string;    // 密码哈希
  nickname: string;        // 昵称
  avatar?: string;         // 头像URL
  role: 'user' | 'developer' | 'admin';
  status: 'active' | 'frozen' | 'deleted';
  developerStatus?: 'none' | 'pending' | 'approved' | 'rejected';
  createdAt: Date;
  updatedAt: Date;
}
```

#### 2.2.2 技能服务 (Skill Service)

**职责**：技能发布、审核、上下架、搜索

**技术栈**：

- 框架：Spring Boot 3.x / NestJS
- 全文检索：Elasticsearch
- 文件存储：OSS/MinIO
- 消息队列：RabbitMQ（异步处理）

**核心接口**：

```
GET    /api/v1/skills               # 技能列表（分页、筛选）
GET    /api/v1/skills/:id            # 技能详情
POST   /api/v1/skills                # 创建技能
PUT    /api/v1/skills/:id            # 更新技能
DELETE /api/v1/skskills/:id          # 删除技能
POST   /api/v1/skills/:id/publish    # 提交发布
POST   /api/v1/skills/:id/unpublish  # 下架技能
GET    /api/v1/skills/search         # 全文搜索
```

**数据模型**：

```typescript
interface Skill {
  id: string;                // UUID
  name: string;               // 技能名称（唯一）
  slug: string;               // URL友好标识
  developerId: string;        // 开发者ID
  categoryId: number;         // 分类ID
  tags: string[];             // 标签
  description: string;        // 详细介绍
  shortDesc: string;           // 简短描述
  icon?: string;              // 图标URL
  screenshots?: string[];      // 截图
  pricingType: 'free' | 'one_time' | 'subscription';
  price?: number;              // 价格（分）
  subscriptionPrice?: number; // 订阅月价
  version: string;             // 当前版本号
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'online' | 'offline';
  stats: {
    views: number;            // 浏览次数
    favorites: number;        // 收藏次数
    uses: number;             // 使用次数
    rating: number;           // 平均评分
    reviews: number;          // 评价数量
  };
  config: SkillConfig;        // 技能配置
  createdAt: Date;
  updatedAt: Date;
  publishedAt?: Date;
}

interface SkillConfig {
  inputSchema: JSONSchema;     // 输入参数定义
  outputSchema: JSONSchema;    // 输出参数定义
  dependencies?: string[];     // 依赖的其他技能
  resources?: {                 // 资源限制
    cpu: string;
    memory: string;
    timeout: number;
  };
}
```

#### 2.2.3 订单服务 (Order Service)

**职责**：订单创建、支付、退款、发票

**技术栈**：

- 框架：Spring Boot 3.x / NestJS
- 事务：Seata 分布式事务
- 消息队列：RocketMQ（可靠消息）

**核心接口**：

```
POST   /api/v1/orders                # 创建订单
GET    /api/v1/orders                # 订单列表
GET    /api/v1/orders/:id            # 订单详情
POST   /api/v1/orders/:id/pay        # 发起支付
POST   /api/v1/orders/:id/cancel     # 取消订单
POST   /api/v1/orders/:id/refund     # 申请退款
GET    /api/v1/orders/:id/invoice    # 获取发票
```

**数据模型**：

```typescript
interface Order {
  id: string;                  // UUID
  orderNo: string;             // 订单号（唯一）
  userId: string;               // 购买用户ID
  skillId: string;              // 技能ID
  developerId: string;          // 开发者ID
  type: 'purchase' | 'subscription' | 'upgrade';
  amount: number;              // 订单金额（分）
  discountAmount: number;      // 优惠金额
  finalAmount: number;         // 实付金额
  status: 'pending' | 'paid' | 'cancelled' | 'refunded';
  paymentMethod?: 'alipay' | 'wechat' | 'card';
  paymentId?: string;          // 支付平台流水号
  paidAt?: Date;
  expireAt: Date;               // 订单过期时间
  refundReason?: string;
  refundedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}
```

#### 2.2.4 支付服务 (Payment Service)

**职责**：聚合支付、退款、对账

**技术栈**：

- 框架：Spring Boot 3.x
- 支付通道：支付宝/微信支付/银行卡

**核心接口**：

```
POST   /api/v1/payments/alipay       # 支付宝支付
POST   /api/v1/payments/wechat       # 微信支付
POST   /api/v1/payments/callback/*   # 支付回调
POST   /api/v1/payments/refund       # 退款申请
GET    /api/v1/payments/reconcile    # 对账查询
```

#### 2.2.5 评论服务 (Review Service)

**职责**：技能评价、评分、回复

**核心接口**：

```
POST   /api/v1/skills/:id/reviews           # 发表评论
GET    /api/v1/skills/:id/reviews           # 评论列表
PUT    /api/v1/reviews/:id                  # 修改评论
DELETE /api/v1/reviews/:id                  # 删除评论
POST   /api/v1/reviews/:id/report           # 举报评论
```

### 2.3 服务间通信

#### 2.3.1 同步通信 (REST/gRPC)

```
┌──────────┐     HTTP/REST     ┌──────────┐
│  网关    │ ◄──────────────► │  服务A   │
└──────────┘                  └──────────┘
                                  │
                            gRPC
                                  │
                             ┌────▼────┐
                             │  服务B   │
                             └──────────┘
```

**通信规范**：

- 内部服务间优先使用 gRPC（高性能）
- 外部接口使用 RESTful API
- 统一使用 Protobuf 定义接口

#### 2.3.2 异步通信 (消息队列)

```
┌──────────┐              ┌──────────────┐              ┌──────────┐
│  服务A   │ ──publish──► │  RabbitMQ    │ ──subscribe─►│  服务B   │
└──────────┘              │  (消息队列)   │              └──────────┘
                           └──────────────┘
                                  │
                                  ▼
                           ┌──────────────┐
                           │  消费者集群   │
                           └──────────────┘
```

**消息场景**：

| 事件 | 消息队列 | 消费者 | 说明 |
|------|----------|--------|------|
| 技能发布 | skill.events | review-service | 触发评分初始化 |
| 订单支付成功 | order.events | notification-service | 发送通知 |
| 技能下架 | skill.events | subscription-service | 处理订阅用户 |
| 开发者提现 | finance.events | payment-service | 处理转账 |

### 2.4 缓存架构

```
┌─────────────────────────────────────────┐
│              应用层缓存                  │
│  Local Cache (Caffeine)                  │
│  • 热数据/配置                           │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│              分布式缓存                  │
│  Redis Cluster (3主3从)                  │
│  • Session                              │
│  • Token                                 │
│  • 接口缓存                              │
│  • 分布式锁                             │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│              数据存储                    │
│  PostgreSQL主从集群                      │
└─────────────────────────────────────────┘
```

**缓存策略**：

| 数据类型 | 缓存策略 | TTL | 更新方式 |
|----------|----------|-----|----------|
| 用户Session | Redis | 24h | 主动删除 |
| 技能详情 | Redis | 5min | 自动过期 |
| 热门技能 | Redis | 1h | 定时更新 |
| 接口响应 | Redis | 1min | 自动过期 |
| 配置信息 | 本地+Redis | - | 配置中心推送 |

### 2.5 异步任务处理

```
┌─────────────────────────────────────────────────────┐
│                    任务触发                          │
│  • 用户操作                                          │
│  • 定时任务                                          │
│  • 消息队列                                          │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              任务队列 (Bull/DelayQueue)              │
│  • 任务分发                                          │
│  • 延迟处理                                          │
│  • 失败重试                                          │
└─────────────────────┬───────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ Worker1 │  │ Worker2 │  │ Worker3 │
    │ (CPU)   │  │ (IO)   │  │ (Cron)  │
    └─────────┘  └─────────┘  └─────────┘
```

**任务类型**：

| 任务类型 | 处理方式 | 示例 |
|----------|----------|------|
| 实时任务 | 同步处理 | API响应、即时支付 |
| 后台任务 | 消息队列 | 邮件发送、通知推送 |
| 定时任务 | CronJob | 数据统计、清理任务 |
| 批处理任务 | 离线任务 | 报表生成、对账处理 |

---

## 3. 前端架构设计

### 3.1 技术选型

| 维度 | 选择 | 说明 |
|------|------|------|
| 框架 | React 18 | 生态完善、性能优秀 |
| 语言 | TypeScript 5 | 类型安全、开发体验 |
| UI库 | Ant Design 5 | 企业级组件库 |
| 状态管理 | Zustand + RTK Query | 轻量级+数据获取 |
| 构建工具 | Vite | 快速启动、热更新 |
| CSS方案 | Tailwind CSS | 原子化CSS |
| 测试 | Vitest + React Testing Library | 单元/集成测试 |

### 3.2 项目结构

```
web/
├── public/
│   ├── favicon.ico
│   └── robots.txt
├── src/
│   ├── assets/                 # 静态资源
│   │   ├── images/
│   │   └── icons/
│   ├── components/             # 通用组件
│   │   ├── common/             # Button/Input/Modal...
│   │   ├── layout/             # Header/Sidebar/Footer...
│   │   └── business/           # 业务组件
│   ├── pages/                  # 页面
│   │   ├── Home/
│   │   ├── Market/
│   │   ├── SkillDetail/
│   │   ├── Developer/
│   │   └── Admin/
│   ├── services/               # API服务
│   │   ├── api/
│   │   │   ├── user.ts
│   │   │   ├── skill.ts
│   │   │   └── order.ts
│   │   └── request.ts         # Axios封装
│   ├── stores/                 # 状态管理
│   │   ├── userStore.ts
│   │   └── uiStore.ts
│   ├── hooks/                  # 自定义Hooks
│   ├── utils/                  # 工具函数
│   ├── types/                  # TypeScript类型
│   ├── router/                 # 路由配置
│   ├── App.tsx
│   └── main.tsx
├── tests/
├── .env.production
├── .env.development
├── vite.config.ts
└── package.json
```

### 3.3 状态管理方案

```typescript
// 用户状态管理 (Zustand)
import { create } from 'zustand';

interface UserState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  login: (user, token) => {
    localStorage.setItem('token', token);
    set({ user, token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },
  updateUser: (partial) => set((state) => ({
    user: state.user ? { ...state.user, ...partial } : null
  })),
}));
```

---

## 4. 后端架构设计

### 4.1 技术选型

| 维度 | 选择 | 说明 |
|------|------|------|
| 核心框架 | Spring Boot 3.x | 成熟稳定 |
| API框架 | Spring MVC / GraphQL | REST + 可选GraphQL |
| ORM | MyBatis-Plus / JPA | 高效CRUD |
| 数据库 | PostgreSQL 15 | 可靠关系型 |
| 缓存 | Redis 7 Cluster | 高性能缓存 |
| 搜索引擎 | Elasticsearch 8 | 全文检索 |
| 消息队列 | RabbitMQ / RocketMQ | 异步通信 |
| 分布式事务 | Seata | 高性能分布式事务 |
| 服务网格 | Istio | 可观测性、安全 |
| 容器编排 | Kubernetes | 自动化运维 |
| 服务注册 | Nacos | 配置中心+注册中心 |

### 4.2 项目结构

```
backend/
├── common/
│   ├── common-core/            # 核心公共模块
│   │   ├── annotation/         # 自定义注解
│   │   ├── config/             # 通用配置
│   │   ├── exception/          # 异常定义
│   │   ├── result/            # 统一响应
│   │   └── util/              # 工具类
│   ├── common-db/             # 数据库公共模块
│   ├── common-redis/          # Redis公共模块
│   └── common-swagger/        # Swagger文档
├── infrastructure/
│   ├── gateway/               # API网关
│   ├── register/              # 服务注册
│   └── config-center/         # 配置中心
├── service/
│   ├── user-service/         # 用户服务
│   │   ├── src/main/java/
│   │   │   ├── controller/
│   │   │   ├── service/
│   │   │   ├── repository/
│   │   │   ├── entity/
│   │   │   ├── dto/
│   │   │   └── UserServiceApplication.java
│   │   └── src/test/
│   ├── skill-service/         # 技能服务
│   ├── order-service/        # 订单服务
│   ├── payment-service/      # 支付服务
│   ├── notification-service/ # 通知服务
│   └── search-service/       # 搜索服务
├── tools/
│   ├── code-generator/        # 代码生成器
│   └── db-migrator/          # 数据库迁移
└── pom.xml
```

### 4.3 API设计规范

#### 4.3.1 RESTful API规范

**URL规范**：

```
# 资源命名
GET     /skills              # 技能列表
GET     /skills/:id          # 技能详情
POST    /skills              # 创建技能
PUT     /skills/:id           # 更新技能
DELETE  /skills/:id           # 删除技能

# 动作命名
POST    /skills/:id/publish   # 发布技能
POST    /skills/:id/favorite  # 收藏技能
POST    /orders/:id/pay       # 支付订单
```

**请求规范**：

```http
POST /api/v1/skills HTTP/1.1
Host: api.skills.com
Content-Type: application/json
Authorization: Bearer <token>
Accept-Language: zh-CN

{
  "name": "智能翻译",
  "categoryId": 5,
  "description": "支持多语言翻译",
  "price": 2900,
  "pricingType": "one_time"
}
```

**响应规范**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "智能翻译",
    "status": "pending",
    "createdAt": "2026-03-29T12:00:00Z"
  },
  "timestamp": 1743254400000,
  "requestId": "req_abc123"
}
```

**错误码规范**：

| 错误码 | 说明 | HTTP状态码 |
|--------|------|------------|
| 0 | 成功 | 200 |
| 10001 | 参数错误 | 400 |
| 10002 | 认证失败 | 401 |
| 10003 | 权限不足 | 403 |
| 10004 | 资源不存在 | 404 |
| 20001 | 业务错误 | 400 |
| 50001 | 系统错误 | 500 |
| 50002 | 服务不可用 | 503 |

---

## 5. 安全架构设计

### 5.1 安全体系

```
┌─────────────────────────────────────────────────────────────────┐
│                        安全防护层                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   WAF       │  │  DDoS防护   │  │  IPS        │             │
│  │  Web应用防火墙 │  │  分布式防护  │  │  入侵防御   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  身份认证    │  │  访问控制    │  │  数据加密   │             │
│  │  JWT/OAuth2 │  │  RBAC/ABAC  │  │  AES-256   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 认证授权流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     认证授权流程                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户 ──► 登录 ──► 验证凭证 ──► 生成Token ──► 返回Token           │
│                    │                     │                       │
│                    ▼                     ▼                       │
│              验证用户名密码         JWT Access Token              │
│              查询用户信息          + Refresh Token                │
│                                         │                        │
│                                         ▼                        │
│  请求 ──► 网关 ──► 验证Token ──► 检查权限 ──► 放行/拒绝           │
│                    │                                            │
│                    ▼                                            │
│              JWT验证                                              │
│              (签名/过期/黑名单)                                   │
│                    │                                            │
│                    ▼                                            │
│              权限校验                                              │
│              (用户角色/资源权限)                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 数据安全策略

| 数据类型 | 存储加密 | 传输加密 | 脱敏展示 |
|----------|----------|----------|----------|
| 用户密码 | bcrypt | - | - |
| 手机号 | AES-256 | TLS 1.3 | 138****8888 |
| 身份证 | AES-256 | TLS 1.3 | 110101****1234 |
| 银行卡 | AES-256 | TLS 1.3 | ****1234 |
| 邮箱 | - | TLS 1.3 | a***@example.com |
| 敏感配置 | AES-256 | - | - |

---

## 6. 可观测性架构

### 6.1 三大支柱

```
┌─────────────────────────────────────────────────────────────────┐
│                       可观测性体系                                │
├───────────────────┬───────────────────┬─────────────────────────┤
│       日志        │        指标        │         链路            │
├───────────────────┼───────────────────┼─────────────────────────┤
│                   │                   │                         │
│  • 结构化日志     │  • RED指标         │  • 分布式追踪           │
│  • ELK Stack      │  • Prometheus      │  • Jaeger               │
│  • 日志聚合分析   │  • Grafana可视化   │  • TraceID串联          │
│  • 异常告警       │  • 性能监控        │  • 慢请求分析           │
│                   │                   │                         │
└───────────────────┴───────────────────┴─────────────────────────┘
```

### 6.2 监控体系

```
┌─────────────────────────────────────────────────────────────────┐
│                      监控告警体系                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    基础设施监控                           │    │
│  │  • CPU/内存/磁盘使用率                                    │    │
│  │  • 网络IO/带宽利用率                                      │    │
│  │  • 容器健康状态                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    应用性能监控                           │    │
│  │  • QPS/TPS                                              │    │
│  │  • 响应时间 (P50/P90/P99)                               │    │
│  │  • 错误率                                               │    │
│  │  • JVM GC/线程池                                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    业务指标监控                           │    │
│  │  • 订单量/交易额                                         │    │
│  │  • 活跃用户数                                            │    │
│  │  • 技能使用量                                            │    │
│  │  • 转化率                                                │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    告警通知渠道                            │    │
│  │  • 短信/电话 (P0)                                        │    │
│  │  • 钉钉/企微 (P1-P2)                                     │    │
│  │  • 邮件 (P3)                                             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. 技术选型总结

### 7.1 技术栈矩阵

| 层级 | 组件 | 选型 | 替代方案 |
|------|------|------|----------|
| 前端框架 | React 18 | TypeScript | Vue 3 |
| UI组件库 | Ant Design 5 | Tailwind CSS | Material UI |
| 移动端 | React Native | Flutter | - |
| 后端框架 | Spring Boot 3 | NestJS | - |
| 数据库 | PostgreSQL 15 | MySQL 8 | - |
| 缓存 | Redis 7 | Memcached | - |
| 搜索引擎 | Elasticsearch 8 | Meilisearch | - |
| 消息队列 | RabbitMQ | RocketMQ | - |
| 对象存储 | OSS | MinIO | - |
| 容器化 | Docker | - | - |
| 编排 | Kubernetes | - | - |
| CI/CD | GitLab CI | Jenkins | - |
| 日志 | ELK Stack | Loki | - |
| 监控 | Prometheus + Grafana | Datadog | - |
| 链路追踪 | Jaeger | Zipkin | - |

### 7.2 成本估算

| 项目 | 规格 | 月成本估算 | 备注 |
|------|------|-----------|------|
| 云服务器 | 4核8G * 5 | ¥3000 | ECS按量付费 |
| 数据库 | 4核16G 100G SSD | ¥2000 | RDS高可用版 |
| 缓存 | 8G Redis Cluster | ¥1500 | Redis内存版 |
| 搜索 | 2核4G 100G | ¥1000 | ES云服务 |
| 对象存储 | 1TB | ¥300 | OSS标准存储 |
| CDN | 100GB/月 | ¥200 | CDN流量包 |
| 消息队列 | 3节点 | ¥800 | RMQ高可用版 |
| 监控服务 | - | ¥500 | 云监控 |
| **合计** | - | **¥9300** | 初期规模 |

---

## 8. 附录

### 8.1 相关文档链接

- [数据库设计文档](./03-数据库设计.md)
- [部署方案文档](./04-部署方案.md)
- [运维方案文档](./05-运维方案.md)
- [API接口文档](./API文档.md)

### 8.2 参考资料

- [Spring Boot官方文档](https://spring.io/projects/spring-boot)
- [React官方文档](https://react.dev)
- [Kubernetes官方文档](https://kubernetes.io/zh/docs)
- [微服务设计模式](https://microservices.io/patterns/index.html)
