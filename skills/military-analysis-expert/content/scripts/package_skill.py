#!/usr/bin/env python3
"""
Military Analysis Expert Skill - Package Script
打包军事分析专家技能为可发布的 .skill 文件
"""

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path


def validate_skill_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """验证技能目录结构"""
    errors = []

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = skill_path / file
        if not file_path.exists():
            errors.append(f"Missing required file: {file}")

    # 检查 _meta.json 格式
    meta_path = skill_path / '_meta.json'
    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # 检查 SKILL.md frontmatter
    skill_md_path = skill_path / 'SKILL.md'
    if skill_md_path.exists():
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter (---)")

        if 'name:' not in content:
            errors.append("SKILL.md missing 'name:' in frontmatter")
        if 'description:' not in content:
            errors.append("SKILL.md missing 'description:' in frontmatter")

    return len(errors) == 0, errors


def package_skill(skill_path: str, output_dir: str = '.'):
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)

    if not skill_path.exists():
        print(f"Error: Skill path does not exist: {skill_path}")
        sys.exit(1)

    # 验证结构
    valid, errors = validate_skill_structure(skill_path)
    if not valid:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print(f"Validating skill structure...")
    print(f"Skill path: {skill_path}")

    # 读取元数据
    with open(skill_path / '_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_name = skill_path.name
    skill_id = meta.get('id', 'unknown')
    skill_version = meta.get('version', '1.0.0')

    # 创建输出文件名
    output_file = output_dir / f"{skill_name}.skill"

    # 创建 .skill 文件（本质上是 zip 文件）
    print(f"Creating package: {output_file}")

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path.parent)
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    print(f"\nPackage created successfully!")
    print(f"Skill ID: {skill_id}")
    print(f"Skill Version: {skill_version}")
    print(f"Output: {output_file.absolute()}")

    return output_file


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'

    package_skill(skill_path, output_dir)
