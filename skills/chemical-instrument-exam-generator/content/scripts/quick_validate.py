#!/usr/bin/env python3
"""
化工仪表培训出题技能 - 快速验证脚本
验证 SKILL.md 和 _meta.json 的基本格式和内容
"""

import os
import json
import sys
from pathlib import Path


def validate_frontmatter(skill_md_path):
    """验证 SKILL.md 的 frontmatter 格式"""
    errors = []
    warnings = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter --- 开头")

    # 提取 frontmatter
    lines = content.split('\n')
    if len(lines) < 3 or lines[0].strip() != '---':
        errors.append("SKILL.md frontmatter 格式不正确")
        return errors, warnings

    # 找到 frontmatter 结束标记
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("SKILL.md 缺少 frontmatter 结束标记 ---")
        return errors, warnings

    # 解析 frontmatter
    frontmatter_lines = lines[1:frontmatter_end]
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key = line.split(':')[0].strip()
            frontmatter[key] = True

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"frontmatter 缺少必填字段: {field}")

    # 检查 name 格式（连字符）
    if 'name' in frontmatter:
        name = frontmatter.get('name', '')
        if 'name' in frontmatter:
            # 重新提取完整值
            for line in frontmatter_lines:
                if line.strip().startswith('name:'):
                    name = line.split(':', 1)[1].strip()
                    break
        if not name or ' ' in name:
            warnings.append("name 字段建议使用连字符格式（如: my-skill）")

    # 检查 description 是否包含触发短语
    if 'description' in frontmatter:
        for line in frontmatter_lines:
            if line.strip().startswith('description:'):
                desc = line.split(':', 1)[1].strip()
                if len(desc) < 20:
                    warnings.append("description 建议至少20个字符，包含触发短语")
                break

    return errors, warnings


def validate_meta_json(meta_path):
    """验证 _meta.json 格式和内容"""
    errors = []
    warnings = []

    if not os.path.exists(meta_path):
        errors.append("_meta.json 文件不存在")
        return errors, warnings

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json 格式错误: {e}")
        return errors, warnings

    # 检查必填字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必填字段: {field}")

    # 检查 id 类型
    if 'id' in meta:
        if not isinstance(meta['id'], int):
            errors.append("_meta.json 的 id 必须是整数类型")

    # 检查 version 格式
    if 'version' in meta:
        version = meta['version']
        if not isinstance(version, str):
            errors.append("_meta.json 的 version 必须是字符串类型（如: 1.0.0）")
        elif not version.replace('.', '').replace('', '').isdigit():
            warnings.append("version 建议使用语义化版本格式（如: 1.0.0）")

    return errors, warnings


def validate_directory_structure(skill_dir):
    """验证目录结构"""
    errors = []
    warnings = []

    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            errors.append(f"缺少必要文件: {file}")

    # 检查可选目录
    optional_dirs = ['scripts', 'references', 'assets']
    for dir_name in optional_dirs:
        dir_path = os.path.join(skill_dir, dir_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            # 检查是否为空目录
            if not os.listdir(dir_path):
                warnings.append(f"{dir_name}/ 目录为空")

    return errors, warnings


def main():
    skill_dir = Path(__file__).parent.parent
    skill_md_path = skill_dir / 'SKILL.md'
    meta_path = skill_dir / '_meta.json'

    print("=" * 60)
    print("化工仪表培训出题技能 - 验证报告")
    print("=" * 60)
    print(f"技能目录: {skill_dir}")
    print()

    all_errors = []
    all_warnings = []

    # 验证 frontmatter
    print("[1/3] 验证 SKILL.md frontmatter...")
    errors, warnings = validate_frontmatter(skill_md_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for err in errors:
            print(f"  ❌ {err}")
    if warnings:
        for warn in warnings:
            print(f"  ⚠️  {warn}")
    if not errors and not warnings:
        print("  ✅ 通过")
    print()

    # 验证 meta.json
    print("[2/3] 验证 _meta.json...")
    errors, warnings = validate_meta_json(meta_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for err in errors:
            print(f"  ❌ {err}")
    if warnings:
        for warn in warnings:
            print(f"  ⚠️  {warn}")
    if not errors and not warnings:
        print("  ✅ 通过")
    print()

    # 验证目录结构
    print("[3/3] 验证目录结构...")
    errors, warnings = validate_directory_structure(skill_dir)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for err in errors:
            print(f"  ❌ {err}")
    if warnings:
        for warn in warnings:
            print(f"  ⚠️  {warn}")
    if not errors and not warnings:
        print("  ✅ 通过")
    print()

    # 最终结果
    print("=" * 60)
    if all_errors:
        print(f"❌ 验证失败: {len(all_errors)} 个错误")
        sys.exit(1)
    elif all_warnings:
        print(f"⚠️  验证通过（有 {len(all_warnings)} 个警告）")
        sys.exit(0)
    else:
        print("✅ 验证通过: 所有检查项均合格")
        sys.exit(0)


if __name__ == '__main__':
    main()
