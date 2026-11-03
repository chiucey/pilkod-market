---
name: phase1-industry-scan
description: Industry panoramic scan and regulatory standards mapping. Used when users need industry-wide scanning, supply chain analysis, competitive landscape research, or regulatory standards review. TOGAF aligned with Phase A (Architecture Vision) and Phase B (Business Architecture) preliminary input.
---

# Phase 1：行业全景扫描

## 核心定位

建立对目标行业的全局认知，识别行业边界、核心价值链、关键参与者。

**TOGAF对齐**：Phase A（架构愿景）、Phase B（业务架构）前期输入

## 执行流程

### Step 1：行业全景认知构建

执行 `phase1-industry-scan/prompt1-1-industry-overview.md` 提示词：

**角色**：20年经验行业战略顾问，精通产业链分析、价值链解构

**输出**：
- 行业定义与边界（GB/T 4754定位）
- 产业链全景图（上中下游）
- 波特价值链分析
- 行业核心特征（8个维度）
- 典型企业画像（3-5家）
- 关键成功因素（5-8个）

### Step 2：标准与法规体系梳理

执行 `phase1-industry-scan/prompt1-2-standards-regulations.md` 提示词：

**角色**：法规与标准研究专家

**输出**：
- 标准体系全景（GB/行业/地方/国际）
- 法规与政策环境
- 准入资质与许可
- 合规风险清单

## 质量约束

- 所有分类必须符合MECE原则
- 数据需标注来源或"行业估算"
- 子行业分类至少3个维度
- 产业链至少覆盖3级

## 交叉验证要点

- [ ] 产业链上中下游价值占比之和≈100%
- [ ] 子行业分类无交叉重叠
- [ ] 关键成功因素覆盖价值链各环节
