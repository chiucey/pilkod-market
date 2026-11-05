#!/usr/bin/env python3
"""
技能打包脚本
"""
import os
import json
import shutil
from pathlib import Path

def package_skill(skill_path: str, output_path: str = None):
    skill_dir = Path(skill_path)
    skill_name = skill_dir.name

    # 创建打包目录
    if output_path:
        pkg_dir = Path(output_path)
    else:
        pkg_dir = skill_dir.parent / f"{skill_name}_package"

    pkg_dir.mkdir(parents=True, exist_ok=True)

    # 复制文件
    for item in skill_dir.iterdir():
        if item.name.startswith('.') or item.name.endswith('.pyc'):
            continue
        dest = pkg_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

    # 验证meta
    meta_path = pkg_dir / "_meta.json"
    if meta_path.exists():
        with open(meta_path) as f:
            meta = json.load(f)
        print(f"✓ 技能ID: {meta.get('id')}")
        print(f"✓ 版本: {meta.get('version')}")

    # 创建打包文件
    archive_path = pkg_dir.parent / f"{skill_name}.skill"
    shutil.make_archive(
        archive_path.with_suffix(''),
        'zip',
        pkg_dir
    )
    shutil.move(str(archive_path) + '.zip', str(archive_path))

    print(f"✓ 打包完成: {archive_path}")
    return str(archive_path)

if __name__ == "__main__":
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    package_skill(skill_path)
