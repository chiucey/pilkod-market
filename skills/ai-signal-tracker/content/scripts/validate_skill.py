#!/usr/bin/env python3
"""验证AI信号追踪器技能的结构和frontmatter"""

import os
import re
import sys

def validate_skill():
    errors = []
    warnings = []

    skill_dir = os.path.dirname(os.path.abspath(__file__)).replace('/scripts', '')
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    meta_json_path = os.path.join(skill_dir, '_meta.json')

    # 1. 检查SKILL.md是否存在
    if not os.path.exists(skill_md_path):
        errors.append("SKILL.md不存在")
        return errors, warnings

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. 检查frontmatter是否在第一行
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        errors.append("Frontmatter必须从第一行开始（以---开头）")

    # 3. 提取frontmatter
    if '---' in content:
        frontmatter_end = content.index('---', 3)  # 找第二个---
        frontmatter = content[2:frontmatter_end].strip()

        # 检查必需字段
        if 'name:' not in frontmatter:
            errors.append("Frontmatter缺少name字段")
        if 'description:' not in frontmatter:
            errors.append("Frontmatter缺少description字段")

        # 检查是否有markdown标题在frontmatter之前
        content_after_frontmatter = content[frontmatter_end + 3:]
        if content_after_frontmatter.strip().startswith('#'):
            # 找到第一个#的位置
            first_content = content_after_frontmatter.strip()
            if first_content.startswith('#'):
                # 第一个非空行是markdown标题，这是OK的
                pass
    else:
        errors.append("缺少frontmatter分隔符---")

    # 4. 检查_meta.json
    if not os.path.exists(meta_json_path):
        errors.append("_meta.json不存在")
    else:
        import json
        with open(meta_json_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        if 'id' not in meta:
            errors.append("_meta.json缺少id字段")
        if 'version' not in meta:
            errors.append("_meta.json缺少version字段")

    # 5. 检查描述是否包含触发短语
    if 'description:' in frontmatter:
        desc_match = re.search(r'description:\s*(.+)', frontmatter)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                warnings.append("description过短，建议至少20字符")

    return errors, warnings

if __name__ == '__main__':
    errors, warnings = validate_skill()

    if errors:
        print("❌ 验证失败:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    if warnings:
        print("⚠️ 警告:")
        for w in warnings:
            print(f"  - {w}")

    print("✅ 验证通过")
    sys.exit(0)