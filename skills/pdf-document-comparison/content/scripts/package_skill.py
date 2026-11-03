#!/usr/bin/env python3
"""
技能打包脚本
"""

import os
import json
import shutil
import zipfile
from pathlib import Path


def validate_skill(skill_dir: Path) -> bool:
    """验证技能结构"""
    errors = []

    # 检查必要文件
    if not (skill_dir / 'SKILL.md').exists():
        errors.append("缺少 SKILL.md")
    if not (skill_dir / '_meta.json').exists():
        errors.append("缺少 _meta.json")

    # 检查 _meta.json 内容
    meta_path = skill_dir / '_meta.json'
    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            errors.append("_meta.json 格式错误")

    # 检查 SKILL.md frontmatter
    skill_md = skill_dir / 'SKILL.md'
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            errors.append("SKILL.md 必须以 frontmatter 开头")

        # 解析 frontmatter
        if '---' in content:
            frontmatter = content.split('---')[1]
            if 'name:' not in frontmatter:
                errors.append("frontmatter 缺少 name 字段")
            if 'description:' not in frontmatter:
                errors.append("frontmatter 缺少 description 字段")

    if errors:
        print("验证失败:")
        for err in errors:
            print(f"  - {err}")
        return False

    print("验证通过!")
    return True


def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    """打包技能"""
    skill_name = skill_dir.name
    output_file = output_dir / f"{skill_name}.skill"

    # 创建 zip 文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item in skill_dir.rglob('*'):
            if item.is_file() and '__pycache__' not in str(item):
                arcname = item.relative_to(skill_dir)
                zf.write(item, arcname)

    print(f"打包完成: {output_file}")
    return output_file


def main():
    import argparse

    parser = argparse.ArgumentParser(description='打包技能')
    parser.add_argument('skill_dir', help='技能目录路径')
    parser.add_argument('-o', '--output', help='输出目录（默认当前目录）')

    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)
    output_dir = Path(args.output) if args.output else Path.cwd()

    if not skill_dir.exists():
        print(f"错误: 目录不存在 {skill_dir}")
        return

    print(f"正在验证技能: {skill_dir}")
    if not validate_skill(skill_dir):
        return

    print(f"正在打包...")
    output_file = package_skill(skill_dir, output_dir)

    print(f"\n打包成功!")
    print(f"输出文件: {output_file.absolute()}")


if __name__ == "__main__":
    main()
