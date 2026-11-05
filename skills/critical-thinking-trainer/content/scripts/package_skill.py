#!/usr/bin/env python3
"""
批判性思维训练师技能打包脚本
"""

import json
import os
import shutil
import zipfile
from pathlib import Path

def validate_skill_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证技能结构"""
    errors = []
    skill_path = Path(skill_path)

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        if not (skill_path / file).exists():
            errors.append(f"缺少必需文件: {file}")

    # 验证 SKILL.md frontmatter
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.startswith('---'):
                errors.append("SKILL.md 必须以 YAML frontmatter 开头")
            if 'name:' not in content[:500]:
                errors.append("SKILL.md 缺少 name 字段")
            if 'description:' not in content[:500]:
                errors.append("SKILL.md 缺少 description 字段")

    # 验证 _meta.json
    meta_json = skill_path / '_meta.json'
    if meta_json.exists():
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")

    return len(errors) == 0, errors

def package_skill(skill_path: str, output_dir: str = '/workspace/temp-skills') -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 验证结构
    valid, errors = validate_skill_structure(skill_path)
    if not valid:
        raise ValueError(f"技能结构验证失败: {', '.join(errors)}")

    # 创建打包目录
    package_name = f"{skill_path.name}.skill"
    package_path = output_dir / package_name

    # 创建 ZIP 文件
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    return str(package_path)

if __name__ == '__main__':
    import sys

    skill_path = sys.argv[1] if len(sys.argv) > 1 else '/workspace/temp-skills/critical-thinking-trainer'

    print(f"正在打包技能: {skill_path}")

    try:
        output_path = package_skill(skill_path)
        print(f"打包成功: {output_path}")

        # 验证打包内容
        with zipfile.ZipFile(output_path, 'r') as zf:
            print("\n打包内容:")
            for name in zf.namelist():
                print(f"  - {name}")

    except ValueError as e:
        print(f"打包失败: {e}")
        sys.exit(1)
