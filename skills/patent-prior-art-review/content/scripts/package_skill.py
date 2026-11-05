#!/usr/bin/env python3
"""
Patent Prior Art Review Skill Packager
打包技能为可分发的.skill文件
"""

import os
import json
import shutil
import sys
import tarfile
from pathlib import Path
from datetime import datetime


def collect_skill_files(skill_path: str) -> list[str]:
    """收集技能目录下的所有文件"""
    files = []
    exclude_patterns = [
        '__pycache__',
        '.pyc',
        '.git',
        '.DS_Store',
        '*.tmp'
    ]

    for root, dirs, filenames in os.walk(skill_path):
        # 过滤目录
        dirs[:] = [d for d in dirs if d not in exclude_patterns and not d.startswith('.')]

        for filename in filenames:
            if any(pattern in filename for pattern in exclude_patterns):
                continue
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, skill_path)
            files.append(rel_path)

    return files


def create_skill_package(skill_path: str, output_dir: str = None) -> str:
    """创建技能包"""
    skill_name = os.path.basename(skill_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    output_file = os.path.join(output_dir, f"{skill_name}_{timestamp}.skill")

    # 创建tar.gz包
    with tarfile.open(output_file, 'w:gz') as tar:
        files = collect_skill_files(skill_path)
        for file_path in files:
            full_path = os.path.join(skill_path, file_path)
            tar.add(full_path, arcname=file_path)

    return output_file


def validate_before_pack(skill_path: str) -> tuple[bool, list[str]]:
    """打包前验证"""
    errors = []

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for req_file in required_files:
        if not os.path.exists(os.path.join(skill_path, req_file)):
            errors.append(f"缺少必需文件: {req_file}")

    # 验证_meta.json
    meta_path = os.path.join(skill_path, '_meta.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            if 'id' not in meta or 'version' not in meta:
                errors.append("_meta.json缺少id或version字段")
        except json.JSONDecodeError:
            errors.append("_meta.json格式错误")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    else:
        skill_path = sys.argv[1]

    print(f"打包技能: {skill_path}")
    print("-" * 50)

    # 打包前验证
    passed, errors = validate_before_pack(skill_path)
    if not passed:
        print("✗ 打包前验证失败:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("✓ 打包前验证通过")

    # 创建包
    output_file = create_skill_package(skill_path)
    print(f"✓ 技能包已创建: {output_file}")

    # 显示包内容
    print("-" * 50)
    print("包内容:")
    with tarfile.open(output_file, 'r:gz') as tar:
        for member in tar.getmembers():
            print(f"  - {member.name}")

    print("-" * 50)
    print("✓ 打包完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())