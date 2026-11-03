#!/usr/bin/env python3
"""
技能结构验证脚本
验证SKILL.md的frontmatter格式和必要字段
"""

import json
import os
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """
    验证SKILL.md的frontmatter格式

    Args:
        skill_path: 技能目录路径

    Returns:
        (是否通过, 消息)
    """
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md文件不存在"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        return False, "SKILL.md必须以---开头（frontmatter开始）"

    # 提取frontmatter
    lines = content.split('\n')
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

    if not frontmatter_lines:
        return False, "frontmatter为空"

    # 解析YAML
    try:
        frontmatter = {}
        for line in frontmatter_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
    except Exception as e:
        return False, f"frontmatter解析失败: {e}"

    # 验证必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            return False, f"缺少必需字段: {field}"

    # 验证name格式
    name = frontmatter['name']
    if not name or ' ' in name:
        return False, "name字段不能包含空格，请使用连字符格式"

    # 验证description不为空
    desc = frontmatter['description']
    if not desc or len(desc) < 10:
        return False, "description字段太短，需要详细描述技能功能"

    return True, "frontmatter验证通过"


def validate_meta_json(skill_path: Path) -> tuple[bool, str]:
    """
    验证_meta.json文件

    Args:
        skill_path: 技能目录路径

    Returns:
        (是否通过, 消息)
    """
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json文件不存在"

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON解析失败: {e}"

    # 验证必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"缺少必需字段: {field}"

    # 验证version格式
    version = meta['version']
    if not isinstance(version, str) or not version.replace('.', '').isdigit():
        return False, "version字段格式错误，应为语义化版本(如1.0.0)"

    return True, "_meta.json验证通过"


def validate_structure(skill_path: Path) -> tuple[bool, str]:
    """
    验证目录结构

    Args:
        skill_path: 技能目录路径

    Returns:
        (是否通过, 消息)
    """
    # 必需的目录/文件
    required_items = [
        "SKILL.md",
        "_meta.json"
    ]

    # 检查必需项
    for item in required_items:
        item_path = skill_path / item
        if not item_path.exists():
            return False, f"缺少必需文件: {item}"

    # 推荐结构
    recommended = {
        "scripts": ["analyze_bills.py", "visualize_trends.py"],
        "references": [],
        "assets": []
    }

    missing_recommended = []
    for dir_name, files in recommended.items():
        dir_path = skill_path / dir_name
        if dir_path.exists():
            for file in files:
                if not (dir_path / file).exists():
                    missing_recommended.append(f"{dir_name}/{file}")

    if missing_recommended:
        return True, f"结构验证通过（缺少推荐文件: {', '.join(missing_recommended)}）"

    return True, "目录结构验证通过"


def main():
    """主函数"""
    if len(sys.argv) < 2:
        # 默认检查当前目录
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    print(f"验证技能目录: {skill_path}")
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

    # 验证结构
    passed, msg = validate_structure(skill_path)
    print(f"[{'✓' if passed else '✗'}] 目录结构: {msg}")
    all_passed = all_passed and passed

    print("-" * 50)

    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 存在验证失败项")
        return 1


if __name__ == '__main__':
    sys.exit(main())
