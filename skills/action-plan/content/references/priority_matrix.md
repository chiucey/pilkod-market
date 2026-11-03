# 优先级矩阵与任务管理

## 优先级定义

### Eisenhower 矩阵

| | 紧急 | 不紧急 |
|---|---|---|
| **重要** | P0: 立即做 | P1: 计划做 |
| **不重要** | P2: 委托做 | P3: 删除做 |

### 优先级标准

| 优先级 | 定义 | 时间要求 | 示例 |
|--------|------|----------|------|
| **P0** | 必须完成，关乎核心目标 | 立即/当天 | 紧急Bug，阻塞问题 |
| **P1** | 应该完成，重要但不紧急 | 1-3天 | 功能开发，文档编写 |
| **P2** | 可以完成，有余力时处理 | 1周内 | 优化改进，学习研究 |
| **P3** | 暂不处理，评估后决定 | 待定 | 低频需求，探索性任务 |

## 升级规则

```javascript
const escalationRules = {
  p0: {
    overdue_1day: "notify_manager",
    overdue_2days: "auto_schedule_overtime",
    overdue_3days: "block_new_tasks"
  },
  p1: {
    overdue_3days: "notify_manager",
    overdue_7days: "escalate_to_lead"
  },
  p2: {
    overdue_1week: "reminder",
    overdue_2weeks: "review_or_close"
  }
};
```

## 任务拆解模板

### 规范文档模板

```markdown
# 项目名称

## 目标
[清晰、可衡量的目标]

## 当前状态
- 已完成：[列出已完成的部分]
- 进行中：[列出进行中的部分]
- 待完成：[列出待完成的部分]

## 验收标准
1. [具体可验证的标准]
2. [具体可验证的标准]

## 里程碑
- [日期]: [里程碑描述]
- [日期]: [里程碑描述]
```

### 任务清单模板

```yaml
# .specify/project/tasks.yaml

tasks:
  - id: T1
    name: 任务名称
    description: 详细描述
    duration: 预估时长
    skill: 对应技能
    output: 产出物路径
    priority: P0/P1/P2/P3
    dependencies: []

quality_gates:
  - task: T1
    check: code_review
    criteria: ["标准1", "标准2"]

notifications:
  - task: T1
    on_complete: email_to_manager
```

## 进度追踪

### 状态定义

| 状态 | 说明 | 颜色 |
|------|------|------|
| PENDING | 待开始 | 灰色 |
| IN_PROGRESS | 进行中 | 蓝色 |
| BLOCKED | 被阻塞 | 红色 |
| IN_REVIEW | 审核中 | 黄色 |
| COMPLETED | 已完成 | 绿色 |

### 每日站会议程

```
1. 昨日完成了什么？
2. 今日计划做什么？
3. 有什么障碍？
4. 需要什么帮助？
```

### 周报模板

```markdown
## 本周总结

### 完成项
- [ ] 任务1
- [ ] 任务2

### 进行中
- [ ] 任务3（60%）

### 变更项
- 任务4：范围调整（新增XXX）

### 下周计划
- [ ] 任务5
- [ ] 任务6

### 风险与问题
- 风险1：描述 → 应对措施
```

## 效果评估

### 核心指标

| 指标 | 计算方式 | 目标 |
|------|----------|------|
| 完成率 | 完成数/总数 | >90% |
| 准时率 | 准时完成数/总数 | >85% |
| 阻塞率 | 阻塞任务数/总数 | <10% |
| 变更率 | 变更任务数/总数 | <15% |

### 趋势分析

```
Week 1: 完成任务 5/10 (50%)
Week 2: 完成任务 7/10 (70%) ↑
Week 3: 完成任务 9/10 (90%) ↑
Week 4: 完成任务 10/10 (100%) ✓
```
