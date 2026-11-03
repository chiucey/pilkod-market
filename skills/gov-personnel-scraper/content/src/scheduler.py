#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务调度器 - 每天8点自动执行爬取任务
"""

import time
import signal
import sys
from datetime import datetime, time as dt_time
from threading import Thread, Event
from typing import Callable, Optional
from pathlib import Path


class Scheduler:
    """定时任务调度器"""

    def __init__(self):
        self.running = False
        self.stop_event = Event()
        self.thread: Optional[Thread] = None

    def _is_time_to_run(self, target_hour: int = 8, target_minute: int = 0) -> bool:
        """检查是否到达执行时间"""
        now = datetime.now()
        target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

        # 如果目标时间已过，检查是否在最近的一分钟内
        if now > target:
            diff = (now - target).total_seconds()
        else:
            # 目标时间未到，明天再执行
            return False

        return 0 <= diff < 60  # 在目标时间的一分钟内

    def _run_loop(self, task_func: Callable, hour: int, minute: int):
        """运行调度循环"""
        print(f"[调度器] 定时任务已启动 - 将在每天 {hour:02d}:{minute:02d} 执行")

        while self.running and not self.stop_event.is_set():
            try:
                if self._is_time_to_run(hour, minute):
                    print(f"[调度器] 到达执行时间，正在执行任务...")
                    task_func()
                    print(f"[调度器] 任务执行完成，等待下次执行...")

                    # 休眠59秒，避免重复执行
                    time.sleep(59)

                # 每分钟检查一次
                time.sleep(60)

            except KeyboardInterrupt:
                print("[调度器] 收到中断信号，正在停止...")
                break
            except Exception as e:
                print(f"[调度器] 执行出错: {e}")
                time.sleep(60)  # 出错后等待1分钟再试

        print("[调度器] 调度器已停止")

    def start(self, task_func: Callable, hour: int = 8, minute: int = 0):
        """启动调度器"""
        if self.running:
            print("[调度器] 调度器已在运行中")
            return

        self.running = True
        self.stop_event.clear()

        self.thread = Thread(
            target=self._run_loop,
            args=(task_func, hour, minute),
            daemon=True
        )
        self.thread.start()
        print(f"[调度器] 调度器已启动，线程ID: {self.thread.ident}")

    def stop(self):
        """停止调度器"""
        if not self.running:
            return

        print("[调度器] 正在停止调度器...")
        self.running = False
        self.stop_event.set()

        if self.thread:
            self.thread.join(timeout=5)
            self.thread = None

        print("[调度器] 调度器已停止")

    def run_once(self, task_func: Callable):
        """立即执行一次任务（不启动调度循环）"""
        print("[调度器] 立即执行任务...")
        try:
            task_func()
            print("[调度器] 任务执行完成")
        except Exception as e:
            print(f"[调度器] 任务执行出错: {e}")


class CronJob:
    """Cron风格的任务定义"""

    def __init__(self, name: str, command: str, schedule: str):
        """
        Args:
            name: 任务名称
            command: 执行命令
            schedule: cron表达式 (minute hour day month weekday)
        """
        self.name = name
        self.command = command
        self.schedule = schedule
        self.parts = schedule.split()

        if len(self.parts) != 5:
            raise ValueError("Cron表达式格式错误，应为: minute hour day month weekday")

    def should_run(self, now: datetime) -> bool:
        """检查是否应该运行"""
        minute, hour, day, month, weekday = self.parts

        checks = [
            self._match_field(minute, now.minute),
            self._match_field(hour, now.hour),
            self._match_field(day, now.day),
            self._match_field(month, now.month),
            self._match_field(weekday, now.weekday()),
        ]

        return all(checks)

    def _match_field(self, pattern: str, value: int) -> bool:
        """匹配字段"""
        if pattern == '*':
            return True

        # 范围，如 1-5
        if '-' in pattern:
            start, end = pattern.split('-')
            return int(start) <= value <= int(end)

        # 列表，如 1,3,5
        if ',' in pattern:
            return value in [int(x) for x in pattern.split(',')]

        # 步进，如 */5
        if '/' in pattern:
            base, step = pattern.split('/')
            base = int(base) if base != '*' else 0
            step = int(step)
            return (value - base) % step == 0

        # 精确匹配
        return value == int(pattern)


def setup_signal_handlers(scheduler: Scheduler):
    """设置信号处理器"""
    def signal_handler(signum, frame):
        print(f"\n[信号] 收到信号 {signum}，正在停止...")
        scheduler.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def test_scheduler():
    """测试调度器"""
    scheduler = Scheduler()

    def sample_task():
        print(f"[测试] 任务执行中，时间: {datetime.now()}")

    # 设置信号处理
    setup_signal_handlers(scheduler)

    # 启动调度器（每小时执行一次用于测试）
    scheduler.start(sample_task, hour=8, minute=0)

    # 主线程等待
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()


if __name__ == '__main__':
    test_scheduler()
