#!/usr/bin/env python3
"""
OAuth2 Learning Skill - Package Script
打包技能为可发布的.skill文件
"""

import json
import os
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
OUTPUT_DIR = Path(__file__).parent.parent.parent

def get_meta():
    """获取技能元数据"""
    meta_file = SKILL_DIR / "_meta.json"
    if meta_file.exists():
        return json.loads(meta_file.read_text(encoding='utf-8'))
    return {}

def package_skill():
    """打包技能"""
    meta = get_meta()
    skill_name = SKILL_DIR.name
    version = meta.get('version', '1.0.0')
    skill_id = meta.get('id', 'unknown')

    # 输出文件名
    output_name = f"{skill_name}-{version}.skill"
    output_path = OUTPUT_DIR / output_name

    print(f"Packaging {skill_name} v{version} (id: {skill_id})...")
    print(f"Output: {output_path}")

    # 创建tar.gz归档
    with tarfile.open(output_path, "w:gz") as tar:
        # 添加所有文件
        for file_path in SKILL_DIR.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                arcname = file_path.relative_to(SKILL_DIR)
                tar.add(file_path, arcname=arcname)
                print(f"  + {arcname}")

    print(f"\n✅ Packaged successfully: {output_path}")
    print(f"   Size: {output_path.stat().st_size / 1024:.1f} KB")

    return output_path

if __name__ == "__main__":
    package_skill()
