#!/usr/bin/env python3
"""快速验证音乐制作人技能的脚本"""

import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent

def check_frontmatter():
    """检查SKILL.md的frontmatter格式"""
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")

    # 检查frontmatter是否在第一行
    if not content.startswith("---"):
        return False, "SKILL.md must start with --- (frontmatter delimiter)"

    # 提取frontmatter
    lines = content.split("\n")
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "Frontmatter closing --- not found"

    frontmatter_text = "\n".join(lines[:frontmatter_end+1])

    # 检查必填字段
    if "name:" not in frontmatter_text:
        return False, "Frontmatter missing 'name' field"
    if "description:" not in frontmatter_text:
        return False, "Frontmatter missing 'description' field"

    # 检查name格式（连字符）
    name_match = re.search(r"name:\s*([a-z0-9-]+)", frontmatter_text)
    if not name_match:
        return False, "Invalid name format (use hyphen-case)"

    # 检查description中是否有触发短语
    desc_match = re.search(r"description:\s*(.+)", frontmatter_text)
    if desc_match:
        desc = desc_match.group(1).lower()
        if "创作音乐" not in desc and "音乐创作" not in desc and "music" not in desc:
            return False, "Description should include trigger phrases for music creation"

    return True, "Frontmatter OK"

def check_meta_json():
    """检查_meta.json格式"""
    meta_file = SKILL_DIR / "_meta.json"
    if not meta_file.exists():
        return False, "_meta.json not found"

    import json
    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False, "_meta.json is not valid JSON"

    if "id" not in meta:
        return False, "_meta.json missing 'id' field"
    if "version" not in meta:
        return False, "_meta.json missing 'version' field"

    if not isinstance(meta["id"], int):
        return False, "_meta.json 'id' must be an integer"

    return True, "_meta.json OK"

def check_structure():
    """检查目录结构"""
    required_dirs = []
    optional_dirs = ["references", "assets", "scripts"]

    for d in required_dirs:
        if not (SKILL_DIR / d).exists():
            return False, f"Missing required directory: {d}"

    for d in optional_dirs:
        if not (SKILL_DIR / d).exists():
            print(f"  Note: Optional directory '{d}' not found (OK)")

    return True, "Structure OK"

def main():
    print("=" * 50)
    print("音乐制作人技能 - 快速验证")
    print("=" * 50)

    all_passed = True

    # 检查1: Frontmatter
    passed, msg = check_frontmatter()
    print(f"\n[{'PASS' if passed else 'FAIL'}] Frontmatter检查: {msg}")
    all_passed = all_passed and passed

    # 检查2: _meta.json
    passed, msg = check_meta_json()
    print(f"[{'PASS' if passed else 'FAIL'}] _meta.json检查: {msg}")
    all_passed = all_passed and passed

    # 检查3: 目录结构
    passed, msg = check_structure()
    print(f"[{'PASS' if passed else 'FAIL'}] 目录结构检查: {msg}")
    all_passed = all_passed and passed

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有检查通过！技能可以发布。")
        return 0
    else:
        print("✗ 部分检查失败，请修复后重试。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
