---
name: resource-budget-monitor
description: 追踪每次成长的 Token 消耗、API 调用次数、执行时间，设置阈值告警与限流。防止智能体陷入"无限自我优化"的死循环，确保成长过程在经济性与性能上可控。触发关键词：资源监控、预算管理、Token消耗、API限流、成本控制、执行时间、资源告警、阈值设置、限流保护。
---

# 资源预算监控技能

## 概述

资源预算监控技能是智能体自我成长系统的核心安全组件，负责实时追踪和管理智能体运行过程中的资源消耗。通过设置预算阈值和自动限流机制，该技能有效防止智能体陷入"无限自我优化"的资源消耗陷阱，确保成长过程在经济性和性能上保持可控。

## 核心功能

### 1. Token 消耗追踪

该功能模块负责精确记录每次 API 调用的 token 使用量，包括输入 token 和输出 token 的详细分类。通过建立历史消耗数据库，技能能够分析 token 使用的趋势和模式，为后续的资源规划提供数据支撑。当检测到单次调用的 token 消耗异常增加时，系统会立即触发预警机制，通知相关模块采取相应的控制措施。

Token 追踪采用增量记录的方式，每次 API 调用后自动累加到总消耗中。系统会保留最近 N 次调用的详细记录（默认 N=100），便于进行趋势分析和异常检测。Token 消耗数据还会按日、周、月三个维度进行聚合统计，帮助用户全面了解资源消耗的时空分布规律。

### 2. API 调用计数与频率监控

API 调用计数模块实时统计智能体的 API 调用总量，并计算每分钟、每小时、每天的调用频率。当调用频率超过预设阈值时，系统会触发限流机制，通过引入延迟或返回错误来控制调用速率。这种主动的频率控制机制能够有效防止因程序错误或恶意攻击导致的 API 调用失控。

频率监控采用滑动窗口算法，能够准确反映最近一段时间内的调用密度。滑动窗口的大小可以根据实际需求进行配置，默认设置为 5 分钟。窗口内的调用次数超过阈值时，系统会进入限流状态，在冷却期结束后自动恢复正常调用。这种设计既保证了资源控制的实时性，又避免了因短暂突增导致的误判。

### 3. 执行时间监控

执行时间监控模块记录每个任务从开始到结束的完整时间消耗，包括等待时间、处理时间和总执行时间。通过分析执行时间的分布特征，系统能够识别性能瓶颈和潜在的问题。当某个任务的执行时间超过历史平均值的 2 个标准差时，会被标记为异常任务，并生成详细的诊断报告。

执行时间数据还会与其他资源指标进行关联分析。例如，当 Token 消耗较高且执行时间较长时，系统会优先检查是否存在效率低下的处理逻辑。这种关联分析能够更准确地定位资源浪费的根源，为优化决策提供有力支持。

### 4. 阈值告警机制

阈值告警是资源预算监控的核心防护机制。系统支持多级别的告警设置，包括信息级、警告级和紧急级三个层次。每个监控指标都可以独立配置阈值，当资源消耗达到相应级别时触发对应级别的告警。

告警的触发逻辑采用比较运算符和逻辑组合的方式，支持"大于"、"小于"、"区间"等多种条件。用户可以根据业务需求灵活配置告警规则，例如"单日 Token 消耗超过 10000 或执行时间超过 60 秒"。告警触发后，系统会执行预设的响应动作，包括记录日志、发送通知、暂停操作等。

### 5. 限流保护机制

当资源消耗持续超过安全阈值时，限流保护机制会自动启动，防止情况进一步恶化。限流采用渐进式策略，初期仅增加调用间隔，中期减少并发数量，后期完全暂停非必要操作。这种渐进式的限流设计能够在保护系统安全的同时，最大程度地减少对正常业务的影响。

限流状态解除后，系统采用渐进恢复策略，逐步恢复正常资源使用。这种设计避免了限流解除过快导致的二次冲击，确保系统在恢复过程中的稳定性。恢复速度可以根据实际需求进行配置，默认设置为每分钟恢复 10% 的资源配额。

### 6. 预算统计报告

预算统计报告模块定期生成资源使用的详细报告，包括消耗趋势图、异常事件列表、优化建议等内容。报告支持多种格式输出，包括 JSON、Markdown 和 HTML 格式。用户可以根据需要选择不同的输出格式，便于进行进一步的分析和归档。

报告生成支持自动化调度，用户可以配置每日、每周或每月自动生成报告。自动生成的报告会通过配置的渠道进行分发，确保相关人员能够及时了解资源使用情况。报告内容还包括与历史同期的对比分析，帮助用户评估资源使用的效率变化。

## 数据结构

### 资源记录模型

```json
{
  "session_id": "唯一会话标识",
  "timestamp": "ISO8601 时间戳",
  "operation_type": "操作类型",
  "token_input": 1234,
  "token_output": 5678,
  "token_total": 6912,
  "api_calls": 1,
  "execution_time_ms": 1234,
  "wait_time_ms": 500,
  "metadata": {}
}
```

### 阈值配置模型

```json
{
  "thresholds": {
    "token": {
      "daily_limit": 50000,
      "per_call_warning": 8000,
      "per_call_critical": 10000
    },
    "api_calls": {
      "per_minute_limit": 60,
      "per_hour_limit": 2000,
      "per_day_limit": 10000
    },
    "execution_time": {
      "per_task_warning_ms": 30000,
      "per_task_critical_ms": 60000,
      "daily_total_warning_ms": 3600000,
      "daily_total_critical_ms": 7200000
    }
  },
  "alert_levels": {
    "info": "notification",
    "warning": "notification + rate_limit",
    "critical": "notification + hard_stop"
  }
}
```

## 使用方法

### 初始化监控会话

```python
from resource_monitor import BudgetMonitor

monitor = BudgetMonitor(
    config_path="config/budget_config.json",
    data_dir="data/budget_tracking"
)

session = monitor.start_session("skill_improvement_v1")
```

### 记录资源消耗

```python
# 记录 API 调用
session.record_api_call(
    operation_type="code_generation",
    token_input=1500,
    token_output=3000,
    execution_time_ms=2500
)

# 批量记录
session.record_batch({
    "operation_type": "analysis",
    "token_input": 2000,
    "token_output": 1500,
    "execution_time_ms": 1800
})
```

### 查询资源状态

```python
# 获取当前状态
status = session.get_status()
print(f"今日 Token 消耗: {status['daily_token_total']}")
print(f"当前 API 频率: {status['current_rpm']}")

# 检查是否需要限流
if session.should_rate_limit():
    wait_time = session.get_rate_limit_wait()
    print(f"需要等待 {wait_time} 秒")
```

### 生成报告

```python
# 生成日报
report = monitor.generate_report(
    period="daily",
    format="markdown"
)
print(report)

# 保存到文件
monitor.save_report(
    report=report,
    output_path="reports/budget_2024_01_15.md"
)
```

## 集成指南

### 与自我成长技能集成

资源预算监控技能可以与自我成长技能无缝集成，实现资源消耗的自动控制。在自我成长技能中添加监控检查点，确保每次优化迭代都在预算范围内进行。当资源消耗接近阈值时，自我成长技能会自动暂停或调整优化策略。

### 与限流技能集成

与限流技能集成后，系统可以实现更精细的资源控制。资源预算监控提供资源状态的实时数据，限流技能根据这些数据进行智能决策。这种组合能够在保证系统安全的同时，最大化资源利用效率。

### 与告警系统集成

告警信息可以发送到多种渠道，包括邮件、钉钉、企业微信等。通过配置 webhooks，系统可以将告警实时推送到指定的告警平台。告警内容包含详细的资源消耗信息和问题诊断，便于快速响应和处理。

## 配置示例

### 基础配置

```json
{
  "monitoring": {
    "enabled": true,
    "session_timeout_minutes": 60
  },
  "thresholds": {
    "token_daily_soft": 30000,
    "token_daily_hard": 50000,
    "api_rpm_soft": 50,
    "api_rpm_hard": 60,
    "execution_time_ms_soft": 30000,
    "execution_time_ms_hard": 60000
  },
  "rate_limiting": {
    "enabled": true,
    "gradual_recovery": true,
    "recovery_rate_per_minute": 0.1
  },
  "reporting": {
    "auto_generate": true,
    "schedule": "0 9 * * *",
    "format": "markdown"
  }
}
```

## 安全考虑

资源预算监控技能本身包含多重安全机制。阈值配置采用权限分级管理，敏感操作需要二次确认。历史数据定期归档和清理，防止数据膨胀影响系统性能。所有操作记录审计日志，便于事后追溯和问题诊断。

## 更新日志

### v1.0.0 (2024-01-15)

- 初始版本发布
- 支持 Token 消耗追踪
- 支持 API 调用计数
- 支持执行时间监控
- 实现阈值告警机制
- 实现限流保护机制
- 支持报告生成

## 作者

MiniMax Agent
