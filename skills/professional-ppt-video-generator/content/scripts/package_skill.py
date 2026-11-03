#!/usr/bin/env python3
"""
技能打包脚本
将技能目录打包成.skill文件用于分发
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
import sys

def get_skill_info(skill_dir):
    """读取技能信息"""
    meta_path = skill_dir / '_meta.json'
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    return meta

def scan_skill_files(skill_dir, exclude_patterns=None):
    """扫描技能目录下的所有文件"""
    if exclude_patterns is None:
        exclude_patterns = [
            '__pycache__', '*.pyc', '.git', '.DS_Store',
            '*.egg-info', '.pytest_cache', 'node_modules'
        ]

    files = []
    for item in skill_dir.rglob('*'):
        if item.is_file():
            # 检查是否应该排除
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in str(item):
                    should_exclude = True
                    break

            if not should_exclude:
                # 计算相对路径
                rel_path = item.relative_to(skill_dir)
                files.append(rel_path)

    return files

def create_package(skill_dir, output_path=None):
    """创建技能包"""
    skill_dir = Path(skill_dir)

    # 获取技能信息
    meta = get_skill_info(skill_dir)
    skill_name = skill_dir.name
    version = meta.get('version', '1.0.0')

    # 确定输出路径
    if output_path is None:
        output_path = skill_dir.parent / f"{skill_name}.skill"

    # 创建临时目录
    temp_dir = skill_dir.parent / '.temp_package'
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    try:
        # 复制文件到临时目录
        for file_path in scan_skill_files(skill_dir):
            src = skill_dir / file_path
            dst = temp_dir / file_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

        # 创建zip包
        output_path = Path(output_path)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in scan_skill_files(skill_dir):
                file_to_add = temp_dir / file_path
                arcname = str(file_path)
                zf.write(file_to_add, arcname)

        print(f"✓ Package created: {output_path}")
        print(f"  - Skill: {skill_name}")
        print(f"  - Version: {version}")
        print(f"  - Files: {len(scan_skill_files(skill_dir))}")

        return output_path

    finally:
        # 清理临时目录
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def main():
    if len(sys.argv) < 2:
        # 默认打包当前技能
        skill_dir = Path(__file__).parent.parent
    else:
        skill_dir = Path(sys.argv[1])

    if not skill_dir.exists():
        print(f"Error: Directory not found: {skill_dir}")
        return 1

    output = create_package(skill_dir)
    print(f"\nPackage ready: {output.absolute()}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
