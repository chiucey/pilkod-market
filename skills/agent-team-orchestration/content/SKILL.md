---
name: agent-team-orchestration
description: 'Agent团队编排技能（v4.0.0）：为MaxClaw内的多Agent协作工作提供全流程管理，支持带模型推荐的团队架构设计、智能任务分解与分配、标准化5要素交接协议、带指标仪表板的执行监控、结果整合与审查。内置质量铁律确保强制性审查。适用于科研/办公/创意/软件开发场景。当用户需要Agent团队编排、多Agent协作、任务分解与分配、团队架构设计、协作规则定义、执行监控或结果整合时使用。 / Agent Team Orchestration Skill (v4.0.0): Provides full-process management for multi-Agent collaborative work within MaxClaw, supporting team architecture design with model recommendations, intelligent task decomposition and assignment, standardized 5-element handoff protocol, execution monitoring with metrics dashboard, result integration and review. Incorporates quality iron rules ensuring mandatory reviews. Suitable for scientific research/office/creative/software development scenarios. Use when users require Agent team orchestration, multi-Agent collaboration, task decomposition and assignment, team architecture design, collaboration rules definition, execution monitoring, or result integration.'
---

# Agent团队编排技能 (v4.0.0)
# Agent Team Orchestration Skill (v4.0.0)

## 1. 技能概述 / Skill Overview

Agent团队编排技能v4.0.0是MaxClaw原生系统中的生产级协作管理能力。这个融合版本将全面的功能性与工程卓越性相结合，具有多文件结构、可执行代码、标准化交接协议和铁板质量规则。

Agent Team Orchestration Skill v4.0.0 is a production-grade collaborative management capability within the MaxClaw native system. This fusion version combines comprehensive functionality with engineering excellence, featuring a multi-file structure with executable code, standardized handoff protocols, and iron-clad quality rules.

核心价值主张包括：（1）基于能力智能分配任务的智能编排；（2）确保无缝Agent协作的标准化交接协议；（3）防止质量漂移的铁板质量规则；（4）带可配置KPI仪表板的全面监控；（5）用于快速团队设置的场景模板。

The core value proposition includes: (1) Intelligent orchestration with capability-based task assignment; (2) Standardized handoff protocols ensuring seamless agent collaboration; (3) Iron-clad quality rules preventing quality drift; (4) Comprehensive monitoring with configurable KPI dashboards; (5) Scenario templates for rapid team setup.

## 2. 核心功能模块 / Core Function Modules

### 2.1 团队架构设计 / Team Architecture Design

团队架构设计支持三种组织形式，带有明确的模型推荐：

Team architecture design supports three organizational forms with explicit model recommendations:

| 架构 / Architecture | 最佳场景 / Best For | 主要模型 / Primary Model | 执行模型 / Execution Model |
|--------------|----------|---------------|-----------------|
| **层级式 / Hierarchical** | 清晰工作流、明确汇报关系 | 高推理能力（编排器）/ High-reasoning (Orchestrator) | 成本效益（构建者）/ Cost-effective (Builders) |
| **网格式 / Mesh** | 多角度分析 | 均衡型（所有Agent）/ Balanced (all agents) | 并行执行 / Parallel execution |
| **混合式 / Hybrid** | 复杂项目 | 分层模型混合 / Tiered model mix | 灵活分配 / Flexible allocation |

**带模型建议的角色定义 / Role Definitions with Model Suggestions:**

| 角色 / Role | 核心职责 / Core Responsibilities | 推荐模型 / Recommended Model | 理由 / Rationale |
|------|----------------------|-------------------|-----------|
| **编排器 / Orchestrator** | 任务路由、状态跟踪、优先级决策、结果汇报 | 高推理能力模型 | 负责判断决策 |
| **构建者 / Builder** | 生成产物（代码、文档、配置） | 成本效益模型 | 处理机械性工作 |
| **审查者 / Reviewer** | 质量验证、缺陷反馈、标准对齐 | 高推理能力模型 | 检测盲点 |
| **运维 / Ops** | 定时任务、健康检查、事件分发 | 稳定低成本模型 | 维护活动 |
| **研究者 / Researcher** | 信息收集、初步分析 | 均衡型模型 | 知识检索 |
| **分析师 / Analyst** | 深入分析、洞察提取 | 高推理能力模型 | 模式识别 |

### 2.2 任务生命周期管理 / Task Lifecycle Management

所有任务必须遵循此状态流程。**状态转换仅由编排器控制。**

All tasks must follow this state flow. **State transitions are exclusively controlled by the Orchestrator.**

```
收件箱 → 已分配 → 进行中 → 审查中 → 已完成 | 已失败
Inbox → Assigned → In Progress → Review → Done | Failed
```

**状态转换规则 / State Transition Rules:**

1. **编排器主导 / Orchestrator Mastery**: 绝不允许多Agent独立更新自己的任务状态
2. **完全可追溯 / Full Traceability**: 每个状态变更必须包含注释：谁、何时、什么、为什么
3. **接受失败 / Accept Failure**: `失败`是有效的终态；必须在归档前记录失败原因，不无限重试

### 2.3 标准化交接协议（5要素）/ Standardized Handoff Protocol (5 Elements)

任务在Agent之间转移时，交接消息**必须**包含以下5个要素：

When tasks transfer between agents, the handoff message MUST contain these 5 elements:

| 要素 / Element | 描述 / Description | 示例 / Example |
|---------|-------------|---------|
| **1. 已完成工作 / Completed Work** | 变更/输出的摘要 | "认证模块已构建" |
| **2. 产物位置 / Artifact Location** | 确切的文件路径 | "/shared/artifacts/auth/" |
| **3. 验证方法 / Verification Method** | 测试命令或验收标准 | "运行 `npm test auth`" |
| **4. 已知问题 / Known Issues** | 未完成项或潜在风险 | "尚未实现限流" |
| **5. 下一步行动 / Next Action** | 接收者的明确任务 | "请审查错误处理中的边界情况" |

**交接示例 / Handoff Examples:**

❌ **不良交接 / Bad Handoff**: "完成了，看看文件吧。"

✅ **良好交接 / Good Handoff**: "认证模块已构建于 `/shared/artifacts/auth/`。运行 `npm test auth` 验证。已知问题：限流尚未实现。下一步：请审查错误处理的边界情况。"

### 2.4 智能任务分解与分配 / Intelligent Task Decomposition and Assignment

任务分解使用基于依赖关系的任务图算法：

Task decomposition uses dependency-based task graph algorithm:

- **分解粒度 / Decomposition Granularity**: L1（阶段级）→ L2（步骤级）→ L3（操作级）
- **依赖类型 / Dependency Types**: 串行、并行、条件、循环
- **分配算法 / Assignment Algorithm**: 考虑技能匹配、负载均衡、历史效率

### 2.5 质量铁律 / Quality Iron Rules

这些规则是**不可协商的**。跳过审查会导致在3-5个任务内质量下降。

These rules are **NON-NEGOTIABLE**. Skipping reviews causes quality degradation within 3-5 tasks.

| 规则 / Rule | 描述 / Description | 执行者 / Enforcer |
|------|-------------|----------|
| **构建者审查规格 / Builder Reviews Spec** | 开始前："这可行吗？缺少什么？" | 构建者 |
| **审查者审查构建 / Reviewer Reviews Build** | 对照规格："是否符合？边界情况是否覆盖？" | 审查者 |
| **编排者审查优先级 / Orchestrator Reviews Priority** | 开始前："这是现在最重要的事吗？" | 编排器 |

> **铁律 / IRON RULE**: 每个产物必须经过至少一组非生产者之外的审查。例外情况："小改动"也不行。

### 2.6 协作规则 / Collaboration Rules

- **沟通模式 / Communication Modes**: 实时同步、定时汇报、混合模式
- **冲突解决 / Conflict Resolution**: 优先级判定、投票仲裁、人工干预
- **任务依赖 / Task Dependencies**: 串行、并行、条件、循环

### 2.7 执行监控 / Execution Monitoring

**进度监控 / Progress Monitoring**: 带可视化仪表板的实时任务状态跟踪

**效率监控 / Efficiency Monitoring**: 执行时间对比、吞吐量指标

**异常监控 / Exception Monitoring**: 超时检测、失败告警、结果验证

**可配置KPI仪表板 / Configurable KPI Dashboard:**
- 不同指标类别的可定制组件
- 实时和历史数据视图
- 可导出报告（CSV、PDF、JSON）

**告警系统 / Alerting System:**
- 多级别：信息、警告、严重
- 多渠道：应用内、Webhook
- 告警聚合防止通知疲劳

### 2.8 场景模板库 / Scenario Template Library

用于快速设置预定义的协作模式：

Predefined collaboration patterns for rapid setup:

| 模板 / Template | 角色 / Roles | 用例 / Use Case |
|----------|-------|----------|
| **科研协作 / Scientific Research** | 研究者、分析师、统计学家、作者 | 文献 → 分析 → 论文 |
| **商业分析 / Business Analysis** | 数据收集员、分析师、财务分析师、作者 | 数据 → 市场 → 报告 |
| **内容创作 / Content Creation** | 创意总监、研究者、作者、编辑 | 构思 → 写作 → 发布 |
| **软件开发 / Software Development** | 架构师、开发者、测试员、运维 | 需求 → 构建 → 部署 |

## 3. 快速开始：最小2-Agent设置 / Quick Start: Minimal 2-Agent Setup

1. **定义角色 / Define Roles**:
   - 您（编排器 / Orchestrator）：路由、跟踪、汇报
   - 构建者 / Builder：执行并生成产物

2. **发起任务 / Initiate Task**:
   1. 创建任务记录（文件/数据库/任务板）
   2. 向构建者发送指令，包含：TaskID、描述、输出路径、交接要求
   3. 构建者完成后，您审查、标记状态、汇报

3. **添加审查者（高级）/ Add Reviewer (Advanced)**:
   - 流程：构建者 → 审查者 → 编排器（发布/返工）

## 4. 常见陷阱与预防 / Common Pitfalls and Prevention

| 陷阱 / Pitfall | 预防 / Prevention |
|---------|------------|
| **没有明确的输出路径 / No clear output path** | 生成Agent时始终指定确切的 `/shared/artifacts/` 子路径 |
| **跳过审查步骤 / Skipping review steps** | 永远不要说"这是小改动，不需要审查" |
| **Agent沉默 / Agent silence** | 要求Agent在开始/阻碍/交接/完成时发言 |
| **能力不匹配 / Capability mismatch** | 分配前验证能力 |
| **编排器做工作 / Orchestrator doing work** | 你是指挥者，不是表演者 |

## 5. 何时不使用此框架 / When NOT to Use This Framework

- **单Agent场景 / Single agent scenarios**: 使用常规提示词
- **一次性简单委托 / One-time simple delegation**: 基本对话调用即可
- **简单问答路由 / Simple Q&A routing**: 只需转发给专家

## 6. 执行流程 / Execution Flow

### 6.1 任务启动阶段 / Task Initiation Phase

1. 权限验证 / Permission verification
2. 加载Agent列表和能力档案 / Load agent list and capability profiles
3. 解析任务指令（场景、描述、规模、需求）/ Parse task instructions
4. 生成带推荐架构的启动报告 / Generate initiation report with recommended architecture

### 6.2 任务执行阶段 / Task Execution Phase

1. 从所有Agent收集状态 / Status collection from all agents
2. 异常检测 / Exception detection
3. 基于依赖关系的任务调度 / Task scheduling based on dependencies
4. 结果处理和验证 / Result processing and validation

### 6.3 任务完成阶段 / Task Completion Phase

1. 结果整合 / Result integration
2. 团队审查和分析 / Team review and analysis
3. 资源清理 / Resource cleanup

## 7. 安全机制 / Security Mechanisms

- **数据隔离 / Data Isolation**: 团队级隔离
- **权限控制 / Permission Control**: 管理员、执行者、观察者层级
- **操作可追溯 / Operation Traceability**: 防篡改审计日志
- **异常告警 / Exception Alerts**: 多级别告警
- **资源限制 / Resource Limitations**: 配额管理

## 8. 技术规格 / Technical Specifications

### 8.1 版本信息 / Version Information

**当前版本：4.0.0** - 融合版本，结合了版本A的全面功能性与版本B的工程卓越性。

**Current version: 4.0.0** - Fusion release combining comprehensive functionality with engineering excellence.

**主要增强 / Key Enhancements:**
- 带可执行代码的多文件工程结构
- Multi-file engineering structure with executable code
- 5要素标准化交接协议
- 5-element standardized handoff protocol
- 带强制性审查执行的质量铁律
- Quality iron rules with mandatory review enforcement
- 带模型推荐的增强角色定义
- Enhanced role definitions with model recommendations
- 可配置KPI监控仪表板
- Configurable KPI monitoring dashboards
- 用于快速设置场景模板库
- Scenario template library for rapid setup

### 8.2 文件结构 / File Structure

```
agent-team-orchestration/
├── SKILL.md                    # 主技能文档 / Main skill documentation
├── _meta.json                  # 技能元数据 / Skill metadata
├── src/
│   └── main.py                 # 带编排逻辑的入口点 / Entry point with orchestration logic
├── config/
│   └── settings.yaml           # 配置文件 / Configuration file
├── instructions/
│   └── system_prompt.md        # 编排器角色提示词 / Orchestrator role prompt
├── tests/
│   └── test_main.py            # 单元测试 / Unit tests
├── assets/
│   └── .gitkeep                # 资产目录占位符 / Asset directory placeholder
└── README.md                    # 安装指南 / Installation guide
```

### 8.3 依赖模块 / Dependencies

核心模块：team_architecture、task_decomposition、ability_matching、collaboration_rules、execution_monitor、result_integration、monitoring_metrics、scenario_template

Core modules: team_architecture, task_decomposition, ability_matching, collaboration_rules, execution_monitor, result_integration, monitoring_metrics, scenario_template

### 8.4 性能指标 / Performance Metrics

| 操作 / Operation | 目标 / Target | 最大值 / Maximum |
|-----------|--------|---------|
| 任务启动 / Task initiation | 3秒 / 3s | 5秒 / 5s |
| 最大团队规模 / Max team scale | 20个Agent / 20 Agents | 50个Agent / 50 Agents |
| 任务分解（100个子任务）/ Task decomposition (100 sub-tasks) | 0.8秒 / 0.8s | 1秒 / 1s |
| 能力匹配 / Capability matching | 1.5秒 / 1.5s | 2秒 / 2s |
| 监控延迟 / Monitoring latency | 0.5秒 / 0.5s | 1秒 / 1s |
| 结果整合（1000个子任务）/ Result integration (1000 sub-tasks) | 8秒 / 8s | 10秒 / 10s |
| 模板匹配 / Template matching | 0.5秒 / 0.5s | 1秒 / 1s |
