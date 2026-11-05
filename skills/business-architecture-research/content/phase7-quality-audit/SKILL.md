---
name: phase7-quality-audit
description: MECE logic audit and TOGAF compliance check. Used when users need quality auditing for business architecture deliverables, cross-validation, or multi-model consistency analysis. TOGAF aligned with Phase F (Migration Planning) and Phase G (Implementation Governance).
---

# Phase 7：交叉验证与质量审计

## 核心定位

对全部产出进行交叉验证、MECE审计和TOGAF合规检查。

**TOGAF对齐**：Phase F（迁移规划）前期 + Phase G（实施治理）

**输入**：Phase 1-6全部产出

**输出**：审计报告 + 差距分析 + 改进建议

## 执行流程

### Step 1：MECE逻辑审计

执行 `phase7-quality-audit/prompt7-1-mece-audit.md` 提示词：

**角色**：严格业务架构审计师

**审计维度**：
- 价值流MECE审计
- 业务域MECE审计
- 流程-能力映射审计
- 活动-流程映射审计
- 异常-活动映射审计
- 支撑-核心映射审计

### Step 2：TOGAF合规性检查

执行 `phase7-quality-audit/prompt7-2-togaf-compliance.md` 提示词：

**角色**：TOGAF 9.2/10认证企业架构师

**检查维度**：
- ADM Phase对齐检查
- BIZBOK指南对齐检查
- 架构原则合规检查
- Top 10改进建议

### Step 3：多模型交叉验证

执行 `phase7-quality-audit/prompt7-3-multi-model-validation.md` 提示词：

**角色**：业务架构评审专家

**验证维度**：
- 价值流一致性对比
- 业务域一致性对比
- 流程详细度一致性对比
- 行业特色准确性对比
- 综合评估与融合建议

## 推荐执行策略

Phase 7的三个Prompt可全部并行执行，同时产出MECE审计、TOGAF合规检查、多模型一致性报告。
