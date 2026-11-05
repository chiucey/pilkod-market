#!/usr/bin/env python3
"""
打包技能脚本
将技能目录打包为 .skill 文件
"""

import os
import json
import shutil
import zipfile
from pathlib import Path


def validate_skill(skill_path: str) -> tuple[bool, str]:
    """验证技能结构"""
    skill_path = Path(skill_path)

    # 检查必需文件
    if not (skill_path / "SKILL.md").exists():
        return False, "SKILL.md not found"

    if not (skill_path / "_meta.json").exists():
        return False, "_meta.json not found"

    # 验证 _meta.json
    meta_path = skill_path / "_meta.json"
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            return False, "_meta.json missing 'id' or 'version'"
    except Exception as e:
        return False, f"Invalid _meta.json: {e}"

    # 验证 SKILL.md frontmatter
    skill_md_path = skill_path / "SKILL.md"
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return False, "SKILL.md must start with frontmatter (---)"

    return True, "OK"


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # 验证
    valid, msg = validate_skill(skill_path)
    if not valid:
        raise ValueError(f"Invalid skill structure: {msg}")

    # 读取 meta
    meta_path = skill_path / "_meta.json"
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 生成输出文件名
    output_file = f"{skill_name}-{meta['version']}.skill"
    output_path = Path(output_dir) / output_file

    # 创建 zip
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    return str(output_path)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    try:
        output_file = package_skill(skill_path, output_dir)
        print(f"Skill packaged successfully: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
