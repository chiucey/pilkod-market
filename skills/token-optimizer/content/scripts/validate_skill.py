#!/usr/bin/env python3
"""
TOKEN优化器技能验证脚本
验证 SKILL.md 和 _meta.json 的格式和内容
"""

import os
import re
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 frontmatter 格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # 检查第一行是否是 ---
    if len(lines) < 1 or lines[0].strip() != '---':
        return False, "SKILL.md 必须以 --- 开头"

    # 找到结束标记 ---
    end_found = False
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_found = True
            break

    if not end_found:
        return False, "Frontmatter 格式不正确，需要 ---...--- 包裹"

    # 解析 YAML frontmatter
    fm_lines = []
    in_fm = False
    for line in lines:
        if line.strip() == '---':
            if not in_fm:
                in_fm = True
                continue
            else:
                break
        if in_fm:
            fm_lines.append(line)

    fm_content = '\n'.join(fm_lines)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(f'^{field}:', fm_content, re.MULTILINE):
            return False, f"Frontmatter 缺少必需字段: {field}"

    return True, "OK"

def validate_meta_json(meta_path):
    """验证 _meta.json 格式"""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        required_keys = ['id', 'version']
        for key in required_keys:
            if key not in meta:
                return False, f"_meta.json 缺少必需字段: {key}"

        # ID 应该是数字
        if not isinstance(meta.get('id'), int):
            return False, "_meta.json 中 id 应该是整数"

        # version 应该是字符串
        if not isinstance(meta.get('version'), str):
            return False, "_meta.json 中 version 应该是字符串"

        return True, "OK"
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 解析错误: {e}"
    except Exception as e:
        return False, f"_meta.json 读取错误: {e}"

def validate_name_consistency(skill_md_path, folder_name):
    """验证 name 字段与文件夹名称一致"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 frontmatter 中的 name
    match = re.search(r'^name:\s*(.+?)$', content, re.MULTILINE)
    if match:
        frontmatter_name = match.group(1).strip()
        if frontmatter_name != folder_name:
            return False, f"Name 不一致: frontmatter='{frontmatter_name}', folder='{folder_name}'"

    return True, "OK"

def validate_structure(skill_dir):
    """验证目录结构"""
    required_dirs = []
    required_files = ['SKILL.md', '_meta.json']

    issues = []

    for f in required_files:
        path = Path(skill_dir) / f
        if not path.exists():
            issues.append(f"缺少必需文件: {f}")

    return len(issues) == 0, '; '.join(issues) if issues else "OK"

def main():
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent

    print(f"=== TOKEN优化器技能验证 ===")
    print(f"技能目录: {skill_dir}")
    print()

    all_passed = True

    # 1. 结构验证
    print("1. 目录结构检查...")
    passed, msg = validate_structure(skill_dir)
    print(f"   结果: {'✅ 通过' if passed else '❌ 失败'} - {msg}")
    all_passed = all_passed and passed

    # 2. Frontmatter 验证
    print("\n2. Frontmatter 格式检查...")
    passed, msg = validate_frontmatter(skill_dir / 'SKILL.md')
    print(f"   结果: {'✅ 通过' if passed else '❌ 失败'} - {msg}")
    all_passed = all_passed and passed

    # 3. _meta.json 验证
    print("\n3. _meta.json 检查...")
    passed, msg = validate_meta_json(skill_dir / '_meta.json')
    print(f"   结果: {'✅ 通过' if passed else '❌ 失败'} - {msg}")
    all_passed = all_passed and passed

    # 4. 名称一致性验证
    print("\n4. 名称一致性检查...")
    folder_name = skill_dir.name
    passed, msg = validate_name_consistency(skill_dir / 'SKILL.md', folder_name)
    print(f"   结果: {'✅ 通过' if passed else '❌ 失败'} - {msg}")
    all_passed = all_passed and passed

    print("\n" + "=" * 40)
    if all_passed:
        print("✅ 所有验证通过!")
        return 0
    else:
        print("❌ 存在验证失败项")
        return 1

if __name__ == '__main__':
    sys.exit(main())
