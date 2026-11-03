#!/usr/bin/env python3
"""
AI数字分身训练师 - 打包脚本
将技能打包成分发格式
"""

import os
import zipfile
import json
from datetime import datetime

def package_skill():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_name = os.path.basename(skill_dir)

    # 输出文件名
    output_file = os.path.join(skill_dir, f"{skill_name}.skill")

    # 创建zip包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 排除 __pycache__ 等
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.') or file.endswith('.pyc'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)

    print(f"技能已打包: {output_file}")
    return output_file

if __name__ == "__main__":
    package_skill()
