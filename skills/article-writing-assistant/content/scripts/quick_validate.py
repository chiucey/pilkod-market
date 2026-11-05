#!/usr/bin/env python3
"""
文章写作助手技能验证脚本
验证 SKILL.md 格式和 _meta.json 完整性
"""

import os
import json
import sys
from pathlib import Path

def validate_skill_structure(skill_path):
    """验证技能目录结构"""
    errors = []
    warnings = []

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_path, file)
        if not os.path.exists(file_path):
            errors.append(f"缺少必需文件: {file}")

    return errors, warnings

def validate_skill_md(skill_path):
    """验证 SKILL.md 文件格式"""
    errors = []
    warnings = []

    skill_md_path = os.path.join(skill_path, 'SKILL.md')

    if not os.path.exists(skill_md_path):
        return ["SKILL.md 不存在"], []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头（frontmatter）
    if not content.strip().startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter (---) 开头")

    # 解析 frontmatter
    if content.startswith('---'):
        lines = content.split('\n')
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break

        if frontmatter_end == -1:
            errors.append("SKILL.md frontmatter 未正确闭合 (缺少结束的 ---)")
            return errors, warnings

        # 解析 frontmatter 内容
        frontmatter_lines = lines[1:frontmatter_end]
        frontmatter = {}
        for line in frontmatter_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        # 检查必需字段
        if 'name' not in frontmatter:
            errors.append("frontmatter 缺少 'name' 字段")
        else:
            name = frontmatter['name']
            # 检查名称格式（连字符）
            if ' ' in name:
                errors.append(f"name 必须使用连字符格式，不能包含空格: '{name}'")
            # 检查名称长度
            if len(name) > 64:
                errors.append(f"name 长度不能超过 64 字符: 当前 {len(name)} 字符")

        if 'description' not in frontmatter:
            errors.append("frontmatter 缺少 'description' 字段")
        elif len(frontmatter.get('description', '')) < 10:
            warnings.append("description 长度过短，建议至少 10 个字符")

    return errors, warnings

def validate_meta_json(skill_path):
    """验证 _meta.json 文件"""
    errors = []
    warnings = []

    meta_path = os.path.join(skill_path, '_meta.json')

    if not os.path.exists(meta_path):
        return ["_meta.json 不存在"], []

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 检查必需字段
        required_fields = ['id', 'version']
        for field in required_fields:
            if field not in meta:
                errors.append(f"_meta.json 缺少 '{field}' 字段")

        # 验证 version 格式（语义化版本）
        if 'version' in meta:
            version = meta['version']
            if not all(part.isdigit() for part in version.split('.')):
                errors.append(f"version 格式无效，应为语义化版本 (如 1.0.0): '{version}'")

        # 检查 id 是否为数字
        if 'id' in meta:
            try:
                int(meta['id'])
            except ValueError:
                errors.append(f"id 必须为数字: '{meta['id']}'")

    except json.JSONDecodeError as e:
        errors.append(f"_meta.json 格式错误: {e}")

    return errors, warnings

def validate_naming(skill_path):
    """验证命名规范"""
    errors = []
    warnings = []

    skill_name = os.path.basename(skill_path)

    # 检查文件夹名称
    if ' ' in skill_name:
        errors.append(f"技能文件夹名称不能包含空格: '{skill_name}'")
    if not skill_name.islower():
        warnings.append(f"技能文件夹名称建议使用小写: '{skill_name}'")
    if len(skill_name) > 64:
        errors.append(f"技能文件夹名称过长: {len(skill_name)} 字符")

    # 检查 SKILL.md 中的 name 是否匹配文件夹
    skill_md_path = os.path.join(skill_path, 'SKILL.md')
    if os.path.exists(skill_md_path):
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.startswith('---'):
            lines = content.split('\n')
            frontmatter_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    frontmatter_end = i
                    break

            if frontmatter_end > 0:
                frontmatter_lines = lines[1:frontmatter_end]
                for line in frontmatter_lines:
                    if line.startswith('name:'):
                        frontmatter_name = line.split(':', 1)[1].strip()
                        if frontmatter_name != skill_name:
                            errors.append(
                                f"SKILL.md 中的 name 与文件夹名称不匹配: "
                                f"'{frontmatter_name}' != '{skill_name}'"
                            )

    return errors, warnings

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]

    print(f"验证技能: {skill_path}")
    print("=" * 50)

    all_errors = []
    all_warnings = []

    # 执行各项验证
    errors, warnings = validate_skill_structure(skill_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = validate_skill_md(skill_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = validate_meta_json(skill_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = validate_naming(skill_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # 输出结果
    if all_warnings:
        print("\n⚠️  警告:")
        for warning in all_warnings:
            print(f"  - {warning}")

    if all_errors:
        print("\n❌ 错误:")
        for error in all_errors:
            print(f"  - {error}")
        print("\n验证失败！")
        sys.exit(1)
    else:
        print("\n✅ 验证通过！")
        sys.exit(0)

if __name__ == '__main__':
    main()
