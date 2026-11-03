# 工作流监控和日志系统使用指南

## 目录
- [概览](#概览)
- [核心功能](#核心功能)
- [日志系统](#日志系统)
- [监控工具](#监控工具)
- [使用示例](#使用示例)
- [最佳实践](#最佳实践)

## 概览

工作流监控和日志系统提供了完整的工作流执行追踪、性能分析和告警功能。

**核心特性：**
- 详细的日志记录
- 实时状态监控
- 性能统计分析
- 异常检测和告警
- 历史数据查询

## 核心功能

### 1. 日志记录（WorkflowLogger）
- 记录工作流执行的每一步
- 会话管理和持久化
- 历史日志查询
- 统计信息生成

### 2. 工作流监控（WorkflowMonitor）
- 实时监控工作流状态
- 性能指标统计
- 超时检测和告警
- 异常情况检测

## 日志系统

### 初始化日志记录器

```python
from scripts.workflow_logger import WorkflowLogger

# 初始化日志记录器
logger = WorkflowLogger(log_dir="./logs/workflows")
```

### 记录工作流

```python
# 记录工作流开始
logger.log_workflow_start(
    workflow_type="document-understanding",
    input_data={"image_path": "document.png"},
    metadata={"user_id": "123"}
)

# 记录步骤
logger.log_step(
    step_name="ocr",
    step_data={"text_count": 100},
    success=True
)

# 记录工作流结束
logger.log_workflow_end(
    result={"summary": "..."},
    success=True
)

# 保存会话
log_file = logger.save_session()
print(f"日志已保存: {log_file}")
```

### 查询日志

```python
# 查看最近会话
sessions = logger.list_sessions(limit=10)
for session in sessions:
    print(f"{session['session_id']}: {session['workflow_count']} 个工作流")

# 查看会话详情
session = logger.get_session_logs("session_20240101_120000")
print(session)

# 查看工作流详情
workflow = logger.get_workflow_logs("workflow_0")
print(workflow)

# 获取统计信息
stats = logger.get_statistics()
print(stats)
```

### 清理旧日志

```python
# 清理 30 天前的日志
logger.clear_old_logs(days=30)
```

## 监控工具

### 初始化监控器

```python
from scripts.workflow_monitor import WorkflowMonitor
from scripts.workflow_logger import WorkflowLogger

# 初始化日志记录器
logger = WorkflowLogger()

# 初始化监控器
monitor = WorkflowMonitor(logger=logger, alert_threshold=60)
```

### 实时监控

```python
# 监控工作流执行
monitor.monitor_workflow(
    workflow_id="workflow_0",
    interval=5  # 每 5 秒检查一次
)
```

### 获取性能指标

```python
# 获取所有工作流的性能指标
metrics = monitor.get_performance_metrics()
print(f"平均执行时间: {metrics['average_duration']:.2f} 秒")

# 获取特定类型工作流的性能指标
metrics = monitor.get_performance_metrics(workflow_type="document-understanding")
```

### 生成监控报告

```python
# 生成监控报告
report = monitor.generate_report(output_path="./monitoring_report.txt")
print(report)
```

### 检测异常

```python
# 检测异常情况
anomalies = monitor.check_anomalies("document-understanding")
for anomaly in anomalies:
    print(f"工作流 {anomaly['workflow_id']} 执行时间异常")
    print(f"  实际时间: {anomaly['duration']:.2f} 秒")
    print(f"  预期时间: {anomaly['expected_duration']:.2f} 秒")
    print(f"  偏差: {anomaly['deviation']:.2f}x")
```

## 使用示例

### 命令行使用

#### 日志系统

```bash
# 查看最近会话
python workflow_logger.py list-sessions

# 查看会话详情
python workflow_logger.py show-session session_20240101_120000

# 查看工作流详情
python workflow_logger.py show-workflow workflow_0

# 查看统计信息
python workflow_logger.py statistics

# 清理旧日志
python workflow_logger.py clean --days 30
```

#### 监控工具

```bash
# 监控工作流
python workflow_monitor.py monitor workflow_0 --interval 5

# 生成监控报告
python workflow_monitor.py report --output report.txt

# 获取性能指标
python workflow_monitor.py metrics --workflow-type document-understanding

# 检测异常
python workflow_monitor.py anomalies --workflow-type document-understanding
```

### API 使用

#### 在工作流中集成日志

```python
from scripts.workflow_engine import WorkflowEngine
from scripts.workflow_logger import WorkflowLogger

# 初始化工作流引擎（启用日志）
engine = WorkflowEngine(enable_logging=True)

# 执行工作流（自动记录日志）
result = engine.run_document_understanding_workflow(
    "document.png",
    questions=["发票金额是多少？"]
)

# 查看日志
sessions = engine.logger.list_sessions()
```

#### 注册告警回调

```python
def alert_callback(alert):
    """告警回调函数"""
    print(f"⚠️ 告警: {alert['message']}")
    # 发送邮件、短信等

# 注册回调
monitor.register_callback(alert_callback)

# 开始监控
monitor.monitor_workflow("workflow_0")
```

## 最佳实践

### 1. 日志管理
- 定期清理旧日志，避免占用过多磁盘空间
- 使用合理的日志目录结构
- 为重要工作流启用详细日志

### 2. 性能监控
- 设置合理的超时阈值
- 定期查看性能指标
- 及时发现和处理异常

### 3. 告警配置
- 注册合适的告警回调
- 设置合理的告警阈值
- 建立告警处理流程

### 4. 数据分析
- 定期分析工作流统计数据
- 识别性能瓶颈
- 优化工作流程

### 5. 故障排查
- 使用日志追踪问题
- 查看历史执行记录
- 分析异常情况

## 常见问题

### Q: 日志文件太大怎么办？
A: 定期运行 `workflow_logger.py clean --days 30` 清理旧日志。

### Q: 如何禁用日志记录？
A: 初始化工作流引擎时设置 `enable_logging=False`。

### Q: 监控会影响工作流性能吗？
A: 监控的开销很小，基本不影响性能。

### Q: 如何自定义告警规则？
A: 修改 `WorkflowMonitor` 中的 `check_workflow_timeout` 方法或注册自定义回调。

### Q: 日志数据安全吗？
A: 日志保存在本地文件中，建议定期备份重要日志。

## 相关资源

- [工作流引擎指南](workflow-guide.md)
- [文档分类器指南](document-classifier-guide.md)
- [OCR 服务指南](ocr-service.md)
