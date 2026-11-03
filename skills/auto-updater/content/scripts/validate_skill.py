#!/usr/bin/env python3
"""
Auto-Updater Skill Validation Script
验证技能结构和内容的正确性
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """验证 SKILL.md frontmatter 格式"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md 文件不存在"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter --- 开头"

    # 提取 frontmatter - 查找结束标记
    # 格式: --- (开始)\n name: ... \n description: ... \n --- (结束)
    lines = content.split('\n')

    # lines[0] 应该是 "---" (开始标记)
    if len(lines) < 1 or lines[0].strip() != '---':
        return False, "SKILL.md frontmatter 格式错误 - 缺少开始标记 ---"

    # 查找结束标记 ---
    end_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return False, "SKILL.md 缺少 frontmatter 结束标记 ---"

    # 提取 frontmatter 内容 (从第1行到结束标记之前)
    frontmatter = '\n'.join(lines[1:end_idx])

    # 验证必需字段
    if 'name:' not in frontmatter:
        return False, "frontmatter 缺少 name 字段"

    if 'description:' not in frontmatter:
        return False, "frontmatter 缺少 description 字段"

    return True, "Frontmatter 验证通过"


def validate_meta_json(skill_path: Path) -> tuple[bool, str]:
    """验证 _meta.json 文件"""
    import json

    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json 文件不存在"

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 格式错误: {e}"

    # 验证必需字段
    required_fields = ['id', 'version', 'name', 'description']
    for field in required_fields:
        if field not in meta:
            return False, f"_meta.json 缺少必需字段: {field}"

    # 验证 id 是数字
    if not isinstance(meta['id'], int):
        return False, "_meta.json id 必须是整数"

    # 验证 version 格式 (语义化版本)
    version_pattern = r'^\d+\.\d+\.\d+$'
    if not re.match(version_pattern, meta['version']):
        return False, f"_meta.json version 格式错误，应为 x.y.z 格式"

    return True, "_meta.json 验证通过"


def validate_directory_structure(skill_path: Path, skill_name: str) -> tuple[bool, str]:
    """验证目录结构"""
    expected_dirs = ['scripts', 'references', 'assets']

    for dir_name in expected_dirs:
        dir_path = skill_path / dir_name
        if not dir_path.exists():
            return False, f"缺少目录: {dir_name}/"

    return True, "目录结构验证通过"


def validate_naming(skill_path: Path, skill_name: str) -> tuple[bool, str]:
    """验证命名规范"""
    # 检查技能名称是否为英文 (允许连字符和下划线)
    name_for_check = skill_name.replace('-', '').replace('_', '')
    if not name_for_check.isalnum():
        return False, f"技能名称 '{skill_name}' 必须只包含英文字母、数字和连字符/下划线"

    # 检查 frontmatter 中的 name 是否与目录名匹配
    skill_md = skill_path / "SKILL.md"
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 frontmatter - 使用更健壮的方法
    lines = content.split('\n')
    end_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx > 1:
        frontmatter = '\n'.join(lines[1:end_idx])
        name_match = re.search(r'^name:\s*(.+?)\s*$', frontmatter, re.MULTILINE)
        if name_match:
            frontmatter_name = name_match.group(1).strip()
            if frontmatter_name != skill_name:
                return False, f"frontmatter name ({frontmatter_name}) 与目录名 ({skill_name}) 不匹配"

    return True, "命名规范验证通过"


def main():
    """主验证流程"""
    if len(sys.argv) < 2:
        print("用法: python validate_skill.py <技能目录路径>")
        sys.exit(1)

    skill_path = Path(sys.argv[1]).resolve()  # 使用 resolve() 获取绝对路径

    if not skill_path.exists():
        print(f"错误: 目录不存在: {skill_path}")
        sys.exit(1)

    skill_name = skill_path.name

    # 如果 skill_name 为空（传入相对路径如 '.'），使用当前目录名
    if not skill_name:
        skill_name = Path.cwd().name

    print(f"正在验证技能: {skill_name}")
    print("-" * 50)

    all_passed = True

    # 执行各项验证
    validators = [
        ("Frontmatter 验证", validate_frontmatter),
        ("_meta.json 验证", validate_meta_json),
        ("目录结构验证", lambda p: validate_directory_structure(p, skill_name)),
        ("命名规范验证", lambda p: validate_naming(p, skill_name)),
    ]

    for name, validator in validators:
        passed, message = validator(skill_path)
        status = "✓" if passed else "✗"
        print(f"{status} {name}: {message}")
        if not passed:
            all_passed = False

    print("-" * 50)

    if all_passed:
        print("验证结果: 全部通过 ✓")
        sys.exit(0)
    else:
        print("验证结果: 部分检查未通过 ✗")
        sys.exit(1)


if __name__ == "__main__":
    main()
