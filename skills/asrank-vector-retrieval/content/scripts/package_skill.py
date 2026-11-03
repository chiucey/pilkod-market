#!/usr/bin/env python3
"""
技能打包脚本

将技能文件夹打包为 .skill 文件用于分发
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path


def validate_skill(skill_dir: Path) -> tuple[bool, list]:
    """
    验证技能结构

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # 检查必需文件
    if not (skill_dir / "SKILL.md").exists():
        errors.append("Missing SKILL.md")

    if not (skill_dir / "_meta.json").exists():
        errors.append("Missing _meta.json")

    # 验证SKILL.md的frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')

        # 检查frontmatter格式
        if not content.startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter (---)")

        # 检查必需字段
        if 'name:' not in content:
            errors.append("SKILL.md missing 'name' field in frontmatter")

        if 'description:' not in content:
            errors.append("SKILL.md missing 'description' field in frontmatter")

    # 验证_meta.json
    meta_file = skill_dir / "_meta.json"
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding='utf-8'))
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    return len(errors) == 0, errors


def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    """
    打包技能

    Args:
        skill_dir: 技能目录
        output_dir: 输出目录

    Returns:
        打包文件路径
    """
    # 验证
    is_valid, errors = validate_skill(skill_dir)
    if not is_valid:
        print("Validation errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # 读取元数据
    meta = json.loads((skill_dir / "_meta.json").read_text(encoding='utf-8'))
    skill_name = skill_dir.name

    # 生成输出文件名
    output_file = output_dir / f"{skill_name}.skill"

    # 创建压缩包
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file():
                # 计算相对路径
                rel_path = file_path.relative_to(skill_dir)

                # 排除敏感文件
                if any(part.startswith('.') for part in rel_path.parts):
                    continue
                if 'node_modules' in str(rel_path):
                    continue

                zf.write(file_path, rel_path)

    print(f"Skill packaged: {output_file}")
    return output_file


def main():
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_directory> [output_directory]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else skill_dir.parent

    if not skill_dir.exists():
        print(f"Error: Skill directory not found: {skill_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    package_skill(skill_dir, output_dir)


if __name__ == "__main__":
    main()
