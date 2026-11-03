#!/usr/bin/env python3
"""
学习备忘录脚本
用于添加、查看、删除学习计划
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path.home() / ".study_plans.json"


def load_plans():
    """加载学习计划"""
    if not DATA_FILE.exists():
        return {"plans": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_plans(data):
    """保存学习计划"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_plan(study_location, study_content, study_time):
    """添加学习计划（日期自动设为明天）"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    plan = {
        "date": tomorrow,
        "study_location": study_location,
        "study_content": study_content,
        "study_time": study_time,
        "reminded": False
    }
    data = load_plans()
    data["plans"].append(plan)
    save_plans(data)
    return plan


def get_today_plans():
    """获取今天的计划"""
    today = datetime.now().strftime("%Y-%m-%d")
    data = load_plans()
    return [p for p in data["plans"] if p["date"] == today and not p.get("reminded", False)]


def mark_reminded(date):
    """标记计划已提醒"""
    data = load_plans()
    for plan in data["plans"]:
        if plan["date"] == date:
            plan["reminded"] = True
    save_plans(data)


def list_plans():
    """列出所有未完成计划"""
    data = load_plans()
    return [p for p in data["plans"] if not p.get("reminded", False)]


def delete_plan(date):
    """删除指定日期的计划"""
    data = load_plans()
    data["plans"] = [p for p in data["plans"] if p["date"] != date]
    save_plans(data)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python study_reminder.py <add|list|check|delete> [参数...]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 5:
            print("用法: python study_reminder.py add <地点> <内容> <时间>")
            sys.exit(1)
        plan = add_plan(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"已添加学习计划：{plan['date']} {plan['study_time']} {plan['study_location']} {plan['study_content']}")

    elif command == "list":
        plans = list_plans()
        if not plans:
            print("暂无学习计划")
        else:
            for p in plans:
                print(f"{p['date']} {p['study_time']} | {p['study_location']} | {p['study_content']}")

    elif command == "check":
        plans = get_today_plans()
        if plans:
            for p in plans:
                print(f"[提醒] 今天 {p['study_time']} 在 {p['study_location']} 学习：{p['study_content']}")
                mark_reminded(p["date"])
        else:
            print("今天没有学习计划")

    elif command == "delete":
        if len(sys.argv) < 3:
            print("用法: python study_reminder.py delete <日期(YYYY-MM-DD)>")
            sys.exit(1)
        delete_plan(sys.argv[2])
        print(f"已删除日期为 {sys.argv[2]} 的计划")