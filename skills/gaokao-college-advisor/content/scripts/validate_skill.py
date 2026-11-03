#!/usr/bin/env python3
"""
高考志愿填报技能验证脚本
验证技能结构是否符合规范
"""

import os
import json
import re
import sys

def validate_frontmatter(skill_md_path):
    """验证SKILL.md的frontmatter格式"""
    print("=" * 60)
    print("验证 Frontmatter 格式...")

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        print("❌ 错误：SKILL.md必须以---开头")
        return False

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                frontmatter_lines.append(i)
            else:
                frontmatter_lines.append(i)
                break

    if len(frontmatter_lines) < 2:
        print("❌ 错误：frontmatter未正确关闭")
        return False

    frontmatter_text = '\n'.join(lines[frontmatter_lines[0]:frontmatter_lines[1]+1])

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        pattern = rf'^{field}:'
        if not re.search(pattern, frontmatter_text, re.MULTILINE):
            print(f"❌ 错误：缺少必需字段 '{field}'")
            return False

    # 验证name格式（连字符，小写）
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            print(f"❌ 错误：name '{name}' 必须使用小写字母和连字符")
            return False

    # 检查markdown标题位置
    content_after_frontmatter = '\n'.join(lines[frontmatter_lines[1]+1:]).strip()
    if content_after_frontmatter.startswith('#'):
        print("❌ 错误：frontmatter后不能直接以#标题开头")
        return False

    print("✅ Frontmatter 格式验证通过")
    return True

def validate_meta_json(meta_path):
    """验证_meta.json文件"""
    print("=" * 60)
    print("验证 _meta.json 文件...")

    if not os.path.exists(meta_path):
        print("❌ 错误：_meta.json 文件不存在")
        return False

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            print(f"❌ 错误：_meta.json缺少必需字段 '{field}'")
            return False

    if not isinstance(meta['id'], int):
        print("❌ 错误：id必须是整数")
        return False

    if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        print("❌ 错误：version必须符合语义化版本格式（如1.0.0）")
        return False

    print("✅ _meta.json 验证通过")
    return True

def validate_directory_structure(base_path):
    """验证目录结构"""
    print("=" * 60)
    print("验证目录结构...")

    # 检查基本结构
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        filepath = os.path.join(base_path, filename)
        if not os.path.exists(filepath):
            print(f"❌ 错误：缺少必需文件 {filename}")
            return False

    print("✅ 目录结构验证通过")
    return True

def validate_paths_english(base_path):
    """验证所有路径和文件名是否为英文"""
    print("=" * 60)
    print("验证路径和文件名（英文）...")

    issues = []

    for root, dirs, files in os.walk(base_path):
        for dirname in dirs:
            if not re.match(r'^[a-zA-Z0-9_-]+$', dirname):
                issues.append(f"目录: {os.path.join(root, dirname)}")

        for filename in files:
            if not re.match(r'^[a-zA-Z0-9_.-]+$', filename):
                issues.append(f"文件: {os.path.join(root, filename)}")

    if issues:
        print("❌ 发现非英文字符路径或文件名：")
        for issue in issues:
            print(f"   - {issue}")
        return False

    print("✅ 路径和文件名验证通过")
    return True

def main():
    # 获取脚本所在目录的父目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)

    print(f"技能目录: {skill_dir}")
    print()

    all_passed = True

    # 验证目录结构
    if not validate_directory_structure(skill_dir):
        all_passed = False

    # 验证frontmatter
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    if not validate_frontmatter(skill_md_path):
        all_passed = False

    # 验证meta.json
    meta_path = os.path.join(skill_dir, '_meta.json')
    if not validate_meta_json(meta_path):
        all_passed = False

    # 验证路径英文
    if not validate_paths_english(skill_dir):
        all_passed = False

    print("=" * 60)
    if all_passed:
        print("🎉 所有验证通过！")
        return 0
    else:
        print("⚠️ 存在验证问题，请修复后重试")
        return 1

if __name__ == '__main__':
    sys.exit(main())
