#!/usr/bin/env python3
"""
工作流日志系统
记录工作流执行的详细信息，支持日志持久化和查询

核心功能：
1. 日志记录：记录工作流执行的每一步
2. 日志持久化：保存日志到文件
3. 日志查询：查询历史日志
4. 日志统计：统计工作流执行情况

版本：1.0.0
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class WorkflowLogger:
    """工作流日志记录器"""

    def __init__(self, log_dir: str = "./logs/workflows"):
        """
        初始化日志记录器

        参数：
            log_dir: 日志目录
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.current_session = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "workflows": []
        }

    def _generate_session_id(self) -> str:
        """生成会话 ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def log_workflow_start(
        self,
        workflow_type: str,
        input_data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        记录工作流开始

        参数：
            workflow_type: 工作流类型
            input_data: 输入数据
            metadata: 元数据
        """
        log_entry = {
            "workflow_id": f"workflow_{len(self.current_session['workflows'])}",
            "workflow_type": workflow_type,
            "status": "started",
            "start_time": datetime.now().isoformat(),
            "input_data": input_data,
            "metadata": metadata or {},
            "steps": [],
            "end_time": None,
            "result": None,
            "error": None
        }

        self.current_session["workflows"].append(log_entry)

    def log_step(
        self,
        step_name: str,
        step_data: Any,
        success: bool,
        error: Optional[str] = None
    ):
        """
        记录工作流步骤

        参数：
            step_name: 步骤名称
            step_data: 步骤数据
            success: 是否成功
            error: 错误信息
        """
        if not self.current_session["workflows"]:
            return

        current_workflow = self.current_session["workflows"][-1]

        step_entry = {
            "step_name": step_name,
            "start_time": datetime.now().isoformat(),
            "data": step_data,
            "success": success,
            "error": error,
            "end_time": datetime.now().isoformat()
        }

        current_workflow["steps"].append(step_entry)

    def log_workflow_end(
        self,
        result: Any,
        success: bool,
        error: Optional[str] = None
    ):
        """
        记录工作流结束

        参数：
            result: 执行结果
            success: 是否成功
            error: 错误信息
        """
        if not self.current_session["workflows"]:
            return

        current_workflow = self.current_session["workflows"][-1]

        current_workflow["status"] = "completed" if success else "failed"
        current_workflow["end_time"] = datetime.now().isoformat()
        current_workflow["result"] = result
        current_workflow["error"] = error

    def save_session(self) -> str:
        """
        保存当前会话到文件

        返回：
            日志文件路径
        """
        self.current_session["end_time"] = datetime.now().isoformat()

        log_file = self.log_dir / f"{self.current_session['session_id']}.json"

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_session, f, ensure_ascii=False, indent=2)

        return str(log_file)

    def get_session_logs(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定会话的日志

        参数：
            session_id: 会话 ID

        返回：
            会话日志
        """
        log_file = self.log_dir / f"{session_id}.json"

        if not log_file.exists():
            return None

        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_sessions(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        列出最近的会话

        参数：
            limit: 返回数量

        返回：
            会话列表
        """
        sessions = []

        for log_file in sorted(self.log_dir.glob("session_*.json"), reverse=True)[:limit]:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    sessions.append({
                        "session_id": session["session_id"],
                        "start_time": session["start_time"],
                        "end_time": session.get("end_time"),
                        "workflow_count": len(session.get("workflows", []))
                    })
            except Exception as e:
                print(f"读取日志文件失败: {log_file}, {e}")

        return sessions

    def get_workflow_logs(
        self,
        workflow_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取指定工作流的日志

        参数：
            workflow_id: 工作流 ID

        返回：
            工作流日志
        """
        for session_file in sorted(self.log_dir.glob("session_*.json"), reverse=True):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    for workflow in session.get("workflows", []):
                        if workflow["workflow_id"] == workflow_id:
                            return workflow
            except Exception as e:
                print(f"读取日志文件失败: {session_file}, {e}")

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取工作流统计信息

        返回：
            统计信息
        """
        stats = {
            "total_sessions": 0,
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "workflow_types": {},
            "average_duration": 0,
            "total_duration": 0
        }

        total_duration = 0
        workflow_count = 0

        for session_file in self.log_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)

                    stats["total_sessions"] += 1

                    for workflow in session.get("workflows", []):
                        stats["total_workflows"] += 1
                        workflow_count += 1

                        if workflow["status"] == "completed":
                            stats["successful_workflows"] += 1
                        else:
                            stats["failed_workflows"] += 1

                        workflow_type = workflow["workflow_type"]
                        stats["workflow_types"][workflow_type] = \
                            stats["workflow_types"].get(workflow_type, 0) + 1

                        # 计算持续时间
                        if workflow["start_time"] and workflow.get("end_time"):
                            start = datetime.fromisoformat(workflow["start_time"])
                            end = datetime.fromisoformat(workflow["end_time"])
                            duration = (end - start).total_seconds()
                            total_duration += duration

            except Exception as e:
                print(f"读取日志文件失败: {session_file}, {e}")

        if workflow_count > 0:
            stats["average_duration"] = total_duration / workflow_count
            stats["total_duration"] = total_duration

        return stats

    def clear_old_logs(self, days: int = 30):
        """
        清理旧日志

        参数：
            days: 保留天数
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)

        for log_file in self.log_dir.glob("session_*.json"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    print(f"删除旧日志: {log_file}")
                except Exception as e:
                    print(f"删除日志失败: {log_file}, {e}")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="工作流日志系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：

1. 查看最近会话：
  python workflow_logger.py list-sessions

2. 查看会话详情：
  python workflow_logger.py show-session session_20240101_120000

3. 查看工作流详情：
  python workflow_logger.py show-workflow workflow_0

4. 查看统计信息：
  python workflow_logger.py statistics

5. 清理旧日志：
  python workflow_logger.py clean --days 30
        """
    )

    parser.add_argument(
        "command",
        choices=["list-sessions", "show-session", "show-workflow", "statistics", "clean"],
        help="命令类型"
    )

    parser.add_argument(
        "id",
        nargs="?",
        help="会话 ID 或工作流 ID"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="保留天数（仅用于 clean 命令）"
    )

    args = parser.parse_args()

    logger = WorkflowLogger()

    if args.command == "list-sessions":
        sessions = logger.list_sessions()
        print(f"最近 {len(sessions)} 个会话:")
        for session in sessions:
            print(f"  - {session['session_id']}")
            print(f"    开始时间: {session['start_time']}")
            print(f"    工作流数量: {session['workflow_count']}")

    elif args.command == "show-session":
        if not args.id:
            print("错误: 需要 session_id")
            return

        session = logger.get_session_logs(args.id)
        if session:
            print(json.dumps(session, ensure_ascii=False, indent=2))
        else:
            print(f"错误: 会话 {args.id} 不存在")

    elif args.command == "show-workflow":
        if not args.id:
            print("错误: 需要 workflow_id")
            return

        workflow = logger.get_workflow_logs(args.id)
        if workflow:
            print(json.dumps(workflow, ensure_ascii=False, indent=2))
        else:
            print(f"错误: 工作流 {args.id} 不存在")

    elif args.command == "statistics":
        stats = logger.get_statistics()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

    elif args.command == "clean":
        logger.clear_old_logs(args.days)
        print(f"已清理 {args.days} 天前的旧日志")


if __name__ == "__main__":
    main()
