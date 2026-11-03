#!/usr/bin/env python3
"""
长篇网络小说技能验证脚本
验证SKILL.md的frontmatter、结构和命名规范
"""

import os
import re
import sys

def validate_skill(path):
    """验证技能目录结构和文件内容"""
    errors = []
    warnings = []

    # 1. 检查SKILL.md是否存在
    skill_md = os.path.join(path, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md文件不存在")
        return errors, warnings

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. 检查frontmatter格式
    if not content.startswith('---'):
        errors.append("SKILL.md必须以frontmatter开头（---）")

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析frontmatter，请确保格式正确")
    else:
        frontmatter = frontmatter_match.group(1)

        # 检查必填字段
        if 'name:' not in frontmatter:
            errors.append("frontmatter缺少name字段")
        if 'description:' not in frontmatter:
            errors.append("frontmatter缺少description字段")

        # 提取name值
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            # 检查name是否使用连字符格式
            if ' ' in name_value:
                warnings.append(f"name应使用连字符格式，建议改为：{name_value.lower().replace(' ', '-')}")
            # 检查name是否包含中文
            if re.search(r'[\u4e00-\u9fff]', name_value):
                errors.append(f"name不能包含中文字符：{name_value}")
            # 检查name长度
            if len(name_value) > 64:
                errors.append(f"name长度超过64字符限制：{len(name_value)}字符")
        else:
            errors.append("无法解析name字段")

    # 3. 检查Meta.json
    meta_path = os.path.join(path, "_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            import json
            try:
                meta = json.load(f)
                if 'id' not in meta:
                    errors.append("_meta.json缺少id字段")
                if 'version' not in meta:
                    errors.append("_meta.json缺少version字段")
            except json.JSONDecodeError as e:
                errors.append(f"_meta.json格式错误：{e}")
    else:
        errors.append("_meta.json文件不存在")

    # 4. 检查frontmatter后不能紧跟markdown标题
    rest_content = content[frontmatter_match.end():].strip()
    if rest_content.startswith('#'):
        errors.append("frontmatter之后不能直接以#标题开头")

    return errors, warnings

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    errors, warnings = validate_skill(skill_path)

    print("=" * 50)
    print("技能验证结果")
    print("=" * 50)

    if warnings:
        print("\n⚠️ 警告：")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n❌ 错误：")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\n✅ 验证通过！")
        sys.exit(0)