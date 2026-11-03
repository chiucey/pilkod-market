---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b75a429d02134cbff33df37531ca5de5
    PropagateID: b75a429d02134cbff33df37531ca5de5
    ReservedCode1: 3046022100bc2ba36c2b37da1c23d53836008aaa41c995dccd9d416222892c5a4a41fc826b0221008a4ae8cd404a5c49f8b24de2a0530ebf53bad8ad4a9c35f476fe8754b0133662
    ReservedCode2: 304502210088d344349db53abd865a3288c9d1973fc163943c79708439ebbe85cb50040cb102207e545e4264ecf2f35b2c179b17ca3aa9c1edb068b02c39476d9d79ee618d4ec4
description: 分析账单数据中各业务（union、cpd、feeds、push、brand、search）的成本。当用户要求分析账单成本、按业务分类统计费用时使用。
name: bill-cost-analyzer
---

# 账单成本分析技能

## 功能说明

分析账单CSV数据，按业务类型统计成本。业务区分规则：

| 业务关键词 | 匹配条件 | 说明 |
|-----------|----------|------|
| union | groupname包含"union" | 联盟业务 |
| cpd | groupname包含"cpd" | CPD业务 |
| feeds | groupname包含"feeds" | Feeds业务 |
| push | groupname包含"push" | Push推送业务 |
| brand | groupname包含"brand" | Brand品牌业务 |
| search/srh | groupname包含"search"或"srh" | 搜索业务 |
| 公共业务 | 不包含以上关键词 | 公共基础设施 |

## 核心逻辑

1. 读取CSV账单数据
2. 根据groupname字段匹配业务类型
3. 汇总各业务的cost字段
4. 输出详细的成本分析报告

## 输出格式

```json
{
  "summary": {
    "total_cost": 总成本,
    "business_count": 业务数量
  },
  "details": [
    {
      "business": "业务名称",
      "keyword": "匹配关键词",
      "cost": 成本,
      "percentage": 占比,
      "instance_count": 实例数
    }
  ]
}
```

## 使用示例

用户提供CSV文件后，技能会自动：
1. 解析数据
2. 按关键词分类统计
3. 计算各项占比
4. 生成分析报告
