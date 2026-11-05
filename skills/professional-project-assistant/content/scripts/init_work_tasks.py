#!/usr/bin/env python3
"""
初始化工作任务存储
创建默认的任务数据结构
"""

import json
import os
from datetime import datetime

def init_work_tasks_storage():
    """初始化工作任务存储文件"""

    memories_path = "/memories"
    work_tasks_file = os.path.join(memories_path, "work_tasks.json")
    notes_file = os.path.join(memories_path, "notes.md")
    daily_log_file = os.path.join(memories_path, "daily_log.md")

    # 确保 /memories 目录存在
    os.makedirs(memories_path, exist_ok=True)

    # 初始化 work_tasks.json
    if not os.path.exists(work_tasks_file):
        initial_data = {
            "tasks": [],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "version": "1.0.0"
        }
        with open(work_tasks_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)
        print(f"✓ 已创建: {work_tasks_file}")
    else:
        print(f"○ 已存在: {work_tasks_file}")

    # 初始化 notes.md
    if not os.path.exists(notes_file):
        with open(notes_file, 'w', encoding='utf-8') as f:
            f.write("# 灵感与生活记录\n\n")
            f.write(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("## 灵感\n\n")
            f.write("## 生活备忘\n\n")
            f.write("## 客户需求\n\n")
        print(f"✓ 已创建: {notes_file}")
    else:
        print(f"○ 已存在: {notes_file}")

    # 初始化 daily_log.md
    if not os.path.exists(daily_log_file):
        with open(daily_log_file, 'w', encoding='utf-8') as f:
            f.write("# 工作日志\n\n")
            f.write(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        print(f"✓ 已创建: {daily_log_file}")
    else:
        print(f"○ 已存在: {daily_log_file}")

    print("\n初始化完成！")

if __name__ == "__main__":
    init_work_tasks_storage()
