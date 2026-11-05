#!/usr/bin/env python3
"""
技能验证脚本 - 验证 SKILL.md 和 _meta.json 的格式和内容
"""
import json
import os
import sys
from pathlib import Path


def validate_frontmatter(skill_md_path: str) -> tuple[bool, list[str]]:
    """验证 SKILL.md 的 frontmatter 格式"""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter (---) 开头")
        return False, errors

    # 提取 frontmatter
    lines = content.split('\n')
    if len(lines) < 3:
        errors.append("SKILL.md frontmatter 不完整")
        return False, errors

    frontmatter_lines = []
    in_frontmatter = False
    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = '\n'.join(frontmatter_lines)

    # 解析 YAML（简化检查）
    required_keys = ['name', 'description']
    for key in required_keys:
        if not any(line.strip().startswith(f'{key}:') for line in frontmatter_lines):
            errors.append(f"Frontmatter 缺少必需字段: {key}")

    # 检查 name 格式
    name_line = [l for l in frontmatter_lines if l.strip().startswith('name:')]
    if name_line:
        name_value = name_line[0].split(':', 1)[1].strip()
        if not name_value:
            errors.append("name 字段不能为空")
        if ' ' in name_value:
            errors.append("name 必须使用连字符格式 (kebab-case)")

    # 检查 description
    desc_line = [l for l in frontmatter_lines if l.strip().startswith('description:')]
    if desc_line:
        desc_value = desc_line[0].split(':', 1)[1].strip()
        if len(desc_value) < 10:
            errors.append("description 太短，至少需要10个字符")

    return len(errors) == 0, errors


def validate_meta(meta_path: str) -> tuple[bool, list[str]]:
    """验证 _meta.json 格式"""
    errors = []

    if not os.path.exists(meta_path):
        errors.append("_meta.json 文件不存在")
        return False, errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json 格式错误: {e}")
        return False, errors

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必需字段: {field}")

    # 验证 id 是数字
    if 'id' in meta and not isinstance(meta['id'], (int, float)):
        errors.append("id 必须是数字类型")

    # 验证 version 格式
    if 'version' in meta:
        version = meta['version']
        if not isinstance(version, str):
            errors.append("version 必须是字符串格式 (如 '1.0.0')")
        elif not any(v.isdigit() for v in version.split('.')):
            errors.append("version 格式应为语义化版本 (如 '1.0.0')")

    return len(errors) == 0, errors


def validate_structure(skill_dir: str) -> tuple[bool, list[str]]:
    """验证技能目录结构"""
    errors = []

    # 必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            errors.append(f"缺少必需文件: {file}")

    # 检查不应存在的文件
    forbidden_patterns = ['node_modules', '.git', '__pycache__']
    for root, dirs, files in os.walk(skill_dir):
        for d in dirs:
            if d in forbidden_patterns:
                errors.append(f"禁止的目录: {d}")
        for f in files:
            if f.endswith('.pyc') or f.endswith('.pyo'):
                errors.append(f"禁止的文件: {f}")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("用法: python validate_skill.py <skill_directory>")
        sys.exit(1)

    skill_dir = sys.argv[1]
    all_valid = True
    all_errors = []

    # 验证结构
    valid, errors = validate_structure(skill_dir)
    if not valid:
        all_valid = False
        all_errors.extend(["结构错误:"] + errors)

    # 验证 SKILL.md
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md):
        valid, errors = validate_frontmatter(skill_md)
        if not valid:
            all_valid = False
            all_errors.extend(["SKILL.md 错误:"] + errors)

    # 验证 _meta.json
    meta_json = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_json):
        valid, errors = validate_meta(meta_json)
        if not valid:
            all_valid = False
            all_errors.extend(["_meta.json 错误:"] + errors)

    if all_valid:
        print("✓ 验证通过")
        sys.exit(0)
    else:
        print("✗ 验证失败:")
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
