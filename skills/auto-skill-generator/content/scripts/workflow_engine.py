#!/usr/bin/env python3
"""
技能生成工作流程引擎
执行4步骤工作流程：需求分析→资源规划→目录创建→编写SKILL.md
"""

import os
import json
import uuid
from datetime import datetime
from state_manager import SkillGeneratorState

class WorkflowEngine:
    """技能生成工作流程引擎"""

    STEPS = [
        {"id": 1, "name": "analyzing", "display": "寻找分析需求", "credits": 50},
        {"id": 2, "name": "planning", "display": "规划资源", "credits": 30},
        {"id": 3, "name": "creating", "display": "创建目录", "credits": 20},
        {"id": 4, "name": "writing", "display": "编写SKILL.md", "credits": 200}
    ]

    def __init__(self, state_manager):
        self.state = state_manager
        self.skill_id = None

    def execute_step(self, step_id, context=None):
        """执行指定步骤"""
        step = self._get_step(step_id)
        if not step:
            return {"success": False, "error": "无效步骤"}

        # 检查积分
        if not self.state.check_credits(step['credits']):
            self.state.update_task_state("paused")
            self.state.save_state()
            return {
                "success": False,
                "error": "积分不足",
                "available": self.state.credits['free_daily'] - self.state.credits['consumed'],
                "required": step['credits'],
                "floor_limit": self.state.credits['floor_limit']
            }

        # 消耗积分
        self.state.consume_credits(step['credits'])
        self.state.update_task_state(step['name'], step=step_id)

        # 执行步骤逻辑
        result = self._run_step_logic(step_id, context)

        # 保存状态
        self.state.save_state()

        return result

    def _get_step(self, step_id):
        """获取步骤信息"""
        for step in self.STEPS:
            if step['id'] == step_id:
                return step
        return None

    def _run_step_logic(self, step_id, context):
        """运行步骤逻辑"""
        handlers = {
            1: self._step_analyze,
            2: self._step_plan,
            3: self._step_create,
            4: self._step_write
        }
        return handlers.get(step_id, lambda x: {"success": False, "error": "未实现"})(context)

    def _step_analyze(self, context):
        """步骤1：寻找分析需求"""
        # 分析用户需求
        analysis_result = {
            "requirements_found": [],
            "complexity": "medium",
            "estimated_credits": 300
        }

        if context:
            if "skill" in context.lower() or "技能" in context:
                analysis_result["requirements_found"].append("技能创建")
            if "自动" in context:
                analysis_result["requirements_found"].append("自动化")

        # 生成任务ID
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        self.state.task['task_id'] = task_id

        return {
            "success": True,
            "step": 1,
            "result": analysis_result,
            "task_id": task_id
        }

    def _step_plan(self, context):
        """步骤2：规划资源"""
        # 估算资源需求
        plan_result = {
            "files_needed": ["SKILL.md", "_meta.json"],
            "directories": ["scripts", "references", "assets"],
            "estimated_time": "5-10分钟",
            "priority": "high"
        }

        return {
            "success": True,
            "step": 2,
            "result": plan_result
        }

    def _step_create(self, context):
        """步骤3：创建目录"""
        skill_name = context.get("skill_name") if isinstance(context, dict) else "new-skill"
        base_path = "/workspace/temp-skills"

        # 创建目录结构
        dirs = [
            f"{base_path}/{skill_name}",
            f"{base_path}/{skill_name}/scripts",
            f"{base_path}/{skill_name}/references",
            f"{base_path}/{skill_name}/assets"
        ]

        created = []
        for d in dirs:
            os.makedirs(d, exist_ok=True)
            created.append(d)

        # 创建 _meta.json
        meta_path = f"{base_path}/{skill_name}/_meta.json"
        meta_content = {
            "id": str(int(datetime.now().timestamp())),
            "version": "1.0.0"
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta_content, f, indent=2, ensure_ascii=False)

        self.state.task['skill_name'] = skill_name

        return {
            "success": True,
            "step": 3,
            "created_directories": created,
            "meta_file": meta_path
        }

    def _step_write(self, context):
        """步骤4：编写SKILL.md"""
        skill_name = self.state.task.get('skill_name') or context.get('skill_name') if isinstance(context, dict) else "new-skill"
        skill_desc = context.get('description', '自动生成的技能') if isinstance(context, dict) else context or '自动生成的技能'

        skill_md_path = f"/workspace/temp-skills/{skill_name}/SKILL.md"

        # 生成SKILL.md内容
        content = f"""---
name: {skill_name}
description: {skill_desc}
---

# {skill_name}

自动生成的技能。

## 功能说明

[待补充详细功能说明]

## 使用方式

[待补充使用说明]
"""

        with open(skill_md_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 生成技能ID
        from pathlib import Path
        import hashlib

        skill_id = int(hashlib.md5(skill_name.encode()).hexdigest()[:8], 16) % 1000000000

        # 更新 _meta.json
        meta_path = f"/workspace/temp-skills/{skill_name}/_meta.json"
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta['id'] = str(skill_id)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        self.state.task['skill_description'] = skill_desc
        self.skill_id = skill_id

        return {
            "success": True,
            "step": 4,
            "skill_id": skill_id,
            "file_path": skill_md_path
        }

    def run_full_workflow(self, context=None):
        """运行完整工作流程"""
        results = []

        for step in self.STEPS:
            result = self.execute_step(step['id'], context)
            results.append(result)

            if not result['success']:
                return {
                    "success": False,
                    "completed_steps": step['id'] - 1,
                    "results": results,
                    "error": result.get('error')
                }

        # 标记完成
        self.state.update_task_state("completed")
        self.state.save_state()

        return {
            "success": True,
            "all_steps_completed": True,
            "results": results,
            "skill_id": self.skill_id
        }

    def rollback_to_step(self, step_id):
        """回滚到指定步骤"""
        if step_id < 1 or step_id > 4:
            return {"success": False, "error": "无效步骤"}

        self.state.rollback_step(step_id)
        self.state.save_state()

        return {
            "success": True,
            "rolled_back_to": step_id - 1,
            "new_state": self.state.task['state']
        }


if __name__ == "__main__":
    # 测试工作流程引擎
    state_manager = SkillGeneratorState()
    state_manager.update_credits(free_daily=2000, floor_limit=1000)

    engine = WorkflowEngine(state_manager)

    # 测试执行
    result = engine.execute_step(1, {"skill_name": "test-skill", "description": "测试技能"})
    print(json.dumps(result, indent=2, ensure_ascii=False))
