#!/usr/bin/env python3
"""
自我迭代技能 - 执行记录器
记录技能执行历史供后续分析
"""

import json
import os
import sys
from datetime import datetime
from typing import Optional

def get_skill_dir() -> str:
    """获取技能目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_execution_log(log_path: str) -> dict:
    """加载执行日志"""
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"version": "1.0", "entries": []}

def save_execution_log(log_path: str, log_data: dict) -> None:
    """保存执行日志"""
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

def record_execution(
    task_type: str,
    result: str = "success",
    duration_ms: Optional[int] = None,
    failure_reason: Optional[str] = None,
    user_feedback: Optional[str] = None,
    metadata: Optional[dict] = None
) -> bool:
    """记录一次执行"""
    skill_dir = get_skill_dir()
    log_path = os.path.join(skill_dir, 'data', 'execution_log.json')

    log_data = load_execution_log(log_path)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "task_type": task_type,
        "result": result,
        "duration_ms": duration_ms,
    }

    if failure_reason:
        entry["failure_reason"] = failure_reason

    if user_feedback:
        entry["user_feedback"] = user_feedback

    if metadata:
        entry["metadata"] = metadata

    log_data["entries"].append(entry)

    try:
        save_execution_log(log_path, log_data)
        return True
    except Exception as e:
        print(f"记录执行失败: {e}")
        return False

def print_usage():
    """打印使用说明"""
    print("""
自我迭代技能 - 执行记录器

用法:
    python record_execution.py <task_type> <result> [options]

参数:
    task_type   任务类型（如: analysis, planning, execution）
    result      执行结果（success, failure, partial）

选项:
    --duration-ms <ms>     执行时间（毫秒）
    --failure-reason <text> 失败原因
    --feedback <text>       用户反馈

示例:
    python record_execution.py analysis success --duration-ms 1500
    python record_execution.py planning failure --failure-reason "缺少数据"
""")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    task_type = sys.argv[1]
    result = sys.argv[2]

    # 解析可选参数
    duration_ms = None
    failure_reason = None
    user_feedback = None

    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--duration-ms' and i + 1 < len(sys.argv):
            duration_ms = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--failure-reason' and i + 1 < len(sys.argv):
            failure_reason = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--feedback' and i + 1 < len(sys.argv):
            user_feedback = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    success = record_execution(
        task_type=task_type,
        result=result,
        duration_ms=duration_ms,
        failure_reason=failure_reason,
        user_feedback=user_feedback
    )

    if success:
        print(f"✓ 执行已记录: {task_type} - {result}")
    else:
        print("✗ 记录失败")
        sys.exit(1)
