#!/usr/bin/env python3
"""
证据整理技能打包脚本
将技能目录打包为 .skill 文件
"""

import os
import zipfile
import json
import sys
from datetime import datetime

def validate_skill(skill_dir):
    """验证技能结构"""
    errors = []

    # 检查必要文件
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        path = os.path.join(skill_dir, f)
        if not os.path.exists(path):
            errors.append(f"缺少必要文件: {f}")

    # 验证 meta.json
    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON格式错误: {e}")

    # 验证 SKILL.md frontmatter
    skill_path = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_path):
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否以 --- 开头
        if not content.strip().startswith('---'):
            errors.append("SKILL.md 必须以 YAML frontmatter (---) 开头")

        # 检查 name 和 description 字段
        if 'name:' not in content:
            errors.append("SKILL.md frontmatter 缺少 name 字段")
        if 'description:' not in content:
            errors.append("SKILL.md frontmatter 缺少 description 字段")

    return errors

def package_skill(skill_dir, output_dir=None):
    """打包技能"""
    skill_name = os.path.basename(skill_dir)

    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)

    # 验证
    errors = validate_skill(skill_dir)
    if errors:
        print("验证失败:")
        for e in errors:
            print(f"  - {e}")
        return False

    # 创建 .skill 文件
    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, skill_dir)
                zf.write(file_path, arc_name)

    print(f"技能打包成功: {output_file}")
    print(f"技能名称: {skill_name}")

    # 列出包含的文件
    with zipfile.ZipFile(output_file, 'r') as zf:
        print("\n包含文件:")
        for name in zf.namelist():
            print(f"  - {name}")

    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_dir> [output_dir]")
        sys.exit(1)

    skill_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(skill_dir):
        print(f"错误: 目录不存在 {skill_dir}")
        sys.exit(1)

    success = package_skill(skill_dir, output_dir)
    sys.exit(0 if success else 1)
