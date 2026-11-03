---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304602210085758b3017614f363c0686cfab4acfe5a9bac61ce8013f0b21f910f0c2b5cf4e0221008798d04957ef4b9c0a65414121bb47ea00dabfb14cb8a656621ba5ce6b2d90f2
    ReservedCode2: 3046022100c67469328f6b7ec2787d2dcb29d7a72368197b8b0017da50750dbaa3b9b93399022100e44481a19c6cf18cc08397a885eb0e79198957897f7ffc9c531db1b6e412c095
---

# 节点1：文本清洗与会议识别（L1）

## 目录
1. [节点定位](#节点定位)
2. [核心职责](#核心职责)
3. [输入要求](#输入要求)
4. [state_fields结构](#state_fields结构)
5. [complexity_score计算](#complexity_score计算)
6. [term_dictionary建立](#term_dictionary建立)
7. [长文本保护规则](#长文本保护规则)
8. [输出协议](#输出协议)
9. [禁止行为](#禁止行为)

## 节点定位
- 阶段标识：STAGE_L1_CLEAN
- 定位：入口节点，负责文本清洗与会议识别
- 下游节点：L2（时序事实档案）

## 核心职责
1. ASR/OCR错误修复
2. 会议元信息提取
3. state_fields生成
4. term_dictionary建立
5. complexity_score计算
6. 异常标记与路由提示

## 输入要求
- 会议原始记录文本（ASR转写/OCR识别/手写整理稿）
- 用户补充信息（如有）

## state_fields结构

```json
{
  "meeting_type": "枚举值（见下）",
  "risk_level": "low|medium|high",
  "discussion_density": "low|medium|high",
  "has_resolution": true|false,
  "has_disagreement": true|false,
  "has_rectification": true|false,
  "complexity_score": 0,
  "estimated_topic_count": 0,
  "enable_verify_pass": "auto",
  "enable_node6": "auto",
  "enable_node7": "auto"
}
```

### meeting_type枚举（11种）
1. 党委会
2. 校长办公会
3. 专题工作会
4. 协调推进会
5. 理论学习
6. 民主生活会
7. 组织生活会
8. 述职评议会
9. 教学委员会
10. 学术委员会
11. 其他

### risk_level判定
- **low**：常规事务性讨论，无风险标记
- **medium**：涉及经费/人事/设备采购等敏感事项
- **high**：涉及整改/重大风险/争议/保密事项

### discussion_density判定
- **low**：多为单向汇报，讨论环节少
- **medium**：有讨论互动，但议题集中
- **high**：多轮深入讨论、争论，议题发散

## complexity_score计算

| 条件 | 加分 |
|------|------|
| 文本长度>12000字 | +2 |
| risk_level=high | +2 |
| discussion_density=high | +2 |
| estimated_topic_count>=5 | +1 |
| has_disagreement=true | +1 |
| has_rectification=true | +2 |

## term_dictionary建立

从文本中提取术语映射关系：
```json
{
  "canonical": "标准名称",
  "variants": ["变体1", "变体2"],
  "category": "组织|政策|项目|术语"
}
```

- 识别同一实体的不同表述（如"双一流"与"双一流建设"）
- 后续节点必须使用canonical名称
- 全流程传递并维护

## 长文本保护规则

当输入文本超过处理能力时：
- 设置 input_status="too_long"
- 设置 requires_segmentation=true
- 设置 pass=false
- 建议分段输入策略

## 输出协议

### MACHINE_RESULT
包含：state_fields、term_dictionary、metadata、异常标记

### CONTENT_MARKDOWN（7个部分）
1. 清洗后文本
2. 会议元信息
3. 状态字段（state_fields）
4. complexity_score计算说明
5. term_dictionary
6. 异常标记
7. 路由提示

## 禁止行为（20项）
1. 生成纪要
2. 生成总结
3. 删除风险信息
4. 补充全文意
5. 合并不同发言
6. 判断发言正确性
7. 修改会议原意
8. 添加个人观点
9. 省略关键细节
10. 改变发言顺序
11. 美化原始表述
12. 删除重复内容（重复可能是刻意强调）
13. 合并议题
14. 评估会议质量
15. 生成行动项
16. 归类议题
17. 标注重要性
18. 推测未说内容
19. 修改数字/日期
20. 优化行文风格