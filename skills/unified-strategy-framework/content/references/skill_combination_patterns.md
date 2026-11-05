# 技能组合策略详解

## 四大策略模式

### 1. 链式调用 (Chain Pattern)

**适用场景**：顺序依赖的多步骤任务

**示例流程**：UUID 改造完整流程
```
Step1: uuid-refactoring-skill (修改代码)
  ↓
Step2: doc-sync-skill (更新文档)
  ↓
Step3: test-generation-skill (生成测试)
  ↓
Step4: verify-and-report-skill (验证并报告)
```

**配置示例**：
```yaml
# .specify/strategies/uuid-migration.yaml
name: UUID 格式迁移
type: chain
skills:
  - name: uuid-refactoring-skill
    on_success: continue
    on_failure: abort
  - name: doc-sync-skill
    on_success: continue
    on_failure: notify
  - name: test-generation-skill
    on_success: continue
    on_failure: retry(2)
  - name: verify-and-report-skill
    on_success: archive
    on_failure: rollback
```

---

### 2. 并行执行 (Parallel Pattern)

**适用场景**：独立子任务可同时执行

**示例流程**：多模块测试
```
├─ test-module-A-skill
├─ test-module-B-skill  (同时执行)
├─ test-module-C-skill
└─ aggregate-results-skill (汇总)
```

---

### 3. 条件分支 (Conditional Pattern)

**适用场景**：根据情况选择不同路径

**示例流程**：部署策略
```
IF env == "development":
  → deploy-to-local-skill
ELSE IF env == "staging":
  → deploy-to-cloudbase-skill
ELSE IF env == "production":
  → deploy-with-rollback-skill
```

---

### 4. 观察者模式 (Observer Pattern)

**适用场景**：持续监控和响应

**示例流程**：系统健康检查
```
Monitor-Skill (每 30 分钟):
  - check_cpu_usage()
  - check_memory_usage()
  - check_error_rate()

ON threshold_exceeded:
  → alert-skill (发送告警)
  → auto-scale-skill (自动扩容)
```

---

## 策略选择矩阵

| 任务特征 | 推荐模式 | 示例 |
|---------|---------|------|
| 多步骤、强依赖 | 链式调用 | 数据迁移、版本升级 |
| 独立子任务 | 并行执行 | 批量测试、分布式部署 |
| 环境差异大 | 条件分支 | 多环境部署、灰度发布 |
| 实时监控 | 观察者模式 | 系统监控、自动告警 |
| 复杂决策 | 混合模式 | 故障自愈、智能调度 |
