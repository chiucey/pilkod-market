#!/usr/bin/env python3
"""
技能打包脚本
将技能文件夹打包为.skill文件用于分发
"""

import os
import zipfile
import json
from pathlib import Path
from datetime import datetime

def get_skill_id(skill_dir):
    """获取技能ID"""
    meta_file = Path(skill_dir) / "_meta.json"
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            return meta.get('id', 'unknown')
    return 'unknown'

def get_skill_version(skill_dir):
    """获取技能版本"""
    meta_file = Path(skill_dir) / "_meta.json"
    if meta_file.exists():
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
            return meta.get('version', '1.0.0')
    return '1.0.0'

def get_skill_name(skill_dir):
    """获取技能名称"""
    skill_md = Path(skill_dir) / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            import re
            name_match = re.search(r'name:\s*(.+)', content)
            if name_match:
                return name_match.group(1).strip()
    return Path(skill_dir).name

def package_skill(skill_dir, output_dir="."):
    """打包技能"""
    skill_path = Path(skill_dir)
    skill_name = get_skill_name(skill_dir)
    skill_id = get_skill_id(skill_dir)
    skill_version = get_skill_version(skill_dir)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = Path(output_dir) / f"{skill_name}_{skill_id}_{skill_version}_{timestamp}.skill"

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files = [f for f in files if not f.startswith('.')]

            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zipf.write(file_path, arcname)

    print(f"✓ Skill packaged: {output_file}")
    print(f"  Name: {skill_name}")
    print(f"  ID: {skill_id}")
    print(f"  Version: {skill_version}")
    return str(output_file)

def main():
    import sys

    if len(sys.argv) < 2:
        skill_dir = "."
        output_dir = "."
    elif len(sys.argv) < 3:
        skill_dir = sys.argv[1]
        output_dir = "."
    else:
        skill_dir = sys.argv[1]
        output_dir = sys.argv[2]

    output_file = package_skill(skill_dir, output_dir)
    print(f"\n✓ Package created: {output_file}")

if __name__ == "__main__":
    main()
