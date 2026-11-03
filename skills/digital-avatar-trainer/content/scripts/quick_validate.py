#!/usr/bin/env python3
"""
AI数字分身训练师 - 快速验证脚本
验证SKILL.md的结构和格式是否符合规范
"""

import os
import re
import json
import sys

def validate_skill():
    errors = []
    warnings = []

    # 检查目录
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 1. 检查SKILL.md是否存在
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md not found")
        return errors, warnings

    # 2. 读取SKILL.md
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. 检查frontmatter是否存在
    if not content.startswith('---'):
        errors.append("SKILL.md must start with frontmatter (---)")

    # 4. 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # 检查必需字段
        if 'name:' not in frontmatter:
            errors.append("Missing 'name:' field in frontmatter")
        if 'description:' not in frontmatter:
            errors.append("Missing 'description:' field in frontmatter")

        # 检查name格式
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"name '{name}' should be lowercase with hyphens only")
            if name != os.path.basename(skill_dir):
                warnings.append(f"name '{name}' should match directory name '{os.path.basename(skill_dir)}'")
    else:
        errors.append("Could not parse frontmatter")

    # 5. 检查_meta.json
    meta_json = os.path.join(skill_dir, "_meta.json")
    if os.path.exists(meta_json):
        with open(meta_json, 'r', encoding='utf-8') as f:
            try:
                meta = json.load(f)
                if 'id' not in meta:
                    errors.append("Missing 'id' in _meta.json")
                if 'version' not in meta:
                    errors.append("Missing 'version' in _meta.json")
            except json.JSONDecodeError:
                errors.append("_meta.json is not valid JSON")
    else:
        errors.append("_meta.json not found")

    # 6. 检查description触发短语
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE | re.DOTALL)
    if desc_match:
        desc = desc_match.group(1)
        trigger_keywords = ['创建AI分身', '训练数字人格', '角色模拟', '聊天记录训练AI']
        has_trigger = any(kw in desc for kw in trigger_keywords)
        if not has_trigger:
            warnings.append("description should include trigger keywords")

    return errors, warnings

if __name__ == "__main__":
    errors, warnings = validate_skill()

    print("=" * 50)
    print("AI数字分身训练师 - 验证报告")
    print("=" * 50)

    if warnings:
        print(f"\n警告 ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n错误 ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\n验证通过！")
        sys.exit(0)
