---
name: phase4-process-detail
description: Business process directory construction and L4 activity decomposition. Used when users need to convert business capabilities into executable processes or perform activity detailing. TOGAF aligned with Phase B (Business Architecture) - Process Architecture.
---

# Phase 4：业务流程目录与活动分解

## 核心定位

将业务能力落地为可执行的业务流程和活动。

**TOGAF对齐**：Phase B（业务架构）— 流程架构 + Phase C（信息系统架构）输入

**输入**：Phase 3业务域与能力地图

**输出**：流程目录（L2级）+ 活动分解（L4级）

## 执行流程

### Step 1：业务流程目录构建

执行 `phase4-process-detail/prompt4-1-process-directory.md` 提示词：

**角色**：业务流程设计专家

**输出**：
- 流程分层架构说明
- 流程目录总览（统计维度）
- 各域流程目录

### Step 2：业务活动分解（L4级）

执行 `phase4-process-detail/prompt4-2-activity-decomposition.md` 提示词：

**角色**：业务流程细化专家

**输出**：
- L3子流程分解
- L4业务活动（完整15字段）

## 质量约束

- 每个域的L2流程数量5-12条
- 流程编号规则：BP-{域缩写}-{序号}
- 每条L2流程分解为5-15个L4活动
- 活动粒度：一个活动是一个人可独立完成的操作单元

## 交叉验证要点

- [ ] 每个二级能力至少对应1条L2流程
- [ ] 活动间的输入/输出形成完整链路
- [ ] 业务规则覆盖行业标准和法规要求
