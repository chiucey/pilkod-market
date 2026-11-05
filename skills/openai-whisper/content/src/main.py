#!/usr/bin/env python3
"""
OpenAI Whisper CLI 本地语音转文字技能主入口
适配 Minimax Agent 调用规范，无第三方平台依赖，仅调用本地 whisper 二进制文件
"""

import sys
import json
import subprocess
import os


def run(input_data=None):
    """
    技能核心执行函数，适配 Minimax Agent 的入参/出参规范
    Args:
        input_data (dict): Minimax Agent 传入的参数字典，必填项 audio_path，其余为可选
            支持参数：
            - audio_path: str，必填，本地音频文件绝对/相对路径
            - model: str，可选，Whisper 模型，默认 turbo，可选 tiny/base/small/medium/large
            - task: str，可选，任务类型，transcribe(转录)/translate(翻译)，默认 transcribe
            - output_format: str，可选，输出格式，默认 txt，支持 txt/srt/vtt/json/tsv
            - output_dir: str，可选，输出文件目录，默认 ./output
    Returns:
        dict: 符合 Minimax Agent 规范的响应结构体
    """
    try:
        # 入参初始化与校验
        input_data = input_data or {}
        audio_path = input_data.get("audio_path")

        # 核心参数校验
        if not audio_path:
            return {
                "status": "error",
                "data": None,
                "message_for_user": "执行失败：请提供音频文件的完整路径"
            }
        if not os.path.exists(audio_path):
            return {
                "status": "error",
                "data": None,
                "message_for_user": f"执行失败：音频文件不存在，路径为 {audio_path}"
            }
        if not os.path.isfile(audio_path):
            return {
                "status": "error",
                "data": None,
                "message_for_user": "执行失败：您提供的路径不是一个有效的文件"
            }

        # 参数默认值赋值
        model = input_data.get("model", "turbo")
        task = input_data.get("task", "transcribe")
        output_format = input_data.get("output_format", "txt")
        output_dir = input_data.get("output_dir", "./output")

        # 输出目录自动创建
        os.makedirs(output_dir, exist_ok=True)

        # 构建 Whisper CLI 执行命令
        exec_cmd = [
            "whisper",
            audio_path,
            "--model", model,
            "--task", task,
            "--output_format", output_format,
            "--output_dir", output_dir
        ]

        # 执行本地命令，捕获完整输出
        exec_result = subprocess.run(
            exec_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )

        # 整理输出文件信息
        audio_filename = os.path.splitext(os.path.basename(audio_path))[0]
        output_file_list = []
        for format_item in output_format.split(","):
            format_item = format_item.strip()
            target_file = os.path.join(output_dir, f"{audio_filename}.{format_item}")
            if os.path.exists(target_file):
                output_file_list.append(os.path.abspath(target_file))

        # 成功响应
        return {
            "status": "success",
            "data": {
                "command_stdout": exec_result.stdout,
                "command_stderr": exec_result.stderr,
                "output_files": output_file_list,
                "audio_path": os.path.abspath(audio_path),
                "model_used": model,
                "task_executed": task
            },
            "message_for_user": f"音频处理完成！\n已生成输出文件：{', '.join(output_file_list)}"
        }

    except subprocess.CalledProcessError as e:
        # Whisper CLI 执行异常捕获
        return {
            "status": "error",
            "data": {
                "command_stdout": e.stdout,
                "command_stderr": e.stderr
            },
            "message_for_user": f"Whisper 执行失败：{e.stderr.strip() if e.stderr else e.stdout.strip()}"
        }
    except Exception as e:
        # 全局异常捕获
        return {
            "status": "error",
            "data": None,
            "message_for_user": f"技能执行异常：{str(e)}"
        }


# 命令行直接执行入口，适配 Minimax Agent 调用方式
if __name__ == "__main__":
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        input_data = json.loads(input_json) if input_json else {}
    else:
        input_data = {}

    output_result = run(input_data)
    print(json.dumps(output_result, ensure_ascii=False, indent=2))
