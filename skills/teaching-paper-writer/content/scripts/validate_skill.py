#!/usr/bin/env python3
"""
教学论文写作助手 - 技能验证脚本
验证 SKILL.md 文件的 frontmatter 格式和结构完整性
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 frontmatter 格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查文件开头是否是 frontmatter
    if not content.startswith('---'):
        return False, "错误：SKILL.md 必须以 YAML frontmatter 开头（---）"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "错误：无法解析 YAML frontmatter"

    frontmatter = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            return False, f"错误：frontmatter 缺少必需字段 '{field}'"

    # 检查 name 字段格式（连字符）
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name_value):
            return False, f"错误：name 字段必须使用连字符格式（小写），当前值：{name_value}"

    # 检查 description 是否包含触发短语
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
    if desc_match:
        desc_value = desc_match.group(1).strip()
        if '当' not in desc_value or len(desc_value) < 20:
            return False, "错误：description 应包含触发短语（如'当用户要求...'）且长度适中"

    # 验证通过 - frontmatter 格式正确
    return True, "Frontmatter 验证通过"

def validate_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        filepath = skill_dir / filename
        if not filepath.exists():
            return False, f"错误：缺少必需文件 {filename}"

    # 检查 _meta.json 格式
    import json
    meta_path = skill_dir / '_meta.json'
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_meta_fields = ['id', 'version']
    for field in required_meta_fields:
        if field not in meta:
            return False, f"错误：_meta.json 缺少必需字段 '{field}'"

    # 检查版本号格式
    if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        return False, f"错误：_meta.json 的 version 字段应符合语义化版本格式（x.y.z），当前值：{meta['version']}"

    return True, "结构验证通过"

def validate_naming(skill_dir, skill_name):
    """验证命名规范"""
    # 检查文件夹名称是否为英文
    if not re.match(r'^[a-z0-9-]+$', skill_dir.name):
        return False, f"错误：技能文件夹名称应使用英文（连字符格式），当前名称：{skill_dir.name}"

    # 检查文件夹名称是否与 SKILL.md 中的 name 一致
    skill_md_path = skill_dir / 'SKILL.md'
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    name_match = re.search(r'^name:\s*(.+)', content, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if name_value != skill_dir.name:
            return False, f"错误：文件夹名称 '{skill_dir.name}' 与 SKILL.md 中的 name '{name_value}' 不一致"

    return True, "命名验证通过"

def validate_references(skill_dir):
    """验证参考文档"""
    references_dir = skill_dir / 'references'
    if references_dir.exists():
        for md_file in references_dir.glob('*.md'):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if len(content) < 100:
                return False, f"警告：{md_file.name} 内容过少，可能不完整"
    return True, "参考文档验证通过"

def main():
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    skill_md_path = skill_dir / 'SKILL.md'

    print(f"正在验证技能：{skill_dir.name}")
    print("-" * 50)

    all_passed = True

    # 验证 frontmatter
    passed, message = validate_frontmatter(skill_md_path)
    print(f"[{'✓' if passed else '✗'}] {message}")
    all_passed = all_passed and passed

    # 验证结构
    passed, message = validate_structure(skill_dir)
    print(f"[{'✓' if passed else '✗'}] {message}")
    all_passed = all_passed and passed

    # 验证命名
    passed, message = validate_naming(skill_dir, skill_dir.name)
    print(f"[{'✓' if passed else '✗'}] {message}")
    all_passed = all_passed and passed

    # 验证参考文档
    passed, message = validate_references(skill_dir)
    print(f"[{'✓' if passed else '✗'}] {message}")
    all_passed = all_passed and passed

    print("-" * 50)
    if all_passed:
        print("✓ 所有验证通过！")
        sys.exit(0)
    else:
        print("✗ 存在验证失败项，请修复后重试")
        sys.exit(1)

if __name__ == '__main__':
    main()
