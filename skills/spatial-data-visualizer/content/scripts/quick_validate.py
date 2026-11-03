#!/usr/bin/env python3
"""
快速验证脚本 - 验证技能结构和内容

检查项：
1. SKILL.md 存在且 frontmatter 正确
2. _meta.json 存在且格式正确
3. 文件命名规范
4. 无非法字符
"""

import json
import os
from pathlib import Path
from typing import List, Tuple


def validate_frontmatter(skill_path: Path) -> Tuple[bool, str]:
    """验证 SKILL.md frontmatter"""
    skill_md = skill_path / 'SKILL.md'

    if not skill_md.exists():
        return False, "SKILL.md 文件不存在"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter 开头（---）"

    # 解析 frontmatter
    lines = content.split('\n')
    frontmatter = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter.append(line)

    # 检查必需字段
    frontmatter_text = '\n'.join(frontmatter)

    if 'name:' not in frontmatter_text:
        return False, "frontmatter 缺少 name 字段"

    if 'description:' not in frontmatter_text:
        return False, "frontmatter 缺少 description 字段"

    # 检查 name 格式
    for line in frontmatter:
        if line.startswith('name:'):
            name = line.split(':', 1)[1].strip()
            if not name:
                return False, "name 字段不能为空"
            if ' ' in name:  # 应该使用连字符
                return False, f"name 应该使用连字符格式，如 '{name.replace(' ', '-')}'"

    return True, "frontmatter 验证通过"


def validate_meta(skill_path: Path) -> Tuple[bool, str]:
    """验证 _meta.json"""
    meta_file = skill_path / '_meta.json'

    if not meta_file.exists():
        return False, "_meta.json 文件不存在"

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError:
        return False, "_meta.json 格式错误"

    # 检查必需字段
    if 'id' not in meta:
        return False, "_meta.json 缺少 id 字段"

    if 'version' not in meta:
        return False, "_meta.json 缺少 version 字段"

    # 检查 version 格式
    version = meta.get('version', '')
    if not version or not version.replace('.', '').replace('0-9', '').isdigit():
        return False, f"version 格式错误: {version}"

    return True, "_meta.json 验证通过"


def validate_naming(skill_path: Path) -> Tuple[bool, str]:
    """验证命名规范"""
    name = skill_path.name

    # 检查是否使用连字符
    if ' ' in name:
        return False, f"文件夹名称不应包含空格，应使用连字符"

    # 检查是否有中文
    for char in name:
        if ord(char) > 127:
            return False, f"文件夹名称应使用英文字母，不应包含: {char}"

    # 检查 SKILL.md 中的 name
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查 frontmatter 中的 name
        in_frontmatter = False
        for line in content.split('\n'):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                continue
            if in_frontmatter and line.startswith('name:'):
                skill_name = line.split(':', 1)[1].strip()
                if ' ' in skill_name:
                    return False, f"SKILL.md 中 name 应使用连字符: '{skill_name}'"
                for char in skill_name:
                    if ord(char) > 127:
                        return False, f"SKILL.md 中 name 应使用英文字母"

    return True, "命名规范验证通过"


def validate_structure(skill_path: Path) -> Tuple[bool, List[str]]:
    """验证目录结构"""
    errors = []

    # 检查必需文件
    if not (skill_path / 'SKILL.md').exists():
        errors.append("缺少 SKILL.md")

    if not (skill_path / '_meta.json').exists():
        errors.append("缺少 _meta.json")

    return len(errors) == 0, errors


def validate_skill(skill_path: str) -> bool:
    """验证技能完整性"""
    skill_path = Path(skill_path)

    if not skill_path.exists():
        print(f"错误: 路径不存在 {skill_path}")
        return False

    print(f"验证技能: {skill_path.name}")
    print("-" * 40)

    all_passed = True

    # 1. 验证结构
    passed, errors = validate_structure(skill_path)
    if not passed:
        print("❌ 结构验证失败:")
        for e in errors:
            print(f"   - {e}")
        all_passed = False
    else:
        print("✓ 结构验证通过")

    # 2. 验证 frontmatter
    passed, msg = validate_frontmatter(skill_path)
    if not passed:
        print(f"❌ {msg}")
        all_passed = False
    else:
        print(f"✓ {msg}")

    # 3. 验证 _meta.json
    passed, msg = validate_meta(skill_path)
    if not passed:
        print(f"❌ {msg}")
        all_passed = False
    else:
        print(f"✓ {msg}")

    # 4. 验证命名
    passed, msg = validate_naming(skill_path)
    if not passed:
        print(f"❌ {msg}")
        all_passed = False
    else:
        print(f"✓ {msg}")

    print("-" * 40)
    print(f"验证结果: {'✓ 通过' if all_passed else '❌ 失败'}")

    return all_passed


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        skill_path = sys.argv[1]
    else:
        # 默认验证当前目录
        skill_path = Path(__file__).parent.parent

    result = validate_skill(skill_path)
    sys.exit(0 if result else 1)