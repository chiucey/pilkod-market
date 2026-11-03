#!/usr/bin/env python3
"""
Skill打包脚本 - sector-analysis-assistant
"""

import json
import os
import shutil
from pathlib import Path

def package_skill(skill_dir: str, output_dir: str = "/workspace/temp-skills"):
    """打包技能到.skill文件"""
    skill_path = Path(skill_dir)
    skill_name = skill_path.name

    # 读取meta信息
    meta_path = skill_path / "_meta.json"
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 打包文件
    output_file = output_path / f"{skill_name}.skill"
    shutil.make_archive(
        str(output_file.with_suffix('')),
        'zip',
        root_dir=skill_path.parent,
        base_dir=skill_name
    )

    # 重命名为.skill
    zip_file = output_file.with_suffix('.zip')
    if output_file.exists():
        output_file.unlink()
    shutil.move(str(zip_file), str(output_file))

    print(f"Skill打包完成: {output_file}")
    print(f"Skill ID: {meta['id']}")
    print(f"Version: {meta['version']}")
    return str(output_file)

if __name__ == "__main__":
    skill_dir = "/workspace/temp-skills/sector-analysis-assistant"
    output_file = package_skill(skill_dir)
    print(f"\n输出文件: {output_file}")
