---
name: unified-strategy-framework
description: 统一策略框架技能。当用户需要系统化解决复杂问题、管理多技能协作、构建因果推理流程时触发。适用于任务编排、技能组合、流程标准化、自动化执行等场景。
---

# 统一策略框架

整合技能库，建立标准化、可复用、可扩展的因果推理与自动化任务执行系统。

## 核心架构

```
┌─────────────────────────────────────────┐
│          应用层 (Application)            │
│  日常任务 | 项目管理 | 代码开发 | 运维   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      编排层 (Orchestration)              │
│  规范驱动工作流 | 任务拆解与调度 | 质量门禁│
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      技能层 (Skills)                     │
│  代码开发 | 文档同步 | 测试验证 | 部署运维│
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      连接层 (MCP)                        │
│  项目管理 | 代码仓库 | 本地服务 | 记忆存储│
└─────────────────────────────────────────┘
```

## 四大策略模式

### 1. 链式调用 (Chain Pattern)

**适用**：顺序依赖的多步骤任务

```
Step1: 技能A (修改代码)
  ↓
Step2: 技能B (更新文档)
  ↓
Step3: 技能C (生成测试)
  ↓
Step4: 技能D (验证并报告)
```

**示例**：数据迁移流程
- uuid-refactoring-skill
- doc-sync-skill
- test-generation-skill
- verify-and-report-skill

### 2. 并行执行 (Parallel Pattern)

**适用**：独立子任务可同时执行

```
├─ 技能A (测试模块A)
├─ 技能B (测试模块B)  (同时执行)
├─ 技能C (测试模块C)
└─ 汇总技能 (收集结果)
```

### 3. 条件分支 (Conditional Pattern)

**适用**：根据情况选择不同路径

```
IF env == "development":
  → deploy-to-local-skill
ELSE IF env == "staging":
  → deploy-to-cloudbase-skill
ELSE IF env == "production":
  → deploy-with-rollback-skill
```

### 4. 观察者模式 (Observer Pattern)

**适用**：持续监控和响应

```
Monitor-Skill (定时检查):
  - check_cpu_usage()
  - check_memory_usage()
  - check_error_rate()

ON threshold_exceeded:
  → alert-skill (发送告警)
  → auto-scale-skill (自动扩容)
```

## 因果推理流程

```
用户请求
  ↓
[意图识别]
  ├─ 代码开发 → 调用编排层 → 生成任务列表 → 分派技能
  ├─ 问题排查 → 搜索记忆 → 匹配历史案例 → 执行解决方案
  ├─ 数据分析 → 调用MCP → 查询数据 → 生成报告
  └─ 部署运维 → 检查环境 → 选择策略 → 执行部署
```

### 推理规则库

#### 文档同步规则
```javascript
{
  trigger: "code_change",
  condition: "file_path matches /(core|routes|middleware)/",
  actions: [
    {type: "search", target: "*.md"},
    {type: "update", target: "README.md"},
    {type: "notify", recipient: "author"}
  ]
}
```

#### 测试覆盖规则
```javascript
{
  trigger: "new_feature",
  condition: "PR merged to main",
  actions: [
    {type: "generate_tests", coverage_target: "80%"},
    {type: "run_tests", suite: "integration"},
    {type: "block_merge", if: "tests_fail"}
  ]
}
```

## 决策树

```
任务输入
  ↓
意图识别 → 代码开发?
  ├─ YES → 规范驱动 → 技能组合 → 执行验证
  │
问题排查?
  ├─ YES → 记忆搜索 → 案例匹配 → 方案执行
  │
数据分析?
  ├─ YES → MCP调用 → 数据查询 → 报告生成
  │
部署运维?
  └─ YES → 环境检查 → 策略选择 → 部署执行
```

## 策略选择矩阵

| 任务特征 | 推荐模式 | 示例 |
|---------|---------|------|
| 多步骤、强依赖 | 链式调用 | 数据迁移、版本升级 |
| 独立子任务 | 并行执行 | 批量测试、分布式部署 |
| 环境差异大 | 条件分支 | 多环境部署、灰度发布 |
| 实时监控 | 观察者模式 | 系统监控、自动告警 |
| 复杂决策 | 混合模式 | 故障自愈、智能调度 |

## 质量标准

### 技能质量要求
- [ ] SKILL.md 格式合规
- [ ] 脚本无语法错误
- [ ] 测试覆盖率 > 80%
- [ ] 文档完整性检查

### 技能审查流程
```
新技能提交 → 自动化检查 → 人工审查 → 灰度测试 → 正式发布
```

## 核心价值

| 对象 | 价值 |
|------|------|
| 个人 | 减少重复劳动，聚焦高价值工作 |
| 团队 | 知识沉淀，技能复用，标准化交付 |
| 组织 | 提效降本，风险可控，创新驱动 |

## 禁止行为

- 不临时拼凑技能组合
- 不跳过质量门禁
- 不重复已解决的同类问题
- 不丢失执行上下文
