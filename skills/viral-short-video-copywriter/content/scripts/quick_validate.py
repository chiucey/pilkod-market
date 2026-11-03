#!/usr/bin/env python3
"""
快速验证脚本 - 爆款短视频文案大师技能
"""
import os
import json
import re
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def validate_frontmatter():
    """验证frontmatter格式"""
    sk_path = os.path.join(SKILL_DIR, "SKILL.md")
    with open(sk_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        return False, "SKILL.md必须以---开头"

    # 提取frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "无法解析frontmatter"

    fm_text = match.group(1)

    # 检查必填字段
    if 'name:' not in fm_text:
        return False, "缺少name字段"
    if 'description:' not in fm_text:
        return False, "缺少description字段"

    return True, "Frontmatter验证通过"

def validate_meta():
    """验证_meta.json"""
    meta_path = os.path.join(SKILL_DIR, "_meta.json")
    if not os.path.exists(meta_path):
        return False, "_meta.json不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta:
        return False, "_meta.json缺少id字段"
    if 'version' not in meta:
        return False, "_meta.json缺少version字段"

    return True, "_meta.json验证通过"

def validate_naming():
    """验证命名规范"""
    folder_name = os.path.basename(SKILL_DIR)
    if not re.match(r'^[a-z0-9-]+$', folder_name):
        return False, f"文件夹名称'{folder_name}'必须为小写字母、数字、连字符"

    sk_path = os.path.join(SKILL_DIR, "SKILL.md")
    with open(sk_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取frontmatter中的name
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        fm = match.group(1)
        name_match = re.search(r'name:\s*(.+)', fm)
        if name_match:
            name_value = name_match.group(1).strip()
            if folder_name != name_value:
                return False, f"文件夹名'{folder_name}'与name字段'{name_value}'不一致"

    return True, "命名规范验证通过"

def main():
    all_passed = True
    results = []

    tests = [
        ("Frontmatter验证", validate_frontmatter),
        ("_meta.json验证", validate_meta),
        ("命名规范验证", validate_naming),
    ]

    for name, test_func in tests:
        passed, msg = test_func()
        results.append((name, passed, msg))
        if not passed:
            all_passed = False
        print(f"{'✅' if passed else '❌'} {name}: {msg}")

    print()
    if all_passed:
        print("🎉 所有验证通过！")
        return 0
    else:
        print("⚠️ 存在验证失败项，请修复后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
