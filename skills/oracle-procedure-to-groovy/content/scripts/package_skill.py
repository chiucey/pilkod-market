#!/usr/bin/env python3
"""
技能打包脚本
将技能目录打包为可分发的.skill文件
"""

import os
import sys
import json
import shutil
import zipfile
from pathlib import Path


def validate_structure(skill_dir: Path) -> tuple[bool, str]:
    """验证技能目录结构"""

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file_name in required_files:
        file_path = skill_dir / file_name
        if not file_path.exists():
            return False, f"缺少必需文件: {file_name}"

    # 验证_meta.json
    meta_path = skill_dir / '_meta.json'
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            return False, "_meta.json缺少id或version字段"
    except json.JSONDecodeError as e:
        return False, f"_meta.json格式错误: {e}"

    # 验证SKILL.md frontmatter
    skill_path = skill_dir / 'SKILL.md'
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return False, "SKILL.md必须以YAML frontmatter开头"

    # 提取frontmatter
    import re
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "SKILL.md frontmatter格式错误"

    # 验证frontmatter字段
    fm_content = frontmatter_match.group(1)
    if 'name:' not in fm_content:
        return False, "SKILL.md frontmatter缺少name字段"
    if 'description:' not in fm_content:
        return False, "SKILL.md frontmatter缺少description字段"

    return True, "验证通过"


def create_package(skill_dir: Path, output_path: Path = None) -> tuple[bool, str]:
    """创建技能包"""

    # 验证结构
    valid, msg = validate_structure(skill_dir)
    if not valid:
        return False, msg

    # 读取meta信息
    meta_path = skill_dir / '_meta.json'
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 生成输出路径
    if output_path is None:
        skill_name = meta.get('name', skill_dir.name)
        output_path = skill_dir.parent / f"{skill_name}.skill"

    # 创建zip包
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in skill_dir.rglob('*'):
                if file_path.is_file():
                    # 跳过隐藏文件和临时文件
                    if any(part.startswith('.') for part in file_path.parts):
                        continue
                    if file_path.suffix in ['.pyc', '__pycache__']:
                        continue

                    arc_name = file_path.relative_to(skill_dir)
                    zf.write(file_path, arc_name)

        return True, str(output_path)
    except Exception as e:
        return False, f"打包失败: {e}"


def extract_package(skill_file: Path, output_dir: Path = None) -> tuple[bool, str]:
    """解压技能包"""

    if output_dir is None:
        output_dir = skill_file.parent / skill_file.stem

    try:
        with zipfile.ZipFile(skill_file, 'r') as zf:
            zf.extractall(output_dir)
        return True, str(output_dir)
    except Exception as e:
        return False, f"解压失败: {e}"


def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description='技能打包工具')
    parser.add_argument('action', choices=['package', 'extract', 'validate'],
                        help='操作: package打包, extract解压, validate验证')
    parser.add_argument('path', help='技能目录或.skill文件路径')
    parser.add_argument('--output', '-o', help='输出路径')

    args = parser.parse_args()

    path = Path(args.path)

    if args.action == 'validate':
        valid, msg = validate_structure(path)
        print(msg)
        sys.exit(0 if valid else 1)

    elif args.action == 'package':
        valid, msg = create_package(path, args.output)
        if valid:
            print(f"技能包已创建: {msg}")
            sys.exit(0)
        else:
            print(f"打包失败: {msg}")
            sys.exit(1)

    elif args.action == 'extract':
        valid, msg = extract_package(path, args.output)
        if valid:
            print(f"技能包已解压: {msg}")
            sys.exit(0)
        else:
            print(f"解压失败: {msg}")
            sys.exit(1)


if __name__ == '__main__':
    main()