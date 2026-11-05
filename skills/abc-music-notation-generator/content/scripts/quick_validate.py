#!/usr/bin/env python3
"""
快速验证脚本 - 检查ABC音乐谱子生成器技能的基本结构
"""

import os
import sys
import re
import json

SKILL_DIR = "/workspace/temp-skills/abc-music-notation-generator"

def validate_frontmatter(skill_md_path):
    """验证SKILL.md的frontmatter格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查第一行必须是 ---
    if not content.startswith('---'):
        return False, "Frontmatter必须以 --- 开头"

    # 提取frontmatter
    lines = content.split('\n')
    # 第一行必须是 ---
    if lines[0].strip() != '---':
        return False, "Frontmatter格式错误 - 第一行必须是 ---"

    # 找到frontmatter结束（从第二行开始找）
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        return False, "Frontmatter缺少结束 ---"

    frontmatter_str = '\n'.join(lines[1:end_idx])

    # 检查必需字段
    if 'name:' not in frontmatter_str:
        return False, "缺少 name 字段"

    if 'description:' not in frontmatter_str:
        return False, "缺少 description 字段"

    # 提取name值
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_str, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not name:
            return False, "name字段不能为空"

    # 提取description值
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter_str, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 10:
            return False, "description字段内容过短"

    return True, "Frontmatter验证通过"

def validate_meta_json(meta_path):
    """验证_meta.json文件"""
    if not os.path.exists(meta_path):
        return False, "_meta.json文件不存在"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json格式错误: {e}"

    if 'id' not in meta:
        return False, "_meta.json缺少 id 字段"

    if 'version' not in meta:
        return False, "_meta.json缺少 version 字段"

    if not isinstance(meta['id'], int):
        return False, "_meta.json的 id 必须是整数"

    return True, "_meta.json验证通过"

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']

    for f in required_files:
        path = os.path.join(skill_dir, f)
        if not os.path.exists(path):
            return False, f"缺少必需文件: {f}"

    # 检查可选目录
    optional_dirs = ['references', 'assets', 'scripts']
    for d in optional_dirs:
        path = os.path.join(skill_dir, d)
        if os.path.exists(path):
            # 检查目录是否为空
            if not os.listdir(path):
                print(f"  警告: {d}/ 目录为空")

    return True, "目录结构验证通过"

def main():
    print("=" * 50)
    print("ABC音乐谱子生成器 - 技能验证")
    print("=" * 50)

    all_passed = True

    # 1. 验证frontmatter
    print("\n[1] 验证Frontmatter...")
    passed, msg = validate_frontmatter(os.path.join(SKILL_DIR, 'SKILL.md'))
    print(f"  {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 2. 验证_meta.json
    print("\n[2] 验证_meta.json...")
    passed, msg = validate_meta_json(os.path.join(SKILL_DIR, '_meta.json'))
    print(f"  {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 3. 验证目录结构
    print("\n[3] 验证目录结构...")
    passed, msg = validate_directory_structure(SKILL_DIR)
    print(f"  {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证失败项")
        return 1

if __name__ == '__main__':
    sys.exit(main())
