#!/usr/bin/env python3
"""
抖音账号分析技能验证脚本
验证 SKILL.md 的 frontmatter 格式和内容完整性
"""

import os
import re
import sys

def validate_skill():
    skill_dir = os.path.dirname(os.path.abspath(__file__)).replace('/scripts', '')
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    meta_json = os.path.join(skill_dir, '_meta.json')

    errors = []
    warnings = []

    # 1. 检查 SKILL.md 是否存在
    if not os.path.exists(skill_md):
        errors.append("SKILL.md 文件不存在")
        return errors, warnings

    # 2. 读取并检查 frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter (---) 开头")

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析 YAML frontmatter")
    else:
        frontmatter = frontmatter_match.group(1)

        # 检查必需字段
        if 'name:' not in frontmatter:
            errors.append("frontmatter 缺少 name 字段")
        if 'description:' not in frontmatter:
            errors.append("frontmatter 缺少 description 字段")

        # 提取 name 值
        name_match = re.search(r'name:\s*(.+)', frontmatter)
        if name_match:
            name_value = name_match.group(1).strip()
            # 检查 name 是否使用连字符格式
            if ' ' in name_value:
                errors.append(f"name 应使用连字符格式: {name_value}")
            # 检查 folder 名称一致性（假设 folder 与 name 相同）
            expected_name = name_value
            actual_folder = os.path.basename(skill_dir)
            if expected_name != actual_folder:
                warnings.append(f"frontmatter name ({expected_name}) 与文件夹名 ({actual_folder}) 不一致")

    # 3. 检查 markdown 标题不在 frontmatter 之前
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if line.startswith('---'):
            if frontmatter_end == -1:
                frontmatter_end = i
                break

    if frontmatter_end > 0:
        for line in lines[:frontmatter_end]:
            if line.strip().startswith('#'):
                errors.append("frontmatter 之前不能有 markdown 标题")
                break

    # 4. 检查 _meta.json
    if not os.path.exists(meta_json):
        errors.append("_meta.json 文件不存在")
    else:
        import json
        with open(meta_json, 'r', encoding='utf-8') as f:
            try:
                meta = json.load(f)
                if 'id' not in meta:
                    errors.append("_meta.json 缺少 id 字段")
                if 'version' not in meta:
                    errors.append("_meta.json 缺少 version 字段")
            except json.JSONDecodeError as e:
                errors.append(f"_meta.json JSON 格式错误: {e}")

    return errors, warnings

if __name__ == '__main__':
    errors, warnings = validate_skill()

    if errors:
        print("❌ 验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    elif warnings:
        print("⚠️ 验证通过（有警告）:")
        for warning in warnings:
            print(f"  - {warning}")
        sys.exit(0)
    else:
        print("✅ 验证通过")
        sys.exit(0)
