#!/usr/bin/env python3
"""
PACK Design System Skill Packaging Script
将技能打包为可分发的.skill文件
"""

import os
import sys
import json
import tarfile
from pathlib import Path
from datetime import datetime

def get_skill_meta(skill_dir):
    """获取技能元数据"""
    meta_path = skill_dir / '_meta.json'
    if meta_path.exists():
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_skill_name(skill_md_path):
    """从SKILL.md获取技能名称"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    name_match = re.search(r'^name:\s*(.+)', content, re.MULTILINE)
    if name_match:
        return name_match.group(1).strip()
    return None

def package_skill(skill_dir, output_dir=None):
    """打包技能"""
    skill_dir = Path(skill_dir)

    if output_dir is None:
        output_dir = skill_dir.parent
    else:
        output_dir = Path(output_dir)

    skill_md_path = skill_dir / 'SKILL.md'
    if not skill_md_path.exists():
        print(f"Error: SKILL.md not found in {skill_dir}")
        return None

    skill_name = get_skill_name(skill_md_path)
    if not skill_name:
        print(f"Error: Could not determine skill name from SKILL.md")
        return None

    meta = get_skill_meta(skill_dir)
    if meta:
        version = meta.get('version', '1.0.0')
    else:
        version = '1.0.0'

    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d')
    output_file = output_dir / f"{skill_name}_{version}_{timestamp}.skill"

    print(f"Packaging skill: {skill_name} v{version}")
    print(f"Output: {output_file}")

    # 创建tar.gz归档
    with tarfile.open(output_file, 'w:gz') as tar:
        # 添加所有技能文件
        for item in skill_dir.rglob('*'):
            if item.is_file() and not item.name.endswith('.pyc'):
                arcname = str(item.relative_to(skill_dir))
                tar.add(item, arcname=arcname)
                print(f"  Adding: {arcname}")

    print(f"\n✓ Skill packaged successfully: {output_file}")
    print(f"  Size: {output_file.stat().st_size / 1024:.1f} KB")

    return output_file

def main():
    # 默认打包当前目录
    skill_dir = Path(__file__).parent.parent

    if len(sys.argv) > 1:
        skill_dir = Path(sys.argv[1])

    output_file = package_skill(skill_dir)

    if output_file:
        print(f"\nTo install this skill, use the skill management interface.")
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
