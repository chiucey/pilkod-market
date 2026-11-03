#!/usr/bin/env python3
"""
技能验证脚本
检查SKILL.md的frontmatter、结构和文件完整性
"""

import os
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_dir):
    """验证frontmatter格式"""
    skill_md = Path(skill_dir) / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md文件不存在"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否在文件开头
    if not content.startswith('---'):
        return False, "SKILL.md必须以frontmatter的---开头，不能有markdown标题"

    # 提取frontmatter
    lines = content.split('\n')
    if len(lines) < 3 or lines[0] != '---':
        return False, "frontmatter格式错误"

    # 找到frontmatter结束
    end_idx = -1
    for i, line in enumerate(lines[2:], start=2):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return False, "frontmatter未正确关闭"

    # 解析frontmatter内容
    frontmatter_lines = lines[1:end_idx+1]
    frontmatter_str = '\n'.join(frontmatter_lines)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if f"{field}:" not in frontmatter_str:
            return False, f"frontmatter缺少必需字段: {field}"

    # 检查name和description格式
    for line in frontmatter_lines[1:]:
        if line.strip().startswith('name:'):
            name_value = line.split(':', 1)[1].strip()
            if not name_value:
                return False, "name字段不能为空"
        if line.strip().startswith('description:'):
            desc_value = line.split(':', 1)[1].strip()
            if not desc_value:
                return False, "description字段不能为空"

    return True, "frontmatter验证通过"

def validate_meta_json(skill_dir):
    """验证_meta.json文件"""
    meta_file = Path(skill_dir) / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json文件不存在"

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in meta:
                return False, f"_meta.json缺少必需字段: {field}"

        # 检查id是否为数字
        if not isinstance(meta['id'], int):
            return False, "_meta.json的id必须是整数"

        return True, "_meta.json验证通过"

    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON格式错误: {e}"

def validate_structure(skill_dir):
    """验证目录结构"""
    skill_path = Path(skill_dir)

    # 检查必需的文件
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        if not (skill_path / filename).exists():
            return False, f"缺少必需文件: {filename}"

    return True, "目录结构验证通过"

def main():
    # 获取技能目录
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # 默认检查当前目录下的技能
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"验证技能目录: {skill_dir}")
    print("-" * 50)

    all_passed = True

    # 1. 结构验证
    passed, msg = validate_structure(skill_dir)
    print(f"[{'✓' if passed else '✗'}] 结构验证: {msg}")
    all_passed = all_passed and passed

    # 2. frontmatter验证
    passed, msg = validate_frontmatter(skill_dir)
    print(f"[{'✓' if passed else '✗'}] Frontmatter验证: {msg}")
    all_passed = all_passed and passed

    # 3. _meta.json验证
    passed, msg = validate_meta_json(skill_dir)
    print(f"[{'✓' if passed else '✗'}] _meta.json验证: {msg}")
    all_passed = all_passed and passed

    print("-" * 50)
    if all_passed:
        print("✓ 所有验证通过!")
        return 0
    else:
        print("✗ 存在验证失败项")
        return 1

if __name__ == "__main__":
    sys.exit(main())
