#!/usr/bin/env python3
"""
OAuth2 Learning Skill - Validation Script
验证技能结构和frontmatter是否符合规范
"""

import json
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
EXIT_CODE = 0

def validate_frontmatter():
    """验证SKILL.md的frontmatter"""
    global EXIT_CODE

    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ SKILL.md not found at {skill_md}")
        EXIT_CODE = 1
        return False

    content = skill_md.read_text(encoding='utf-8')

    # 检查frontmatter位置
    if not content.startswith('---'):
        print("❌ SKILL.md must start with YAML frontmatter (---)")
        EXIT_CODE = 1
        return False

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        print("❌ Frontmatter closing (---) not found")
        EXIT_CODE = 1
        return False

    frontmatter_text = '\n'.join(lines[1:frontmatter_end])

    # 解析frontmatter
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:\s*\S', frontmatter_text, re.MULTILINE):
            print(f"❌ Missing required field: {field}")
            EXIT_CODE = 1

    # 验证name格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            print(f"❌ name must be lowercase with hyphens: {name}")
            EXIT_CODE = 1
        if len(name) > 64:
            print(f"❌ name must be <= 64 characters: {name} ({len(name)})")
            EXIT_CODE = 1

    # 验证description包含触发短语
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if 'when' not in desc.lower():
            print("⚠️  description should contain trigger phrase (e.g., 'Use when...')")

    print("✅ Frontmatter validation passed")
    return True

def validate_meta_json():
    """验证_meta.json"""
    global EXIT_CODE

    meta_file = SKILL_DIR / "_meta.json"
    if not meta_file.exists():
        print("❌ _meta.json not found")
        EXIT_CODE = 1
        return False

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        print(f"❌ _meta.json is not valid JSON: {e}")
        EXIT_CODE = 1
        return False

    # 验证必需字段
    if 'id' not in meta:
        print("❌ _meta.json missing 'id' field")
        EXIT_CODE = 1

    if 'version' not in meta:
        print("❌ _meta.json missing 'version' field")
        EXIT_CODE = 1
    elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        print(f"❌ version should be semver format: {meta['version']}")
        EXIT_CODE = 1

    print("✅ _meta.json validation passed")
    return True

def validate_structure():
    """验证目录结构"""
    global EXIT_CODE

    # 检查references目录
    refs_dir = SKILL_DIR / "references"
    if refs_dir.exists():
        md_files = list(refs_dir.glob("*.md"))
        print(f"✅ references/ contains {len(md_files)} markdown files")

    print("✅ Directory structure validation passed")
    return True

def main():
    print("=" * 50)
    print("OAuth2 Learning Skill - Validation")
    print("=" * 50)

    validate_frontmatter()
    validate_meta_json()
    validate_structure()

    print("=" * 50)
    if EXIT_CODE == 0:
        print("✅ All validations passed!")
    else:
        print(f"❌ Validation failed with {EXIT_CODE} error(s)")

    return EXIT_CODE

if __name__ == "__main__":
    sys.exit(main())
