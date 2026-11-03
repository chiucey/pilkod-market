#!/usr/bin/env python3
"""
打包技能脚本 - 生成可发布的.skill文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def collect_skill_files(skill_path: str) -> list:
    """收集技能的所有文件"""
    files = []
    skip_patterns = [
        '__pycache__',
        '.pyc',
        '.git',
        '.DS_Store',
        'node_modules',
        '.venv',
        'venv'
    ]

    for root, dirs, filenames in os.walk(skill_path):
        # 过滤目录
        dirs[:] = [d for d in dirs if d not in skip_patterns]

        for filename in filenames:
            # 跳过临时文件
            if any(pattern in filename for pattern in skip_patterns):
                continue

            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, skill_path)
            files.append((file_path, rel_path))

    return files


def validate_for_packaging(skill_path: str) -> tuple[bool, str]:
    """验证技能是否可以打包"""
    # 检查必需文件
    required = ['SKILL.md', '_meta.json']
    for file in required:
        if not os.path.exists(os.path.join(skill_path, file)):
            return False, f"Missing required file: {file}"

    # 检查_meta.json
    try:
        with open(os.path.join(skill_path, '_meta.json'), 'r') as f:
            meta = json.load(f)

        if 'id' not in meta or 'version' not in meta:
            return False, "_meta.json missing 'id' or 'version'"
    except Exception as e:
        return False, f"Invalid _meta.json: {e}"

    return True, "Valid"


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """
    打包技能为.zip文件

    Returns:
        输出的.zip文件路径
    """
    skill_path = os.path.abspath(skill_path)
    skill_name = os.path.basename(skill_path)

    # 验证
    valid, msg = validate_for_packaging(skill_path)
    if not valid:
        raise ValueError(f"Cannot package skill: {msg}")

    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(skill_path)
    output_dir = os.path.abspath(output_dir)

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    # 创建.zip文件
    files = collect_skill_files(skill_path)

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path, rel_path in files:
            zf.write(file_path, rel_path)

    print(f"Packaged skill: {skill_name}")
    print(f"Files included: {len(files)}")
    print(f"Output: {output_file}")

    return output_file


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"\n✓ Skill packaged successfully!")
        print(f"File: {output_file}")
    except Exception as e:
        print(f"\n✗ Packaging failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
