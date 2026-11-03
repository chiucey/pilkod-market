#!/usr/bin/env python3
"""
Sandbox Executor Test Suite
测试沙箱执行器的各项功能
"""

import pytest
import sys
import os

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sandbox_executor import (
    SandboxedExecutor,
    SecurityValidator,
    SecurityConfig,
    SandboxLimits,
    ExecutionStatus,
    CheckpointManager
)


class TestSecurityValidator:
    """安全验证器测试"""

    def setup_method(self):
        """测试前设置"""
        self.config = SecurityConfig()
        self.validator = SecurityValidator(self.config)

    def test_safe_code_passes(self):
        """安全代码应该通过验证"""
        safe_code = """
def add(a, b):
    return a + b

result = add(1, 2)
print(result)
"""
        is_safe, errors = self.validator.validate(safe_code)
        assert is_safe is True
        assert len(errors) == 0

    def test_eval_detected(self):
        """应该检测到 eval()"""
        unsafe_code = """
code = "print('hello')"
eval(code)
"""
        is_safe, errors = self.validator.validate(unsafe_code)
        assert is_safe is False
        assert any(e["pattern"] == "eval(" for e in errors)

    def test_exec_detected(self):
        """应该检测到 exec()"""
        unsafe_code = """
code = "print('hello')"
exec(code)
"""
        is_safe, errors = self.validator.validate(unsafe_code)
        assert is_safe is False
        assert any(e["pattern"] == "exec(" for e in errors)

    def test_subprocess_detected(self):
        """应该检测到 subprocess"""
        unsafe_code = """
import subprocess
subprocess.run(['ls'])
"""
        is_safe, errors = self.validator.validate(unsafe_code)
        assert is_safe is False
        assert any("subprocess" in e["pattern"] for e in errors)

    def test_dangerous_import_detected(self):
        """应该检测到危险导入"""
        unsafe_code = """
__import__('os')
"""
        is_safe, errors = self.validator.validate(unsafe_code)
        assert is_safe is False


class TestSandboxedExecutor:
    """沙箱执行器测试"""

    def setup_method(self):
        """测试前设置"""
        self.limits = SandboxLimits(max_execution_time=30, max_memory_mb=256)
        self.executor = SandboxedExecutor(
            limits=self.limits,
            rollback_enabled=False
        )

    def test_simple_python_execution(self):
        """测试简单 Python 代码执行"""
        code = """
result = 1 + 2
print(f"Result: {result}")
assert result == 3
"""
        result = self.executor.execute(code=code, language="python", timeout=10)

        assert result.status in [ExecutionStatus.SUCCESS, ExecutionStatus.PASSED]
        assert result.exit_code == 0
        assert "Result: 3" in result.stdout

    def test_function_execution(self):
        """测试函数执行"""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(f"5! = {factorial(5)}")
assert factorial(5) == 120
"""
        result = self.executor.execute(code=code, language="python")

        assert result.status == ExecutionStatus.SUCCESS
        assert result.exit_code == 0
        assert "5! = 120" in result.stdout

    def test_security_rejection(self):
        """测试安全拒绝"""
        unsafe_code = """
import os
os.system('ls')
"""
        result = self.executor.execute(code=unsafe_code, language="python")

        assert result.status == ExecutionStatus.REJECTED
        assert len(result.errors) > 0

    def test_timeout_handling(self):
        """测试超时处理"""
        code = """
import time
time.sleep(10)
"""
        result = self.executor.execute(code=code, language="python", timeout=2)

        assert result.status == ExecutionStatus.TIMEOUT

    def test_syntax_error_handling(self):
        """测试语法错误处理"""
        code = """
def broken(
    return None
"""
        result = self.executor.execute(code=code, language="python")

        assert result.status == ExecutionStatus.FAILED
        assert result.exit_code != 0

    def test_resource_tracking(self):
        """测试资源追踪"""
        code = """
data = [i for i in range(1000)]
print(f"Data length: {len(data)}")
"""
        result = self.executor.execute(code=code, language="python")

        assert result.status == ExecutionStatus.SUCCESS
        assert "resources" in result.__dict__
        assert result.duration_ms > 0


class TestCheckpointManager:
    """检查点管理器测试"""

    def setup_method(self):
        """测试前设置"""
        import tempfile
        self.backup_dir = tempfile.mkdtemp()
        self.manager = CheckpointManager(backup_root=self.backup_dir)

    def teardown_method(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.backup_dir, ignore_errors=True)

    def test_create_checkpoint(self):
        """测试创建检查点"""
        state = {"counter": 42, "name": "test"}
        checkpoint_id = self.manager.create_checkpoint("test", state)

        assert checkpoint_id.startswith("test_")
        assert checkpoint_id in self.manager.checkpoints

    def test_get_checkpoint(self):
        """测试获取检查点"""
        state = {"counter": 42, "items": [1, 2, 3]}
        checkpoint_id = self.manager.create_checkpoint("test", state)

        retrieved = self.manager.get_checkpoint(checkpoint_id)
        assert retrieved is not None
        assert retrieved["counter"] == 42
        assert retrieved["items"] == [1, 2, 3]

    def test_cleanup_old_checkpoints(self):
        """测试清理旧检查点"""
        # 创建多个检查点
        for i in range(10):
            self.manager.create_checkpoint("test", {"index": i})

        assert len(self.manager.checkpoints) == 10

        # 清理，保留最后 3 个
        self.manager.cleanup_old_checkpoints(keep_last=3)

        assert len(self.manager.checkpoints) == 3


class TestExecutionStatus:
    """执行状态测试"""

    def test_status_transitions(self):
        """测试状态转换"""
        pending = ExecutionStatus.PENDING
        assert pending.value == "pending"

        # 测试所有状态
        all_statuses = [
            ExecutionStatus.PENDING,
            ExecutionStatus.VALIDATING,
            ExecutionStatus.RUNNING,
            ExecutionStatus.SUCCESS,
            ExecutionStatus.FAILED,
            ExecutionStatus.TIMEOUT,
            ExecutionStatus.TESTING,
            ExecutionStatus.PASSED,
            ExecutionStatus.ROLLING_BACK,
            ExecutionStatus.ROLLED_BACK,
            ExecutionStatus.MOUNTED,
            ExecutionStatus.REJECTED
        ]

        assert len(all_statuses) == 12


class TestIntegration:
    """集成测试"""

    def test_full_execution_flow(self):
        """测试完整执行流程"""
        executor = SandboxedExecutor(rollback_enabled=False)

        code = """
def calculate_area(radius):
    pi = 3.14159
    return pi * radius * radius

# Test cases
assert abs(calculate_area(1) - 3.14159) < 0.0001
assert abs(calculate_area(0) - 0) < 0.0001
assert abs(calculate_area(2) - 12.56636) < 0.0001

print("All tests passed!")
area = calculate_area(5)
print(f"Area of radius 5: {area}")
"""
        result = executor.execute(
            code=code,
            language="python",
            timeout=30
        )

        # 验证执行结果
        assert result.status == ExecutionStatus.SUCCESS
        assert result.exit_code == 0
        assert "All tests passed!" in result.stdout
        assert "Area of radius 5:" in result.stdout

        # 验证日志记录
        logs = executor.get_logs(result.execution_id)
        assert logs["status"] == "success"
        assert "duration_ms" in logs


class TestEdgeCases:
    """边界情况测试"""

    def setup_method(self):
        """测试前设置"""
        self.executor = SandboxedExecutor(rollback_enabled=False)

    def test_empty_code(self):
        """测试空代码"""
        result = self.executor.execute(code="", language="python")
        assert result.status == ExecutionStatus.SUCCESS
        assert result.exit_code == 0

    def test_infinite_loop_protection(self):
        """测试无限循环保护"""
        code = """
while True:
    pass
"""
        result = self.executor.execute(code=code, language="python", timeout=2)
        assert result.status == ExecutionStatus.TIMEOUT

    def test_large_output(self):
        """测试大输出处理"""
        code = """
print("\\n".join([str(i) for i in range(10000)]))
"""
        result = self.executor.execute(code=code, language="python")
        # 应该正常完成或因输出过大而失败
        assert result.status in [
            ExecutionStatus.SUCCESS,
            ExecutionStatus.FAILED,
            ExecutionStatus.PASSED
        ]


def run_tests():
    """运行所有测试"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
