#!/usr/bin/env python3
"""
打包开源项目教程生成器技能为 .skill 文件
"""

import os
import shutil
import zipfile
import json
from pathlib import Path
from datetime import datetime

def collect_skill_files(base_path):
    """收集技能的所有文件"""
    files_to_package = []

    for root, dirs, files in os.walk(base_path):
        # 跳过 __pycache__ 等目录
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]

        for file in files:
            if file.endswith('.pyc'):
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, base_path)
            files_to_package.append({
                'full_path': full_path,
                'rel_path': rel_path
            })

    return files_to_package

def create_skill_package(base_path, output_path):
    """创建技能包"""
    print("=" * 60)
    print("开源项目教程生成器 - 打包工具")
    print("=" * 60)
    print()

    # 获取技能名称
    skill_name = os.path.basename(base_path)
    print(f"技能名称: {skill_name}")

    # 收集文件
    print("收集文件...")
    files = collect_skill_files(base_path)
    print(f"找到 {len(files)} 个文件:")
    for f in files:
        print(f"  - {f['rel_path']}")
    print()

    # 创建包
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"{skill_name}_{timestamp}.skill"
    zip_path = os.path.join(output_path, zip_name)

    print(f"创建包文件: {zip_name}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_info in files:
            zipf.write(
                file_info['full_path'],
                file_info['rel_path']
            )
            print(f"  添加: {file_info['rel_path']}")

    # 验证包
    print()
    print("验证包内容...")
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        file_list = zipf.namelist()
        print(f"包内文件数: {len(file_list)}")

        # 检查必需文件
        required = ['SKILL.md', '_meta.json']
        for req in required:
            if req not in file_list:
                print(f"  ⚠️ 警告: 缺少必需文件 {req}")
            else:
                print(f"  ✓ {req}")

    print()
    print("=" * 60)
    print(f"✅ 打包完成!")
    print(f"包文件路径: {zip_path}")
    print("=" * 60)

    return zip_path

def main():
    import sys

    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(base_path)

    # 确定输出路径（与技能目录同级）
    output_path = os.path.dirname(base_path)

    create_skill_package(base_path, output_path)

if __name__ == "__main__":
    main()
