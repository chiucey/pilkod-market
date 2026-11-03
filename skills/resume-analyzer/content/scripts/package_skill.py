#!/usr/bin/env python3
"""打包技能为.skill文件"""

import os
import json
import shutil
import sys
import zipfile
from pathlib import Path
from datetime import datetime

def get_meta(skill_path):
    """读取技能元数据"""
    meta_file = Path(skill_path) / "_meta.json"
    return json.loads(meta_file.read_text(encoding='utf-8'))

def create_skill_package(skill_path, output_dir=None):
    """创建.skill打包文件"""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    # 获取元数据
    meta = get_meta(skill_path)

    # 生成输出文件名
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = Path(skill_path).parent

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{skill_name}.skill"

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 添加所有文件
        for root, dirs, files in os.walk(skill_path):
            # 排除scripts目录（仅用于开发）
            if 'scripts' in root.split(os.sep):
                continue

            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"✅ Skill packaged successfully!")
    print(f"📦 Output: {output_file}")
    print(f"📋 Version: {meta.get('version', '1.0.0')}")

    return str(output_file)

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output_file = create_skill_package(skill_path, output_dir)
        print(f"\n🎉 Done! Skill file created at: {output_file}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
