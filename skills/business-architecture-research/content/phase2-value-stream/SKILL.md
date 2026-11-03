---
name: phase2-value-stream
description: Value stream identification and modeling. Used when users need value stream analysis, end-to-end process mapping, or value chain decomposition. TOGAF aligned with Phase B (Business Architecture) - Value Stream Mapping.
---

# Phase 2：价值流识别与建模

## 核心定位

识别行业核心价值流，建立端到端的价值流模型。

**TOGAF对齐**：Phase B（业务架构）— 价值流映射（Value Stream Mapping）

**输入**：Phase 1行业全景报告

**输出**：价值流目录（L2级）+ 价值流间依赖关系

## 执行流程

### Step 1：价值流识别与定义

执行 `phase2-value-stream/prompt2-1-value-stream-identification.md` 提示词：

**角色**：TOGAF认证业务架构师（Level 3+），擅长价值流分析和业务能力映射

**输出**：
- 价值流总览表（核心/支撑/使能分类）
- 价值流分类汇总
- 价值流间依赖关系矩阵
- 每条价值流的详细定义（起点/终点事件、约束、风险）

### Step 2：价值流阶段与步骤分解

执行 `phase2-value-stream/prompt2-2-stage-decomposition.md` 提示词：

**角色**：资深行业业务流程专家

**输出**：
- 每条价值流的阶段分解（4-7个阶段）
- 每个步骤的完整字段（12字段）

## 质量约束

- 核心价值流数量建议5-8条
- 每条价值流必须有明确起点/终点事件
- 价值流间依赖关系必须形成DAG（有向无环图）
- 每条价值流分解为4-7个阶段，每个阶段3-8个步骤

## 交叉验证要点

- [ ] 价值流覆盖行业价值链全部环节
- [ ] 核心价值流构成完整客户价值交付闭环
- [ ] 依赖关系矩阵无循环依赖
