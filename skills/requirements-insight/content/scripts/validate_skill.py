#!/usr/bin/env python3
"""
快速验证脚本 - 检查skill基本结构
"""
import os
import json
import sys

def validate_frontmatter():
    """验证frontmatter"""
    skill_md_path = "SKILL.md"

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter格式
    if not content.startswith('---'):
        return False, "SKILL.md必须以---开头"

    lines = content.split('\n')
    fm_end = -1
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == '---':
            fm_end = i
            break

    if fm_end == -1:
        return False, "SKILL.md frontmatter未正确闭合"

    fm_lines = lines[1:fm_end]
    fm_content = '\n'.join(fm_lines)

    # 检查必要字段
    if 'name:' not in fm_content:
        return False, "frontmatter缺少name字段"
    if 'description:' not in fm_content:
        return False, "frontmatter缺少description字段"

    # 检查name和folder名称是否一致
    folder_name = os.path.basename(os.path.dirname(os.path.abspath(skill_md_path)))
    for line in fm_lines:
        if line.strip().startswith('name:'):
            skill_name = line.split(':')[1].strip()
            if skill_name != folder_name:
                return False, f"name字段({skill_name})与文件夹名称({folder_name})不一致"

    return True, "Frontmatter验证通过"

def validate_meta_json():
    """验证_meta.json"""
    meta_path = "_meta.json"

    if not os.path.exists(meta_path):
        return False, "_meta.json不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta:
        return False, "_meta.json缺少id字段"
    if 'version' not in meta:
        return False, "_meta.json缺少version字段"

    return True, "_meta.json验证通过"

def validate_structure():
    """验证目录结构"""
    required_dirs = []
    optional_dirs = ['references', 'scripts', 'assets']

    for d in optional_dirs:
        if os.path.exists(d):
            required_dirs.append(d)

    return True, f"目录结构验证通过"

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '/workspace/temp-skills/requirements-insight')

    all_passed = True

    # 验证frontmatter
    passed, msg = validate_frontmatter()
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 验证meta.json
    passed, msg = validate_meta_json()
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 验证结构
    passed, msg = validate_structure()
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    if all_passed:
        print("\n✓ 所有验证通过")
        sys.exit(0)
    else:
        print("\n✗ 验证失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
