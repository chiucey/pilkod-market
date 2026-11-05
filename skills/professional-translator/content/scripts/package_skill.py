#!/usr/bin/env python3
"""
技能打包脚本 - 创建 .skill 文件
"""

import os
import zipfile
import json
from datetime import datetime

def package_skill(skill_dir, output_dir=None):
    """打包技能目录为 .skill 文件"""

    skill_name = os.path.basename(skill_dir)

    if output_dir is None:
        output_dir = os.path.dirname(skill_dir)

    output_file = os.path.join(output_dir, f"{skill_name}.skill")

    # 创建ZIP文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, skill_dir)
                zipf.write(file_path, arcname)

    # 读取元数据
    meta_path = os.path.join(skill_dir, "_meta.json")
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    print(f"技能打包完成: {output_file}")
    print(f"  技能名称: {skill_name}")
    print(f"  技能ID: {meta.get('id')}")
    print(f"  版本: {meta.get('version')}")
    print(f"  包含文件数: {len(files) if 'files' in locals() else 'N/A'}")

    return output_file

if __name__ == "__main__":
    import sys
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    package_skill(skill_dir)
