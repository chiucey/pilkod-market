# 因果推理引擎详解

## 因果关系图谱

```
[代码修改] --> [影响范围分析]
                    |
    +---------------+---------------+
    |               |               |
[更新文档]    [数据迁移]      [更新API文档]
    |               |               |
    +---------------+---------------+
                    |
              [运行测试]
                    |
           +--------+--------+
           |                 |
        [通过]           [失败]
           |                 |
    [归档并通知]      [回滚并告警]
```

## 推理规则库

### 规则 1: 文档同步规则

```javascript
{
  "trigger": "code_change",
  "condition": "file_path matches /(core|routes|middleware)/",
  "actions": [
    {"type": "search", "target": "*.md", "keywords": ["function_name"]},
    {"type": "update", "target": "README.md"},
    {"type": "notify", "recipient": "author"}
  ]
}
```

### 规则 2: 测试覆盖规则

```javascript
{
  "trigger": "new_feature",
  "condition": "PR merged to main",
  "actions": [
    {"type": "generate_tests", "coverage_target": "80%"},
    {"type": "run_tests", "suite": "integration"},
    {"type": "block_merge", "if": "tests_fail"}
  ]
}
```

### 规则 3: 数据迁移规则

```javascript
{
  "trigger": "schema_change",
  "condition": "ID format changed",
  "actions": [
    {"type": "backup_db"},
    {"type": "migrate_data", "strategy": "dual_write"},
    {"type": "verify_integrity"},
    {"type": "rollback_plan", "on": "verification_fail"}
  ]
}
```

## 决策树

```
用户请求
  ↓
[意图识别]
  ├─ 代码开发 → 调用 Spec-Kit → 生成任务列表 → 分派 Skills
  ├─ 问题排查 → 搜索 Memory → 匹配历史案例 → 执行解决方案
  ├─ 数据分析 → 调用 MCP → 查询数据 → 生成报告
  └─ 部署运维 → 检查环境 → 选择策略 → 执行部署
```

## MCP 服务能力

### Yunxiao MCP
- list_change_requests() - 查询合并请求
- create_work_item() - 创建工作项
- search_workitems() - 搜索工作项
- list_pipelines() - 查询流水线
- create_pipeline_run() - 运行流水线

### Local Server MCP
- query_local_db() - 查询本地数据库
- execute_sql() - 执行 SQL
- backup_data() - 备份数据
- restore_data() - 恢复数据

### Memory MCP
- search_memory(query, category) - 搜索记忆
- update_memory(action, content) - 更新记忆
- list_memories(category) - 列出记忆
