#!/usr/bin/env python3
"""
Clawdbot Documentation Expert 主入口
无任何第三方依赖/OpenClaw依赖，仅处理Minimax Agent输入输出
"""

import sys
import json


def run(input_data: dict = None) -> dict:
    """
    Skill核心执行函数：接收AI输入，返回结构化结果

    Args:
        input_data: Minimax Agent传入的用户问题/参数字典

    Returns:
        标准响应格式（适配Minimax Agent）
    """
    try:
        # 无业务依赖：仅传递用户输入给AI提示词处理
        user_query = input_data.get("user_input", "") if input_data else ""

        result = {
            "status": "success",
            "data": {
                "processed": True,
                "user_query": user_query,
                "skill_name": "Clawdbot Documentation Expert"
            },
            "message_for_user": "已接收你的Clawdbot文档问题，将为你精准解答~"
        }
        return result
    except Exception as e:
        # 标准化错误返回
        return {
            "status": "error",
            "data": None,
            "message_for_user": f"文档处理失败：{str(e)}，请重新描述你的问题"
        }


if __name__ == "__main__":
    # 脚本模式：从标准输入读取Minimax Agent传入的JSON参数
    input_data = {}
    if not sys.stdin.isatty():
        input_json = sys.stdin.read().strip()
        if input_json:
            input_data = json.loads(input_json)

    # 输出标准JSON结果
    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False, indent=2))
