# 工程咨询工作流实现指南

## 典型场景

### 1. 工程项目评审

```
需求分析 → 并行处理(成本/风险/合规) → 条件分支 → 报告生成
```

### 2. 合同审核

```
文档接收 → 条款提取 → 风险识别 → 合规检查 → 意见生成
```

### 3. 造价咨询

```
工程量计算 → 材料询价 → 人工估算 → 利润分析 → 报告输出
```

## 实现要点

### Agent 设计原则

1. **单一职责** - 每个 Agent 只处理特定任务
2. **状态独立** - 通过状态传递实现协作
3. **错误恢复** - 关键节点配置重试和降级
4. **可观测性** - 添加完整的日志和追踪

### 状态传递示例

```python
class ConsultationState(TypedDict):
    project_id: str
    documents: list
    analysis_results: dict
    final_report: str
    errors: list
```
