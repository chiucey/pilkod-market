#!/usr/bin/env python3
"""
每日提醒脚本 - 被 Cron 调用，输出待办摘要供发送
用法: python3 daily_reminder.py
"""
import json, os
from datetime import datetime

TODO_FILE = os.path.expanduser("~/.openclaw/todo_manager/todos.json")

def run():
    if not os.path.exists(TODO_FILE):
        print("NO_TODOS")
        return

    with open(TODO_FILE) as f:
        data = json.load(f)

    undone = [t for t in data if not t.get("done", False)]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not undone:
        print("EMPTY")
        return

    lines = [f"📋 待办提醒 {now}（共 {len(undone)} 项）\n"]
    overdue = []
    today = []
    future = []

    for t in undone:
        due = t.get("due", "")
        if due:
            try:
                due_dt = datetime.strptime(due, "%Y-%m-%d %H:%M")
                today_dt = datetime.strptime(now.split()[0], "%Y-%m-%d")
                if due_dt.date() < today_dt.date():
                    overdue.append(t)
                elif due_dt.date() == today_dt.date():
                    today.append(t)
                else:
                    future.append(t)
            except:
                future.append(t)
        else:
            future.append(t)

    if overdue:
        lines.append("🔴 已过期:")
        for t in overdue:
            lines.append(f"  [{t['id']}] {t['content']}（{t['due']}）")
        lines.append("")

    if today:
        lines.append("🟡 今天截止:")
        for t in today:
            lines.append(f"  [{t['id']}] {t['content']}（{t['due']}）")
        lines.append("")

    if future:
        lines.append("📌 后续待办:")
        for t in future:
            due_str = f" → {t['due']}" if t.get("due") else ""
            lines.append(f"  [{t['id']}] {t['content']}{due_str}")

    print("\n".join(lines))

if __name__ == "__main__":
    run()
