#!/usr/bin/env python3
"""
提单转换技能验证脚本
验证技能结构和文件完整性
"""

import os
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证SKILL.md的frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    frontmatter_end = content.find('---', 3)
    if frontmatter_end == -1:
        return False, "Missing closing --- for frontmatter"

    frontmatter = content[3:frontmatter_end].strip()

    required_fields = ['name', 'description']
    for field in required_fields:
        if f"{field}:" not in frontmatter:
            return False, f"Missing required field: {field}"

    return True, "Frontmatter valid"

def validate_meta_json(meta_path):
    """验证_meta.json"""
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field: {field}"

    if not isinstance(meta['id'], int):
        return False, "id must be an integer"

    if not isinstance(meta['version'], str):
        return False, "version must be a string"

    return True, "Meta JSON valid"

def main():
    skill_dir = Path(__file__).parent.parent

    print("=" * 50)
    print("提单转换技能验证")
    print("=" * 50)

    # 检查必要文件
    skill_md = skill_dir / "SKILL.md"
    meta_json = skill_dir / "_meta.json"

    if not skill_md.exists():
        print("❌ SKILL.md not found")
        sys.exit(1)
    print("✓ SKILL.md exists")

    if not meta_json.exists():
        print("❌ _meta.json not found")
        sys.exit(1)
    print("✓ _meta.json exists")

    # 验证frontmatter
    valid, msg = validate_frontmatter(skill_md)
    if valid:
        print(f"✓ {msg}")
    else:
        print(f"❌ {msg}")
        sys.exit(1)

    # 验证meta.json
    valid, msg = validate_meta_json(meta_json)
    if valid:
        print(f"✓ {msg}")
    else:
        print(f"❌ {msg}")
        sys.exit(1)

    # 检查目录结构
    required_dirs = ['references', 'assets', 'assets/templates']
    for dir_name in required_dirs:
        dir_path = skill_dir / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory not found")

    print("=" * 50)
    print("验证完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
