#!/usr/bin/env python3
"""
打包脚本 - 将skill打包为.skill文件
"""
import os
import zipfile
import shutil
from datetime import datetime

def package_skill(skill_dir, output_dir='.'):
    """打包skill"""
    skill_name = os.path.basename(skill_dir)

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f'{skill_name}.skill')

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            # 跳过__pycache__等目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)

    print(f"✓ Skill已打包: {output_file}")
    return output_file

if __name__ == '__main__':
    import sys

    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '/workspace/temp-skills/requirements-insight'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '/workspace/temp-skills'

    package_skill(skill_dir, output_dir)
