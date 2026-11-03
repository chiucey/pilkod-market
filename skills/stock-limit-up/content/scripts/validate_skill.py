#!/usr/bin/env python3
"""
涨停板筛选与龙头股分析技能 - 验证脚本
验证 SKILL.md 的 frontmatter 和结构完整性
"""

import os
import re
import json
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def validate_frontmatter():
    """验证 SKILL.md 的 frontmatter"""
    skill_file = os.path.join(SKILL_DIR, "SKILL.md")

    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 --- 开头"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析 frontmatter"

    frontmatter_text = frontmatter_match.group(1)

    # 解析 YAML
    try:
        import yaml
        fm = yaml.safe_load(frontmatter_text)
    except:
        return False, "Frontmatter YAML 解析失败"

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in fm:
            return False, f"缺少必需字段: {field}"

    # 检查 name 格式
    name = fm['name']
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"name 必须使用小写字母、数字和连字符: {name}"

    # 检查 description 长度
    desc = fm['description']
    if len(desc) < 20:
        return False, "description 太短，需要更详细的触发描述"

    return True, "Frontmatter 验证通过"

def validate_meta():
    """验证 _meta.json"""
    meta_file = os.path.join(SKILL_DIR, "_meta.json")

    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 检查必需字段
    required = ['id', 'version']
    for field in required:
        if field not in meta:
            return False, f"缺少必需字段: {field}"

    # 验证版本格式
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"版本号格式错误: {version}"

    return True, "_meta.json 验证通过"

def validate_directory_structure():
    """验证目录结构"""
    required_dirs = []
    for dir_name in required_dirs:
        dir_path = os.path.join(SKILL_DIR, dir_name)
        if not os.path.isdir(dir_path):
            return False, f"缺少目录: {dir_name}"

    return True, "目录结构验证通过"

def main():
    """主验证流程"""
    print("=" * 50)
    print("涨停板筛选与龙头股分析技能 - 验证检查")
    print("=" * 50)

    all_passed = True

    # 1. Frontmatter 验证
    print("\n[1/3] 验证 Frontmatter...")
    passed, msg = validate_frontmatter()
    print(f"    {'✓' if passed else '✗'} {msg}")
    if not passed:
        all_passed = False

    # 2. Meta 验证
    print("\n[2/3] 验证 _meta.json...")
    passed, msg = validate_meta()
    print(f"    {'✓' if passed else '✗'} {msg}")
    if not passed:
        all_passed = False

    # 3. 目录结构
    print("\n[3/3] 验证目录结构...")
    passed, msg = validate_directory_structure()
    print(f"    {'✓' if passed else '✗'} {msg}")
    if not passed:
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证失败项")
        return 1

if __name__ == "__main__":
    sys.exit(main())
