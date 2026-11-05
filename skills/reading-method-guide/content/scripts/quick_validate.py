#!/usr/bin/env python3
"""验证技能结构和内容的脚本"""
import os
import re
import json
import sys

def validate_skill(skill_dir):
    """验证技能目录结构和内容"""
    errors = []
    warnings = []

    # 检查目录是否存在
    if not os.path.exists(skill_dir):
        return [f"技能目录不存在: {skill_dir}"]

    # 检查必需文件
    skill_md = os.path.join(skill_dir, "SKILL.md")
    meta_json = os.path.join(skill_dir, "_meta.json")

    if not os.path.exists(skill_md):
        errors.append("缺少 SKILL.md 文件")
    else:
        # 验证 frontmatter
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否以 --- 开头
        if not content.strip().startswith('---'):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头 (---)")

        # 提取 frontmatter
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            # 验证必需字段
            if 'name:' not in fm_text:
                errors.append("frontmatter 缺少 name 字段")
            if 'description:' not in fm_text:
                errors.append("frontmatter 缺少 description 字段")
        else:
            errors.append("无法解析 YAML frontmatter")

    if not os.path.exists(meta_json):
        errors.append("缺少 _meta.json 文件")
    else:
        # 验证 _meta.json
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError:
            errors.append("_meta.json 格式错误")

    return errors, warnings

if __name__ == "__main__":
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/reading-method-guide"
    errors, warnings = validate_skill(skill_dir)

    if errors:
        print("❌ 验证失败:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("✅ 验证通过")
        sys.exit(0)
