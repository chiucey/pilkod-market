---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502200747bc4cac67addc9c6ee5167ffca75395d7eee3848a850cca00cbfa1878d51a022100b8bdc3dc73ac676ed437b6b7a5ac99eef896bf591ba5ef0cf43fc83540a7216b
    ReservedCode2: 3045022100afddfe45fcd4b59df4d74911a4cf8ddb905c2fd3c81f22355c3c5373cf4b7b4602202dc56abc34866d9990a3bfdb610b6debda98aad1eb006cb9c1515f196bc907ba
---

# 节点3：议题归类母版生成（L3）

## 目录
1. [节点定位](#节点定位)
2. [核心职责](#核心职责)
3. [两种运行模式](#两种运行模式)
4. [revision_mode](#revision_mode)
5. [locked_sections机制](#locked_sections机制)
6. [has_resolution控制](#has_resolution控制)
7. [VERIFY_PASS强制运行](#verify_pass强制运行)
8. [RISK_GUARD/POLICY_REVIEW回流处理](#risk_guardpolicy_review回流处理)
9. [输出协议](#输出协议)
10. [禁止行为](#禁止行为)

## 节点定位
- 阶段标识：STAGE_L3_DRAFT（初稿）/ STAGE_L3_REVISION（修订）
- 定位：结构层节点，生成正式结构化母版
- 上游节点：L2（或VERIFY_PASS/RISK_GUARD/POLICY_REVIEW回流的修订patch）
- 下游节点：VERIFY_PASS（强制校验）

## 核心职责
1. 正式结构化母版生成
2. 议题归类与组织
3. 多轮修订稳定控制
4. locked_sections管理
5. 修订patch处理

## 两种运行模式

### STAGE_L3_DRAFT（初稿模式）
- 首次生成结构化母版
- 基于L2的coverage_index进行议题归类
- 生成后必须进入VERIFY_PASS

### STAGE_L3_REVISION（修订模式）
- 接收来自VERIFY_PASS/RISK_GUARD/POLICY_REVIEW的修订patch
- 根据patch指令进行定向修订
- 修订后必须重新进入VERIFY_PASS

## revision_mode

### incremental（默认）
- 仅修改patch指定的部分
- 未涉及的段落保持不变
- 保持locked_sections约束
- 适用于大多数修订场景

### full_rebuild
- 重新生成整个母版
- 仅当用户明确要求时使用
- 必须不违反locked_sections约束
- 需谨慎使用，需记录full_rebuild原因

## locked_sections机制

### 锁定范围scope
| scope | 含义 | 允许操作 |
|-------|------|---------|
| full | 完全锁定 | 禁止任何修改 |
| partial | 部分锁定 | 允许措辞优化但不改变实质内容 |
| append_only | 仅追加 | 允许追加新信息，禁止修改已有内容 |

### 建议默认append_only的内容
- 风险问题
- 整改事项
- 未决事项
- 争议事项

### locked_sections结构
```json
{
  "section_id": "S01",
  "section": "议题一：xxx",
  "scope": "full|partial|append_only",
  "reason": "锁定原因",
  "content_hash": "hash值",
  "snapshot": "锁定时内容快照"
}
```

### 锁定校验
- VERIFY_PASS检查是否存在locked_sections非法修改
- 修订时必须遵守scope约束
- full_rebuild模式也必须尊重locked_sections

## has_resolution控制

当has_resolution=false时：
- 禁止使用"会议决定"、"一致同意"、"正式部署"等表述
- 应使用"会议讨论了"、"与会人员提出了"等中性表述
- 不得为无决议的讨论制造结论

当has_resolution=true时：
- 可使用决议性表述
- 但必须与L2事实一致，不得夸大

## VERIFY_PASS强制运行

V7规则：
- 所有L3_DRAFT完成后必须进入STAGE_VERIFY_PASS
- 所有L3_REVISION完成后必须进入STAGE_VERIFY_PASS
- 不可跳过，不可绕过
- VERIFY_PASS通过后才可进入STAGE_L3_CONFIRMED

## RISK_GUARD/POLICY_REVIEW回流处理

### 区分两种回流
1. **应回到L3修正的**：L3存在事实错误需要修正
2. **不应修改L3的**：L3事实正确但派生版本需调整

### 处理策略
- 对于应修正L3的问题：回到STAGE_L3_REVISION修正L3
- 对于不应修改L3的问题：仅在L3中增加"派生或流转注意事项"标注，不修改L3实质内容
- 禁止因派生审查而删除L3中的真实风险信息

## 输出协议

### MACHINE_RESULT
包含：state_fields（传递+更新）、母版结构、locked_sections、revision_count、revision_history

### CONTENT_MARKDOWN（7个部分）
1. 议题归类母版正文
2. 议题索引
3. locked_sections清单
4. revision记录（修订模式）
5. 与L2的映射关系
6. 未覆盖事项说明
7. 路由提示

## 禁止行为
1. 新增L2未记录的事实
2. 删除L2已记录的风险/争议/未决事项
3. 制造L2未体现的决议
4. 合并不同议题的关键信息导致丢失
5. 修改term_dictionary中的canonical名称
6. 违反locked_sections约束
7. 在has_resolution=false时使用决议性表述
8. 为美观而省略关键细节