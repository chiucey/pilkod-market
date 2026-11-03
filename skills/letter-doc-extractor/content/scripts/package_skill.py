#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能打包脚本 - 将技能打包为 .skill 文件
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime


def validate_skill(skill_path: str) -> bool:
    """验证技能结构"""
    errors = []

    # 检查必需文件
    required_files = [
        "SKILL.md",
        "_meta.json"
    ]

    for f in required_files:
        if not os.path.exists(os.path.join(skill_path, f)):
            errors.append(f"缺少必需文件: {f}")

    # 验证 _meta.json
    meta_path = os.path.join(skill_path, "_meta.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except Exception as e:
            errors.append(f"_meta.json 解析错误: {e}")

    # 验证 SKILL.md frontmatter
    skill_path_file = os.path.join(skill_path, "SKILL.md")
    if os.path.exists(skill_path_file):
        with open(skill_path_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头")

        # 解析 frontmatter
        if content.startswith('---'):
            end_idx = content.find('---', 3)
            if end_idx > 0:
                frontmatter = content[3:end_idx].strip()
                if 'name:' not in frontmatter:
                    errors.append("SKILL.md frontmatter 缺少 'name' 字段")
                if 'description:' not in frontmatter:
                    errors.append("SKILL.md frontmatter 缺少 'description' 字段")

    if errors:
        print("验证失败:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("验证通过!")
    return True


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能"""
    skill_name = os.path.basename(skill_path)

    if not validate_skill(skill_path):
        print("打包终止: 技能验证失败")
        sys.exit(1)

    # 创建临时打包目录
    temp_dir = os.path.join(os.path.dirname(skill_path), f"_pkg_{skill_name}")
    os.makedirs(temp_dir, exist_ok=True)

    # 复制文件（排除临时文件）
    exclude_patterns = ['__pycache__', '.pyc', '.DS_Store', '.git']
    for root, dirs, files in os.walk(skill_path):
        # 过滤目录
        dirs[:] = [d for d in dirs if not any(p in d for p in exclude_patterns)]

        for file in files:
            if any(p in file for p in exclude_patterns):
                continue

            src = os.path.join(root, file)
            rel_path = os.path.relpath(src, skill_path)
            dst = os.path.join(temp_dir, rel_path)

            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    # 创建 .skill 文件（zip格式）
    if output_dir is None:
        output_dir = os.path.dirname(skill_path)

    date_str = datetime.now().strftime("%Y%m%d")
    skill_file = os.path.join(output_dir, f"{skill_name}_{date_str}.skill")

    shutil.make_archive(
        skill_file.replace('.skill', ''),
        'zip',
        temp_dir
    )

    # 重命名为 .skill
    zip_file = skill_file.replace('.skill', '.zip')
    if os.path.exists(zip_file):
        os.rename(zip_file, skill_file)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    print(f"打包完成: {skill_file}")
    return skill_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    package_skill(skill_path, output_dir)
