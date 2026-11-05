---
name: phase5-exception-management
description: Comprehensive business exception scenario coverage and exception management framework. Used when users need to identify business risks, sort out exception scenarios, or establish exception handling mechanisms. TOGAF aligned with Phase B (Business Architecture) - Risk and Compliance Framework.
---

# Phase 5：业务异常场景全覆盖

## 核心定位

系统梳理业务异常场景，建立异常分级标准和处理机制。

**TOGAF对齐**：Phase B（业务架构）— 风险与合规框架

**输入**：Phase 4业务流程与活动分解

**输出**：异常管理框架 + 异常场景大全

## 执行流程

### Step 1：业务异常管理框架

执行 `phase5-exception-management/prompt5-1-exception-framework.md` 提示词：

**角色**：运营风险管理专家

**输出**：
- 异常分级标准（P0/P1/P2/P3）
- 异常管理组织与职责
- 异常处理通用流程（5步法）
- 异常分类体系
- 统计与分析模板

### Step 2：业务异常场景大全

执行 `phase5-exception-management/prompt5-2-exception-scenarios.md` 提示词：

**角色**：资深运营专家

**输出**：
- 每个业务域的异常场景大全
- 每个场景的完整字段（10字段）

## 质量约束

- 异常分级必须与业务影响程度直接挂钩
- 每个业务域至少识别5个异常场景
- P0级异常必须有应急方案
- 处理流程必须形成闭环

## 交叉验证要点

- [ ] 异常场景覆盖所有业务活动的异常分支
- [ ] 触发条件可被现有系统或人工检测
- [ ] 预防措施覆盖根因消除
