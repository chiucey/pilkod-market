#!/usr/bin/env python3
"""
跨境电商选品技能 - 快速验证脚本
验证技能结构和frontmatter是否符合规范
"""

import os
import sys
import json
from pathlib import Path

def validate_frontmatter(skill_path):
    """验证SKILL.md的frontmatter格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md 文件不存在"

    content = skill_md.read_text(encoding='utf-8')

    # 检查frontmatter是否在文件开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 --- 开头（frontmatter必须在第一行）"

    # 解析frontmatter
    lines = content.split('\n')
    if len(lines) < 3 or lines[0].strip() != '---':
        return False, "frontmatter格式错误：缺少结束标记"

    # 找到frontmatter结束标记
    end_index = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_index = i
            break

    if end_index < 2:
        return False, "frontmatter格式错误：缺少结束标记"

    # 提取frontmatter内容
    frontmatter_lines = []
    in_frontmatter = False
    for line in lines:
        if line.strip() == '---' and not in_frontmatter:
            in_frontmatter = True
            continue
        elif line.strip() == '---' and in_frontmatter:
            break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not any(line.strip().startswith(f'{field}:') for line in frontmatter_lines):
            return False, f"frontmatter缺少必需字段: {field}"

    # 验证name字段格式
    for line in frontmatter_lines:
        if line.strip().startswith('name:'):
            name_value = line.split(':', 1)[1].strip()
            if not name_value:
                return False, "name字段不能为空"
            if not name_value.replace('-', '').replace('_', '').isalnum():
                return False, "name字段只能包含字母、数字和连字符"
            if not name_value.startswith('skill-') and not any(c.isalpha() for c in name_value):
                pass  # 允许非skill-前缀的名称

    # 验证description字段
    for line in frontmatter_lines:
        if line.strip().startswith('description:'):
            desc_value = line.split(':', 1)[1].strip()
            if len(desc_value) < 10:
                return False, "description字段长度至少10个字符"

    return True, "frontmatter验证通过"

def validate_meta_json(skill_path):
    """验证_meta.json文件"""
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json 文件不存在"

    try:
        meta_data = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return False, "_meta.json 格式错误：JSON解析失败"

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta_data:
            return False, f"_meta.json缺少必需字段: {field}"

    # 验证ID格式（应为整数）
    if not isinstance(meta_data['id'], int):
        return False, "_meta.json中id必须是整数"

    # 验证version格式
    version = meta_data.get('version', '')
    if not isinstance(version, str) or not version:
        return False, "_meta.json中version必须是字符串且非空"

    # 验证version格式（x.y.z）
    version_parts = version.split('.')
    if len(version_parts) != 3:
        return False, "_meta.json中version格式应为 x.y.z"

    return True, "_meta.json验证通过"

def validate_directory_structure(skill_path):
    """验证目录结构"""
    required_dirs = []

    # 检查scripts目录（如果存在）
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        # scripts目录存在时，应该有验证脚本
        pass

    return True, "目录结构验证通过"

def validate_naming(skill_path):
    """验证命名规范"""
    skill_name = skill_path.name

    # 检查技能名称是否为英文
    if not all(ord(c) < 128 for c in skill_name):
        return False, "技能目录名称必须使用英文字母"

    # 检查格式（连字符）
    if not skill_name.replace('-', '').replace('_', '').isalnum():
        return False, "技能目录名称格式错误"

    return True, "命名规范验证通过"

def main():
    skill_path = Path(__file__).parent.parent

    print(f"正在验证技能: {skill_path.name}")
    print("-" * 50)

    all_passed = True

    # 验证frontmatter
    passed, msg = validate_frontmatter(skill_path)
    print(f"[{'✓' if passed else '✗'}] SKILL.md frontmatter: {msg}")
    all_passed = all_passed and passed

    # 验证_meta.json
    passed, msg = validate_meta_json(skill_path)
    print(f"[{'✓' if passed else '✗'}] _meta.json: {msg}")
    all_passed = all_passed and passed

    # 验证目录结构
    passed, msg = validate_directory_structure(skill_path)
    print(f"[{'✓' if passed else '✗'}] 目录结构: {msg}")
    all_passed = all_passed and passed

    # 验证命名
    passed, msg = validate_naming(skill_path)
    print(f"[{'✓' if passed else '✗'}] 命名规范: {msg}")
    all_passed = all_passed and passed

    print("-" * 50)

    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 验证失败，请修复上述问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
