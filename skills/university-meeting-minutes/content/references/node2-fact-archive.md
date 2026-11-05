---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022003df54cbe489a21846185aa19dfd33f53957a9900b20c2fe8a138fee60c089f8022100d0f72a33eb1304d9c457c6e80ddc0a6e256f43df01260e2caa6342ea0b57051b
    ReservedCode2: 3045022100c74c6e80834c4ff29873c1317e0749e6e29afeb435f2a70df33aa2b6c000ac9602205142ddb0fd1262c2c6a1a6bc60155e97296f390e41705ba91d9998c967cd4230
---

# 节点2：时序事实档案生成（L2）

## 目录
1. [节点定位](#节点定位)
2. [核心职责](#核心职责)
3. [输入要求](#输入要求)
4. [L2编号体系](#l2编号体系)
5. [discussion_density与事实粒度](#discussion_density与事实粒度)
6. [coverage_index结构](#coverage_index结构)
7. [重复争论折叠规则](#重复争论折叠规则)
8. [分段输入兼容](#分段输入兼容)
9. [输出协议](#输出协议)
10. [禁止行为](#禁止行为)

## 节点定位
- 阶段标识：STAGE_L2_FACT
- 定位：事实层节点，建立会议事实时间轴
- 上游节点：L1
- 下游节点：L3

## 核心职责
1. 建立会议事实时间轴
2. L2编号体系管理
3. 议题锚点表生成
4. coverage_index构建
5. 正式任务候选记录

## 输入要求
- L1输出的MACHINE_RESULT（含state_fields、term_dictionary）
- L1输出的清洗后文本（CONTENT_MARKDOWN第1部分）

## L2编号体系

### 标准格式
- 单一事实条目：L2-[001]、L2-[002]...
- 分段输入：L2-S01-[001]、L2-S02-[001]...（S后为段号）

### 编号规则
- 严格按时间顺序编号
- 每条事实独立编号
- 编号一旦生成不可更改
- 合并后重新编号需保留原编号映射

## discussion_density与事实粒度

| 密度 | 粒度规则 |
|------|---------|
| low | 允许合并低信息量发言，保留核心信息点 |
| medium | 标准粒度，每条独立事实单独记录 |
| high | 必须细粒度保留，每个发言要点独立记录 |

## coverage_index结构

coverage_index是L2的关键产出，为后续VERIFY_PASS校验提供覆盖基准：

```json
{
  "topics": ["议题1", "议题2"],
  "key_facts": ["关键事实1", "关键事实2"],
  "formal_task_candidates": [
    {
      "description": "任务描述",
      "responsible": "责任主体（若明确）",
      "source_refs": ["L2-[001]"]
    }
  ],
  "risks": ["风险1", "风险2"],
  "disagreements": ["争议1"],
  "unresolved_items": ["未决1"],
  "abnormal_items": ["异常1"],
  "source_refs": {
    "total_count": 0,
    "coverage_rate": 0
  }
}
```

### 8类覆盖项
1. **topics**：议题清单
2. **key_facts**：关键事实
3. **formal_task_candidates**：正式任务候选（可能成为L4的正式任务）
4. **risks**：风险标记
5. **disagreements**：争议记录
6. **unresolved_items**：未决事项
7. **abnormal_items**：异常标记
8. **source_refs**：来源引用统计

## 重复争论折叠规则

- 同一争论点连续超过3轮发言：允许摘要化保留
- 折叠时必须保留：争论焦点、各方立场、是否有结论
- **禁止**：删除争议、制造统一意见、省略关键分歧

## 分段输入兼容

### input_mode="segment"
- 使用L2-S01-[001]格式编号
- 建议suggested_next_stage="STAGE_L2_MERGE"
- 合并时重新编号为标准格式

### 合并规则
- 保持时间顺序
- 去除重复条目
- 保留所有非重复信息
- 更新coverage_index

## 输出协议

### MACHINE_RESULT
包含：state_fields（传递+更新）、coverage_index、fact_timeline、议题锚点表、formal_task_candidates

### CONTENT_MARKDOWN（10个部分）
1. 事实时间轴
2. L2编号索引
3. 议题锚点表
4. coverage_index
5. 正式任务候选
6. 风险标记汇总
7. 争议记录汇总
8. 未决事项汇总
9. 异常标记汇总
10. 路由提示

## 禁止行为
1. 归类议题（L3职责）
2. 判断事实重要性（仅记录不判断）
3. 精简事实（保留完整信息）
4. 合并不同议题的事实
5. 删除争议性发言
6. 生成结论或决议
7. 补充L1未记录的信息
8. 修改发言原意
9. 评估事实可靠性
10. 优化原始表述