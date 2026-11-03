#!/usr/bin/env python3
"""
PRD to Markdown Skill Validator
验证SKILL.md的frontmatter和结构是否符合规范
"""

import os
import re
import sys

def validate_skill(skill_path):
    """验证技能文件的frontmatter和结构"""
    errors = []
    warnings = []

    skill_md = os.path.join(skill_path, "SKILL.md")
    meta_json = os.path.join(skill_path, "_meta.json")

    # 检查_meta.json存在
    if not os.path.exists(meta_json):
        errors.append("缺少_meta.json文件")
        return errors, warnings

    # 检查SKILL.md存在
    if not os.path.exists(skill_md):
        errors.append("缺少SKILL.md文件")
        return errors, warnings

    # 验证_meta.json格式
    import json
    with open(meta_json, 'r', encoding='utf-8') as f:
        try:
            meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json缺少id字段")
            if 'version' not in meta:
                errors.append("_meta.json缺少version字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json格式错误: {e}")

    # 验证SKILL.md frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.strip().startswith('---'):
        errors.append("SKILL.md必须以YAML frontmatter开头(---)")
        return errors, warnings

    # 提取frontmatter
    lines = content.split('\n')
    if len(lines) < 3 or lines[0] != '---' or '---' not in lines[1:]:
        errors.append("SKILL.md frontmatter格式错误，需要---开头和结尾")
        return errors, warnings

    # 找到frontmatter结束位置
    fm_end = lines.index('---', 1)
    fm_content = '\n'.join(lines[1:fm_end])

    # 检查必需字段
    if 'name:' not in fm_content:
        errors.append("frontmatter缺少name字段")
    if 'description:' not in fm_content:
        errors.append("frontmatter缺少description字段")

    # 提取name和description
    name_match = re.search(r'^name:\s*(.+)$', fm_content, re.MULTILINE)
    desc_match = re.search(r'^description:\s*(.+)$', fm_content, re.MULTILINE)

    if name_match:
        name = name_match.group(1).strip()
        if not name:
            errors.append("name字段不能为空")
        elif not re.match(r'^[a-z0-9-]+$', name):
            warnings.append(f"name应使用小写连字符格式，当前: {name}")
    else:
        name = None

    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            warnings.append("description建议至少20字符以提高触发准确性")
    else:
        desc = None

    # 检查frontmatter后不应有H1标题
    after_fm = '\n'.join(lines[fm_end+1:]).strip()
    if after_fm.startswith('# '):
        errors.append("frontmatter后不应直接出现H1标题(# )")

    return errors, warnings

def main():
    if len(sys.argv) < 2:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    else:
        skill_path = sys.argv[1]

    errors, warnings = validate_skill(skill_path)

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    if errors:
        print(f"❌ 错误 ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print(f"⚠️ 警告 ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if not errors and not warnings:
        print("✅ 验证通过！")
    elif not errors:
        print("✅ 基本验证通过")
    else:
        print("❌ 验证失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
