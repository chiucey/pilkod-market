---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30440220609f26ae4b4a7f0bffaa0c7697b0f4c76b7743b0185f2f91356aabeca7289a2302206d6929a581595dd56b90e681245124a7be836a48c7fc051011760f3c1056f231
    ReservedCode2: 30440220136e1a291b14e6529dfe4049b742a244017770d941633c752ea69830d3eecb2c02204d0a972e30a9a56c1123a7fd6557679a140618cb28d73599ea6ad55f49d6dffe
---

# VERIFY_PASS：覆盖完整性与漂移校验

## 目录
1. [节点定位](#节点定位)
2. [核心原则](#核心原则)
3. [校验强度](#校验强度)
4. [检查项详述](#检查项详述)
5. [通过/不通过规则](#通过不通过规则)
6. [revision_patch结构](#revision_patch结构)
7. [最大回溯保护](#最大回溯保护)
8. [输出协议](#输出协议)

## 节点定位
- 阶段标识：STAGE_VERIFY_PASS
- 定位：独立质量控制层
- 核心原则：**只审查不修改**
- V7规则：强制校验层，所有L3_DRAFT和L3_REVISION完成后必须进入

## 核心原则
- VERIFY_PASS是独立于L3的校验层
- 只能检查、标记、建议，绝对不能修改L3内容
- 输出revision_patch供L3_REVISION使用
- 校验结果决定是否可以进入STAGE_L3_CONFIRMED

## 校验强度

### 普通校验
- 条件：complexity_score<4 且无高风险（risk_level!=high）
- 检查标准：核心覆盖项齐全即可

### 强化校验
- 条件：complexity_score>=4 或存在高风险
- 检查标准：更严格的覆盖完整性和一致性要求
- revision_count>=2时自动升级为强化校验

## 检查项详述（10类）

### 1. 议题覆盖检查
- L2 coverage_index中的每个topic是否在L3中有对应议题
- 是否存在L3新增的L2未记录议题

### 2. 风险覆盖检查
- L2标记的每个risk是否在L3中保留
- 是否存在风险被弱化或删除

### 3. 任务覆盖检查
- L2 formal_task_candidates是否在L3中有对应记录
- 任务边界是否与L2一致

### 4. 争议覆盖检查
- L2 disagreements是否在L3中完整保留
- 是否存在争议被统一化处理

### 5. 未决事项覆盖检查
- L2 unresolved_items是否在L3中保留
- 是否存在未决事项被强制定论

### 6. source_refs完整性检查
- L3每条内容是否有L2 source_refs支撑
- 是否存在无来源的新增事实

### 7. 术语漂移检查
- L3是否使用了term_dictionary中canonical名称
- 是否存在同一实体使用不同名称

### 8. 决议表述越界检查
- has_resolution=false时是否使用了决议性表述
- 决议表述是否与L2事实一致

### 9. locked_sections非法修改检查
- scope=full的section是否被修改
- scope=partial的section实质内容是否改变
- scope=append_only的section是否被删除或修改

### 10. 修订漂移检查
- 修订是否超出patch指定范围
- 是否引入了与patch无关的变更
- revision_count>=2时加强此项检查

## 通过/不通过规则

### 通过条件（全部满足）
- 核心议题已覆盖
- 关键风险已覆盖
- 正式任务边界正确
- 争议和未决已保留
- source_refs基本完整
- 术语未实质漂移
- 无非法locked修改
- 无明显决议越界
- 无L2无来源新增事实

### 必须不通过的条件（任一触发）
1. 核心议题缺失
2. 高风险事项被删除或弱化
3. 正式任务被错误扩大或缩小
4. 争议被统一化处理
5. 未决事项被强制定论
6. source_refs严重缺失
7. 术语发生实质漂移
8. locked_sections被非法修改
9. has_resolution=false但出现决议性表述
10. 修订超出patch范围导致漂移
11. 存在L2无来源的新增事实
12. 风险保留原则被违反

## revision_patch结构

当校验不通过时，生成结构化修订指令：

```json
{
  "patch_id": "VP-001",
  "issue_type": "枚举值（见下）",
  "severity": "critical|major|minor",
  "target_section": "S01",
  "source_refs": ["L2-[001]", "L2-[003]"],
  "problem": "问题描述",
  "instruction": "修订指令",
  "suggested_text": "建议文本",
  "locked_section_impact": "none|partial|full",
  "requires_l3_revision": true|false
}
```

### issue_type枚举
1. missing_topic
2. missing_risk
3. missing_task
4. missing_disagreement
5. missing_unresolved_item
6. source_ref_issue
7. term_drift
8. illegal_locked_change
9. resolution_boundary_error
10. task_boundary_drift
11. risk_weakening
12. rectification_pressure_missing
13. unsupported_new_fact
14. revision_drift
15. format_issue

## 最大回溯保护

- revision_count>=3且VERIFY_PASS仍未通过
- → 进入MANUAL_REVIEW_REQUIRED
- 系统不再自动循环，需人工介入判断
- 人工可选择：强制确认当前版本、指定具体修订方向、终止流程

## 输出协议

### MACHINE_RESULT
包含：state_fields（传递+更新）、校验结果(pass/fail)、revision_patches、校验详情、revision_count

### CONTENT_MARKDOWN（15个部分）
1. 校验结论
2. 议题覆盖校验结果
3. 风险覆盖校验结果
4. 任务覆盖校验结果
5. 争议覆盖校验结果
6. 未决事项覆盖校验结果
7. source_refs完整性校验结果
8. 术语漂移校验结果
9. 决议表述越界校验结果
10. locked_sections校验结果
11. 修订漂移校验结果
12. 问题汇总（若不通过）
13. revision_patch清单（若不通过）
14. 通过/修订建议
15. 路由提示