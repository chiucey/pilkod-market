---
name: saic-case
description: 市场监督管理投诉举报案件处理技能。基于《市场监督管理投诉举报处理办法》（2026年4月15日施行，总局令第121号），辅助用户处理投诉举报案件，包括案件材料审查、投诉书/举报书起草、管辖判断、时限跟踪、程序合规检查、违法线索研判与举报策略。激活关键词：投诉、举报、市场监管、市场监督投诉、举报材料、投诉举报办理。
---

# 市场监督管理投诉举报案件处理技能（SAIC-Case）

基于《市场监督管理投诉举报处理办法》（国家市场监督管理总局令第121号，2026年4月15日施行）构建的专业技能。

## 核心能力

- **案件材料审查**：对照《办法》第10-11条，核查投诉/举报材料是否齐备
- **投诉书/举报书起草**：根据《办法》规定的形式要件，起草规范化文书
- **管辖判断**：依据第13-14条（投诉）、第29-33条（举报），确定有管辖权的部门
- **时限监控**：跟踪7日受理、60日调解、15日核查等关键节点
- **程序合规检查**：对照《办法》全文，检查各环节程序是否合法
- **违法线索研判**：分析涉嫌违反的市场监督管理法律法规条款
- **举报策略**：根据第35条重复举报规则，优化举报策略
- **恶意索赔识别**：依据第16条、第42条，识别和应对恶意索赔行为

## 核心法律依据速查

| 关键条款 | 内容摘要 |
|---------|---------|
| 第3条 | 投诉/举报的定义 |
| 第7条 | 投诉举报禁止滥用权利 |
| 第10-11条 | 投诉提交材料要求 |
| 第15条 | 7个工作日受理决定 |
| 第16条 | 不予受理的七种情形 |
| 第17条 | "非为生活消费"的判断因素 |
| 第23条 | 终止调解八种情形 |
| 第28条 | 举报提交材料要求 |
| 第35条 | 举报处理规则（重复举报、并案处理） |
| 第42条 | 涉嫌敲诈勒索/骗取赔偿移送公安机关 |

## 使用方式

### 1. 投诉材料审查

用户提交投诉材料后，调用审查函数检查：

```python
import sys
sys.path.append('~/.openclaw/skills/saic-case/scripts')
from complaint_analyzer import review_complaint

# 审查投诉材料
result = review_complaint({
    "complainant_info": "...",  # 真实身份信息
    "respondent_info": "...",   # 被投诉人信息
    "claim": "...",             # 投诉请求
    "facts": "...",             # 事实依据
    "purpose": "..."            # 消费目的（是否为生活消费）
})
```

### 2. 投诉书/举报书生成

```python
from document_generator import generate_complaint_letter, generate_report_letter

# 生成投诉书
complaint = generate_complaint_letter(
    complainant={"name": "...", "phone": "...", "address": "..."},
    respondent={"name": "...", "address": "..."},
    claim="...",
    facts=["事实1", "事实2"],
    evidence=["证据1", "证据2"]
)

# 生成举报书
report = generate_report_letter(
    reporter={"name": "...", "phone": "...", "address": "..."},
    respondent={"name": "...", "address": "..."},
    violation_type="...",
    clues=["线索1", "线索2"],
    evidence=["证据1", "证据2"],
    legal_basis=["《消费者权益保护法》第X条"]
)
```

### 3. 管辖判断

```python
from jurisdiction_checker import determine_jurisdiction

# 判断投诉管辖
result = determine_jurisdiction(
    case_type="complaint",  # "complaint" 或 "report"
    respondent_type="platform_seller",  # "general"/"platform"/"platform_seller"
    platform_info={"name": "...", "registered_address": "..."},
    respondent_address={"displayed": "...", "actual": "..."}
)
```

### 4. 时限计算

```python
from deadline_calculator import calculate_deadlines

# 计算关键时限
deadlines = calculate_deadlines(
    case_type="complaint",
    acceptance_date="2026-04-15"  # 投诉受理日期
)
# 返回：受理决定期限、调解终止期限、线索核查期限等
```

### 5. 合规检查

```python
from compliance_checker import check_procedure_compliance

# 程序合规检查
issues = check_procedure_compliance(
    case_type="complaint",
    timeline={
        "received": "2026-04-15",
        "acceptance_decision": "2026-04-22",
        "mediation_end": "2026-06-14"
    },
    procedures_followed=["acceptance_notice", "mediation", "investigation_ clue_discovery"]
)
```

### 6. 违法线索分析

```python
from violation_analyzer import analyze_violation

# 分析涉嫌违法行为
analysis = analyze_violation({
    "facts": ["经营者销售过期食品", "经营者拒绝开具发票"],
    "case_context": "消费者在超市购买食品后发现过期"
})
# 返回：涉嫌违反的法律条款、证据充分性评估、举报建议
```

## 流程图

```
用户案件输入
     │
     ▼
┌─────────────┐    否    ┌──────────────────┐
│ 材料是否齐备？│──→不受理│ 告知理由+救济途径  │
└──────┬──────┘         └──────────────────┘
       是
       ▼
┌────────────────┐    是     ┌──────────────────┐
│ 是否为生活消费？│──→否 ──→│ 第16条第3项不予受理 │
└──────┬─────────┘          └──────────────────┘
       是
       ▼
┌──────────────────┐
│ 确定管辖部门      │
│（第13-14/29-33条）│
└────────┬─────────┘
         ▼
┌──────────────────┐
│ 7工作日内受理决定  │
│（第15条）         │
└────────┬─────────┘
         ▼
    ┌────────────┐
    │ 进入调解程序？ │
    └─────┬──────┘
      双方同意
         ▼
┌──────────────────┐     60日未成/拒绝/撤回     ┌──────────────┐
│ 调解成功→制作调解书 │────────────────→终止调解│ 告知救济途径  │
└──────────────────┘                          └──────────────┘
         │
    发现违法线索
         ▼
┌──────────────────┐
│ 15工作日内核查     │
│ 特殊可延长15工作日  │
│（第27条）         │
└──────────────────┘
         ▼
┌──────────────────┐
│ 涉嫌敲诈勒索/骗赔？ │
│（第42条）         │
    是→移送公安机关
         ▼
┌──────────────────┐
│ 依《行政处罚程序》  │
│ 立案查处           │
└──────────────────┘
```

## 注意事项

- 本技能依据2026年4月15日施行的总局令第121号构建
- 投诉须证明"为生活消费需要"（第16条第3项）
- 举报须提供"具体线索和事实依据"（第28条）
- 重复举报同一事实不再处理，但补充新事实可合并处理（第35条）
- 涉嫌敲诈勒索、夹带掉包造假等行为须移送公安机关（第42条）
- 调解须双方同意，任何一方拒绝则不能强制调解（第18条）

## 参考文件

- `references/legal_provisions.md` — 重点条款逐条解读
- `references/jurisdiction_rules.md` — 管辖规则详解
- `references/bad_claims_rules.md` — 恶意索赔认定规则
- `references/key_deadlines.md` — 时限汇总表
- `templates/complaint_template.md` — 投诉书模板
- `templates/report_template.md` — 举报书模板
