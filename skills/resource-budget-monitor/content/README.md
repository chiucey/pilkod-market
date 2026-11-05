# 资源预算监控技能

追踪 Token 消耗、API 调用次数、执行时间，设置阈值告警与限流。

## 功能特性

- **Token 消耗追踪** - 精确记录每次 API 调用的输入/输出 Token
- **API 调用计数** - 实时统计调用次数和频率
- **执行时间监控** - 记录每个任务的时间消耗
- **阈值告警机制** - 支持信息/警告/严重三级告警
- **限流保护** - 自动限流防止资源耗尽
- **预算报告** - 生成 Markdown/JSON 格式的统计报告

## 快速开始

```python
from resource_monitor import create_monitor

# 创建监控器
monitor = create_monitor(data_dir="data/budget_tracking")

# 开始监控会话
session = monitor.start_session("my_task")

# 记录资源消耗
session.record_api_call(
    operation_type="code_generation",
    token_input=1500,
    token_output=3000,
    execution_time_ms=2500
)

# 获取当前状态
status = session.get_status()
print(f"Token 消耗: {status['daily_token_total']}")

# 检查限流
if session.should_rate_limit():
    print("触发限流")

# 结束会话
stats = session.end_session()
```

## 配置阈值

```python
from resource_monitor import ThresholdConfig, BudgetMonitor

thresholds = ThresholdConfig(
    token_daily_soft=30000,
    token_daily_hard=50000,
    api_rpm_hard=60,
    execution_time_ms_hard=60000
)

monitor = BudgetMonitor(
    data_dir="data/budget_tracking",
    thresholds=thresholds
)
```

## 生成报告

```python
# 生成日报
report = monitor.generate_report(period="daily", format="markdown")
print(report)

# 保存报告
monitor.save_report(report, "reports/budget_report.md")
```

## 文件结构

```
resource-budget-monitor/
├── SKILL.md              # 技能定义文件
├── resource_monitor.py  # 核心监控模块
├── config.json          # 配置文件
├── example_usage.py     # 使用示例
└── requirements.txt    # 依赖声明
```

## 告警级别

| 级别 | 触发条件 | 响应动作 |
|------|----------|----------|
| INFO | 达到软限制的 80% | 记录通知 |
| WARNING | 达到软限制 | 限流 + 通知 |
| CRITICAL | 达到硬限制 | 硬停止 + 通知 |

## 与其他技能集成

### 与自我成长技能集成

```python
# 在自我成长循环中添加监控检查点
while should_continue:
    status = session.get_status()
    if status['daily_token_total'] >= BUDGET_LIMIT:
        break  # 预算耗尽，停止循环
    # 执行成长迭代
```

### 与限流技能集成

资源预算监控技能可与限流技能配合使用，实现更精细的资源控制。

## 作者

MiniMax Agent
