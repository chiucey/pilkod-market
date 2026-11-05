#!/usr/bin/env python3
"""
技能验证脚本 - 验证SKILL.md的结构和质量
"""

import os
import re
import sys

def validate_skill(skill_dir):
    """验证技能目录结构和内容"""
    errors = []
    warnings = []

    skill_md = os.path.join(skill_dir, "SKILL.md")
    meta_json = os.path.join(skill_dir, "_meta.json")

    # 1. 检查SKILL.md是否存在
    if not os.path.exists(skill_md):
        errors.append("SKILL.md 不存在")
        return errors, warnings

    # 2. 读取SKILL.md内容
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. 检查frontmatter
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 frontmatter (---) 开头")

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # 检查必需字段
        if 'name:' not in frontmatter:
            errors.append("frontmatter 缺少 name 字段")
        if 'description:' not in frontmatter:
            errors.append("frontmatter 缺少 description 字段")
    else:
        errors.append("无法解析 frontmatter")

    # 4. 检查_meta.json
    if not os.path.exists(meta_json):
        errors.append("_meta.json 不存在")
    else:
        import json
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        if 'id' not in meta:
            errors.append("_meta.json 缺少 id 字段")
        if 'version' not in meta:
            errors.append("_meta.json 缺少 version 字段")

    # 5. 检查references目录
    references_dir = os.path.join(skill_dir, "references")
    if os.path.exists(references_dir):
        ref_files = os.listdir(references_dir)
        if ref_files:
            print(f"  参考文件: {', '.join(ref_files)}")

    return errors, warnings

def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"验证技能目录: {skill_dir}")

    errors, warnings = validate_skill(skill_dir)

    if errors:
        print("\n❌ 验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("\n✅ 验证通过")
        sys.exit(0)

if __name__ == "__main__":
    main()
