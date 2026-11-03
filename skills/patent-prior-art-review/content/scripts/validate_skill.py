#!/usr/bin/env python3
"""
Patent Prior Art Review Skill Validator
验证技能结构和Frontmatter是否符合规范
"""

import os
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_path: str) -> tuple[bool, list[str]]:
    """验证SKILL.md的frontmatter格式"""
    errors = []
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md文件不存在"]

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.strip().startswith('---'):
        errors.append("SKILL.md必须以---开头（frontmatter必须放在最前面）")
        return False, errors

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if f"{field}:" not in frontmatter_text:
            errors.append(f"Frontmatter缺少必需字段: {field}")

    # 检查name字段
    if 'name:' in frontmatter_text:
        import re
        name_match = re.search(r'name:\s*([^\n]+)', frontmatter_text)
        if name_match:
            name_value = name_match.group(1).strip()
            # 检查名称格式（连字符）
            if not name_value.replace('-', '').replace('_', '').isalnum():
                errors.append("name字段只能包含字母、数字和连字符")
            # 检查名称与文件夹名匹配
            folder_name = os.path.basename(skill_path)
            if name_value != folder_name:
                errors.append(f"name字段值 '{name_value}' 与文件夹名称 '{folder_name}' 不匹配")

    # 检查description字段
    if 'description:' in frontmatter_text:
        import re
        desc_match = re.search(r'description:\s*([^\n]+)', frontmatter_text)
        if desc_match:
            desc_value = desc_match.group(1).strip()
            if len(desc_value) < 10:
                errors.append("description字段内容过短，应提供更详细的描述")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list[str]]:
    """验证_meta.json文件"""
    errors = []
    meta_path = Path(skill_path) / "_meta.json"

    if not meta_path.exists():
        return False, ["_meta.json文件不存在"]

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"_meta.json格式错误: {str(e)}"]

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json缺少必需字段: {field}")

    # 验证id类型
    if 'id' in meta:
        if not isinstance(meta['id'], int):
            errors.append("id字段必须是整数类型")

    # 验证version格式
    if 'version' in meta:
        import re
        version_pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(version_pattern, meta['version']):
            errors.append("version字段必须符合语义化版本格式 (如: 1.0.0)")

    return len(errors) == 0, errors


def validate_directory_structure(skill_path: str) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []
    required_items = ['SKILL.md', '_meta.json']

    for item in required_items:
        item_path = Path(skill_path) / item
        if not item_path.exists():
            errors.append(f"缺少必需文件: {item}")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    else:
        skill_path = sys.argv[1]

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 1. 目录结构验证
    passed, errors = validate_directory_structure(skill_path)
    if passed:
        print("✓ 目录结构验证通过")
    else:
        print("✗ 目录结构验证失败:")
        for error in errors:
            print(f"  - {error}")
        all_passed = False

    # 2. Frontmatter验证
    passed, errors = validate_frontmatter(skill_path)
    if passed:
        print("✓ Frontmatter验证通过")
    else:
        print("✗ Frontmatter验证失败:")
        for error in errors:
            print(f"  - {error}")
        all_passed = False

    # 3. _meta.json验证
    passed, errors = validate_meta_json(skill_path)
    if passed:
        print("✓ _meta.json验证通过")
    else:
        print("✗ _meta.json验证失败:")
        for error in errors:
            print(f"  - {error}")
        all_passed = False

    print("-" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 存在验证错误")
        return 1


if __name__ == "__main__":
    sys.exit(main())