#!/usr/bin/env python3
"""快速验证 HTML PPT PDF Deck 技能结构"""

import os
import json
import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
ERRORS = []
WARNINGS = []

def check_file_exists(path, name):
    if not path.exists():
        ERRORS.append(f"Missing required file: {name}")
        return False
    return True

def validate_frontmatter(skill_md_content):
    """验证 frontmatter 格式"""
    lines = skill_md_content.split('\n')
    if not lines[0].strip() == '---':
        ERRORS.append("SKILL.md must start with --- (frontmatter delimiter)")
        return False

    # 找到第二个 ---
    try:
        end_idx = lines[1:].index('---') + 1
    except ValueError:
        ERRORS.append("Frontmatter missing closing ---")
        return False

    frontmatter = '\n'.join(lines[1:end_idx])

    # 检查必需字段
    if not re.search(r'^name:', frontmatter, re.MULTILINE):
        ERRORS.append("Frontmatter missing 'name' field")
    if not re.search(r'^description:', frontmatter, re.MULTILINE):
        ERRORS.append("Frontmatter missing 'description' field")

    # 检查 name 格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            ERRORS.append(f"Invalid name format '{name}': use lowercase with hyphens only")

    return len(ERRORS) == 0

def validate_meta(meta_path):
    """验证 _meta.json"""
    if not check_file_exists(meta_path, "_meta.json"):
        return False

    try:
        with open(meta_path) as f:
            meta = json.load(f)

        if 'id' not in meta:
            ERRORS.append("_meta.json missing 'id' field")
        if 'version' not in meta:
            ERRORS.append("_meta.json missing 'version' field")

        return True
    except json.JSONDecodeError as e:
        ERRORS.append(f"_meta.json is not valid JSON: {e}")
        return False

def main():
    print("Validating html-ppt-pdf-deck skill...")

    # 检查 SKILL.md
    skill_md = SKILL_DIR / "SKILL.md"
    if check_file_exists(skill_md, "SKILL.md"):
        with open(skill_md) as f:
            content = f.read()
        validate_frontmatter(content)

    # 检查 _meta.json
    validate_meta(SKILL_DIR / "_meta.json")

    # 检查目录结构
    required_dirs = ['references', 'scripts']
    for d in required_dirs:
        path = SKILL_DIR / d
        if not path.exists():
            WARNINGS.append(f"Recommended directory missing: {d}")

    # 检查 references
    references_dir = SKILL_DIR / "references"
    if references_dir.exists():
        ref_files = list(references_dir.glob("*.md"))
        if len(ref_files) < 2:
            WARNINGS.append(f"Only {len(ref_files)} reference files found (recommend 2+)")

    # 输出结果
    print()
    if ERRORS:
        print(f"ERRORS ({len(ERRORS)}):")
        for e in ERRORS:
            print(f"  - {e}")

    if WARNINGS:
        print(f"WARNINGS ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"  - {w}")

    if not ERRORS and not WARNINGS:
        print("✓ All validations passed!")
    elif not ERRORS:
        print("✓ Core validation passed (warnings are non-blocking)")
    else:
        print(f"\n✗ Validation failed with {len(ERRORS)} error(s)")
        exit(1)

if __name__ == "__main__":
    main()
