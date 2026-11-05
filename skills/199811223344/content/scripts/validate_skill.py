#!/usr/bin/env python3
"""
技能验证脚本
检查 SKILL.md 和目录结构是否符合规范
"""

import os
import re
import sys

def validate_skill(skill_path):
    """验证技能结构"""
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md 不存在")
        return errors, warnings

    # Check frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Frontmatter must be at the beginning
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 frontmatter (---) 开头")

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        frontmatter = match.group(1)

        # Check required fields
        if 'name:' not in frontmatter:
            errors.append("frontmatter 缺少 name 字段")
        if 'description:' not in frontmatter:
            errors.append("frontmatter 缺少 description 字段")

        # Extract name
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        if name_match:
            skill_name = name_match.group(1).strip()
            # Check folder name matches
            folder_name = os.path.basename(skill_path)
            if skill_name != folder_name:
                warnings.append(f"name ({skill_name}) 与文件夹名 ({folder_name}) 不匹配")
    else:
        errors.append("无法解析 frontmatter")

    # Check _meta.json
    meta_json = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_json):
        errors.append("_meta.json 不存在")
    else:
        import json
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    # Check for markdown headings BEFORE frontmatter (invalid)
    # Valid: frontmatter starts at line 1, markdown starts after --- closing
    if content.startswith('# '):
        errors.append("SKILL.md 以 markdown 标题 (#) 开头，应该以 frontmatter (---) 开头")

    # Check frontmatter is at the very beginning
    if not content.strip().startswith('---'):
        errors.append("SKILL.md 必须以 frontmatter (---) 开头")

    return errors, warnings

def main():
    if len(sys.argv) < 2:
        skill_path = "."
    else:
        skill_path = sys.argv[1]

    print(f"验证技能: {skill_path}")
    print("=" * 50)

    errors, warnings = validate_skill(skill_path)

    if warnings:
        print("\n⚠️  警告:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n❌ 错误:")
        for e in errors:
            print(f"  - {e}")
        print("\n验证失败!")
        sys.exit(1)
    else:
        print("\n✅ 验证通过!")
        sys.exit(0)

if __name__ == "__main__":
    main()
