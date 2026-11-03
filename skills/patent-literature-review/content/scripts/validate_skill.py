#!/usr/bin/env python3
"""
技能验证脚本
检查SKILL.md和_meta.json的格式和内容
"""

import json
import os
import sys
import re

def validate_frontmatter(skill_path: str) -> tuple[bool, list]:
    """验证frontmatter格式"""
    errors = []
    skill_file = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_file):
        return False, [f"SKILL.md not found at {skill_file}"]

    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.strip().startswith('---'):
        errors.append("SKILL.md must start with --- (frontmatter delimiter)")
        return False, errors

    # 提取frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        errors.append("Cannot parse frontmatter")
        return False, errors

    fm_content = fm_match.group(1)

    # 检查必填字段
    if not re.search(r'^name:\s*.+', fm_content, re.MULTILINE):
        errors.append("Missing 'name' field in frontmatter")

    if not re.search(r'^description:\s*.+', fm_content, re.MULTILINE):
        errors.append("Missing 'description' field in frontmatter")

    # 检查name格式（连字符格式）
    name_match = re.search(r'^name:\s*(.+)', fm_content, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Name '{name}' must be lowercase with hyphens only")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list]:
    """验证_meta.json"""
    errors = []
    meta_file = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_file):
        return False, [f"_meta.json not found at {meta_file}"]

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    # 检查必填字段
    if 'id' not in meta:
        errors.append("Missing 'id' field in _meta.json")

    if 'version' not in meta:
        errors.append("Missing 'version' field in _meta.json")

    # 验证id是整数
    if 'id' in meta and not isinstance(meta['id'], int):
        errors.append("'id' must be an integer")

    # 验证version格式
    if 'version' in meta:
        if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            errors.append("'version' must follow semver format (e.g., 1.0.0)")

    return len(errors) == 0, errors


def validate_directory_structure(skill_path: str) -> tuple[bool, list]:
    """验证目录结构"""
    errors = []

    # 检查基本结构
    if not os.path.isdir(skill_path):
        errors.append(f"{skill_path} is not a directory")
        return False, errors

    if not os.path.exists(os.path.join(skill_path, "SKILL.md")):
        errors.append("Missing SKILL.md")

    if not os.path.exists(os.path.join(skill_path, "_meta.json")):
        errors.append("Missing _meta.json")

    return len(errors) == 0, errors


def validate_scripts(skill_path: str) -> tuple[bool, list]:
    """验证脚本文件"""
    scripts_dir = os.path.join(skill_path, "scripts")
    errors = []

    if os.path.exists(scripts_dir):
        for filename in os.listdir(scripts_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(scripts_dir, filename)
                # 检查文件是否有语法错误
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        compile(f.read(), filepath, 'exec')
                except SyntaxError as e:
                    errors.append(f"Syntax error in {filename}: {e}")

    return len(errors) == 0, errors


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/patent-literature-review"

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 验证目录结构
    passed, errors = validate_directory_structure(skill_path)
    if not passed:
        print("❌ 目录结构验证失败:")
        for e in errors:
            print(f"   - {e}")
        all_passed = False
    else:
        print("✓ 目录结构验证通过")

    # 验证frontmatter
    passed, errors = validate_frontmatter(skill_path)
    if not passed:
        print("❌ Frontmatter验证失败:")
        for e in errors:
            print(f"   - {e}")
        all_passed = False
    else:
        print("✓ Frontmatter验证通过")

    # 验证_meta.json
    passed, errors = validate_meta_json(skill_path)
    if not passed:
        print("❌ _meta.json验证失败:")
        for e in errors:
            print(f"   - {e}")
        all_passed = False
    else:
        print("✓ _meta.json验证通过")

    # 验证脚本
    passed, errors = validate_scripts(skill_path)
    if not passed:
        print("❌ 脚本验证失败:")
        for e in errors:
            print(f"   - {e}")
        all_passed = False
    else:
        print("✓ 脚本验证通过")

    print("-" * 50)
    if all_passed:
        print("✅ 所有验证通过!")
        sys.exit(0)
    else:
        print("❌ 验证失败，请修复以上问题")
        sys.exit(1)


if __name__ == "__main__":
    main()