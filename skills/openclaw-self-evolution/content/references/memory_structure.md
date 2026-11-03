# 记忆库结构参考

## 目录说明

```
/memories/
├── session_notes.md           # 当前会话记录
├── task_state.md             # 活跃任务状态
├── user_preferences/         # 用户偏好
│   ├── output_style.md       # 输出风格偏好
│   ├── common_formats.md     # 常用格式
│   └── focus_areas.md        # 关注领域
├── task_rules/               # 任务规则
│   └── active_rules.md       # 生效中的规则
├── error_log/                # 错误日志
│   └── analysis_YYYYMMDD.md  # 按日期归档
├── optimization_strategy.md   # 优化策略
└── evolution_reports/        # 进化报告
    └── report_YYYYMMDD.md
```

## 偏好记录示例

### 输出风格偏好 (output_style.md)

```markdown
# 用户输出风格偏好

## 偏好
- 语言：简体中文
- 格式：结构化Markdown
- 详细程度：简洁为主，按需扩展

## 禁忌
- 避免过度解释
- 不使用无意义的客套话
```

### 常用格式 (common_formats.md)

```markdown
# 常用格式规范

## 代码块
- 使用指定语言标识符
- 添加文件名注释

## 表格
- 使用标准Markdown表格
- 对齐清晰

## 列表
- 最多嵌套2层
- 使用有序/无序列表混合
```

## 错误日志格式

```markdown
# 错误分析 - YYYYMMDD

## 任务描述
[简述任务]

## 错误类型
- [ ] 理解偏差
- [ ] 执行错误
- [ ] 环境问题
- [ ] 其他

## 根本原因
[详细分析]

## 解决方案
[具体措施]

## 预防措施
[如何避免再次发生]
```

## 优化策略格式

```markdown
# 优化策略

## 已解决的问题
| 日期 | 问题 | 解决方案 | 状态 |
|------|------|----------|------|
| ...  | ...  | ...      | 完成 |

## 正在优化
| 问题 | 进展 | 目标 |
|------|------|------|
| ...  | ...  | ...  |
```
