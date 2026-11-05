#!/usr/bin/env python3
"""
Self-Aware Routing 技能打包脚本
生成可分发的 .skill 文件
"""

import json
import os
import sys
import zipfile
from pathlib import Path
from datetime import datetime


def get_package_name(skill_path: Path) -> str:
    """生成包名"""
    # 从 meta.json 读取
    meta_file = skill_path / "_meta.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        name = meta.get("id", skill_path.name)
        version = meta.get("version", "1.0.0")
    else:
        name = skill_path.name
        version = "1.0.0"

    return f"{name}_v{version}.skill"


def scan_skill_files(skill_path: Path) -> list[Path]:
    """扫描技能目录，收集所有文件"""
    files = []

    for item in skill_path.rglob("*"):
        if item.is_file():
            # 跳过 __pycache__ 和 .pyc 文件
            if "__pycache__" in str(item):
                continue
            if item.suffix == ".pyc":
                continue
            files.append(item)

    return sorted(files)


def create_skill_archive(skill_path: Path, output_dir: Path = None) -> Path:
    """创建技能归档"""
    skill_name = skill_path.name

    if output_dir is None:
        output_dir = Path("/workspace/temp-skills")

    output_dir.mkdir(parents=True, exist_ok=True)

    package_name = get_package_name(skill_path)
    archive_path = output_dir / package_name

    # 创建 ZIP 归档
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in scan_skill_files(skill_path):
            # 计算相对路径
            rel_path = file_path.relative_to(skill_path)

            # 添加到归档
            zf.write(file_path, rel_path)
            print(f"  + {rel_path}")

    print(f"\n✓ Package created: {archive_path}")
    print(f"  Size: {archive_path.stat().st_size / 1024:.2f} KB")

    return archive_path


def verify_archive(archive_path: Path, skill_path: Path) -> bool:
    """验证归档内容"""
    print("\nVerifying archive contents...")

    required_files = {"SKILL.md", "_meta.json"}

    with zipfile.ZipFile(archive_path, "r") as zf:
        file_list = set(zf.namelist())

    for required in required_files:
        if required not in file_list:
            print(f"  ✗ Missing: {required}")
            return False
        print(f"  ✓ {required}")

    return True


def main():
    if len(sys.argv) > 1:
        skill_path = Path(sys.argv[1])
    else:
        skill_path = Path(__file__).parent.parent

    print(f"Packaging skill: {skill_path}")
    print("=" * 50)

    if not skill_path.exists():
        print(f"✗ Skill path not found: {skill_path}")
        sys.exit(1)

    # 创建归档
    archive_path = create_skill_archive(skill_path)

    # 验证
    if verify_archive(archive_path, skill_path):
        print("\n" + "=" * 50)
        print(f"✓ Packaging complete!")
        print(f"  Output: {archive_path}")
        sys.exit(0)
    else:
        print("\n✗ Verification failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()