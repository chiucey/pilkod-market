#!/usr/bin/env python3
"""
工作流监控工具
实时监控工作流执行状态，提供性能统计和告警功能

核心功能：
1. 实时监控：监控工作流执行状态
2. 性能统计：统计工作流执行性能
3. 告警机制：异常情况告警
4. 可视化展示：生成监控报告

版本：1.0.0
"""

import json
import time
import os
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
from workflow_logger import WorkflowLogger


class WorkflowMonitor:
    """工作流监控器"""

    def __init__(
        self,
        logger: Optional[WorkflowLogger] = None,
        alert_threshold: int = 60
    ):
        """
        初始化监控器

        参数：
            logger: 日志记录器
            alert_threshold: 告警阈值（秒）
        """
        self.logger = logger or WorkflowLogger()
        self.alert_threshold = alert_threshold
        self.alerts = []
        self.callbacks = []

    def register_callback(
        self,
        callback: Callable[[Dict[str, Any]], None]
    ):
        """
        注册回调函数

        参数：
            callback: 回调函数
        """
        self.callbacks.append(callback)

    def check_workflow_timeout(
        self,
        workflow_id: str,
        timeout: int
    ) -> bool:
        """
        检查工作流是否超时

        参数：
            workflow_id: 工作流 ID
            timeout: 超时时间（秒）

        返回：
            是否超时
        """
        workflow = self.logger.get_workflow_logs(workflow_id)

        if not workflow:
            return False

        if workflow["status"] in ["completed", "failed"]:
            return False

        start_time = datetime.fromisoformat(workflow["start_time"])
        elapsed = (datetime.now() - start_time).total_seconds()

        return elapsed > timeout

    def monitor_workflow(
        self,
        workflow_id: str,
        interval: int = 5
    ):
        """
        监控工作流执行

        参数：
            workflow_id: 工作流 ID
            interval: 检查间隔（秒）
        """
        print(f"开始监控工作流: {workflow_id}")

        while True:
            workflow = self.logger.get_workflow_logs(workflow_id)

            if not workflow:
                print(f"工作流 {workflow_id} 不存在")
                break

            if workflow["status"] in ["completed", "failed"]:
                print(f"工作流 {workflow_id} 已完成，状态: {workflow['status']}")
                break

            # 检查超时
            if self.check_workflow_timeout(workflow_id, self.alert_threshold):
                alert = {
                    "workflow_id": workflow_id,
                    "alert_type": "timeout",
                    "message": f"工作流 {workflow_id} 执行超时",
                    "timestamp": datetime.now().isoformat()
                }
                self.alerts.append(alert)
                print(f"⚠️ 警告: {alert['message']}")

                # 触发回调
                for callback in self.callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        print(f"回调执行失败: {e}")

            time.sleep(interval)

    def get_performance_metrics(
        self,
        workflow_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取性能指标

        参数：
            workflow_type: 工作流类型（可选）

        返回：
            性能指标
        """
        metrics = {
            "workflow_type": workflow_type,
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "average_duration": 0,
            "min_duration": float('inf'),
            "max_duration": 0,
            "durations": []
        }

        total_duration = 0

        for session_file in self.logger.log_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)

                    for workflow in session.get("workflows", []):
                        if workflow_type and workflow["workflow_type"] != workflow_type:
                            continue

                        metrics["total_workflows"] += 1

                        if workflow["status"] == "completed":
                            metrics["successful_workflows"] += 1

                            if workflow["start_time"] and workflow.get("end_time"):
                                start = datetime.fromisoformat(workflow["start_time"])
                                end = datetime.fromisoformat(workflow["end_time"])
                                duration = (end - start).total_seconds()

                                metrics["durations"].append(duration)
                                total_duration += duration

                                metrics["min_duration"] = min(metrics["min_duration"], duration)
                                metrics["max_duration"] = max(metrics["max_duration"], duration)

                        else:
                            metrics["failed_workflows"] += 1

            except Exception as e:
                print(f"读取日志文件失败: {session_file}, {e}")

        if metrics["durations"]:
            metrics["average_duration"] = total_duration / len(metrics["durations"])
        else:
            metrics["min_duration"] = 0

        return metrics

    def generate_report(
        self,
        output_path: Optional[str] = None
    ) -> str:
        """
        生成监控报告

        参数：
            output_path: 输出路径（可选）

        返回：
            报告内容
        """
        stats = self.logger.get_statistics()
        metrics = self.get_performance_metrics()

        report = f"""
工作流监控报告
{'=' * 60}

会话统计:
  总会话数: {stats['total_sessions']}
  总工作流数: {stats['total_workflows']}
  成功工作流: {stats['successful_workflows']}
  失败工作流: {stats['failed_workflows']}
  成功率: {stats['successful_workflows'] / stats['total_workflows'] * 100 if stats['total_workflows'] > 0 else 0:.2f}%

工作流类型分布:
"""
        for workflow_type, count in stats["workflow_types"].items():
            report += f"  {workflow_type}: {count}\n"

        report += f"""
性能指标:
  平均执行时间: {metrics['average_duration']:.2f} 秒
  最短执行时间: {metrics['min_duration']:.2f} 秒
  最长执行时间: {metrics['max_duration']:.2f} 秒
  总执行时间: {stats['total_duration']:.2f} 秒

告警记录:
  总告警数: {len(self.alerts)}
"""

        if self.alerts:
            for alert in self.alerts[-5:]:  # 显示最近 5 条
                report += f"  [{alert['timestamp']}] {alert['message']}\n"

        report += f"\n报告生成时间: {datetime.now().isoformat()}\n"

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到: {output_path}")

        return report

    def check_anomalies(
        self,
        workflow_type: str
    ) -> List[Dict[str, Any]]:
        """
        检查异常情况

        参数：
            workflow_type: 工作流类型

        返回：
            异常列表
        """
        anomalies = []
        metrics = self.get_performance_metrics(workflow_type)

        if metrics["durations"]:
            avg_duration = metrics["average_duration"]
            std_duration = (sum((d - avg_duration) ** 2 for d in metrics["durations"]) / len(metrics["durations"])) ** 0.5

            for session_file in self.logger.log_dir.glob("session_*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session = json.load(f)

                        for workflow in session.get("workflows", []):
                            if workflow["workflow_type"] != workflow_type:
                                continue

                            if workflow["start_time"] and workflow.get("end_time"):
                                start = datetime.fromisoformat(workflow["start_time"])
                                end = datetime.fromisoformat(workflow["end_time"])
                                duration = (end - start).total_seconds()

                                # 检查是否超过 3 个标准差
                                if abs(duration - avg_duration) > 3 * std_duration:
                                    anomalies.append({
                                        "workflow_id": workflow["workflow_id"],
                                        "duration": duration,
                                        "expected_duration": avg_duration,
                                        "deviation": abs(duration - avg_duration) / std_duration
                                    })

                except Exception as e:
                    print(f"读取日志文件失败: {session_file}, {e}")

        return anomalies


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="工作流监控工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：

1. 监控工作流：
  python workflow_monitor.py monitor workflow_0 --interval 5

2. 生成监控报告：
  python workflow_monitor.py report --output report.txt

3. 获取性能指标：
  python workflow_monitor.py metrics --workflow-type document-understanding

4. 检查异常：
  python workflow_monitor.py anomalies --workflow-type document-understanding
        """
    )

    parser.add_argument(
        "command",
        choices=["monitor", "report", "metrics", "anomalies"],
        help="命令类型"
    )

    parser.add_argument(
        "workflow_id",
        nargs="?",
        help="工作流 ID（仅用于 monitor 命令）"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="检查间隔（秒）"
    )

    parser.add_argument(
        "--workflow-type",
        help="工作流类型（仅用于 metrics 和 anomalies 命令）"
    )

    parser.add_argument(
        "--output",
        help="输出路径（仅用于 report 命令）"
    )

    args = parser.parse_args()

    monitor = WorkflowMonitor()

    if args.command == "monitor":
        if not args.workflow_id:
            print("错误: 需要 workflow_id")
            return

        monitor.monitor_workflow(args.workflow_id, args.interval)

    elif args.command == "report":
        report = monitor.generate_report(args.output)
        print(report)

    elif args.command == "metrics":
        metrics = monitor.get_performance_metrics(args.workflow_type)
        print(json.dumps(metrics, ensure_ascii=False, indent=2))

    elif args.command == "anomalies":
        if not args.workflow_type:
            print("错误: 需要 workflow_type")
            return

        anomalies = monitor.check_anomalies(args.workflow_type)
        print(f"检测到 {len(anomalies)} 个异常:")
        for anomaly in anomalies:
            print(f"  - 工作流 {anomaly['workflow_id']}")
            print(f"    执行时间: {anomaly['duration']:.2f} 秒")
            print(f"    预期时间: {anomaly['expected_duration']:.2f} 秒")
            print(f"    偏差: {anomaly['deviation']:.2f}x")


if __name__ == "__main__":
    main()
