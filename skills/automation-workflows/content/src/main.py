#!/usr/bin/env python3
"""
automation-workflows Skill Main Entry Module

This skill provides comprehensive no-code automation workflow design guidance
for solopreneurs, covering opportunity identification, workflow design,
tool selection (Zapier/Make/n8n), building/testing, monitoring/maintenance,
and ROI calculation.

Author: MiniMax Agent
Version: 0.2.0
"""

import sys
import json
from typing import Dict, Any, Optional


def run(input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute the skill core entry point.

    This is an instructional/guidance skill that provides workflow automation
    consulting services. The core capabilities are implemented through
    system prompts.

    Args:
        input_data (dict, optional): Parameters passed by AI

    Returns:
        dict: Standardized response structure
    """
    try:
        result = {
            "status": "success",
            "data": {
                "skill_type": "instructional_playbook",
                "skill_name": "automation-workflows",
                "version": "0.2.0",
                "core_function": "no-code automation workflow design & implementation guidance",
                "capabilities": [
                    "opportunity_identification",
                    "tool_selection",
                    "workflow_design",
                    "building_testing",
                    "monitoring_maintenance",
                    "roi_calculation",
                    "scenario_templates"
                ],
                "supported_tools": ["Zapier", "Make", "n8n"],
                "target_audience": "solopreneurs, professionals seeking productivity"
            },
            "message_for_user": (
                "自动化工作流技能已加载。我将为你提供全流程的无代码自动化工作流设计与实现指导，"
                "包括：\n"
                "1. 识别可自动化的重复任务\n"
                "2. 选择合适的无代码工具（Zapier/Make/n8n）\n"
                "3. 设计标准化工作流\n"
                "4. 搭建与测试\n"
                "5. 监控与运维\n"
                "6. ROI计算与优先级排序\n\n"
                "请告诉我你希望自动化什么工作，我将为你提供具体方案。"
            )
        }
        return result
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message_for_user": f"技能执行失败: {str(e)}"
        }


def get_skill_info() -> Dict[str, Any]:
    """
    Get skill metadata information.

    Returns:
        dict: Skill information including name, version, description
    """
    return {
        "name": "automation-workflows",
        "version": "0.2.0",
        "description": "No-code automation workflow design skill for solopreneurs",
        "author": "MiniMax Agent",
        "license": "MIT-0",
        "permissions": ["network:false"],
        "triggers": [
            "automate", "automation", "workflow automation",
            "save time", "reduce manual work", "automate my business",
            "no-code automation", "自动化", "工作流自动化",
            "节省时间", "减少手工工作", "无代码自动化"
        ]
    }


if __name__ == "__main__":
    # Handle both interactive and pipe input modes
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        input_data = json.loads(input_json) if input_json else {}
    else:
        input_data = {}

    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False, indent=2))
