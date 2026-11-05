#!/usr/bin/env python3
"""
技能验证脚本
验证 SKILL.md 和 _meta.json 的结构和内容
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any


def validate_skill(skill_path: str) -> Tuple[bool, List[str]]:
    """
    验证技能结构和内容

    Args:
        skill_path: 技能目录路径

    Returns:
        (是否通过, 错误列表)
    """
    errors = []
    skill_dir = Path(skill_path)

    # 1. 检查目录存在
    if not skill_dir.exists():
        errors.append(f"❌ 技能目录不存在: {skill_path}")
        return False, errors

    if not skill_dir.is_dir():
        errors.append(f"❌ 路径不是目录: {skill_path}")
        return False, errors

    # 2. 检查 SKILL.md 存在
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("❌ SKILL.md 不存在")
        return False, errors

    # 3. 读取并解析 SKILL.md
    try:
        content = skill_md.read_text(encoding='utf-8')
    except Exception as e:
        errors.append(f"❌ 读取 SKILL.md 失败: {e}")
        return False, errors

    # 4. 验证 frontmatter
    frontmatter_errors = validate_frontmatter(content)
    errors.extend(frontmatter_errors)

    # 5. 检查 _meta.json
    meta_errors = validate_meta(skill_dir)
    errors.extend(meta_errors)

    # 6. 检查命名一致性
    name_errors = validate_naming(skill_dir, content)
    errors.extend(name_errors)

    return len(errors) == 0, errors


def validate_frontmatter(content: str) -> List[str]:
    """验证 frontmatter"""
    errors = []

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        errors.append("❌ SKILL.md 必须以 YAML frontmatter (---) 开头")
        return errors

    # 提取 frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if line.strip() == '---' and i > 0:
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("❌ YAML frontmatter 未正确闭合")
        return errors

    frontmatter_text = '\n'.join(lines[1:frontmatter_end])

    # 检查必填字段
    if 'name:' not in frontmatter_text and 'name :' not in frontmatter_text:
        errors.append("❌ frontmatter 缺少 name 字段")

    if 'description:' not in frontmatter_text and 'description :' not in frontmatter_text:
        errors.append("❌ frontmatter 缺少 description 字段")

    # 提取 name 值
    name_match = re.search(r'name:\s*([^\n]+)', frontmatter_text)
    if name_match:
        name_value = name_match.group(1).strip()
        if not name_value:
            errors.append("❌ name 字段不能为空")
        elif ' ' in name_value and not name_value.startswith('"'):
            errors.append(f"❌ name 应使用连字符格式: {name_value}")

    return errors


def validate_meta(skill_dir: Path) -> List[str]:
    """验证 _meta.json"""
    errors = []

    meta_file = skill_dir / "_meta.json"
    if not meta_file.exists():
        errors.append("❌ _meta.json 不存在")
        return errors

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        errors.append(f"❌ _meta.json 格式错误: {e}")
        return errors

    # 检查必填字段
    if 'id' not in meta:
        errors.append("❌ _meta.json 缺少 id 字段")

    if 'version' not in meta:
        errors.append("❌ _meta.json 缺少 version 字段")

    # 验证 id 类型
    if 'id' in meta:
        if not isinstance(meta['id'], int):
            errors.append(f"❌ _meta.json id 应为整数: {meta['id']}")

    # 验证 version 格式
    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"❌ _meta.json version 格式错误: {version} (应为 x.y.z)")

    return errors


def validate_naming(skill_dir: Path, content: str) -> List[str]:
    """验证命名一致性"""
    errors = []

    # 获取目录名（绝对路径）
    dir_name = skill_dir.resolve().name

    # 从 frontmatter 提取 name
    frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        name_match = re.search(r'name:\s*([^\n]+)', frontmatter_match.group(1))
        if name_match:
            frontmatter_name = name_match.group(1).strip()

            # 比较目录名
            if frontmatter_name != dir_name:
                errors.append(f"❌ 目录名与 frontmatter name 不一致: 目录={dir_name}, frontmatter={frontmatter_name}")

    return errors


def main():
    import argparse
    parser = argparse.ArgumentParser(description='验证技能结构')
    parser.add_argument('path', nargs='?', default='.',
                       help='技能目录路径')

    args = parser.parse_args()

    success, errors = validate_skill(args.path)

    if errors:
        print("验证结果：❌ 失败")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print("✅ 验证通过")


if __name__ == '__main__':
    main()
