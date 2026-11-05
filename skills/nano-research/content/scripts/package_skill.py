#!/usr/bin/env python3
"""NanoResearch 技能打包脚本"""

import json
import os
import shutil
import sys
import tarfile
from pathlib import Path

def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """打包技能为 .skill 文件"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # 创建打包目录
    temp_dir = Path("/tmp/skill_package")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    # 复制文件
    for item in skill_path.rglob("*"):
        if item.is_file() and not item.name.startswith("."):
            dest = temp_dir / item.relative_to(skill_path)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)

    # 创建归档
    output_file = Path(output_dir) / f"{skill_name}.skill"
    with tarfile.open(output_file, "w:gz") as tar:
        tar.add(temp_dir, arcname=skill_name)

    # 清理
    shutil.rmtree(temp_dir)

    print(f"Skill packaged: {output_file}")
    return str(output_file)

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/workspace/temp-skills"
    package_skill(skill_path, output_dir)
