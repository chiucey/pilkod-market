---
name: phase3-capability-map
description: Business domain identification and capability map construction. Used when users need to establish business domain models, build capability maps, or perform business capability mapping. TOGAF aligned with Phase B (Business Architecture) - Business Capability Mapping.
---

# Phase 3：业务域与能力地图构建

## 核心定位

建立业务域模型和能力地图，形成结构化的业务能力清单。

**TOGAF对齐**：Phase B（业务架构）— 业务能力映射（Capability Map）

**输入**：Phase 2价值流目录

**输出**：业务域总览 + 完整能力地图（L3级）

## 执行流程

### Step 1：业务域识别与建模

执行 `phase3-capability-map/prompt3-1-domain-modeling.md` 提示词：

**角色**：TOGAF认证企业架构师（Level 3+），精通业务能力映射

**输出**：
- 业务域总览表（核心/支撑/使能分类）
- 域间协同关系表
- 完整业务能力地图（一级/二级能力）
- 能力-价值流映射矩阵

## 质量约束

- 业务域划分必须MECE（无遗漏、无重叠）
- 每个域的一级能力3-5个，二级能力总计不少于域数量的2倍
- 能力描述必须说明"做什么"（What），不涉及"怎么做"（How）
- 能力-价值流映射矩阵中，每条价值流至少被3个域支撑

## 交叉验证要点

- [ ] 业务域覆盖价值流所有参与方
- [ ] 能力地图与价值流阶段形成完整映射
- [ ] 域