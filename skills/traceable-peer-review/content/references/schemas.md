# 输出模式和数据结构参考

本文档定义了可追踪同行评审系统的输入/输出数据结构和模式规范。

## 1. 输入数据结构

### 1.1 论文语义单元

```typescript
interface PaperSemanticUnit {
  id: string;           // 唯一标识符，格式: "u{index}"
  page: number;        // 页码（1-indexed）
  line_start: number;  // 起始行号
  line_end: number;    // 结束行号
  content: string;     // 文本内容
  unit_type: "text" | "header" | "equation" | "table" | "figure" | "caption";
  bbox?: BoundingBox;  // 边界框（可选）
}

interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  page_width: number;   // 页面宽度（用于归一化）
  page_height: number;  // 页面高度（用于归一化）
}
```

### 1.2 位置锚点

```typescript
interface LocationAnchor {
  page: number;           // 页码
  line_start: number;     // 起始行
  line_end: number;       // 结束行

  // 以下为可选的渲染辅助字段
  bbox?: BoundingBox;
  normalized_coords?: {
    y1_percent: number;   // 0-100
    y2_percent: number;  // 0-100
    x1_percent: number;  // 默认 8
    x2_percent: number;   // 默认 92
  };
}
```

## 2. 核心数据结构

### 2.1 声明-证据-风险分类账条目

```typescript
interface ClaimLedgerEntry {
  claim_id: string;           // 格式: "c{index}"
  claim_text: string;          // 声明文本
  in_paper_evidence: string[]; // 论文内证据锚点列表

  risk_statement: string;     // 风险声明
  status: "confirmed" | "suspected";

  // 可选字段
  supporting_annotations?: string[];  // 关联注释ID
  novelty_tag?: NoveltyTag;            // 新颖性标签
  verification_status?: "verified" | "failed" | "pending";
}
```

### 2.2 调查议程项

```typescript
interface InvestigationAgendaItem {
  question_id: string;        // 格式: "q{index}"
  question_text: string;      // 问题文本

  related_claims: string[];   // 关联的声明ID
  priority: "critical" | "high" | "medium" | "low";

  // 验证结果
  retrieved_papers?: RetrieverPaper[];
  verification_result?: {
    comparable: boolean;
    matched_setting: boolean;
    novelty_tag: NoveltyTag;
    notes: string;
  };
}
```

### 2.3 锚定注释

```typescript
interface AnchoredAnnotation {
  annotation_id: string;      // 格式: "ann_{index}"
  location: LocationAnchor;   // 位置锚点

  // 分类和严重性
  category: IssueCategory;
  severity: "critical" | "major" | "minor";

  // 内容
  diagnosis: string;          // 问题诊断
  scientific_risk: string;    // 科学风险解释

  // 修复建议（核心可操作性部分）
  repair_action: string;      // 具体可执行的操作
  suggested_rewrite?: string; // 建议的修改文本（可选）

  // 关联
  linked_claims: string[];    // 关联的声明ID
  linked_comparators?: string[]; // 用于比较的先前工作
}

type IssueCategory =
  | "soundness"      // 技术正确性
  | "novelty"        // 新颖性
  | "clarity"        // 清晰度
  | "experiment"     // 实验
  | "ethics"         // 伦理
  | "presentation"   // 呈现
  | "comparison"     // 比较
  | "other";         // 其他
```

### 2.4 新颖性标签

```typescript
type NoveltyTag =
  | "SUPPORTED"                 // 无直接可比先前工作
  | "PARTIALLY_OVERLAPPING"     // 存在重叠但有剩余新颖性
  | "SUBSTANTIALLY_OVERLAPPED" // 直接可比工作已覆盖
  | "UNCLEAR";                  // 默认：无法确定

interface NoveltyAssessment {
  claim: string;
  comparators_found: string[];   // 检索到的可比论文
  matched_setting: boolean;     // 是否满足匹配设置
  novelty_tag: NoveltyTag;
  notes: string;                // 备注和解释
  matched_setting_decision?: string; // 匹配决策记录
}
```

### 2.5 优先级修复计划项

```typescript
interface RepairPlanItem {
  item_id: string;              // 格式: "S{index}"
  priority: "P0" | "P1" | "P2"; // P0=必须, P1=高, P2=可选

  linked_annotations: string[]; // 关联的注释ID
  linked_issues: string[];      // 关联的问题

  action_description: string;   // 操作描述
  concrete_revision?: string;   // 具体修订建议
  expected_benefit: string;     // 预期收益

  status: "pending" | "in_progress" | "completed" | "not_applicable";
}
```

## 3. 输出数据包结构

### 3.1 完整审稿包

```typescript
interface ReviewPackage {
  // 元数据
  metadata: {
    paper_title?: string;
    paper_id?: string;
    generated_at: string;        // ISO 8601 时间戳
    generator_version: string;    // 技能版本
    evaluation_pool?: string;     // 评估数据集标识
  };

  // 核心输出
  report: StructuredReport;     // 结构化报告 (R)
  annotations: AnchoredAnnotation[]; // 锚定注释集 (A)
  repair_plan: RepairPlanItem[];      // 优先级修复计划 (P)
  novelty_assessment: NoveltyAssessment[]; // 新颖性/价值评估 (N)

  // 可追踪性证据
  evidence_graph: {
    claims: ClaimLedgerEntry[];
    agenda: InvestigationAgendaItem[];
  };

  // 质量指标
  quality_metrics: {
    annotation_count: number;
    critical_count: number;
    major_count: number;
    minor_count: number;

    // 覆盖率指标（如果有参考）
    strict_coverage?: number;
    major_issue_coverage?: number;

    // 可追踪性指标
    annotations_with_anchor: number;
    annotations_with_risk: number;
    annotations_with_repair: number;

    // 新颖性检查指标
    novelty_checks_performed: number;
    comparable_papers_retrieved: number;
  };

  // 隐私和安全标记
  privacy_security: {
    pdf_sanitized: boolean;
    local_processing: boolean;
    external_services_used: string[];
    data_retention: "session" | "none";
  };

  // 导出门控状态
  export_gate: {
    schema_valid: boolean;
    search_budget_met: boolean;
    intent_coverage_met: boolean;
    annotation_budget_met: boolean;
    all_annotations_complete: boolean;
    ready_for_export: boolean;
  };
}
```

### 3.2 结构化报告

```typescript
interface StructuredReport {
  summary: {
    paper_overview: string;      // 论文概述
    core_contribution: string;   // 核心贡献
    method_summary: string;      // 方法概要
  };

  strengths: Array<{
    point: string;
    evidence: string;            // 证据锚点
  }>;

  weaknesses: Array<{
    point: string;
    severity: "critical" | "major" | "minor";
    location: string;            // 位置锚点
    impact: string;              // 影响说明
  }>;

  key_issues: KeyIssue[];

  overall_assessment: {
    recommendation: "Accept" | "Major Revision" | "Minor Revision" | "Reject";
    confidence: "high" | "medium" | "low";
    rationale: string;
  };
}

interface KeyIssue {
  issue_id: string;
  title: string;
  severity: "critical" | "major" | "minor";
  location: string;             // 位置锚点
  evidence: string;             // 证据
  impact: string;               // 影响
  fix_required: string;         // 需要的修复
}
```

## 4. JSON Schema 验证规则

### 4.1 注释必填字段检查

每个 AnchoredAnnotation 必须包含：
- [ ] annotation_id (非空字符串)
- [ ] location.page (正整数)
- [ ] location.line_start (非负整数)
- [ ] location.line_end (>= line_start)
- [ ] category (属于 IssueCategory)
- [ ] severity (属于 "critical" | "major" | "minor")
- [ ] diagnosis (非空字符串)
- [ ] scientific_risk (非空字符串)
- [ ] repair_action (非空字符串)

### 4.2 导出门控条件

```python
def check_export_gate(package: ReviewPackage) -> dict:
    return {
        "schema_valid": (
            package.report.summary is not None and
            len(package.annotations) > 0 and
            len(package.repair_plan) > 0
        ),
        "search_budget_met": package.quality_metrics.novelty_checks_performed >= 3,
        "intent_coverage_met": len(set(a.category for a in package.annotations)) >= 3,
        "annotation_budget_met": len(package.annotations) >= 10,
        "all_annotations_complete": all(
            a.repair_action is not None and a.repair_action != ""
            for a in package.annotations
        ),
    }
```

## 5. 导出格式

### 5.1 结构化报告 (Markdown)

```markdown
# Structured Review Report

## Summary
[内容...]

## Strengths
1. [优势1] - [证据锚点]
2. [优势2] - [证据锚点]

## Weaknesses
### Critical Issues
- **[标题]** [严重性] - [位置锚点]
  - 风险: [科学风险]
  - 修复: [修复建议]

### Major Issues
[...]

## Key Issues Summary
| ID | Severity | Location | Issue |
|---|---|---|---|
| iss_001 | Critical | p3/l14-22 | 新颖性声明过强 |

## Recommendation
**Major Revision Required**

[Rationale...]
```

### 5.2 锚定注释 (JSON Lines)

```jsonl
{"annotation_id":"ann_001","location":{"page":3,"line_start":14,"line_end":22},"category":"novelty","severity":"critical","diagnosis":"声明的'首创性'无法与已发表的端到端自主发现系统区分","scientific_risk":"声明无法通过匹配设置的直接比较验证","repair_action":"将'first'声明限定于具体维度","linked_claims":["c1"]}
{"annotation_id":"ann_002","location":{"page":5,"line_start":10,"line_end":15},"category":"experiment","severity":"major","diagnosis":"缺少统计显著性检验","scientific_risk":"无法确定观察到的差异是否显著","repair_action":"添加方差和统计检验","linked_claims":["c3"]}
```

### 5.3 完整包 (JSON)

```json
{
  "metadata": {...},
  "report": {...},
  "annotations": [...],
  "repair_plan": [...],
  "novelty_assessment": [...],
  "evidence_graph": {...},
  "quality_metrics": {...},
  "privacy_security": {...},
  "export_gate": {...}
}
```

## 6. 示例数据

### 6.1 完整分类账条目示例

```json
{
  "claim_id": "c1",
  "claim_text": "DeepScientist是首个实现大规模SOTA超越的科学发现系统",
  "in_paper_evidence": ["p1/l5-10", "p2/l20-25"],
  "risk_statement": "如果AI Scientist-v2、CodeScientist等已实现可比能力，则此'首创'声明不成立",
  "status": "suspected",
  "novelty_tag": "UNCLEAR",
  "verification_status": "pending"
}
```

### 6.2 完整注释示例

```json
{
  "annotation_id": "ann_001",
  "location": {
    "page": 1,
    "line_start": 5,
    "line_end": 10,
    "normalized_coords": {
      "y1_percent": 12.5,
      "y2_percent": 18.3,
      "x1_percent": 8,
      "x2_percent": 92
    }
  },
  "category": "novelty",
  "severity": "critical",
  "diagnosis": "论文声称'首个大规模证据证明AI实现超越人类SOTA的发现'，但未精确限定维度",
  "scientific_risk": "此声明无法与已发表的端到端自主发现系统（如AI Scientist-v2、CodeScientist）区分，可能导致审稿人基于新颖性过度声明而拒绝论文",
  "repair_action": "将'first'声明限定于具体维度，例如：'首个在三个不同AI研究领域实现SOTA超越、且在一个月时间窗口内完成评估的系统'",
  "suggested_rewrite": "We present DeepScientist, the first system to demonstrate SOTA-surpassing discoveries across three distinct AI research domains (Agent Failure Attribution, LLM Inference Acceleration, AI Text Detection) within a month-long evaluation window using 20,000+ GPU hours.",
  "linked_claims": ["c1"],
  "linked_comparators": ["AI Scientist-v2", "CodeScientist", "Kosmos"]
}
```

### 6.3 完整修复计划项示例

```json
{
  "item_id": "S1",
  "priority": "P0",
  "linked_annotations": ["ann_001", "ann_002"],
  "linked_issues": ["iss_001"],
  "action_description": "将新颖性声明精确限定到具体维度",
  "concrete_revision": "Replace 'first large-scale evidence' with 'first demonstration of SOTA-surpassing discoveries across three distinct AI research domains within a month-long evaluation window using 20,000+ GPU hours.'",
  "expected_benefit": "防止审稿人基于与先前单任务或短时系统的比较而否决新颖性声明",
  "status": "pending"
}
```