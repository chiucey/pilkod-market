---
name: university-meeting-minutes
description: 高校会议记录七节点智能工作流系统。当用户需要处理高校会议记录、生成会议纪要、提取待办事项或审查会议内容风险时使用。支持ASR转写/OCR识别/手写整理稿输入，经文本清洗、事实归档、母版生成、独立校验、任务标准化、派生生成、风险审查与政治规范审查全流程处理。
---

# 高校会议记录智能工作流系统

## 任务目标

将高校会议原始记录经七节点+独立校验层流水线，产出结构化、可追溯、风险可控的会议纪要体系。

## 架构概览

### 七节点+独立校验层流程

```
RAW → [L1] → [L2] → [L3_DRAFT] → [VERIFY_PASS] → L3_CONFIRMED
                          ↑              ↓                       ↓
                          └── L3_REVISION ←┘                      ↓
                          ↑                                        ↓
                          └──────────────────────────────────────────┘
                                       (need_revision=true)
```

### 状态机阶段

STAGE_L1_CLEAN → STAGE_L2_FACT → STAGE_L3_DRAFT → STAGE_VERIFY_PASS → STAGE_L3_REVISION(如需) → STAGE_L3_CONFIRMED → STAGE_TASK_NORMALIZE → STAGE_DERIVED → STAGE_RISK_GUARD(可选) → STAGE_POLICY_REVIEW(可选) → STAGE_ARCHIVED

### 四条核心原则

1. **真实性优先于简洁性**：宁可保留冗余事实，不可为精简而丢失信息
2. **可追溯性优先于可读性**：每条结论必须有source_refs支撑
3. **稳定性优先于华丽表达**：已确认内容不因措辞优化而改变实质
4. **风险保留优先于宣传化**：风险信息不得为宣传效果而弱化或删除

## 前置准备

- 读取 [references/general-rules.md](references/general-rules.md) 了解系统总体规则与约束
- 确认用户已提供会议原始记录文本
- 所有节点输出遵循双输出协议：MACHINE_RESULT(机器可解析JSON) + CONTENT_MARKDOWN(人类可读正文)

## 操作步骤

### 步骤1：文本清洗与会议识别（L1）

- 读取 [references/node1-text-cleaning.md](references/node1-text-cleaning.md) 获取完整节点规格
- 执行L1处理：文本清洗、ASR/OCR修复、元信息提取、state_fields生成、term_dictionary建立、complexity_score计算
- 完成后向用户展示结果摘要，并提供以下选项

> **请选择下一步操作：**
> 1. 继续进入节点2（时序事实归档）
> 2. 修订当前L1输出（补充信息或修正识别结果）
> 3. 终止流程

### 步骤2：时序事实归档（L2）

- 读取 [references/node2-fact-archive.md](references/node2-fact-archive.md) 获取完整节点规格
- 执行L2处理：建立事实时间轴、L2编号、议题锚点表、coverage_index、正式任务候选记录
- 完成后向用户展示结果摘要，并提供以下选项

> **请选择下一步操作：**
> 1. 继续进入节点3（议题归类母版生成）
> 2. 修订当前L2输出（补充事实或修正时序）
> 3. 终止流程

### 步骤3：议题归类母版生成（L3_DRAFT）

- 读取 [references/node3-topic-master.md](references/node3-topic-master.md) 获取完整节点规格
- 执行L3_DRAFT处理：生成结构化母版、议题归类、建立locked_sections
- L3_DRAFT完成后必须进入VERIFY_PASS，向用户提示

> **L3草稿已生成。按系统规则，必须进入VERIFY_PASS（覆盖完整性与漂移校验）进行质量校验。**
> 请选择：
> 1. 进入VERIFY_PASS校验（推荐，系统强制要求）
> 2. 查看L3草稿详情后再决定

### 步骤3.5：覆盖完整性与漂移校验（VERIFY_PASS）

- 读取 [references/verify-pass.md](references/verify-pass.md) 获取完整校验规格
- VERIFY_PASS为独立质量控制层，只审查不修改
- 校验强度由complexity_score和risk_level决定：普通校验（complexity_score<4且无高风险）或强化校验
- 检查10类项目：议题覆盖/风险覆盖/任务覆盖/争议覆盖/未决事项/source_refs/术语漂移/决议表述越界/locked_sections非法修改/修订漂移
- 根据校验结果向用户提示

### 步骤3.5b：L3修订（STAGE_L3_REVISION）

- 当VERIFY_PASS返回need_revision=true时进入
- 根据revision_patch进行增量修订（默认）或全量重建（需用户明确要求）
- 修订后必须重新进入VERIFY_PASS校验
- revision_count>=3且VERIFY_PASS仍未通过 → 进入MANUAL_REVIEW_REQUIRED

> **修订次数已达上限（>=3次），VERIFY_PASS仍未通过。系统建议进入人工复核。**
> 请选择：
> 1. 进入人工复核（MANUAL_REVIEW_REQUIRED）
> 2. 强制确认当前版本（需明确确认风险）

### 步骤4：任务标准化（TASK_NORMALIZER）

- 前置条件：L3已确认（STAGE_L3_CONFIRMED），VERIFY_PASS已通过
- 读取 [references/node4-task-normalizer.md](references/node4-task-normalizer.md) 获取完整规格
- 执行任务提取：三要素识别（明确责任主体+执行动作+执行意图），缺一不得列入正式任务表

> **请选择下一步操作：**
> 1. 继续进入节点5（派生版本生成）
> 2. 修订当前任务提取结果
> 3. 终止流程（仅完成任务提取）

### 步骤5：派生版本生成（DERIVED）

- 读取 [references/node5-derived-generation.md](references/node5-derived-generation.md) 获取完整规格
- 执行结构映射与版本派生，7种派生类型：正式纪要版/简报摘要版/领导参阅版/工作通报版/内部讨论版/对外公开版/自定义模板版

> **派生版本已生成。请选择下一步操作：**
> 1. 进入RISK_GUARD（敏感风险审查）
> 2. 进入POLICY_REVIEW（政治规范审查）
> 3. 同时进入RISK_GUARD和POLICY_REVIEW
> 4. 跳过审查，直接归档
> 5. 修订派生结果

### 步骤6：敏感风险审查（RISK_GUARD，可选）

- 读取 [references/node6-risk-guard.md](references/node6-risk-guard.md) 获取完整规格
- 风险治理层：只审查/标记/提示/建议，禁止自动删改
- 7类风险检查：风险泄露/舆情风险/不当公开风险/整改风险/表述风险/隐私风险/保密风险

### 步骤7：政治规范审查（POLICY_REVIEW，可选）

- 读取 [references/node7-policy-review.md](references/node7-policy-review.md) 获取完整规格
- 政策规范治理层：只检查/标记/提示/建议，禁止自动升格/宣传化

### 步骤8：归档与导出（ARCHIVED）

- 全部审查通过后，将最终版本标记为STAGE_ARCHIVED
- 向用户确认流程完成，输出最终版本清单
- **导出 .docx 文件（按需）**：当用户需要导出公文格式的 .docx 时：
  1. 读取 [references/format-spec.md](references/format-spec.md) 获取完整排版规范
  2. 按模板样式生成 .docx：标题用方正小标宋简体22pt居中、一级标题用黑体16pt、二级标题用楷体_GB2312 16pt、正文用仿宋_GB2312 16pt、行距固定28pt、页边距上3.70/下3.50/左2.80/右2.60cm

> **导出选项：**
> 1. 导出 .docx（按公文模板排版）
> 2. 仅输出 Markdown 文本
> 3. 同时导出两种格式

## 修订回流规则

- 所有节点的修订回溯目标统一为STAGE_L3_REVISION
- VERIFY_PASS need_revision=true → L3_REVISION → VERIFY_PASS（循环）
- RISK_GUARD need_revision=true → 区分：L3事实问题回溯L3_REVISION；派生问题仅重新生成DERIVED
- POLICY_REVIEW need_revision=true → L3_REVISION
- 禁止使用DERIVED_REVISION等非标准状态

## 资源索引

| 编号 | 类型 | 文件 |
|------|------|------|
| 1 | 参考 | [references/general-rules.md](references/general-rules.md) |
| 2 | 参考 | [references/node1-text-cleaning.md](references/node1-text-cleaning.md) |
| 3 | 参考 | [references/node2-fact-archive.md](references/node2-fact-archive.md) |
| 4 | 参考 | [references/node3-topic-master.md](references/node3-topic-master.md) |
| 5 | 参考 | [references/node4-task-normalizer.md](references/node4-task-normalizer.md) |
| 6 | 参考 | [references/node5-derived-generation.md](references/node5-derived-generation.md) |
| 7 | 参考 | [references/node6-risk-guard.md](references/node6-risk-guard.md) |
| 8 | 参考 | [references/node7-policy-review.md](references/node7-policy-review.md) |
| 9 | 参考 | [references/verify-pass.md](references/verify-pass.md) |
| 10 | 参考 | [references/format-spec.md](references/format-spec.md) |
| 11 | 资产 | [assets/meeting-template.docx](assets/meeting-template.docx) |

## 注意事项

- 仅在执行对应节点时读取该节点的参考文档，避免上下文膨胀
- 每个节点完成后必须向用户提供明确的选项菜单，由用户决定下一步
- VERIFY_PASS是强制环节，不得跳过；L3_DRAFT和L3_REVISION后必须进入
- 修订回溯统一指向L3_REVISION，禁止创建非标准修订状态
- revision_count>=3且仍未通过VERIFY_PASS时，必须提示人工复核
- 各节点严格遵循职责边界，禁止跨节点越权操作