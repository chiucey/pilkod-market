---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8cb8a0e49a02fad4356683a710a38f6c
    PropagateID: 8cb8a0e49a02fad4356683a710a38f6c
    ReservedCode1: 3046022100aabb23c32e7ddb8e7409db39f791d08243e74b936d33e69c5bd9284f90c17052022100ee827c31e5c2bc423beae6e8031d16ee11621f8563c09bf5515047bc3f5beeb5
    ReservedCode2: 3045022100c53f7bf51485b3a5f5432508216da03cd868a2bab3f769b63637ffd6a52cea01022040dbcd9243b6da6471ed196583eab9b28a954738412c1d079cd05f41c0aedf19
description: SKILL Self-Evolution System - Transforms scattered Skills into intelligent composite Skills with a self-evolution loop. Use when analyzing Skills usage patterns, creating composite Skills, building automated workflows, or establishing a skill evolution system.
name: skill-evolution-system
---

# SKILL自进化系统

## 系统概述

本系统将250+个独立SKILL转化为智能组合Skills，通过持续学习形成自我进化闭环。

## 核心架构：三层进化体系

### 第一层：技能盘点与环境感知

**执行流程：**

1. **扫描已安装SKILL目录**
   ```bash
   ls -la /workspace/.minimax/skills/
   ```

2. **统计类别分布**
   - 信息处理类 (42个): brave-search, autoresearch, deep-research...
   - 内容创作类 (38个): content-creation, writing, business-writing...
   - 开发工程类 (65个): code, code-generator, python...
   - 数据分析类 (28个): analyst, data-analyst, chart-image...
   - 自动化工作流类 (35个): automation-workflows, workflow-builder...
   - 商业策略类 (22个): business-strategy, market-research...
   - 安全合规类 (15个): security-auditor, detect-injection...
   - 平台集成类 (50+个): notion, github, vercel-deploy...

3. **识别最近活跃SKILL**
   - 检查对话历史中的Skill调用频率
   - 标记高活跃度Skills

### 第二层：使用模式智能分析

**频率矩阵分析：**

| 操作类型 | 频率 | 典型组合 | 对应SKILL链 |
|---------|------|---------|------------|
| 搜索-摘要 | ⭐⭐⭐⭐⭐ | 热点搜索→内容摘要→关键提取 | brave-search → summarize → cognitive-memory |
| 研究-报告 | ⭐⭐⭐⭐⭐ | 深度研究→结构化输出→存档 | deep-research → writing → obsidian |
| 代码-测试 | ⭐⭐⭐⭐⭐ | 代码生成→审查→测试 | code → code-review → backend-testing |
| 数据-可视化 | ⭐⭐⭐⭐ | 数据分析→图表生成→展示 | analyst → chart-image → presentation |
| 营销-分发 | ⭐⭐⭐⭐ | 内容创作→SEO优化→多平台发布 | content-creation → seo → social-media |
| 知识-积累 | ⭐⭐⭐⭐⭐ | 信息收集→整理归档→检索优化 | brave-search → cognitive-memory → context-optimizer |

### 第三层：复合Skills生成引擎

**核心公式：**
```
复合Skill = Σ(高频单点Skill × 权重系数) + 智能编排层 + 进化反馈机制
```

**智能组合示例：**

## 复合Skill #1: auto-intelligence (智能情报中心)

**描述：** 全自动热点发现 → 深度研究 → 智能摘要 → 知识沉淀

**组件技能：**
- trigger: 热点猎人-topic_miner (触发层)
- search: brave-search / autoresearch (搜索层)
- analysis: pattern-detection / research-engine (分析层)
- synthesis: deep-research-pro / in-depth-research (研究层)
- output: summarize / writing-assistant (输出层)
- storage: cognitive-memory / obsidian (存储层)
- notification: feishu-multi-agent-messaging (通知层)

**执行流程：**
1. [触发] 监控热点话题变化
2. [搜索] 多源并行信息抓取
3. [分析] 模式识别与关键信息提取
4. [研究] 深度分析与交叉验证
5. [输出] 结构化摘要生成
6. [存储] 知识图谱自动更新
7. [通知] 相关方实时推送

## 复合Skill #2: code-factory (智能代码工厂)

**描述：** 需求解析 → 代码生成 → 智能审查 → 自动化测试 → 部署上线

**组件技能：**
- parse: ai-tool-compliance (需求解析)
- generate: code-generator / python (代码生成)
- review: code-reviewer-cn / ai-code-review (代码审查)
- test: backend-testing / debugging (测试调试)
- deploy: vercel-deploy / github (部署发布)
- monitor: monitoring-observability / log-analysis (监控维护)

**执行流程：**
1. [解析] 理解需求并拆解任务
2. [生成] 遵循最佳实践编写代码
3. [审查] 自动检测安全漏洞和性能问题
4. [测试] 单元测试 + 集成测试全覆盖
5. [部署] 自动化CI/CD流水线
6. [监控] 实时追踪运行状态

## 复合Skill #3: insight-miner (商业洞察挖掘机)

**描述：** 市场研究 → 竞品分析 → 趋势预测 → 策略建议

**组件技能：**
- research: market-research-agent / market-research
- analyze: business-strategy / data-analyst-pro
- predict: pattern-detection / deep-research
- report: business-writing / presentation-builder
- alert: finance-news / social-media-agent

**执行流程：**
1. [研究] 全网市场数据采集
2. [分析] 竞品对比与差异识别
3. [预测] 趋势建模与预测
4. [报告] 可执行策略生成
5. [预警] 异常情况实时告警

## 复合Skill #4: growth-engine (增长引擎驱动)

**描述：** 内容生产 → SEO优化 → 社媒分发 → 效果追踪 → 迭代优化

**组件技能：**
- create: content-creation / marketing-drafter
- optimize: seo / humanizer
- distribute: social-media-agent / slack
- track: analytics / pattern-detection
- iterate: self-improving-agent / context-optimizer

## 复合Skill #5: security-shield (安全护盾)

**描述：** 预防 → 检测 → 响应 → 修复全链路安全

**组件技能：**
- prevent: security-best-practices / guardrails
- detect: detect-injection / ai-tool-compliance
- audit: security-auditor / legal-compliance
- respond: notification-system / automation-workflows
- fix: debugging / automation-tools

## 第四层：自我进化闭环机制

### 进化触发条件

| 触发类型 | 触发条件 | 进化动作 |
|---------|---------|---------|
| 质量驱动 | 任务完成度 < 85% | 分析失败原因，更新执行策略 |
| 效率驱动 | 执行时间 > 预期 150% | 优化流程路径，引入缓存 |
| 反馈驱动 | 用户评分 < 4/5 | 记录反馈，改进输出格式 |
| 模式驱动 | 连续3次相似任务 | 提取通用模式，固化流程 |
| 新技能驱动 | 检测到新SKILL安装 | 评估整合可能性 |

### 进化评估矩阵

每次复合Skill执行后，自动评估：

```
┌─────────────────────────────────────────────────────────┐
│                    进化评估报告                          │
├─────────────────────────────────────────────────────────┤
│  时间维度: 执行耗时、响应延迟、吞吐量                     │
│  质量维度: 准确率、完整率、一致性                         │
│  覆盖维度: 边界处理、异常恢复、特殊情况                    │
│  效率维度: 资源消耗、并行度、复用率                       │
│  用户维度: 满意度、修正次数、改进建议                     │
└─────────────────────────────────────────────────────────┘
```

**评分规则：**
- 综合评分 < 80%: 触发自我优化
- 综合评分 < 60%: 触发深度重构
- 综合评分 > 95%: 固化最佳实践

### 进化知识库结构

```markdown
## 进化记录 [Skill名称] v1.x.x

### 本次进化
- 触发原因: [质量/效率/反馈/模式]
- 问题诊断: [根本原因分析]
- 优化方案: [具体改进措施]
- 影响评估: [对其他Skill的潜在影响]

### 最佳实践
- 成功模式: [已固化的有效策略]
- 失败教训: [已规避的错误模式]
- 参数调优: [最优配置参数]

### 进化历史
- v1.0.0: 初始版本
- v1.1.0: [优化项]
- v1.2.0: [优化项]
```

## 执行启动协议

### 第一步：环境扫描

```
1. 扫描已安装SKILL目录: /workspace/.minimax/skills/
2. 统计类别分布
3. 识别最近活跃SKILL
```

### 第二步：模式挖掘

```
1. 分析最近对话历史
2. 识别重复操作序列
3. 计算操作频率矩阵
```

### 第三步：候选生成

```
1. 基于高频模式生成复合Skill候选
2. 评估组件Skill的可组合性
3. 计算预期效率提升
```

### 第四步：用户确认

```
1. 展示候选复合Skill设计
2. 征求用户调整意见
3. 确认后执行创建
```

### 第五步：执行与进化

```
1. 执行复合Skill任务
2. 收集执行数据
3. 评估并触发进化（如需要）
4. 更新进化知识库
```

## 终极目标

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│     250+ 散装Skills ──→ N 个复合Skills × 自我进化           │
│                                                            │
│     = 精而细 + 持续进化 + 标准化 + 智能化编排                │
│                                                            │
│     进化公式:                                              │
│     Skill(t+1) = Skill(t) + Δ质量 + Δ效率 + Δ智能化         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## 使用方法

### 快速启动
当用户要求以下操作时自动触发：
- "分析我的Skills使用模式"
- "创建复合Skill"
- "优化我的工作流"
- "建立技能进化体系"
- "扫描已安装的Skills"

### 自定义启动
直接调用本Skill并指定目标：
1. 环境扫描模式
2. 模式分析模式
3. 复合Skill生成模式
4. 进化评估模式
5. 完整执行模式

## 文件结构

```
skill-evolution-system/
├── SKILL.md                    # 主技能文件
├── _meta.json                  # 元数据
├── references/
│   ├── skill-categories.md     # SKILL分类参考
│   ├── evolution-template.md   # 进化记录模板
│   └── composite-examples.md   # 复合Skill示例
└── scripts/
    ├── pattern_analyzer.py     # 模式分析脚本
    ├── skill_generator.py      # Skill生成器
    └── evolution_tracker.py    # 进化追踪器
```
