#!/usr/bin/env python3
"""Alpha-Eleven 技能验证脚本"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(filepath):
    """验证frontmatter格式"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.strip().startswith('---'):
        return False, "Frontmatter必须以---开头"

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析frontmatter"

    frontmatter = frontmatter_match.group(1)

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            return False, f"缺少必填字段: {field}"

    # 检查name格式
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name必须使用小写字母、数字和连字符: {name}"

    # 检查description包含触发短语
    desc_match = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1)
        if '当用户要求' not in desc and 'Use when' not in desc:
            return False, "description必须包含触发短语（如'当用户要求'或'Use when'）"

    return True, "Frontmatter验证通过"

def validate_file_structure(skill_dir):
    """验证文件结构"""
    issues = []

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for fname in required_files:
        fpath = skill_dir / fname
        if not fpath.exists():
            issues.append(f"缺少必需文件: {fname}")

    # 检查_meta.json格式
    meta_path = skill_dir / '_meta.json'
    if meta_path.exists():
        import json
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            required_meta = ['id', 'version']
            for key in required_meta:
                if key not in meta:
                    issues.append(f"_meta.json缺少字段: {key}")
        except json.JSONDecodeError as e:
            issues.append(f"_meta.json格式错误: {e}")

    return issues

def validate_content(filepath):
    """验证内容质量"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = []

    # 检查是否包含11层
    layer_count = len(re.findall(r'第[0-9]+层', content))
    if layer_count < 11:
        issues.append(f"框架应包含11层，当前只有{layer_count}层引用")

    # 检查是否包含关键指标
    if '关键指标' not in content:
        issues.append("缺少关键指标定义")

    # 检查是否有输出定义
    output_count = content.count('**输出**')
    if output_count < 5:
        issues.append(f"输出定义过少（{output_count}个），建议每层都有明确输出")

    return issues

def main():
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / 'SKILL.md'

    print("=" * 50)
    print("Alpha-Eleven 技能验证")
    print("=" * 50)

    all_passed = True

    # 验证frontmatter
    print("\n[1] 验证Frontmatter格式...")
    passed, msg = validate_frontmatter(skill_md)
    print(f"    {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 验证文件结构
    print("\n[2] 验证文件结构...")
    issues = validate_file_structure(skill_dir)
    if issues:
        for issue in issues:
            print(f"    ✗ {issue}")
        all_passed = False
    else:
        print("    ✓ 文件结构完整")

    # 验证内容
    print("\n[3] 验证内容质量...")
    issues = validate_content(skill_md)
    if issues:
        for issue in issues:
            print(f"    ⚠ {issue}")
    else:
        print("    ✓ 内容质量符合要求")

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 验证通过！技能可以发布")
        return 0
    else:
        print("✗ 验证失败，请修复上述问题")
        return 1

if __name__ == '__main__':
    sys.exit(main())
