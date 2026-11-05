#!/usr/bin/env python3
"""快速验证学习辅导AI技能的结构和内容"""

import os
import json
import re
import sys

def validate_skill(skill_path: str) -> bool:
    """验证技能的完整性和正确性"""
    errors = []
    warnings = []

    # 检查 SKILL.md 是否存在
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        errors.append("SKILL.md 文件不存在")
        return False

    # 读取并检查 frontmatter
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查 frontmatter 是否在文件开头
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter 开头（---）")

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)

        # 检查必需字段
        if 'name:' not in frontmatter_text:
            errors.append("frontmatter 必须包含 'name' 字段")
        if 'description:' not in frontmatter_text:
            errors.append("frontmatter 必须包含 'description' 字段")
    else:
        errors.append("无法解析 YAML frontmatter")

    # 检查 _meta.json
    meta_path = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_path):
        errors.append("_meta.json 文件不存在")
    else:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("_meta.json 必须包含 'id' 字段")
        if 'version' not in meta:
            errors.append("_meta.json 必须包含 'version' 字段")

    # 检查核心结构关键词
    required_sections = ['分步讲解', '易混淆点', '练习题', '解析']
    for section in required_sections:
        if section not in content:
            warnings.append(f"建议包含 '{section}' 相关内容")

    # 输出结果
    if errors:
        print("❌ 验证失败:")
        for e in errors:
            print(f"   - {e}")
        return False

    if warnings:
        print("⚠️ 验证通过（有警告）:")
        for w in warnings:
            print(f"   - {w}")
    else:
        print("✅ 验证通过！")

    return True

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
