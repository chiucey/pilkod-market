---
name: business-architecture-research
description: Industry Business Architecture Deep Research System. Used when users need in-depth business architecture research for any industry, TOGAF standard modeling, value stream analysis, or business capability mapping. Includes 7 Phases: industry panoramic scan, value stream identification, business domain modeling, process activity decomposition, exception scenario analysis, support coordination system, cross-validation and audit. Supports parallel execution and cross-validation across multiple models.
---

# 行业业务架构深度调研系统

## 核心定位

这是一个**分阶段、模块化**的业务架构调研系统，遵循：
- **TOGAF 9.2/10** 企业架构标准
- **MECE** 原则（互斥且穷尽）
- **先博后渊** 的渐进式深化策略
- **多模型交叉验证** 质量保障

## 使用方式

### 完整调研流程（7个Phase）

```
Phase 1（先博）     Phase 2           Phase 3           Phase 4           Phase 5           Phase 6           Phase 7（交叉验证）
行业全景扫描  →  价值流识别  →  业务域建模  →  流程与活动  →  异常场景  →  支持协同  →  MECE审计
法规标准梳理     阶段步骤分解     能力地图         L4活动分解       异常管理框架                      TOGAF合规检查
                                                                                                  多模型交叉验证
```

### 选择性使用

各Phase可独立使用，根据需要选择：

| 用户意图 | 建议使用 |
|:---|:---|
| 了解行业全貌 | Phase 1 |
| 分析核心业务流程 | Phase 2 |
| 建立能力地图 | Phase 3 |
| 细化到可执行流程 | Phase 4 |
| 识别业务风险点 | Phase 5 |
| 补充后台支撑体系 | Phase 6 |
| 质量审计与验证 | Phase 7 |

## 子Skill索引

| Phase | 子Skill名称 | 触发短语示例 |
|:---:|:---|:---|
| 1 | `phase1-industry-scan` | "行业全景扫描"、"行业背景调研" |
| 2 | `phase2-value-stream` | "价值流分析"、"端到端流程梳理" |
| 3 | `phase3-capability-map` | "业务域建模"、"能力地图构建" |
| 4 | `phase4-process-detail` | "流程细化"、"活动分解" |
| 5 | `phase5-exception-management` | "异常场景"、"风险识别" |
| 6 | `phase6-support-system` | "支持协同"、"后台体系" |
| 7 | `phase7-quality-audit` | "质量审计"、"交叉验证" |

## 输出文件结构

```
📁 {行业名称}业务架构/
├── 00-总览与导航.md
├── 01-行业全景/（Phase 1）
├── 02-价值流体系/（Phase 2）
├── 03-业务域与能力/（Phase 3）
├── 04-流程与活动/（Phase 4）
├── 05-异常管理/（Phase 5）
├── 06-支持协同/（Phase 6）
└── 07-审计报告/（Phase 7）
```

## 使用参数说明

执行时需替换以下参数：

| 占位符 | 说明 | 示例 |
|:---|:---|:---|
| `{行业名称}` | 目标行业名称 | 化工、钢铁、食品加工 |
| `{核心产品}` | 行业核心产出物 | 水泥、钢材、饮料 |
| `{关键工艺}` | 行业核心生产工艺 | 窑烧、轧制、灌装 |

## 推荐执行策略

| Phase | 并行策略 | 交叉验证方式 |
|:---:|:---|:---|
| Phase 1 | Prompt 1.1 + 1.2 可并行 | 对比行业全景认知 |
| Phase 2 | Prompt 2.1 先执行，2.2 依赖2.1 | 价值流识别MECE验证 |
| Phase 3 | Prompt 3.1 依赖Phase 2 | 域划分与价值流对齐 |
| Phase 4 | Prompt 4.1 先执行，4.2 依赖4.1 | 流程-能力映射完整性 |
| Phase 5 | Prompt 5.1 + 5.2 可并行 | 异常覆盖完整性 |
| Phase 6 | Prompt 6.1 依赖Phase 3-5 | 支撑体系覆盖度 |
| Phase 7 | 全部并行执行 | 全局MECE + TOGAF合规 |
