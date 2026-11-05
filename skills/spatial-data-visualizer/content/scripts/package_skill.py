#!/usr/bin/env python3
"""
技能打包脚本 - 将技能打包为可分发的 .skill 文件

用法:
    python package_skill.py <skill_path> [--output <output.skill>]
"""

import json
import os
import zipfile
import shutil
import argparse
from pathlib import Path


def get_skill_meta(skill_path: Path) -> dict:
    """读取技能元数据"""
    meta_file = skill_path / '_meta.json'
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def is_safe_path(path: Path, base: Path) -> bool:
    """检查路径是否在基目录内（防止路径穿越）"""
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def package_skill(skill_path: str, output_path: str = None) -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path).resolve()
    skill_name = skill_path.name

    # 读取元数据
    meta = get_skill_meta(skill_path)
    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # 确定输出路径
    if output_path:
        output_path = Path(output_path)
    else:
        output_path = skill_path.parent / f"{skill_name}.skill"

    # 创建临时目录
    temp_dir = skill_path.parent / f".temp_{skill_name}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    try:
        # 创建打包目录结构
        pkg_dir = temp_dir / skill_name
        pkg_dir.mkdir()

        # 复制文件（排除隐藏文件和临时文件）
        ignore_patterns = ['.git', '__pycache__', '.DS_Store', '*.pyc']

        def should_ignore(name: str) -> bool:
            for pattern in ignore_patterns:
                if pattern.startswith('*') and name.endswith(pattern[1:]):
                    return True
                if pattern in name:
                    return True
            return False

        for item in skill_path.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(skill_path)

                # 检查是否是隐藏文件或临时文件
                if any(part.startswith('.') for part in rel_path.parts):
                    continue
                if should_ignore(item.name):
                    continue

                # 确保路径安全
                dest = pkg_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)

                # 检查路径安全
                if not is_safe_path(item, skill_path):
                    print(f"警告: 跳过不安全的路径 {rel_path}")
                    continue

                shutil.copy2(item, dest)

        # 创建 .skill 文件（本质是 zip）
        if output_path.exists():
            output_path.unlink()

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for item in pkg_dir.rglob('*'):
                if item.is_file():
                    arcname = item.relative_to(pkg_dir)
                    zf.write(item, arcname)

        print(f"技能打包完成: {output_path}")
        print(f"  - ID: {skill_id}")
        print(f"  - Version: {version}")
        print(f"  - 文件数: {len(list(pkg_dir.rglob('*.*')))}")

        return str(output_path)

    finally:
        # 清理临时目录
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def extract_skill(skill_file: str, output_dir: str = None) -> str:
    """解压 .skill 文件"""
    skill_file = Path(skill_file)

    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = skill_file.parent / skill_file.stem

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 解压
    with zipfile.ZipFile(skill_file, 'r') as zf:
        zf.extractall(output_dir)

    print(f"技能解压到: {output_dir}")
    return str(output_dir)


def main():
    parser= argparse.ArgumentParser(description='技能打包工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')

    # pack 命令
    pack_parser = subparsers.add_parser('pack', help='打包技能')
    pack_parser.add_argument('skill_path', help='技能目录路径')
    pack_parser.add_argument('-o', '--output', help='输出文件路径')

    # unpack 命令
    unpack_parser = subparsers.add_parser('unpack', help='解压技能')
    unpack_parser.add_argument('skill_file', help='.skill 文件路径')
    unpack_parser.add_argument('-o', '--output', help='输出目录路径')

    args = parser.parse_args()

    if args.command == 'pack':
        package_skill(args.skill_path, args.output)
    elif args.command == 'unpack':
        extract_skill(args.skill_file, args.output)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()