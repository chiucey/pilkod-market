#!/usr/bin/env python3
"""快速验证脚本 - 检查技能结构完整性"""

import json
import os
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """验证技能结构"""
    skill_dir = Path(skill_path)

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = skill_dir / file
        if not file_path.exists():
            print(f"❌ Missing required file: {file}")
            return False
        print(f"✅ Found: {file}")

    # 验证 SKILL.md frontmatter
    with open(skill_dir / 'SKILL.md', 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            print("❌ SKILL.md must start with YAML frontmatter (---)")
            return False
        if 'name:' not in content or 'description:' not in content:
            print("❌ SKILL.md must have 'name' and 'description' in frontmatter")
            return False
        print("✅ SKILL.md frontmatter valid")

    # 验证 _meta.json
    with open(skill_dir / '_meta.json', 'r', encoding='utf-8') as f:
        meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            print("❌ _meta.json must have 'id' and 'version'")
            return False
        print(f"✅ _meta.json valid (id: {meta['id']}, version: {meta['version']})")

    # 检查目录结构
    for subdir in ['references', 'scripts', 'assets']:
        subdir_path = skill_dir / subdir
        if subdir_path.exists():
            print(f"✅ Found directory: {subdir}")

    print("\n🎉 验证通过！")
    return True

if __name__ == '__main__':
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    success = validate_skill(skill_path)
    exit(0 if success else 1)
