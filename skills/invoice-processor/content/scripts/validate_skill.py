#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
技能验证脚本
验证技能结构和内容是否符合规范
"""
import os
import json
from pathlib import Path


def validate_skill(skill_dir: str) -> bool:
    """
    验证技能目录

    Args:
        skill_dir: 技能目录路径

    Returns:
        bool: 验证是否通过
    """
    skill_dir = Path(skill_dir)
    errors = []
    warnings = []

    print("=" * 50)
    print(f"验证技能: {skill_dir.name}")
    print("=" * 50)

    # 1. 检查目录是否存在
    if not skill_dir.exists():
        errors.append(f"目录不存在: {skill_dir}")
        return False

    # 2. 检查必需文件
    required_files = ['SKILL.md', '_meta.json', 'main.py']
    for file_name in required_files:
        file_path = skill_dir / file_name
        if not file_path.exists():
            errors.append(f"缺少必需文件: {file_name}")

    # 3. 检查 SKILL.md frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否以 --- 开头
        if not content.strip().startswith('---'):
            errors.append("SKILL.md 必须以 YAML frontmatter 开头")

        # 检查必需字段
        if 'name:' not in content:
            errors.append("SKILL.md 缺少 name 字段")
        if 'description:' not in content:
            errors.append("SKILL.md 缺少 description 字段")

    # 4. 检查 _meta.json
    meta_json = skill_dir / "_meta.json"
    if meta_json.exists():
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    # 5. 检查目录结构
    expected_dirs = ['core', 'parsers', 'processors']
    for dir_name in expected_dirs:
        dir_path = skill_dir / dir_name
        if not dir_path.exists():
            warnings.append(f"建议包含目录: {dir_name}")

    # 输出结果
    print("\n验证结果:")
    if errors:
        print("\n❌ 错误:")
        for error in errors:
            print(f"   - {error}")

    if warnings:
        print("\n⚠️ 警告:")
        for warning in warnings:
            print(f"   - {warning}")

    if not errors:
        print("\n✅ 验证通过!")
        return True
    else:
        print("\n❌ 验证失败")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python validate_skill.py <skill_dir>")
        sys.exit(1)

    skill_dir = sys.argv[1]
    success = validate_skill(skill_dir)
    sys.exit(0 if success else 1)
