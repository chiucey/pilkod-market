# AutoLearn&Refine_Claw 参考文档

## 复盘报告模板

```json
{
  "report_version": "1.0",
  "generated_at": "2026-03-29T08:16:04Z",
  "task_info": {
    "task_id": "string",
    "task_type": "string",
    "task_description": "string",
    "security_level": "string"
  },
  "execution_summary": {
    "accuracy": 0.0,
    "completion": 0.0,
    "timeliness": 0.0,
    "compliance": 0.0,
    "satisfaction": 0.0,
    "overall_score": 0.0
  },
  "defects": [
    {
      "id": "string",
      "type": "逻辑错误|内容偏差|效率低下|合规风险|工具调用失误",
      "severity": "critical|major|minor",
      "location": "string",
      "description": "string",
      "root_cause": "string",
      "impact": "string",
      "fix_suggestion": "string"
    }
  ],
  "learning_inputs": [
    {
      "source": "string",
      "content_type": "knowledge|case|pattern",
      "relevance": 0.0,
      "applied_to": "string"
    }
  ],
  "optimization_plan": [
    {
      "action": "string",
      "target": "string",
      "expected_improvement": "string",
      "risk_level": "low|medium|high"
    }
  ],
  "verification_results": [
    {
      "test_case": "string",
      "result": "pass|fail",
      "details": "string"
    }
  ],
  "iteration_log": {
    "iteration_id": "string",
    "timestamp": "string",
    "changes": ["string"],
    "verified": true
  },
  "approval": {
    "security_review": "approved|rejected|pending",
    "review_notes": "string",
    "reviewer": "system",
    "review_timestamp": "string"
  }
}
```

## 五维度评估计算公式

| 维度 | 计算公式 | 说明 |
|------|----------|------|
| 准确率 | `正确数 / 总数 * 100%` | 数值越高越好 |
| 完成度 | `已完成步骤 / 总步骤 * 100%` | 反映任务完整度 |
| 时效性 | `min(预期耗时/实际耗时, 1.0) * 100%` | 效率指标 |
| 合规性 | `(处理数 - 拦截数) / 处理数 * 100%` | 安全指标 |
| 满意度 | `用户评分 / 满分 * 100%` | 主观评价 |

## 缺陷分类详解

### 1. 逻辑错误 (Logic Error)
- **识别特征**: 执行路径判断失误、条件分支错误
- **根因**: 规则理解偏差、边界条件遗漏
- **修复**: 补充规则、完善边界处理

### 2. 内容偏差 (Content Drift)
- **识别特征**: 输出偏离原始目标、信息不准确
- **根因**: Prompt 模糊、上下文丢失
- **修复**: 优化 Prompt、加强上下文锚定

### 3. 效率低下 (Low Efficiency)
- **识别特征**: 耗时超出预期、资源消耗过高
- **根因**: 未使用最优路径、重复计算
- **修复**: 算法优化、批量处理

### 4. 合规风险 (Compliance Risk)
- **识别特征**: 触发安全审核、拦截警告
- **根因**: 内容边界模糊、规则理解不足
- **修复**: 加强审核规则、完善内容过滤

### 5. 工具调用失误 (Tool Invocation Error)
- **识别特征**: API 调用失败、参数错误
- **根因**: 接口理解偏差、参数传递问题
- **修复**: 修正调用逻辑、完善错误处理

## 模拟验证检查清单

- [ ] 正常场景：标准输入 → 预期输出
- [ ] 边界场景：极限值 → 正确处理
- [ ] 异常场景：无效输入 → 优雅降级
- [ ] 安全场景：敏感输入 → 正确拦截
- [ ] 性能场景：大数据量 → 响应时间可接受

## 迭代日志格式

```json
{
  "iteration_id": "ITER-20260329-001",
  "timestamp": "2026-03-29T08:16:04Z",
  "trigger": "复盘报告触发",
  "changes": [
    {
      "type": "prompt_optimization|workflow_adjustment|rule_update",
      "before": "string",
      "after": "string",
      "reason": "string"
    }
  ],
  "verification": {
    "test_count": 3,
    "pass_count": 3,
    "performance_delta": "0%"
  },
  "approval": {
    "status": "approved",
    "approver": "security_system",
    "timestamp": "string"
  }
}
```

## 学习来源白名单

| 来源类型 | 示例 | 状态 |
|----------|------|------|
| MiniMax 官方知识库 | 平台文档、接口规范 | ✓ 允许 |
| 合规行业数据 | 公开财报、行业报告 | ✓ 允许 |
| 安全学术资料 | 论文、技术博客 | ✓ 允许 |
| 第三方未授权内容 | 爬取数据、版权内容 | ✗ 禁止 |
