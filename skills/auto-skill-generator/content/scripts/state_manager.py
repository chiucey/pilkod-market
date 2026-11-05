#!/usr/bin/env python3
"""
技能生成器状态管理脚本
管理任务状态、积分追踪和回滚操作
"""

import json
import os
from datetime import datetime
from pathlib import Path

class SkillGeneratorState:
    """技能生成器状态管理器"""

    STATE_FILE = "/memories/skill_generator_state.md"

    TASK_STATES = [
        "idle", "analyzing", "planning",
        "creating", "writing", "paused",
        "completed", "stopped"
    ]

    def __init__(self):
        self.credits = {
            "free_daily": 0,
            "floor_limit": 1000,
            "consumed": 0
        }
        self.task = {
            "state": "idle",
            "task_id": None,
            "current_step": 0,
            "start_time": None,
            "skill_name": None,
            "skill_description": None
        }
        self.rollback_log = []
        self.pending_task = None

    def load_state(self):
        """从状态文件加载"""
        if os.path.exists(self.STATE_FILE):
            with open(self.STATE_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                self._parse_state_file(content)
        return self

    def save_state(self):
        """保存状态到文件"""
        os.makedirs(os.path.dirname(self.STATE_FILE), exist_ok=True)
        with open(self.STATE_FILE, 'w', encoding='utf-8') as f:
            f.write(self._generate_state_file())
        return self

    def _parse_state_file(self, content):
        """解析状态文件内容"""
        lines = content.split('\n')
        section = None

        for line in lines:
            line = line.strip()
            if line.startswith('##'):
                section = line.lower().replace('## ', '')
            elif section == '当前积分':
                if '免费积分:' in line:
                    self.credits['free_daily'] = int(line.split(':')[1].strip())
                elif '底线积分:' in line:
                    self.credits['floor_limit'] = int(line.split(':')[1].strip())
                elif '已消耗:' in line:
                    self.credits['consumed'] = int(line.split(':')[1].strip())
            elif section == '任务状态':
                if '状态:' in line:
                    self.task['state'] = line.split(':')[1].strip()
                elif '任务ID:' in line:
                    self.task['task_id'] = line.split(':')[1].strip()
                elif '当前步骤:' in line:
                    self.task['current_step'] = int(line.split('/')[0].split(':')[1].strip())
                elif '开始时间:' in line:
                    self.task['start_time'] = line.split(':')[1].strip()

    def _generate_state_file(self):
        """生成状态文件内容"""
        return f"""# Skill-Generator 状态

## 当前积分
- 免费积分: {self.credits['free_daily']}
- 底线积分: {self.credits['floor_limit']}
- 已消耗: {self.credits['consumed']}
- 可用积分: {self.credits['free_daily'] - self.credits['consumed']}

## 任务状态
- 状态: {self.task['state']}
- 任务ID: {self.task['task_id'] or '无'}
- 当前步骤: {self.task['current_step']}/4
- 开始时间: {self.task['start_time'] or '无'}

## 回滚日志
{chr(10).join(self.rollback_log) if self.rollback_log else '- 无'}

## 待完成任务
- 技能名称: {self.task['skill_name'] or '无'}
- 描述: {self.task['skill_description'] or '无'}
"""

    def update_credits(self, free_daily=None, floor_limit=None, consumed=None):
        """更新积分信息"""
        if free_daily is not None:
            self.credits['free_daily'] = free_daily
        if floor_limit is not None:
            self.credits['floor_limit'] = floor_limit
        if consumed is not None:
            self.credits['consumed'] = consumed
        return self

    def consume_credits(self, amount):
        """消耗积分"""
        available = self.credits['free_daily'] - self.credits['consumed']
        if available < amount:
            return False
        self.credits['consumed'] += amount
        return True

    def check_credits(self, required):
        """检查积分是否足够"""
        available = self.credits['free_daily'] - self.credits['consumed']
        return available >= required and available - required >= self.credits['floor_limit']

    def update_task_state(self, state, step=None, skill_name=None, skill_desc=None):
        """更新任务状态"""
        if state in self.TASK_STATES:
            self.task['state'] = state
        if step is not None:
            self.task['current_step'] = step
        if skill_name:
            self.task['skill_name'] = skill_name
        if skill_desc:
            self.task['skill_description'] = skill_desc
        if not self.task['start_time']:
            self.task['start_time'] = datetime.now().isoformat()
        return self

    def add_rollback(self, step_name, action):
        """添加回滚日志"""
        self.rollback_log.append(f"- {step_name}: {action}")
        return self

    def rollback_step(self, step):
        """回滚到指定步骤"""
        rollback_actions = {
            3: lambda: self._rollback_directory(),
            4: lambda: self._rollback_skill_md()
        }
        if step in rollback_actions:
            rollback_actions[step]()
            self.task['state'] = ["planning", "analyzing", "idle"][step-2]
            self.task['current_step'] = step - 1

    def _rollback_directory(self):
        """回滚目录创建"""
        if self.task['skill_name']:
            skill_path = f"/workspace/temp-skills/{self.task['skill_name']}"
            if os.path.exists(skill_path):
                import shutil
                shutil.rmtree(skill_path)
                self.add_rollback("步骤3", "回滚（已删除目录）")

    def _rollback_skill_md(self):
        """回滚SKILL.md编写"""
        if self.task['skill_name']:
            skill_md_path = f"/workspace/temp-skills/{self.task['skill_name']}/SKILL.md"
            if os.path.exists(skill_md_path):
                os.remove(skill_md_path)
                self.add_rollback("步骤4", "回滚（已删除SKILL.md）")

    def is_task_pending(self):
        """检查是否有未完成任务"""
        return self.task['state'] not in ["idle", "completed", "stopped"]

    def get_summary(self):
        """获取任务摘要"""
        return {
            "credits": self.credits.copy(),
            "available": self.credits['free_daily'] - self.credits['consumed'],
            "task_state": self.task['state'],
            "current_step": self.task['current_step'],
            "has_pending_task": self.is_task_pending()
        }


if __name__ == "__main__":
    # 测试状态管理器
    state = SkillGeneratorState()
    state.update_credits(free_daily=2000, floor_limit=1000)
    state.update_task_state("analyzing", step=1, skill_name="test-skill")
    state.consume_credits(50)
    state.save_state()
    print(json.dumps(state.get_summary(), indent=2, ensure_ascii=False))
