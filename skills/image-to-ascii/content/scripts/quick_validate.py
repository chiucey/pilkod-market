#!/usr/bin/env python3
"""
技能快速验证脚本
Quick validation script for image-to-ascii skill
"""

import os
import json
import sys


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
        else:
            print(f"✓ 找到文件: {file}")

    # 检查SKILL.md的frontmatter
    skill_md = os.path.join(skill_path, 'SKILL.md')
    if os.path.exists(skill_md):
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.startswith('---'):
                errors.append("SKILL.md必须以frontmatter(---)开头")
            if 'name:' not in content:
                errors.append("SKILL.md缺少name字段")
            if 'description:' not in content:
                errors.append("SKILL.md缺少description字段")
    else:
        warnings.append("references目录不存在")

    # 检查_meta.json
    meta_json = os.path.join(skill_path, '_meta.json')
    if os.path.exists(meta_json):
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
                if 'id' not in meta:
                    errors.append("_meta.json缺少id字段")
                if 'version' not in meta:
                    errors.append("_meta.json缺少version字段")
                print(f"✓ _meta.json有效: id={meta.get('id')}, version={meta.get('version')}")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json格式错误: {e}")

    # 检查references目录
    references_dir = os.path.join(skill_path, 'references')
    if os.path.exists(references_dir):
        print(f"✓ references目录存在")
        py_files = [f for f in os.listdir(references_dir) if f.endswith('.py')]
        if py_files:
            print(f"✓ 找到Python参考文件: {', '.join(py_files)}")
    else:
        warnings.append("references目录不存在")

    return errors, warnings


def main():
    skill_path = '/workspace/temp-skills/image-to-ascii'

    print("=" * 50)
    print("图片转ASCII艺术技能 - 验证检查")
    print("=" * 50)

    errors, warnings = validate_skill_structure(skill_path)

    print("\n" + "=" * 50)
    print("验证结果:")
    print("=" * 50)

    if warnings:
        print("\n⚠️ 警告:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\n❌ 错误:")
        for e in errors:
            print(f"  - {e}")
        print("\n验证失败！")
        sys.exit(1)
    else:
        print("\n✅ 所有验证通过！")
        sys.exit(0)


if __name__ == '__main__':
    main()
