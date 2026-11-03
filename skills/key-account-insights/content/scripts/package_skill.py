#!/usr/bin/env python3
"""
Skill Package Script - Key Account Insights
打包技能为可分发的 .skill 文件
"""

import os
import json
import zipfile
from datetime import datetime
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
        elif not file_path.is_file():
            errors.append(f"{file} is not a file")

    # 验证 SKILL.md frontmatter
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.startswith('---'):
                errors.append("SKILL.md must start with YAML frontmatter (---)")
            if 'name:' not in content[:500]:
                errors.append("SKILL.md missing 'name' in frontmatter")
            if 'description:' not in content[:500]:
                errors.append("SKILL.md missing 'description' in frontmatter")

    # 验证 _meta.json
    meta_json = skill_path / '_meta.json'
    if meta_json.exists():
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                if 'id' not in meta:
                    errors.append("_meta.json missing 'id' field")
                if 'version' not in meta:
                    errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    return len(errors) == 0, errors


def get_skill_name(skill_path: Path) -> str:
    """从 SKILL.md 获取技能名称"""
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return skill_path.name

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
        # 解析 frontmatter
        if content.startswith('---'):
            end_idx = content.find('---', 3)
            if end_idx > 0:
                frontmatter = content[3:end_idx]
                for line in frontmatter.split('\n'):
                    if line.startswith('name:'):
                        return line.split(':', 1)[1].strip()

    return skill_path.name


def package_skill(skill_path: str, output_dir: str = None) -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        raise FileNotFoundError(f"Skill path does not exist: {skill_path}")

    # 验证结构
    is_valid, errors = validate_skill_structure(skill_path)
    if not is_valid:
        raise ValueError(f"Skill validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    # 获取技能名称
    skill_name = get_skill_name(skill_path)

    # 确定输出路径
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = skill_path.parent

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = output_path / f"{skill_name}_{timestamp}.skill"

    # 创建 zip 文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # 计算相对路径
                arcname = file_path.relative_to(skill_path)
                zipf.write(file_path, arcname)

    return str(output_file)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='Package skill to .skill file')
    parser.add_argument('skill_path', help='Path to skill directory')
    parser.add_argument('--output', '-o', help='Output directory (optional)')

    args = parser.parse_args()

    try:
        output_file = package_skill(args.skill_path, args.output)
        print(f"✓ Skill packaged successfully: {output_file}")

        # 显示包含的文件
        skill_path = Path(args.skill_path)
        print("\nIncluded files:")
        for file_path in sorted(skill_path.rglob('*')):
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"  {file_path.relative_to(skill_path)} ({size:,} bytes)")

    except Exception as e:
        print(f"✗ Error: {e}")
        exit(1)


if __name__ == '__main__':
    main()
