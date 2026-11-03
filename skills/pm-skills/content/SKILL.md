---
name: pm-skills
description: 全面的产品经理技能库，包含6大模块21个子技能，将经典PM方法论转化为AI可调用的工作流系统。包含产品发现、产品策略、产品执行、市场研究、数据分析和增长营销六大模块的AI工作流。当用户需要产品发现、策略规划、需求文档编写、用户研究、竞品分析、数据分析、增长分析、或任何PM日常工作场景时使用。具体如下：（1）创意发现：创意构思、假设测试、机会解决方案树、用户访谈、持续发现...（2）战略规划：产品战略画布、商业模式画布、定价策略、竞争分析、愿景定义...（3）执行落地：PRD 撰写、OKR 规划、产品路线图、冲刺计划、优先级排序...（4）市场分析：用户画像、市场细分、竞品分析、市场规模估算...（5）数据分析：SQL 查询生成、队列分析、A/B 测试分析、指标定义...（6）GTM 增长：GTM 策略、增长循环、竞争战卡、上市计划...（7）营销增长：营销创意、定位策略、北极星指标、增长实验...（8）辅助工具：简历审阅、法律文档检查、语法检查... 来自产品管理专家 Paweł Huryn。
---

# PM Skills - 产品经理技能库

系统性的产品经理方法论工作流集合，将经典的产品管理框架转化为可执行的 AI 协作流程。

## 技能库结构

```
pm-skills/
├── 产品发现 (Product Discovery)
│   ├── opportunity-solution-tree   机会解决方案树
│   ├── interview-script            客户访谈脚本
│   ├── brainstorm-ideas-new       新产品头脑风暴
│   ├── identify-assumptions-new    假设识别
│   ├── metrics-dashboard           指标仪表板
│   ├── prioritize-features         功能优先级
│   └── summarize-interview         访谈总结
│
├── 产品策略 (Product Strategy)
│   ├── product-strategy            产品策略画布
│   ├── swot-analysis              SWOT分析
│   ├── business-model             商业模式画布
│   ├── lean-canvas                精益画布
│   ├── value-proposition           价值主张
│   └── pestle-analysis            PESTLE分析
│
├── 产品执行 (Product Execution)
│   ├── create-prd                 产品需求文档
│   ├── user-stories               用户故事
│   ├── brainstorm-okrs            OKRs规划
│   └── sprint-plan                Sprint计划
│
├── 市场研究 (Market Research)
│   ├── competitor-analysis         竞品分析
│   └── user-personas              用户画像
│
├── 数据分析 (Data Analytics)
│   └── sentiment-analysis          情感分析
│
└── 增长营销 (Marketing Growth)
    └── aarrr-metrics              AARRR海盗指标
```

---

## 模块一：产品发现 (Product Discovery)

### 机会解决方案树 (opportunity-solution-tree)

**触发场景**: 进行产品发现、结构化探索性问题、映射需求到解决方案

**核心价值**:
- 将期望结果反向映射到机会和解决方案
- 识别验证实验
- 优先排序探索方向

**使用指南**:
```
1. 定义期望的北极星指标和目标值
2. 探索机会领域 (功能型/情感型/社会型)
3. 针对每个机会头脑风暴解决方案
4. 为高优先级方案设计验证实验
5. 迭代 OST 直到找到清晰的路径
```

---

### 客户访谈脚本 (interview-script)

**触发场景**: 准备用户访谈、进行客户研究、设计访谈大纲

**核心价值**:
- 结构化的 JTBD 访谈框架
- 深入的动机探询技巧
- 完整的访谈记录模板

**使用指南**:
```
1. 热身阶段 (5分钟): 建立信任
2. 背景探索 (10分钟): 了解工作场景
3. JTBD 深挖 (20分钟): 功能/情感/社会需求
4. 未来状态探索 (10分钟): 理想解决方案
5. 收尾确认 (5分钟): 总结和后续
```

---

### 新产品头脑风暴 (brainstorm-ideas-new)

**触发场景**: 构思新产品创意、激发产品灵感、跨职能视角思考

**核心价值**:
- 三视角创意生成 (PM/Designer/Engineer)
- 创意组合策略
- ICE/RICE 快速评估

**使用指南**:
```
1. PM视角: 关注价值、市场、商业
2. Designer视角: 关注体验、情感、交互
3. Engineer视角: 关注可行性、创新、扩展
4. 发散-收敛循环
5. 使用 ICE/RICE 快速排序
```

---

### 假设识别 (identify-assumptions-new)

**触发场景**: 风险识别、产品假设分析、精益验证

**核心价值**:
- 8大风险类别全覆盖
- 假设验证矩阵
- 精益实验设计

**8大风险类别**:
| 类别 | 描述 |
|-----|------|
| 价值风险 | 用户是否真正需要 |
| 可用性风险 | 用户能否轻松使用 |
| 可行性风险 | 能否构建 |
| 商业化风险 | 能否带来商业价值 |
| 市场吸引力 | 市场是否足够大 |
| 竞争优势 | 能否在竞争中胜出 |
| 团队风险 | 团队能否执行 |
| GTM风险 | 能否有效触达用户 |

---

### 指标仪表板 (metrics-dashboard)

**触发场景**: 设计产品指标体系、建立数据看板、定义成功指标

**核心价值**:
- 四层指标体系 (北极星→结果→输入→健康)
- 告警机制设计
- 仪表板模板

**指标层级**:
```
北极星指标 (North Star)
    ↓
结果指标 (Outcome Metrics)
    ↓
输入指标 (Input Metrics)
    ↓
健康指标 (Health Metrics)
```

---

### 功能优先级 (prioritize-features)

**触发场景**: 功能优先级排序、Backlog整理、资源分配决策

**核心价值**:
- 多种优先级框架
- 评估矩阵模板
- 决策会议指南

**框架选择指南**:
| 场景 | 推荐框架 |
|-----|---------|
| 快速决策 | ICE |
| 资源规划 | RICE |
| 范围定义 | MoSCoW |
| 满意度优化 | Kano |
| 敏捷团队 | WSJF |

---

### 访谈总结 (summarize-interview)

**触发场景**: 总结访谈、提取洞察、生成研究报告

**核心价值**:
- JTBD 结构化提取
- 满意度信号识别
- 洞察提炼方法论

---

## 模块二：产品策略 (Product Strategy)

### 产品策略画布 (product-strategy)

**触发场景**: 制定产品战略、创建策略画布、规划产品方向

**核心价值**:
- 9段式全面战略框架
- 从愿景到防御性
- 权衡取舍决策

**9个组成部分**:
| 组件 | 核心问题 |
|-----|---------|
| 愿景 | 我们要成为什么？ |
| 目标用户 | 服务谁？ |
| 价值主张 | 创造什么价值？ |
| 成本 | 需要投入什么？ |
| 增长 | 如何获取用户？ |
| 能力 | 具备什么能力？ |
| 指标 | 如何衡量成功？ |
| 权衡 | 愿意放弃什么？ |
| 防御性 | 如何保护优势？ |

---

### SWOT 分析 (swot-analysis)

**触发场景**: 战略分析、竞争分析、企业诊断

**核心价值**:
- 内外部环境分析
- TOWS 策略矩阵
- 可行动建议生成

**TOWS 策略**:
| 组合 | 策略类型 |
|-----|---------|
| S + O | SO策略 (最大化) |
| W + O | WO策略 (改善) |
| S + T | ST策略 (防御) |
| W + T | WT策略 (最小化) |

---

### 商业模式画布 (business-model)

**触发场景**: 构建商业模式、分析企业价值链

**核心价值**:
- Alexander Osterwalder 九模块
- 端到端商业逻辑
- 收入成本结构分析

**九大模块**:
```
客户细分 | 价值主张 | 渠道通路 | 客户关系 | 收入来源
                    ↓
关键活动 | 关键资源 | 关键合作伙伴
                    ↓
              成本结构
```

---

### 精益画布 (lean-canvas)

**触发场景**: 创业计划、商业模式草稿、快速验证

**核心价值**:
- 问题驱动的商业模式
- 假设验证导向
- 精益启动适配

**九大模块**:
```
问题 | 解决方案 | 关键指标 | UVP | 不公平优势
                    ↓
客户细分 | 渠道 | 成本结构 | 收入来源
```

---

### 价值主张 (value-proposition)

**触发场景**: 设计价值主张、创建JTBD价值主张、定义用户价值

**核心价值**:
- 6部分 JTBD 框架
- Who/Why/How/前后对比
- 替代方案分析

**6部分结构**:
| 部分 | 描述 |
|-----|------|
| WHO | 目标用户 |
| WHY | 动机 |
| HOW | 如何使用 |
| WHAT BEFORE | 行动前状态 |
| WHAT AFTER | 行动后状态 |
| ALTERNATIVES | 替代方案 |

---

### PESTLE 分析 (pestle-analysis)

**触发场景**: 宏观环境分析、市场趋势研究、外部环境扫描

**核心价值**:
- 六大外部因素全覆盖
- 跨维度交互分析
- 战略建议生成

**六大因素**:
| 因素 | 关注点 |
|-----|-------|
| Political | 政府、政策、法规 |
| Economic | 经济、利率、汇率 |
| Social | 人口、生活方式、文化 |
| Technological | 技术、创新、数字化 |
| Legal | 法律、合规、知识产权 |
| Environmental | 环境、可持续性 |

---

## 模块三：产品执行 (Product Execution)

### 产品需求文档 (create-prd)

**触发场景**: 编写PRD、创建产品规格、设计产品需求

**核心价值**:
- 8部分完整 PRD 模板
- 验收标准设计
- 发布计划模板

**PRD 八部分**:
1. 文档概述
2. 产品背景
3. 产品目标
4. 市场与用户
5. 价值主张
6. 解决方案
7. 发布计划
8. 附录

---

### 用户故事 (user-stories)

**触发场景**: 编写用户故事、创建Backlog、设计验收标准

**核心价值**:
- 3C's + INVEST 原则
- 分层结构 (Epic→Feature→Story)
- 故事拆分方法

**INVEST 原则**:
| 字母 | 含义 |
|-----|------|
| I | Independent (独立) |
| N | Negotiable (可协商) |
| V | Valuable (有价值) |
| E | Estimable (可估算) |
| S | Small (小) |
| T | Testable (可测试) |

---

### OKRs 规划 (brainstorm-okrs)

**触发场景**: 制定OKRs、设定目标、设计关键结果

**核心价值**:
- OKRs 创建流程
- 对齐框架
- 追踪机制

**OKRs 结构**:
```
目标 (Objective) - 定性的鼓舞人心的陈述
    ↓
关键结果 (Key Results) - 定量的可衡量的指标
    ↓
 Initiatives (关键举措) - 达成KR的具体行动
```

---

### Sprint 计划 (sprint-plan)

**触发场景**: 规划Sprint、Sprint计划会议、迭代规划

**核心价值**:
- 5步规划流程
- 容量估算方法
- 风险识别矩阵

**规划流程**:
```
确定Sprint目标 → 评估团队容量 → 选择待办项 → 识别依赖 → 风险评估
```

---

## 模块四：市场研究 (Market Research)

### 竞品分析 (competitor-analysis)

**触发场景**: 竞品分析、竞争对手研究、竞争策略制定

**核心价值**:
- 多维度竞品对比
- SWOT 竞争分析
- 差异化机会识别

**分析维度**:
| 维度 | 内容 |
|-----|------|
| 产品 | 功能对比、价格对比 |
| 市场 | 份额、用户群、定位 |
| 商业模式 | 收入、获客、留存 |
| 优劣势 | 优势来源、用户投诉 |

---

### 用户画像 (user-personas)

**触发场景**: 创建用户画像、用户研究、用户细分

**核心价值**:
- 定性+定量画像结合
- Goals/Pains/Behaviors 框架
- 画像维护指南

**画像结构**:
```
人口统计 → 心理特征 → Goals → Pain Points → Behaviors
    ↓
使用场景 → 决策流程 → 挫折时刻 → 沟通偏好
```

---

## 模块五：数据分析 (Data Analytics)

### 情感分析 (sentiment-analysis)

**触发场景**: 反馈分析、满意度分析、NPS研究

**核心价值**:
- 多来源反馈整合
- 情感量化指标
- 用户细分洞察

**分析框架**:
```
数据收集 → 情感分类 → 主题聚类 → 洞察提炼 → 建议生成
```

---

## 模块六：增长营销 (Marketing Growth)

### AARRR 海盗指标 (aarrr-metrics)

**触发场景**: 增长分析、用户漏斗分析、增长策略制定

**核心价值**:
- 五阶段增长漏斗
- 各阶段核心指标
- 优化优先级矩阵

**AARRR 框架**:
| 阶段 | 核心问题 | 关键指标 |
|-----|---------|---------|
| Acquisition | 如何获取用户？ | CAC、CTR、CVR |
| Activation | 用户是否激活？ | Aha时刻率 |
| Retention | 用户是否留存？ | D7/D30留存 |
| Referral | 用户是否推荐？ | NPS、K因子 |
| Revenue | 如何变现？ | ARPU、LTV |

---

## 使用建议

### 按场景选择技能

| 场景 | 推荐技能 |
|-----|---------|
| 新产品探索 | opportunity-solution-tree + brainstorm-ideas-new + identify-assumptions-new |
| 用户研究 | interview-script + user-personas + summarize-interview |
| 战略规划 | product-strategy + swot-analysis + business-model |
| 商业模式 | lean-canvas + value-proposition + business-model |
| 需求管理 | create-prd + user-stories + prioritize-features |
| 团队对齐 | brainstorm-okrs + sprint-plan |
| 市场分析 | pestle-analysis + competitor-analysis |
| 增长优化 | aarrr-metrics + sentiment-analysis + metrics-dashboard |

### 技能组合工作流

**产品发现到上线完整流程**:
```
1. 发现: opportunity-solution-tree
2. 研究: interview-script + user-personas
3. 验证: identify-assumptions-new + brainstorm-ideas-new
4. 策略: product-strategy + value-proposition
5. 执行: create-prd + user-stories + sprint-plan
6. 衡量: metrics-dashboard + aarrr-metrics
```

---

## 参考资料

详细的技能使用指南、模板和示例请参阅 `references/` 目录：

- `references/product-discovery/` - 产品发现详细指南
- `references/product-strategy/` - 产品策略详细指南
- `references/product-execution/` - 产品执行详细指南
- `references/market-research/` - 市场研究详细指南
- `references/data-analytics/` - 数据分析详细指南
- `references/marketing-growth/` - 增长营销详细指南
