#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""

import os
import sys
import json
import shutil
import zipfile
from datetime import datetime


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """
    打包技能为 .skill 文件

    Args:
        skill_path: 技能目录路径
        output_dir: 输出目录，默认在 skill 目录下

    Returns:
        打包后的文件路径
    """
    skill_name = os.path.basename(skill_path)

    print("=" * 50)
    print("技能打包")
    print("=" * 50)

    # 验证必需文件
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        filepath = os.path.join(skill_path, filename)
        if not os.path.exists(filepath):
            print(f"错误: 缺少必需文件 {filename}")
            sys.exit(1)

    # 读取meta信息
    with open(os.path.join(skill_path, '_meta.json'), 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 生成输出文件名
    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d')
    output_filename = f"{skill_name}_{meta['version']}_{timestamp}.skill"
    output_path = os.path.join(output_dir, output_filename)

    # 创建打包文件
    print(f"正在打包: {skill_name}")
    print(f"版本: {meta['version']}")

    # 收集所有文件
    files_to_package = []
    for root, dirs, files in os.walk(skill_path):
        # 排除隐藏文件和目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.startswith('.'):
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, skill_path)
            files_to_package.append((full_path, rel_path))

    print(f"文件数量: {len(files_to_package)}")

    # 创建ZIP文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for full_path, rel_path in files_to_package:
            zf.write(full_path, arcname=rel_path)
            print(f"  + {rel_path}")

    # 验证打包结果
    with zipfile.ZipFile(output_path, 'r') as zf:
        file_count = len(zf.namelist())

    print(f"\n打包完成: {output_path}")
    print(f"打包文件数: {file_count}")

    # 清理临时文件
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"打包文件大小: {size / 1024:.2f} KB")

    print("=" * 50)

    return output_path


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/douyin-search-assistant"
    package_skill(skill_path)
