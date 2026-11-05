# 测试失败根因分析模式参考

## 常见根因类型及特征

### 1. 环境问题

| 根因类型 | 错误特征 | 诊断关键词 |
|---------|---------|-----------|
| 配置缺失 | ImportError, ModuleNotFoundError | 环境变量, config, .env |
| 版本冲突 | ImportError, AttributeError | 版本号, incompatib |
| 网络问题 | TimeoutError, ConnectionRefusedError | timeout, connection, DNS |
| 资源限制 | MemoryError, OutOfMemoryError | memory, heap, resource |
| 权限问题 | PermissionError, AccessDeniedError | permission, denied, access |

### 2. 数据问题

| 根因类型 | 错误特征 | 诊断关键词 |
|---------|---------|-----------|
| 空值处理 | NullPointerError, NoneType | None, null, undefined |
| 边界条件 | IndexError, ValueError | index, range, bounds |
| 数据格式 | JSONDecodeError, ParseError | JSON, parse, format |
| 测试数据污染 | 间歇性失败, 随机失败 | state, pollution, isolation |
| 时序依赖 | 特定顺序失败 | race, concurrent, order |

### 3. 代码缺陷

| 根因类型 | 错误特征 | 诊断关键词 |
|---------|---------|-----------|
| 空指针引用 | NullPointerError, AttributeError | None, null, undefined |
| 数组越界 | IndexError, OutOfRange | index, length, size |
| 类型错误 | TypeError, InvalidType | type, expected, got |
| 资源泄漏 | 文件句柄, 数据库连接 | resource, leak, close |
| 并发问题 | 死锁, 竞态条件 | deadlock, race, concurrent |

### 4. 测试设计问题

| 根因类型 | 错误特征 | 诊断关键词 |
|---------|---------|-----------|
| 测试依赖 | 前置测试失败导致连锁失败 | dependency, order, sequence |
| 测试隔离不足 | 状态污染, 共享状态 | state, pollution, shared |
| 异步问题 | 超时, 竞态条件 | async, await, promise |
| Mock 配置错误 | UnexpectedCall, 假阳性 | mock, stub, spy |
| 断言过于严格 | 数值误差, 浮点比较 | precision, floating, delta |

## 修复方案模板

### 模板 1：Fixture 清理模式

```python
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """自动清理测试环境"""
    # 准备阶段
    setup_test_environment()

    yield  # 测试执行

    # 清理阶段
    teardown_test_environment()
    reset_database_connections()
    clear_temp_files()
```

### 模板 2：重试机制模式

```python
import time
from functools import wraps

def retry_on_failure(max_attempts=3, delay=1):
    """测试重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (TimeoutError, ConnectionError) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (attempt + 1))
            raise last_exception
        return wrapper
    return decorator
```

### 模板 3：条件跳过模式

```python
import pytest

def requires_external_service():
    """检查外部服务是否可用"""
    return pytest.mark.skipif(
        not is_service_available("payment-gateway"),
        reason="External service unavailable"
    )

@requires_external_service()
def test_payment_processing():
    # 测试支付处理
    pass
```

### 模板 4：参数化边界测试

```python
@pytest.mark.parametrize("input_value,expected", [
    (0, "zero"),
    (1, "one"),
    (-1, "negative"),
    (999999, "large"),
    (None, "null"),
])
def test_number_conversion(input_value, expected):
    assert convert_number_to_word(input_value) == expected
```

### 模板 5：隔离数据库连接

```python
@pytest.fixture
def isolated_db():
    """提供隔离的数据库连接"""
    db = create_fresh_database()
    connection = db.connect()
    transaction = connection.begin()

    yield connection

    transaction.rollback()
    connection.close()
    db.destroy()
```

## 错误分组算法

### 相似度计算公式

```
Similarity(A, B) = α × StackMatch(A, B) + β × MessageMatch(A, B) + γ × LocationMatch(A, B)

其中：
- StackMatch: 堆栈跟踪匹配度（权重 0.5）
- MessageMatch: 错误消息匹配度（权重 0.3）
- LocationMatch: 错误位置匹配度（权重 0.2）
```

### 分组阈值

| 相似度范围 | 分组决策 |
|----------|---------|
| ≥ 0.8 | 强关联，必需同组 |
| 0.6 ~ 0.8 | 中等关联，建议同组 |
| 0.4 ~ 0.6 | 弱关联，可选同组 |
| < 0.4 | 无关联，独立分析 |

## 优先级计算

```python
def calculate_priority(group):
    # 影响测试数（30%）
    impact_score = len(group.tests) / total_tests * 100 * 0.3

    # 业务重要性（25%）
    importance_score = get_module_importance(group.module) * 25

    # 修复复杂度（25%）- 越简单分数越高
    complexity_score = (10 - estimate_fix_complexity(group)) / 10 * 25

    # 根因确定性（20%）
    certainty_score = group.confidence * 20

    return impact_score + importance_score + complexity_score + certainty_score
```

## 诊断检查清单

### 环境问题诊断
- [ ] 检查环境变量配置
- [ ] 验证依赖版本兼容性
- [ ] 测试网络连通性
- [ ] 检查系统资源限制
- [ ] 验证文件权限

### 数据问题诊断
- [ ] 检查空值处理逻辑
- [ ] 验证边界条件测试
- [ ] 检查数据格式转换
- [ ] 分析测试数据状态
- [ ] 检查时序依赖

### 代码缺陷诊断
- [ ] 分析堆栈跟踪
- [ ] 检查资源管理
- [ ] 验证并发安全
- [ ] 检查错误处理
- [ ] 分析内存使用

### 测试设计诊断
- [ ] 检查测试依赖关系
- [ ] 验证测试隔离性
- [ ] 分析异步处理
- [ ] 检查 Mock 配置
- [ ] 验证断言精度
