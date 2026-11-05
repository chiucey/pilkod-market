---
name: sandboxed-code-executor
description: 安全执行智能体生成的代码或工具，提供自动测试与回滚能力。当用户要求执行代码、验证生成代码、测试工具、回滚操作或需要隔离环境运行代码时使用。
---

# Sandboxed Code Executor (沙箱执行与验证技能)

## 1. 概述

**功能定位**：为 AI 智能体提供安全的代码/工具执行环境，支持自动测试与回滚机制。

**核心价值**：
- 在隔离环境中验证代码正确性与安全性
- 通过自动化测试确保代码质量
- 失败时自动回滚，保护主流程稳定
- 记录执行日志，支持问题诊断

## 2. 沙箱隔离机制

### 2.1 资源限制

```yaml
sandbox_limits:
  max_execution_time: 300  # 最大执行时间（秒）
  max_memory_mb: 512        # 最大内存限制（MB）
  max_disk_mb: 100          # 最大磁盘使用（MB）
  max_cpu_percent: 80       # 最大CPU使用率
  max_processes: 10         # 最大子进程数
  network_access: false     # 网络访问控制
```

### 2.2 安全策略

| 策略项 | 说明 | 默认值 |
|--------|------|--------|
| `allow_file_write` | 允许写入文件系统 | `false` |
| `allow_network` | 允许网络请求 | `false` |
| `allow_subprocess` | 允许创建子进程 | `false` |
| `allowed_dirs` | 允许访问的目录 | 仅临时目录 |
| `timeout` | 执行超时设置 | `60s` |

### 2.3 隔离技术

```
┌─────────────────────────────────────────────┐
│              Host System                      │
│  ┌─────────────────────────────────────┐     │
│  │     Sandbox Container               │     │
│  │  ┌─────────────────────────────┐   │     │
│  │  │     Code Execution Layer     │   │     │
│  │  │  - Resource Limits          │   │     │
│  │  │  - System Call Filtering    │   │     │
│  │  │  - Seccomp Profiles         │   │     │
│  │  └─────────────────────────────┘   │     │
│  └─────────────────────────────────────┘     │
└─────────────────────────────────────────────┘
```

## 3. 执行流程

### 3.1 标准执行流程

```
User Request
     │
     ▼
┌─────────────┐
│ Code Review │ ← 静态分析代码安全性
└─────────────┘
     │
     ▼
┌─────────────┐
│ Sandbox     │ ← 创建隔离执行环境
│ Init        │
└─────────────┘
     │
     ▼
┌─────────────┐
│ Execute     │ ← 在沙箱中执行代码
│ Code        │
└─────────────┘
     │
     ▼
┌─────────────┐
│ Run Tests   │ ← 执行自动化测试
└─────────────┘
     │
     ▼
┌─────────────┐     ┌─────────────┐
│ Pass?       │─No─▶│ Rollback    │ ← 失败则回滚
└─────────────┘     └─────────────┘
     │Yes
     ▼
┌─────────────┐
│ Mount to     │ ← 挂载到主流程
│ Main Flow   │
└─────────────┘
```

### 3.2 执行状态机

| 状态 | 说明 | 可转换状态 |
|------|------|------------|
| `pending` | 等待执行 | `validating` |
| `validating` | 静态验证中 | `running`, `rejected` |
| `running` | 执行中 | `success`, `failed`, `timeout` |
| `success` | 执行成功 | `testing` |
| `testing` | 测试中 | `passed`, `failed` |
| `passed` | 测试通过 | `mounted` |
| `failed` | 执行失败 | `rolling_back` |
| `timeout` | 执行超时 | `rolling_back` |
| `rolling_back` | 回滚中 | `rolled_back` |
| `mounted` | 已挂载到主流程 | - |

## 4. 自动化测试框架

### 4.1 测试类型

| 类型 | 说明 | 优先级 |
|------|------|--------|
| `unit_test` | 单元测试 | 必须 |
| `integration_test` | 集成测试 | 必须 |
| `security_scan` | 安全扫描 | 必须 |
| `performance_test` | 性能测试 | 可选 |
| `fuzz_test` | 模糊测试 | 可选 |

### 4.2 测试配置

```yaml
test_config:
  framework: jest|pytest|junit  # 根据语言选择
  coverage_threshold: 80        # 覆盖率阈值
  timeout: 120                  # 测试超时（秒）
  retry_count: 2                # 失败重试次数

test_suites:
  - name: "unit_tests"
    pattern: "**/*.test.{js,ts,py}"
    required: true

  - name: "integration_tests"
    pattern: "**/*.integration.{js,ts,py}"
    required: true
```

### 4.3 安全扫描规则

```yaml
security_rules:
  banned_patterns:
    - "eval\("           # 禁止 eval
    - "exec\("           # 禁止 exec
    - "subprocess"       # 禁止子进程（除非白名单）
    - "__import__"       # 禁止动态导入
    - "os.system"       # 禁止系统调用

  allowed_modules:
    python:
      - "json"
      - "re"
      - "math"
      - "datetime"
    javascript:
      - "fs"             # 只读模式
      - "path"
      - "crypto"
```

## 5. 回滚机制

### 5.1 回滚策略

| 策略 | 触发条件 | 说明 |
|------|----------|------|
| `immediate` | 任何测试失败 | 立即停止并回滚 |
| `graceful` | 关键测试失败 | 等待非关键测试完成后回滚 |
| `checkpoint` | 手动触发 | 在检查点保存状态 |

### 5.2 回滚实现

```python
class RollbackManager:
    def __init__(self):
        self.checkpoints = []
        self.backup_root = "/tmp/sandbox_backups"

    def create_checkpoint(self, name: str, state: dict) -> str:
        """创建检查点"""
        checkpoint_id = f"{name}_{int(time.time())}"
        checkpoint_path = f"{self.backup_root}/{checkpoint_id}"

        # 保存状态快照
        with open(f"{checkpoint_path}.json", "w") as f:
            json.dump(state, f)

        self.checkpoints.append(checkpoint_id)
        return checkpoint_id

    def rollback_to(self, checkpoint_id: str) -> bool:
        """回滚到指定检查点"""
        checkpoint_path = f"{self.backup_root}/{checkpoint_id}"

        if not os.path.exists(f"{checkpoint_path}.json"):
            return False

        with open(f"{checkpoint_path}.json", "r") as f:
            state = json.load(f)

        # 恢复状态
        self._restore_state(state)
        return True

    def cleanup_old_checkpoints(self, keep_last: int = 5):
        """清理旧检查点"""
        for checkpoint in self.checkpoints[:-keep_last]:
            shutil.rmtree(f"{self.backup_root}/{checkpoint}")
```

### 5.3 回滚触发条件

```yaml
rollback_triggers:
  - type: "test_failure"
    severity: "critical"
    action: "immediate"

  - type: "test_failure"
    severity: "warning"
    action: "graceful"

  - type: "timeout"
    action: "immediate"

  - type: "memory_exceeded"
    action: "immediate"

  - type: "security_violation"
    action: "immediate"
```

## 6. 日志与监控

### 6.1 日志结构

```json
{
  "execution_id": "exec_123456",
  "timestamp": "2026-03-29T18:46:01Z",
  "status": "success",
  "code_hash": "sha256:abc123...",
  "execution": {
    "start_time": "2026-03-29T18:46:01Z",
    "end_time": "2026-03-29T18:46:05Z",
    "duration_ms": 4000,
    "exit_code": 0
  },
  "tests": {
    "total": 10,
    "passed": 10,
    "failed": 0,
    "coverage": 85.5
  },
  "resources": {
    "memory_peak_mb": 128,
    "cpu_time_ms": 350,
    "io_read_bytes": 1024,
    "io_write_bytes": 512
  },
  "errors": []
}
```

### 6.2 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| `execution_time` | 执行耗时 | > 300s |
| `memory_usage` | 内存峰值 | > 512MB |
| `test_pass_rate` | 测试通过率 | < 100% |
| `security_issues` | 安全问题数 | > 0 |
| `rollback_count` | 回滚次数 | > 3/小时 |

## 7. API 接口

### 7.1 核心接口

```yaml
endpoints:
  - path: "/sandbox/execute"
    method: "POST"
    description: "提交代码执行任务"
    params:
      - name: "code"
        type: "string"
        required: true
      - name: "language"
        type: "enum"
        values: ["python", "javascript", "typescript", "bash"]
      - name: "tests"
        type: "array"
        description: "测试用例"
      - name: "timeout"
        type: "number"
        default: 60
      - name: "rollback_on_failure"
        type: "boolean"
        default: true

  - path: "/sandbox/status/{execution_id}"
    method: "GET"
    description: "获取执行状态"

  - path: "/sandbox/rollback/{execution_id}"
    method: "POST"
    description: "手动触发回滚"

  - path: "/sandbox/logs/{execution_id}"
    method: "GET"
    description: "获取执行日志"
```

### 7.2 请求示例

```bash
# 提交执行任务
curl -X POST http://localhost:8080/sandbox/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")",
    "language": "python",
    "timeout": 30,
    "rollback_on_failure": true
  }'

# 响应
{
  "execution_id": "exec_abc123",
  "status": "pending",
  "estimated_time": 5
}
```

## 8. 使用示例

### 8.1 Python 代码执行

```python
from sandbox_executor import SandboxedExecutor

executor = SandboxedExecutor(
    timeout=60,
    memory_limit_mb=512,
    allow_network=False
)

# 提交代码
result = executor.execute(
    code="""
def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    print("All tests passed!")

test_add()
""",
    language="python"
)

print(f"Status: {result.status}")
print(f"Output: {result.stdout}")
```

### 8.2 带回滚的执行

```python
executor = SandboxedExecutor(rollback_enabled=True)

# 创建检查点
checkpoint = executor.create_checkpoint("before_execution", {
    "db_state": get_database_state(),
    "file_state": get_file_state()
})

result = executor.execute(code=generated_code)

if result.status == "failed":
    executor.rollback_to(checkpoint)
    print("Rolled back successfully")
```

## 9. 最佳实践

### 9.1 代码验证

1. **静态分析优先**：执行前先进行静态代码分析
2. **安全扫描必须**：使用自动化工具扫描安全漏洞
3. **最小权限**：只授予完成任务所需的最小权限

### 9.2 测试策略

1. **测试驱动验证**：先生成测试用例，再执行代码
2. **覆盖率要求**：单元测试覆盖率不低于 80%
3. **边界测试**：重点测试边界条件和异常情况

### 9.3 回滚策略

1. **渐进式部署**：先在小范围验证，再扩大范围
2. **保持检查点**：关键操作前创建检查点
3. **快速恢复**：确保回滚时间在可接受范围内

## 10. 错误处理

### 10.1 错误类型

| 错误类型 | 说明 | 处理方式 |
|----------|------|----------|
| `SyntaxError` | 语法错误 | 拒绝执行 |
| `SecurityViolation` | 安全违规 | 立即停止，回滚 |
| `TimeoutError` | 执行超时 | 终止进程，回滚 |
| `TestFailure` | 测试失败 | 记录日志，回滚 |
| `ResourceExceeded` | 资源超限 | 终止进程，回滚 |

### 10.2 错误响应

```json
{
  "error": {
    "code": "SECURITY_VIOLATION",
    "message": "Code contains banned pattern: eval()",
    "details": {
      "line": 15,
      "pattern": "eval(",
      "severity": "critical"
    }
  },
  "action": "rollback",
  "timestamp": "2026-03-29T18:46:01Z"
}
```
