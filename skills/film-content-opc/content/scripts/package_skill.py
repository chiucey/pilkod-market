#!/usr/bin/env python3
"""
影视内容OPC技能 - 打包脚本
"""

import json
import os
import shutil
import sys
from pathlib import Path

def package_skill(skill_dir: str, output_dir: str = "dist"):
    """打包技能"""
    skill_path = Path(skill_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 技能名称
    skill_name = skill_path.name
    output_file = output_path / f"{skill_name}.skill"

    # 读取meta
    meta_path = skill_path / "_meta.json"
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 创建zip文件
    zip_file = output_path / f"{skill_name}.zip"

    # 使用shutil创建归档
    shutil.make_archive(str(zip_file.with_suffix('')), 'zip', skill_path, skill_path)

    # 重命名为.skill
    if output_file.exists():
        output_file.unlink()
    shutil.move(str(zip_file), str(output_file))

    print(f"\n{'='*50}")
    print(f"✅ 技能打包完成!")
    print(f"{'='*50}")
    print(f"📦 输出文件: {output_file.absolute()}")
    print(f"🏷️  技能ID: {meta['id']}")
    print(f"📌 版本号: {meta['version']}")
    print(f"{'='*50}")

    return str(output_file.absolute())

if __name__ == "__main__":
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    package_skill(skill_dir)
