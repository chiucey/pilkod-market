---
name: fullstack-developer
description: Full-stack development expert skill. Use when users request building complete web applications, designing interfaces, developing frontend/backend features, integrating databases, implementing APIs, or solving full-stack development issues. Trigger phrases include creating websites, developing applications, building systems, full-stack development, frontend/backend development, web design, API development, database design.
---

# 全栈开发专家

## 核心能力

### 1. 前端开发
- **框架选择**：React, Vue.js, Angular, Svelte, Next.js, Nuxt.js
- **样式方案**：Tailwind CSS, CSS Modules, Styled-Components, Sass/Less
- **动画交互**：Framer Motion, GSAP, CSS Animations, Three.js/WebGL
- **响应式设计**：移动优先、Flexbox/Grid、媒体查询、跨浏览器兼容

### 2. 后端开发
- **运行时**：Node.js, Deno, Bun
- **框架**：Express.js, NestJS, Fastify, Koa, Django, Flask, Spring Boot, Laravel
- **API设计**：RESTful, GraphQL, gRPC, WebSocket
- **认证授权**：JWT, OAuth2, Session, SSO

### 3. 数据库
- **关系型**：PostgreSQL, MySQL, MariaDB, SQLite
- **非关系型**：MongoDB, Redis, Cassandra, DynamoDB
- **ORM/ODM**：Prisma, TypeORM, Sequelize, Mongoose
- **缓存策略**：Redis缓存、CDN、浏览器缓存

### 4. DevOps与部署
- **容器化**：Docker, Kubernetes
- **CI/CD**：GitHub Actions, GitLab CI, Jenkins
- **云服务**：Vercel, Netlify, AWS, Azure, GCP
- **监控**：Prometheus, Grafana, ELK Stack

## 开发工作流

### 阶段1：需求分析与架构设计
```
1. 明确功能需求和用户体验目标
2. 选择技术栈（考虑团队能力、项目规模、维护成本）
3. 设计数据库架构和API接口
4. 制定项目结构和代码规范
```

### 阶段2：项目初始化
```bash
# React + TypeScript + Vite
npm create vite@latest project-name -- --template react-ts

# Vue + TypeScript + Vite
npm create vite@latest project-name -- --template vue-ts

# Next.js
npx create-next-app@latest project-name
```

### 阶段3：开发与最佳实践
- 组件设计：原子化设计、可复用、单一职责
- 状态管理：React Context, Redux Toolkit, Zustand, Pinia
- 类型安全：TypeScript strict模式、Zod验证
- 代码质量：ESLint, Prettier, Husky, lint-staged

### 阶段4：测试策略
- 单元测试：Jest, Vitest, Mocha
- 组件测试：React Testing Library, Vue Test Utils
- E2E测试：Playwright, Cypress, Selenium
- 覆盖率：≥80%关键路径

### 阶段5：性能优化
- 前端优化：代码分割、懒加载、Tree Shaking、图片优化
- 后端优化：数据库索引、查询优化、缓存策略
- 网络优化：CDN、Gzip压缩、HTTP/2、预加载
- Core Web Vitals：LCP < 2.5s, FID < 100ms, CLS < 0.1

## UI/UX设计原则

### 视觉设计
1. **简洁性**：去除不必要的元素，突出核心内容
2. **一致性**：统一的色彩、字体、间距、交互模式
3. **层次感**：通过大小、颜色、对比度建立视觉层次
4. **留白**：合理使用空白，提升可读性和呼吸感

### 色彩系统
```
主色（Primary）：品牌色，用于主要按钮、链接、强调
次色（Secondary）：辅助色，用于次要元素
中性色（Neutral）：文字、背景、边框
功能色（Semantic）：成功绿、警告黄、错误红、信息蓝
```

### 交互动效
- **过渡**：0.2-0.3s ease-out 用于颜色、大小变化
- **入场动画**：fade-in + slide-up，营造自然感
- **反馈动画**：点击缩放、hover高亮、loading状态
- **页面切换**：优雅的路由过渡动画

## 代码规范

### 目录结构（推荐）
```
src/
├── components/       # 可复用组件
│   ├── ui/          # 基础UI组件（Button, Input, Card）
│   └── features/    # 业务功能组件
├── pages/           # 页面组件
├── hooks/           # 自定义Hooks
├── utils/           # 工具函数
├── services/        # API服务层
├── stores/          # 状态管理
├── types/           # TypeScript类型定义
└── styles/          # 全局样式
```

### Git提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

## 部署流程

### 前端部署
```bash
# 构建生产版本
npm run build

# 部署到 Vercel
npx vercel --prod

# 部署到 Netlify
netlify deploy --prod
```

### 后端部署
```bash
# Docker镜像构建
docker build -t app-name .

# Docker Compose启动
docker-compose up -d
```

## 质量检查清单

### 功能完整性
- [ ] 所有功能点已实现并可正常使用
- [ ] 表单验证完整（必填、格式、边界）
- [ ] 错误处理友好（错误提示、重试机制）
- [ ] 加载状态清晰（骨架屏、loading动画）

### 视觉质量
- [ ] 设计稿还原度高（像素级对比）
- [ ] 响应式布局无问题（桌面/平板/手机）
- [ ] 动画流畅无卡顿（60fps）
- [ ] 字体渲染清晰（抗锯齿、字重选择）

### 性能指标
- [ ] 首屏加载时间 < 3s
- [ ] Lighthouse评分 > 90
- [ ] 无重大内存泄漏
- [ ] 图片已优化压缩

### 代码质量
- [ ] 无console.error/warning
- [ ] TypeScript类型完整
- [ ] 单元测试覆盖核心逻辑
- [ ] 代码审查通过

## 常见问题解决

### 前端问题
| 问题 | 解决方案 |
|------|----------|
| 组件重渲染 | useMemo/useCallback/React.memo |
| 内存泄漏 | 清理副作用、取消订阅、移除事件监听 |
| 跨域问题 | CORS配置、代理服务器、JSONP |
| SEO问题 | SSR/SSG、meta标签、结构化数据 |

### 后端问题
| 问题 | 解决方案 |
|------|----------|
| 数据库连接池耗尽 | 连接池配置、连接复用、超时设置 |
| API响应慢 | 索引优化、缓存、异步处理 |
| 并发问题 | 分布式锁、乐观锁、队列削峰 |
| 安全漏洞 | 输入验证、SQL注入防护、XSS防护 |

### 部署问题
| 问题 | 解决方案 |
|------|----------|
| 构建失败 | 检查依赖版本、环境变量、Node版本 |
| 运行时错误 | 查看日志、添加监控、回滚版本 |
| 性能下降 | Profiling分析、CDN加速、缓存优化 |

## 技能使用指南

### 触发条件
当用户请求以下内容时激活此技能：
- 创建完整的Web应用或网站
- 开发前端界面或后端服务
- 设计数据库架构
- 实现API接口
- 解决全栈开发中的技术问题
- 优化应用性能
- 配置部署流程

### 输出要求
1. 提供完整的、可运行的代码
2. 包含必要的注释和文档
3. 遵循行业最佳实践
4. 确保代码质量和可维护性
5. 包含部署和测试说明
