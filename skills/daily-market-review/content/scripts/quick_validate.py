#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能文件的必填字段和格式
"""

import os
import re
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md 的 frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "Frontmatter must start with '---' at the beginning of the file"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "Could not parse frontmatter"

    try:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
    except:
        import yaml
        try:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
        except:
            return False, "Invalid YAML in frontmatter"

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            return False, f"Missing required field: {field}"

    # 检查 name 格式
    name = frontmatter['name']
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"Invalid name format '{name}'. Use lowercase with hyphens only"

    if len(name) > 64:
        return False, f"Name too long ({len(name)} chars). Max 64 characters"

    # 检查 description 是否包含触发短语
    description = frontmatter['description']
    trigger_keywords = ['复盘', '收盘', '市场总结', '大盘分析']
    has_trigger = any(keyword in description for keyword in trigger_keywords)
    if not has_trigger:
        return False, "Description should include trigger keywords like '复盘' or '收盘'"

    return True, "Frontmatter validated successfully"

def validate_meta_json(meta_path):
    """验证 _meta.json"""
    if not os.path.exists(meta_path):
        return False, f"Missing _meta.json at {meta_path}"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 检查必填字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field in _meta.json: {field}"

    # 检查 id 是否为数字
    if not isinstance(meta['id'], int) and not meta['id'].isdigit():
        return False, f"Invalid id '{meta['id']}'. Must be a number"

    # 检查 version 格式
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"Invalid version format '{version}'. Use semantic versioning (e.g., 1.0.0)"

    return True, "_meta.json validated successfully"

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            return False, f"Missing required file: {file}"

    return True, "Directory structure validated successfully"

def validate_naming(skill_dir):
    """验证文件夹名称与 frontmatter name 一致"""
    # 读取 SKILL.md
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 name
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "Could not parse frontmatter"

    import yaml
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    name = frontmatter.get('name', '')

    # 获取目录名
    dir_name = os.path.basename(os.path.normpath(skill_dir))

    if name != dir_name:
        return False, f"Name mismatch: folder is '{dir_name}' but frontmatter name is '{name}'"

    return True, "Naming validated successfully"

def main():
    # 获取技能目录路径
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # 默认路径
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Validating skill at: {skill_dir}")
    print("-" * 50)

    all_passed = True

    # 1. 目录结构验证
    passed, msg = validate_directory_structure(skill_dir)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 2. Frontmatter 验证
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    passed, msg = validate_frontmatter(skill_md_path)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 3. _meta.json 验证
    meta_path = os.path.join(skill_dir, '_meta.json')
    passed, msg = validate_meta_json(meta_path)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 4. 命名一致性验证
    passed, msg = validate_naming(skill_dir)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    print("-" * 50)
    if all_passed:
        print("✓ All validations passed!")
        return 0
    else:
        print("✗ Some validations failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
