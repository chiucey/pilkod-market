#!/usr/bin/env python3
"""
技能验证脚本 - 快速验证SKILL.md结构
"""

import os
import re
import json
import sys

def validate_frontmatter(skill_path):
    """验证frontmatter格式"""
    skillyaml_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skillyaml_path):
        return False, "SKILL.md不存在"

    with open(skillyaml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md必须以YAML frontmatter开头(---)"

    # 检查frontmatter必填字段
    if not re.search(r'^name:', content, re.MULTILINE):
        return False, "缺少name字段"
    if not re.search(r'^description:', content, re.MULTILINE):
        return False, "缺少description字段"

    return True, "OK"

def validate_meta(skill_path):
    """验证_meta.json"""
    meta_path = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_path):
        return False, "_meta.json不存在"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        if 'id' not in meta or 'version' not in meta:
            return False, "_meta.json缺少id或version"
    except json.JSONDecodeError:
        return False, "_meta.json格式错误"

    return True, "OK"

def main():
    skill_path = "/workspace/temp-skills/gml-developer"

    errors = []

    # 验证frontmatter
    ok, msg = validate_frontmatter(skill_path)
    if not ok:
        errors.append(f"Frontmatter: {msg}")

    # 验证meta
    ok, msg = validate_meta(skill_path)
    if not ok:
        errors.append(f"Meta: {msg}")

    if errors:
        print("验证失败:")
        for e in errors:
            print(f"  - {e}")
        return 1
    else:
        print("验证通过 ✓")
        return 0

if __name__ == "__main__":
    sys.exit(main())