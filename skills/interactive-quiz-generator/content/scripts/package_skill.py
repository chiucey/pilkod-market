#!/usr/bin/env python3
"""
Package Skill Script
将技能打包为可分发的 .skill 文件
"""

import json
import zipfile
import shutil
import sys
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: Path, output_dir: Path = None) -> Path:
    """
    打包技能为 .skill 文件

    Args:
        skill_path: 技能目录路径
        output_dir: 输出目录（默认与技能目录同级）

    Returns:
        打包文件路径
    """
    skill_path = Path(skill_path).resolve()

    if not skill_path.exists() or not skill_path.is_dir():
        raise ValueError(f"技能路径无效: {skill_path}")

    # 读取元数据
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        raise ValueError("_meta.json 不存在")

    meta = json.loads(meta_file.read_text(encoding='utf-8'))
    skill_name = skill_path.name
    version = meta.get('version', '1.0.0')

    # 设置输出目录
    if output_dir is None:
        output_dir = skill_path.parent
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建打包文件名
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    package_name = f"{skill_name}_v{version}_{timestamp}.skill"
    package_path = output_dir / package_name

    # 打包文件
    exclude_patterns = {
        '__pycache__', '*.pyc', '.git', '.DS_Store',
        'node_modules', '.venv', 'venv', '.idea', '.vscode'
    }

    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                # 检查是否应该排除
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern in str(file_path):
                        should_exclude = True
                        break

                if should_exclude:
                    continue

                # 添加到压缩包
                arc_name = file_path.relative_to(skill_path)
                zf.write(file_path, arc_name)

    print(f"✓ 技能已打包: {package_path}")
    print(f"  - 名称: {skill_name}")
    print(f"  - 版本: {version}")
    print(f"  - 大小: {package_path.stat().st_size / 1024:.1f} KB")

    return package_path


def extract_skill(package_path: Path, extract_dir: Path = None) -> Path:
    """
    解压技能包

    Args:
        package_path: .skill 文件路径
        extract_dir: 解压目录

    Returns:
        解压后的技能目录路径
    """
    package_path = Path(package_path).resolve()

    if not package_path.exists() or package_path.suffix != '.skill':
        raise ValueError(f"无效的技能包: {package_path}")

    if extract_dir is None:
        extract_dir = package_path.parent
    extract_dir = Path(extract_dir)

    # 解压
    with zipfile.ZipFile(package_path, 'r') as zf:
        zf.extractall(extract_dir)

    print(f"✓ 技能已解压到: {extract_dir}")
    return extract_dir


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='技能打包工具')
    parser.add_argument('action', choices=['pack', 'extract'],
                        help='操作: pack 打包, extract 解压')
    parser.add_argument('path', help='技能目录或技能包路径')
    parser.add_argument('--output', '-o', help='输出目录')

    args = parser.parse_args()

    if args.action == 'pack':
        package_skill(args.path, args.output)
    elif args.action == 'extract':
        extract_skill(args.path, args.output)


if __name__ == '__main__':
    main()
