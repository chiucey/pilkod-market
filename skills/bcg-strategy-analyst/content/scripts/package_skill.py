#!/usr/bin/env python3
"""打包技能为 .skill 文件"""

import json
import os
import shutil
import zipfile
from pathlib import Path

def package_skill(skill_dir: str, output_dir: str = "/workspace/temp-skills") -> str:
    skill_path = Path(skill_dir)
    skill_name = skill_path.name

    # 读取 meta
    with open(skill_path / "_meta.json", "r") as f:
        meta = json.load(f)

    # 创建输出路径
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 创建 .skill 文件 (zip)
    skill_file = output_path / f"{skill_name}.skill"

    with zipfile.ZipFile(skill_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    return str(skill_file)

if __name__ == "__main__":
    import sys
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/bcg-strategy-analyst"
    result = package_skill(skill_dir)
    print(f"✅ 技能已打包: {result}")
