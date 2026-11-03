#!/usr/bin/env python3
"""
Smart Memory Hub 技能打包脚本
"""

import json
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Set


def get_all_files(directory: Path, exclude_patterns: Set[str] = None) -> List[Path]:
    """获取目录中所有文件"""
    if exclude_patterns is None:
        exclude_patterns = {
            '__pycache__', '*.pyc', '*.pyo', '.git', '.DS_Store',
            'Thumbs.db', '*.log', '.pytest_cache', '.mypy_cache'
        }

    files = []
    for item in directory.rglob("*"):
        if item.is_file():
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.startswith('*'):
                    if item.suffix == pattern[1:]:
                        should_exclude = True
                        break
                elif pattern in str(item):
                    should_exclude = True
                    break
            if not should_exclude:
                files.append(item)
    return files


def create_package(skill_path: str, output_path: str = None) -> str:
    """创建技能包"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        raise FileNotFoundError(f"技能目录不存在: {skill_path}")

    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        skill_name = meta.get('name', skill_path.name)
        skill_version = meta.get('version', '1.0.0')
    else:
        skill_name = skill_path.name
        skill_version = '1.0.0'

    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"{skill_name}_{skill_version}_{timestamp}.skill"

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        files = get_all_files(skill_path)
        for file in files:
            relative_path = file.relative_to(skill_path)
            zipf.write(file, relative_path)
            print(f"  + {relative_path}")

    print(f"\n✓ 技能包已创建: {output_path}")
    print(f"  技能名称: {skill_name}")
    print(f"  技能版本: {skill_version}")
    print(f"  文件数量: {len(files)}")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("用法: python package_skill.py <skill_path> [output.skill]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    create_package(skill_path, output_path)


if __name__ == "__main__":
    main()
