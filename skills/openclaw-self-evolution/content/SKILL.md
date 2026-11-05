---
name: openclaw-self-evolution
description: OpenClaw自我进化引擎技能。当用户要求记录偏好、分析错误、迭代能力、同步规则、生成进化报告，或需要AI助手自动优化自身表现时使用。
---

# OpenClaw 自我进化引擎

## 核心能力

### 1. 记忆沉淀
- 自动记录用户偏好（输出风格、常用格式、关注领域）
- 记录任务规则与高频需求
- 跨对话持久化存储至 `/memories`

### 2. 错误复盘
- 任务执行失败/不符合预期时自动分析
- 提取失败原因并分类（理解偏差、执行错误、环境问题）
- 生成优化策略避免重复犯错

### 3. 能力迭代
- 根据用户需求自动补充领域知识
- 更新执行规则和最佳实践
- 无需用户反复调教

### 4. 规则同步
- 用户新增的任务要求自动同步
- 跨工作流全局生效
- 保持规则一致性

## 工作流程

### 记忆写入流程
1. 交互结束后提取：用户偏好、规则要求、执行问题
2. 写入持久化记忆库（使用 `create_memory` 工具）
3. 按主题分类存储：`/memories/user_preferences/`、`/memories/task_rules/`、`/memories/error_log/`

### 记忆调取流程
1. 接收新任务时首先调用 `view_memory(path="/memories")`
2. 加载相关历史规则与偏好
3. 优先按照用户习惯执行

### 错误复盘流程
1. 识别执行失败或不符合预期的情况
2. 分析根本原因并记录到 `/memories/error_log/`
3. 生成优化建议写入 `/memories/optimization_strategy.md`
4. 下次执行前检查并应用优化策略

### 进化报告生成
- 触发词："生成进化报告"、"本周进化总结"
- 汇总：新增能力、规则更新、待优化项
- 输出格式：Markdown 报告

## 存储结构

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

## 输出规则

- **静默执行**：优化过程后台执行，不干扰正常任务
- **主动告知条件**：
  - 规则发生重大更新
  - 需要用户确认优化方向
  - 用户明确要求反馈
- **保护原则**：严格遵循用户原始要求，不擅自修改核心规则

## 进化报告模板

```markdown
# 进化报告 - YYYY/MM/DD

## 本周优化
- 新增能力：xxx
- 规则更新：xxx
- 错误修复：xxx

## 待优化项
- xxx

## 用户反馈
- xxx

## 下周计划
- xxx
```

## 触发词示例

- "记录我的偏好：..."
- "分析上次任务失败的原因"
- "更新执行规则"
- "生成进化报告"
- "同步新规则到所有工作流"
