#!/usr/bin/env python3
"""
打包技能脚本

将技能文件夹打包为 .skill 文件，便于分发和安装。
"""

import os
import shutil
import json
import zipfile
from pathlib import Path


def validate_skill(skill_path: str) -> tuple:
    """验证技能结构和文件"""
    errors = []
    warnings = []

    # 检查必要文件
    skill_md = os.path.join(skill_path, 'SKILL.md')
    meta_json = os.path.join(skill_path, '_meta.json')

    if not os.path.exists(skill_md):
        errors.append("缺少 SKILL.md 文件")
    else:
        # 验证 frontmatter
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.startswith('---'):
                errors.append("SKILL.md 必须以 --- 开头")
            if 'name:' not in content:
                errors.append("SKILL.md 缺少 name 字段")
            if 'description:' not in content:
                errors.append("SKILL.md 缺少 description 字段")

    if not os.path.exists(meta_json):
        errors.append("缺少 _meta.json 文件")
    else:
        # 验证 meta.json 格式
        with open(meta_json, 'r', encoding='utf-8') as f:
            try:
                meta = json.load(f)
                if 'id' not in meta:
                    errors.append("_meta.json 缺少 id 字段")
                if 'version' not in meta:
                    errors.append("_meta.json 缺少 version 字段")
            except json.JSONDecodeError:
                errors.append("_meta.json 格式错误")

    return errors, warnings


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能"""
    skill_name = os.path.basename(skill_path.rstrip('/'))

    # 验证
    errors, warnings = validate_skill(skill_path)
    if errors:
        print("验证失败:")
        for e in errors:
            print(f"  - {e}")
        return None

    # 输出目录
    if output_dir is None:
        output_dir = os.path.dirname(skill_path)
    os.makedirs(output_dir, exist_ok=True)

    # 创建 .skill 文件
    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # 跳过 __pycache__ 等目录
            dirs[:] = [d for d in dirs if not d.startswith('__') and d != '__pycache__']

            for file in files:
                if file.endswith('.pyc'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zipf.write(file_path, arcname)

    print(f"技能已打包: {output_file}")
    return output_file


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        skill_path = '/workspace/temp-skills/schedule-overview'
    else:
        skill_path = sys.argv[1]

    result = package_skill(skill_path)
    if result:
        print(f"\n打包成功！")
        print(f"输出文件: {result}")
    else:
        print("\n打包失败，请检查错误信息")
        sys.exit(1)
