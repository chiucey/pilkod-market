#!/usr/bin/env python3
"""
技能打包脚本
将技能打包为 .skill 文件
"""

import os
import sys
import json
import zipfile
import argparse
from pathlib import Path
from typing import List, Set


# 需要排除的文件/目录
EXCLUDE_PATTERNS: Set[str] = {
    '.DS_Store',
    'Thumbs.db',
    '__pycache__',
    '.git',
    '.svn',
    '.pytest_cache',
    '.tox',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.Python',
    '*.egg-info',
    '.venv',
    'venv',
    'env',
    'node_modules',
    'package-lock.json',
    'yarn.lock',
    # 排除临时文件和验证输出
    'test_output',
    'dist',
    'build',
    '.coverage',
    'htmlcov',
}

# 需要包含的目录
REQUIRED_DIRS: List[str] = [
    'scripts',
]


def should_exclude(path: Path) -> bool:
    """检查路径是否应该被排除"""
    name = path.name

    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith('*'):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True

    return False


def collect_files(skill_dir: Path) -> List[Path]:
    """收集需要打包的文件"""
    files = []

    for root, dirs, filenames in os.walk(skill_dir):
        root_path = Path(root)

        # 过滤目录
        dirs[:] = [d for d in dirs if not should_exclude(root_path / d)]

        for filename in filenames:
            file_path = root_path / filename
            if not should_exclude(file_path):
                # 计算相对于 skill_dir 的路径
                rel_path = file_path.relative_to(skill_dir)
                files.append(rel_path)

    return sorted(files)


def package_skill(skill_path: str, output_path: str = None) -> bool:
    """
    打包技能

    Args:
        skill_path: 技能目录路径
        output_path: 输出文件路径（可选）

    Returns:
        是否成功
    """
    skill_dir = Path(skill_path).resolve()

    if not skill_dir.exists():
        print(f"❌ 技能目录不存在: {skill_path}")
        return False

    if not skill_dir.is_dir():
        print(f"❌ 路径不是目录: {skill_path}")
        return False

    # 收集文件
    files = collect_files(skill_dir)
    if not files:
        print("❌ 没有文件可打包")
        return False

    # 确定输出路径
    if output_path is None:
        output_path = str(skill_dir.parent / f"{skill_dir.name}.skill")

    # 创建 ZIP 文件
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in files:
                full_path = skill_dir / file_path
                zf.write(full_path, file_path)

        print(f"✅ 技能已打包: {output_path}")
        print(f"   包含 {len(files)} 个文件")
        return True

    except Exception as e:
        print(f"❌ 打包失败: {e}")
        return False


def extract_skill(skill_path: str, output_dir: str = None) -> bool:
    """
    解压技能包

    Args:
        skill_path: .skill 文件路径
        output_dir: 输出目录（可选，默认解压到同名目录）

    Returns:
        是否成功
    """
    skill_file = Path(skill_path).resolve()

    if not skill_file.exists():
        print(f"❌ 技能文件不存在: {skill_path}")
        return False

    if not skill_file.suffix == '.skill':
        print("❌ 文件不是 .skill 格式")
        return False

    # 确定输出目录
    if output_dir is None:
        output_dir = str(skill_file.with_suffix(''))

    try:
        with zipfile.ZipFile(skill_file, 'r') as zf:
            zf.extractall(output_dir)

        print(f"✅ 技能已解压到: {output_dir}")
        return True

    except Exception as e:
        print(f"❌ 解压失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='技能打包工具')
    parser.add_argument('command', choices=['pack', 'extract'],
                      help='命令: pack 打包, extract 解压')
    parser.add_argument('path', help='技能目录或 .skill 文件路径')
    parser.add_argument('--output', '-o', help='输出路径')

    args = parser.parse_args()

    if args.command == 'pack':
        success = package_skill(args.path, args.output)
    else:
        success = extract_skill(args.path, args.output)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
