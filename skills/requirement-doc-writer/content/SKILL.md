---
name: requirement-doc-writer
description: A requirement document writing assistant. Use when users need to transform vague ideas, task descriptions, or requirements into structured markdown documents. Actively clarifies key information and generates clear, complete requirement specifications. Triggers: "写需求文档", "整理需求", "生成规格说明", "转成markdown", "帮我写文档".
---

# Requirement Document Writer

帮助用户将模糊的需求、想法或任务描述转写成结构化、清晰的Markdown需求文档。

## 设计模式

* **Inversion**：首先识别信息缺口，主动追问关键细节
* **Structured**：按标准需求文档模板组织内容
* **Refinement**：通过迭代澄清确保文档完整准确

## Gotchas

* 不要在信息不完整时强行生成文档，先追问关键信息
* 用户可能不知道该提供什么，按标准需求维度引导提问
* 文档结构要灵活适配不同类型的需求（功能/非功能/技术/业务）
* 最终输出必须是可直接使用的Markdown格式

## Workflow

### Step 1: Initial Assessment

接收用户输入，判断需求状态：

1. **已完整**：用户提供的信息是否包含目标、范围、约束等核心要素？
2. **部分清晰**：存在明确点但有遗漏
3. **高度模糊**：只有初步想法或单一关键词

### Step 2: Clarify Key Dimensions

对于**部分清晰**和**高度模糊**的需求，按需追问以下维度：

| 维度 | 追问问题示例 |
|------|-------------|
| **目标** | 这个需求的最终目标是什么？解决什么问题？ |
| **用户** | 谁会使用这个功能？他们的角色是什么？ |
| **范围** | 这个需求包含什么？不包含什么？ |
| **优先级** | 哪些是必须有的？哪些是nice-to-have？ |
| **约束** | 有时间、预算、技术限制吗？ |
| **验收标准** | 怎么算完成了？有什么具体的成功指标？ |
| **相关方** | 还有谁关心这个需求？需要考虑他们的意见吗？ |
| **依赖** | 这个需求依赖其他系统或需求吗？ |

**追问原则**：
- 先问最关键的3-5个问题，避免信息过载
- 用选择题而非开放式问题加速澄清
- 标记用户未回答但可能影响文档的问题

### Step 3: Determine Document Type

根据需求类型选择合适的文档模板：

| 需求类型 | 适用模板 |
|---------|---------|
| 产品功能需求 | 功能需求规格说明书 (FRS) |
| 技术/架构需求 | 技术需求文档 |
| 业务/流程需求 | 业务需求说明书 (BRS) |
| 非功能需求 | 质量属性需求 |
| 单一功能点 | 轻量级功能卡片 |
| 完整系统/项目 | 完整项目需求文档 |

### Step 4: Generate Document

基于选定模板和澄清的信息生成Markdown文档：

```
## 文档标题
### 1. 概述
- 背景
- 目标
- 范围定义

### 2. 用户与角色
- 用户群体
- 用户故事/用例

### 3. 功能需求
- 功能点1
- 功能点2

### 4. 非功能需求（如适用）
- 性能
- 安全
- 可用性

### 5. 约束与假设
- 技术约束
- 业务约束
- 假设条件

### 6. 验收标准
- 验收条件列表

### 7. 依赖与风险
- 依赖项
- 已知风险
```

### Step 5: Review and Iterate

呈现文档给用户并：

1. **确认完整性**：检查是否有遗漏的关键章节
2. **验证准确性**：确认信息理解正确
3. **收集反馈**：用户是否有修改意见
4. **迭代修订**：根据反馈调整文档

### Step 6: Final Output

输出最终版本的Markdown文档，包含：

- 完整的文档结构
- 清晰的分级标题
- 适当的项目符号列表
- 必要的表格或图表（如适用）
- 元数据（版本、作者、日期）

## Reference Templates

详细的文档模板请参考：
- `references/templates.md` - 完整的需求文档模板集合
- `references/questionnaire.md` - 需求澄清问题清单

## Document Format Guidelines

生成Markdown时遵循：

1. **标题层级**：最多使用3级标题，避免过深嵌套
2. **列表样式**：无序列表用于并列项，有序列表用于步骤
3. **表格**：用于对比、规格等结构化数据
4. **代码块**：用于示例、配置、API规格
5. **强调**：适度使用加粗/斜体突出关键信息
