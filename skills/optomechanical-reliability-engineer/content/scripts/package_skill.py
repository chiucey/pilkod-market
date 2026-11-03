#!/usr/bin/env python3
"""
技能打包脚本
将技能目录打包成.skill文件用于分发
"""

import os
import sys
import json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

def scan_directory(base_path, exclude_patterns=None):
    """扫描目录中的所有文件"""
    if exclude_patterns is None:
        exclude_patterns = [
            '__pycache__',
            '.git',
            '.DS_Store',
            '*.pyc',
            'node_modules',
            '.venv'
        ]

    files = []
    for root, dirs, filenames in os.walk(base_path):
        # 过滤目录
        dirs[:] = [d for d in dirs if d not in exclude_patterns]

        for filename in filenames:
            # 过滤文件
            skip = False
            for pattern in exclude_patterns:
                if pattern.startswith('*') and filename.endswith(pattern[1:]):
                    skip = True
                    break
                if pattern in filename:
                    skip = True
                    break

            if not skip:
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, base_path)
                files.append(rel_path)

    return files

def create_skill_package(skill_dir, output_dir=None):
    """创建技能包"""
    skill_path = Path(skill_dir)
    skill_name = skill_path.name

    if output_dir is None:
        output_dir = skill_path.parent
    else:
        output_dir = Path(output_dir)

    # 读取meta信息
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        version = meta.get('version', '1.0.0')
        skill_id = meta.get('id', 'unknown')
    else:
        version = '1.0.0'
        skill_id = 'unknown'

    # 生成包文件名
    timestamp = datetime.now().strftime('%Y%m%d')
    package_name = f"{skill_name}_{version}_{timestamp}.skill"
    package_path = output_dir / package_name

    # 扫描文件
    files = scan_directory(skill_path)

    print(f"打包技能: {skill_name}")
    print(f"版本: {version}")
    print(f"技能ID: {skill_id}")
    print(f"文件数量: {len(files)}")
    print("-" * 50)

    # 创建zip包
    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            full_path = skill_path / file_path
            print(f"  + {file_path}")
            zf.write(full_path, file_path)

    print("-" * 50)
    print(f"打包完成: {package_path}")

    return str(package_path)

def main():
    import sys

    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # 默认打包当前目录下的技能
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        package_path = create_skill_package(skill_dir, output_dir)
        print(f"\n✓ 打包成功!")
        print(f"输出文件: {package_path}")
        return 0
    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
