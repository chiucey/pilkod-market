#!/usr/bin/env python3
"""
Package PRD to Markdown Skill
将技能打包为可分发的.skill文件
"""

import os
import json
import zipfile
import shutil
from datetime import datetime

def package_skill(skill_path, output_dir=None):
    """打包技能为.skill文件"""
    skill_name = os.path.basename(skill_path)

    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    # 读取meta信息
    meta_path = os.path.join(skill_path, "_meta.json")
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 创建zip包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 跳过scripts目录
            if 'scripts' in dirs:
                dirs.remove('scripts')

            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zf.write(file_path, arcname)

    print(f"✅ 技能已打包: {output_file}")
    print(f"   ID: {meta.get('id', 'N/A')}")
    print(f"   Version: {meta.get('version', 'N/A')}")
    return output_file

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    else:
        skill_path = sys.argv[1]

    package_skill(skill_path)
