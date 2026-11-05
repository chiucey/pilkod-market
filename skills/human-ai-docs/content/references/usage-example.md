# Human-AI-Docs 使用示例

> **文档版本**: 1.0.0
> **场景**: 首次初始化项目文档

---

## 对话记录

### 用户触发

```
用户: 梳理项目
```

### AI 分析项目

```
AI: 检测项目结构...

发现:
- Node.js 项目 (package.json)
- 项目名称: MyWebApp
- 目录结构: src/, components/, api/, utils/
- 已有文件: README.md, package.json

请描述项目的主要功能：
1. 这是什么类型的项目？
2. 主要使用的技术栈？
3. 核心模块有哪些？
```

### 用户描述

```
用户:
- 这是一个 Vue3 + Node.js 的 Web 管理后台
- 技术栈: Vue3, Vite, Element Plus, Express, PostgreSQL
- 核心模块: 用户管理、权限控制、数据看板
- 主要工作流: CRUD + 图表展示
```

### AI 生成文档

```
AI: 正在生成文档...

✅ 创建目录结构:
   docs/

✅ 生成核心文档:
   README.md
   CLAUDE.md
   docs/architecture.md
   docs/tech-stack.md
   docs/workflows.md
   docs/api.md

✅ 初始化状态日志:
   .ai-docs/doc-state.log.md

完成! 生成摘要:
- README.md: 约 150 行
- CLAUDE.md: 约 80 行 (<100 ✅)
- docs/: 4 个技术文档
```

---

## 生成的文件结构

```
MyWebApp/
├── README.md                    # 人类用户指南
├── CLAUDE.md                    # AI 上下文（80 行）
├── docs/
│   ├── architecture.md          # 架构设计
│   ├── tech-stack.md           # 技术栈
│   ├── workflows.md            # 工作流
│   └── api.md                  # API 文档
└── .ai-docs/
    └── doc-state.log.md        # 状态日志
```

---

## 生成的 README.md 示例

```markdown
# MyWebApp 管理后台

> 基于 Vue3 + Node.js 的企业级管理后台

## 快速开始

### 环境要求
- Node.js 18+
- PostgreSQL 14+
- pnpm 8+

### 安装

```bash
# 克隆项目
git clone https://github.com/xxx/mywebapp.git
cd mywebapp

# 安装依赖
pnpm install

# 配置环境
cp .env.example .env
# 编辑 .env 配置数据库

# 启动开发服务器
pnpm dev
```

### 技术栈

- **前端**: Vue 3 + Vite + Element Plus
- **后端**: Express + PostgreSQL
- **工具**: TypeScript, ESLint, Prettier

## 主要功能

1. **用户管理**: CRUD + 角色权限
2. **数据看板**: ECharts 图表展示
3. **系统设置**: 配置管理

## 开发指南

详见 [开发指南](docs/workflows.md)

## API 文档

详见 [API 文档](docs/api.md)
```

---

## 生成的 CLAUDE.md 示例

```markdown
# MyWebApp AI Context

> **Version**: 1.0.0 | **Platform**: Claude Code

---

## 项目概览

- **类型**: Vue3 + Node.js Web 管理后台
- **前端**: Vue 3, Vite, Element Plus, ECharts
- **后端**: Express, PostgreSQL, Prisma

---

## 操作索引表

| 操作指令 | 详细文档 | 触发词 |
|----------|----------|--------|
| 添加新页面 | @docs/workflows.md#new-page | "添加页面", "new page" |
| 添加API | @docs/workflows.md#new-api | "添加接口", "new API" |
| 运行测试 | @docs/testing.md | "测试", "run tests" |
| 部署应用 | @docs/deployment.md | "部署", "deploy" |

---

## 项目结构

```
src/
├── components/     # Vue 组件
├── views/          # 页面视图
├── api/            # API 调用
├── stores/         # 状态管理
└── utils/          # 工具函数

server/
├── routes/         # 路由
├── controllers/    # 控制器
├── models/         # 数据模型
└── middleware/     # 中间件
```

---

## 常用命令

```bash
# 前端开发
pnpm dev          # 启动开发服务器
pnpm build        # 构建生产版本

# 后端开发
pnpm server:dev   # 启动后端服务
pnpm server:build  # 构建后端

# 测试
pnpm test         # 运行所有测试
```

---

## 技术栈

@docs/tech-stack.md

---

## 架构设计

@docs/architecture.md
```

---

## 增量更新示例

### 用户触发

```
用户: 更新工程文档
```

### AI 检查状态

```
AI: 检查文档状态...

上次更新: 2026-03-20
当前时间: 2026-03-27

请描述自上次更新以来的变更：
1. 新增了哪些功能/模块？
2. 修改了哪些现有逻辑？
3. 有哪些废弃内容？
```

### 用户描述

```
用户: 添加了文件上传功能，修改了用户模块的接口
```

### AI 分析并更新

```
AI: 分析变更影响...

需要更新的文档:
1. 新增: docs/upload.md (文件上传)
2. 更新: docs/api.md (用户接口变更)
3. 更新: CLAUDE.md (操作索引表)

确认更新? [Y/n]
```

### 更新后

```
✅ 更新完成

变更摘要:
- 新增: docs/upload.md
- 更新: docs/api.md
- 更新: CLAUDE.md
- 记录: .ai-docs/doc-state.log.md
```

---

## 验证步骤

### 1. 检查文件

```bash
ls -la README.md CLAUDE.md docs/
```

### 2. 验证 CLAUDE.md 行数

```bash
wc -l CLAUDE.md
# 预期: <100 行
```

### 3. 测试 @import

```bash
# 在 Claude Code 中
@import docs/architecture.md
```

---

## 常见问题

### Q: 如何添加新的操作到索引表？

**A**: 编辑 CLAUDE.md，在操作索引表中添加新行：

```markdown
| 新操作 | @docs/new-doc.md | "触发词" |
```

### Q: README 和 CLAUDE.md 有什么区别？

**A**:
- README.md: 面向人类，自然语言，侧重快速上手
- CLAUDE.md: 面向AI，结构化，任务导向，@import引用

### Q: docs/ 目录应该包含哪些文件？

**A**: 根据项目需求，一般包括：
- architecture.md (架构设计)
- workflows.md (开发工作流)
- tech-stack.md (技术栈)
- api.md (API文档)
- testing.md (测试指南)

---
