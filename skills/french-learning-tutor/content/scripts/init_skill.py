#!/usr/bin/env python3
"""
French Learning Tutor - 技能初始化脚本
用于设置用户学习状态和初始化每日练习数据
"""

import json
import os
from datetime import datetime, timedelta

# 默认用户状态
DEFAULT_USER_STATE = {
    "current_level": "A1",
    "current_day": 1,
    "total_days": 0,
    "vocabulary_known": 0,
    "grammar_progress": "0%",
    "streak": 0,
    "last_review_date": None,
    "pending_reviews": [],
    "feishu_webhook": None,
    "feishu_enabled": False,
    "settings": {
        "push_time": "09:00",
        "daily_goal_minutes": 60,
        "speaking_enabled": True,
        "listening_speed": "slow"
    }
}

# 艾宾浩斯复习间隔（天）
REVIEW_INTERVALS = [1, 3, 7, 14, 30, 60]

# 学习内容存储路径
STATE_FILE = "user_state.json"
VOCABULARY_FILE = "vocabulary.json"
PROGRESS_FILE = "progress.json"


def init_user_state():
    """初始化用户学习状态"""
    state = DEFAULT_USER_STATE.copy()
    state["created_at"] = datetime.now().isoformat()
    state["last_active"] = datetime.now().isoformat()
    return state


def init_vocabulary():
    """初始化词汇表"""
    return {
        "words": {},
        "last_updated": datetime.now().isoformat()
    }


def init_progress():
    """初始化进度追踪"""
    return {
        "daily_progress": [],
        "weekly_goals": {},
        "monthly_stats": {},
        "last_updated": datetime.now().isoformat()
    }


def calculate_next_review(learning_date, interval):
    """计算下次复习日期"""
    return (datetime.strptime(learning_date, "%Y-%m-%d") + timedelta(days=interval)).strftime("%Y-%m-%d")


def generate_review_schedule(learning_dates):
    """根据遗忘曲线生成复习计划"""
    schedule = {}
    for learning_date in learning_dates:
        for interval in REVIEW_INTERVALS:
            review_date = calculate_next_review(learning_date, interval)
            if review_date not in schedule:
                schedule[review_date] = []
            schedule[review_date].append(learning_date)
    return schedule


def get_daily_exercises(level="A1", day=1):
    """获取每日练习（简化版示例）"""
    exercises = {
        "A1": [
            {"day": 1, "title": "Hello!", "topic": "greetings", "url": "https://apprendre.tv5monde.com/en/exercises/a1-breakthrough/hello"},
            {"day": 2, "title": "A day!", "topic": "daily_routine", "url": "https://apprendre.tv5monde.com/en/exercises/a1-breakthrough/day"},
            {"day": 3, "title": "Our clothes", "topic": "clothing", "url": "https://apprendre.tv5monde.com/en/exercises/a1-breakthrough/our-clothes"},
            {"day": 4, "title": "Trips", "topic": "prepositions", "url": "https://apprendre.tv5monde.com/en/exercises/a1-breakthrough/trips"},
            {"day": 5, "title": "Christmas", "topic": "festivals", "url": "https://apprendre.tv5monde.com/en/exercises/a1-breakthrough/christmas"},
            {"day": 6, "title": "Music!", "topic": "music", "url": "https://apprendre.tv5monde.com/en/exercises/a1-breakthrough/music"},
            {"day": 7, "title": "Sports in middle school", "topic": "sports", "url": "https://apprendre.tv5monde.com/en/exercises/a1-breakthrough/sports-middle-school"}
        ]
    }
    return exercises.get(level, exercises["A1"])


def check_review_due(state):
    """检查是否有需要复习的内容"""
    today = datetime.now().strftime("%Y-%m-%d")
    due_reviews = []

    for review in state.get("pending_reviews", []):
        if review["next_review"] <= today:
            due_reviews.append(review)

    return due_reviews


def add_review_item(state, learning_date, content_type, content_id, topic):
    """添加复习项目"""
    reviews = state.get("pending_reviews", [])

    for interval in REVIEW_INTERVALS:
        review_date = calculate_next_review(learning_date, interval)
        reviews.append({
            "learning_date": learning_date,
            "next_review": review_date,
            "content_type": content_type,
            "content_id": content_id,
            "topic": topic,
            "interval": interval
        })

    state["pending_reviews"] = reviews
    return state


def update_user_progress(state, task_completed, score):
    """更新用户进度"""
    state["total_days"] += 1
    state["last_active"] = datetime.now().isoformat()

    # 更新连续学习天数
    if task_completed:
        state["streak"] += 1
    else:
        state["streak"] = 0

    # 更新词汇量（简单估算）
    if score >= 80:
        state["vocabulary_known"] = state.get("vocabulary_known", 0) + 5
    elif score >= 60:
        state["vocabulary_known"] = state.get("vocabulary_known", 0) + 2

    return state


def should_increase_difficulty(state):
    """判断是否应该增加难度"""
    recent_completion = state.get("recent_completion_rate", 0.9)
    recent_error_rate = state.get("recent_error_rate", 0.1)

    return recent_completion >= 0.9 and recent_error_rate < 0.1


def should_decrease_difficulty(state):
    """判断是否应该降低难度"""
    recent_completion = state.get("recent_completion_rate", 0.9)
    recent_error_rate = state.get("recent_error_rate", 0.1)

    return recent_completion < 0.6 or recent_error_rate > 0.3


def get_next_level(current_level):
    """获取下一级别"""
    levels = ["A1", "A2", "B1", "B2"]
    current_idx = levels.index(current_level) if current_level in levels else 0
    if current_idx < len(levels) - 1:
        return levels[current_idx + 1]
    return current_level


if __name__ == "__main__":
    # 初始化数据
    print("🎓 法语学习技能初始化中...")

    user_state = init_user_state()
    vocabulary = init_vocabulary()
    progress = init_progress()

    # 保存初始状态
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(user_state, f, ensure_ascii=False, indent=2)
    print(f"✅ 用户状态已初始化: {STATE_FILE}")

    with open(VOCABULARY_FILE, "w", encoding="utf-8") as f:
        json.dump(vocabulary, f, ensure_ascii=False, indent=2)
    print(f"✅ 词汇表已初始化: {VOCABULARY_FILE}")

    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
    print(f"✅ 进度追踪已初始化: {PROGRESS_FILE}")

    print("\n🎉 初始化完成！开始你的法语学习之旅吧！")
    print(f"📅 今日学习主题: {get_daily_exercises('A1', 1)[0]['title']}")