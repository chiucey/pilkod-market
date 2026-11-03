---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 69a618b0bfa32652c0f31f7966d2fbf5
    PropagateID: 69a618b0bfa32652c0f31f7966d2fbf5
    ReservedCode1: 3046022100ed728ded758b0001576eb733ea96dbea5a546f381dad734cb8ea6d1cef5d320a022100d18df483327a87f1c858be9dd9725ebb2e77aa82eb8cfc15a3b10bbae3dedd0d
    ReservedCode2: 3044022074279f5b6f9b06c7383804a29ec80200b2f0bb89d288f093a019d4fcff737d20022005707ac42f4c253da79fac7b69b75c4456c31e9fbd1f7953bc632c5b5ad9b1a8
---

# 单份访谈洞察模板

```markdown
# 访谈洞察报告 - [受访者编号]

**受访者信息**
- 编号：{interviewer_id}
- 访谈日期：{interview_date}
- 访谈时长：{interview_duration}
- 置信度：{confidence_level}

---

## 1. 用户目标
> 核心目标是什么？受访者试图达成什么？

### 洞察摘要
{goal_summary}

### 原话摘录
| 摘录 | 页码/位置 | 频次 |
|------|----------|------|
| {quote_1} | {location_1} | {freq_1} |
| {quote_2} | {location_2} | {freq_2} |

---

## 2. 痛点分析
> 遇到了什么阻碍？困难点在哪？

### 洞察摘要
{pain_point_summary}

### 原话摘录
| 摘录 | 页码/位置 | 频次 |
|------|----------|------|
| {quote_1} | {location_1} | {freq_1} |

---

## 3. 行为模式
> 习惯怎么做？典型使用路径？

### 洞察摘要
{behavior_pattern_summary}

### 原话摘录
| 摘录 | 页码/位置 | 频次 |
|------|----------|------|
| {quote_1} | {location_1} | {freq_1} |

---

## 4. 机会点
> 潜在的改进机会或创新点

### 洞察摘要
{opportunity_summary}

### 原话摘录
| 摘录 | 页码/位置 | 频次 |
|------|----------|------|
| {quote_1} | {location_1} | {freq_1} |

---

## 5. 建议动作
> 基于洞察的下一步行动建议

| 优先级 | 建议动作 | 依据洞察 | 预期影响 |
|--------|---------|---------|---------|
| P0 | {action_1} | {source_insight_1} | {expected_impact_1} |
| P1 | {action_2} | {source_insight_2} | {expected_impact_2} |

---

## 6. 知识库融合洞察

### 6.1 知识库相关背景
> 从项目背景、产品策略、历史研究中提取的相关信息

| 背景来源 | 相关内容摘要 | 关联程度 |
|---------|------------|---------|
| {kb_source_1} | {kb_summary_1} | {relevance_1} |

### 6.2 与历史结论一致性/冲突分析

| 对比维度 | 历史结论 | 本次访谈信号 | 关系判断 |
|---------|---------|-------------|---------|
| {dimension_1} | {historical_conclusion_1} | {new_signal_1} | {relationship_1} |

### 6.3 融合后的机会点
> 结合知识库背景后的修正/强化机会点

| 机会点 | 知识库支撑 | 新访谈验证 | 综合评级 |
|--------|----------|-----------|---------|
| {opportunity_1} | {kb_support_1} | {new_validation_1} | {rating_1} |

### 6.4 需要进一步验证的问题
> 基于冲突或空白需要深挖的问题

| 问题 | 冲突来源 | 建议验证方式 |
|------|---------|-------------|
| {question_1} | {conflict_source_1} | {verification_method_1} |

---

**洞察提取完成时间**：{extraction_timestamp}
**研究员**：{researcher_name}
```

---

# 合并综合洞察模板

```markdown
# 用户访谈综合洞察报告

**项目名称**：{project_name}
**访谈数量**：{interview_count} 份
**访谈时间范围**：{date_range}
**综合置信度**：{overall_confidence}

---

## 执行摘要
{executive_summary}

---

## 一、核心洞察汇总

### 1.1 用户目标共识
> 跨访谈的高频目标

| 目标主题 | 出现频次 | 涉及受访者 |
|---------|---------|-----------|
| {goal_1} | {freq_1}/{total} | {respondents_1} |

### 1.2 痛点图谱
> 痛点分布与严重程度

| 痛点 | 出现频次 | 痛苦程度 | 关联目标 |
|------|---------|---------|---------|
| {pain_point_1} | {freq_1}/{total} | {severity_1} | {related_goal_1} |

### 1.3 行为模式矩阵
> 跨用户的行为模式对比

| 行为模式 | 覆盖用户 | 典型场景 |
|---------|---------|---------|
| {pattern_1} | {coverage_1}/{total} | {scenario_1} |

### 1.4 机会点优先级
> 综合评估的机会点排序

| 优先级 | 机会点 | 支撑证据数 | 预估影响 |
|--------|-------|-----------|---------|
| P0 | {opportunity_1} | {evidence_count_1} | {impact_1} |

### 1.5 建议动作路线图
> 建议执行顺序

| 阶段 | 时间 | 建议动作 | 负责方 |
|------|-----|---------|-------|
| NOW | {q1} | {action_1} | {owner_1} |

---

## 二、知识库融合分析

### 2.1 历史洞察回顾
> 知识库中已有的相关洞察

| 历史洞察 | 来源 | 时间 | 适用性 |
|---------|-----|------|-------|
| {historical_insight_1} | {source_1} | {date_1} | {applicability_1} |

### 2.2 新旧信号对比

#### 一致性发现
> 历史结论得到验证

| 结论 | 访谈验证 | 置信度提升 |
|------|---------|-----------|
| {conclusion_1} | {validation_1} | ↑ |

#### 冲突性发现
> 新信号与历史结论不符

| 历史结论 | 新访谈信号 | 差异分析 | 建议处理 |
|---------|-----------|---------|---------|
| {historical_1} | {new_signal_1} | {analysis_1} | {recommendation_1} |

#### 新增发现
> 历史未覆盖的新洞察

| 新发现 | 支撑访谈 | 重要性 |
|--------|---------|--------|
| {new_finding_1} | {source_interview_1} | {importance_1} |

### 2.3 综合机会点
> 融合后形成的最终机会点清单

| 机会点 | 知识库支撑 | 访谈验证强度 | 综合评级 |
|--------|----------|-------------|---------|
| {opportunity_1} | {kb_support_1} | {validation_strength_1} | {rating_1} |

### 2.4 待验证假设
> 需要进一步验证的假设

| 假设 | 来源 | 验证建议 |
|------|-----|---------|
| {hypothesis_1} | {source_1} | {verification_1} |

---

## 三、受访者洞察索引

| 受访者编号 | 核心贡献 | 独特视角 |
|-----------|---------|---------|
| {id_1} | {contribution_1} | {unique_perspective_1} |

---

## 四、附录

### 4.1 输出文档清单
- 单份洞察：{individual_count} 份
- 合并洞察：1 份
- 知识库参考：{kb_reference_count} 份

### 4.2 原始资料链接
- {feishu_links}

**报告生成时间**：{generation_timestamp}
```
