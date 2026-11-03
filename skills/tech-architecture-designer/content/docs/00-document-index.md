---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 93f4ec05d885ddddba4ebe94b089fdce
    PropagateID: 93f4ec05d885ddddba4ebe94b089fdce
    ReservedCode1: 3045022100c04a1e2a3a9fb7a21d1bb6d881eda653d5735d1e1808f8ec982f087eb5f14e3d02207a652bd303e3561f1df47cb63c248260ddc0619fabe774219504e1d9bd38088d
    ReservedCode2: 3046022100e16ae6920c2a21e211dfaf4bbf9fb2e8530d4f6767f4b000b51e9815b824e6ba022100b1278fedef8f94c2cf399a02302d30fef3a1f58139cc36100ce44449ca72981b
---

# Agent Skills 平台技术文档总览

> 本文档为 Agent Skills 平台完整技术方案索引，涵盖产品需求、技术架构、数据库设计、部署方案和运维方案。

---

## 文档结构

```
Agent Skills 平台技术文档
│
├── 00-document-index.md              ← 当前文件
├── 01-prd-product-requirements.md    ← 产品需求文档
├── 02-technical-architecture.md     ← 技术架构设计
├── 03-database-design.md            ← 数据库设计
├── 04-deployment-plan.md            ← 部署方案
└── 05-operations-plan.md            ← 运维方案
```

---

## 文档内容摘要

### 01-PRD产品需求文档

**核心内容**：

- 产品愿景：打造全球领先的 AI Agent 技能市场
- 目标用户：技能开发者、技能使用者、企业用户
- 功能模块：用户系统、技能市场、技能发布、交易支付、开发者工具、社区支持、平台管理
- 非功能需求：性能、安全、兼容性、可用性

**关键章节**：

| 章节 | 页码 | 内容 |
|------|------|------|
| 产品概述 | P3-6 | 愿景、定位、价值主张 |
| 用户分析 | P7-15 | 用户画像、场景、旅程地图 |
| 功能需求 | P16-48 | 功能模块清单、优先级 |
| 非功能需求 | P49-55 | 性能、安全、兼容性指标 |
| 验收标准 | P63-68 | 功能验收、质量指标、里程碑 |

### 02-技术架构设计

**核心内容**：

- 云原生微服务架构设计
- 前端技术栈：React 18 + TypeScript + Ant Design
- 后端技术栈：Spring Boot 3.x + PostgreSQL
- 服务划分：用户服务、技能服务、订单服务、支付服务等
- 安全架构：WAF、身份认证、权限控制、数据加密

**关键架构图**：

```
客户端层 → 网关层 → 服务层 → 数据层
```

| 章节 | 页码 | 内容 |
|------|------|------|
| 架构设计原则 | P3-5 | 高可用、可扩展、可观测、安全 |
| 系统架构设计 | P6-35 | 微服务划分、通信机制、缓存策略 |
| 前端架构设计 | P36-42 | 技术选型、项目结构、状态管理 |
| 后端架构设计 | P43-55 | 项目结构、API规范 |
| 安全架构设计 | P56-62 | 认证授权、数据安全 |
| 可观测性架构 | P63-70 | 日志、指标、链路追踪 |

### 03-数据库设计

**核心内容**：

- 数据库选型：PostgreSQL + Redis + Elasticsearch + MongoDB
- 表结构设计：用户表、技能表、订单表、支付表、审计日志表
- 索引设计：优化查询性能
- 缓存设计：Redis 缓存策略
- 高可用设计：读写分离、备份策略

**核心表结构**：

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| users | 用户基础信息 | id, email, phone, password_hash, role |
| skills | 技能基础信息 | id, name, slug, developer_id, category_id, price |
| categories | 技能分类 | id, name, slug, parent_id |
| orders | 订单表 | id, order_no, user_id, skill_id, amount, status |
| reviews | 技能评价 | id, skill_id, user_id, rating, content |
| subscriptions | 订阅表 | id, user_id, skill_id, status, start_at, end_at |
| payments | 支付记录 | id, payment_no, order_id, channel, amount |
| developer_earnings | 开发者收益 | id, developer_id, amount, commission |
| operation_logs | 操作日志 | id, user_id, operation, module, ip |

### 04-部署方案

**核心内容**：

- Kubernetes 集群设计
- 服务部署配置（Deployment、Service、HPA）
- CI/CD 流水线设计（GitLab CI）
- 数据库高可用部署
- 监控日志组件部署

**关键配置**：

| 组件 | 配置 | 说明 |
|------|------|------|
| K8s集群 | 3节点系统池 + 6节点应用池 | 高可用部署 |
| Ingress | Nginx + SSL卸载 | 统一入口 |
| CI/CD | GitLab CI + ArgoCD | 自动化部署 |
| 数据库 | Patroni + PostgreSQL | 主从高可用 |

### 05-运维方案

**核心内容**：

- 监控体系：基础设施、应用层、业务层监控
- 告警管理：AlertManager 规则、通知渠道
- 日志管理：收集、存储、查询
- 备份恢复：备份策略、恢复流程
- 安全管理：密钥管理、安全扫描
- 故障管理：处理流程、报告模板
- SLA承诺：可用性、响应时间、补偿机制

**关键指标**：

| 指标类型 | 目标值 | 说明 |
|----------|--------|------|
| 系统可用性 | ≥ 99.9% | 年度可用性 |
| API响应时间 | P99 ≤ 500ms | 99%请求 |
| 故障恢复时间 | MTTR ≤ 30分钟 | 平均恢复时间 |
| 备份成功率 | 100% | 每日全量备份 |
| 安全事件 | 0 发生 | 年度安全目标 |

---

## 技术栈总结

| 层级 | 技术选型 |
|------|----------|
| **前端** | React 18, TypeScript, Ant Design, Vite |
| **后端** | Spring Boot 3.x, MyBatis-Plus, JWT |
| **数据库** | PostgreSQL 15, Redis 7, Elasticsearch 8 |
| **消息队列** | RabbitMQ, RocketMQ |
| **容器** | Docker, Kubernetes |
| **监控** | Prometheus, Grafana, Loki, Jaeger |
| **安全** | Vault, WAF, SSL/TLS |
| **CI/CD** | GitLab CI, ArgoCD |
| **日志** | ELK Stack, Loki |

---

## 快速导航

### 需求阶段

- 查看产品愿景 → [PRD产品需求文档 - 产品概述](./01-PRD产品需求文档.md#1-产品概述)
- 查看功能清单 → [PRD产品需求文档 - 功能需求](./01-PRD产品需求文档.md#3-功能需求)
- 查看验收标准 → [PRD产品需求文档 - 验收标准](./01-PRD产品需求文档.md#6-验收标准)

### 设计阶段

- 查看架构设计 → [技术架构设计 - 系统架构设计](./02-技术架构设计.md#2-系统架构设计)
- 查看数据库设计 → [数据库设计 - 表结构](./03-数据库设计.md#2-postgresql-数据库设计)
- 查看部署架构 → [部署方案 - 部署架构总览](./04-部署方案.md#1-部署架构总览)

### 实施阶段

- 查看服务配置 → [部署方案 - 服务部署配置](./04-部署方案.md#3-服务部署配置)
- 查看CI/CD流程 → [部署方案 - CICD流水线设计](./04-部署方案.md#5-cicd-流水线设计)
- 查看监控告警 → [运维方案 - 监控体系](./05-运维方案.md#2-监控体系)

### 运维阶段

- 查看告警规则 → [运维方案 - 告警管理](./05-运维方案.md#3-告警管理)
- 查看备份恢复 → [运维方案 - 备份与恢复](./05-运维方案.md#5-备份与恢复)
- 查看SLA承诺 → [运维方案 - SLA承诺](./05-运维方案.md#10-sla-承诺)

---

## 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| V1.0 | 2026-03-29 | 技术架构团队 | 初始版本，包含完整技术方案 |

---

## 联系方式

| 角色 | 职责 | 联系方式 |
|------|------|----------|
| 技术架构负责人 | 架构设计咨询 | architecture@skills-platform.com |
| 数据库负责人 | 数据库设计咨询 | dba@skills-platform.com |
| 运维负责人 | 部署运维咨询 | ops@skills-platform.com |

---

**最后更新**：2026-03-29
