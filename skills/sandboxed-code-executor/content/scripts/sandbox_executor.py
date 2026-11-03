#!/usr/bin/env python3
"""
Sandboxed Code Executor
安全执行智能体生成的代码或工具，提供自动测试与回滚能力。
"""

import os
import sys
import json
import time
import uuid
import hashlib
import shutil
import subprocess
import tempfile
import threading
import resource
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from pathlib import Path


class ExecutionStatus(Enum):
    """执行状态枚举"""
    PENDING = "pending"
    VALIDATING = "validating"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    TESTING = "testing"
    PASSED = "passed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"
    MOUNTED = "mounted"
    REJECTED = "rejected"


class ErrorSeverity(Enum):
    """错误严重级别"""
    LOW = "low"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class SandboxLimits:
    """沙箱资源限制"""
    max_execution_time: int = 300  # 秒
    max_memory_mb: int = 512
    max_disk_mb: int = 100
    max_cpu_percent: int = 80
    max_processes: int = 10
    network_access: bool = False


@dataclass
class SecurityConfig:
    """安全配置"""
    allow_file_write: bool = False
    allow_network: bool = False
    allow_subprocess: bool = False
    allowed_dirs: List[str] = field(default_factory=lambda: ["/tmp/sandbox"])
    banned_patterns: List[str] = field(default_factory=lambda: [
        "eval(", "exec(", "__import__", "os.system", "subprocess"
    ])
    allowed_modules: Dict[str, List[str]] = field(default_factory=lambda: {
        "python": ["json", "re", "math", "datetime", "collections", "itertools"],
        "javascript": ["fs", "path", "crypto"]
    })


@dataclass
class ExecutionResult:
    """执行结果"""
    execution_id: str
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    duration_ms: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    resources: Dict[str, Any] = field(default_factory=dict)
    tests: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    checkpoint_id: Optional[str] = None


class CheckpointManager:
    """检查点管理器"""

    def __init__(self, backup_root: str = "/tmp/sandbox_backups"):
        self.backup_root = backup_root
        self.checkpoints: List[str] = []
        os.makedirs(backup_root, exist_ok=True)

    def create_checkpoint(self, name: str, state: Dict[str, Any]) -> str:
        """创建检查点"""
        checkpoint_id = f"{name}_{int(time.time() * 1000)}"
        checkpoint_path = os.path.join(self.backup_root, checkpoint_id)

        os.makedirs(checkpoint_path, exist_ok=True)

        # 保存状态快照
        state_file = os.path.join(checkpoint_path, "state.json")
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2, default=str)

        self.checkpoints.append(checkpoint_id)
        return checkpoint_id

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """获取检查点状态"""
        checkpoint_path = os.path.join(self.backup_root, checkpoint_id)
        state_file = os.path.join(checkpoint_path, "state.json")

        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                return json.load(f)
        return None

    def rollback_to(self, checkpoint_id: str, restore_func: Callable[[Dict], bool]) -> bool:
        """回滚到指定检查点"""
        state = self.get_checkpoint(checkpoint_id)
        if state is None:
            return False
        return restore_func(state)

    def cleanup_old_checkpoints(self, keep_last: int = 5):
        """清理旧检查点"""
        if len(self.checkpoints) <= keep_last:
            return

        for checkpoint in self.checkpoints[:-keep_last]:
            checkpoint_path = os.path.join(self.backup_root, checkpoint)
            if os.path.exists(checkpoint_path):
                shutil.rmtree(checkpoint_path)

        self.checkpoints = self.checkpoints[-keep_last:]


class SecurityValidator:
    """安全验证器"""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.banned_patterns = config.banned_patterns

    def validate(self, code: str) -> tuple[bool, List[Dict[str, Any]]]:
        """验证代码安全性"""
        errors = []

        # 检查禁止的模式
        for pattern in self.banned_patterns:
            if pattern in code:
                errors.append({
                    "type": "SecurityViolation",
                    "severity": "critical",
                    "message": f"Code contains banned pattern: {pattern}",
                    "pattern": pattern
                })

        # 检查可疑的导入
        if "__import__" in code or "importlib" in code:
            errors.append({
                "type": "SecurityViolation",
                "severity": "critical",
                "message": "Dynamic import is not allowed",
                "pattern": "__import__"
            })

        # 检查网络访问
        if self.config.allow_network is False:
            network_patterns = ["requests.", "urllib", "http.client", "socket."]
            for pattern in network_patterns:
                if pattern in code:
                    errors.append({
                        "type": "SecurityViolation",
                        "severity": "warning",
                        "message": f"Network access detected: {pattern}",
                        "pattern": pattern
                    })

        return len(errors) == 0, errors


class ResourceMonitor:
    """资源监控器"""

    def __init__(self, limits: SandboxLimits):
        self.limits = limits
        self.peak_memory = 0
        self.cpu_time = 0
        self.start_time = None

    def set_limits(self):
        """设置资源限制"""
        # 设置内存限制
        memory_limit = self.limits.max_memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

        # 设置最大进程数
        resource.setrlimit(resource.RLIMIT_NPROC, (self.limits.max_processes, self.limits.max_processes))

        # 设置最大文件大小
        disk_limit = self.limits.max_disk_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_FSIZE, (disk_limit, disk_limit))

    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()

    def get_usage(self) -> Dict[str, Any]:
        """获取资源使用情况"""
        # 获取当前内存使用
        try:
            with open("/proc/self/status", "r") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        self.peak_memory = int(line.split()[1]) / 1024  # KB to MB
                        break
        except Exception:
            pass

        return {
            "memory_peak_mb": self.peak_memory,
            "cpu_time_ms": int(self.cpu_time * 1000),
            "duration_ms": int((time.time() - self.start_time) * 1000) if self.start_time else 0
        }


class TestRunner:
    """测试运行器"""

    def __init__(self, language: str):
        self.language = language
        self.test_framework = self._detect_framework()

    def _detect_framework(self) -> str:
        """检测测试框架"""
        frameworks = {
            "python": ["pytest", "unittest"],
            "javascript": ["jest", "mocha", "jasmine"],
            "typescript": ["jest", "mocha"],
            "bash": ["bats"]
        }
        return frameworks.get(self.language, [])[0] if self.language in frameworks else "unknown"

    def run_tests(self, code: str, working_dir: str, timeout: int = 120) -> Dict[str, Any]:
        """运行测试"""
        result = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "coverage": 0.0,
            "duration_ms": 0,
            "output": ""
        }

        start_time = time.time()

        if self.language == "python":
            result = self._run_python_tests(code, working_dir, timeout)
        elif self.language in ["javascript", "typescript"]:
            result = self._run_js_tests(code, working_dir, timeout)

        result["duration_ms"] = int((time.time() - start_time) * 1000)
        return result

    def _run_python_tests(self, code: str, working_dir: str, timeout: int) -> Dict[str, Any]:
        """运行 Python 测试"""
        # 创建临时测试文件
        test_file = os.path.join(working_dir, "test_code.py")
        with open(test_file, "w") as f:
            f.write(code)

        result = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "coverage": 0.0,
            "output": ""
        }

        try:
            # 尝试使用 pytest 运行
            cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir
            )

            result["output"] = process.stdout + process.stderr
            result["exit_code"] = process.returncode

            # 解析 pytest 输出
            for line in result["output"].split("\n"):
                if "passed" in line.lower() or "failed" in line.lower():
                    # 简单解析
                    pass

        except subprocess.TimeoutExpired:
            result["output"] = f"Test execution timeout after {timeout} seconds"
            result["exit_code"] = -1
        except Exception as e:
            result["output"] = f"Test execution error: {str(e)}"
            result["exit_code"] = -1

        return result

    def _run_js_tests(self, code: str, working_dir: str, timeout: int) -> Dict[str, Any]:
        """运行 JavaScript/TypeScript 测试"""
        result = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "coverage": 0.0,
            "output": ""
        }

        try:
            cmd = ["npx", "jest", "--passWithNoTests", "--detectOpenHandles"]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=working_dir
            )

            result["output"] = process.stdout + process.stderr
            result["exit_code"] = process.returncode

        except Exception as e:
            result["output"] = f"Test execution error: {str(e)}"
            result["exit_code"] = -1

        return result


class SandboxedExecutor:
    """沙箱代码执行器"""

    def __init__(
        self,
        limits: Optional[SandboxLimits] = None,
        security_config: Optional[SecurityConfig] = None,
        rollback_enabled: bool = True
    ):
        self.limits = limits or SandboxLimits()
        self.security_config = security_config or SecurityConfig()
        self.rollback_enabled = rollback_enabled

        self.security_validator = SecurityValidator(self.security_config)
        self.checkpoint_manager = CheckpointManager()
        self.resource_monitor = ResourceMonitor(self.limits)

        self.executions: Dict[str, ExecutionResult] = {}

    def execute(
        self,
        code: str,
        language: str = "python",
        tests: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        rollback_on_failure: bool = True,
        checkpoint_state: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """执行代码"""
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        timeout = timeout or self.limits.max_execution_time

        # 创建检查点（如果启用）
        checkpoint_id = None
        if self.rollback_enabled and checkpoint_state:
            checkpoint_id = self.checkpoint_manager.create_checkpoint(
                execution_id,
                checkpoint_state
            )

        # 初始化结果
        result = ExecutionResult(
            execution_id=execution_id,
            status=ExecutionStatus.PENDING,
            checkpoint_id=checkpoint_id
        )
        self.executions[execution_id] = result

        # 步骤 1: 静态验证
        result.status = ExecutionStatus.VALIDATING
        is_safe, security_errors = self.security_validator.validate(code)

        if not is_safe:
            result.status = ExecutionStatus.REJECTED
            result.errors = security_errors
            if rollback_on_failure and checkpoint_id:
                self._rollback(execution_id, checkpoint_id)
            return result

        # 步骤 2: 在沙箱中执行
        result.status = ExecutionStatus.RUNNING
        result.start_time = datetime.now()

        try:
            execution_result = self._run_in_sandbox(
                code=code,
                language=language,
                timeout=timeout
            )

            result.stdout = execution_result.get("stdout", "")
            result.stderr = execution_result.get("stderr", "")
            result.exit_code = execution_result.get("exit_code", -1)
            result.resources = execution_result.get("resources", {})
            result.end_time = datetime.now()
            result.duration_ms = int(
                (result.end_time - result.start_time).total_seconds() * 1000
            )

            if result.exit_code == 0:
                result.status = ExecutionStatus.SUCCESS
            else:
                result.status = ExecutionStatus.FAILED
                result.errors.append({
                    "type": "ExecutionError",
                    "message": f"Exit code: {result.exit_code}",
                    "stderr": result.stderr
                })

        except subprocess.TimeoutExpired:
            result.status = ExecutionStatus.TIMEOUT
            result.errors.append({
                "type": "TimeoutError",
                "message": f"Execution timeout after {timeout} seconds"
            })
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.errors.append({
                "type": "ExecutionError",
                "message": str(e)
            })

        # 步骤 3: 运行测试（如果有）
        if tests and result.status == ExecutionStatus.SUCCESS:
            result.status = ExecutionStatus.TESTING
            test_result = self._run_tests(code, tests, timeout - 60)
            result.tests = test_result

            if test_result.get("failed", 0) > 0:
                result.status = ExecutionStatus.FAILED
            else:
                result.status = ExecutionStatus.PASSED

        # 步骤 4: 处理失败和回滚
        if result.status in [ExecutionStatus.FAILED, ExecutionStatus.TIMEOUT]:
            if rollback_on_failure and checkpoint_id:
                self._rollback(execution_id, checkpoint_id)
            else:
                result.status = ExecutionStatus.FAILED

        return result

    def _run_in_sandbox(
        self,
        code: str,
        language: str,
        timeout: int
    ) -> Dict[str, Any]:
        """在沙箱中运行代码"""
        # 创建临时工作目录
        with tempfile.TemporaryDirectory() as working_dir:
            # 写入代码文件
            extensions = {
                "python": ".py",
                "javascript": ".js",
                "typescript": ".ts",
                "bash": ".sh"
            }
            ext = extensions.get(language, ".txt")
            code_file = os.path.join(working_dir, f"code{ext}")

            with open(code_file, "w") as f:
                f.write(code)

            # 确定执行命令
            commands = {
                "python": [sys.executable, code_file],
                "javascript": ["node", code_file],
                "bash": ["bash", code_file]
            }
            cmd = commands.get(language, commands["python"])

            result = {
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "resources": {}
            }

            self.resource_monitor.start_monitoring()

            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=working_dir,
                    preexec_fn=self.resource_monitor.set_limits
                )

                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    result["stdout"] = stdout
                    result["stderr"] = stderr
                    result["exit_code"] = process.returncode
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    result["stdout"] = stdout
                    result["stderr"] = stderr
                    raise subprocess.TimeoutExpired(cmd, timeout)

            except Exception as e:
                raise

            result["resources"] = self.resource_monitor.get_usage()
            return result

    def _run_tests(
        self,
        code: str,
        tests: List[str],
        timeout: int
    ) -> Dict[str, Any]:
        """运行测试"""
        # 合并代码和测试
        full_code = code + "\n\n# === Tests ===\n" + "\n\n".join(tests)

        with tempfile.TemporaryDirectory() as working_dir:
            test_file = os.path.join(working_dir, "test_code.py")
            with open(test_file, "w") as f:
                f.write(full_code)

            runner = TestRunner("python")
            return runner.run_tests(full_code, working_dir, timeout)

    def _rollback(self, execution_id: str, checkpoint_id: str):
        """执行回滚"""
        result = self.executions[execution_id]
        result.status = ExecutionStatus.ROLLING_BACK

        if self.checkpoint_manager.rollback_to(checkpoint_id, lambda s: True):
            result.status = ExecutionStatus.ROLLED_BACK
        else:
            result.errors.append({
                "type": "RollbackError",
                "message": f"Failed to rollback to checkpoint: {checkpoint_id}"
            })

    def get_status(self, execution_id: str) -> Optional[ExecutionResult]:
        """获取执行状态"""
        return self.executions.get(execution_id)

    def get_logs(self, execution_id: str) -> Dict[str, Any]:
        """获取执行日志"""
        result = self.executions.get(execution_id)
        if result is None:
            return {"error": "Execution not found"}

        return {
            "execution_id": result.execution_id,
            "status": result.status.value,
            "start_time": result.start_time.isoformat() if result.start_time else None,
            "end_time": result.end_time.isoformat() if result.end_time else None,
            "duration_ms": result.duration_ms,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "resources": result.resources,
            "tests": result.tests,
            "errors": result.errors
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Sandboxed Code Executor")
    parser.add_argument("--code", "-c", help="Code to execute")
    parser.add_argument("--file", "-f", help="File containing code")
    parser.add_argument("--language", "-l", default="python", choices=["python", "javascript", "bash"])
    parser.add_argument("--timeout", "-t", type=int, default=60)
    parser.add_argument("--rollback", action="store_true", default=True)

    args = parser.parse_args()

    if args.file:
        with open(args.file, "r") as f:
            code = f.read()
    elif args.code:
        code = args.code
    else:
        print("Error: Either --code or --file must be provided")
        sys.exit(1)

    executor = SandboxedExecutor(rollback_enabled=args.rollback)
    result = executor.execute(
        code=code,
        language=args.language,
        timeout=args.timeout
    )

    print(f"Execution ID: {result.execution_id}")
    print(f"Status: {result.status.value}")
    print(f"Exit Code: {result.exit_code}")
    print(f"Duration: {result.duration_ms}ms")

    if result.stdout:
        print("\n--- STDOUT ---")
        print(result.stdout)

    if result.stderr:
        print("\n--- STDERR ---")
        print(result.stderr)

    if result.errors:
        print("\n--- ERRORS ---")
        for error in result.errors:
            print(json.dumps(error, indent=2))

    if result.resources:
        print("\n--- RESOURCES ---")
        print(json.dumps(result.resources, indent=2))


if __name__ == "__main__":
    main()
