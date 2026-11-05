# 记忆体文件模板

本文档提供各层记忆体文件的模板和示例。

---

## Layer 2: session_notes.md

```markdown
# Session Notes

**Created**: 2026-04-27 20:52:05
**Task ID**: T-042
**Status**: in_progress

## Current Focus
- 重构认证模块 (auth-refactor)

## Progress
- [x] 分析现有认证流程
- [x] 设计新架构
- [ ] 更新单元测试
- [ ] 部署 staging

## Intermediate Results
- 新架构已确定：使用 JWT + Refresh Token
- 数据库迁移脚本已准备

## Active Constraints
- 需要兼容现有 API 端点
- 必须在 5 月 1 日前完成

## Key Variables
- `AUTH_TIMEOUT`: 3600
- `REFRESH_THRESHOLD`: 300

## Blockers
- 待产品确认移动端兼容性需求

## Last Updated
2026-04-27 21:15:00
```

---

## Layer 3: user_preferences.md

```markdown
# User Preferences

**Last Updated**: 2026-04-27 20:52:05

## Code Style
- Code comments: en-US
- Indentation: 4 spaces (not tabs)
- Line length: 100 chars max

## Communication
- Response language: zh-CN (中文回复)
- Detail level: comprehensive (详细解释)
- Tone: professional

## Task Handling
- Prefer short-term tasks before long-term
- Always confirm before destructive actions
- Report progress every 10 minutes for tasks > 30 min

## Project-Specific
- Default project: internal-tools
- Preferred deployment: staging first, then production

## Tags Legend
- `[unconfirmed]` - 未验证
- `[low]` - 低置信度
- `[medium]` - 中置信度
- `[high]` - 高置信度
- `[validated]` - 已验证
- `[stale]` - 长期未引用
```

---

## Layer 3: domain_knowledge.md

```markdown
# Domain Knowledge

**Last Updated**: 2026-04-27 20:52:05

## Authentication
- JWT 最佳实践: [high]
  - Access Token 有效期: 15-60 分钟
  - Refresh Token 有效期: 7-30 天
  - 必须支持 Token 撤销机制

## Database
- PostgreSQL 事务隔离级别: [high]
  - 读已提交 (Read Committed) 为默认
  - 需要可重复读时使用 SELECT FOR UPDATE

## Security
- 密码存储: Argon2 > bcrypt > scrypt > SHA-256 [validated]
- HTTPS 必须用于所有生产环境通信 [validated]
- 敏感数据不记录日志 [high]
```

---

## Layer 4: patterns.md

```markdown
# Success Patterns

## Code Review
- **Pattern**: PR 前先运行本地 linter [validated]
  - 验证次数: 15
  - 节省平均: 10 分钟/次 review 循环

- **Pattern**: 重大重构先写单元测试覆盖 [high]
  - 验证次数: 8
  - 减少回归 bug: 73%

## Debugging
- **Pattern**: 遇到神秘 bug 先检查日志时间戳同步 [high]
  - 验证次数: 5
  - 发现率: 60% 是时间问题导致

## Communication
- **Pattern**: 长任务用 TodoWrite 跟踪进度 [high]
  - 用户满意度: +40%
  - 任务完成率: +25%
```

---

## Layer 4: lessons.md

```markdown
# Failure Lessons

## Docker Deployment
- **Anti-pattern**: 未验证环境变量就 docker-compose up [high]
  - 发生: 2026-04-20
  - 根因: DATABASE_URL 未在 .env 中设置
  - **Correction**: 先跑 `docker-compose config` 验证解析后配置

- **Anti-pattern**: 生产环境直接 docker-compose up -d [medium]
  - 发生: 2026-04-15
  - 根因: 跳过 staging 验证步骤
  - **Correction**: 始终 staging → production 顺序部署

## API Design
- **Anti-pattern**: 返回嵌套过深的 JSON 结构 [medium]
  - 发生: 2026-04-10
  - 根因: 直接映射数据库 schema
  - **Correction**: API response 应扁平化，最多 2 层嵌套

## Error Handling
- **Anti-pattern**: 捕获 Exception 后只打印日志 [medium]
  - 发生: 2026-04-05
  - 根因: 未考虑恢复策略
  - **Correction**: 异常必须转换用户友好的错误 + 监控告警
```

---

## Layer 5: metrics.md

```markdown
# Performance Metrics

**Last Review**: 2026-04-27 20:52:05
**Review Interval**: 每5任务 或 用户明确请求

## Task Metrics
| Metric | Value | Trend |
|--------|-------|-------|
| Task Success Rate | 87% | ↑ +5% |
| Avg Completion Rounds | 3.2 | ↓ -0.8 |
| User Corrections/Session | 1.4 | ↓ -0.3 |

## Memory Metrics
| Metric | Value | Trend |
|--------|-------|-------|
| Memory Hit Rate | 72% | ↑ +12% |
| Pattern Application Rate | 45% | → stable |
| Lesson Anti-pattern Avoidance | 68% | ↑ +8% |

## Self-Improvement Directives
1. **立即应用**: 用户要求代码注释英文，记忆命中率提升
2. **本周改进**: 增加阶段性确认频率，用户满意度目标 90%+
3. **长期优化**: 考虑为高频任务类型建立专门的 pattern 库

## Recent Improvements
- 2026-04-25: 开始使用 TodoWrite 跟踪多步骤任务
- 2026-04-20: 改进了 restart 前的状态保存完整性
```

---

## Episode Case Template

```markdown
# Episode Case: [Brief Title]

**ID**: YYYY-MM-XXX
**Date**: 2026-04-27 20:52:05
**Tags**: [tag1], [tag2], [tag3]

## Context (情境)
[描述事件发生的背景和上下文]

## Action (动作)
[描述当时采取的具体行动]

## Result (结果)
[描述行动的结果：成功/部分成功/失败]

## Root Cause Analysis (根因分析)
[如果失败或部分成功，分析根本原因]

## Pattern Extracted (提取的模式)
[从这次经验中提取的可复用模式]

## Confidence Level
[unconfirmed] / [low] / [medium] / [high] / [validated]

## Verified Count
[被验证次数]
```

---

## Project Context Template

```markdown
# Project: [Project Name]

**Slug**: [project-slug]
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

## Overview
[项目简介]

## Key Decisions
| Date | Decision | Rationale |
|------|----------|-----------|
| YYYY-MM-DD | [决策内容] | [决策理由] |

## Important Findings
[按时间倒序的重要发现]

## Architecture Notes
[架构相关的关键文档链接和说明]

## Active Issues
- [ ] [Issue 1]
- [ ] [Issue 2]
```
