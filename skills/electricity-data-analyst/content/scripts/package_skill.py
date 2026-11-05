#!/usr/bin/env python3
"""
技能打包脚本
将技能目录打包成.skill文件
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def get_package_name(skill_path: Path) -> str:
    """
    获取打包文件名

    Args:
        skill_path: 技能目录路径

    Returns:
        打包文件名（不含扩展名）
    """
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        import json
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        skill_name = meta.get('name', skill_path.name)
        version = meta.get('version', '1.0.0')
        return f"{skill_name}_v{version}"

    return f"{skill_path.name}_package"


def scan_directory(path: Path, base_path: Path = None) -> list:
    """
    扫描目录，返回所有文件列表

    Args:
        path: 要扫描的路径
        base_path: 基础路径（用于计算相对路径）

    Returns:
        文件路径列表
    """
    if base_path is None:
        base_path = path

    files = []
    for item in path.iterdir():
        # 跳过隐藏文件和目录
        if item.name.startswith('.') or item.name.startswith('__'):
            continue

        # 跳过临时文件和构建产物
        skip_patterns = [
            '__pycache__',
            '.pyc',
            '.pyo',
            '.egg-info',
            'node_modules',
            '.git'
        ]
        if any(pattern in item.name for pattern in skip_patterns):
            continue

        if item.is_file():
            files.append(item)
        elif item.is_dir():
            files.extend(scan_directory(item, base_path))

    return files


def create_package(skill_path: Path, output_dir: Path = None) -> Path:
    """
    创建技能包

    Args:
        skill_path: 技能目录路径
        output_dir: 输出目录，None则使用skill_path的父目录

    Returns:
        打包文件路径
    """
    skill_path = Path(skill_path).resolve()
    skill_name = get_package_name(skill_path)

    if output_dir is None:
        output_dir = skill_path.parent
    else:
        output_dir = Path(output_dir).resolve()

    output_dir.mkdir(parents=True, exist_ok=True)

    # 创建临时目录
    temp_dir = output_dir / f".temp_{skill_name}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    # 创建包结构
    package_dir = temp_dir / skill_name
    package_dir.mkdir()

    # 复制文件
    files = scan_directory(skill_path)
    for src_file in files:
        rel_path = src_file.relative_to(skill_path)
        dst_file = package_dir / rel_path
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)

    # 打包
    package_file = output_dir / f"{skill_name}.skill"
    with zipfile.ZipFile(package_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in package_dir.rglob('*'):
            if file.is_file():
                arcname = f"{skill_name}/{file.relative_to(package_dir)}"
                zf.write(file, arcname)

    # 清理临时目录
    shutil.rmtree(temp_dir)

    return package_file


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not skill_path.exists():
        print(f"错误: 路径不存在 {skill_path}")
        sys.exit(1)

    if not skill_path.is_dir():
        print(f"错误: 路径不是目录 {skill_path}")
        sys.exit(1)

    print(f"打包技能: {skill_path}")

    try:
        package_file = create_package(skill_path, output_dir)
        print(f"✓ 打包成功: {package_file}")
        print(f"  文件大小: {package_file.stat().st_size / 1024:.2f} KB")
    except Exception as e:
        print(f"✗ 打包失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
