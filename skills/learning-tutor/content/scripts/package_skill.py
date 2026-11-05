#!/usr/bin/env python3
"""打包学习辅导AI技能为 .skill 文件"""

import os
import json
import shutil
import zipfile
import sys
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """将技能打包为 .skill 文件"""
    skill_name = os.path.basename(skill_path)

    # 创建临时打包目录
    temp_dir = f"/tmp/skill_package_{skill_name}"

    # 清理旧目录
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 复制文件到临时目录
    for item in os.listdir(skill_path):
        src = os.path.join(skill_path, item)
        dst = os.path.join(temp_dir, item)

        # 跳过 __pycache__ 等
        if item.startswith('__') or item.startswith('.'):
            continue

        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    # 创建 .skill 文件（实际上是 zip）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    skill_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(temp_dir):
            # 过滤隐藏文件
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]

            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zf.write(file_path, arcname)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    return skill_file

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    try:
        skill_file = package_skill(skill_path, output_dir)
        print(f"✅ 技能打包成功: {skill_file}")
    except Exception as e:
        print(f"❌ 打包失败: {e}")
        sys.exit(1)
