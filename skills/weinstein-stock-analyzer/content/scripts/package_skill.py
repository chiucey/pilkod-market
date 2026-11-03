#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能打包脚本
"""

import os
import sys
import json
import shutil
from pathlib import Path
import zipfile


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能为.skill文件"""
    print("=" * 60)
    print("笑傲牛熊技能打包")
    print("=" * 60)

    skill_path = os.path.abspath(skill_path)
    skill_name = os.path.basename(skill_path)

    # 读取meta
    meta_path = os.path.join(skill_path, '_meta.json')
    if not os.path.exists(meta_path):
        print("❌ 错误: 缺少_meta.json文件")
        return None

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # 创建输出文件名
    output_file = os.path.join(output_dir, f"{skill_name}_{skill_id}_{version}.skill")
    output_file = os.path.abspath(output_file)

    # 创建临时目录
    temp_dir = os.path.join(output_dir, f".temp_{skill_name}")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 复制文件
    files_to_include = [
        'SKILL.md',
        '_meta.json',
    ]

    dirs_to_include = [
        'references',
        'scripts',
    ]

    for f in files_to_include:
        src = os.path.join(skill_path, f)
        if os.path.exists(src):
            shutil.copy2(src, temp_dir)
            print(f"✓ 包含: {f}")

    for d in dirs_to_include:
        src = os.path.join(skill_path, d)
        if os.path.exists(src):
            dst = os.path.join(temp_dir, d)
            shutil.copytree(src, dst)
            print(f"✓ 包含目录: {d}/")

    # 创建zip
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    print()
    print("=" * 60)
    print(f"✓ 打包完成!")
    print(f"输出文件: {output_file}")
    print("=" * 60)

    return output_file


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    package_skill(skill_path, output_dir)
