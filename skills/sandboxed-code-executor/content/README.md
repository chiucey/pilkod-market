# Sandboxed Code Executor

安全执行智能体生成的代码或工具，提供自动测试与回滚能力。

## 目录结构

```
sandboxed-code-executor/
├── SKILL.md                    # 技能定义文档
├── scripts/
│   └── sandbox_executor.py    # 核心执行器实现
├── tests/
│   └── test_sandbox_executor.py # 测试套件
├── templates/
│   └── example_config.json     # 配置模板
└── README.md                   # 本文件
```

## 快速开始

### Python 代码执行

```python
from sandbox_executor import SandboxedExecutor

# 初始化执行器
executor = SandboxedExecutor(
    timeout=60,
    memory_limit_mb=512,
    rollback_enabled=True
)

# 执行代码
result = executor.execute(
    code="""
def add(a, b):
    return a + b

assert add(1, 2) == 3
print("Success!")
""",
    language="python"
)

print(f"Status: {result.status}")
print(f"Output: {result.stdout}")
```

### 命令行使用

```bash
# 从文件执行
python sandbox_executor.py -f script.py -l python -t 60

# 直接执行代码
python sandbox_executor.py -c "print('Hello!')" -l python
```

## 核心特性

### 安全隔离

- 资源限制（内存、CPU、时间）
- 安全模式检测（禁止 eval、exec 等）
- 网络访问控制
- 文件系统访问限制

### 自动测试

- 支持多种测试框架（pytest、jest 等）
- 覆盖率检测
- 失败重试机制

### 回滚机制

- 检查点保存与恢复
- 失败自动回滚
- 状态快照管理

## API 参考

### `SandboxedExecutor`

主执行器类。

#### 构造函数

```python
SandboxedExecutor(
    limits: SandboxLimits = None,      # 资源限制
    security_config: SecurityConfig = None,  # 安全配置
    rollback_enabled: bool = True     # 是否启用回滚
)
```

#### `execute()`

执行代码。

```python
result = executor.execute(
    code: str,                          # 要执行的代码
    language: str = "python",           # 语言
    tests: List[str] = None,            # 测试用例
    timeout: int = None,                # 超时时间
    rollback_on_failure: bool = True,   # 失败时回滚
    checkpoint_state: dict = None       # 检查点状态
)
```

#### `get_status()`

获取执行状态。

```python
result = executor.get_status(execution_id: str)
```

#### `get_logs()`

获取执行日志。

```python
logs = executor.get_logs(execution_id: str)
```

## 执行状态

| 状态 | 说明 |
|------|------|
| `pending` | 等待执行 |
| `validating` | 验证中 |
| `running` | 执行中 |
| `success` | 执行成功 |
| `failed` | 执行失败 |
| `timeout` | 执行超时 |
| `testing` | 测试中 |
| `passed` | 测试通过 |
| `rejected` | 被拒绝 |
| `rolling_back` | 回滚中 |
| `rolled_back` | 已回滚 |
| `mounted` | 已挂载 |

## 许可证

MIT License
