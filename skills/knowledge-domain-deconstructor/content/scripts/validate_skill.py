#!/usr/bin/env python3
"""
SKILL.md 结构验证器
检查 frontmatter、命名规范、文件完整性
"""

import os
import re
import sys

def validate_skill(path):
    """验证技能文件结构"""
    skill_md = os.path.join(path, "SKILL.md")
    meta_json = os.path.join(path, "_meta.json")

    errors = []
    warnings = []

    # 1. 检查 SKILL.md 是否存在
    if not os.path.exists(skill_md):
        errors.append("SKILL.md 不存在")
        return errors, warnings

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. 检查 frontmatter 是否在第一行
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        errors.append("Frontmatter 必须从第一行开始（不能有标题或空白行）")

    # 3. 提取 frontmatter
    if '---' in content:
        fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            # 检查必填字段
            if 'name:' not in fm_text:
                errors.append("Frontmatter 缺少 name 字段")
            if 'description:' not in fm_text:
                errors.append("Frontmatter 缺少 description 字段")
        else:
            errors.append("Frontmatter 格式错误（需要 --- 包围）")
    else:
        errors.append("缺少 frontmatter（需要 --- 开头和结尾）")

    # 4. 检查 name 字段格式（连字符、英文）
    name_match = re.search(r'^name:\s*([a-z0-9-]+)', fm_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1)
        if not re.match(r'^[a-z0-9-]+$', name_value):
            errors.append(f"name 必须是英文小写+连字符，当前: {name_value}")
        if name_value != os.path.basename(path):
            warnings.append(f"name ('{name_value}') 应与文件夹名 ('{os.path.basename(path)}') 一致")

    # 5. 检查 _meta.json
    if not os.path.exists(meta_json):
        errors.append("_meta.json 不存在")
    else:
        import json
        try:
            with open(meta_json, 'r') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json JSON 格式错误: {e}")

    # 6. 检查内容长度
    # 移除 frontmatter 后检查内容
    main_content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    if len(main_content.strip()) < 100:
        warnings.append("SKILL.md 内容较少，可能不完整")

    return errors, warnings

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = os.path.dirname(os.path.abspath(__file__))

    errors, warnings = validate_skill(path)

    print("=== 验证结果 ===")
    if errors:
        print(f"❌ 错误 ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    if warnings:
        print(f"⚠️  警告 ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    if not errors and not warnings:
        print("✅ 验证通过")

    sys.exit(1 if errors else 0)